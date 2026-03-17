"""Shared utilities for IR tools.

This module provides utility functions that are shared across extractors
and synthesizers for different languages. These utilities abstract common
operations to avoid code duplication.

Primary utilities:
- ts_span_to_ir: Convert tree-sitter span to IR span (convenience wrapper)
- generate_content_hash: Compute deterministic hash for IR content
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SourceSpan
    from .treesitter import TSSourceSpan


def ts_span_to_ir(span: TSSourceSpan) -> SourceSpan:
    """Convert tree-sitter span to IR span.

    This is a convenience wrapper around TSSourceSpan.to_ir_span().
    It exists for backwards compatibility and as a functional alternative
    to the method-based conversion.

    Args:
        span: Tree-sitter source span with byte offsets

    Returns:
        IR source span with line/column for JSON serialization

    Example:
        from ir_core.utils import ts_span_to_ir
        from ir_core.treesitter import TSSourceSpan

        ts_span = TSSourceSpan(
            file="example.py",
            start_byte=0,
            end_byte=10,
            start_point=(0, 0),
            end_point=(0, 10),
        )
        ir_span = ts_span_to_ir(ts_span)
        # Or use: ts_span.to_ir_span()
    """
    return span.to_ir_span()


def generate_content_hash(data: dict) -> str:
    """Generate a deterministic content hash for IR data.

    Uses canonical JSON serialization (sorted keys, minimal separators)
    to ensure consistent hashing regardless of field order.

    Args:
        data: Dictionary to hash (typically from model.model_dump())

    Returns:
        Hex-encoded SHA-256 hash string

    Example:
        ir_dict = ir_version.model_dump(mode="json", exclude_none=True)
        hash_str = generate_content_hash(ir_dict)
    """
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_source_hash(source: str) -> str:
    """Compute SHA-256 hash of source code.

    Args:
        source: Source code as string

    Returns:
        Hex-encoded SHA-256 hash string
    """
    return hashlib.sha256(source.encode("utf-8")).hexdigest()
