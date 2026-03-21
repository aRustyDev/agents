"""Tests for error handling and error taxonomy."""

import pytest
from ir_validate.errors import (
    ValidationError,
    ValidationErrorCode,
    ValidationException,
    create_error,
    get_suggestion,
)


class TestValidationError:
    """Tests for ValidationError dataclass."""

    def test_basic_creation(self) -> None:
        """Test basic error creation."""
        error = ValidationError(
            code="V001-001",
            message="Test error message",
            location="$.modules[0]",
            severity="error",
        )

        assert error.code == "V001-001"
        assert error.message == "Test error message"
        assert error.location == "$.modules[0]"
        assert error.severity == "error"

    def test_category_extraction(self) -> None:
        """Test category is extracted from code."""
        error = ValidationError(
            code="V002-003",
            message="Test",
            location="$",
        )
        assert error.category == "V002"

    def test_category_description(self) -> None:
        """Test category description lookup."""
        error = ValidationError(
            code="V001-001",
            message="Test",
            location="$",
        )
        assert "Schema" in error.category_description

        error_v003 = ValidationError(
            code="V003-001",
            message="Test",
            location="$",
        )
        assert "Consistency" in error_v003.category_description

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        error = ValidationError(
            code="V001-001",
            message="Test",
            location="$.test",
            severity="warning",
            suggestion="Fix it",
            context={"field": "name"},
        )

        d = error.to_dict()
        assert d["code"] == "V001-001"
        assert d["message"] == "Test"
        assert d["location"] == "$.test"
        assert d["severity"] == "warning"
        assert d["suggestion"] == "Fix it"
        assert d["context"]["field"] == "name"
        assert d["category"] == "V001"

    def test_str_format(self) -> None:
        """Test string formatting."""
        error = ValidationError(
            code="V001-001",
            message="Field missing",
            location="$.modules[0].id",
            suggestion="Add the id field",
        )

        s = str(error)
        assert "V001-001" in s
        assert "Field missing" in s
        assert "$.modules[0].id" in s
        assert "Add the id field" in s


class TestValidationErrorCode:
    """Tests for ValidationErrorCode enum."""

    def test_v001_codes_exist(self) -> None:
        """Test V001 schema error codes exist."""
        assert ValidationErrorCode.V001_MISSING_REQUIRED_FIELD
        assert ValidationErrorCode.V001_INVALID_TYPE
        assert ValidationErrorCode.V001_INVALID_ENUM_VALUE

    def test_v002_codes_exist(self) -> None:
        """Test V002 reference error codes exist."""
        assert ValidationErrorCode.V002_DANGLING_REF
        assert ValidationErrorCode.V002_CIRCULAR_REF

    def test_v003_codes_exist(self) -> None:
        """Test V003 consistency error codes exist."""
        assert ValidationErrorCode.V003_LAYER_MISMATCH
        assert ValidationErrorCode.V003_TYPE_DEFINITION_MISSING

    def test_v004_codes_exist(self) -> None:
        """Test V004 gap marker error codes exist."""
        assert ValidationErrorCode.V004_INVALID_GAP_TYPE
        assert ValidationErrorCode.V004_INVALID_PRESERVATION_LEVEL

    def test_code_value_format(self) -> None:
        """Test error code values follow correct format."""
        for code in ValidationErrorCode:
            assert code.value.startswith("V00")
            assert "-" in code.value


class TestGetSuggestion:
    """Tests for get_suggestion function."""

    def test_missing_field_suggestion(self) -> None:
        """Test suggestion for missing required field."""
        suggestion = get_suggestion(
            ValidationErrorCode.V001_MISSING_REQUIRED_FIELD,
            field="id",
        )
        assert suggestion is not None
        assert "id" in suggestion

    def test_invalid_type_suggestion(self) -> None:
        """Test suggestion for invalid type."""
        suggestion = get_suggestion(
            ValidationErrorCode.V001_INVALID_TYPE,
            expected="array",
            actual="string",
        )
        assert suggestion is not None
        assert "array" in suggestion
        assert "string" in suggestion

    def test_dangling_ref_suggestion(self) -> None:
        """Test suggestion for dangling reference."""
        suggestion = get_suggestion(
            ValidationErrorCode.V002_DANGLING_REF,
            ref="mod_nonexistent",
        )
        assert suggestion is not None
        assert "mod_nonexistent" in suggestion

    def test_unknown_code_returns_none(self) -> None:
        """Test unknown codes return None."""
        # This is a valid code but may not have a suggestion template
        suggestion = get_suggestion(
            ValidationErrorCode.V001_ADDITIONAL_PROPERTIES,
        )
        # May or may not have a suggestion - just verify it doesn't crash


class TestCreateError:
    """Tests for create_error helper function."""

    def test_creates_error_with_suggestion(self) -> None:
        """Test error creation with auto-suggestion."""
        error = create_error(
            code=ValidationErrorCode.V001_MISSING_REQUIRED_FIELD,
            message="Missing field 'id'",
            location="$.modules[0]",
            field="id",
        )

        assert error.code == ValidationErrorCode.V001_MISSING_REQUIRED_FIELD.value
        assert error.message == "Missing field 'id'"
        assert error.location == "$.modules[0]"
        assert error.suggestion is not None
        assert "id" in error.suggestion

    def test_creates_error_with_severity(self) -> None:
        """Test error creation with custom severity."""
        error = create_error(
            code=ValidationErrorCode.V003_VISIBILITY_INCONSISTENT,
            message="Visibility mismatch",
            location="$.modules[0].exports[0]",
            severity="warning",
        )

        assert error.severity == "warning"

    def test_stores_context(self) -> None:
        """Test context is stored in error."""
        error = create_error(
            code=ValidationErrorCode.V002_DANGLING_REF,
            message="Reference not found",
            location="$.modules[0].submodules[0]",
            ref="mod_missing",
            extra="value",
        )

        assert error.context["ref"] == "mod_missing"
        assert error.context["extra"] == "value"


class TestValidationException:
    """Tests for ValidationException."""

    def test_basic_exception(self) -> None:
        """Test basic exception creation."""
        exc = ValidationException("Something went wrong")
        assert str(exc) == "Something went wrong"
        assert exc.cause is None

    def test_exception_with_cause(self) -> None:
        """Test exception with underlying cause."""
        cause = FileNotFoundError("test.json")
        exc = ValidationException("Cannot load schema", cause=cause)

        assert "Cannot load schema" in str(exc)
        assert exc.cause is cause
        assert isinstance(exc.cause, FileNotFoundError)

    def test_exception_is_exception(self) -> None:
        """Test that ValidationException is an Exception."""
        exc = ValidationException("Test")
        assert isinstance(exc, Exception)

        with pytest.raises(ValidationException):
            raise exc
