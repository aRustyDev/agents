"""Scala source code extractor for IR pipeline.

This package extracts structured IR from Scala source code,
handling HKT, implicits/givens, variance, and type classes.
"""

from __future__ import annotations

from ir_extract_scala.extractor import ScalaExtractor

__all__ = ["ScalaExtractor"]
__version__ = "0.1.0"
