"""Rust IR Synthesizer.

This module provides synthesis of Rust source code from the 5-layer IR
representation. It generates borrow-checker-valid Rust code with proper
ownership, lifetimes, and idiomatic patterns.

Example:
    from ir_synthesize_rust import RustSynthesizer

    synthesizer = RustSynthesizer()
    code = synthesizer.synthesize(ir, config)

Key features:
    - Generates compilable, borrow-checker-valid Rust code
    - Infers ownership and lifetime annotations
    - Uses idiomatic Rust patterns (Result, Option, iterators)
    - Supports formatting via rustfmt
"""

from .synthesizer import RustSynthesizer
from .generator import RustCodeGenerator
from .ownership import OwnershipPlanner
from .formatter import RustFormatter

__all__ = [
    "RustSynthesizer",
    "RustCodeGenerator",
    "OwnershipPlanner",
    "RustFormatter",
]
