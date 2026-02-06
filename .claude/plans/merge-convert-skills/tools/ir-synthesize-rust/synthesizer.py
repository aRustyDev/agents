"""Main Rust synthesizer implementation.

This module provides the RustSynthesizer class that transforms IR into Rust
source code with proper ownership, lifetimes, and borrow-checker-valid output.

Example:
    synthesizer = RustSynthesizer()
    code = synthesizer.synthesize(ir, config)

    # With custom configuration
    config = SynthConfig(
        output_format=OutputFormat.FORMATTED,
        emit_type_hints=True,
        target_version="2021",
    )
    code = synthesizer.synthesize(ir, config)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ir_core.base import (
    OutputFormat,
    SynthConfig,
    Synthesizer,
    register_synthesizer,
)
from ir_core.models import (
    GapMarker,
    GapType,
    IRVersion,
    Severity,
    SynthesisError,
    SynthesisErrorCode,
    TypeDef,
    TypeKind,
)

from .formatter import FormatConfig, RustFormatter
from .generator import RustCodeGenerator, SynthesisContext
from .ownership import OwnershipPlanner


@dataclass
class RustSynthesisContext(SynthesisContext):
    """Extended context for Rust synthesis.

    Attributes:
        ir: The IR being synthesized
        config: Synthesis configuration
        edition: Rust edition to target
        gaps: Gaps encountered during synthesis
    """

    ir: IRVersion | None = None
    config: SynthConfig | None = None
    edition: str = "2021"
    gaps: list[GapMarker] | None = None


@register_synthesizer("rust")
class RustSynthesizer(Synthesizer):
    """Rust code synthesizer from IR.

    This synthesizer generates borrow-checker-valid Rust code from the
    5-layer IR representation. It supports multiple preservation levels
    and integrates with rustfmt for formatting.

    Attributes:
        generator: RustCodeGenerator for code construct generation
        formatter: RustFormatter for code formatting
        ownership_planner: OwnershipPlanner for ownership decisions

    Example:
        synthesizer = RustSynthesizer()
        code = synthesizer.synthesize(ir, SynthConfig())

        # Check for synthesis issues
        for gap in synthesizer.last_gaps:
            print(f"Gap: {gap.description}")
    """

    def __init__(self) -> None:
        """Initialize the Rust synthesizer."""
        self.generator = RustCodeGenerator()
        self.formatter = RustFormatter()
        self.ownership_planner = OwnershipPlanner()

        # State from last synthesis
        self.last_gaps: list[GapMarker] = []
        self._gap_counter = 0

    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        """Synthesize Rust source code from IR.

        Args:
            ir: IRVersion containing the layers to synthesize
            config: Synthesis configuration

        Returns:
            Generated Rust source code as a string

        Raises:
            SynthesisError: If synthesis fails with S001-S005 error codes
        """
        # Validate IR
        if not ir.module:
            raise SynthesisError(
                code=SynthesisErrorCode.S001,
                message="IR has no module defined",
            )

        # Determine Rust edition from config
        edition = config.target_version or "2021"
        if edition not in ("2015", "2018", "2021"):
            edition = "2021"

        # Plan ownership for all functions
        ownership_plans = self.ownership_planner.plan_ir(ir)

        # Create synthesis context
        context = RustSynthesisContext(
            ir=ir,
            config=config,
            edition=edition,
            gaps=[],
            imports_needed=set(),
        )

        self._gap_counter = 0

        try:
            # Generate code sections
            sections: list[str] = []

            # Module documentation
            if ir.module.metadata.documentation and config.emit_docstrings:
                sections.append(f"//! {ir.module.metadata.documentation}")

            # Imports section (generated after collecting needed imports)
            imports_section = ""

            # Type definitions
            for type_def in ir.types:
                code = self._gen_type_def(type_def, context)
                if code:
                    sections.append(code)

            # Functions
            for func in ir.functions:
                # Set ownership plan for this function
                context.ownership_plan = ownership_plans.get(func.id)
                code = self.generator.gen_function(func, context)
                if code:
                    sections.append(code)

            # Generate imports
            if context.imports_needed:
                imports_section = self._gen_imports(context.imports_needed)
                sections.insert(
                    1 if ir.module.metadata.documentation else 0,
                    imports_section
                )

            # Join sections
            code = "\n\n".join(filter(None, sections))

            # Format if requested
            if config.output_format == OutputFormat.FORMATTED:
                format_config = FormatConfig(
                    edition=edition,
                    max_width=config.line_length,
                    tab_spaces=config.indent_size,
                )
                self.formatter = RustFormatter(format_config)
                code = self.formatter.format(code)

            self.last_gaps = context.gaps or []
            return code

        except Exception as e:
            raise SynthesisError(
                code=SynthesisErrorCode.S005,
                message=f"Code generation failed: {e}",
            ) from e

    def target_language(self) -> str:
        """Return the target language identifier."""
        return "rust"

    def estimate_output(self, ir: IRVersion) -> dict[str, Any]:
        """Estimate properties of the synthesized output.

        Args:
            ir: IRVersion to estimate for

        Returns:
            Dictionary with estimates
        """
        # Count entities
        type_count = len(ir.types)
        func_count = len(ir.functions)
        import_count = len(ir.module.imports) if ir.module else 0

        # Rough line estimate (Rust is more verbose than Python)
        estimated_lines = (
            import_count * 1
            + type_count * 20  # Average struct/enum size
            + func_count * 12  # Average function size
        )

        # Complexity based on gaps
        critical_gaps = sum(1 for g in ir.gaps if g.severity == Severity.CRITICAL)
        if critical_gaps > 0:
            complexity = "high"
        elif len(ir.gaps) > 5:
            complexity = "medium"
        else:
            complexity = "low"

        # Check for ownership-related gaps
        ownership_gaps = sum(
            1 for g in ir.gaps
            if g.gap_pattern_id and g.gap_pattern_id.startswith("MM-")
        )

        return {
            "estimated_lines": estimated_lines,
            "estimated_complexity": complexity,
            "type_count": type_count,
            "function_count": func_count,
            "import_count": import_count,
            "gap_count": len(ir.gaps),
            "ownership_gap_count": ownership_gaps,
        }

    def _next_gap_id(self, context: RustSynthesisContext) -> str:
        """Generate the next gap ID."""
        self._gap_counter += 1
        module_id = context.ir.module.id if context.ir and context.ir.module else "unknown"
        return f"synth_gap:{module_id}:{self._gap_counter}"

    def _add_gap(
        self,
        context: RustSynthesisContext,
        gap_type: GapType,
        severity: Severity,
        description: str,
        source_concept: str,
        target_concept: str | None = None,
        location: str = "",
    ) -> None:
        """Add a gap marker to the context."""
        if context.gaps is None:
            context.gaps = []

        gap = GapMarker(
            id=self._next_gap_id(context),
            location=location,
            gap_type=gap_type,
            severity=severity,
            description=description,
            source_concept=source_concept,
            target_concept=target_concept,
        )
        context.gaps.append(gap)

    def _gen_imports(self, imports_needed: set[str]) -> str:
        """Generate use statements from needed imports.

        Args:
            imports_needed: Set of import paths

        Returns:
            Rust use statements
        """
        if not imports_needed:
            return ""

        lines: list[str] = []

        # Group by top-level module
        std_imports: list[str] = []
        other_imports: list[str] = []

        for imp in sorted(imports_needed):
            if imp.startswith("std::"):
                std_imports.append(imp)
            else:
                other_imports.append(imp)

        # Generate use statements
        for imp in std_imports:
            lines.append(f"use {imp};")

        if std_imports and other_imports:
            lines.append("")

        for imp in other_imports:
            lines.append(f"use {imp};")

        return "\n".join(lines)

    def _gen_type_def(
        self, type_def: TypeDef, context: RustSynthesisContext
    ) -> str:
        """Generate a type definition.

        Args:
            type_def: Type definition
            context: Synthesis context

        Returns:
            Rust type definition code
        """
        if type_def.kind == TypeKind.STRUCT:
            return self.generator.gen_struct(type_def, context)

        elif type_def.kind == TypeKind.ENUM:
            return self.generator.gen_enum(type_def, context)

        elif type_def.kind == TypeKind.INTERFACE:
            return self.generator.gen_trait(type_def, context)

        elif type_def.kind == TypeKind.ALIAS:
            # Type alias
            vis = self.generator.gen_visibility(
                type_def.visibility.value
                if hasattr(type_def.visibility, 'value')
                else str(type_def.visibility)
            )
            generics = self.generator.gen_type_params(type_def.params)
            aliased = "/* unknown */"
            if type_def.body.aliased_type:
                aliased = self.generator.gen_type_ref(
                    type_def.body.aliased_type, context
                )
            return f"{vis}type {type_def.name}{generics} = {aliased};"

        else:
            self._add_gap(
                context,
                GapType.STRUCTURAL,
                Severity.MEDIUM,
                f"Unknown type kind: {type_def.kind}",
                str(type_def.kind),
                "struct/enum/trait",
                f"type:{type_def.id}",
            )
            return f"// Unsupported type: {type_def.name}"


def synthesize_rust(ir: IRVersion, config: SynthConfig | None = None) -> str:
    """Convenience function to synthesize Rust code.

    Args:
        ir: IRVersion to synthesize
        config: Optional synthesis configuration

    Returns:
        Generated Rust source code
    """
    synthesizer = RustSynthesizer()
    return synthesizer.synthesize(ir, config or SynthConfig())
