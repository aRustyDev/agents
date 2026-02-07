"""TypeScript source code extractor.

Main extractor implementation that transforms TypeScript source code
into the 5-layer IR representation.
"""

from __future__ import annotations

import logging
from typing import Any

from ir_core.base import (
    ExtractConfig,
    Extractor,
    register_extractor,
)
from ir_core.models import (
    FunctionDef,
    GapMarker,
    GapSeverity,
    IRVersion,
    ModuleStructure,
    Parameter,
    SemanticAnnotation,
    TypeDef,
    TypeKind,
)

from ir_extract_typescript.parser import (
    TSClass,
    TSEnum,
    TSInterface,
    TSTypeAlias,
    TypeScriptParser,
)
from ir_extract_typescript.types import TypeAnalyzer, TypeCategory

logger = logging.getLogger(__name__)


@register_extractor("typescript")
class TypeScriptExtractor(Extractor):
    """TypeScript source code extractor.

    Extracts TypeScript source into the 5-layer IR representation with
    special handling for:

    - Structural typing
    - Union and intersection types
    - Generic constraints and variance
    - Interface and type alias definitions
    - Decorators and access modifiers
    """

    def __init__(self) -> None:
        """Initialize the extractor."""
        self._parser = TypeScriptParser()
        self._type_analyzer = TypeAnalyzer()

    def extract(
        self, source: str, path: str, config: ExtractConfig
    ) -> IRVersion:
        """Extract IR from TypeScript source code.

        Args:
            source: TypeScript source code
            path: File path for error reporting
            config: Extraction configuration

        Returns:
            IRVersion with extracted layers
        """
        logger.info(f"Extracting TypeScript from {path}")

        # Parse source
        parsed = self._parser.parse(source)

        # Initialize IR
        ir = IRVersion(
            version="ir-v1.0",
            source_language="typescript",
            source_path=path,
        )

        # Extract module structure (Layer 4)
        ir.structural = self._extract_module_structure(parsed, path)

        # Extract type definitions (Layer 3)
        ir.types = self._extract_types(parsed)

        # Extract functions (Layer 2)
        ir.functions = self._extract_functions(parsed)

        # Add semantic annotations
        ir.annotations = self._generate_annotations(parsed, ir)

        # Detect gaps
        ir.gaps = self._detect_gaps(parsed, ir)

        # Handle parse errors
        for error in parsed.get("errors", []):
            ir.gaps.append(
                GapMarker(
                    kind="E001",
                    description=error.get("message", "Parse error"),
                    location=f"{path}:{error.get('line', 0)}",
                    severity=GapSeverity.HIGH,
                )
            )

        return ir

    def supported_version(self) -> str:
        """Return the IR schema version this extractor produces."""
        return "ir-v1.0"

    def _extract_module_structure(
        self, parsed: dict[str, Any], path: str
    ) -> ModuleStructure:
        """Extract module structure (Layer 4)."""
        structure = ModuleStructure(
            name=self._get_module_name(path),
            path=path,
            language="typescript",
        )

        # Extract imports
        for imp in parsed.get("imports", []):
            import_info = {
                "module": imp.module_path,
                "type_only": imp.type_only,
            }
            if imp.default_import:
                import_info["default"] = imp.default_import
            if imp.named_imports:
                import_info["named"] = [
                    {"name": name, "alias": alias}
                    for name, alias in imp.named_imports
                ]
            if imp.namespace_import:
                import_info["namespace"] = imp.namespace_import
            structure.imports.append(import_info)

        # Extract exports
        exported_names = set()

        for iface in parsed.get("interfaces", []):
            if iface.exported:
                exported_names.add(iface.name)

        for alias in parsed.get("type_aliases", []):
            if alias.exported:
                exported_names.add(alias.name)

        for enum in parsed.get("enums", []):
            if enum.exported:
                exported_names.add(enum.name)

        for cls in parsed.get("classes", []):
            if cls.exported:
                exported_names.add(cls.name)

        for func in parsed.get("functions", []):
            if func.exported:
                exported_names.add(func.name)

        for var in parsed.get("variables", []):
            if var.get("exported"):
                exported_names.add(var.get("name", ""))

        structure.exports = list(exported_names)

        return structure

    def _get_module_name(self, path: str) -> str:
        """Extract module name from path."""
        import os

        basename = os.path.basename(path)
        name, _ = os.path.splitext(basename)
        return name

    def _extract_types(self, parsed: dict[str, Any]) -> list[TypeDef]:
        """Extract type definitions (Layer 3)."""
        types = []

        # Extract interfaces
        for iface in parsed.get("interfaces", []):
            type_def = self._convert_interface(iface)
            types.append(type_def)

        # Extract type aliases
        for alias in parsed.get("type_aliases", []):
            type_def = self._convert_type_alias(alias)
            types.append(type_def)

        # Extract enums
        for enum in parsed.get("enums", []):
            type_def = self._convert_enum(enum)
            types.append(type_def)

        # Extract classes
        for cls in parsed.get("classes", []):
            type_def = self._convert_class(cls)
            types.append(type_def)

        return types

    def _convert_interface(self, iface: TSInterface) -> TypeDef:
        """Convert TSInterface to TypeDef."""
        type_def = TypeDef(
            name=iface.name,
            kind=TypeKind.INTERFACE,
            line=iface.line,
            column=iface.column,
        )

        # Type parameters
        for param in iface.type_params:
            type_def.type_params.append(
                {
                    "name": param.name,
                    "constraint": param.constraint,
                    "default": param.default,
                }
            )

        # Extends
        type_def.extends = iface.extends

        # Properties
        for prop in iface.properties:
            type_def.properties.append(
                {
                    "name": prop.name,
                    "type": prop.type_annotation,
                    "optional": prop.optional,
                    "readonly": prop.readonly,
                }
            )

        # Methods
        for method in iface.methods:
            type_def.methods.append(self._convert_method(method))

        # Index signatures
        for key_type, value_type in iface.index_signatures:
            type_def.index_signatures.append(
                {"key_type": key_type, "value_type": value_type}
            )

        # Call signatures
        for call in iface.call_signatures:
            type_def.call_signatures.append(self._convert_method(call))

        type_def.visibility = "public" if iface.exported else "internal"

        return type_def

    def _convert_type_alias(self, alias: TSTypeAlias) -> TypeDef:
        """Convert TSTypeAlias to TypeDef."""
        type_def = TypeDef(
            name=alias.name,
            kind=TypeKind.TYPE_ALIAS,
            line=alias.line,
            column=alias.column,
        )

        # Type parameters
        for param in alias.type_params:
            type_def.type_params.append(
                {
                    "name": param.name,
                    "constraint": param.constraint,
                    "default": param.default,
                }
            )

        # Analyze the type value
        type_info = self._type_analyzer.analyze(alias.type_value)
        if type_info:
            type_def.aliased_type = alias.type_value
            type_def.type_category = type_info.category.value

            # If it's a union type, store constituents
            if type_info.category == TypeCategory.UNION:
                type_def.union_types = [t.raw for t in type_info.constituent_types]
            elif type_info.category == TypeCategory.INTERSECTION:
                type_def.intersection_types = [
                    t.raw for t in type_info.constituent_types
                ]

        type_def.visibility = "public" if alias.exported else "internal"

        return type_def

    def _convert_enum(self, enum: TSEnum) -> TypeDef:
        """Convert TSEnum to TypeDef."""
        type_def = TypeDef(
            name=enum.name,
            kind=TypeKind.ENUM,
            line=enum.line,
            column=enum.column,
        )

        for member in enum.members:
            type_def.enum_members.append(
                {"name": member.name, "value": member.value}
            )

        type_def.const_enum = enum.const
        type_def.visibility = "public" if enum.exported else "internal"

        return type_def

    def _convert_class(self, cls: TSClass) -> TypeDef:
        """Convert TSClass to TypeDef."""
        type_def = TypeDef(
            name=cls.name,
            kind=TypeKind.CLASS,
            line=cls.line,
            column=cls.column,
        )

        # Type parameters
        for param in cls.type_params:
            type_def.type_params.append(
                {
                    "name": param.name,
                    "constraint": param.constraint,
                    "default": param.default,
                }
            )

        # Extends
        if cls.extends:
            type_def.extends = [cls.extends]

        # Implements
        type_def.implements = cls.implements

        # Properties
        for prop in cls.properties:
            type_def.properties.append(
                {
                    "name": prop.name,
                    "type": prop.type_annotation,
                    "optional": prop.optional,
                    "readonly": prop.readonly,
                    "visibility": prop.visibility.value,
                    "static": prop.static,
                }
            )

        # Methods
        for method in cls.methods:
            type_def.methods.append(self._convert_method(method))

        # Constructor
        if cls.constructor:
            type_def.constructor = self._convert_method(cls.constructor)

        # Decorators
        type_def.decorators = cls.decorators
        type_def.abstract = cls.abstract
        type_def.visibility = "public" if cls.exported else "internal"

        return type_def

    def _convert_method(self, method: Any) -> dict[str, Any]:
        """Convert method to IR format."""
        result: dict[str, Any] = {
            "name": method.name,
            "parameters": [],
        }

        for param in method.parameters:
            result["parameters"].append(
                {
                    "name": param.name,
                    "type": param.type_annotation,
                    "optional": param.optional,
                    "rest": param.rest,
                }
            )

        if method.return_type:
            result["return_type"] = method.return_type

        if method.type_params:
            result["type_params"] = [
                {
                    "name": p.name,
                    "constraint": p.constraint,
                    "default": p.default,
                }
                for p in method.type_params
            ]

        if hasattr(method, "visibility"):
            result["visibility"] = method.visibility.value
        if hasattr(method, "static"):
            result["static"] = method.static
        if hasattr(method, "async_"):
            result["async"] = method.async_
        if hasattr(method, "abstract"):
            result["abstract"] = method.abstract

        return result

    def _extract_functions(self, parsed: dict[str, Any]) -> list[FunctionDef]:
        """Extract function definitions (Layer 2)."""
        functions = []

        for func in parsed.get("functions", []):
            func_def = FunctionDef(
                name=func.name,
                line=func.line,
                column=func.column,
            )

            # Parameters
            for param in func.parameters:
                func_def.parameters.append(
                    Parameter(
                        name=param.name,
                        type_annotation=param.type_annotation,
                        optional=param.optional,
                        rest=param.rest,
                        default_value=param.default_value,
                    )
                )

            # Return type
            func_def.return_type = func.return_type

            # Type parameters
            for param in func.type_params:
                func_def.type_params.append(
                    {
                        "name": param.name,
                        "constraint": param.constraint,
                        "default": param.default,
                    }
                )

            # Async/generator
            func_def.async_ = func.async_
            func_def.generator = func.generator

            # Visibility
            func_def.visibility = "public" if func.exported else "internal"

            functions.append(func_def)

        return functions

    def _generate_annotations(
        self, parsed: dict[str, Any], ir: IRVersion
    ) -> list[SemanticAnnotation]:
        """Generate semantic annotations for TypeScript-specific concepts."""
        annotations = []

        # TS-004: Structural typing annotation
        for i, type_def in enumerate(ir.types):
            if type_def.kind in {TypeKind.INTERFACE, TypeKind.CLASS}:
                annotations.append(
                    SemanticAnnotation(
                        kind="TS-004",
                        target=f"type:{i}",
                        value={"typing": "structural"},
                        description="TypeScript uses structural typing",
                    )
                )

        # TS-006: Type inference for variables without explicit types
        for var in parsed.get("variables", []):
            if not var.get("type"):
                annotations.append(
                    SemanticAnnotation(
                        kind="TS-006",
                        target=f"var:{var.get('name')}",
                        value={"inferred": True},
                        description="Type inferred by TypeScript",
                    )
                )

        # TS-009: Union types
        for i, type_def in enumerate(ir.types):
            if hasattr(type_def, "union_types") and type_def.union_types:
                annotations.append(
                    SemanticAnnotation(
                        kind="TS-009",
                        target=f"type:{i}",
                        value={"union_members": type_def.union_types},
                        description="Union type definition",
                    )
                )

        return annotations

    def _detect_gaps(
        self, parsed: dict[str, Any], ir: IRVersion
    ) -> list[GapMarker]:
        """Detect semantic gaps in the extracted IR."""
        gaps = []

        # Detect conditional types (complex to convert)
        for alias in parsed.get("type_aliases", []):
            if " extends " in alias.type_value and " ? " in alias.type_value:
                gaps.append(
                    GapMarker(
                        kind="TS-010",
                        description=f"Conditional type '{alias.name}' may not convert accurately",
                        location=f"line {alias.line}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Manual review required for conditional type",
                    )
                )

        # Detect mapped types
        for alias in parsed.get("type_aliases", []):
            if alias.type_value.startswith("{") and " in " in alias.type_value:
                gaps.append(
                    GapMarker(
                        kind="TS-011",
                        description=f"Mapped type '{alias.name}' may not convert accurately",
                        location=f"line {alias.line}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Manual review required for mapped type",
                    )
                )

        # Detect template literal types
        for alias in parsed.get("type_aliases", []):
            if alias.type_value.startswith("`"):
                gaps.append(
                    GapMarker(
                        kind="TS-012",
                        description=f"Template literal type '{alias.name}' may not convert",
                        location=f"line {alias.line}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Consider using string type in target language",
                    )
                )

        # Detect decorators (may not have equivalents)
        for cls in parsed.get("classes", []):
            if cls.decorators:
                gaps.append(
                    GapMarker(
                        kind="TS-013",
                        description=f"Class '{cls.name}' uses decorators",
                        location=f"line {cls.line}",
                        severity=GapSeverity.LOW,
                        suggestion="Decorators may need manual conversion",
                    )
                )

        # Detect function overloads (interfaces with multiple call signatures)
        for iface in parsed.get("interfaces", []):
            if len(iface.call_signatures) > 1:
                gaps.append(
                    GapMarker(
                        kind="TS-014",
                        description=f"Interface '{iface.name}' has multiple call signatures",
                        location=f"line {iface.line}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Function overloads may need manual handling",
                    )
                )

        return gaps
