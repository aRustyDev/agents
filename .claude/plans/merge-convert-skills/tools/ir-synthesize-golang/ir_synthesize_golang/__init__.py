"""Go synthesizer for the IR extraction/synthesis pipeline.

This package generates idiomatic Go source code from the 5-layer IR representation,
with proper handling of:

- Error handling patterns (multiple returns with error)
- Concurrency (goroutines and channels)
- Defer statements
- Interfaces (implicit satisfaction)
- Generics (Go 1.18+)
"""

from ir_synthesize_golang.synthesizer import GolangSynthesizer

__all__ = ["GolangSynthesizer"]
__version__ = "0.1.0"
