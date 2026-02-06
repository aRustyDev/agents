"""Error taxonomy for IR validation.

This module defines the complete error taxonomy for IR validation,
organized by error category (V001-V004) with actionable error messages.

Error Categories:
- V001: Schema validation errors (structural/type mismatches)
- V002: Reference integrity errors (dangling/circular references)
- V003: Cross-layer consistency errors (layer mismatch, constraint violations)
- V004: Gap marker validity errors (invalid gap types, preservation levels)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class ValidationErrorCode(str, Enum):
    """Error codes organized by category.

    V001: Schema Validation
    V002: Reference Integrity
    V003: Cross-Layer Consistency
    V004: Gap Marker Validity
    """

    # V001: Schema validation errors
    V001_MISSING_REQUIRED_FIELD = "V001-001"
    V001_INVALID_TYPE = "V001-002"
    V001_INVALID_ENUM_VALUE = "V001-003"
    V001_PATTERN_MISMATCH = "V001-004"
    V001_INVALID_FORMAT = "V001-005"
    V001_ARRAY_ITEM_INVALID = "V001-006"
    V001_ADDITIONAL_PROPERTIES = "V001-007"
    V001_INVALID_VERSION = "V001-008"

    # V002: Reference integrity errors
    V002_DANGLING_REF = "V002-001"
    V002_CIRCULAR_REF = "V002-002"
    V002_INVALID_REF_FORMAT = "V002-003"
    V002_CROSS_FILE_REF_NOT_FOUND = "V002-004"
    V002_SELF_REF = "V002-005"
    V002_TYPE_MISMATCH_REF = "V002-006"

    # V003: Cross-layer consistency errors
    V003_LAYER_MISMATCH = "V003-001"
    V003_PARENT_CHILD_INCONSISTENT = "V003-002"
    V003_TYPE_DEFINITION_MISSING = "V003-003"
    V003_FUNCTION_SIGNATURE_MISMATCH = "V003-004"
    V003_BINDING_TYPE_MISMATCH = "V003-005"
    V003_EFFECT_PROPAGATION_VIOLATION = "V003-006"
    V003_SCOPE_VIOLATION = "V003-007"
    V003_VISIBILITY_INCONSISTENT = "V003-008"

    # V004: Gap marker validity errors
    V004_INVALID_GAP_TYPE = "V004-001"
    V004_INVALID_PRESERVATION_LEVEL = "V004-002"
    V004_GAP_LOCATION_NOT_FOUND = "V004-003"
    V004_INVALID_SEVERITY = "V004-004"
    V004_DECISION_POINT_NOT_FOUND = "V004-005"
    V004_ANNOTATION_TARGET_NOT_FOUND = "V004-006"
    V004_INVALID_ANNOTATION_KIND = "V004-007"
    V004_CONFIDENCE_OUT_OF_RANGE = "V004-008"


# Error code category to description mapping
ERROR_CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "V001": "Schema Validation Error",
    "V002": "Reference Integrity Error",
    "V003": "Cross-Layer Consistency Error",
    "V004": "Gap Marker Validity Error",
}


@dataclass
class ValidationError:
    """A validation error with structured information.

    Attributes:
        code: The error code (e.g., "V001-001").
        message: Human-readable error message.
        location: JSON path to the error location (e.g., "$.modules[0].definitions[2]").
        severity: Error severity level.
        suggestion: Optional actionable suggestion to fix the error.
        context: Additional context about the error.
    """

    code: str
    message: str
    location: str
    severity: Literal["error", "warning", "info"] = "error"
    suggestion: str | None = None
    context: dict[str, str] = field(default_factory=dict)

    @property
    def category(self) -> str:
        """Extract the error category (e.g., 'V001' from 'V001-001')."""
        return self.code.split("-")[0]

    @property
    def category_description(self) -> str:
        """Get the human-readable category description."""
        return ERROR_CATEGORY_DESCRIPTIONS.get(self.category, "Unknown Error Category")

    def __str__(self) -> str:
        """Format error as a readable string."""
        parts = [f"[{self.code}] {self.message}"]
        parts.append(f"  Location: {self.location}")
        if self.suggestion:
            parts.append(f"  Suggestion: {self.suggestion}")
        return "\n".join(parts)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "code": self.code,
            "message": self.message,
            "location": self.location,
            "severity": self.severity,
            "category": self.category,
            "category_description": self.category_description,
            "suggestion": self.suggestion,
            "context": self.context,
        }


# Suggestion templates for common errors
SUGGESTIONS: dict[str, str] = {
    ValidationErrorCode.V001_MISSING_REQUIRED_FIELD: "Add the required field '{field}' with an appropriate value.",
    ValidationErrorCode.V001_INVALID_TYPE: "Change the value type from '{actual}' to '{expected}'.",
    ValidationErrorCode.V001_INVALID_ENUM_VALUE: "Use one of the valid values: {valid_values}.",
    ValidationErrorCode.V001_PATTERN_MISMATCH: "Ensure the value matches the pattern: {pattern}.",
    ValidationErrorCode.V001_INVALID_FORMAT: "Format the value as a valid {format}.",
    ValidationErrorCode.V002_DANGLING_REF: "Either define the referenced item '{ref}' or remove the reference.",
    ValidationErrorCode.V002_CIRCULAR_REF: "Break the circular reference chain: {chain}.",
    ValidationErrorCode.V003_LAYER_MISMATCH: "Ensure {parent_layer} nodes contain {child_layer} nodes, not {actual}.",
    ValidationErrorCode.V003_TYPE_DEFINITION_MISSING: "Add a type definition for '{type_id}' in type_definitions.",
    ValidationErrorCode.V004_INVALID_PRESERVATION_LEVEL: "Use a preservation level between 0 and 3.",
    ValidationErrorCode.V004_GAP_LOCATION_NOT_FOUND: "Ensure the location '{location}' references an existing IR node.",
    ValidationErrorCode.V004_ANNOTATION_TARGET_NOT_FOUND: "Ensure the target '{target}' references an existing IR node.",
}


def get_suggestion(code: ValidationErrorCode, **kwargs: str) -> str | None:
    """Get a formatted suggestion for an error code.

    Args:
        code: The validation error code.
        **kwargs: Values to interpolate into the suggestion template.

    Returns:
        Formatted suggestion string, or None if no suggestion template exists.
    """
    template = SUGGESTIONS.get(code)
    if template is None:
        return None
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def create_error(
    code: ValidationErrorCode,
    message: str,
    location: str,
    severity: Literal["error", "warning", "info"] = "error",
    **context: str,
) -> ValidationError:
    """Create a validation error with automatic suggestion lookup.

    Args:
        code: The validation error code.
        message: Human-readable error message.
        location: JSON path to the error location.
        severity: Error severity level.
        **context: Additional context values for suggestion formatting.

    Returns:
        A configured ValidationError instance.
    """
    suggestion = get_suggestion(code, **context)
    return ValidationError(
        code=code.value,
        message=message,
        location=location,
        severity=severity,
        suggestion=suggestion,
        context=context,
    )


class ValidationException(Exception):
    """Exception raised when validation cannot proceed.

    This is distinct from validation errors found in the IR document.
    It represents issues with the validation process itself.
    """

    def __init__(self, message: str, cause: Exception | None = None):
        """Initialize the exception.

        Args:
            message: Description of what went wrong.
            cause: Optional underlying exception that caused this.
        """
        super().__init__(message)
        self.cause = cause
