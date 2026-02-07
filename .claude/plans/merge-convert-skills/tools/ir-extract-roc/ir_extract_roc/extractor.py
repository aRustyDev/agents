"""Roc source code extractor.

Main extractor implementation that transforms Roc source code
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

from ir_extract_roc.parser import (
    Purity,
    RocFunction,
    RocParser,
    RocRecord,
    RocTagUnion,
)

logger = logging.getLogger(__name__)


@register_extractor("roc")
class RocExtractor(Extractor):
    """Roc source code extractor.

    Extracts Roc source into the 5-layer IR representation with
    special handling for:

    - Pure functional patterns
    - Platform-based effects (Task type)
    - Result type (no exceptions)
    - Pattern matching (when...is)
    - Tag unions
    """

    def __init__(self) -> None:
        """Initialize the extractor."""
        self._parser = RocParser()

    def extract(
        self, source: str, path: str, config: ExtractConfig
    ) -> IRVersion:
        """Extract IR from Roc source code.

        Args:
            source: Roc source code
            path: File path for error reporting
            config: Extraction configuration

        Returns:
            IRVersion with extracted layers
        """
        logger.info(f"Extracting Roc from {path}")

        # Parse source
        parsed = self._parser.parse(source)

        # Initialize IR
        ir = IRVersion(
            version="ir-v1.0",
            source_language="roc",
            source_path=path,
        )

        # Extract module structure (Layer 4)
        ir.structural = self._extract_module_structure(parsed, path)

        # Extract type definitions (Layer 3)
        ir.types = self._extract_types(parsed)

        # Extract functions (Layer 2)
        ir.functions = self._extract_functions(parsed)

        # Add semantic annotations
        ir.annotations = self._generate_annotations(parsed, ir, source)

        # Detect gaps
        ir.gaps = self._detect_gaps(parsed, ir, source)

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
            name=self._get_module_name(parsed, path),
            path=path,
            language="roc",
        )

        # Handle app header
        if parsed.get("app"):
            app = parsed["app"]
            structure.exports = app.provides
            # Platform is a special import
            structure.imports.append({
                "module": app.platform,
                "alias": app.platform_alias,
                "platform": True,
            })

        # Handle module header
        if parsed.get("module"):
            module = parsed["module"]
            structure.exports = module.exposes

        # Regular imports
        for imp in parsed.get("imports", []):
            import_info: dict[str, Any] = {
                "module": imp.module,
            }
            if imp.exposing:
                import_info["exposing"] = imp.exposing
            if imp.alias:
                import_info["alias"] = imp.alias
            structure.imports.append(import_info)

        return structure

    def _get_module_name(
        self, parsed: dict[str, Any], path: str
    ) -> str:
        """Determine module name from parsed data or path."""
        if parsed.get("module") and parsed["module"].name:
            return parsed["module"].name

        # Extract from path
        import os

        basename = os.path.basename(path)
        name, _ = os.path.splitext(basename)
        return name

    def _extract_types(self, parsed: dict[str, Any]) -> list[TypeDef]:
        """Extract type definitions (Layer 3)."""
        types = []

        # Extract records
        for record in parsed.get("records", []):
            type_def = self._convert_record(record)
            types.append(type_def)

        # Extract tag unions
        for tag_union in parsed.get("tag_unions", []):
            type_def = self._convert_tag_union(tag_union)
            types.append(type_def)

        # Extract opaques
        for opaque in parsed.get("opaques", []):
            type_def = self._convert_opaque(opaque)
            types.append(type_def)

        return types

    def _convert_record(self, record: RocRecord) -> TypeDef:
        """Convert RocRecord to TypeDef."""
        type_def = TypeDef(
            name=record.name,
            kind=TypeKind.STRUCT,  # Records are similar to structs
            line=record.line,
            column=record.column,
        )

        # Type parameters
        for param in record.type_params:
            type_def.type_params.append({
                "name": param.name,
                "abilities": param.abilities,
            })

        # Fields
        for field in record.fields:
            type_def.properties.append({
                "name": field.name,
                "type": field.type_annotation,
                "optional": field.optional,
            })

        type_def.visibility = "public"

        return type_def

    def _convert_tag_union(self, tag_union: RocTagUnion) -> TypeDef:
        """Convert RocTagUnion to TypeDef."""
        type_def = TypeDef(
            name=tag_union.name,
            kind=TypeKind.ENUM,  # Tag unions are similar to enums with data
            line=tag_union.line,
            column=tag_union.column,
        )

        # Type parameters
        for param in tag_union.type_params:
            type_def.type_params.append({
                "name": param.name,
                "abilities": param.abilities,
            })

        # Variants as enum members
        for variant in tag_union.variants:
            type_def.enum_members.append({
                "name": variant.name,
                "payload_types": variant.payload_types,
            })

        type_def.visibility = "public"

        return type_def

    def _convert_opaque(self, opaque: Any) -> TypeDef:
        """Convert opaque type to TypeDef."""
        type_def = TypeDef(
            name=opaque.name,
            kind=TypeKind.TYPE_ALIAS,
            line=opaque.line,
            column=opaque.column,
        )

        # Type parameters
        for param in opaque.type_params:
            type_def.type_params.append({
                "name": param.name,
                "abilities": param.abilities,
            })

        type_def.aliased_type = opaque.inner_type
        type_def.abilities = opaque.abilities
        type_def.visibility = "public"

        return type_def

    def _extract_functions(self, parsed: dict[str, Any]) -> list[FunctionDef]:
        """Extract function definitions (Layer 2)."""
        functions = []

        for func in parsed.get("functions", []):
            func_def = self._convert_function(func)
            functions.append(func_def)

        return functions

    def _convert_function(self, func: RocFunction) -> FunctionDef:
        """Convert RocFunction to FunctionDef."""
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
                    type_annotation=param.type_annotation or "",
                )
            )

        # Return type
        func_def.return_type = func.return_type

        # Type parameters
        for param in func.type_params:
            func_def.type_params.append({
                "name": param.name,
                "abilities": param.abilities,
            })

        # Purity
        func_def.purity = func.purity.value
        func_def.abilities_required = func.abilities_required

        # Full type annotation
        func_def.type_annotation = func.type_annotation

        func_def.visibility = "public"

        return func_def

    def _generate_annotations(
        self, parsed: dict[str, Any], ir: IRVersion, source: str
    ) -> list[SemanticAnnotation]:
        """Generate semantic annotations for Roc-specific concepts."""
        annotations = []

        # ROC-001: Pure functions
        for i, func_def in enumerate(ir.functions):
            if hasattr(func_def, "purity") and func_def.purity == "pure":
                annotations.append(
                    SemanticAnnotation(
                        kind="ROC-001",
                        target=f"function:{i}",
                        value={"purity": "pure"},
                        description="Pure function with no side effects",
                    )
                )

        # ROC-002: Platform effects (Task type)
        for i, func in enumerate(parsed.get("functions", [])):
            if func.purity == Purity.PLATFORM_TASK:
                annotations.append(
                    SemanticAnnotation(
                        kind="ROC-002",
                        target=f"function:{i}",
                        value={"effect_type": "platform_task"},
                        description="Function uses platform Task for effects",
                    )
                )

        # ROC-003: Result types (no exceptions)
        for i, func in enumerate(parsed.get("functions", [])):
            if func.returns_result:
                annotations.append(
                    SemanticAnnotation(
                        kind="ROC-003",
                        target=f"function:{i}",
                        value={"pattern": "result_type"},
                        description="Function returns Result (no exceptions)",
                    )
                )

        # ROC-004: Pattern matching
        if self._parser.has_pattern_matching(source):
            pattern_matches = self._parser.extract_pattern_matches(source)
            for pm in pattern_matches:
                annotations.append(
                    SemanticAnnotation(
                        kind="ROC-004",
                        target=f"line:{pm['line']}",
                        value={
                            "branches": len(pm["branches"]),
                        },
                        description="Pattern matching expression",
                    )
                )

        # ROC-005: Tag unions
        for i, type_def in enumerate(ir.types):
            if type_def.enum_members:
                # Check if any variant has payload
                has_payload = any(
                    m.get("payload_types") for m in type_def.enum_members
                )
                if has_payload:
                    annotations.append(
                        SemanticAnnotation(
                            kind="ROC-005",
                            target=f"type:{i}",
                            value={"pattern": "tag_union_with_data"},
                            description="Tag union with variant data",
                        )
                    )

        return annotations

    def _detect_gaps(
        self, parsed: dict[str, Any], ir: IRVersion, source: str
    ) -> list[GapMarker]:
        """Detect semantic gaps in the extracted IR."""
        gaps = []

        # ROC-010: Platform-specific code
        if parsed.get("app") and parsed["app"].platform:
            gaps.append(
                GapMarker(
                    kind="ROC-010",
                    description="Code depends on Roc platform",
                    location=f"line {parsed['app'].line}",
                    severity=GapSeverity.MEDIUM,
                    suggestion="Platform effects need manual conversion",
                )
            )

        # ROC-011: Ability constraints
        for func in parsed.get("functions", []):
            if func.abilities_required:
                gaps.append(
                    GapMarker(
                        kind="ROC-011",
                        description=f"Function '{func.name}' requires abilities: {', '.join(func.abilities_required)}",
                        location=f"line {func.line}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Ability constraints need trait/protocol conversion",
                    )
                )

        # ROC-012: Complex pattern matching
        pattern_matches = self._parser.extract_pattern_matches(source)
        for pm in pattern_matches:
            if len(pm["branches"]) > 5:
                gaps.append(
                    GapMarker(
                        kind="ROC-012",
                        description="Complex pattern matching expression",
                        location=f"line {pm['line']}",
                        severity=GapSeverity.LOW,
                        suggestion="Consider extracting to helper functions",
                    )
                )

        # ROC-013: Opaque types
        for opaque in parsed.get("opaques", []):
            gaps.append(
                GapMarker(
                    kind="ROC-013",
                    description=f"Opaque type '{opaque.name}' hides implementation",
                    location=f"line {opaque.line}",
                    severity=GapSeverity.LOW,
                    suggestion="Convert to newtype or wrapper in target language",
                )
            )

        # ROC-014: Backslash lambda syntax
        if "\\" in source and "->" in source:
            # Rough detection of lambda usage
            lambda_count = source.count("\\")
            if lambda_count > 5:
                gaps.append(
                    GapMarker(
                        kind="ROC-014",
                        description=f"Heavy use of backslash lambdas ({lambda_count} occurrences)",
                        location="multiple",
                        severity=GapSeverity.LOW,
                        suggestion="Convert to appropriate lambda syntax in target language",
                    )
                )

        return gaps
