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
    ExtractConfig,
    Extractor,
    OutputFormat,
    SynthConfig,
    Synthesizer,
)
from .gaps import GapDetector
from .models import (
    AnnotationSource,
    AutomationLevel,
    Binding,
    Block,
    ControlFlowGraph,
    Effect,
    EffectKind,
    Expression,
    # Error codes
    ExtractionError,
    ExtractionErrorCode,
    # Enums
    ExtractionMode,
    Field_,
    Function,
    GapMarker,
    GapType,
    IRVersion,
    Lifetime,
    LifetimeKind,
    Module,
    ModuleMetadata,
    Mutability,
    Param,
    PreservationLevel,
    PreservationStatus,
    SemanticAnnotation,
    Severity,
    SourceSpan,
    Statement,
    SynthesisError,
    SynthesisErrorCode,
    Terminator,
    TerminatorKind,
    TypeBody,
    TypeDef,
    TypeKind,
    TypeRef,
    TypeRefKind,
    ValidationError,
    ValidationErrorCode,
    Visibility,
)
from .treesitter import TreeSitterAdapter, TSSourceSpan
from .utils import compute_source_hash, generate_content_hash, ts_span_to_ir
from .validation import SchemaValidator

__version__ = "0.1.0"
__all__ = [
    # Base classes
    "Extractor",
    "Synthesizer",
    "ExtractConfig",
    "SynthConfig",
    "OutputFormat",
    # Core models
    "IRVersion",
    "Module",
    "ModuleMetadata",
    "TypeDef",
    "TypeKind",
    "TypeBody",
    "TypeRef",
    "TypeRefKind",
    "Function",
    "Param",
    "Field_",
    "Binding",
    "Expression",
    "ControlFlowGraph",
    "Block",
    "Statement",
    "Terminator",
    "TerminatorKind",
    "Effect",
    "Lifetime",
    "GapMarker",
    "SemanticAnnotation",
    "AnnotationSource",
    "PreservationStatus",
    "SourceSpan",
    "TSSourceSpan",
    # Errors
    "ExtractionError",
    "ExtractionErrorCode",
    "SynthesisError",
    "SynthesisErrorCode",
    "ValidationError",
    "ValidationErrorCode",
    # Enums
    "AutomationLevel",
    "ExtractionMode",
    "EffectKind",
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
