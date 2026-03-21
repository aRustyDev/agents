"""Schema loading and validation for IR documents.

This module handles loading the ir-v1.json schema and performing
JSON Schema validation with custom validators for semantic rules.
"""

import json
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from jsonschema import Draft7Validator
    from jsonschema import ValidationError as JsonSchemaError
except ImportError:
    jsonschema = None  # type: ignore
    Draft7Validator = None  # type: ignore
    JsonSchemaError = Exception  # type: ignore

from .errors import (
    ValidationError,
    ValidationErrorCode,
    ValidationException,
    create_error,
)

# Default schema path relative to this file
DEFAULT_SCHEMA_PATH = Path(__file__).parent.parent.parent / "schemas" / "ir-v1.json"


@lru_cache(maxsize=4)
def load_schema(schema_path: Path | None = None) -> dict[str, Any]:
    """Load the IR schema from disk.

    Args:
        schema_path: Optional path to schema file. Defaults to ir-v1.json.

    Returns:
        Parsed JSON schema dictionary.

    Raises:
        ValidationException: If schema file cannot be loaded.
    """
    path = schema_path or DEFAULT_SCHEMA_PATH

    if not path.exists():
        raise ValidationException(f"Schema file not found: {path}")

    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationException(f"Invalid JSON in schema file: {path}", cause=e)
    except OSError as e:
        raise ValidationException(f"Cannot read schema file: {path}", cause=e)


def get_schema_version(schema: dict[str, Any]) -> str:
    """Extract the schema version from the loaded schema.

    Args:
        schema: Loaded schema dictionary.

    Returns:
        Schema version string (e.g., "v1").
    """
    schema_id = schema.get("$id", "")
    if "v1" in schema_id.lower():
        return "v1"
    return "unknown"


