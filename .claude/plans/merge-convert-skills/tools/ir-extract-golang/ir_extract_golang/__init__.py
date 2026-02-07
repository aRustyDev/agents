"""Go extractor for the IR extraction/synthesis pipeline.

This package extracts Go source code into the 5-layer IR representation,
with special handling for:

- Error handling patterns (multiple returns with error)
- Goroutines and channels
- Defer statements
- Interfaces (structural typing)
- Generics (Go 1.18+)
"""

from ir_extract_golang.extractor import GolangExtractor

__all__ = ["GolangExtractor"]
__version__ = "0.1.0"
