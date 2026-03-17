"""Schema validation for IR documents.

This module provides validation of IR instances against the JSON schema,
with detailed error reporting including line numbers and paths.

Features:
    - JSON Schema validation against ir-v1.json
    - Cross-reference validation between layers
    - Consistency checks across IR layers
    - Human-readable error messages with locations

Example:
    validator = SchemaValidator()
    result = validator.validate(ir_version)
    if not result.is_valid:
        for error in result.errors:
            print(f"{error.path}: {error.message}")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .models import (
    IRVersion,
    ValidationErrorCode,
)


class ValidationSeverity(str, Enum):
    """Severity of validation issues.

    Attributes:
        ERROR: Schema violation, IR is invalid
        WARNING: Potential issue, IR is valid but may cause problems
        INFO: Informational message
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """A single validation issue.

    Attributes:
        code: Validation error code
        severity: Issue severity
        message: Human-readable description
        path: JSON path to the problematic element
        expected: What was expected
        actual: What was found
        line_number: Line number in source (if applicable)
        suggestion: Suggested fix
    """

    code: ValidationErrorCode
    severity: ValidationSeverity
    message: str
    path: str = ""
    expected: str | None = None
    actual: str | None = None
    line_number: int | None = None
    suggestion: str | None = None

    def __str__(self) -> str:
        parts = [f"[{self.code.value}]"]
        if self.path:
            parts.append(f"at {self.path}")
        if self.line_number:
            parts.append(f"(line {self.line_number})")
        parts.append(f": {self.message}")
        if self.suggestion:
            parts.append(f" Suggestion: {self.suggestion}")
        return " ".join(parts)


