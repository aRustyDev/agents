"""Roc extractor for the IR extraction/synthesis pipeline.

This package extracts Roc source code into the 5-layer IR representation,
with special handling for:

- Pure functional patterns
- Platform-based effects (Task type)
- Result type (no exceptions)
- Pattern matching (when...is)
- Tag unions
- Backslash lambda syntax
"""

from ir_extract_roc.extractor import RocExtractor

__all__ = ["RocExtractor"]
__version__ = "0.1.0"
