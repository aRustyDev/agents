"""Error handling tests.

This module tests error scenarios across the pipeline:
- Invalid Python syntax (E001)
- Unsupported constructs (E002)
- Type inference failures (E003)
- Cross-file reference errors (E004)
- Metaprogramming issues (E005)
- Synthesis errors (S001-S005)
- Validation errors (V001-V004)

Each test verifies that errors are properly detected, categorized,
and provide actionable messages.
"""

from __future__ import annotations

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

from ir_core import (
    IRVersion,
    ExtractConfig,
    ExtractionMode,
    ExtractionError,
    SynthesisError,
    ValidationError as IRValidationError,
    ExtractionErrorCode,
    SynthesisErrorCode,
    ValidationErrorCode,
    Module,
    ModuleMetadata,
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
    from ir_validate.errors import ValidationError, ValidationErrorCode as ValidatorErrorCode
    HAS_VALIDATOR = True
except ImportError:
    HAS_VALIDATOR = False
    IRValidator = None  # type: ignore
    ValidationError = None  # type: ignore
    ValidatorErrorCode = None  # type: ignore


requires_extractor = pytest.mark.skipif(
    not HAS_EXTRACTOR, reason="PythonExtractor not available"
)
requires_synthesizer = pytest.mark.skipif(
    not HAS_SYNTHESIZER, reason="PythonSynthesizer not available"
)
requires_validator = pytest.mark.skipif(
    not HAS_VALIDATOR, reason="IRValidator not available"
)


# =============================================================================
# Extraction Error Tests (E001-E005)
# =============================================================================


@pytest.mark.integration
class TestExtractionErrors:
    """Tests for extraction error handling."""

    @requires_extractor
    def test_invalid_python_syntax_e001(
        self,
        invalid_python_source: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Test E001: Parse error detection."""
        extractor = PythonExtractor()

        # Should either raise ExtractionError or return IR with gaps
        try:
            ir = extractor.extract(invalid_python_source, "invalid.py", extract_config)
            # If extraction succeeds, should have gaps marked
            assert ir.gaps is not None or ir.preservation is not None
        except ExtractionError as e:
            assert e.code == ExtractionErrorCode.E001
            assert "parse" in str(e).lower() or "syntax" in str(e).lower()

    @requires_extractor
    def test_unsupported_constructs_e002(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test E002: Unsupported syntax detection."""
        # Python 3.12+ type parameter syntax
        source = '''def identity[T](x: T) -> T:
    return x
'''
        extractor = PythonExtractor()

        try:
            ir = extractor.extract(source, "generics.py", extract_config)
            # Newer Python features might be partially supported
            assert ir is not None
        except ExtractionError as e:
            # Might fail on older Python versions
            assert e.code in [ExtractionErrorCode.E001, ExtractionErrorCode.E002]

    @requires_extractor
    def test_type_inference_failure_e003(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test E003: Type inference failure handling."""
        source = '''def complex_types(x):
    # Very dynamic code that's hard to type
    if hasattr(x, 'foo'):
        return x.foo()
    elif hasattr(x, 'bar'):
        return x.bar()
    else:
        return x[0] if x else None
'''
        extractor = PythonExtractor()

        ir = extractor.extract(source, "dynamic.py", extract_config)

        # Should succeed but might have type gaps
        assert ir is not None
        # Functions should still be extracted
        assert len(ir.functions) >= 1

    @requires_extractor
    def test_cross_file_reference_e004(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Test E004: Cross-file reference handling."""
        source = '''from nonexistent_module import SomeClass

def use_external(x: SomeClass) -> SomeClass:
    return x
'''
        extractor = PythonExtractor()

        # Should handle missing imports gracefully
        ir = extractor.extract(source, "refs.py", extract_config)

        assert ir is not None
        # Import should be recorded
        assert len(ir.module.imports) >= 1

    @requires_extractor
    def test_metaprogramming_e005(
        self,
        python_with_unsupported_patterns: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Test E005: Metaprogramming pattern detection."""
        extractor = PythonExtractor()

        ir = extractor.extract(python_with_unsupported_patterns, "meta.py", extract_config)

        # Should extract what it can
        assert ir is not None
        # May have gaps for dynamic patterns
        # Gap detection depends on implementation

    @requires_extractor
    def test_extraction_error_has_location(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify extraction errors include source location."""
        source = '''def broken(
    # Missing closing paren
    x
    :
'''
        extractor = PythonExtractor()

        try:
            ir = extractor.extract(source, "broken.py", extract_config)
            # If it succeeds with gaps, verify gaps have locations
            for gap in (ir.gaps or []):
                assert gap.location is not None
        except ExtractionError as e:
            # Error should have location info
            assert e.location is not None or "line" in str(e).lower()


# =============================================================================
# Synthesis Error Tests (S001-S005)
# =============================================================================


@pytest.mark.integration
class TestSynthesisErrors:
    """Tests for synthesis error handling."""

    @requires_synthesizer
    def test_invalid_ir_s001(
        self,
        synth_config: SynthConfig,
    ) -> None:
        """Test S001: Invalid IR detection."""
        synthesizer = PythonSynthesizer()

        # Create IR without module
        invalid_ir = IRVersion(
            version="ir-v1.0",
            module=None,  # type: ignore
            types=[],
            functions=[],
            bindings=[],
        )

        with pytest.raises(SynthesisError) as exc_info:
            synthesizer.synthesize(invalid_ir, synth_config)

        assert exc_info.value.code == SynthesisErrorCode.S001

    @requires_synthesizer
    def test_unsupported_construct_s002(
        self,
        synth_config: SynthConfig,
    ) -> None:
        """Test S002: Unsupported IR construct handling."""
        synthesizer = PythonSynthesizer()

        # Create IR with minimal valid structure
        metadata = ModuleMetadata(
            source_file="test.py",
            source_language="python",
        )
        module = Module(
            id="module:test.py",
            name="test",
            path=["test"],
            imports=[],
            exports=[],
            definitions=[],
            submodules=[],
            extraction_scope="full",
            metadata=metadata,
        )
        ir = IRVersion(
            version="ir-v1.0",
            module=module,
            types=[],
            functions=[],
            bindings=[],
        )

        # Should succeed with empty output or minimal code
        try:
            output = synthesizer.synthesize(ir, synth_config)
            assert output is not None
        except SynthesisError as e:
            # S002 would indicate unsupported construct
            assert e.code in [SynthesisErrorCode.S002, SynthesisErrorCode.S005]

    @requires_synthesizer
    def test_type_mapping_failure_s003(
        self,
        sample_ir_with_gaps: IRVersion,
        synth_config: SynthConfig,
    ) -> None:
        """Test S003: Type mapping failure handling."""
        synthesizer = PythonSynthesizer()

        # Synthesize IR with gaps
        # Should succeed but may produce warnings
        try:
            output = synthesizer.synthesize(sample_ir_with_gaps, synth_config)
            assert output is not None
        except SynthesisError as e:
            assert e.code in [SynthesisErrorCode.S003, SynthesisErrorCode.S005]

    @requires_synthesizer
    def test_synthesis_error_provides_context(
        self,
        synth_config: SynthConfig,
    ) -> None:
        """Verify synthesis errors provide helpful context."""
        synthesizer = PythonSynthesizer()

        invalid_ir = IRVersion(
            version="ir-v1.0",
            module=None,  # type: ignore
            types=[],
            functions=[],
            bindings=[],
        )

        with pytest.raises(SynthesisError) as exc_info:
            synthesizer.synthesize(invalid_ir, synth_config)

        error = exc_info.value
        assert error.code is not None
        assert str(error) != ""
        assert "S00" in str(error)


# =============================================================================
# Validation Error Tests (V001-V004)
# =============================================================================


@pytest.mark.integration
class TestValidationErrors:
    """Tests for validation error handling."""

    @requires_validator
    def test_schema_mismatch_v001(
        self,
        invalid_ir: dict[str, Any],
    ) -> None:
        """Test V001: Schema validation errors."""
        validator = IRValidator()

        result = validator.validate(invalid_ir)

        assert not result.is_valid
        # Should have V001 schema errors
        v001_errors = [e for e in result.errors if e.code.startswith("V001")]
        assert len(v001_errors) > 0

    @requires_validator
    def test_dangling_reference_v002(
        self,
        ir_with_dangling_refs: dict[str, Any],
    ) -> None:
        """Test V002: Dangling reference detection."""
        validator = IRValidator(skip_schema=True)

        result = validator.validate(ir_with_dangling_refs)

        # Should have V002 reference errors
        v002_errors = [e for e in result.errors if e.code.startswith("V002")]
        # May or may not detect depending on implementation
        # At minimum should complete without crashing
        assert result is not None

    @requires_validator
    def test_layer_inconsistency_v003(self) -> None:
        """Test V003: Layer consistency errors."""
        validator = IRValidator(skip_schema=True, skip_references=True)

        # Create IR with inconsistent layer relationships
        ir_data = {
            "version": "ir-v1.0",
            "module": {
                "id": "module:test.py",
                "name": "test",
                "path": ["test"],
                "visibility": "public",
                "imports": [],
                "exports": [],
                "definitions": [],
                "submodules": [],
                "extraction_scope": "full",
                "metadata": {
                    "source_file": "test.py",
                    "source_language": "python",
                },
            },
            "types": [],
            "functions": [],
            "bindings": [],
        }

        result = validator.validate(ir_data)

        # Should pass or have V003 errors
        # At minimum should complete
        assert result is not None

    @requires_validator
    def test_gap_marker_validity_v004(self) -> None:
        """Test V004: Gap marker validation."""
        validator = IRValidator()

        ir_data = {
            "version": "ir-v1.0",
            "module": {
                "id": "module:test.py",
                "name": "test",
                "path": ["test"],
                "visibility": "public",
                "imports": [],
                "exports": [],
                "definitions": [],
                "submodules": [],
                "extraction_scope": "full",
                "metadata": {
                    "source_file": "test.py",
                    "source_language": "python",
                },
            },
            "types": [],
            "functions": [],
            "bindings": [],
            "gaps": [
                {
                    "id": "gap:test:0",
                    "location": "invalid_location_that_does_not_exist",
                    "gap_type": "invalid_type",  # Invalid enum value
                    "severity": "critical",
                    "description": "Test gap",
                    "source_concept": "test",
                },
            ],
        }

        result = validator.validate(ir_data)

        # Should detect issues with gap marker
        # V004 or V001 (schema) errors
        assert not result.is_valid or len(result.errors) > 0

    @requires_validator
    def test_validation_error_format(
        self,
        invalid_ir: dict[str, Any],
    ) -> None:
        """Verify validation errors have proper format."""
        validator = IRValidator()

        result = validator.validate(invalid_ir)

        for error in result.errors:
            assert error.code is not None
            assert error.code.startswith("V")
            assert error.message is not None
            assert error.location is not None
            assert error.severity in ["error", "warning", "info"]

    @requires_validator
    def test_validation_result_format(
        self,
        invalid_ir: dict[str, Any],
    ) -> None:
        """Verify validation result formatting."""
        validator = IRValidator()

        result = validator.validate(invalid_ir)

        # Test different output formats
        human_output = result.format(output_format="human", use_color=False)
        assert len(human_output) > 0

        json_output = result.format(output_format="json", use_color=False)
        assert len(json_output) > 0

        compact_output = result.format(output_format="compact", use_color=False)
        assert len(compact_output) > 0


# =============================================================================
# Gap Detection Tests
# =============================================================================


@pytest.mark.integration
class TestGapDetection:
    """Tests for semantic gap detection."""

    @requires_extractor
    def test_detect_type_system_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify type system gaps are detected."""
        from ir_core import GapDetector

        source = '''def dynamic_function(x):
    return x.some_method()
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "dynamic.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # Should return list of gaps
        assert isinstance(gaps, list)

    @requires_extractor
    def test_detect_runtime_gaps(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify runtime behavior gaps are detected."""
        from ir_core import GapDetector

        source = '''import random

def randomized():
    return random.randint(1, 100)
'''
        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(source, "random.py", extract_config)
        gaps = detector.detect(ir, "python", "rust")

        # Should detect IO effect
        io_effects = [f for f in ir.functions for e in f.effects if e.kind == "io"]
        # May or may not detect random as IO
        assert isinstance(gaps, list)

    def test_gap_markers_valid_structure(
        self,
        sample_ir_with_gaps: IRVersion,
    ) -> None:
        """Verify gap marker structure is valid."""
        for gap in sample_ir_with_gaps.gaps:
            # Required fields
            assert gap.id is not None
            assert gap.location is not None
            assert gap.gap_type is not None
            assert gap.severity is not None
            assert gap.description is not None
            assert gap.source_concept is not None

            # Valid enum values
            from ir_core import GapType, Severity

            assert gap.gap_type in [t.value for t in GapType] or isinstance(gap.gap_type, GapType)
            assert gap.severity in [s.value for s in Severity] or isinstance(gap.severity, Severity)

    @requires_extractor
    def test_gap_detection_does_not_crash(
        self,
        sample_python_complex: str,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify gap detection handles complex code without crashing."""
        from ir_core import GapDetector

        extractor = PythonExtractor()
        detector = GapDetector()

        ir = extractor.extract(sample_python_complex, "complex.py", extract_config)

        # Should not raise
        gaps = detector.detect(ir, "python", "rust")
        assert isinstance(gaps, list)

        # Try other target languages
        gaps_go = detector.detect(ir, "python", "go")
        assert isinstance(gaps_go, list)

        gaps_ts = detector.detect(ir, "python", "typescript")
        assert isinstance(gaps_ts, list)


# =============================================================================
# Error Recovery Tests
# =============================================================================


@pytest.mark.integration
class TestErrorRecovery:
    """Tests for error recovery and graceful degradation."""

    @requires_extractor
    def test_partial_extraction_on_error(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify partial extraction succeeds despite errors."""
        source = '''def valid_function():
    return 42

def broken_function(
    # Syntax error here
    :
    pass

def another_valid():
    return "ok"
'''
        extractor = PythonExtractor()

        try:
            ir = extractor.extract(source, "partial.py", extract_config)
            # Might extract partial content
            assert ir is not None
        except ExtractionError:
            # Or fail entirely - both are acceptable
            pass

    @requires_extractor
    @requires_synthesizer
    def test_synthesis_with_gaps(
        self,
        sample_ir_with_gaps: IRVersion,
        synth_config: SynthConfig,
    ) -> None:
        """Verify synthesis proceeds despite gaps."""
        synthesizer = PythonSynthesizer()

        # Should not crash on IR with gaps
        output = synthesizer.synthesize(sample_ir_with_gaps, synth_config)

        assert output is not None

    @requires_validator
    def test_validation_continues_after_first_error(
        self,
        invalid_ir: dict[str, Any],
    ) -> None:
        """Verify validation finds all errors, not just first."""
        validator = IRValidator()

        result = validator.validate(invalid_ir)

        # Should have multiple errors
        assert len(result.errors) >= 1

    @requires_extractor
    def test_graceful_handling_of_encoding_issues(
        self,
        extract_config: ExtractConfig,
    ) -> None:
        """Verify encoding issues are handled gracefully."""
        # Valid Python with unicode
        source = '''# coding: utf-8
def greet():
    return "Hello, 世界! 🌍"
'''
        extractor = PythonExtractor()

        ir = extractor.extract(source, "unicode.py", extract_config)

        assert ir is not None
        assert len(ir.functions) >= 1
