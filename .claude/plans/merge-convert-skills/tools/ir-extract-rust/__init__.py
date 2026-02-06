"""Rust IR Extractor.

This module provides extraction of Rust source code to the 5-layer IR
representation. It handles Rust-specific concepts like ownership, lifetimes,
and borrow checking semantics.

Example:
    from ir_extract_rust import RustExtractor

    extractor = RustExtractor()
    ir = extractor.extract(rust_source, "example.rs", config)

Layers extracted:
    - Layer 4: Modules, use statements, visibility (pub/pub(crate)/private)
    - Layer 3: Structs, enums, traits, impl blocks, generics with bounds
    - Layer 2: Functions, control flow, Result/Option handling, async
    - Layer 1: Ownership, borrowing, lifetimes, move semantics
    - Layer 0: Full AST for expression-level details (optional)
"""

from .extractor import RustExtractor
from .parser import RustParser
from .ownership import OwnershipAnalyzer
from .lifetimes import LifetimeExtractor

__all__ = [
    "RustExtractor",
    "RustParser",
    "OwnershipAnalyzer",
    "LifetimeExtractor",
]
