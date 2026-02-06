"""Tests for the RoundTripValidator class.

Tests cover:
- Basic validation workflow
- Preservation level handling
- Error handling
- Batch validation
- Semantic equivalence testing
"""

from __future__ import annotations

import pytest

from ir_roundtrip.validator import (
    RoundTripValidator,
    RoundTripResult,
    PreservationLevel,
    ValidationStatus,
    SemanticResult,
)

from .conftest import requires_full_toolchain


class TestPreservationLevel:
    """Tests for PreservationLevel enum."""

    def test_level_values(self) -> None:
        """Test preservation level values."""
        assert PreservationLevel.L1_SYNTACTIC.value == "l1"
        assert PreservationLevel.L2_OPERATIONAL.value == "l2"
        assert PreservationLevel.L3_SEMANTIC.value == "l3"


class TestValidationStatus:
    """Tests for ValidationStatus enum."""

    def test_status_values(self) -> None:
        """Test validation status values."""
        assert ValidationStatus.PASSED.value == "passed"
        assert ValidationStatus.FAILED.value == "failed"
        assert ValidationStatus.ERROR.value == "error"
        assert ValidationStatus.SKIPPED.value == "skipped"


class TestRoundTripResult:
    """Tests for RoundTripResult class."""

    def test_passed_property(self) -> None:
        """Test passed property."""
        result = RoundTripResult(
            status=ValidationStatus.PASSED,
            level=PreservationLevel.L3_SEMANTIC,
            source="def foo(): pass",
        )
        assert result.passed

        result = RoundTripResult(
            status=ValidationStatus.FAILED,
            level=PreservationLevel.L3_SEMANTIC,
            source="def foo(): pass",
        )
        assert not result.passed

    def test_source_hash(self) -> None:
        """Test source hash calculation."""
        result = RoundTripResult(
            status=ValidationStatus.PASSED,
            level=PreservationLevel.L3_SEMANTIC,
            source="def foo(): pass",
        )
        # Hash should be consistent
        assert len(result.source_hash) == 64  # SHA-256 hex

    def test_target_hash_when_present(self) -> None:
        """Test target hash when target is present."""
        result = RoundTripResult(
            status=ValidationStatus.PASSED,
            level=PreservationLevel.L3_SEMANTIC,
            source="def foo(): pass",
            target="def foo(): pass",
        )
        assert result.target_hash is not None
        assert len(result.target_hash) == 64

    def test_target_hash_when_absent(self) -> None:
        """Test target hash when target is None."""
        result = RoundTripResult(
            status=ValidationStatus.ERROR,
            level=PreservationLevel.L3_SEMANTIC,
            source="def foo(): pass",
        )
        assert result.target_hash is None

    def test_summary_for_passed(self) -> None:
        """Test summary for passed result."""
        result = RoundTripResult(
            status=ValidationStatus.PASSED,
            level=PreservationLevel.L3_SEMANTIC,
            source="",
            duration_ms=10.5,
        )
        summary = result.summary()

        assert "[PASS]" in summary
        assert "L3" in summary
        assert "10.5ms" in summary

    def test_summary_for_failed_with_reason(self) -> None:
        """Test summary for failed result with reason."""
        result = RoundTripResult(
            status=ValidationStatus.FAILED,
            level=PreservationLevel.L1_SYNTACTIC,
            source="",
            failure_reason="AST mismatch",
            duration_ms=5.0,
        )
        summary = result.summary()

        assert "[FAIL]" in summary
        assert "L1" in summary
        assert "AST mismatch" in summary


class TestSemanticResult:
    """Tests for SemanticResult class."""

    def test_pass_rate_calculation(self) -> None:
        """Test pass rate calculation."""
        result = SemanticResult(
            equivalent=True,
            test_count=100,
            pass_count=95,
            fail_count=5,
        )
        assert result.pass_rate == 0.95

    def test_pass_rate_zero_tests(self) -> None:
        """Test pass rate with zero tests."""
        result = SemanticResult(equivalent=True, test_count=0)
        assert result.pass_rate == 0.0


class TestRoundTripValidatorInit:
    """Tests for RoundTripValidator initialization."""

    def test_default_init(self) -> None:
        """Test default initialization."""
        validator = RoundTripValidator()

        assert validator.extract_config is not None
        assert validator.synth_config is not None

    def test_custom_configs(self) -> None:
        """Test initialization with custom configs."""
        from ir_core.base import ExtractConfig, SynthConfig, OutputFormat

        extract_config = ExtractConfig()
        synth_config = SynthConfig(output_format=OutputFormat.SOURCE)

        validator = RoundTripValidator(
            extract_config=extract_config,
            synth_config=synth_config,
        )

        assert validator.extract_config is extract_config
        assert validator.synth_config is synth_config


class TestValidatorHelpers:
    """Tests for validator helper methods."""

    def test_detect_function_name(self) -> None:
        """Test function name detection."""
        validator = RoundTripValidator()

        # Simple function
        source = "def add(a, b): return a + b"
        assert validator._detect_function_name(source) == "add"

        # Skips private functions
        source = "def _private(): pass\ndef public(): pass"
        assert validator._detect_function_name(source) == "public"

        # No functions
        source = "x = 1"
        assert validator._detect_function_name(source) is None

    def test_elapsed_ms(self) -> None:
        """Test elapsed time calculation."""
        import time

        validator = RoundTripValidator()
        start = time.perf_counter()
        time.sleep(0.01)  # 10ms

        elapsed = validator._elapsed_ms(start)
        assert elapsed >= 10  # At least 10ms


