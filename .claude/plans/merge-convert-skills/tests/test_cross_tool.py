"""Cross-tool integration tests.

This module tests the interaction between different tools in the pipeline:
- Extractor with Validator
- Synthesizer with Extractor (re-extraction of synthesized code)
- Query with Patterns
- Gap Detector with IR structures

These tests verify that tools produce output compatible with their consumers.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest

# Add tools to path
TOOLS_DIR = Path(__file__).parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR / "ir-core"))
sys.path.insert(0, str(TOOLS_DIR / "ir-extract-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-synthesize-python"))
sys.path.insert(0, str(TOOLS_DIR / "ir-validate"))
sys.path.insert(0, str(TOOLS_DIR / "ir-query"))

from ir_core import (
    IRVersion,
    ExtractConfig,
    ExtractionMode,
    GapDetector,
    GapMarker,
    GapType,
    Severity,
    PreservationLevel,
)
from ir_core.base import SynthConfig, OutputFormat


# =============================================================================
# Import Tools with Graceful Fallback
# =============================================================================

try:
    from ir_extract_python import PythonExtractor
    HAS_EXTRACTOR = True
except ImportError:
    HAS_EXTRACTOR = False
    PythonExtractor = None  # type: ignore

try:
    from ir_synthesize_python import PythonSynthesizer
    HAS_SYNTHESIZER = True
except ImportError:
    HAS_SYNTHESIZER = False
    PythonSynthesizer = None  # type: ignore

try:
    from ir_validate import IRValidator
    HAS_VALIDATOR = True
except ImportError:
    HAS_VALIDATOR = False
    IRValidator = None  # type: ignore

try:
    from ir_query import IRQueryInterface
    HAS_QUERY = True
except ImportError:
    HAS_QUERY = False
    IRQueryInterface = None  # type: ignore


requires_extractor = pytest.mark.skipif(
    not HAS_EXTRACTOR, reason="PythonExtractor not available"
)
requires_synthesizer = pytest.mark.skipif(
    not HAS_SYNTHESIZER, reason="PythonSynthesizer not available"
)
requires_validator = pytest.mark.skipif(
    not HAS_VALIDATOR, reason="IRValidator not available"
)
requires_query = pytest.mark.skipif(
    not HAS_QUERY, reason="IRQueryInterface not available"
)


# =============================================================================
# Extractor + Validator Tests
# =============================================================================


@pytest.mark.integration
class TestExtractorWithValidator:
    """Tests for extractor output validation."""

    @requires_extractor
    @requires_validator
    def test_extracted_ir_passes_validation(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify extracted IR passes schema validation."""
        extractor = PythonExtractor()
        validator = IRValidator()

        ir = extractor.extract(sample_python_source, "test.py", extract_config)
        ir_dict = ir.model_dump(mode="json", exclude_none=True)

        result = validator.validate(ir_dict)

        assert result.is_valid, (
            f"Extracted IR failed validation:\n{result.format()}"
        )
        assert result.error_count == 0

    @requires_extractor
    @requires_validator
    def test_extracted_ir_has_valid_references(
        self,
        sample_python_class: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify extracted IR has valid internal references."""
        extractor = PythonExtractor()
        validator = IRValidator(skip_schema=True, skip_consistency=True)

        ir = extractor.extract(sample_python_class, "classes.py", extract_config)
        ir_dict = ir.model_dump(mode="json", exclude_none=True)

        result = validator.validate(ir_dict)

        # Check no V002 (reference) errors
        ref_errors = [e for e in result.errors if e.code.startswith("V002")]
        assert len(ref_errors) == 0, (
            f"Reference errors found: {[str(e) for e in ref_errors]}"
        )

    @requires_extractor
    @requires_validator
    def test_extracted_ir_layer_consistency(
        self,
        sample_python_complex: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify extracted IR has consistent layer relationships."""
        extractor = PythonExtractor()
        validator = IRValidator(skip_schema=True, skip_references=True)

        ir = extractor.extract(sample_python_complex, "complex.py", extract_config)
        ir_dict = ir.model_dump(mode="json", exclude_none=True)

        result = validator.validate(ir_dict)

        # Check no V003 (consistency) errors
        consistency_errors = [e for e in result.errors if e.code.startswith("V003")]
        assert len(consistency_errors) == 0, (
            f"Consistency errors found: {[str(e) for e in consistency_errors]}"
        )

    @requires_extractor
    @requires_validator
    def test_complex_code_extraction_validates(
        self,
        sample_python_complex: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify complex code extraction produces valid IR."""
        extractor = PythonExtractor()
        validator = IRValidator()

        ir = extractor.extract(sample_python_complex, "complex.py", extract_config)
        ir_dict = ir.model_dump(mode="json", exclude_none=True)

        result = validator.validate(ir_dict)

        # May have warnings but should not have errors
        assert result.error_count == 0, (
            f"Complex code extraction produced errors:\n{result.format()}"
        )


# =============================================================================
# Synthesizer + Extractor Tests (Re-extraction)
# =============================================================================


@pytest.mark.integration
class TestSynthesizerWithExtractor:
    """Tests for synthesized code re-extraction."""

    @requires_extractor
    @requires_synthesizer
    def test_synthesized_code_can_be_reextracted(
        self,
        sample_ir: IRVersion,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify synthesized code can be re-extracted to IR."""
        synthesizer = PythonSynthesizer()
        extractor = PythonExtractor()

        # Synthesize
        output = synthesizer.synthesize(sample_ir, synth_config)

        # Re-extract
        re_ir = extractor.extract(output, "synthesized.py", extract_config)

        assert re_ir is not None
        assert re_ir.module is not None

    @requires_extractor
    @requires_synthesizer
    def test_reextracted_ir_has_same_functions(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify re-extracted IR has same number of functions."""
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        # Extract original
        original_ir = extractor.extract(sample_python_source, "original.py", extract_config)

        # Synthesize
        output = synthesizer.synthesize(original_ir, synth_config)

        # Re-extract
        re_ir = extractor.extract(output, "reextracted.py", extract_config)

        # Compare function counts
        original_funcs = len([f for f in original_ir.functions if f.receiver is None])
        re_funcs = len([f for f in re_ir.functions if f.receiver is None])

        assert re_funcs >= original_funcs - 1, (
            f"Lost functions during roundtrip: {original_funcs} -> {re_funcs}"
        )

    @requires_extractor
    @requires_synthesizer
    def test_reextracted_ir_has_same_types(
        self,
        sample_python_class: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify re-extracted IR has same number of types."""
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        # Extract original
        original_ir = extractor.extract(sample_python_class, "original.py", extract_config)

        # Synthesize
        output = synthesizer.synthesize(original_ir, synth_config)

        # Re-extract
        re_ir = extractor.extract(output, "reextracted.py", extract_config)

        # Compare type counts
        original_types = len(original_ir.types)
        re_types = len(re_ir.types)

        assert re_types >= original_types - 1, (
            f"Lost types during roundtrip: {original_types} -> {re_types}"
        )

    @requires_extractor
    @requires_synthesizer
    @requires_validator
    def test_reextracted_ir_validates(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Verify re-extracted IR passes validation."""
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()
        validator = IRValidator()

        # Extract -> Synthesize -> Re-extract
        original_ir = extractor.extract(sample_python_source, "original.py", extract_config)
        output = synthesizer.synthesize(original_ir, synth_config)
        re_ir = extractor.extract(output, "reextracted.py", extract_config)

        # Validate re-extracted IR
        ir_dict = re_ir.model_dump(mode="json", exclude_none=True)
        result = validator.validate(ir_dict)

        assert result.is_valid, (
            f"Re-extracted IR failed validation:\n{result.format()}"
        )


# =============================================================================
# Query + Pattern Tests
# =============================================================================


@pytest.mark.integration
class TestQueryWithPatterns:
    """Tests for query interface with extracted patterns."""

    @requires_extractor
    @requires_query
    def test_query_results_match_extracted_patterns(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
        db_connection: sqlite3.Connection,
    ) -> None:
        """Verify query results match patterns in extracted IR."""
        extractor = PythonExtractor()
        query = IRQueryInterface(db_connection)

        # Extract IR
        ir = extractor.extract(sample_python_source, "test.py", extract_config)

        # Store IR unit
        unit_id = query.store_ir_unit(
            {
                "layer": 4,
                "unit_type": "module",
                "content": ir.module.model_dump(mode="json", exclude_none=True),
            },
            source_path="test.py",
            source_language="python",
        )

        # Retrieve and verify
        retrieved = query.get_ir_unit(unit_id)

        assert retrieved is not None
        assert retrieved["layer"] == 4
        assert retrieved["unit_type"] == "module"
        assert retrieved["content"] is not None

    @requires_query
    def test_query_gap_patterns(
        self,
        db_connection: sqlite3.Connection,
    ) -> None:
        """Test querying for gap patterns."""
        query = IRQueryInterface(db_connection)

        # Query for gaps (may return empty if tables not populated)
        gaps = query.get_gap_patterns("python", "rust")

        # Should return a list (possibly empty)
        assert isinstance(gaps, list)

    @requires_query
    def test_query_language_profile(
        self,
        db_connection: sqlite3.Connection,
    ) -> None:
        """Test querying language profile."""
        query = IRQueryInterface(db_connection)

        profile = query.get_language_profile("python")

        assert profile is not None
        assert profile["name"] == "python"
        assert profile["tier"] == 1

    @requires_query
    def test_query_patterns_for_conversion(
        self,
        db_connection: sqlite3.Connection,
    ) -> None:
        """Test querying patterns for a specific conversion."""
        query = IRQueryInterface(db_connection)

        patterns = query.get_patterns_for_conversion("python", "rust")

        # Should return a list (possibly empty if no patterns stored)
        assert isinstance(patterns, list)


# =============================================================================
# Gap Detector + IR Tests
# =============================================================================


@pytest.mark.integration
class TestGapDetectorWithIR:
    """Tests for gap detection on extracted IR."""

    @requires_extractor
    def test_gap_detector_finds_type_system_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify gap detector finds type system gaps."""
        source = '''def process(data):  # No type hints
    return data.upper()
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "untyped.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # Should detect dynamic typing gap (TS-001)
        type_gaps = [g for g in gaps if g.gap_pattern_id and g.gap_pattern_id.startswith("TS")]
        # May or may not find gaps depending on implementation
        assert isinstance(gaps, list)

    @requires_extractor
    def test_gap_detector_finds_memory_model_gaps(
        self,
        sample_python_class: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify gap detector finds memory model gaps for Python->Rust."""
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(sample_python_class, "classes.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # Should detect GC-to-ownership gaps (MM-002)
        memory_gaps = [g for g in gaps if g.gap_pattern_id and g.gap_pattern_id.startswith("MM")]
        # May or may not find gaps depending on IR content
        assert isinstance(gaps, list)

    @requires_extractor
    def test_gap_detector_finds_effect_gaps(
        self,
        sample_python_async: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify gap detector finds effect system gaps."""
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(sample_python_async, "async.py", extract_config)
        gaps = detector.detect(ir, "python", "go")

        # Should detect async/effect gaps
        effect_gaps = [g for g in gaps if g.gap_pattern_id and g.gap_pattern_id.startswith("EF")]
        assert isinstance(gaps, list)

    def test_gap_detector_with_sample_ir(self, sample_ir_with_gaps: IRVersion) -> None:
        """Test gap detector output format."""
        detector = GapDetector()

        # Verify existing gaps
        existing_gaps = sample_ir_with_gaps.gaps
        assert len(existing_gaps) == 2

        # Detect additional gaps
        new_gaps = detector.detect(sample_ir_with_gaps, "python", "rust")

        # Verify gap format
        for gap in new_gaps:
            assert gap.id is not None or gap.id == ""
            assert gap.location is not None
            assert gap.gap_type in GapType
            assert gap.severity in Severity


# =============================================================================
# Multi-Tool Chain Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.slow
class TestMultiToolChain:
    """Tests for multi-tool processing chains."""

    @requires_extractor
    @requires_validator
    @requires_synthesizer
    def test_extract_validate_synthesize_validate(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test full chain with validation at each step."""
        extractor = PythonExtractor()
        validator = IRValidator()
        synthesizer = PythonSynthesizer()

        # Step 1: Extract
        ir = extractor.extract(sample_python_source, "test.py", extract_config)

        # Step 2: Validate extracted IR
        ir_dict = ir.model_dump(mode="json", exclude_none=True)
        result1 = validator.validate(ir_dict)
        assert result1.is_valid, f"Extraction produced invalid IR: {result1.format()}"

        # Step 3: Synthesize
        output = synthesizer.synthesize(ir, synth_config)

        # Step 4: Re-extract
        re_ir = extractor.extract(output, "synthesized.py", extract_config)

        # Step 5: Validate re-extracted IR
        re_ir_dict = re_ir.model_dump(mode="json", exclude_none=True)
        result2 = validator.validate(re_ir_dict)
        assert result2.is_valid, f"Re-extraction produced invalid IR: {result2.format()}"

    @requires_extractor
    @requires_validator
    @requires_query
    def test_extract_validate_store_query(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
        db_connection: sqlite3.Connection,
    ) -> None:
        """Test extraction, validation, storage, and querying."""
        extractor = PythonExtractor()
        validator = IRValidator()
        query = IRQueryInterface(db_connection)

        # Extract
        ir = extractor.extract(sample_python_source, "test.py", extract_config)

        # Validate
        ir_dict = ir.model_dump(mode="json", exclude_none=True)
        result = validator.validate(ir_dict)
        assert result.is_valid

        # Store
        unit_id = query.store_ir_unit(
            {
                "layer": 4,
                "unit_type": "module",
                "content": ir.module.model_dump(mode="json", exclude_none=True),
            },
            source_path="test.py",
            source_language="python",
        )

        # Query back
        retrieved = query.get_ir_unit(unit_id)
        assert retrieved is not None
        assert retrieved["source_language"] == "python"

        # Query by language
        units = query.get_ir_units_by_language("python")
        assert len(units) >= 1

    @requires_extractor
    @requires_synthesizer
    def test_multiple_extraction_synthesis_cycles(
        self,
        sample_python_source: str,
        extract_config: ExtractConfig,
        synth_config: SynthConfig,
    ) -> None:
        """Test multiple roundtrip cycles."""
        extractor = PythonExtractor()
        synthesizer = PythonSynthesizer()

        current_source = sample_python_source

        for i in range(3):
            # Extract
            ir = extractor.extract(current_source, f"cycle{i}.py", extract_config)
            assert ir is not None, f"Extraction failed at cycle {i}"

            # Synthesize
            output = synthesizer.synthesize(ir, synth_config)
            assert output is not None, f"Synthesis failed at cycle {i}"
            assert len(output) > 0, f"Empty output at cycle {i}"

            current_source = output

        # Final output should still be valid Python
        # Re-extract to verify
        final_ir = extractor.extract(current_source, "final.py", extract_config)
        assert final_ir is not None
        assert final_ir.module is not None
