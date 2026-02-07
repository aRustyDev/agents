"""TypeScript extractor for the IR extraction/synthesis pipeline.

This package extracts TypeScript source code into the 5-layer IR representation,
with special handling for TypeScript-specific concepts:

- Structural typing vs nominal
- Union and intersection types
- Generic constraints and variance
- Interface and type alias definitions
- Decorators and access modifiers

Example:
    from ir_extract_typescript import TypeScriptExtractor
    from ir_core.base import ExtractConfig

    extractor = TypeScriptExtractor()
    ir = extractor.extract(source, "example.ts", ExtractConfig())

    for func in ir.functions:
        print(f"Function: {func.name}")
"""

from ir_extract_typescript.extractor import TypeScriptExtractor

__all__ = ["TypeScriptExtractor"]
__version__ = "0.1.0"
