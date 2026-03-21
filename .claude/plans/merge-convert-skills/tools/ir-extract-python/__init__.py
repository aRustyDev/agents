"""Python IR Extractor - Extract IR from Python source code.

This module implements the Python-specific extractor for the IR extraction/synthesis
pipeline. It follows the hybrid architecture from ADR-009: tree-sitter for parsing
combined with semantic enrichment via jedi/pyright.

Features:
    - Parse Python 3.8+ source code using tree-sitter
    - Extract functions, classes, and type definitions
    - Detect Python-specific patterns (comprehensions, decorators, async)
    - Optional semantic enrichment via jedi or pyright
    - Generate 5-layer IR representation

Usage:
    from ir_extract_python import PythonExtractor, PythonParser

    extractor = PythonExtractor()
    ir = extractor.extract(source_code, "module.py", config)

    # Or parse only
    parser = PythonParser()
    tree = parser.parse(source_code)
    functions = parser.extract_functions(tree)

CLI:
    python -m ir_extract_python file.py
    python -m ir_extract_python --output ir.yaml file.py
    python -m ir_extract_python --enrich file.py

See Also:
    - ADR-009: Extractor Architecture
    - ir-core: Base classes and models
"""

from __future__ import annotations

from .extractor import PythonExtractor
from .parser import PythonParser
from .patterns import PythonPatternMatcher
from .semantic import SemanticEnricher

__version__ = "0.1.0"
__all__ = [
    "PythonExtractor",
    "PythonParser",
    "PythonPatternMatcher",
    "SemanticEnricher",
]
