"""Pytest configuration and fixtures for ir-extract-python tests."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from ir_core.base import ExtractConfig, ExtractionMode, SemanticEnrichmentLevel

if TYPE_CHECKING:
    from ir_extract_python import PythonExtractor, PythonParser, PythonPatternMatcher


# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def extractor() -> PythonExtractor:
    """Create a PythonExtractor instance."""
    from ir_extract_python import PythonExtractor
    return PythonExtractor()


@pytest.fixture
def parser() -> PythonParser:
    """Create a PythonParser instance."""
    from ir_extract_python import PythonParser
    return PythonParser()


@pytest.fixture
def matcher() -> PythonPatternMatcher:
    """Create a PythonPatternMatcher instance."""
    from ir_extract_python import PythonPatternMatcher
    return PythonPatternMatcher()


@pytest.fixture
def config() -> ExtractConfig:
    """Create a default ExtractConfig without semantic enrichment."""
    return ExtractConfig(
        mode=ExtractionMode.FULL_MODULE,
        semantic_level=SemanticEnrichmentLevel.NONE,
    )


@pytest.fixture
def config_with_enrichment() -> ExtractConfig:
    """Create an ExtractConfig with basic semantic enrichment."""
    return ExtractConfig(
        mode=ExtractionMode.FULL_MODULE,
        semantic_level=SemanticEnrichmentLevel.BASIC,
    )


@pytest.fixture
def config_signature_only() -> ExtractConfig:
    """Create an ExtractConfig for signature-only extraction."""
    return ExtractConfig(
        mode=ExtractionMode.SIGNATURE_ONLY,
        semantic_level=SemanticEnrichmentLevel.NONE,
    )


@pytest.fixture
def config_with_layer0() -> ExtractConfig:
    """Create an ExtractConfig including Layer 0 (expressions)."""
    return ExtractConfig(
        mode=ExtractionMode.FULL_MODULE,
        semantic_level=SemanticEnrichmentLevel.NONE,
        include_layer0=True,
    )


@pytest.fixture
def simple_function_source() -> str:
    """Return simple function fixture source."""
    return (FIXTURES_DIR / "simple_function.py").read_text()


@pytest.fixture
def async_code_source() -> str:
    """Return async code fixture source."""
    return (FIXTURES_DIR / "async_code.py").read_text()


@pytest.fixture
def class_definitions_source() -> str:
    """Return class definitions fixture source."""
    return (FIXTURES_DIR / "class_definitions.py").read_text()


@pytest.fixture
def comprehensions_source() -> str:
    """Return comprehensions fixture source."""
    return (FIXTURES_DIR / "comprehensions.py").read_text()


@pytest.fixture
def pattern_matching_source() -> str:
    """Return pattern matching fixture source."""
    return (FIXTURES_DIR / "pattern_matching.py").read_text()


@pytest.fixture
def type_annotations_source() -> str:
    """Return type annotations fixture source."""
    return (FIXTURES_DIR / "type_annotations.py").read_text()


@pytest.fixture
def decorators_source() -> str:
    """Return decorators fixture source."""
    return (FIXTURES_DIR / "decorators.py").read_text()


@pytest.fixture
def exception_handling_source() -> str:
    """Return exception handling fixture source."""
    return (FIXTURES_DIR / "exception_handling.py").read_text()


def load_fixture(name: str) -> str:
    """Load a fixture file by name.

    Args:
        name: Fixture filename (with or without .py extension)

    Returns:
        Fixture source code
    """
    if not name.endswith(".py"):
        name = f"{name}.py"
    return (FIXTURES_DIR / name).read_text()


# Make load_fixture available for direct import
pytest.load_fixture = load_fixture  # type: ignore