class SchemaValidator:
    """Validates IR data against the JSON schema with custom extensions.

    This validator performs:
    1. Standard JSON Schema Draft-07 validation
    2. Custom validation for ID patterns (mod_, fn:, type:, etc.)
    3. Version format validation
    """

    # ID prefix patterns by entity type
    ID_PATTERNS: dict[str, str] = {
        "module": "mod_",
        "import": "imp_",
        "export": "exp_",
        "definition": "def_",
        "function": "fn:",
        "type": "type:",
    }

    def __init__(self, schema_version: str = "v1"):
        """Initialize the schema validator.

        Args:
            schema_version: Schema version to use (currently only "v1" supported).

        Raises:
            ValidationException: If jsonschema is not installed.
        """
        if jsonschema is None:
            raise ValidationException(
                "jsonschema package is required for schema validation. "
                "Install with: pip install jsonschema"
            )

        self.schema_version = schema_version
        self.schema = load_schema()
        self._validator = Draft7Validator(self.schema)

    def validate(self, ir_data: dict[str, Any]) -> list[ValidationError]:
        """Validate IR data against the schema.

        Args:
            ir_data: The IR document to validate.

        Returns:
            List of validation errors found. Empty list if valid.
        """
        errors: list[ValidationError] = []

        # Standard JSON Schema validation
        errors.extend(self._validate_schema(ir_data))

        # Custom validations
        errors.extend(self._validate_version_format(ir_data))
        errors.extend(self._validate_id_patterns(ir_data))

        return errors

    def _validate_schema(self, ir_data: dict[str, Any]) -> Iterator[ValidationError]:
        """Perform standard JSON Schema validation.

        Args:
            ir_data: The IR document to validate.

        Yields:
            Validation errors from schema validation.
        """
        for error in self._validator.iter_errors(ir_data):
            yield self._convert_jsonschema_error(error)

    def _convert_jsonschema_error(self, error: JsonSchemaError) -> ValidationError:
        """Convert a jsonschema error to our ValidationError format.

        Args:
            error: The jsonschema validation error.

        Returns:
            Converted ValidationError.
        """
        # Build JSON path from path elements
        path_parts = ["$"]
        for elem in error.absolute_path:
            if isinstance(elem, int):
                path_parts.append(f"[{elem}]")
            else:
                path_parts.append(f".{elem}")
        location = "".join(path_parts)

        # Map error type to our error code
        code = self._map_error_type(error)

        # Build message with context
        message = self._build_error_message(error)

        # Get suggestion context
        context = self._extract_error_context(error)

        return create_error(
            code=code,
            message=message,
            location=location,
            severity="error",
            **context,
        )

    def _map_error_type(self, error: JsonSchemaError) -> ValidationErrorCode:
        """Map jsonschema error type to our error code.

        Args:
            error: The jsonschema validation error.

        Returns:
            Corresponding ValidationErrorCode.
        """
        validator = error.validator

        mapping = {
            "required": ValidationErrorCode.V001_MISSING_REQUIRED_FIELD,
            "type": ValidationErrorCode.V001_INVALID_TYPE,
            "enum": ValidationErrorCode.V001_INVALID_ENUM_VALUE,
            "pattern": ValidationErrorCode.V001_PATTERN_MISMATCH,
            "format": ValidationErrorCode.V001_INVALID_FORMAT,
            "items": ValidationErrorCode.V001_ARRAY_ITEM_INVALID,
            "additionalProperties": ValidationErrorCode.V001_ADDITIONAL_PROPERTIES,
        }

        return mapping.get(validator, ValidationErrorCode.V001_INVALID_TYPE)

    def _build_error_message(self, error: JsonSchemaError) -> str:
        """Build a human-readable error message.

        Args:
            error: The jsonschema validation error.

        Returns:
            Formatted error message.
        """
        validator = error.validator

        if validator == "required":
            missing = error.validator_value
            if isinstance(missing, list):
                missing = missing[0] if len(missing) == 1 else missing
            return f"Missing required field: {missing}"

        if validator == "type":
            expected = error.validator_value
            actual = type(error.instance).__name__
            return f"Expected type '{expected}', got '{actual}'"

        if validator == "enum":
            valid = error.validator_value
            actual = error.instance
            return f"Invalid value '{actual}'. Must be one of: {valid}"

        if validator == "pattern":
            pattern = error.validator_value
            actual = error.instance
            return f"Value '{actual}' does not match pattern: {pattern}"

        if validator == "format":
            fmt = error.validator_value
            return f"Value is not a valid {fmt}"

        # Default to jsonschema's message
        return str(error.message)

    def _extract_error_context(self, error: JsonSchemaError) -> dict[str, str]:
        """Extract context values for suggestion formatting.

        Args:
            error: The jsonschema validation error.

        Returns:
            Dictionary of context values.
        """
        context: dict[str, str] = {}

        if error.validator == "required":
            missing = error.validator_value
            if isinstance(missing, list) and missing:
                context["field"] = missing[0]
            else:
                context["field"] = str(missing)

        elif error.validator == "type":
            context["expected"] = str(error.validator_value)
            context["actual"] = type(error.instance).__name__

        elif error.validator == "enum":
            context["valid_values"] = ", ".join(str(v) for v in error.validator_value)

        elif error.validator == "pattern":
            context["pattern"] = str(error.validator_value)

        elif error.validator == "format":
            context["format"] = str(error.validator_value)

        return context

    def _validate_version_format(
        self, ir_data: dict[str, Any]
    ) -> Iterator[ValidationError]:
        """Validate the IR version format.

        Args:
            ir_data: The IR document to validate.

        Yields:
            Validation errors for invalid version format.
        """
        version = ir_data.get("version", "")
        if not version:
            return  # Missing version is caught by schema validation

        # Version should be ir-v{major}.{minor}
        import re

        pattern = r"^ir-v\d+\.\d+$"
        if not re.match(pattern, version):
            yield create_error(
                code=ValidationErrorCode.V001_INVALID_VERSION,
                message=f"Invalid version format: '{version}'. Expected format: ir-v{{major}}.{{minor}}",
                location="$.version",
                severity="error",
                pattern=pattern,
            )

    def _validate_id_patterns(
        self, ir_data: dict[str, Any]
    ) -> Iterator[ValidationError]:
        """Validate that IDs follow expected patterns.

        Args:
            ir_data: The IR document to validate.

        Yields:
            Validation errors for invalid ID patterns.
        """
        # Validate module IDs
        for i, module in enumerate(ir_data.get("modules", [])):
            mod_id = module.get("id", "")
            if mod_id and not mod_id.startswith("mod_"):
                yield create_error(
                    code=ValidationErrorCode.V001_PATTERN_MISMATCH,
                    message=f"Module ID '{mod_id}' should start with 'mod_'",
                    location=f"$.modules[{i}].id",
                    severity="warning",
                    pattern="mod_*",
                )

            # Validate import IDs
            for j, imp in enumerate(module.get("imports", [])):
                imp_id = imp.get("id", "")
                if imp_id and not imp_id.startswith("imp_"):
                    yield create_error(
                        code=ValidationErrorCode.V001_PATTERN_MISMATCH,
                        message=f"Import ID '{imp_id}' should start with 'imp_'",
                        location=f"$.modules[{i}].imports[{j}].id",
                        severity="warning",
                        pattern="imp_*",
                    )

            # Validate export IDs
            for j, exp in enumerate(module.get("exports", [])):
                exp_id = exp.get("id", "")
                if exp_id and not exp_id.startswith("exp_"):
                    yield create_error(
                        code=ValidationErrorCode.V001_PATTERN_MISMATCH,
                        message=f"Export ID '{exp_id}' should start with 'exp_'",
                        location=f"$.modules[{i}].exports[{j}].id",
                        severity="warning",
                        pattern="exp_*",
                    )

            # Validate definition IDs
            for j, defn in enumerate(module.get("definitions", [])):
                def_id = defn.get("id", "")
                if def_id and not def_id.startswith("def_"):
                    yield create_error(
                        code=ValidationErrorCode.V001_PATTERN_MISMATCH,
                        message=f"Definition ID '{def_id}' should start with 'def_'",
                        location=f"$.modules[{i}].definitions[{j}].id",
                        severity="warning",
                        pattern="def_*",
                    )

        # Validate type definition IDs
        for i, typedef in enumerate(ir_data.get("type_definitions", [])):
            type_id = typedef.get("id", "")
            if type_id and not type_id.startswith("type:"):
                yield create_error(
                    code=ValidationErrorCode.V001_PATTERN_MISMATCH,
                    message=f"Type definition ID '{type_id}' should start with 'type:'",
                    location=f"$.type_definitions[{i}].id",
                    severity="warning",
                    pattern="type:*",
                )


def validate_against_schema(
    ir_data: dict[str, Any], schema_version: str = "v1"
) -> list[ValidationError]:
    """Convenience function to validate IR data against schema.

    Args:
        ir_data: The IR document to validate.
        schema_version: Schema version to use.

    Returns:
        List of validation errors found.
    """
    validator = SchemaValidator(schema_version)
    return validator.validate(ir_data)
