"""Rust source code extractor to IR.

This module provides the main RustExtractor class that transforms Rust source
code into the 5-layer IR representation. It handles Rust-specific concepts
like ownership, lifetimes, and borrow checking semantics.

Example:
    extractor = RustExtractor()
    ir = extractor.extract(rust_source, "example.rs", ExtractConfig())
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from ir_core.base import (
    ExtractConfig,
    ExtractionMode,
    Extractor,
    SemanticEnrichmentLevel,
    register_extractor,
)
from ir_core.models import (
    AnnotationSource,
    Binding,
    BorrowKind,
    Constraint,
    Definition,
    Effect,
    EffectKind,
    ExtractionError,
    ExtractionErrorCode,
    ExtractionMode as IRExtractionMode,
    Export,
    Field_,
    Function,
    GapMarker,
    GapType,
    Import,
    ImportedItem,
    IRVersion,
    Lifetime,
    LifetimeKind,
    MethodSignature,
    Module,
    ModuleMetadata,
    Mutability,
    Param,
    Receiver,
    SemanticAnnotation,
    Severity,
    SourceSpan,
    TypeBody,
    TypeDef,
    TypeKind,
    TypeParam,
    TypeRef,
    TypeRefKind,
    Variant,
    Visibility,
)

from .lifetimes import LifetimeExtractor, LifetimeSource
from .ownership import OwnershipAnalyzer, OwnershipKind
from .parser import (
    RustEnum,
    RustField,
    RustFunction,
    RustImpl,
    RustParser,
    RustStruct,
    RustTrait,
    RustUse,
)

if TYPE_CHECKING:
    from tree_sitter import Node

logger = logging.getLogger(__name__)


# Rust to IR type mapping
RUST_TYPE_MAP = {
    "i8": "builtins.int",
    "i16": "builtins.int",
    "i32": "builtins.int",
    "i64": "builtins.int",
    "i128": "builtins.int",
    "isize": "builtins.int",
    "u8": "builtins.int",
    "u16": "builtins.int",
    "u32": "builtins.int",
    "u64": "builtins.int",
    "u128": "builtins.int",
    "usize": "builtins.int",
    "f32": "builtins.float",
    "f64": "builtins.float",
    "bool": "builtins.bool",
    "char": "builtins.str",
    "str": "builtins.str",
    "String": "builtins.str",
    "()": "builtins.None",
    "!": "builtins.None",
    "Vec": "builtins.list",
    "HashMap": "builtins.dict",
    "HashSet": "builtins.set",
    "Option": "typing.Optional",
    "Result": "rust.Result",
    "Box": "rust.Box",
    "Rc": "rust.Rc",
    "Arc": "rust.Arc",
    "RefCell": "rust.RefCell",
    "Mutex": "rust.Mutex",
    "RwLock": "rust.RwLock",
}

# Visibility mapping
VISIBILITY_MAP = {
    "public": Visibility.PUBLIC,
    "private": Visibility.PRIVATE,
    "pub_crate": Visibility.INTERNAL,
    "pub_super": Visibility.PACKAGE,
    "pub_self": Visibility.PRIVATE,
    "pub_in": Visibility.PACKAGE,
}


@register_extractor("rust")
class RustExtractor(Extractor):
    """Rust source code extractor.

    Transforms Rust source code into the 5-layer IR representation,
    with special handling for:
    - Ownership semantics (owned, borrowed, mutable borrows)
    - Lifetime annotations and elision
    - Borrow checker constraints
    - Trait bounds and where clauses

    Example:
        extractor = RustExtractor()
        ir = extractor.extract('''
            fn process(data: Vec<i32>) -> Vec<i32> {
                data.into_iter().map(|x| x * 2).collect()
            }
        ''', "example.rs", ExtractConfig())
    """

    def __init__(self) -> None:
        """Initialize the Rust extractor."""
        self.parser = RustParser()
        self.ownership_analyzer = OwnershipAnalyzer()
        self.lifetime_extractor = LifetimeExtractor()

        # State for current extraction
        self._id_counter = 0
        self._gaps: list[GapMarker] = []
        self._annotations: list[SemanticAnnotation] = []
        self._types: list[TypeDef] = []
        self._functions: list[Function] = []
        self._bindings: list[Binding] = []
        self._imports: list[Import] = []
        self._definitions: list[Definition] = []

    def extract(
        self, source: str, path: str, config: ExtractConfig
    ) -> IRVersion:
        """Extract IR from Rust source code.

        Args:
            source: Rust source code
            path: File path
            config: Extraction configuration

        Returns:
            IRVersion with all extracted layers

        Raises:
            ExtractionError: If parsing or extraction fails
        """
        # Reset state
        self._id_counter = 0
        self._gaps = []
        self._annotations = []
        self._types = []
        self._functions = []
        self._bindings = []
        self._imports = []
        self._definitions = []

        try:
            tree = self.parser.parse(source)
        except Exception as e:
            raise ExtractionError(
                code=ExtractionErrorCode.E001,
                message=f"Failed to parse Rust source: {e}",
            ) from e

        # Extract module name from path
        module_name = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        module_id = f"module:{module_name}"

        # Extract imports
        for use in self.parser.iter_uses(source):
            self._extract_use(use)

        # Extract types
        for struct in self.parser.iter_structs(source, path):
            self._extract_struct(struct, config)

        for enum in self.parser.iter_enums(source, path):
            self._extract_enum(enum, config)

        for trait in self.parser.iter_traits(source, path):
            self._extract_trait(trait, config)

        # Extract impl blocks
        for impl in self.parser.iter_impls(source, path):
            self._extract_impl(impl, source, config)

        # Extract top-level functions
        for func in self.parser.iter_functions(source, path):
            ir_func = self._extract_function(func, source, config)
            if ir_func:
                self._functions.append(ir_func)
                self._definitions.append(Definition(
                    id=self._next_id("def"),
                    kind="function",
                    ref=ir_func.id,
                    visibility=self._map_visibility(func.visibility),
                ))

        # Analyze ownership if semantic enrichment is enabled
        if config.semantic_level != SemanticEnrichmentLevel.NONE:
            try:
                self._analyze_ownership(tree.root_node, source)
            except Exception as e:
                logger.warning(
                    "Ownership analysis failed for %s: %s",
                    path,
                    str(e),
                    exc_info=True,
                )

        # Build module
        module = Module(
            id=module_id,
            name=module_name,
            path=path.replace("/", ".").rsplit(".", 1)[0].split("."),
            visibility=Visibility.PUBLIC,
            imports=self._imports,
            exports=[],  # Rust uses pub, not explicit exports
            definitions=self._definitions,
            submodules=[],
            extraction_scope="full" if config.mode == ExtractionMode.FULL_MODULE else "partial",
            metadata=ModuleMetadata(
                source_file=path,
                source_language="rust",
                extraction_version="ir-v1.0",
                extraction_mode=IRExtractionMode(config.mode.value),
                source_hash=hashlib.sha256(source.encode()).hexdigest(),
                extraction_timestamp=datetime.now(timezone.utc),
            ),
        )

        return IRVersion(
            version="ir-v1.0",
            module=module,
            types=self._types,
            functions=self._functions,
            bindings=self._bindings,
            annotations=self._annotations,
            gaps=self._gaps,
        )

    def supported_version(self) -> str:
        """Return the IR schema version this extractor produces."""
        return "ir-v1.0"

    def _next_id(self, prefix: str) -> str:
        """Generate the next unique ID."""
        self._id_counter += 1
        return f"{prefix}:{self._id_counter}"

    def _add_gap(
        self,
        location: str,
        gap_type: GapType,
        severity: Severity,
        description: str,
        source_concept: str,
        target_concept: str | None = None,
        pattern_id: str | None = None,
    ) -> None:
        """Add a gap marker."""
        self._gaps.append(GapMarker(
            id=self._next_id("gap"),
            location=location,
            gap_type=gap_type,
            gap_pattern_id=pattern_id,
            severity=severity,
            description=description,
            source_concept=source_concept,
            target_concept=target_concept,
        ))

    def _add_annotation(
        self,
        target: str,
        kind: str,
        value: dict,
        confidence: float = 1.0,
        source: AnnotationSource = AnnotationSource.INFERRED,
    ) -> None:
        """Add a semantic annotation."""
        self._annotations.append(SemanticAnnotation(
            id=self._next_id("ann"),
            target=target,
            kind=kind,
            value=value,
            confidence=confidence,
            source=source,
        ))

    def _map_visibility(self, vis: str) -> Visibility:
        """Map Rust visibility to IR visibility."""
        return VISIBILITY_MAP.get(vis, Visibility.PRIVATE)

    def _map_type(self, type_str: str) -> TypeRef:
        """Map a Rust type string to a TypeRef.

        Args:
            type_str: Rust type string

        Returns:
            TypeRef representing the type
        """
        clean = type_str.strip()

        # Handle references
        if clean.startswith("&mut "):
            inner = clean[5:].strip()
            inner_ref = self._map_type(inner)
            return TypeRef(
                kind=TypeRefKind.REFERENCE,
                type_id=inner_ref.type_id,
                args=inner_ref.args,
                mutable=True,
            )
        elif clean.startswith("&"):
            inner = clean[1:].strip()
            # Remove lifetime if present
            if inner.startswith("'"):
                parts = inner.split(" ", 1)
                if len(parts) > 1:
                    inner = parts[1]
            inner_ref = self._map_type(inner)
            return TypeRef(
                kind=TypeRefKind.REFERENCE,
                type_id=inner_ref.type_id,
                args=inner_ref.args,
                mutable=False,
            )

        # Handle tuples
        if clean.startswith("(") and clean.endswith(")"):
            inner = clean[1:-1]
            if inner == "":
                return TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.None")
            elements = self._split_type_args(inner)
            return TypeRef(
                kind=TypeRefKind.TUPLE,
                elements=[self._map_type(e) for e in elements],
            )

        # Handle arrays/slices
        if clean.startswith("[") and clean.endswith("]"):
            inner = clean[1:-1]
            if ";" in inner:
                # Fixed size array
                elem_type, _ = inner.rsplit(";", 1)
                return TypeRef(
                    kind=TypeRefKind.NAMED,
                    type_id="builtins.list",
                    args=[self._map_type(elem_type.strip())],
                )
            else:
                # Slice
                return TypeRef(
                    kind=TypeRefKind.NAMED,
                    type_id="builtins.list",
                    args=[self._map_type(inner)],
                )

        # Handle generics
        if "<" in clean:
            base, rest = clean.split("<", 1)
            args_str = rest.rstrip(">")
            args = self._split_type_args(args_str)
            base = base.strip()

            # Map base type
            type_id = RUST_TYPE_MAP.get(base, f"rust.{base}")

            return TypeRef(
                kind=TypeRefKind.NAMED,
                type_id=type_id,
                args=[self._map_type(a) for a in args],
            )

        # Handle function pointers
        if clean.startswith("fn("):
            return self._parse_fn_type(clean)

        # Simple types
        type_id = RUST_TYPE_MAP.get(clean, f"rust.{clean}")
        return TypeRef(kind=TypeRefKind.NAMED, type_id=type_id)

    def _split_type_args(self, args_str: str) -> list[str]:
        """Split generic type arguments respecting nesting.

        Args:
            args_str: Type arguments string

        Returns:
            List of type argument strings
        """
        args: list[str] = []
        depth = 0
        current = ""

        for char in args_str:
            if char in "<([":
                depth += 1
                current += char
            elif char in ">)]":
                depth -= 1
                current += char
            elif char == "," and depth == 0:
                args.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            args.append(current.strip())

        return args

    def _parse_fn_type(self, type_str: str) -> TypeRef:
        """Parse a function pointer type.

        Args:
            type_str: Function type string (e.g., "fn(i32) -> i32")

        Returns:
            TypeRef for the function type
        """
        # Extract params and return type
        paren_start = type_str.index("(")
        paren_end = type_str.rindex(")")

        params_str = type_str[paren_start + 1:paren_end]
        params = self._split_type_args(params_str) if params_str.strip() else []

        return_type = None
        if "->" in type_str[paren_end:]:
            ret_str = type_str.split("->", 1)[1].strip()
            return_type = self._map_type(ret_str)

        return TypeRef(
            kind=TypeRefKind.FUNCTION,
            params=[self._map_type(p) for p in params],
            return_type=return_type or TypeRef(
                kind=TypeRefKind.NAMED, type_id="builtins.None"
            ),
        )

    def _extract_type_params(
        self, params: list
    ) -> list[TypeParam]:
        """Extract type parameters from parsed params.

        Args:
            params: List of RustTypeParam

        Returns:
            List of IR TypeParam
        """
        result: list[TypeParam] = []
        for p in params:
            # Skip lifetime parameters for now (they go elsewhere)
            if p.name.startswith("'"):
                continue
            result.append(TypeParam(
                name=p.name,
                bounds=[self._map_type(b) for b in p.bounds],
                default=self._map_type(p.default) if p.default else None,
            ))
        return result

    def _extract_constraints(
        self, where_clause: list | None
    ) -> list[Constraint]:
        """Extract constraints from where clause.

        Args:
            where_clause: List of RustWhereClause

        Returns:
            List of IR Constraint
        """
        if not where_clause:
            return []

        constraints: list[Constraint] = []
        for clause in where_clause:
            for bound in clause.bounds:
                constraints.append(Constraint(
                    kind="type_bound",
                    param=clause.param,
                    bound=self._map_type(bound),
                ))

        return constraints

    def _extract_use(self, use: RustUse) -> None:
        """Extract a use statement into an Import.

        Args:
            use: Parsed use statement
        """
        import_id = self._next_id("import")

        if use.items:
            # use foo::{bar, baz}
            items = [
                ImportedItem(
                    name=name,
                    alias=alias,
                    kind="variable",  # Could be type, function, etc.
                )
                for name, alias in use.items
            ]
        elif use.is_glob:
            # use foo::*
            items = [ImportedItem(name="*", kind="wildcard")]
            self._add_gap(
                location=import_id,
                gap_type=GapType.STRUCTURAL,
                severity=Severity.MEDIUM,
                description="Glob import - consider explicit imports",
                source_concept="use foo::*",
                target_concept="explicit imports",
            )
        else:
            # use foo::bar
            name = use.path[-1] if use.path else ""
            items = [
                ImportedItem(
                    name=name,
                    alias=use.alias,
                    kind="variable",
                )
            ] if name else []

        self._imports.append(Import(
            id=import_id,
            module_path=use.path,
            imported_items=items,
            alias=use.alias if not use.items else None,
            is_reexport=use.visibility == "public",
        ))

    def _extract_struct(
        self, struct: RustStruct, config: ExtractConfig
    ) -> None:
        """Extract a struct into a TypeDef.

        Args:
            struct: Parsed struct
            config: Extraction configuration
        """
        type_id = self._next_id("type")

        # Extract fields
        fields: list[Field_] = []
        for f in struct.fields:
            field = Field_(
                name=f.name or f"_{f.index}",
                type=self._map_type(f.type_str),
                visibility=self._map_visibility(f.visibility),
                mutability=Mutability.MUTABLE,
            )
            fields.append(field)

        # Extract lifetimes from type parameters
        lifetime_params = [
            p for p in struct.type_params if p.name.startswith("'")
        ]
        if lifetime_params:
            self._add_annotation(
                target=type_id,
                kind="MM-010",  # Lifetime annotation
                value={
                    "lifetimes": [p.name for p in lifetime_params],
                    "bounds": {
                        p.name: p.bounds for p in lifetime_params if p.bounds
                    },
                },
            )

        type_def = TypeDef(
            id=type_id,
            name=struct.name,
            kind=TypeKind.STRUCT,
            params=self._extract_type_params(struct.type_params),
            constraints=self._extract_constraints(struct.where_clause),
            body=TypeBody(fields=fields),
            visibility=self._map_visibility(struct.visibility),
            span=SourceSpan(
                file=struct.span.file,
                start_line=struct.span.start_line,
                start_col=struct.span.start_col,
                end_line=struct.span.end_line,
                end_col=struct.span.end_col,
            ) if config.preserve_spans else None,
        )

        self._types.append(type_def)
        self._definitions.append(Definition(
            id=self._next_id("def"),
            kind="type",
            ref=type_id,
            visibility=self._map_visibility(struct.visibility),
        ))

    def _extract_enum(self, enum: RustEnum, config: ExtractConfig) -> None:
        """Extract an enum into a TypeDef.

        Args:
            enum: Parsed enum
            config: Extraction configuration
        """
        type_id = self._next_id("type")

        # Extract variants
        variants: list[Variant] = []
        for v in enum.variants:
            if v.kind == "unit":
                variants.append(Variant(
                    name=v.name,
                    kind="unit",
                    discriminant=v.discriminant,
                ))
            elif v.kind == "tuple":
                variants.append(Variant(
                    name=v.name,
                    kind="tuple",
                    types=[self._map_type(f.type_str) for f in v.fields],
                    discriminant=v.discriminant,
                ))
            elif v.kind == "struct":
                variants.append(Variant(
                    name=v.name,
                    kind="struct",
                    fields=[
                        Field_(
                            name=f.name or f"_{f.index}",
                            type=self._map_type(f.type_str),
                            visibility=Visibility.PRIVATE,
                        )
                        for f in v.fields
                    ],
                    discriminant=v.discriminant,
                ))

        type_def = TypeDef(
            id=type_id,
            name=enum.name,
            kind=TypeKind.ENUM,
            params=self._extract_type_params(enum.type_params),
            constraints=self._extract_constraints(enum.where_clause),
            body=TypeBody(variants=variants),
            visibility=self._map_visibility(enum.visibility),
            span=SourceSpan(
                file=enum.span.file,
                start_line=enum.span.start_line,
                start_col=enum.span.start_col,
                end_line=enum.span.end_line,
                end_col=enum.span.end_col,
            ) if config.preserve_spans else None,
        )

        self._types.append(type_def)
        self._definitions.append(Definition(
            id=self._next_id("def"),
            kind="type",
            ref=type_id,
            visibility=self._map_visibility(enum.visibility),
        ))

    def _extract_trait(
        self, trait: RustTrait, config: ExtractConfig
    ) -> None:
        """Extract a trait into a TypeDef.

        Args:
            trait: Parsed trait
            config: Extraction configuration
        """
        type_id = self._next_id("type")

        # Extract required methods
        required_methods: list[MethodSignature] = []
        provided_methods: list[str] = []

        for item in trait.items:
            if item.kind == "method" and item.signature:
                sig = item.signature
                method_sig = MethodSignature(
                    name=sig.name,
                    params=[
                        Param(
                            name=p.name,
                            type=self._map_type(p.type_str),
                            mutability=(
                                Mutability.MUTABLE if p.is_mut
                                else Mutability.IMMUTABLE
                            ),
                        )
                        for p in sig.params if not p.is_self
                    ],
                    return_type=(
                        self._map_type(sig.return_type)
                        if sig.return_type
                        else TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.None")
                    ),
                    type_params=self._extract_type_params(sig.type_params),
                    effects=[Effect(kind=EffectKind.ASYNC)] if sig.is_async else [],
                )

                if sig.body is None:
                    required_methods.append(method_sig)
                else:
                    provided_methods.append(sig.name)

        # Build supertrait constraints
        constraints = self._extract_constraints(trait.where_clause)
        for st in trait.supertraits:
            constraints.append(Constraint(
                kind="type_bound",
                param="Self",
                bound=self._map_type(st),
            ))

        type_def = TypeDef(
            id=type_id,
            name=trait.name,
            kind=TypeKind.INTERFACE,
            params=self._extract_type_params(trait.type_params),
            constraints=constraints,
            body=TypeBody(
                required_methods=required_methods,
                provided_methods=provided_methods,
            ),
            visibility=self._map_visibility(trait.visibility),
            span=SourceSpan(
                file=trait.span.file,
                start_line=trait.span.start_line,
                start_col=trait.span.start_col,
                end_line=trait.span.end_line,
                end_col=trait.span.end_col,
            ) if config.preserve_spans else None,
        )

        if trait.is_unsafe:
            self._add_annotation(
                target=type_id,
                kind="unsafe_trait",
                value={"reason": "Rust unsafe trait"},
                source=AnnotationSource.EXPLICIT,
            )

        self._types.append(type_def)
        self._definitions.append(Definition(
            id=self._next_id("def"),
            kind="type",
            ref=type_id,
            visibility=self._map_visibility(trait.visibility),
        ))

    def _extract_impl(
        self, impl: RustImpl, source: str, config: ExtractConfig
    ) -> None:
        """Extract an impl block.

        Args:
            impl: Parsed impl block
            source: Full source code
            config: Extraction configuration
        """
        # Create methods with proper receiver
        for func in impl.items:
            ir_func = self._extract_function(func, source, config)
            if ir_func:
                # Set the receiver based on the self type
                self_param = next(
                    (p for p in func.params if p.is_self), None
                )
                if self_param:
                    mutability = Mutability.IMMUTABLE
                    if self_param.self_mutability == "mut":
                        mutability = Mutability.MUTABLE

                    ir_func.receiver = Receiver(
                        type=self._map_type(impl.self_type),
                        mutability=mutability,
                    )

                # Add trait implementation annotation
                if impl.trait_name:
                    self._add_annotation(
                        target=ir_func.id,
                        kind="trait_impl",
                        value={
                            "trait": impl.trait_name,
                            "self_type": impl.self_type,
                        },
                        source=AnnotationSource.EXPLICIT,
                    )

                self._functions.append(ir_func)

    def _extract_function(
        self, func: RustFunction, source: str, config: ExtractConfig
    ) -> Function | None:
        """Extract a function into IR.

        Args:
            func: Parsed function
            source: Full source code
            config: Extraction configuration

        Returns:
            Function or None if extraction fails
        """
        func_id = self._next_id("func")

        # Build parameters
        params: list[Param] = []
        for p in func.params:
            if p.is_self:
                continue  # Handled as receiver

            # Determine mutability from ownership
            ownership, lifetime = self.ownership_analyzer.get_ownership_for_param(
                p.type_str
            )
            mutability = Mutability.IMMUTABLE
            if ownership == OwnershipKind.MUT_BORROWED or p.is_mut:
                mutability = Mutability.MUTABLE
            elif ownership == OwnershipKind.OWNED:
                mutability = Mutability.MOVE

            param = Param(
                name=p.name,
                type=self._map_type(p.type_str),
                mutability=mutability,
            )

            # Add ownership annotation
            self._add_annotation(
                target=f"{func_id}:param:{p.name}",
                kind="MM-002",  # Ownership annotation
                value={
                    "ownership": ownership.value,
                    "lifetime": lifetime,
                },
            )

            params.append(param)

        # Build effects
        effects: list[Effect] = []
        if func.is_async:
            effects.append(Effect(kind=EffectKind.ASYNC))
        if func.is_unsafe:
            effects.append(Effect(kind=EffectKind.UNSAFE))

        # Extract lifetime information
        if func.body:
            try:
                lifetimes = self.lifetime_extractor.extract_function_lifetimes(
                    func.body.parent, source
                )
                if lifetimes.lifetime_params:
                    self._add_annotation(
                        target=func_id,
                        kind="MM-010",  # Lifetime annotation
                        value={
                            "params": [p.name for p in lifetimes.lifetime_params],
                            "constraints": [
                                {"short": c.short, "long": c.long}
                                for c in lifetimes.constraints
                            ],
                            "elision_applied": lifetimes.elision_applied,
                        },
                    )
            except Exception as e:
                logger.warning("Failed to extract lifetimes: %s", e)

        return Function(
            id=func_id,
            name=func.name,
            params=params,
            return_type=(
                self._map_type(func.return_type)
                if func.return_type
                else TypeRef(kind=TypeRefKind.NAMED, type_id="builtins.None")
            ),
            type_params=self._extract_type_params(func.type_params),
            effects=effects,
            body=None,  # CFG extraction not implemented yet
            visibility=self._map_visibility(func.visibility),
            span=SourceSpan(
                file=func.span.file,
                start_line=func.span.start_line,
                start_col=func.span.start_col,
                end_line=func.span.end_line,
                end_col=func.span.end_col,
            ) if config.preserve_spans else None,
            doc_comment=func.doc_comment,
        )

    def _analyze_ownership(self, root: "Node", source: str) -> None:
        """Analyze ownership semantics in the source.

        Args:
            root: Root AST node
            source: Full source code
        """
        analysis = self.ownership_analyzer.analyze(source, root)

        # Record move errors as gaps
        for error in analysis.move_errors:
            self._add_gap(
                location="ownership",
                gap_type=GapType.SEMANTIC,
                severity=Severity.HIGH,
                description=error,
                source_concept="use-after-move",
                target_concept="valid ownership",
                pattern_id="MM-009",
            )

        # Record borrow errors as gaps
        for error in analysis.borrow_errors:
            self._add_gap(
                location="ownership",
                gap_type=GapType.SEMANTIC,
                severity=Severity.HIGH,
                description=error,
                source_concept="borrow conflict",
                target_concept="valid borrowing",
                pattern_id="MM-011",
            )

        # Create bindings for tracked variables
        for name, info in analysis.bindings.items():
            binding_id = self._next_id("binding")

            # Map ownership to lifetime
            lifetime_kind = LifetimeKind.SCOPED
            borrow_kind = None

            if info.kind == OwnershipKind.OWNED:
                lifetime_kind = LifetimeKind.OWNED
            elif info.kind == OwnershipKind.BORROWED:
                lifetime_kind = LifetimeKind.BORROWED
                borrow_kind = BorrowKind.SHARED
            elif info.kind == OwnershipKind.MUT_BORROWED:
                lifetime_kind = LifetimeKind.BORROWED
                borrow_kind = BorrowKind.MUTABLE
            elif info.kind == OwnershipKind.MOVED:
                lifetime_kind = LifetimeKind.OWNED

            binding = Binding(
                id=binding_id,
                name=name,
                type=self._map_type(info.type_str),
                mutability=(
                    Mutability.MUTABLE if info.kind == OwnershipKind.MUT_BORROWED
                    else Mutability.IMMUTABLE
                ),
                lifetime=Lifetime(
                    kind=lifetime_kind,
                    borrow_kind=borrow_kind,
                ),
            )

            # Add ownership annotation
            self._add_annotation(
                target=binding_id,
                kind="MM-002",
                value={
                    "ownership": info.kind.value,
                    "is_copy": info.is_copy,
                    "moved_at": info.moved_at,
                },
            )

            self._bindings.append(binding)
