"""Main Python extractor implementation.

This module provides the PythonExtractor class that transforms Python source code
into the 5-layer IR representation. It follows the hybrid architecture: tree-sitter
for parsing, jedi/pyright for semantic enrichment.

Example:
    extractor = PythonExtractor()
    ir = extractor.extract(source_code, "module.py", config)

    # With custom configuration
    config = ExtractConfig(
        mode=ExtractionMode.FULL_MODULE,
        semantic_level=SemanticEnrichmentLevel.FULL,
        resolve_imports=True,
    )
    ir = extractor.extract(source_code, "module.py", config)
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ir_core.base import (
    Extractor,
    ExtractConfig,
    ExtractionMode,
    SemanticEnrichmentLevel,
    register_extractor,
)
from ir_core.models import (
    IRVersion,
    Module,
    ModuleMetadata,
    TypeDef,
    TypeBody,
    TypeKind,
    TypeRef,
    TypeRefKind,
    TypeParam,
    TypeRelationship,
    Function,
    Param,
    Receiver,
    Effect,
    EffectKind,
    Binding,
    Lifetime,
    LifetimeKind,
    Mutability,
    Visibility,
    ControlFlowGraph,
    Block,
    Terminator,
    TerminatorKind,
    Statement,
    Expression,
    ExpressionKind,
    Argument,
    Import,
    ImportedItem,
    Export,
    DefinitionRef,
    Definition,
    Attribute,
    GapMarker,
    GapType,
    Severity,
    SemanticAnnotation,
    AnnotationSource,
    AutomationLevel,
    PreservationStatus,
    PreservationLevel,
    SourceSpan as IRSourceSpan,
    ExtractionError,
    ExtractionErrorCode,
    Field_,
    Variant,
)
from ir_core.treesitter import (
    TreeSitterAdapter,
    TreeNode,
    ParseTree,
    SourceSpan,
    GASTNode,
    GASTKind,
)

from .parser import PythonParser
from .semantic import SemanticEnricher
from .patterns import PythonPatternMatcher, Pattern, PatternKind


def _source_span_to_ir(span: SourceSpan) -> IRSourceSpan:
    """Convert tree-sitter SourceSpan to IR SourceSpan."""
    return IRSourceSpan(
        file=span.file,
        start_line=span.start_line,
        start_col=span.start_col,
        end_line=span.end_line,
        end_col=span.end_col,
    )


@register_extractor("python")
class PythonExtractor(Extractor):
    """Python source code extractor using tree-sitter + semantic enrichment.

    This extractor implements the full Python extraction pipeline:
    1. Parse source with tree-sitter-python
    2. Normalize CST to GAST via PythonParser
    3. Enrich with type information via SemanticEnricher (jedi/pyright)
    4. Generate 5-layer IR structure
    5. Detect and mark semantic gaps

    Attributes:
        parser: PythonParser instance for tree-sitter parsing
        enricher: SemanticEnricher instance for type analysis
        pattern_matcher: PythonPatternMatcher for idiom detection

    Example:
        extractor = PythonExtractor()
        ir = extractor.extract('''
            def hello(name: str) -> str:
                return f"Hello, {name}!"
        ''', "hello.py", ExtractConfig())
    """

    def __init__(self) -> None:
        """Initialize the Python extractor."""
        self.parser = PythonParser()
        self.enricher = SemanticEnricher()
        self.pattern_matcher = PythonPatternMatcher()

        # Counters for generating unique IDs
        self._id_counters: dict[str, int] = {}
        self._current_path: str = ""
        self._current_source: str = ""

    def _next_id(self, prefix: str) -> str:
        """Generate the next unique ID for a given prefix."""
        count = self._id_counters.get(prefix, 0)
        self._id_counters[prefix] = count + 1
        return f"{prefix}:{self._current_path}:{count}"

    def _reset_state(self, path: str, source: str) -> None:
        """Reset extraction state for a new file."""
        self._id_counters = {}
        self._current_path = path
        self._current_source = source

    def extract(
        self, source: str, path: str, config: ExtractConfig
    ) -> IRVersion:
        """Extract IR from Python source code.

        Args:
            source: Python source code as a string
            path: File path (used for error reporting and import resolution)
            config: Extraction configuration

        Returns:
            IRVersion containing all extracted layers

        Raises:
            ExtractionError: If extraction fails with E001-E005 error codes
        """
        self._reset_state(path, source)

        # Step 1: Parse with tree-sitter
        try:
            tree = self.parser.parse(source, path)
        except Exception as e:
            raise ExtractionError(
                code=ExtractionErrorCode.E001,
                message=f"Parse error: {e}",
                location=IRSourceSpan(
                    file=path, start_line=1, start_col=0, end_line=1, end_col=0
                ),
            ) from e

        # Check for parse errors
        if tree.has_errors:
            for error_node in tree.errors:
                # Continue with partial extraction but record the error
                pass

        # Step 2: Extract raw structures
        functions_raw = self.parser.extract_functions(tree)
        classes_raw = self.parser.extract_classes(tree)
        imports_raw = self.parser.extract_imports(tree)

        # Step 3: Semantic enrichment (if configured)
        if config.semantic_level != SemanticEnrichmentLevel.NONE:
            enriched_data = self._enrich_semantics(
                source, path, config, functions_raw, classes_raw
            )
        else:
            enriched_data = None

        # Step 4: Build IR structures
        types: list[TypeDef] = []
        type_relationships: list[TypeRelationship] = []
        functions: list[Function] = []
        bindings: list[Binding] = []
        expressions: list[Expression] = []
        gaps: list[GapMarker] = []
        annotations: list[SemanticAnnotation] = []

        # Process imports
        ir_imports = self._process_imports(imports_raw, gaps)

        # Process classes -> TypeDefs
        for class_node in classes_raw:
            type_def, class_funcs, class_gaps = self._process_class(
                class_node, config, enriched_data
            )
            types.append(type_def)
            functions.extend(class_funcs)
            gaps.extend(class_gaps)

        # Process functions
        for func_node in functions_raw:
            func, func_bindings, func_gaps = self._process_function(
                func_node, config, enriched_data
            )
            functions.append(func)
            bindings.extend(func_bindings)
            gaps.extend(func_gaps)

        # Step 5: Detect patterns and create annotations
        patterns = self._detect_patterns(tree)
        for pattern in patterns:
            annotation = self._pattern_to_annotation(pattern)
            annotations.append(annotation)

        # Build module metadata
        source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        metadata = ModuleMetadata(
            source_file=path,
            source_language="python",
            extraction_version=self.supported_version(),
            extraction_mode=config.mode,
            source_hash=source_hash,
            extraction_timestamp=datetime.now(timezone.utc),
            documentation=self._extract_module_docstring(tree),
        )

        # Build module
        module = Module(
            id=f"module:{path}",
            name=Path(path).stem,
            path=self._path_to_module_path(path),
            visibility=Visibility.PUBLIC,
            imports=ir_imports,
            exports=[],  # Will be populated based on __all__ or public names
            definitions=self._build_definitions(types, functions),
            submodules=[],
            extraction_scope="full" if config.mode == ExtractionMode.FULL_MODULE else "partial",
            metadata=metadata,
        )

        # Build preservation status
        preservation = self._compute_preservation(gaps, module.id)

        # Construct final IR
        return IRVersion(
            version=self.supported_version(),
            module=module,
            types=types,
            type_relationships=type_relationships,
            functions=functions,
            bindings=bindings,
            data_flow_nodes=[],
            expressions=expressions if config.include_layer0 else [],
            annotations=annotations,
            gaps=gaps,
            preservation=preservation,
        )

    def supported_version(self) -> str:
        """Return the IR schema version this extractor produces."""
        return "ir-v1.0"

    def validate_source(self, source: str, path: str) -> list[GapMarker]:
        """Validate source code and return potential issues.

        This is a quick validation pass that doesn't perform full extraction.

        Args:
            source: Python source code
            path: File path for error reporting

        Returns:
            List of gap markers for detected issues
        """
        gaps: list[GapMarker] = []

        try:
            tree = self.parser.parse(source, path)
        except Exception as e:
            gaps.append(GapMarker(
                id=f"gap:{path}:parse_error",
                location=f"file:{path}",
                gap_type=GapType.IMPOSSIBLE,
                severity=Severity.CRITICAL,
                description=f"Parse error: {e}",
                source_concept="Python source",
                target_concept=None,
            ))
            return gaps

        if tree.has_errors:
            for error_node in tree.errors:
                gaps.append(GapMarker(
                    id=f"gap:{path}:{error_node.span.start_line}",
                    location=f"line:{error_node.span.start_line}",
                    gap_type=GapType.IMPOSSIBLE,
                    severity=Severity.HIGH,
                    description=f"Syntax error at line {error_node.span.start_line}",
                    source_concept="Python syntax",
                    target_concept=None,
                ))

        # Check for known unsupported patterns
        patterns = self.pattern_matcher.detect_unsupported(tree.root)
        for pattern in patterns:
            gaps.append(GapMarker(
                id=f"gap:{path}:{pattern.kind.value}:{pattern.span.start_line}",
                location=f"line:{pattern.span.start_line}",
                gap_type=GapType.STRUCTURAL,
                severity=Severity.MEDIUM,
                description=pattern.description,
                source_concept=pattern.kind.value,
                target_concept=None,
                automation_level=pattern.automation_level,
            ))

        return gaps

    def _enrich_semantics(
        self,
        source: str,
        path: str,
        config: ExtractConfig,
        functions: list[TreeNode],
        classes: list[TreeNode],
    ) -> dict[str, Any]:
        """Perform semantic enrichment on extracted nodes.

        Args:
            source: Python source code
            path: File path
            config: Extraction configuration
            functions: Extracted function nodes
            classes: Extracted class nodes

        Returns:
            Dictionary mapping node locations to semantic information
        """
        enriched: dict[str, Any] = {}

        try:
            if config.semantic_level == SemanticEnrichmentLevel.FULL:
                # Use pyright for full type analysis
                enriched = self.enricher.enrich_with_pyright(
                    source, path, config.project_root
                )
            else:
                # Use jedi for basic type inference
                enriched = self.enricher.enrich_with_jedi(source, path)
        except Exception:
            # Graceful degradation: continue without semantic info
            pass

        return enriched

    def _process_imports(
        self,
        imports: list[TreeNode],
        gaps: list[GapMarker],
    ) -> list[Import]:
        """Process import statements into IR Import structures.

        Args:
            imports: List of import tree nodes
            gaps: List to append any detected gaps

        Returns:
            List of IR Import objects
        """
        ir_imports: list[Import] = []

        for imp_node in imports:
            if imp_node.type == "import_statement":
                ir_imports.extend(self._process_import_statement(imp_node, gaps))
            elif imp_node.type == "import_from_statement":
                ir_imports.extend(self._process_from_import(imp_node, gaps))

        return ir_imports

    def _process_import_statement(
        self, node: TreeNode, gaps: list[GapMarker]
    ) -> list[Import]:
        """Process 'import X' or 'import X as Y' statements."""
        imports: list[Import] = []

        for child in node.children:
            if child.type == "dotted_name":
                module_path = [
                    part.text for part in child.children
                    if part.type == "identifier"
                ]
                imports.append(Import(
                    id=self._next_id("import"),
                    module_path=module_path,
                    imported_items=[ImportedItem(
                        name=module_path[-1],
                        alias=None,
                        kind="module",
                    )],
                    alias=None,
                ))
            elif child.type == "aliased_import":
                name_node = child.child_by_field("name")
                alias_node = child.child_by_field("alias")
                if name_node:
                    module_path = [
                        part.text for part in name_node.children
                        if part.type == "identifier"
                    ] if name_node.type == "dotted_name" else [name_node.text]
                    alias = alias_node.text if alias_node else None
                    imports.append(Import(
                        id=self._next_id("import"),
                        module_path=module_path,
                        imported_items=[ImportedItem(
                            name=module_path[-1],
                            alias=alias,
                            kind="module",
                        )],
                        alias=alias,
                    ))

        return imports

    def _process_from_import(
        self, node: TreeNode, gaps: list[GapMarker]
    ) -> list[Import]:
        """Process 'from X import Y' statements."""
        imports: list[Import] = []

        module_node = node.child_by_field("module_name")
        module_path: list[str] = []

        if module_node:
            if module_node.type == "dotted_name":
                module_path = [
                    part.text for part in module_node.children
                    if part.type == "identifier"
                ]
            elif module_node.type == "relative_import":
                # Handle relative imports like 'from . import X' or 'from ..foo import X'
                dots = sum(1 for c in module_node.children if c.type == ".")
                module_path = ["."] * dots
                dotted = module_node.find_first("dotted_name")
                if dotted:
                    module_path.extend(
                        part.text for part in dotted.children
                        if part.type == "identifier"
                    )

        # Extract imported items
        imported_items: list[ImportedItem] = []

        # Check for wildcard import
        wildcard = node.find_first("wildcard_import")
        if wildcard:
            imported_items.append(ImportedItem(
                name="*",
                alias=None,
                kind="wildcard",
            ))
            # Wildcard imports are a gap - we can't know what's imported
            gaps.append(GapMarker(
                id=self._next_id("gap"),
                location=f"line:{node.span.start_line}",
                gap_type=GapType.STRUCTURAL,
                gap_pattern_id="PY-001",
                severity=Severity.MEDIUM,
                description="Wildcard import cannot be fully resolved",
                source_concept="from X import *",
                target_concept="explicit imports",
                suggested_mitigations=["Replace with explicit imports"],
                automation_level=AutomationLevel.PARTIAL,
            ))
        else:
            # Process individual imports
            for child in node.children:
                if child.type == "dotted_name":
                    name = child.text
                    imported_items.append(ImportedItem(
                        name=name,
                        alias=None,
                        kind="variable",  # Could be type, function, etc.
                    ))
                elif child.type == "aliased_import":
                    name_node = child.child_by_field("name")
                    alias_node = child.child_by_field("alias")
                    if name_node:
                        imported_items.append(ImportedItem(
                            name=name_node.text,
                            alias=alias_node.text if alias_node else None,
                            kind="variable",
                        ))

        if imported_items:
            imports.append(Import(
                id=self._next_id("import"),
                module_path=module_path,
                imported_items=imported_items,
            ))

        return imports

    def _process_class(
        self,
        class_node: TreeNode,
        config: ExtractConfig,
        enriched_data: dict[str, Any] | None,
    ) -> tuple[TypeDef, list[Function], list[GapMarker]]:
        """Process a class definition into a TypeDef.

        Args:
            class_node: Tree node for the class
            config: Extraction configuration
            enriched_data: Semantic enrichment data

        Returns:
            Tuple of (TypeDef, list of methods as Functions, list of gaps)
        """
        gaps: list[GapMarker] = []
        functions: list[Function] = []

        name_node = class_node.child_by_field("name")
        class_name = name_node.text if name_node else "<anonymous>"
        class_id = self._next_id("type")

        # Extract type parameters from generic base classes
        type_params: list[TypeParam] = []
        bases_node = class_node.child_by_field("superclasses")
        base_types: list[TypeRef] = []

        if bases_node:
            for base in bases_node.children:
                if base.type == "argument_list":
                    continue
                base_type = self._node_to_type_ref(base)
                if base_type:
                    base_types.append(base_type)
                    # Check for Generic[T] and extract type params
                    if base.text.startswith("Generic["):
                        params = self._extract_generic_params(base)
                        type_params.extend(params)

        # Extract body
        body_node = class_node.child_by_field("body")
        fields: list[Field_] = []
        methods: list[str] = []

        if body_node:
            for stmt in body_node.named_children():
                if stmt.type == "function_definition":
                    # Process method
                    func, func_bindings, func_gaps = self._process_function(
                        stmt, config, enriched_data, class_id=class_id
                    )
                    functions.append(func)
                    methods.append(func.id)
                    gaps.extend(func_gaps)
                elif stmt.type == "expression_statement":
                    # Check for class-level attribute annotations
                    expr = stmt.named_children()[0] if stmt.named_children() else None
                    if expr and expr.type == "assignment":
                        field = self._extract_class_field(expr)
                        if field:
                            fields.append(field)
                    elif expr and expr.type == "type":
                        # Type annotation without assignment
                        field = self._extract_annotated_field(expr)
                        if field:
                            fields.append(field)

        # Determine type kind
        type_kind = TypeKind.CLASS

        # Check for dataclass decorator
        decorators = self._extract_decorators(class_node)
        for dec in decorators:
            if dec.name in ("dataclass", "dataclasses.dataclass"):
                type_kind = TypeKind.STRUCT  # Dataclasses are more struct-like
            elif dec.name in ("Protocol", "typing.Protocol", "typing_extensions.Protocol"):
                type_kind = TypeKind.INTERFACE

        type_body = TypeBody(
            fields=fields,
            methods=methods,
        )

        # Extract docstring
        docstring = self._extract_docstring(body_node) if body_node else None

        type_def = TypeDef(
            id=class_id,
            name=class_name,
            kind=type_kind,
            params=type_params,
            body=type_body,
            visibility=Visibility.PUBLIC if not class_name.startswith("_") else Visibility.PRIVATE,
            span=_source_span_to_ir(class_node.span),
            annotations=[],
        )

        # Add inheritance relationships
        # (These would be added to type_relationships in the caller)

        return type_def, functions, gaps

    def _process_function(
        self,
        func_node: TreeNode,
        config: ExtractConfig,
        enriched_data: dict[str, Any] | None,
        class_id: str | None = None,
    ) -> tuple[Function, list[Binding], list[GapMarker]]:
        """Process a function definition into a Function.

        Args:
            func_node: Tree node for the function
            config: Extraction configuration
            enriched_data: Semantic enrichment data
            class_id: If this is a method, the parent class ID

        Returns:
            Tuple of (Function, list of Bindings, list of gaps)
        """
        gaps: list[GapMarker] = []
        bindings: list[Binding] = []

        name_node = func_node.child_by_field("name")
        func_name = name_node.text if name_node else "<anonymous>"
        func_id = self._next_id("func")

        # Check if async
        is_async = func_node.type == "async_function_definition" or any(
            c.type == "async" for c in func_node.children
        )

        # Extract parameters
        params_node = func_node.child_by_field("parameters")
        params, receiver = self._extract_parameters(params_node, class_id)

        # Extract return type
        return_type_node = func_node.child_by_field("return_type")
        return_type = self._node_to_type_ref(return_type_node) if return_type_node else TypeRef(
            kind=TypeRefKind.NAMED,
            type_id="builtins.None",
        )

        # Try to get enriched return type
        if enriched_data:
            key = f"{func_node.span.start_line}:{func_node.span.start_col}"
            if key in enriched_data:
                enriched_type = enriched_data[key].get("return_type")
                if enriched_type:
                    return_type = self._string_to_type_ref(enriched_type)

        # Extract type parameters
        type_params = self._extract_type_params(func_node)

        # Compute effects
        effects = self._compute_effects(func_node, is_async)

        # Extract body
        body_node = func_node.child_by_field("body")
        cfg = None

        if body_node and config.mode != ExtractionMode.SIGNATURE_ONLY:
            cfg, body_bindings, body_gaps = self._process_body(body_node, config)
            bindings.extend(body_bindings)
            gaps.extend(body_gaps)

        # Extract decorators
        decorators = self._extract_decorators(func_node)
        attributes = [Attribute(name=d.name, arguments=d.args) for d in decorators]

        # Extract docstring
        doc_comment = self._extract_docstring(body_node) if body_node else None

        # Determine visibility
        visibility = Visibility.PUBLIC
        if func_name.startswith("__") and not func_name.endswith("__"):
            visibility = Visibility.PRIVATE
        elif func_name.startswith("_"):
            visibility = Visibility.PROTECTED

        func = Function(
            id=func_id,
            name=func_name,
            params=params,
            return_type=return_type,
            type_params=type_params,
            effects=effects,
            body=cfg,
            visibility=visibility,
            receiver=receiver,
            span=_source_span_to_ir(func_node.span),
            doc_comment=doc_comment,
        )

        return func, bindings, gaps

    def _extract_parameters(
        self, params_node: TreeNode | None, class_id: str | None
    ) -> tuple[list[Param], Receiver | None]:
        """Extract function parameters.

        Args:
            params_node: Tree node for parameters
            class_id: Parent class ID if this is a method

        Returns:
            Tuple of (list of Param, Receiver if method)
        """
        params: list[Param] = []
        receiver: Receiver | None = None

        if not params_node:
            return params, receiver

        first_param = True

        for child in params_node.named_children():
            if child.type in ("identifier", "typed_parameter", "default_parameter",
                              "typed_default_parameter", "list_splat_pattern",
                              "dictionary_splat_pattern"):
                param = self._extract_single_param(child)
                if param:
                    # Check if this is self/cls
                    if first_param and class_id and param.name in ("self", "cls"):
                        receiver = Receiver(
                            type=TypeRef(kind=TypeRefKind.NAMED, type_id=class_id),
                            mutability=Mutability.MUTABLE if param.name == "self" else Mutability.IMMUTABLE,
                            name=param.name,
                        )
                    else:
                        params.append(param)
                first_param = False

        return params, receiver

    def _extract_single_param(self, node: TreeNode) -> Param | None:
        """Extract a single parameter from various node types."""
        if node.type == "identifier":
            return Param(
                name=node.text,
                type=TypeRef(kind=TypeRefKind.NAMED, type_id="typing.Any"),
            )

        if node.type == "typed_parameter":
            name_node = node.children[0] if node.children else None
            type_node = node.child_by_field("type")
            return Param(
                name=name_node.text if name_node else "unknown",
                type=self._node_to_type_ref(type_node) if type_node else TypeRef(
                    kind=TypeRefKind.NAMED, type_id="typing.Any"
                ),
            )

        if node.type == "default_parameter":
            name_node = node.child_by_field("name")
            value_node = node.child_by_field("value")
            return Param(
                name=name_node.text if name_node else "unknown",
                type=TypeRef(kind=TypeRefKind.NAMED, type_id="typing.Any"),
                # default would be an Expression, simplified here
            )

        if node.type == "typed_default_parameter":
            name_node = node.child_by_field("name")
            type_node = node.child_by_field("type")
            return Param(
                name=name_node.text if name_node else "unknown",
                type=self._node_to_type_ref(type_node) if type_node else TypeRef(
                    kind=TypeRefKind.NAMED, type_id="typing.Any"
                ),
            )

        if node.type == "list_splat_pattern":
            # *args
            name_node = node.named_children()[0] if node.named_children() else None
            return Param(
                name=name_node.text if name_node else "args",
                type=TypeRef(kind=TypeRefKind.NAMED, type_id="tuple"),
                variadic=True,
            )

        if node.type == "dictionary_splat_pattern":
            # **kwargs
            name_node = node.named_children()[0] if node.named_children() else None
            return Param(
                name=name_node.text if name_node else "kwargs",
                type=TypeRef(kind=TypeRefKind.NAMED, type_id="dict"),
                variadic=True,
            )

        return None

    def _node_to_type_ref(self, node: TreeNode | None) -> TypeRef:
        """Convert a type annotation node to a TypeRef.

        Args:
            node: Tree node representing a type annotation

        Returns:
            TypeRef representing the type
        """
        if node is None:
            return TypeRef(kind=TypeRefKind.NAMED, type_id="typing.Any")

        text = node.text.strip()

        # Handle common cases
        if node.type == "identifier":
            return TypeRef(kind=TypeRefKind.NAMED, type_id=text)

        if node.type == "type":
            # Unwrap type node
            inner = node.named_children()[0] if node.named_children() else None
            return self._node_to_type_ref(inner)

        if node.type == "attribute":
            # Module-qualified type like typing.Optional
            return TypeRef(kind=TypeRefKind.NAMED, type_id=text)

        if node.type == "subscript":
            # Generic type like List[int] or Optional[str]
            base_node = node.child_by_field("value")
            args_node = node.child_by_field("subscript")

            base_text = base_node.text if base_node else "Any"

            # Handle special cases
            if base_text in ("Optional", "typing.Optional"):
                inner_type = self._node_to_type_ref(args_node)
                return TypeRef(
                    kind=TypeRefKind.UNION,
                    members=[inner_type, TypeRef(kind=TypeRefKind.NAMED, type_id="None")],
                )

            if base_text in ("Union", "typing.Union"):
                members = []
                if args_node and args_node.type == "expression_list":
                    for member in args_node.named_children():
                        members.append(self._node_to_type_ref(member))
                else:
                    members.append(self._node_to_type_ref(args_node))
                return TypeRef(kind=TypeRefKind.UNION, members=members)

            if base_text in ("Callable", "typing.Callable"):
                # Callable[[args], return]
                return self._parse_callable_type(args_node)

            if base_text in ("Tuple", "tuple", "typing.Tuple"):
                elements = []
                if args_node and args_node.type == "expression_list":
                    for elem in args_node.named_children():
                        elements.append(self._node_to_type_ref(elem))
                else:
                    elements.append(self._node_to_type_ref(args_node))
                return TypeRef(kind=TypeRefKind.TUPLE, elements=elements)

            # Generic type
            args = []
            if args_node:
                if args_node.type == "expression_list":
                    for arg in args_node.named_children():
                        args.append(self._node_to_type_ref(arg))
                else:
                    args.append(self._node_to_type_ref(args_node))

            return TypeRef(
                kind=TypeRefKind.NAMED,
                type_id=base_text,
                args=args,
            )

        if node.type == "binary_operator":
            # Union type with | syntax (Python 3.10+)
            op = node.child_by_field("operator")
            if op and op.text == "|":
                left = self._node_to_type_ref(node.child_by_field("left"))
                right = self._node_to_type_ref(node.child_by_field("right"))
                # Flatten nested unions
                members = []
                for t in [left, right]:
                    if t.kind == TypeRefKind.UNION:
                        members.extend(t.members)
                    else:
                        members.append(t)
                return TypeRef(kind=TypeRefKind.UNION, members=members)

        if node.type == "none":
            return TypeRef(kind=TypeRefKind.NAMED, type_id="None")

        # Default fallback
        return TypeRef(kind=TypeRefKind.NAMED, type_id=text or "typing.Any")

    def _parse_callable_type(self, args_node: TreeNode | None) -> TypeRef:
        """Parse a Callable type annotation."""
        if not args_node:
            return TypeRef(
                kind=TypeRefKind.FUNCTION,
                params=[],
                return_type=TypeRef(kind=TypeRefKind.NAMED, type_id="typing.Any"),
            )

        params: list[TypeRef] = []
        return_type = TypeRef(kind=TypeRefKind.NAMED, type_id="typing.Any")

        if args_node.type == "expression_list":
            children = list(args_node.named_children())
            if len(children) >= 2:
                # First is param list, last is return type
                param_list = children[0]
                return_node = children[-1]

                if param_list.type == "list":
                    for param in param_list.named_children():
                        params.append(self._node_to_type_ref(param))

                return_type = self._node_to_type_ref(return_node)

        return TypeRef(
            kind=TypeRefKind.FUNCTION,
            params=params,
            return_type=return_type,
        )

    def _string_to_type_ref(self, type_str: str) -> TypeRef:
        """Convert a type string to a TypeRef.

        This is used for enriched type information from jedi/pyright.
        """
        type_str = type_str.strip()

        if not type_str or type_str == "None":
            return TypeRef(kind=TypeRefKind.NAMED, type_id="None")

        # Simple types
        if "[" not in type_str and "|" not in type_str:
            return TypeRef(kind=TypeRefKind.NAMED, type_id=type_str)

        # Union types (Python 3.10+ syntax)
        if "|" in type_str:
            members = [
                self._string_to_type_ref(m.strip())
                for m in type_str.split("|")
            ]
            return TypeRef(kind=TypeRefKind.UNION, members=members)

        # Generic types
        bracket_pos = type_str.find("[")
        if bracket_pos > 0:
            base = type_str[:bracket_pos]
            # Parse arguments (simplified - doesn't handle nested brackets properly)
            return TypeRef(kind=TypeRefKind.NAMED, type_id=base)

        return TypeRef(kind=TypeRefKind.NAMED, type_id=type_str)

    def _extract_type_params(self, func_node: TreeNode) -> list[TypeParam]:
        """Extract type parameters from a generic function."""
        # Python 3.12+ syntax: def func[T](x: T) -> T
        type_params: list[TypeParam] = []

        for child in func_node.children:
            if child.type == "type_parameter":
                # Extract TypeVar definitions
                for param in child.named_children():
                    if param.type == "type":
                        name = param.text
                        type_params.append(TypeParam(name=name))

        return type_params

    def _extract_generic_params(self, base_node: TreeNode) -> list[TypeParam]:
        """Extract type parameters from Generic[T, K] base class."""
        params: list[TypeParam] = []

        subscript = base_node.find_first("subscript")
        if subscript:
            args = subscript.child_by_field("subscript")
            if args:
                if args.type == "expression_list":
                    for arg in args.named_children():
                        params.append(TypeParam(name=arg.text))
                else:
                    params.append(TypeParam(name=args.text))

        return params

    def _compute_effects(self, func_node: TreeNode, is_async: bool) -> list[Effect]:
        """Compute the effects of a function.

        Args:
            func_node: Function tree node
            is_async: Whether the function is async

        Returns:
            List of Effect annotations
        """
        effects: list[Effect] = []

        if is_async:
            effects.append(Effect(
                kind=EffectKind.ASYNC,
                source=AnnotationSource.EXPLICIT,
            ))

        # Check for raise statements
        body = func_node.child_by_field("body")
        if body:
            raises = body.find_all("raise_statement")
            if raises:
                effects.append(Effect(
                    kind=EffectKind.THROWS,
                    source=AnnotationSource.INFERRED,
                ))

            # Check for I/O operations (simplified heuristic)
            calls = body.find_all("call")
            io_functions = {"print", "open", "read", "write", "input"}
            for call in calls:
                func_name = call.child_by_field("function")
                if func_name and func_name.text in io_functions:
                    effects.append(Effect(
                        kind=EffectKind.IO,
                        source=AnnotationSource.INFERRED,
                    ))
                    break

            # Check for await expressions
            awaits = body.find_all("await")
            if awaits:
                effects.append(Effect(
                    kind=EffectKind.SUSPENDS,
                    source=AnnotationSource.INFERRED,
                ))

        if not effects:
            effects.append(Effect(kind=EffectKind.PURE, source=AnnotationSource.INFERRED))

        return effects

    def _process_body(
        self,
        body_node: TreeNode,
        config: ExtractConfig,
    ) -> tuple[ControlFlowGraph | None, list[Binding], list[GapMarker]]:
        """Process a function body into a control flow graph.

        Args:
            body_node: Tree node for the function body
            config: Extraction configuration

        Returns:
            Tuple of (CFG, bindings, gaps)
        """
        bindings: list[Binding] = []
        gaps: list[GapMarker] = []

        # For now, create a simple single-block CFG
        # A full implementation would build proper basic blocks
        block_id = self._next_id("block")
        statements: list[Statement] = []

        for stmt in body_node.named_children():
            if stmt.type == "expression_statement":
                # Simple expression statement
                statements.append(Statement(kind="noop"))
            elif stmt.type == "assignment":
                # Variable assignment
                target = stmt.child_by_field("left")
                if target:
                    binding = Binding(
                        id=self._next_id("binding"),
                        name=target.text,
                        type=TypeRef(kind=TypeRefKind.NAMED, type_id="typing.Any"),
                        mutability=Mutability.MUTABLE,
                        lifetime=Lifetime(kind=LifetimeKind.SCOPED),
                    )
                    bindings.append(binding)
                    statements.append(Statement(
                        kind="assign",
                        target=binding.id,
                    ))
            elif stmt.type == "return_statement":
                # Return is handled by terminator
                pass

        # Create entry block with return terminator
        entry_block = Block(
            id=block_id,
            statements=statements,
            terminator=Terminator(kind=TerminatorKind.RETURN),
        )

        cfg = ControlFlowGraph(
            entry=block_id,
            blocks=[entry_block],
            exit=block_id,
        )

        return cfg, bindings, gaps

    def _extract_decorators(self, node: TreeNode) -> list[_DecoratorInfo]:
        """Extract decorator information from a function or class."""
        decorators: list[_DecoratorInfo] = []

        for child in node.children:
            if child.type == "decorator":
                name_node = child.find_first("identifier") or child.find_first("attribute")
                if name_node:
                    # Check for call with arguments
                    call = child.find_first("call")
                    args: list[Any] = []
                    if call:
                        args_node = call.child_by_field("arguments")
                        if args_node:
                            for arg in args_node.named_children():
                                args.append(arg.text)

                    decorators.append(_DecoratorInfo(
                        name=name_node.text,
                        args=args,
                    ))

        return decorators

    def _extract_class_field(self, assignment: TreeNode) -> Field_ | None:
        """Extract a field from a class-level assignment."""
        left = assignment.child_by_field("left")
        right = assignment.child_by_field("right")

        if not left:
            return None

        # Check for type annotation
        type_ref = TypeRef(kind=TypeRefKind.NAMED, type_id="typing.Any")

        if left.type == "type":
            # Annotated assignment: name: Type = value
            pass  # Would need to extract type from annotation

        return Field_(
            name=left.text,
            type=type_ref,
            visibility=Visibility.PUBLIC if not left.text.startswith("_") else Visibility.PRIVATE,
        )

    def _extract_annotated_field(self, type_node: TreeNode) -> Field_ | None:
        """Extract a field from a type annotation without assignment."""
        # name: Type
        if type_node.type == "type":
            children = list(type_node.children)
            if len(children) >= 2:
                name = children[0].text
                type_ref = self._node_to_type_ref(children[-1])
                return Field_(
                    name=name,
                    type=type_ref,
                    visibility=Visibility.PUBLIC if not name.startswith("_") else Visibility.PRIVATE,
                )
        return None

    def _extract_docstring(self, body_node: TreeNode | None) -> str | None:
        """Extract docstring from a function or class body."""
        if not body_node:
            return None

        children = list(body_node.named_children())
        if not children:
            return None

        first = children[0]
        if first.type == "expression_statement":
            expr = first.named_children()[0] if first.named_children() else None
            if expr and expr.type == "string":
                # Remove quotes
                text = expr.text
                if text.startswith('"""') or text.startswith("'''"):
                    return text[3:-3].strip()
                elif text.startswith('"') or text.startswith("'"):
                    return text[1:-1].strip()

        return None

    def _extract_module_docstring(self, tree: ParseTree) -> str | None:
        """Extract module-level docstring."""
        return self._extract_docstring(tree.root)

    def _detect_patterns(self, tree: ParseTree) -> list[Pattern]:
        """Detect Python-specific patterns in the code."""
        patterns: list[Pattern] = []

        patterns.extend(self.pattern_matcher.detect_comprehensions(tree.root))
        patterns.extend(self.pattern_matcher.detect_decorators(tree.root))
        patterns.extend(self.pattern_matcher.detect_context_managers(tree.root))
        patterns.extend(self.pattern_matcher.detect_async_patterns(tree.root))

        return patterns

    def _pattern_to_annotation(self, pattern: Pattern) -> SemanticAnnotation:
        """Convert a detected pattern to a semantic annotation."""
        return SemanticAnnotation(
            id=self._next_id("annotation"),
            target=f"line:{pattern.span.start_line}",
            kind=f"pattern:{pattern.kind.value}",
            value={
                "pattern": pattern.kind.value,
                "description": pattern.description,
            },
            confidence=pattern.confidence,
            source=AnnotationSource.INFERRED,
        )

    def _path_to_module_path(self, path: str) -> list[str]:
        """Convert a file path to a module path."""
        p = Path(path)
        parts = list(p.parts[:-1]) + [p.stem]
        # Filter out common prefixes
        return [part for part in parts if part not in (".", "src", "lib")]

    def _build_definitions(
        self, types: list[TypeDef], functions: list[Function]
    ) -> list[Definition]:
        """Build definition references for the module."""
        definitions: list[Definition] = []

        for t in types:
            definitions.append(Definition(
                id=f"def:{t.id}",
                kind="type",
                ref=t.id,
                visibility=t.visibility,
            ))

        for f in functions:
            # Skip methods (they're part of types)
            if f.receiver is None:
                definitions.append(Definition(
                    id=f"def:{f.id}",
                    kind="function",
                    ref=f.id,
                    visibility=f.visibility,
                ))

        return definitions

    def _compute_preservation(
        self, gaps: list[GapMarker], unit_id: str
    ) -> PreservationStatus:
        """Compute the preservation status based on detected gaps."""
        # Find highest severity gap
        max_severity = Severity.LOW
        blocking_gaps: list[str] = []

        for gap in gaps:
            if gap.severity == Severity.CRITICAL:
                max_severity = Severity.CRITICAL
                blocking_gaps.append(gap.id)
            elif gap.severity == Severity.HIGH and max_severity != Severity.CRITICAL:
                max_severity = Severity.HIGH
                blocking_gaps.append(gap.id)

        # Determine achievable level
        if max_severity == Severity.CRITICAL:
            max_level = PreservationLevel.SYNTACTIC
        elif max_severity == Severity.HIGH:
            max_level = PreservationLevel.SEMANTIC
        else:
            max_level = PreservationLevel.IDIOMATIC

        return PreservationStatus(
            id=f"preservation:{unit_id}",
            unit_id=unit_id,
            current_level=PreservationLevel.SYNTACTIC,
            max_achievable_level=max_level,
            blocking_gaps=blocking_gaps,
        )


class _DecoratorInfo:
    """Helper class for decorator information."""

    def __init__(self, name: str, args: list[Any] | None = None) -> None:
        self.name = name
        self.args = args or []
