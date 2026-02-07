"""Roc synthesizer for the IR extraction/synthesis pipeline.

This package generates idiomatic Roc source code from the 5-layer IR representation,
with proper handling of:

- Pure functional patterns
- Platform-based effects (Task type)
- Result type (no exceptions)
- Pattern matching (when...is)
- Tag unions
- Backslash lambda syntax
"""

from ir_synthesize_roc.synthesizer import RocSynthesizer

__all__ = ["RocSynthesizer"]
__version__ = "0.1.0"
