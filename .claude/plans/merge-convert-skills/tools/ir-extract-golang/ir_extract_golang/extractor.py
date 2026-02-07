"""Go source code extractor.

Main extractor implementation that transforms Go source code
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

from ir_extract_golang.parser import (
    GolangParser,
    GoFunction,
    GoInterface,
    GoStruct,
    GoTypeAlias,
)

logger = logging.getLogger(__name__)


@register_extractor("golang")
class GolangExtractor(Extractor):
    """Go source code extractor.

    Extracts Go source into the 5-layer IR representation with
    special handling for:

    - Error handling patterns (multiple returns with error)
    - Goroutines and channels
    - Defer statements
    - Interfaces (structural typing)
    - Generics (Go 1.18+)
    """

    def __init__(self) -> None:
        """Initialize the extractor."""
        self._parser = GolangParser()

    def extract(
        self, source: str, path: str, config: ExtractConfig
    ) -> IRVersion:
        """Extract IR from Go source code.

        Args:
            source: Go source code
            path: File path for error reporting
            config: Extraction configuration

        Returns:
            IRVersion with extracted layers
        """
        logger.info(f"Extracting Go from {path}")

        # Parse source
        parsed = self._parser.parse(source)

        # Initialize IR
        ir = IRVersion(
            version="ir-v1.0",
            source_language="golang",
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
            name=parsed.get("package", ""),
            path=path,
            language="golang",
        )

        # Extract imports
        for imp in parsed.get("imports", []):
            import_info: dict[str, Any] = {
                "module": imp.path,
            }
            if imp.alias:
                import_info["alias"] = imp.alias
            if imp.dot_import:
                import_info["dot_import"] = True
            if imp.blank_import:
                import_info["blank_import"] = True
            structure.imports.append(import_info)

        # Extract exports (exported = capitalized first letter)
        exported_names = set()

        for struct in parsed.get("structs", []):
            if struct.exported:
                exported_names.add(struct.name)

        for iface in parsed.get("interfaces", []):
            if iface.exported:
                exported_names.add(iface.name)

        for alias in parsed.get("type_aliases", []):
            if alias.exported:
                exported_names.add(alias.name)

        for func in parsed.get("functions", []):
            if func.exported and not func.is_method:
                exported_names.add(func.name)

        for const in parsed.get("constants", []):
            if const.exported:
                exported_names.add(const.name)

        for var in parsed.get("variables", []):
            if var.exported:
                exported_names.add(var.name)

        structure.exports = list(exported_names)

        return structure

    def _extract_types(self, parsed: dict[str, Any]) -> list[TypeDef]:
        """Extract type definitions (Layer 3)."""
        types = []

        # Extract structs
        for struct in parsed.get("structs", []):
            type_def = self._convert_struct(struct)
            types.append(type_def)

        # Extract interfaces
        for iface in parsed.get("interfaces", []):
            type_def = self._convert_interface(iface)
            types.append(type_def)

        # Extract type aliases
        for alias in parsed.get("type_aliases", []):
            type_def = self._convert_type_alias(alias)
            types.append(type_def)

        return types

    def _convert_struct(self, struct: GoStruct) -> TypeDef:
        """Convert GoStruct to TypeDef."""
        type_def = TypeDef(
            name=struct.name,
            kind=TypeKind.STRUCT,
            line=struct.line,
            column=struct.column,
        )

        # Type parameters
        for param in struct.type_params:
            type_def.type_params.append(
                {
                    "name": param.name,
                    "constraint": param.constraint,
                }
            )

        # Properties (fields)
        for field in struct.fields:
            type_def.properties.append(
                {
                    "name": field.name,
                    "type": field.type_annotation,
                    "visibility": field.visibility.value,
                    "embedded": field.embedded,
                    "tag": field.tag,
                }
            )

        # Methods
        for method in struct.methods:
            type_def.methods.append(self._convert_method(method))

        type_def.visibility = "public" if struct.exported else "internal"

        return type_def

    def _convert_interface(self, iface: GoInterface) -> TypeDef:
        """Convert GoInterface to TypeDef."""
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
                }
            )

        # Embedded interfaces
        type_def.extends = iface.embedded

        # Methods
        for method in iface.methods:
            type_def.methods.append(self._convert_method(method))

        type_def.visibility = "public" if iface.exported else "internal"

        return type_def

    def _convert_type_alias(self, alias: GoTypeAlias) -> TypeDef:
        """Convert GoTypeAlias to TypeDef."""
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
                }
            )

        type_def.aliased_type = alias.aliased_type
        type_def.visibility = "public" if alias.exported else "internal"

        return type_def

    def _convert_method(self, method: Any) -> dict[str, Any]:
        """Convert method to IR format."""
        result: dict[str, Any] = {
            "name": method.name,
            "parameters": [],
            "returns": [],
        }

        for param in method.parameters:
            result["parameters"].append(
                {
                    "name": param.name,
                    "type": param.type_annotation,
                    "variadic": param.variadic,
                }
            )

        for ret in method.results:
            result["returns"].append(
                {
                    "name": ret.name,
                    "type": ret.type_annotation,
                }
            )

        if method.type_params:
            result["type_params"] = [
                {
                    "name": p.name,
                    "constraint": p.constraint,
                }
                for p in method.type_params
            ]

        if method.receiver:
            result["receiver"] = {
                "name": method.receiver[0],
                "type": method.receiver[1],
            }

        result["visibility"] = method.visibility.value
        result["returns_error"] = method.returns_error

        return result

    def _extract_functions(self, parsed: dict[str, Any]) -> list[FunctionDef]:
        """Extract function definitions (Layer 2)."""
        functions = []

        for func in parsed.get("functions", []):
            func_def = self._convert_function(func)
            functions.append(func_def)

        return functions

    def _convert_function(self, func: GoFunction) -> FunctionDef:
        """Convert GoFunction to FunctionDef."""
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
                    rest=param.variadic,
                )
            )

        # Results (multiple return values)
        for i, ret in enumerate(func.results):
            if i == 0:
                func_def.return_type = ret.type_annotation
            else:
                if not hasattr(func_def, "additional_returns"):
                    func_def.additional_returns = []
                func_def.additional_returns.append(
                    {"name": ret.name, "type": ret.type_annotation}
                )

        # Type parameters
        for param in func.type_params:
            func_def.type_params.append(
                {
                    "name": param.name,
                    "constraint": param.constraint,
                }
            )

        # Receiver (for methods)
        if func.receiver:
            func_def.receiver = {
                "name": func.receiver[0],
                "type": func.receiver[1],
            }

        # Concurrency info
        if func.goroutines:
            func_def.goroutines = func.goroutines
        if func.channel_ops:
            func_def.channel_ops = func.channel_ops
        if func.defers:
            func_def.defers = func.defers

        # Visibility
        func_def.visibility = "public" if func.exported else "internal"

        return func_def

    def _generate_annotations(
        self, parsed: dict[str, Any], ir: IRVersion
    ) -> list[SemanticAnnotation]:
        """Generate semantic annotations for Go-specific concepts."""
        annotations = []

        # GO-001: Structural typing for interfaces
        for i, type_def in enumerate(ir.types):
            if type_def.kind == TypeKind.INTERFACE:
                annotations.append(
                    SemanticAnnotation(
                        kind="GO-001",
                        target=f"type:{i}",
                        value={"typing": "structural"},
                        description="Go uses structural typing for interfaces",
                    )
                )

        # GO-002: Error handling pattern
        for i, func_def in enumerate(ir.functions):
            if hasattr(func_def, "additional_returns"):
                for ret in func_def.additional_returns:
                    if ret.get("type") == "error":
                        annotations.append(
                            SemanticAnnotation(
                                kind="GO-002",
                                target=f"function:{i}",
                                value={"pattern": "error_return"},
                                description="Function returns error as part of multiple returns",
                            )
                        )
                        break
            elif func_def.return_type == "error":
                annotations.append(
                    SemanticAnnotation(
                        kind="GO-002",
                        target=f"function:{i}",
                        value={"pattern": "error_return"},
                        description="Function returns error",
                    )
                )

        # GO-003: Goroutine usage
        for i, func in enumerate(parsed.get("functions", [])):
            if func.goroutines:
                annotations.append(
                    SemanticAnnotation(
                        kind="GO-003",
                        target=f"function:{i}",
                        value={
                            "concurrency": "goroutines",
                            "count": len(func.goroutines),
                        },
                        description="Function spawns goroutines",
                    )
                )

        # GO-004: Channel operations
        for i, func in enumerate(parsed.get("functions", [])):
            if func.channel_ops:
                send_count = sum(
                    1 for op in func.channel_ops if op["type"] == "send"
                )
                recv_count = sum(
                    1 for op in func.channel_ops if op["type"] == "receive"
                )
                annotations.append(
                    SemanticAnnotation(
                        kind="GO-004",
                        target=f"function:{i}",
                        value={
                            "concurrency": "channels",
                            "sends": send_count,
                            "receives": recv_count,
                        },
                        description="Function uses channel operations",
                    )
                )

        # GO-005: Defer usage
        for i, func in enumerate(parsed.get("functions", [])):
            if func.defers:
                annotations.append(
                    SemanticAnnotation(
                        kind="GO-005",
                        target=f"function:{i}",
                        value={
                            "defer_count": len(func.defers),
                        },
                        description="Function uses defer statements",
                    )
                )

        return annotations

    def _detect_gaps(
        self, parsed: dict[str, Any], ir: IRVersion
    ) -> list[GapMarker]:
        """Detect semantic gaps in the extracted IR."""
        gaps = []

        # GO-010: Goroutine synchronization complexity
        for func in parsed.get("functions", []):
            if len(func.goroutines) > 1:
                gaps.append(
                    GapMarker(
                        kind="GO-010",
                        description=f"Function '{func.name}' spawns multiple goroutines",
                        location=f"line {func.line}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Review synchronization patterns for conversion",
                    )
                )

        # GO-011: Channel complexity
        for func in parsed.get("functions", []):
            if len(func.channel_ops) > 3:
                gaps.append(
                    GapMarker(
                        kind="GO-011",
                        description=f"Function '{func.name}' has complex channel usage",
                        location=f"line {func.line}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Channel patterns may need manual conversion",
                    )
                )

        # GO-012: Multiple error returns
        for func in parsed.get("functions", []):
            if len(func.results) > 2:
                gaps.append(
                    GapMarker(
                        kind="GO-012",
                        description=f"Function '{func.name}' has {len(func.results)} return values",
                        location=f"line {func.line}",
                        severity=GapSeverity.LOW,
                        suggestion="Consider tuple or Result type in target language",
                    )
                )

        # GO-013: Generic constraints
        for struct in parsed.get("structs", []):
            for param in struct.type_params:
                if param.constraint and param.constraint not in ("any", "comparable"):
                    gaps.append(
                        GapMarker(
                            kind="GO-013",
                            description=f"Type '{struct.name}' has custom generic constraint",
                            location=f"line {struct.line}",
                            severity=GapSeverity.MEDIUM,
                            suggestion="Generic constraint may need manual conversion",
                        )
                    )

        # GO-014: Embedded types
        for struct in parsed.get("structs", []):
            embedded_fields = [f for f in struct.fields if f.embedded]
            if embedded_fields:
                gaps.append(
                    GapMarker(
                        kind="GO-014",
                        description=f"Struct '{struct.name}' uses embedded types",
                        location=f"line {struct.line}",
                        severity=GapSeverity.LOW,
                        suggestion="Embedded types may need explicit delegation",
                    )
                )

        # GO-015: Struct tags
        for struct in parsed.get("structs", []):
            tagged_fields = [f for f in struct.fields if f.tag]
            if tagged_fields:
                gaps.append(
                    GapMarker(
                        kind="GO-015",
                        description=f"Struct '{struct.name}' has field tags",
                        location=f"line {struct.line}",
                        severity=GapSeverity.LOW,
                        suggestion="Field tags need manual conversion to target language attributes",
                    )
                )

        return gaps
