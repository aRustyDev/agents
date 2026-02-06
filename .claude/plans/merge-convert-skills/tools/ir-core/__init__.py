"""IR Core - Infrastructure for IR extraction and synthesis.

This module provides the core abstractions and utilities for the intermediate
representation (IR) extraction/synthesis pipeline. It is designed to be
language-agnostic and extensible for new language support.

Architecture:
    - Extractor: Base class for language-specific extractors
    - Synthesizer: Base class for language-specific synthesizers
    - TreeSitterAdapter: Generic tree-sitter wrapper for parsing
    - SchemaValidator: Validates IR against JSON schema
    - GapDetector: Detects semantic gaps during extraction

Usage:
    from ir_core import Extractor, Synthesizer, IRVersion
    from ir_core.treesitter import TreeSitterAdapter
    from ir_core.validation import SchemaValidator
    from ir_core.gaps import GapDetector

Phase 5 (Python MVP):
    - Python extractor using tree-sitter + jedi/pyright
    - Python synthesizer targeting idiomatic Python
    - L3 semantic equivalence verification

See Also:
    - ADR-009: Extractor Architecture
    - IR Schema: docs/src/ir-schema/
    - Equivalence Levels: docs/src/validation/equivalence-levels.md
"""

from __future__ import annotations

from .base import (
    Extractor,
    Synthesizer,
    ExtractConfig,
    SynthConfig,
)
from .models import (
    IRVersion,
    Module,
    TypeDef,
    Function,
    Binding,
    Expression,
    GapMarker,
    SemanticAnnotation,
    PreservationStatus,
    SourceSpan,
    TypeRef,
    # Error codes
    ExtractionError,
    SynthesisError,
    ValidationError,
    # Enums
    ExtractionMode,
    GapType,
    Severity,
    PreservationLevel,
    Visibility,
    Mutability,
    LifetimeKind,
)
from .validation import SchemaValidator
from .gaps import GapDetector
from .treesitter import TreeSitterAdapter, TSSourceSpan
from .utils import ts_span_to_ir, generate_content_hash, compute_source_hash

__version__ = "0.1.0"
__all__ = [
    # Base classes
    "Extractor",
    "Synthesizer",
    "ExtractConfig",
    "SynthConfig",
    # Core models
    "IRVersion",
    "Module",
    "TypeDef",
    "Function",
    "Binding",
    "Expression",
    "GapMarker",
    "SemanticAnnotation",
    "PreservationStatus",
    "SourceSpan",
    "TSSourceSpan",
    "TypeRef",
    # Errors
    "ExtractionError",
    "SynthesisError",
    "ValidationError",
    # Enums
    "ExtractionMode",
    "GapType",
    "Severity",
    "PreservationLevel",
    "Visibility",
    "Mutability",
    "LifetimeKind",
    # Utilities
    "SchemaValidator",
    "GapDetector",
    "TreeSitterAdapter",
    "ts_span_to_ir",
    "generate_content_hash",
    "compute_source_hash",
]
