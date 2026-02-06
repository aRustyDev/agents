"""Main IR validation logic.

This module provides the primary IRValidator class that orchestrates
all validation checks: schema, references, and consistency.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

from .consistency import check_consistency
from .errors import ValidationError, ValidationException
from .references import check_reference_integrity
from .report import ValidationReport, format_report
from .schema import validate_against_schema


@dataclass
class ValidationResult:
    """Result of validating an IR document.

    Attributes:
        is_valid: Whether the document passed validation (no errors).
        errors: List of all validation errors.
        warnings: List of warnings (subset of errors with severity="warning").
        info: List of informational messages.
        report: Full validation report.
    """

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    report: ValidationReport | None = None

    @property
    def warnings(self) -> list[ValidationError]:
        """Get warnings only."""
        return [e for e in self.errors if e.severity == "warning"]

    @property
    def info_messages(self) -> list[ValidationError]:
        """Get informational messages only."""
        return [e for e in self.errors if e.severity == "info"]

    @property
    def error_count(self) -> int:
        """Count of actual errors (not warnings/info)."""
        return sum(1 for e in self.errors if e.severity == "error")

    @property
    def warning_count(self) -> int:
        """Count of warnings."""
        return len(self.warnings)

    def format(
        self,
        output_format: Literal["human", "json", "compact"] = "human",
        use_color: bool = True,
    ) -> str:
        """Format the validation result for output.

        Args:
            output_format: Output format type.
            use_color: Whether to use ANSI colors.

        Returns:
            Formatted output string.
        """
        if self.report is None:
            self.report = ValidationReport.create(self.errors)
        return format_report(self.report, output_format, use_color)


class IRValidator:
    """Validates IR documents against schema and semantic rules.

    This validator performs:
    1. Schema validation (ir-v1.json compliance)
    2. Reference integrity (dangling refs, circular refs)
    3. Cross-layer consistency (layer relationships)
    4. Gap marker validity (correct types, levels)

    Example:
        >>> validator = IRValidator()
        >>> result = validator.validate(ir_data)
        >>> if not result.is_valid:
        ...     print(result.format())
    """

    def __init__(
        self,
        schema_version: str = "v1",
        strict: bool = False,
        skip_schema: bool = False,
        skip_references: bool = False,
        skip_consistency: bool = False,
    ):
        """Initialize the validator.

        Args:
            schema_version: Schema version to validate against.
            strict: If True, treat warnings as errors.
            skip_schema: Skip JSON schema validation.
            skip_references: Skip reference integrity checks.
            skip_consistency: Skip cross-layer consistency checks.
        """
        self.schema_version = schema_version
        self.strict = strict
        self.skip_schema = skip_schema
        self.skip_references = skip_references
        self.skip_consistency = skip_consistency

    def validate(
        self,
        ir_data: dict[str, Any],
        file_path: str | None = None,
    ) -> ValidationResult:
        """Validate IR data against schema and semantic rules.

        Args:
            ir_data: The IR document to validate.
            file_path: Optional path to the source file (for reporting).

        Returns:
            ValidationResult with all errors found.
        """
        all_errors: list[ValidationError] = []

        # Phase 1: Schema validation
        if not self.skip_schema:
            try:
                schema_errors = validate_against_schema(ir_data, self.schema_version)
                all_errors.extend(schema_errors)
            except ValidationException as e:
                # Schema loading failed - create a single error
                all_errors.append(
                    ValidationError(
                        code="V001-000",
                        message=f"Schema validation failed: {e}",
                        location="$",
                        severity="error",
                    )
                )

        # Phase 2: Reference integrity
        if not self.skip_references:
            ref_errors = check_reference_integrity(ir_data)
            all_errors.extend(ref_errors)

        # Phase 3: Cross-layer consistency
        if not self.skip_consistency:
            consistency_errors = check_consistency(ir_data)
            all_errors.extend(consistency_errors)

        # Determine validity
        has_errors = any(e.severity == "error" for e in all_errors)
        has_warnings = any(e.severity == "warning" for e in all_errors)

        if self.strict:
            is_valid = not has_errors and not has_warnings
        else:
            is_valid = not has_errors

        # Create report
        report = ValidationReport.create(
            errors=all_errors,
            file_path=file_path,
            schema_version=self.schema_version,
            strict_mode=str(self.strict),
        )

        return ValidationResult(
            is_valid=is_valid,
            errors=all_errors,
            report=report,
        )

    def validate_file(self, file_path: Path | str) -> ValidationResult:
        """Validate an IR file (YAML or JSON).

        Args:
            file_path: Path to the IR file.

        Returns:
            ValidationResult with all errors found.

        Raises:
            ValidationException: If file cannot be read or parsed.
        """
        path = Path(file_path)

        if not path.exists():
            raise ValidationException(f"File not found: {path}")

        try:
            with open(path) as f:
                content = f.read()
        except OSError as e:
            raise ValidationException(f"Cannot read file: {path}", cause=e)

        # Parse based on extension
        try:
            if path.suffix.lower() in (".yaml", ".yml"):
                ir_data = yaml.safe_load(content)
            elif path.suffix.lower() == ".json":
                ir_data = json.loads(content)
            else:
                # Try YAML first (superset of JSON)
                try:
                    ir_data = yaml.safe_load(content)
                except yaml.YAMLError:
                    ir_data = json.loads(content)
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValidationException(f"Cannot parse file: {path}", cause=e)

        if not isinstance(ir_data, dict):
            raise ValidationException(f"IR document must be an object, got {type(ir_data).__name__}")

        return self.validate(ir_data, file_path=str(path))


def validate_ir(
    ir_data: dict[str, Any],
    schema_version: str = "v1",
    strict: bool = False,
) -> ValidationResult:
    """Convenience function to validate IR data.

    Args:
        ir_data: The IR document to validate.
        schema_version: Schema version to use.
        strict: Treat warnings as errors.

    Returns:
        ValidationResult with all errors found.
    """
    validator = IRValidator(schema_version=schema_version, strict=strict)
    return validator.validate(ir_data)