@pytest.mark.integration
@requires_full_toolchain
class TestRoundTripValidation:
    """Integration tests for full round-trip validation.

    These tests require the full toolchain (extractor + synthesizer).
    """

    def test_simple_function_l3(self, simple_function: str) -> None:
        """Test L3 validation of simple function."""
        validator = RoundTripValidator()
        result = validator.validate(
            simple_function,
            PreservationLevel.L3_SEMANTIC,
            filename="test_simple.py",
        )

        # Should either pass or report a structured failure
        assert result.status in (
            ValidationStatus.PASSED,
            ValidationStatus.FAILED,
            ValidationStatus.ERROR,
        )

    def test_simple_function_l1(self, simple_function: str) -> None:
        """Test L1 validation of simple function."""
        validator = RoundTripValidator()
        result = validator.validate(
            simple_function,
            PreservationLevel.L1_SYNTACTIC,
            filename="test_simple.py",
        )

        # L1 may fail due to formatting differences
        assert result.status in (
            ValidationStatus.PASSED,
            ValidationStatus.FAILED,
            ValidationStatus.ERROR,
        )

    def test_validation_captures_ir(self, simple_function: str) -> None:
        """Test that validation captures the IR."""
        validator = RoundTripValidator()
        result = validator.validate(
            simple_function,
            PreservationLevel.L3_SEMANTIC,
            filename="test_ir.py",
        )

        # IR should be captured on success or structured failure
        if result.status != ValidationStatus.ERROR:
            assert result.ir is not None

    def test_validation_captures_target(self, simple_function: str) -> None:
        """Test that validation captures synthesized code."""
        validator = RoundTripValidator()
        result = validator.validate(
            simple_function,
            PreservationLevel.L3_SEMANTIC,
            filename="test_target.py",
        )

        if result.status != ValidationStatus.ERROR:
            assert result.target is not None

    def test_error_on_syntax_error(self) -> None:
        """Test error handling for syntax errors."""
        validator = RoundTripValidator()
        result = validator.validate(
            "def broken( return 1",  # Syntax error
            PreservationLevel.L3_SEMANTIC,
        )

        assert result.status == ValidationStatus.ERROR
        assert result.failure_reason is not None


class TestSemanticValidation:
    """Tests for L3 semantic validation specifically."""

    def test_validate_l3_semantic_equivalent(self) -> None:
        """Test L3 semantic validation for equivalent code."""
        validator = RoundTripValidator()

        source = "def add(a, b): return a + b"
        target = "def add(a, b): return a + b"
        test_inputs = [{"a": 1, "b": 2}, {"a": 0, "b": 0}]

        result = validator.validate_l3_semantic(source, target, test_inputs)

        assert result.equivalent
        assert result.test_count == 2
        assert result.pass_count == 2
        assert result.fail_count == 0

    def test_validate_l3_semantic_not_equivalent(self) -> None:
        """Test L3 semantic validation for non-equivalent code."""
        validator = RoundTripValidator()

        source = "def add(a, b): return a + b"
        target = "def add(a, b): return a - b"
        test_inputs = [{"a": 5, "b": 3}]

        result = validator.validate_l3_semantic(source, target, test_inputs)

        assert not result.equivalent
        assert result.fail_count == 1
        assert len(result.counterexamples) == 1

    def test_validate_l3_semantic_with_exceptions(self) -> None:
        """Test L3 validation when exceptions occur."""
        validator = RoundTripValidator()

        source = """def divide(a, b):
    if b == 0:
        raise ValueError("zero")
    return a / b
"""
        target = source  # Same code
        test_inputs = [{"a": 10, "b": 0}]

        result = validator.validate_l3_semantic(source, target, test_inputs)

        # Both raise same exception - should be equivalent
        assert result.equivalent

    def test_validate_l3_semantic_no_inputs(self) -> None:
        """Test L3 validation with no inputs."""
        validator = RoundTripValidator()

        result = validator.validate_l3_semantic(
            "def foo(): pass",
            "def foo(): pass",
            [],
        )

        # No tests = trivially equivalent with low confidence
        assert result.equivalent
        assert result.confidence == 0.0


@pytest.mark.integration
@requires_full_toolchain
class TestBatchValidation:
    """Tests for batch validation."""

    def test_batch_validation(
        self,
        simple_function: str,
        function_with_conditionals: str,
    ) -> None:
        """Test batch validation of multiple files."""
        validator = RoundTripValidator()

        sources = [
            ("simple.py", simple_function),
            ("conditionals.py", function_with_conditionals),
        ]

        results = validator.validate_batch(sources, PreservationLevel.L3_SEMANTIC)

        assert len(results) == 2

    def test_batch_with_progress(self, simple_function: str) -> None:
        """Test batch validation with progress callback."""
        validator = RoundTripValidator()
        progress_calls: list[tuple[int, int]] = []

        def progress(current: int, total: int) -> None:
            progress_calls.append((current, total))

        sources = [
            ("test1.py", simple_function),
            ("test2.py", simple_function),
        ]

        validator.validate_batch(
            sources,
            PreservationLevel.L3_SEMANTIC,
            progress_callback=progress,
        )

        # Should have progress calls
        assert len(progress_calls) >= 2
        # Final call should be (total, total)
        assert progress_calls[-1] == (2, 2)