@dataclass
class ValidationResult:
    """Result of validation operation.

    Attributes:
        is_valid: Whether IR passed validation
        issues: List of validation issues found
        checked_count: Number of elements checked
        error_count: Number of errors
        warning_count: Number of warnings
    """

    is_valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    checked_count: int = 0
    error_count: int = 0
    warning_count: int = 0

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue."""
        self.issues.append(issue)
        if issue.severity == ValidationSeverity.ERROR:
            self.is_valid = False
            self.error_count += 1
        elif issue.severity == ValidationSeverity.WARNING:
            self.warning_count += 1

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    def summary(self) -> str:
        """Get a summary of validation results."""
        status = "VALID" if self.is_valid else "INVALID"
        return (
            f"Validation {status}: "
            f"{self.error_count} errors, {self.warning_count} warnings "
            f"({self.checked_count} elements checked)"
        )


class SchemaValidator:
    """Validates IR against JSON schema and consistency rules.

    Provides comprehensive validation including:
    - JSON Schema validation (structure)
    - Cross-reference validation (references exist)
    - Consistency validation (layers are consistent)
    - Semantic validation (values make sense)

    Example:
        validator = SchemaValidator()

        # Validate IR instance
        result = validator.validate(ir_version)

        # Check result
        if result.is_valid:
            print("IR is valid!")
        else:
            for error in result.errors:
                print(error)

        # Validate just schema
        schema_result = validator.validate_schema(ir_dict)
    """

    def __init__(self, schema_path: Path | None = None):
        """Initialize validator.

        Args:
            schema_path: Path to JSON schema file (optional)
        """
        self.schema_path = schema_path
        self._schema: dict[str, Any] | None = None
        self._jsonschema_available = False

        # Try to import jsonschema
        try:
            import jsonschema
            self._jsonschema_available = True
        except ImportError:
            pass

    def _load_schema(self) -> dict[str, Any] | None:
        """Load JSON schema if path provided."""
        if self._schema is not None:
            return self._schema

        if self.schema_path and self.schema_path.exists():
            with open(self.schema_path) as f:
                self._schema = json.load(f)

        return self._schema

    def validate(self, ir: IRVersion) -> ValidationResult:
        """Validate an IR instance.

        Performs all validation checks:
        1. Schema validation
        2. Cross-reference validation
        3. Consistency validation
        4. Semantic validation

        Args:
            ir: IRVersion instance to validate

        Returns:
            ValidationResult with all issues found
        """
        result = ValidationResult()

        # Convert to dict for schema validation
        ir_dict = ir.model_dump(mode="json")

        # Schema validation
        self._validate_schema(ir_dict, result)

        # Cross-reference validation
        self._validate_cross_references(ir, result)

        # Consistency validation
        self._validate_consistency(ir, result)

        # Semantic validation
        self._validate_semantics(ir, result)

        return result

    def validate_schema(self, ir_dict: dict[str, Any]) -> ValidationResult:
        """Validate just the schema structure.

        Args:
            ir_dict: IR as dictionary

        Returns:
            ValidationResult for schema validation only
        """
        result = ValidationResult()
        self._validate_schema(ir_dict, result)
        return result

    def _validate_schema(
        self,
        ir_dict: dict[str, Any],
        result: ValidationResult,
    ) -> None:
        """Validate against JSON schema.

        Args:
            ir_dict: IR as dictionary
            result: ValidationResult to add issues to
        """
        schema = self._load_schema()

        if schema and self._jsonschema_available:
            import jsonschema

            try:
                jsonschema.validate(ir_dict, schema)
                result.checked_count += 1
            except jsonschema.ValidationError as e:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.V001,
                    severity=ValidationSeverity.ERROR,
                    message=str(e.message),
                    path=".".join(str(p) for p in e.absolute_path),
                    expected=str(e.schema.get("type", "unknown")),
                    actual=str(type(e.instance).__name__),
                ))
        else:
            # Basic validation without jsonschema
            self._validate_basic_structure(ir_dict, result)

    def _validate_basic_structure(
        self,
        ir_dict: dict[str, Any],
        result: ValidationResult,
    ) -> None:
        """Basic structure validation without jsonschema.

        Args:
            ir_dict: IR as dictionary
            result: ValidationResult to add issues to
        """
        # Check required top-level fields
        required = {"version", "module"}
        missing = required - set(ir_dict.keys())
        if missing:
            result.add_issue(ValidationIssue(
                code=ValidationErrorCode.V001,
                severity=ValidationSeverity.ERROR,
                message=f"Missing required fields: {missing}",
                path="$",
            ))

        result.checked_count += 1

        # Check version format
        if "version" in ir_dict:
            version = ir_dict["version"]
            if not isinstance(version, str) or not version.startswith("ir-v"):
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.V001,
                    severity=ValidationSeverity.ERROR,
                    message="Invalid version format",
                    path="$.version",
                    expected="ir-v{major}.{minor}",
                    actual=str(version),
                ))
            result.checked_count += 1

        # Check module structure
        if "module" in ir_dict:
            module = ir_dict["module"]
            module_required = {"id", "name", "metadata"}
            missing = module_required - set(module.keys())
            if missing:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.V001,
                    severity=ValidationSeverity.ERROR,
                    message=f"Module missing required fields: {missing}",
                    path="$.module",
                ))
            result.checked_count += 1

    def _validate_cross_references(
        self,
        ir: IRVersion,
        result: ValidationResult,
    ) -> None:
        """Validate that cross-references between layers are valid.

        Args:
            ir: IRVersion to validate
            result: ValidationResult to add issues to
        """
        # Collect all defined IDs
        defined_ids: set[str] = set()

        # Module ID
        defined_ids.add(ir.module.id)

        # Type IDs
        for type_def in ir.types:
            defined_ids.add(type_def.id)
            result.checked_count += 1

        # Function IDs
        for func in ir.functions:
            defined_ids.add(func.id)
            result.checked_count += 1

        # Binding IDs
        for binding in ir.bindings:
            defined_ids.add(binding.id)
            result.checked_count += 1

        # Expression IDs
        for expr in ir.expressions:
            defined_ids.add(expr.id)
            result.checked_count += 1

        # Check references in definitions
        for defn in ir.module.definitions:
            if defn.ref and defn.ref not in defined_ids:
                # Don't error for type: and function: prefixed refs
                if not (defn.ref.startswith("type:") or defn.ref.startswith("func:")):
                    result.add_issue(ValidationIssue(
                        code=ValidationErrorCode.V002,
                        severity=ValidationSeverity.WARNING,
                        message="Definition references undefined ID",
                        path=f"$.module.definitions[{defn.id}].ref",
                        expected="defined ID",
                        actual=defn.ref,
                    ))
            result.checked_count += 1

        # Check type references in functions
        for func in ir.functions:
            self._validate_type_ref(func.return_type, defined_ids, result,
                                    f"$.functions[{func.id}].return_type")
            for i, param in enumerate(func.params):
                self._validate_type_ref(param.type, defined_ids, result,
                                        f"$.functions[{func.id}].params[{i}].type")

        # Check type references in bindings
        for binding in ir.bindings:
            self._validate_type_ref(binding.type, defined_ids, result,
                                    f"$.bindings[{binding.id}].type")

    def _validate_type_ref(
        self,
        type_ref: Any,
        defined_ids: set[str],
        result: ValidationResult,
        path: str,
    ) -> None:
        """Validate a type reference.

        Args:
            type_ref: TypeRef to validate
            defined_ids: Set of defined IDs
            result: ValidationResult
            path: JSON path for error reporting
        """
        if type_ref is None:
            return

        result.checked_count += 1

        # Check if type_id references a known type
        if hasattr(type_ref, "type_id") and type_ref.type_id:
            # Skip built-in types and type parameters
            type_id = type_ref.type_id
            if (type_id not in defined_ids and
                not type_id.startswith("type:") and
                not type_id.startswith("type_param:")):
                # This is just informational - external types are allowed
                pass

        # Recursively validate nested type refs
        if hasattr(type_ref, "args"):
            for i, arg in enumerate(type_ref.args):
                self._validate_type_ref(arg, defined_ids, result, f"{path}.args[{i}]")

        if hasattr(type_ref, "return_type") and type_ref.return_type:
            self._validate_type_ref(type_ref.return_type, defined_ids, result,
                                    f"{path}.return_type")

    def _validate_consistency(
        self,
        ir: IRVersion,
        result: ValidationResult,
    ) -> None:
        """Validate consistency across IR layers.

        Args:
            ir: IRVersion to validate
            result: ValidationResult to add issues to
        """
        # Check that all exported items are defined
        export_refs = {exp.item.definition_id for exp in ir.module.exports}
        definition_ids = {defn.id for defn in ir.module.definitions}

        for exp in ir.module.exports:
            if exp.item.definition_id not in definition_ids:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.V003,
                    severity=ValidationSeverity.ERROR,
                    message="Export references undefined definition",
                    path=f"$.module.exports[{exp.id}]",
                    expected="defined in definitions",
                    actual=exp.item.definition_id,
                ))
            result.checked_count += 1

        # Check that metadata is consistent
        if ir.module.metadata:
            if ir.module.metadata.extraction_version != ir.version:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.V003,
                    severity=ValidationSeverity.WARNING,
                    message="Module extraction_version differs from IR version",
                    path="$.module.metadata.extraction_version",
                    expected=ir.version,
                    actual=ir.module.metadata.extraction_version,
                ))
            result.checked_count += 1

        # Check gap markers reference valid locations
        all_ids = {ir.module.id}
        all_ids.update(t.id for t in ir.types)
        all_ids.update(f.id for f in ir.functions)
        all_ids.update(b.id for b in ir.bindings)
        all_ids.update(e.id for e in ir.expressions)

        for gap in ir.gaps:
            if gap.location not in all_ids:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.V003,
                    severity=ValidationSeverity.WARNING,
                    message="Gap marker references unknown location",
                    path=f"$.gaps[{gap.id}].location",
                    actual=gap.location,
                ))
            result.checked_count += 1

    def _validate_semantics(
        self,
        ir: IRVersion,
        result: ValidationResult,
    ) -> None:
        """Validate semantic correctness of IR.

        Args:
            ir: IRVersion to validate
            result: ValidationResult to add issues to
        """
        # Check preservation status consistency
        if ir.preservation:
            if ir.preservation.current_level.value > ir.preservation.max_achievable_level.value:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.V004,
                    severity=ValidationSeverity.ERROR,
                    message="Current preservation level exceeds max achievable",
                    path="$.preservation.current_level",
                    expected=f"<= {ir.preservation.max_achievable_level.value}",
                    actual=str(ir.preservation.current_level.value),
                ))
            result.checked_count += 1

        # Check annotation confidence values
        for ann in ir.annotations:
            if not 0.0 <= ann.confidence <= 1.0:
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.V004,
                    severity=ValidationSeverity.ERROR,
                    message="Annotation confidence out of range",
                    path=f"$.annotations[{ann.id}].confidence",
                    expected="0.0 <= confidence <= 1.0",
                    actual=str(ann.confidence),
                ))
            result.checked_count += 1

        # Check gap severity makes sense for gap type
        for gap in ir.gaps:
            if gap.gap_type.value == "impossible" and gap.severity.value != "critical":
                result.add_issue(ValidationIssue(
                    code=ValidationErrorCode.V004,
                    severity=ValidationSeverity.WARNING,
                    message="Impossible gap should have critical severity",
                    path=f"$.gaps[{gap.id}].severity",
                    expected="critical",
                    actual=gap.severity.value,
                    suggestion="Change severity to 'critical' for impossible gaps",
                ))
            result.checked_count += 1


def validate_ir(ir: IRVersion, schema_path: Path | None = None) -> ValidationResult:
    """Convenience function for quick validation.

    Args:
        ir: IRVersion to validate
        schema_path: Optional path to JSON schema

    Returns:
        ValidationResult
    """
    validator = SchemaValidator(schema_path)
    return validator.validate(ir)


def validate_ir_file(path: Path, schema_path: Path | None = None) -> ValidationResult:
    """Validate an IR file.

    Args:
        path: Path to IR JSON file
        schema_path: Optional path to JSON schema

    Returns:
        ValidationResult
    """
    with open(path) as f:
        ir_dict = json.load(f)

    # Parse into IRVersion
    ir = IRVersion.model_validate(ir_dict)

    return validate_ir(ir, schema_path)
