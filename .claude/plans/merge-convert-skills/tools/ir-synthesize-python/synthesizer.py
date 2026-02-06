"""Main Python synthesizer implementation.

This module provides the PythonSynthesizer class that transforms IR into Python source
code. It supports multiple preservation levels and output formatting options.

Example:
    synthesizer = PythonSynthesizer()
    code = synthesizer.synthesize(ir, config)

    # With custom configuration
    config = SynthConfig(
        output_format=OutputFormat.FORMATTED,
        emit_type_hints=True,
        target_version="3.11",
    )
    code = synthesizer.synthesize(ir, config)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ir_core.base import (
    Synthesizer,
    SynthConfig,
    OutputFormat,
    register_synthesizer,
)
from ir_core.models import (
    IRVersion,
    Module,
    TypeDef,
    Function,
    Import,
    GapMarker,
    GapType,
    Severity,
    PreservationLevel,
    SynthesisError,
    SynthesisErrorCode,
)

from .generator import PythonCodeGenerator
from .formatter import PythonFormatter
from .idioms import PythonIdiomGenerator


class PreservationMode(str, Enum):
    """Preservation mode for code synthesis.

    Attributes:
        CORRECT: L1 - Generate correct, compilable Python code
        IDIOMATIC: L2 - Generate idiomatic Python using native patterns
        OPTIMIZED: L3 - Generate optimized code with performance considerations
    """

    CORRECT = "correct"
    IDIOMATIC = "idiomatic"
    OPTIMIZED = "optimized"


@dataclass
class SynthesisContext:
    """Context for synthesis operations.

    Holds state that needs to be shared across generation steps.

    Attributes:
        ir: The IR being synthesized
        config: Synthesis configuration
        mode: Preservation mode
        imports_needed: Set of imports that need to be added
        gaps: List of gaps encountered during synthesis
        type_map: Mapping of IR type IDs to Python type names
        use_future_annotations: Whether to use `from __future__ import annotations`
    """

    ir: IRVersion
    config: SynthConfig
    mode: PreservationMode
    imports_needed: set[str]
    gaps: list[GapMarker]
    type_map: dict[str, str]
    use_future_annotations: bool = True

    @property
    def target_version(self) -> tuple[int, int]:
        """Parse target Python version from config.

        Returns:
            Tuple of (major, minor) version numbers.
            Defaults to (3, 10) if not specified.
        """
        if self.config.target_version:
            try:
                parts = self.config.target_version.split(".")
                return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
            except (ValueError, IndexError):
                pass
        return (3, 10)  # Default to Python 3.10

    @property
    def supports_pep604_union(self) -> bool:
        """Whether X | Y union syntax is supported (Python 3.10+)."""
        return self.target_version >= (3, 10)

    @property
    def supports_builtin_generics(self) -> bool:
        """Whether list[T] syntax is supported (Python 3.9+)."""
        return self.target_version >= (3, 9)


@register_synthesizer("python")
class PythonSynthesizer(Synthesizer):
    """Python code synthesizer from IR.

    This synthesizer generates idiomatic Python code from the 5-layer IR
    representation. It supports multiple preservation levels and integrates
    with formatting tools like black and ruff.

    Attributes:
        generator: PythonCodeGenerator for code construct generation
        formatter: PythonFormatter for code formatting
        idiom_generator: PythonIdiomGenerator for idiomatic patterns

    Example:
        synthesizer = PythonSynthesizer()
        code = synthesizer.synthesize(ir, SynthConfig())

        # Check for synthesis issues
        for gap in synthesizer.last_gaps:
            print(f"Gap: {gap.description}")
    """

    def __init__(self) -> None:
        """Initialize the Python synthesizer."""
        self.generator = PythonCodeGenerator()
        self.formatter = PythonFormatter()
        self.idiom_generator = PythonIdiomGenerator()

        # State from last synthesis
        self.last_gaps: list[GapMarker] = []
        self._gap_counter = 0

    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        """Synthesize Python source code from IR.

        Args:
            ir: IRVersion containing the layers to synthesize
            config: Synthesis configuration

        Returns:
            Generated Python source code as a string

        Raises:
            SynthesisError: If synthesis fails with S001-S005 error codes
        """
        # Validate IR
        if not ir.module:
            raise SynthesisError(
                code=SynthesisErrorCode.S001,
                message="IR has no module defined",
            )

        # Determine preservation mode from config
        mode = self._determine_mode(config)

        # Create synthesis context
        context = SynthesisContext(
            ir=ir,
            config=config,
            mode=mode,
            imports_needed=set(),
            gaps=[],
            type_map=self._build_type_map(ir),
        )

        self._gap_counter = 0

        try:
            # Generate code sections
            sections: list[str] = []

            # Module docstring
            if ir.module.metadata.documentation and config.emit_docstrings:
                sections.append(self._gen_module_docstring(ir.module.metadata.documentation))

            # Imports (generated after processing to collect needed imports)
            imports_section = self._gen_imports(ir.module.imports, context)

            # Type definitions (classes, dataclasses, protocols)
            for type_def in ir.types:
                code = self._gen_type_def(type_def, context)
                if code:
                    sections.append(code)

            # Module-level functions (non-methods)
            for func in ir.functions:
                if func.receiver is None:  # Skip methods
                    code = self._gen_function(func, context)
                    if code:
                        sections.append(code)

            # Prepend imports section
            if imports_section or context.imports_needed:
                all_imports = self._merge_imports(imports_section, context.imports_needed)
                sections.insert(0 if not ir.module.metadata.documentation else 1, all_imports)

            # Join sections
            code = "\n\n".join(filter(None, sections))

            # Format if requested
            if config.output_format == OutputFormat.FORMATTED:
                code = self.formatter.format(code)
            elif config.output_format == OutputFormat.PRESERVED:
                # Attempt to preserve original formatting (limited support)
                pass

            self.last_gaps = context.gaps
            return code

        except Exception as e:
            raise SynthesisError(
                code=SynthesisErrorCode.S005,
                message=f"Code generation failed: {e}",
            ) from e

    def target_language(self) -> str:
        """Return the target language identifier."""
        return "python"

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

        # Rough line estimate
        estimated_lines = (
            import_count * 1
            + type_count * 15  # Average class size
            + func_count * 8  # Average function size
        )

        # Complexity based on gaps
        critical_gaps = sum(1 for g in ir.gaps if g.severity == Severity.CRITICAL)
        if critical_gaps > 0:
            complexity = "high"
        elif len(ir.gaps) > 5:
            complexity = "medium"
        else:
            complexity = "low"

        return {
            "estimated_lines": estimated_lines,
            "estimated_complexity": complexity,
            "type_count": type_count,
            "function_count": func_count,
            "import_count": import_count,
            "gap_count": len(ir.gaps),
        }

    def _determine_mode(self, config: SynthConfig) -> PreservationMode:
        """Determine preservation mode from config."""
        mode_str = config.custom_options.get("preservation_mode", "idiomatic")
        try:
            return PreservationMode(mode_str)
        except ValueError:
            return PreservationMode.IDIOMATIC

    def _build_type_map(self, ir: IRVersion) -> dict[str, str]:
        """Build a mapping from IR type IDs to Python type names."""
        type_map: dict[str, str] = {}

        # Built-in type mappings
        type_map.update({
            "builtins.int": "int",
            "builtins.str": "str",
            "builtins.float": "float",
            "builtins.bool": "bool",
            "builtins.bytes": "bytes",
            "builtins.None": "None",
            "builtins.list": "list",
            "builtins.dict": "dict",
            "builtins.set": "set",
            "builtins.tuple": "tuple",
            "builtins.object": "object",
            "typing.Any": "Any",
            "typing.Optional": "Optional",
            "typing.Union": "Union",
            "typing.Callable": "Callable",
            "typing.Sequence": "Sequence",
            "typing.Mapping": "Mapping",
            "typing.Iterable": "Iterable",
            "typing.Iterator": "Iterator",
            "typing.Generator": "Generator",
            "typing.AsyncIterator": "AsyncIterator",
            "typing.AsyncGenerator": "AsyncGenerator",
            "typing.Awaitable": "Awaitable",
            "typing.Coroutine": "Coroutine",
            "typing.TypeVar": "TypeVar",
            "typing.Generic": "Generic",
            "typing.Protocol": "Protocol",
            "None": "None",
        })

        # Add types from IR
        for type_def in ir.types:
            type_map[type_def.id] = type_def.name

        return type_map

    def _next_gap_id(self, context: SynthesisContext) -> str:
        """Generate the next gap ID."""
        self._gap_counter += 1
        return f"synth_gap:{context.ir.module.id}:{self._gap_counter}"

    def _add_gap(
        self,
        context: SynthesisContext,
        gap_type: GapType,
        severity: Severity,
        description: str,
        source_concept: str,
        target_concept: str | None = None,
        location: str = "",
    ) -> None:
        """Add a gap marker to the context."""
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

    def _gen_module_docstring(self, doc: str) -> str:
        """Generate a module-level docstring."""
        return f'"""{doc}"""'

    def _gen_imports(self, imports: list[Import], context: SynthesisContext) -> str:
        """Generate import statements from IR imports."""
        lines: list[str] = []

        # Group imports by type
        standard_imports: list[str] = []
        from_imports: dict[str, list[str]] = {}

        for imp in imports:
            module_path = ".".join(imp.module_path)

            if not imp.imported_items:
                # import module
                if imp.alias:
                    standard_imports.append(f"import {module_path} as {imp.alias}")
                else:
                    standard_imports.append(f"import {module_path}")
            else:
                # from module import items
                for item in imp.imported_items:
                    if item.kind == "wildcard":
                        # Wildcard import - add gap
                        self._add_gap(
                            context,
                            GapType.STRUCTURAL,
                            Severity.MEDIUM,
                            "Wildcard import synthesized - consider explicit imports",
                            "from X import *",
                            "explicit imports",
                            f"import:{imp.id}",
                        )
                        if module_path not in from_imports:
                            from_imports[module_path] = []
                        from_imports[module_path].append("*")
                    else:
                        if module_path not in from_imports:
                            from_imports[module_path] = []
                        if item.alias:
                            from_imports[module_path].append(f"{item.name} as {item.alias}")
                        else:
                            from_imports[module_path].append(item.name)

        # Sort and format
        lines.extend(sorted(standard_imports))

        for module, items in sorted(from_imports.items()):
            items_str = ", ".join(sorted(set(items)))
            lines.append(f"from {module} import {items_str}")

        return "\n".join(lines)

    def _merge_imports(self, existing: str, needed: set[str]) -> str:
        """Merge existing imports with needed typing imports."""
        lines = existing.split("\n") if existing else []

        # Parse needed imports
        typing_imports: set[str] = set()
        other_imports: list[str] = []

        for imp in needed:
            if imp.startswith("typing."):
                typing_imports.add(imp.split(".")[-1])
            else:
                other_imports.append(imp)

        # Add typing imports
        if typing_imports:
            typing_line = f"from typing import {', '.join(sorted(typing_imports))}"
            # Check if we already have a typing import
            has_typing = any("from typing import" in line for line in lines)
            if not has_typing:
                lines.insert(0, typing_line)

        # Add other imports
        for imp in other_imports:
            imp_line = f"import {imp}"
            if imp_line not in lines:
                lines.append(imp_line)

        return "\n".join(lines)

    def _gen_type_def(self, type_def: TypeDef, context: SynthesisContext) -> str:
        """Generate a type definition (class, dataclass, protocol)."""
        return self.generator.gen_class(type_def, context)

    def _gen_function(self, func: Function, context: SynthesisContext) -> str:
        """Generate a function definition."""
        return self.generator.gen_function(func, context)
