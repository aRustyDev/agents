"""Roc source code synthesizer.

Main synthesizer implementation that transforms IR representation
into idiomatic Roc source code.
"""

from __future__ import annotations

import logging
from typing import Any

from ir_core.base import (
    SynthConfig,
    Synthesizer,
    register_synthesizer,
)
from ir_core.models import (
    GapMarker,
    GapSeverity,
    IRVersion,
    TypeKind,
)

from ir_synthesize_roc.generator import RocCodeGenerator

logger = logging.getLogger(__name__)


@register_synthesizer("roc")
class RocSynthesizer(Synthesizer):
    """Roc source code synthesizer.

    Generates idiomatic Roc source code from IR representation with
    proper handling of:

    - Pure functional patterns
    - Platform-based effects (Task type)
    - Result type (no exceptions)
    - Pattern matching (when...is)
    - Tag unions
    """

    def __init__(self) -> None:
        """Initialize the synthesizer."""
        self._generator = RocCodeGenerator()

    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        """Synthesize Roc code from IR.

        Args:
            ir: IR version to synthesize
            config: Synthesis configuration

        Returns:
            Generated Roc source code
        """
        logger.info(f"Synthesizing Roc from {ir.source_path}")

        parts: list[str] = []

        # Generate header (app or module)
        header = self._generate_header(ir)
        if header:
            parts.append(header)
            parts.append("")

        # Generate imports
        if ir.structural and ir.structural.imports:
            imports = self._generate_imports(ir.structural.imports)
            if imports:
                parts.append(imports)
                parts.append("")

        # Generate type definitions
        for type_def in ir.types:
            if type_def.kind == TypeKind.STRUCT:
                parts.append(self._generator.generate_record_type(type_def))
            elif type_def.kind == TypeKind.ENUM:
                parts.append(self._generator.generate_tag_union(type_def))
            parts.append("")

        # Generate functions
        for func_def in ir.functions:
            parts.append(self._generator.generate_function(func_def))
            parts.append("")

        code = "\n".join(parts)

        # Add gap comments
        code = self._add_gap_comments(code, ir)

        return code

    def supported_version(self) -> str:
        """Return the IR schema version this synthesizer supports."""
        return "ir-v1.0"

    def detect_cross_language_gaps(
        self, ir: IRVersion, target_lang: str
    ) -> list[GapMarker]:
        """Detect gaps when synthesizing to Roc from another language."""
        gaps = []
        source_lang = ir.source_language

        if source_lang == "python":
            gaps.extend(self._detect_python_to_roc_gaps(ir))
        elif source_lang == "typescript":
            gaps.extend(self._detect_typescript_to_roc_gaps(ir))
        elif source_lang == "rust":
            gaps.extend(self._detect_rust_to_roc_gaps(ir))
        elif source_lang == "golang":
            gaps.extend(self._detect_golang_to_roc_gaps(ir))

        return gaps

    def _generate_header(self, ir: IRVersion) -> str:
        """Generate app or module header."""
        if not ir.structural:
            return ""

        # Check if we have platform info (app file)
        platform = None
        platform_alias = "pf"
        for imp in ir.structural.imports:
            if imp.get("platform"):
                platform = imp.get("module")
                platform_alias = imp.get("alias", "pf")
                break

        if platform:
            return self._generator.generate_app_header(
                ir.structural.exports or ["main"],
                platform,
                platform_alias,
            )
        elif ir.structural.exports:
            return self._generator.generate_module_header(ir.structural.exports)

        return ""

    def _generate_imports(self, imports: list[dict[str, Any]]) -> str:
        """Generate import statements."""
        lines = []

        for imp in imports:
            if imp.get("platform"):
                continue  # Handled in header

            module = imp.get("module", "")
            exposing = imp.get("exposing")
            alias = imp.get("alias")

            lines.append(
                self._generator.generate_import(module, exposing, alias)
            )

        return "".join(lines)

    def _add_gap_comments(self, code: str, ir: IRVersion) -> str:
        """Add comments for detected gaps."""
        if not ir.gaps:
            return code

        comments = []
        for gap in ir.gaps:
            severity_str = gap.severity.value if hasattr(gap.severity, "value") else str(gap.severity)
            comments.append(f"# GAP[{gap.kind}]: {gap.description}")
            comments.append(f"#   Severity: {severity_str}")
            if gap.suggestion:
                comments.append(f"#   Suggestion: {gap.suggestion}")
            comments.append("")

        if comments:
            header = "# --- Conversion Gaps ---\n"
            header += "\n".join(comments)
            code = header + "\n" + code

        return code

    def _detect_python_to_roc_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to Python→Roc conversion."""
        gaps = []

        # PY-ROC-001: Exception handling
        for func_def in ir.functions:
            if hasattr(func_def, "raises") and func_def.raises:
                gaps.append(
                    GapMarker(
                        kind="PY-ROC-001",
                        description=f"Function '{func_def.name}' uses exceptions",
                        location=f"function:{func_def.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Convert to Result type with explicit error handling",
                    )
                )

        # PY-ROC-002: Mutable state
        gaps.append(
            GapMarker(
                kind="PY-ROC-002",
                description="Roc is purely functional - no mutable state",
                location="global",
                severity=GapSeverity.MEDIUM,
                suggestion="Convert mutable patterns to pure functions",
            )
        )

        # PY-ROC-003: Dynamic typing
        for func_def in ir.functions:
            for param in func_def.parameters:
                if not param.type_annotation or param.type_annotation == "Any":
                    gaps.append(
                        GapMarker(
                            kind="PY-ROC-003",
                            description=f"Parameter '{param.name}' lacks type annotation",
                            location=f"function:{func_def.name}",
                            severity=GapSeverity.LOW,
                            suggestion="Add explicit type annotation",
                        )
                    )

        return gaps

    def _detect_typescript_to_roc_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to TypeScript→Roc conversion."""
        gaps = []

        # TS-ROC-001: Classes
        for type_def in ir.types:
            if type_def.kind == TypeKind.CLASS:
                gaps.append(
                    GapMarker(
                        kind="TS-ROC-001",
                        description=f"Class '{type_def.name}' - Roc has no classes",
                        location=f"type:{type_def.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Convert to record type with functions",
                    )
                )

        # TS-ROC-002: null/undefined
        gaps.append(
            GapMarker(
                kind="TS-ROC-002",
                description="Roc has no null/undefined",
                location="global",
                severity=GapSeverity.LOW,
                suggestion="Use tag unions like [Just a, Nothing] for optional values",
            )
        )

        # TS-ROC-003: Async/await
        for func_def in ir.functions:
            if hasattr(func_def, "async_") and func_def.async_:
                gaps.append(
                    GapMarker(
                        kind="TS-ROC-003",
                        description=f"Async function '{func_def.name}'",
                        location=f"function:{func_def.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Convert to Task type with platform effects",
                    )
                )

        return gaps

    def _detect_rust_to_roc_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to Rust→Roc conversion."""
        gaps = []

        # RS-ROC-001: Ownership
        gaps.append(
            GapMarker(
                kind="RS-ROC-001",
                description="Roc uses reference counting, not ownership",
                location="global",
                severity=GapSeverity.LOW,
                suggestion="Ownership patterns simplified in Roc",
            )
        )

        # RS-ROC-002: Traits
        for type_def in ir.types:
            if type_def.kind == TypeKind.INTERFACE:
                gaps.append(
                    GapMarker(
                        kind="RS-ROC-002",
                        description=f"Trait '{type_def.name}' converts to ability",
                        location=f"type:{type_def.name}",
                        severity=GapSeverity.LOW,
                        suggestion="Use Roc abilities for type classes",
                    )
                )

        # RS-ROC-003: Macros
        for annotation in ir.annotations:
            if "macro" in annotation.kind.lower():
                gaps.append(
                    GapMarker(
                        kind="RS-ROC-003",
                        description="Rust macros have no Roc equivalent",
                        location=annotation.target,
                        severity=GapSeverity.HIGH,
                        suggestion="Manually expand macro to functions",
                    )
                )

        return gaps

    def _detect_golang_to_roc_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to Go→Roc conversion."""
        gaps = []

        # GO-ROC-001: Goroutines
        for func_def in ir.functions:
            if hasattr(func_def, "goroutines") and func_def.goroutines:
                gaps.append(
                    GapMarker(
                        kind="GO-ROC-001",
                        description=f"Function '{func_def.name}' uses goroutines",
                        location=f"function:{func_def.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Concurrency handled via platform in Roc",
                    )
                )

        # GO-ROC-002: Channels
        for func_def in ir.functions:
            if hasattr(func_def, "channel_ops") and func_def.channel_ops:
                gaps.append(
                    GapMarker(
                        kind="GO-ROC-002",
                        description=f"Function '{func_def.name}' uses channels",
                        location=f"function:{func_def.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Consider Task composition instead",
                    )
                )

        # GO-ROC-003: Interfaces
        for type_def in ir.types:
            if type_def.kind == TypeKind.INTERFACE:
                gaps.append(
                    GapMarker(
                        kind="GO-ROC-003",
                        description=f"Interface '{type_def.name}' to ability",
                        location=f"type:{type_def.name}",
                        severity=GapSeverity.LOW,
                        suggestion="Convert to Roc ability",
                    )
                )

        # GO-ROC-004: Pointers
        gaps.append(
            GapMarker(
                kind="GO-ROC-004",
                description="Roc has no pointers",
                location="global",
                severity=GapSeverity.LOW,
                suggestion="All values are immutable; use records for structured data",
            )
        )

        return gaps
