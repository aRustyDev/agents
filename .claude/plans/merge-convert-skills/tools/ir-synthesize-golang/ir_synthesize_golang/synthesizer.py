"""Go source code synthesizer.

Main synthesizer implementation that transforms IR representation
into idiomatic Go source code.
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

from ir_synthesize_golang.formatter import get_formatter
from ir_synthesize_golang.generator import GolangCodeGenerator

logger = logging.getLogger(__name__)


@register_synthesizer("golang")
class GolangSynthesizer(Synthesizer):
    """Go source code synthesizer.

    Generates idiomatic Go source code from IR representation with
    proper handling of:

    - Error handling patterns (multiple returns with error)
    - Goroutines and channels
    - Defer statements
    - Interfaces (structural typing)
    - Generics (Go 1.18+)
    """

    def __init__(self) -> None:
        """Initialize the synthesizer."""
        self._generator = GolangCodeGenerator()

    def synthesize(self, ir: IRVersion, config: SynthConfig) -> str:
        """Synthesize Go code from IR.

        Args:
            ir: IR version to synthesize
            config: Synthesis configuration

        Returns:
            Generated Go source code
        """
        logger.info(f"Synthesizing Go from {ir.source_path}")

        parts: list[str] = []

        # Generate package declaration
        package_name = self._get_package_name(ir)
        parts.append(self._generator.generate_package(package_name))
        parts.append("")

        # Generate imports
        if ir.structural and ir.structural.imports:
            imports = self._process_imports(ir.structural.imports)
            if imports:
                parts.append(self._generator.generate_imports(imports))
                parts.append("")

        # Generate type definitions
        for type_def in ir.types:
            if type_def.kind == TypeKind.STRUCT:
                parts.append(self._generator.generate_struct(type_def))
                parts.append("")
            elif type_def.kind == TypeKind.INTERFACE:
                parts.append(self._generator.generate_interface(type_def))
                parts.append("")
            elif type_def.kind == TypeKind.TYPE_ALIAS:
                parts.append(self._generator.generate_type_alias(type_def))
                parts.append("")

        # Generate functions
        for func_def in ir.functions:
            parts.append(self._generator.generate_function(func_def))
            parts.append("")

        code = "\n".join(parts)

        # Format if enabled
        if config.format:
            formatter = get_formatter()
            code = formatter.format(code)

        # Add gap comments
        code = self._add_gap_comments(code, ir)

        return code

    def supported_version(self) -> str:
        """Return the IR schema version this synthesizer supports."""
        return "ir-v1.0"

    def detect_cross_language_gaps(
        self, ir: IRVersion, target_lang: str
    ) -> list[GapMarker]:
        """Detect gaps when synthesizing to Go from another language."""
        gaps = []
        source_lang = ir.source_language

        if source_lang == "python":
            gaps.extend(self._detect_python_to_go_gaps(ir))
        elif source_lang == "typescript":
            gaps.extend(self._detect_typescript_to_go_gaps(ir))
        elif source_lang == "rust":
            gaps.extend(self._detect_rust_to_go_gaps(ir))

        return gaps

    def _get_package_name(self, ir: IRVersion) -> str:
        """Determine package name from IR."""
        if ir.structural and ir.structural.name:
            name = ir.structural.name
            # Convert to valid Go package name (lowercase, no special chars)
            return name.lower().replace("-", "").replace("_", "")
        return "main"

    def _process_imports(
        self, imports: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Process and convert imports to Go format."""
        go_imports = []

        for imp in imports:
            module = imp.get("module", "")

            # Map common modules to Go equivalents
            go_module = self._map_import(module, imp)
            if go_module:
                go_imports.append(go_module)

        return go_imports

    def _map_import(
        self, module: str, imp: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Map source language import to Go import."""
        # Common Python to Go mappings
        python_to_go = {
            "json": {"module": "encoding/json"},
            "os": {"module": "os"},
            "sys": {"module": "os"},
            "io": {"module": "io"},
            "re": {"module": "regexp"},
            "math": {"module": "math"},
            "time": {"module": "time"},
            "http": {"module": "net/http"},
            "asyncio": {"module": "sync"},
            "typing": None,  # No equivalent
            "dataclasses": None,  # No equivalent
        }

        # TypeScript/Node to Go mappings
        ts_to_go = {
            "fs": {"module": "os"},
            "path": {"module": "path/filepath"},
            "http": {"module": "net/http"},
            "https": {"module": "net/http"},
            "crypto": {"module": "crypto"},
            "stream": {"module": "io"},
            "buffer": None,  # No direct equivalent
            "events": None,  # No direct equivalent
        }

        # Rust to Go mappings
        rust_to_go = {
            "std::io": {"module": "io"},
            "std::fs": {"module": "os"},
            "std::collections": {"module": "container/list"},
            "std::sync": {"module": "sync"},
            "tokio": {"module": "sync"},
            "serde": {"module": "encoding/json"},
            "serde_json": {"module": "encoding/json"},
        }

        # Try mappings
        if module in python_to_go:
            return python_to_go[module]
        if module in ts_to_go:
            return ts_to_go[module]
        if module in rust_to_go:
            return rust_to_go[module]

        # Pass through Go imports unchanged
        if "/" in module or module in ("fmt", "errors", "context", "strings"):
            return {"module": module, **{k: v for k, v in imp.items() if k != "module"}}

        return None

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

    def _detect_python_to_go_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to Python→Go conversion."""
        gaps = []

        # PY-GO-001: Dynamic typing
        for annotation in ir.annotations:
            if annotation.kind == "PY-002":  # Type inference
                gaps.append(
                    GapMarker(
                        kind="PY-GO-001",
                        description="Python dynamic typing converted to explicit Go types",
                        location=annotation.target,
                        severity=GapSeverity.LOW,
                        suggestion="Verify inferred types match expected behavior",
                    )
                )

        # PY-GO-002: Exception handling
        for func_def in ir.functions:
            if hasattr(func_def, "raises") and func_def.raises:
                gaps.append(
                    GapMarker(
                        kind="PY-GO-002",
                        description=f"Function '{func_def.name}' uses exceptions, converted to error returns",
                        location=f"function:{func_def.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Review error handling flow",
                    )
                )

        # PY-GO-003: Generators
        for func_def in ir.functions:
            if hasattr(func_def, "generator") and func_def.generator:
                gaps.append(
                    GapMarker(
                        kind="PY-GO-003",
                        description=f"Generator function '{func_def.name}' needs manual conversion",
                        location=f"function:{func_def.name}",
                        severity=GapSeverity.HIGH,
                        suggestion="Consider using channels or iterator pattern",
                    )
                )

        # PY-GO-004: Duck typing
        for type_def in ir.types:
            if type_def.kind == TypeKind.INTERFACE:
                gaps.append(
                    GapMarker(
                        kind="PY-GO-004",
                        description=f"Protocol/ABC '{type_def.name}' converted to interface",
                        location=f"type:{type_def.name}",
                        severity=GapSeverity.LOW,
                        suggestion="Go interfaces are structurally typed, verify compatibility",
                    )
                )

        return gaps

    def _detect_typescript_to_go_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to TypeScript→Go conversion."""
        gaps = []

        # TS-GO-001: Union types
        for type_def in ir.types:
            if hasattr(type_def, "union_types") and type_def.union_types:
                gaps.append(
                    GapMarker(
                        kind="TS-GO-001",
                        description=f"Union type '{type_def.name}' has no direct Go equivalent",
                        location=f"type:{type_def.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Consider using interface or type switch",
                    )
                )

        # TS-GO-002: Optional properties
        for type_def in ir.types:
            for prop in type_def.properties:
                if prop.get("optional"):
                    gaps.append(
                        GapMarker(
                            kind="TS-GO-002",
                            description=f"Optional property '{prop.get('name')}' in '{type_def.name}'",
                            location=f"type:{type_def.name}",
                            severity=GapSeverity.LOW,
                            suggestion="Use pointer type or zero value semantics",
                        )
                    )

        # TS-GO-003: Async/await
        for func_def in ir.functions:
            if hasattr(func_def, "async_") and func_def.async_:
                gaps.append(
                    GapMarker(
                        kind="TS-GO-003",
                        description=f"Async function '{func_def.name}' needs goroutine/channel conversion",
                        location=f"function:{func_def.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Use goroutines and channels for concurrency",
                    )
                )

        # TS-GO-004: Decorators
        for type_def in ir.types:
            if hasattr(type_def, "decorators") and type_def.decorators:
                gaps.append(
                    GapMarker(
                        kind="TS-GO-004",
                        description=f"Decorators on '{type_def.name}' have no Go equivalent",
                        location=f"type:{type_def.name}",
                        severity=GapSeverity.MEDIUM,
                        suggestion="Consider middleware pattern or code generation",
                    )
                )

        return gaps

    def _detect_rust_to_go_gaps(self, ir: IRVersion) -> list[GapMarker]:
        """Detect gaps specific to Rust→Go conversion."""
        gaps = []

        # RS-GO-001: Ownership/borrowing
        gaps.append(
            GapMarker(
                kind="RS-GO-001",
                description="Rust ownership semantics have no Go equivalent",
                location="global",
                severity=GapSeverity.MEDIUM,
                suggestion="Go uses garbage collection; review memory patterns",
            )
        )

        # RS-GO-002: Result/Option types
        for func_def in ir.functions:
            if func_def.return_type and "Result" in str(func_def.return_type):
                gaps.append(
                    GapMarker(
                        kind="RS-GO-002",
                        description=f"Result type in '{func_def.name}' converted to multiple returns",
                        location=f"function:{func_def.name}",
                        severity=GapSeverity.LOW,
                        suggestion="Verify error handling matches Rust semantics",
                    )
                )

        # RS-GO-003: Traits vs Interfaces
        for type_def in ir.types:
            if type_def.kind == TypeKind.INTERFACE:
                gaps.append(
                    GapMarker(
                        kind="RS-GO-003",
                        description=f"Trait '{type_def.name}' converted to interface",
                        location=f"type:{type_def.name}",
                        severity=GapSeverity.LOW,
                        suggestion="Go interfaces are implicit; implementations don't declare them",
                    )
                )

        # RS-GO-004: Macros
        for annotation in ir.annotations:
            if "macro" in annotation.kind.lower():
                gaps.append(
                    GapMarker(
                        kind="RS-GO-004",
                        description="Rust macros have no Go equivalent",
                        location=annotation.target,
                        severity=GapSeverity.HIGH,
                        suggestion="Manual expansion or code generation required",
                    )
                )

        return gaps
