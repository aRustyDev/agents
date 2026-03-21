"""Python IR Synthesizer - Generate Python source code from IR.

This module implements the Python-specific synthesizer for the IR extraction/synthesis
pipeline. It generates idiomatic Python code from the intermediate representation,
supporting multiple preservation levels (L1-L3).

Features:
    - Generate Python 3.11+ source code from IR
    - Support for functions, classes, and type definitions
    - Generate idiomatic patterns (comprehensions, context managers, dataclasses)
    - Optional formatting via black/ruff
    - Multiple preservation levels (correct, idiomatic, optimized)

Usage:
    from ir_synthesize_python import PythonSynthesizer

    synthesizer = PythonSynthesizer()
    code = synthesizer.synthesize(ir, config)

    # With custom configuration
    from ir_core import SynthConfig, OutputFormat
    config = SynthConfig(
        output_format=OutputFormat.FORMATTED,
        emit_type_hints=True,
        target_version="3.11",
    )
    code = synthesizer.synthesize(ir, config)

CLI:
    python -m ir_synthesize_python ir.yaml
    python -m ir_synthesize_python --format --level idiomatic ir.yaml
    python -m ir_synthesize_python --output output.py ir.yaml

See Also:
    - ADR-009: Extractor Architecture
    - ir-core: Base classes and models
    - docs/src/validation/equivalence-levels.md: Preservation levels
"""

from __future__ import annotations

from .formatter import PythonFormatter
from .generator import PythonCodeGenerator
from .idioms import PythonIdiomGenerator
from .synthesizer import PythonSynthesizer

__version__ = "0.1.0"
__all__ = [
    "PythonCodeGenerator",
    "PythonFormatter",
    "PythonIdiomGenerator",
    "PythonSynthesizer",
]
