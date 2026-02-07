"""Scala source code synthesizer.

Main synthesizer implementation that transforms IR representation
into idiomatic Scala source code.
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

from ir_synthesize_scala.generator import ScalaCodeGenerator

logger = logging.getLogger(__name__)


@register_synthesizer("scala")
class ScalaSynthesizer(Synthesizer):
    """Scala source code synthesizer.

    Generates idiomatic Scala source code from IR representation with
    proper handling of:

    - Higher-kinded types
    - Variance annotations
    - Implicits and given instances
    - Case classes and sealed traits
    - Pattern matching
    - For comprehensions
    """

    def __init__(self) -> None:
        """Initialize the synthesizer."""
        self._generator = ScalaCodeGenerator()

    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        """Synthesize Scala code from IR.

        Args:
            ir: IR version to synthesize
            config: Synthesis configuration

        Returns:
            Generated Scala source code
        """
        logger.info(f"Synthesizing Scala from {ir.source_path}")

        parts: list[str] = []

        # Generate package if available
        if ir.structural and hasattr(ir.structural, 'package'):
            pkg = getattr(ir.structural, 'package', None)
            if pkg:
                parts.append(self._generator.generate_package(pkg))
                parts.append("")

        # Generate imports
        if ir.structural and ir.structural.imports:
            imports = self._generate_imports(ir.structural.imports)
            if imports:
                parts.append(imports)
                parts.append("")

        # Generate type definitions
        for type_def in ir.types:
            if type_def.kind == TypeKind.INTERFACE:
                parts.append(self._generator.generate_trait(type_def))
            elif type_def.kind == TypeKind.STRUCT:
                parts.append(self._generator.generate_case_class(type_def))
            elif type_def.kind == TypeKind.CLASS:
                # Check if it's an object (singleton)
                if hasattr(type_def, 'singleton') and type_def.singleton:
                    parts.append(self._generator.generate_object(type_def))
                else:
                    parts.append(self._generator.generate_class(type_def))
            elif type_def.kind == TypeKind.ENUM:
                parts.append(self._generate_sealed_trait(type_def))
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
        """Detect gaps when synthesizing to Scala from another language."""
        gaps = []
        source_lang = ir.source_language

        if source_lang == "python":
            gaps.extend(self._detect_python_to_scala_gaps(ir))
        elif source_lang == "typescript":
            gaps.extend(self._detect_typescript_to_scala_gaps(ir))
        elif source_lang == "rust":
            gaps.extend(self._detect_rust_to_scala_gaps(ir))
        elif source_lang == "golang":
            gaps.extend(self._detect_golang_to_scala_gaps(ir))
        elif source_lang == "roc":
            gaps.extend(self._detect_roc_to_scala_gaps(ir))

        return gaps

    def _generate_imports(self, imports: list[dict[str, Any]]) -> str:
        """Generate import statements."""
        lines = []

        for imp in imports:
            path = imp.get("module", "")
            selectors = imp.get("selectors")
            is_wildcard = imp.get("wildcard", False)

            lines.append(
                self._generator.generate_import(path, selectors, is_wildcard)
            )

        return "".join(lines)

    def _generate_sealed_trait(self, type_def: Any) -> str:
        """Generate sealed trait and case objects for enum."""
        lines = []

        # Sealed trait
        name = type_def.name
        type_params = ""
        if type_def.type_params:
            params = [p.get("name", "") for p in type_def.type_params]
            type_params = f"[{', '.join(params)}]"

        lines.append(f"sealed trait {name}{type_params}")
        lines.append("")

        # Case objects/classes for variants
        if type_def.enum_members:
            for member in type_def.enum_members:
                member_name = member.get("name", "")
                payload_types = member.get("payload_types", [])

                if payload_types:
                    # Case class with payload
                    fields = ", ".join(
                        f"value{i}: {t}" for i, t in enumerate(payload_types)
                    )
                    lines.append(f"case class {member_name}({fields}) extends {name}")
                else:
                    # Case object
                    lines.append(f"case object {member_name} extends {name}")

        return "\n".join(lines)

    def _add_gap_comments(self, code: str, ir: IRVersion) -> str:
        """Add comments for detected gaps."""
        if not ir.gaps:
            return code

        comments = []
        for gap in ir.gaps:
            severity_str = gap.severity.value if hasattr(gap.severity, "value") else str(gap.severity)
            comments.append(f"// GAP[{gap.kind}]: {gap.description}")
            comments.append(f"//   Severity: {severity_str}")
            if gap.suggestion:
                comments.append(f"//   Suggestion: {gap.suggestion}")
            comments.append("")

        if comments:
            header = "// --- Conversion Gaps ---\n"
            header += "\n".join(comments)
            code = header + "\n" + code

        return code

    def _detect_python_to_scala_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to Python→Scala conversion."""
        gaps = []

        # PY-SC-001: Dynamic typing
        for func_def in ir.functions:
            for param in func_def.parameters:
                if not param.type_annotation or param.type_annotation in ("Any", "object"):
                    gaps.append(GapMarker(
                        kind="PY-SC-001",
                        description=f"Parameter '{param.name}' has no/weak type",
                        location=f"function:{func_def.name}",
                        severity=GapSeverity.LOW,
                        suggestion="Add explicit type annotation",
                    ))

        # PY-SC-002: Duck typing
        gaps.append(GapMarker(
            kind="PY-SC-002",
            description="Python duck typing may need trait abstractions",
            location="global",
            severity=GapSeverity.MEDIUM,
            suggestion="Define traits for structural types",
        ))

        # PY-SC-003: Exceptions
        for func_def in ir.functions:
            if hasattr(func_def, "raises") and func_def.raises:
                gaps.append(GapMarker(
                    kind="PY-SC-003",
                    description=f"Function '{func_def.name}' uses exceptions",
                    location=f"function:{func_def.name}",
                    severity=GapSeverity.MEDIUM,
                    suggestion="Consider using Either/Try for error handling",
                ))

        return gaps

    def _detect_typescript_to_scala_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to TypeScript→Scala conversion."""
        gaps = []

        # TS-SC-001: Union types
        for type_def in ir.types:
            if hasattr(type_def, 'union_types') and type_def.union_types:
                gaps.append(GapMarker(
                    kind="TS-SC-001",
                    description=f"Union type in '{type_def.name}'",
                    location=f"type:{type_def.name}",
                    severity=GapSeverity.MEDIUM,
                    suggestion="Convert to sealed trait hierarchy",
                ))

        # TS-SC-002: null/undefined
        gaps.append(GapMarker(
            kind="TS-SC-002",
            description="TypeScript null/undefined handling",
            location="global",
            severity=GapSeverity.LOW,
            suggestion="Use Option[T] instead",
        ))

        # TS-SC-003: Structural typing
        gaps.append(GapMarker(
            kind="TS-SC-003",
            description="TypeScript structural typing",
            location="global",
            severity=GapSeverity.MEDIUM,
            suggestion="Define traits for interface compatibility",
        ))

        return gaps

    def _detect_rust_to_scala_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to Rust→Scala conversion."""
        gaps = []

        # RS-SC-001: Ownership semantics
        gaps.append(GapMarker(
            kind="RS-SC-001",
            description="Rust ownership not needed in Scala (GC)",
            location="global",
            severity=GapSeverity.LOW,
            suggestion="Remove ownership annotations",
        ))

        # RS-SC-002: Lifetimes
        for func_def in ir.functions:
            if hasattr(func_def, 'lifetimes') and func_def.lifetimes:
                gaps.append(GapMarker(
                    kind="RS-SC-002",
                    description=f"Lifetimes in '{func_def.name}' not applicable",
                    location=f"function:{func_def.name}",
                    severity=GapSeverity.LOW,
                    suggestion="Remove lifetime parameters",
                ))

        # RS-SC-003: Trait objects vs HKT
        for type_def in ir.types:
            if type_def.kind == TypeKind.INTERFACE:
                gaps.append(GapMarker(
                    kind="RS-SC-003",
                    description=f"Trait '{type_def.name}' may use HKT in Scala",
                    location=f"type:{type_def.name}",
                    severity=GapSeverity.LOW,
                    suggestion="Consider using higher-kinded types",
                ))

        return gaps

    def _detect_golang_to_scala_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to Go→Scala conversion."""
        gaps = []

        # GO-SC-001: Multiple return values
        for func_def in ir.functions:
            if hasattr(func_def, 'returns_multiple') and func_def.returns_multiple:
                gaps.append(GapMarker(
                    kind="GO-SC-001",
                    description=f"Multiple returns in '{func_def.name}'",
                    location=f"function:{func_def.name}",
                    severity=GapSeverity.LOW,
                    suggestion="Use tuple or case class",
                ))

        # GO-SC-002: Error handling
        for func_def in ir.functions:
            if func_def.return_type and "error" in str(func_def.return_type).lower():
                gaps.append(GapMarker(
                    kind="GO-SC-002",
                    description=f"Go error return in '{func_def.name}'",
                    location=f"function:{func_def.name}",
                    severity=GapSeverity.MEDIUM,
                    suggestion="Use Either[Error, T] or Try[T]",
                ))

        # GO-SC-003: Goroutines/channels
        for func_def in ir.functions:
            if hasattr(func_def, 'goroutines') and func_def.goroutines:
                gaps.append(GapMarker(
                    kind="GO-SC-003",
                    description=f"Goroutines in '{func_def.name}'",
                    location=f"function:{func_def.name}",
                    severity=GapSeverity.HIGH,
                    suggestion="Use Scala Future or Akka actors",
                ))

        # GO-SC-004: Interfaces
        for type_def in ir.types:
            if type_def.kind == TypeKind.INTERFACE:
                gaps.append(GapMarker(
                    kind="GO-SC-004",
                    description=f"Go interface '{type_def.name}'",
                    location=f"type:{type_def.name}",
                    severity=GapSeverity.LOW,
                    suggestion="Convert to Scala trait",
                ))

        return gaps

    def _detect_roc_to_scala_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to Roc→Scala conversion."""
        gaps = []

        # ROC-SC-001: Task effects
        for func_def in ir.functions:
            if func_def.return_type and "Task" in str(func_def.return_type):
                gaps.append(GapMarker(
                    kind="ROC-SC-001",
                    description=f"Task effect in '{func_def.name}'",
                    location=f"function:{func_def.name}",
                    severity=GapSeverity.MEDIUM,
                    suggestion="Use cats-effect IO or ZIO",
                ))

        # ROC-SC-002: Tag unions
        for type_def in ir.types:
            if type_def.kind == TypeKind.ENUM:
                gaps.append(GapMarker(
                    kind="ROC-SC-002",
                    description=f"Tag union '{type_def.name}'",
                    location=f"type:{type_def.name}",
                    severity=GapSeverity.LOW,
                    suggestion="Convert to sealed trait + case classes/objects",
                ))

        # ROC-SC-003: Abilities
        for annotation in ir.annotations:
            if "ability" in annotation.kind.lower():
                gaps.append(GapMarker(
                    kind="ROC-SC-003",
                    description="Roc ability",
                    location=annotation.target,
                    severity=GapSeverity.MEDIUM,
                    suggestion="Convert to Scala type class (trait + given)",
                ))

        return gaps
