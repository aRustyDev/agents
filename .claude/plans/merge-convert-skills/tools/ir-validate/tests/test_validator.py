"""Tests for the main IRValidator class."""

import pytest
from typing import Any

from ir_validate import IRValidator, ValidationResult
from ir_validate.errors import ValidationErrorCode


class TestIRValidator:
    """Tests for IRValidator."""

    def test_validate_minimal_valid(self, minimal_valid_ir: dict[str, Any]) -> None:
        """Test validation of minimal valid IR."""
        validator = IRValidator(skip_schema=True)  # Skip schema if jsonschema not installed
        result = validator.validate(minimal_valid_ir)

        assert isinstance(result, ValidationResult)
        # Should have no errors (warnings may exist)
        assert result.error_count == 0

    def test_validate_complex_valid(self, complex_valid_ir: dict[str, Any]) -> None:
        """Test validation of complex valid IR."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(complex_valid_ir)

        assert isinstance(result, ValidationResult)
        assert result.error_count == 0

    def test_validate_with_dangling_refs(self, ir_with_dangling_refs: dict[str, Any]) -> None:
        """Test detection of dangling references."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(ir_with_dangling_refs)

        assert not result.is_valid
        assert result.error_count > 0

        # Check that we found the dangling ref errors
        error_codes = [e.code for e in result.errors]
        assert any(ValidationErrorCode.V002_DANGLING_REF.value in code for code in error_codes)

    def test_validate_with_circular_refs(self, ir_with_circular_refs: dict[str, Any]) -> None:
        """Test detection of circular references."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(ir_with_circular_refs)

        # Should detect circular reference
        error_codes = [e.code for e in result.errors]
        assert any(ValidationErrorCode.V002_CIRCULAR_REF.value in code for code in error_codes)

    def test_validate_with_invalid_preservation(
        self, ir_with_invalid_preservation: dict[str, Any]
    ) -> None:
        """Test detection of invalid preservation levels."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(ir_with_invalid_preservation)

        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert any(
            ValidationErrorCode.V004_INVALID_PRESERVATION_LEVEL.value in code
            for code in error_codes
        )

    def test_validate_with_inconsistent_visibility(
        self, ir_with_inconsistent_visibility: dict[str, Any]
    ) -> None:
        """Test detection of visibility inconsistencies."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(ir_with_inconsistent_visibility)

        # Should have at least a warning about exporting private as public
        warning_codes = [e.code for e in result.warnings]
        assert any(
            ValidationErrorCode.V003_VISIBILITY_INCONSISTENT.value in code
            for code in warning_codes
        )

    def test_strict_mode(self, ir_with_inconsistent_visibility: dict[str, Any]) -> None:
        """Test strict mode treats warnings as errors."""
        # Non-strict mode
        validator_normal = IRValidator(skip_schema=True, strict=False)
        result_normal = validator_normal.validate(ir_with_inconsistent_visibility)

        # Strict mode
        validator_strict = IRValidator(skip_schema=True, strict=True)
        result_strict = validator_strict.validate(ir_with_inconsistent_visibility)

        # If there are warnings, strict mode should fail where normal passes
        if result_normal.warning_count > 0:
            assert not result_strict.is_valid

    def test_skip_options(self, ir_with_dangling_refs: dict[str, Any]) -> None:
        """Test skip options work correctly."""
        # Skip references - should not find dangling ref errors
        validator = IRValidator(
            skip_schema=True,
            skip_references=True,
            skip_consistency=True,
        )
        result = validator.validate(ir_with_dangling_refs)

        # Should not find reference errors when skipped
        ref_errors = [
            e for e in result.errors
            if e.code.startswith(ValidationErrorCode.V002_DANGLING_REF.value[:4])
        ]
        assert len(ref_errors) == 0

    def test_result_format_human(self, minimal_valid_ir: dict[str, Any]) -> None:
        """Test human-readable output format."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(minimal_valid_ir)

        output = result.format(output_format="human", use_color=False)
        assert "IR Validation Report" in output
        assert "Status:" in output

    def test_result_format_json(self, minimal_valid_ir: dict[str, Any]) -> None:
        """Test JSON output format."""
        import json

        validator = IRValidator(skip_schema=True)
        result = validator.validate(minimal_valid_ir)

        output = result.format(output_format="json")
        parsed = json.loads(output)

        assert "summary" in parsed
        assert "errors" in parsed
        assert isinstance(parsed["summary"]["passed"], bool)

    def test_result_format_compact(self, ir_with_dangling_refs: dict[str, Any]) -> None:
        """Test compact output format."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(ir_with_dangling_refs)

        output = result.format(output_format="compact")
        # Compact format should have summary line
        assert "# " in output


class TestValidationResult:
    """Tests for ValidationResult properties."""

    def test_error_count(self, ir_with_dangling_refs: dict[str, Any]) -> None:
        """Test error count property."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(ir_with_dangling_refs)

        # Should match count of severity="error"
        expected = sum(1 for e in result.errors if e.severity == "error")
        assert result.error_count == expected

    def test_warning_count(self, ir_with_inconsistent_visibility: dict[str, Any]) -> None:
        """Test warning count property."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(ir_with_inconsistent_visibility)

        # Should match count of severity="warning"
        expected = sum(1 for e in result.errors if e.severity == "warning")
        assert result.warning_count == expected

    def test_warnings_property(self, ir_with_inconsistent_visibility: dict[str, Any]) -> None:
        """Test warnings property returns only warnings."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(ir_with_inconsistent_visibility)

        for warning in result.warnings:
            assert warning.severity == "warning"

    def test_info_messages_property(self, complex_valid_ir: dict[str, Any]) -> None:
        """Test info_messages property."""
        validator = IRValidator(skip_schema=True)
        result = validator.validate(complex_valid_ir)

        for info in result.info_messages:
            assert info.severity == "info"
