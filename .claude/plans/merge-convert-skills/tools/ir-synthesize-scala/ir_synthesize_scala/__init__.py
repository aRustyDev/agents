"""Scala source code synthesizer for IR pipeline.

This package generates idiomatic Scala source code from IR,
handling HKT, implicits/givens, variance, and type classes.
"""

from __future__ import annotations

from ir_synthesize_scala.synthesizer import ScalaSynthesizer

__all__ = ["ScalaSynthesizer"]
__version__ = "0.1.0"
