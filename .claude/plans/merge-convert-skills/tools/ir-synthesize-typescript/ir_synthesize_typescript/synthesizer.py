"""TypeScript source code synthesizer.

Main synthesizer implementation that transforms IR into TypeScript source code.
"""

from __future__ import annotations

import logging
from typing import Any

from ir_core.base import (
    OutputFormat,
    SynthConfig,
    Synthesizer,
    register_synthesizer,
)
from ir_core.models import GapMarker, GapSeverity, IRVersion, TypeKind

from ir_synthesize_typescript.formatter import PrettierFormatter, SimpleFormatter
from ir_synthesize_typescript.generator import GeneratorConfig, TypeScriptCodeGenerator

logger = logging.getLogger(__name__)


@register_synthesizer("typescript")
class TypeScriptSynthesizer(Synthesizer):
    """TypeScript source code synthesizer.

    Synthesizes TypeScript code from IR, generating valid TypeScript with:

    - Full type annotations
    - Interface and type alias definitions
    - Proper import/export statements
    - Class definitions with modifiers
    - Async/await support
    """

    def __init__(self) -> None:
        """Initialize the synthesizer."""
        self._generator: TypeScriptCodeGenerator | None = None
        self._formatter: PrettierFormatter | None = None
        self._simple_formatter: SimpleFormatter | None = None
        self.last_gaps: list[GapMarker] = []

    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        """Synthesize TypeScript code from IR.

        Args:
            ir: IRVersion containing the layers to synthesize
            config: Synthesis configuration

        Returns:
            Generated TypeScript source code
        """
        logger.info(f"Synthesizing TypeScript from IR (source: {ir.source_language})")

        self.last_gaps = []

        # Configure generator
        gen_config = GeneratorConfig(
            indent_size=config.indent_size,
            use_tabs=config.use_tabs,
            line_length=config.line_length,
            emit_type_annotations=config.emit_type_hints,
        )

        self._generator = TypeScriptCodeGenerator(gen_config)

        # Check for cross-language conversion gaps
        if ir.source_language and ir.source_language != "typescript":
            self._detect_conversion_gaps(ir)

        # Generate imports
        imports = self._generate_imports(ir)

        # Generate code
        code = self._generator.generate(
            types=ir.types,
            functions=ir.functions,
            imports=imports,
        )

        # Format output
        if config.output_format == OutputFormat.FORMATTED:
            code = self._format_code(code, config)
        elif config.output_format == OutputFormat.PRESERVED:
            # Preserve original formatting (best effort)
            code = self._normalize_code(code)

        return code

    def target_language(self) -> str:
        """Return the target language identifier."""
        return "typescript"

    def _generate_imports(self, ir: IRVersion) -> list[dict[str, Any]]:
        """Generate import statements from IR structural layer."""
        imports = []

        if ir.structural and hasattr(ir.structural, "imports"):
            for imp in ir.structural.imports:
                imports.append(imp)

        return imports

    def _format_code(self, code: str, config: SynthConfig) -> str:
        """Format code using prettier or simple formatter."""
        if self._formatter is None:
            self._formatter = PrettierFormatter(
                config={
                    "tab_width": config.indent_size,
                    "use_tabs": config.use_tabs,
                    "print_width": config.line_length,
                }
            )

        if self._formatter.is_available():
            return self._formatter.format(code)
        else:
            # Fall back to simple formatter
            if self._simple_formatter is None:
                self._simple_formatter = SimpleFormatter(
                    indent_size=config.indent_size,
                    use_tabs=config.use_tabs,
                    line_length=config.line_length,
                )
            code = self._simple_formatter.format(code)
            return self._simple_formatter.normalize_whitespace(code)

    def _normalize_code(self, code: str) -> str:
        """Normalize code whitespace."""
        if self._simple_formatter is None:
            self._simple_formatter = SimpleFormatter()
        return self._simple_formatter.normalize_whitespace(code)

    def _detect_conversion_gaps(self, ir: IRVersion) -> None:
        """Detect gaps when converting from other languages."""
        source_lang = ir.source_language

        if source_lang == "python":
            self._detect_python_gaps(ir)
        elif source_lang == "rust":
            self._detect_rust_gaps(ir)

    def _detect_python_gaps(self, ir: IRVersion) -> None:
        """Detect gaps when converting from Python."""
        for type_def in ir.types:
            # Python dynamic typing
            if type_def.kind == TypeKind.CLASS:
                for prop in type_def.properties:
                    if not prop.get("type"):
                        self.last_gaps.append(
                            GapMarker(
                                kind="PY-TS-001",
                                description=f"Property '{prop.get('name')}' in {type_def.name} has no type annotation",
                                location=f"type:{type_def.name}",
                                severity=GapSeverity.LOW,
                                suggestion="Add explicit type annotation or use 'any'",
                            )
                        )

        for func in ir.functions:
            # Check for missing return type
            if not func.return_type:
                self.last_gaps.append(
                    GapMarker(
                        kind="PY-TS-002",
                        description=f"Function '{func.name}' has no return type",
                        location=f"func:{func.name}",
                        severity=GapSeverity.LOW,
                        suggestion="Add return type annotation",
                    )
                )

            # Check for *args, **kwargs
            for param in func.parameters:
                if param.name.startswith("*"):
                    self.last_gaps.append(
                        GapMarker(
                            kind="PY-TS-003",
                            description=f"Python *args/**kwargs in '{func.name}' need manual conversion",
                            location=f"func:{func.name}",
                            severity=GapSeverity.MEDIUM,
                            suggestion="Use rest parameters or overloads",
                        )
                    )

    def _detect_rust_gaps(self, ir: IRVersion) -> None:
        """Detect gaps when converting from Rust."""
        # Check for ownership annotations that will be lost
        for annotation in ir.annotations:
            if annotation.kind == "MM-002":
                # Ownership annotation
                self.last_gaps.append(
                    GapMarker(
                        kind="RS-TS-001",
                        description="Rust ownership semantics lost in TypeScript",
                        location=annotation.target,
                        severity=GapSeverity.LOW,
                        suggestion="TypeScript uses garbage collection; ownership not applicable",
                    )
                )
            elif annotation.kind == "MM-010":
                # Lifetime annotation
                self.last_gaps.append(
                    GapMarker(
                        kind="RS-TS-002",
                        description="Rust lifetime annotation lost in TypeScript",
                        location=annotation.target,
                        severity=GapSeverity.LOW,
                        suggestion="TypeScript does not have lifetime concept",
                    )
                )

        # Check for Result/Option types
        for func in ir.functions:
            if func.return_type:
                if "Result<" in func.return_type:
                    self.last_gaps.append(
                        GapMarker(
                            kind="RS-TS-003",
                            description=f"Rust Result type in '{func.name}' converted to Promise or throws",
                            location=f"func:{func.name}",
                            severity=GapSeverity.MEDIUM,
                            suggestion="Consider using Promise or throw for error handling",
                        )
                    )
                if "Option<" in func.return_type:
                    self.last_gaps.append(
                        GapMarker(
                            kind="RS-TS-004",
                            description=f"Rust Option type in '{func.name}' converted to nullable",
                            location=f"func:{func.name}",
                            severity=GapSeverity.LOW,
                            suggestion="Using T | null for Option<T>",
                        )
                    )

    def estimate_output(self, ir: IRVersion) -> dict[str, Any]:
        """Estimate properties of the synthesized output."""
        type_lines = sum(
            10 + len(t.properties) * 2 + len(t.methods) * 3 for t in ir.types
        )
        func_lines = sum(5 + len(f.parameters) for f in ir.functions)

        return {
            "estimated_lines": type_lines + func_lines + len(ir.types) + len(ir.functions),
            "type_count": len(ir.types),
            "function_count": len(ir.functions),
            "estimated_complexity": "medium" if len(ir.types) > 10 else "low",
        }
