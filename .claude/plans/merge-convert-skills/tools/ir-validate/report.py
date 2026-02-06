"""Validation report generation for IR documents.

This module provides human-readable and machine-readable
output formats for validation results.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from .errors import ValidationError


@dataclass
class ValidationSummary:
    """Summary statistics for a validation run.

    Attributes:
        total_errors: Total number of errors.
        total_warnings: Total number of warnings.
        total_info: Total number of informational messages.
        errors_by_category: Error counts grouped by category (V001-V004).
        passed: Whether validation passed (no errors).
    """

    total_errors: int = 0
    total_warnings: int = 0
    total_info: int = 0
    errors_by_category: dict[str, int] = field(default_factory=dict)
    passed: bool = True

    @classmethod
    def from_errors(cls, errors: list[ValidationError]) -> "ValidationSummary":
        """Create summary from a list of validation errors.

        Args:
            errors: List of validation errors.

        Returns:
            Summary statistics.
        """
        summary = cls()

        for error in errors:
            if error.severity == "error":
                summary.total_errors += 1
                summary.passed = False
            elif error.severity == "warning":
                summary.total_warnings += 1
            else:
                summary.total_info += 1

            category = error.category
            summary.errors_by_category[category] = (
                summary.errors_by_category.get(category, 0) + 1
            )

        return summary


@dataclass
class ValidationReport:
    """Complete validation report.

    Attributes:
        file_path: Path to the validated file.
        schema_version: Schema version used.
        timestamp: When validation was performed.
        summary: Summary statistics.
        errors: List of all validation errors.
        metadata: Additional metadata about the validation run.
    """

    file_path: str | None
    schema_version: str
    timestamp: str
    summary: ValidationSummary
    errors: list[ValidationError]
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        errors: list[ValidationError],
        file_path: str | None = None,
        schema_version: str = "v1",
        **metadata: str,
    ) -> "ValidationReport":
        """Create a validation report.

        Args:
            errors: List of validation errors.
            file_path: Path to the validated file.
            schema_version: Schema version used.
            **metadata: Additional metadata.

        Returns:
            Complete validation report.
        """
        return cls(
            file_path=file_path,
            schema_version=schema_version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            summary=ValidationSummary.from_errors(errors),
            errors=errors,
            metadata=metadata,
        )


class ReportFormatter:
    """Formats validation reports for different output types."""

    # ANSI color codes for terminal output
    COLORS = {
        "error": "\033[91m",  # Red
        "warning": "\033[93m",  # Yellow
        "info": "\033[94m",  # Blue
        "success": "\033[92m",  # Green
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
    }

    def __init__(self, use_color: bool = True):
        """Initialize the formatter.

        Args:
            use_color: Whether to use ANSI colors in output.
        """
        self.use_color = use_color

    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled.

        Args:
            text: Text to color.
            color: Color name.

        Returns:
            Colored text or original text.
        """
        if not self.use_color:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def format_human(self, report: ValidationReport) -> str:
        """Format report for human reading.

        Args:
            report: The validation report.

        Returns:
            Human-readable report string.
        """
        lines: list[str] = []

        # Header
        lines.append(self._color("=" * 60, "dim"))
        lines.append(self._color("IR Validation Report", "bold"))
        lines.append(self._color("=" * 60, "dim"))
        lines.append("")

        # File info
        if report.file_path:
            lines.append(f"File: {report.file_path}")
        lines.append(f"Schema: {report.schema_version}")
        lines.append(f"Timestamp: {report.timestamp}")
        lines.append("")

        # Summary
        summary = report.summary
        if summary.passed:
            status = self._color("PASSED", "success")
        else:
            status = self._color("FAILED", "error")

        lines.append(f"Status: {status}")
        lines.append(
            f"Errors: {self._color(str(summary.total_errors), 'error')}, "
            f"Warnings: {self._color(str(summary.total_warnings), 'warning')}, "
            f"Info: {self._color(str(summary.total_info), 'info')}"
        )

        if summary.errors_by_category:
            lines.append("")
            lines.append("By Category:")
            for category, count in sorted(summary.errors_by_category.items()):
                lines.append(f"  {category}: {count}")

        # Errors
        if report.errors:
            lines.append("")
            lines.append(self._color("-" * 60, "dim"))
            lines.append("Issues Found:")
            lines.append(self._color("-" * 60, "dim"))

            for error in report.errors:
                lines.append("")
                lines.append(self._format_error(error))

        lines.append("")
        lines.append(self._color("=" * 60, "dim"))

        return "\n".join(lines)

    def _format_error(self, error: ValidationError) -> str:
        """Format a single error for human reading.

        Args:
            error: The validation error.

        Returns:
            Formatted error string.
        """
        severity_color = {
            "error": "error",
            "warning": "warning",
            "info": "info",
        }.get(error.severity, "dim")

        lines = []

        # Error header
        header = f"[{error.code}] {error.severity.upper()}"
        lines.append(self._color(header, severity_color))

        # Message
        lines.append(f"  {error.message}")

        # Location
        lines.append(f"  Location: {self._color(error.location, 'dim')}")

        # Suggestion
        if error.suggestion:
            lines.append(f"  Suggestion: {error.suggestion}")

        return "\n".join(lines)

    def format_json(self, report: ValidationReport, indent: int = 2) -> str:
        """Format report as JSON.

        Args:
            report: The validation report.
            indent: JSON indentation level.

        Returns:
            JSON string.
        """
        data = {
            "file_path": report.file_path,
            "schema_version": report.schema_version,
            "timestamp": report.timestamp,
            "summary": {
                "passed": report.summary.passed,
                "total_errors": report.summary.total_errors,
                "total_warnings": report.summary.total_warnings,
                "total_info": report.summary.total_info,
                "errors_by_category": report.summary.errors_by_category,
            },
            "errors": [e.to_dict() for e in report.errors],
            "metadata": report.metadata,
        }
        return json.dumps(data, indent=indent)

    def format_compact(self, report: ValidationReport) -> str:
        """Format report in compact single-line-per-error format.

        Suitable for CI/grep processing.

        Args:
            report: The validation report.

        Returns:
            Compact report string.
        """
        lines: list[str] = []

        for error in report.errors:
            # Format: file:location:severity:code:message
            file_path = report.file_path or "<stdin>"
            line = f"{file_path}:{error.location}:{error.severity}:{error.code}:{error.message}"
            lines.append(line)

        # Summary line
        summary = report.summary
        status = "PASS" if summary.passed else "FAIL"
        lines.append(
            f"# {status}: {summary.total_errors} errors, "
            f"{summary.total_warnings} warnings, {summary.total_info} info"
        )

        return "\n".join(lines)


def format_report(
    report: ValidationReport,
    output_format: Literal["human", "json", "compact"] = "human",
    use_color: bool = True,
) -> str:
    """Format a validation report.

    Args:
        report: The validation report.
        output_format: Output format type.
        use_color: Whether to use ANSI colors (human format only).

    Returns:
        Formatted report string.
    """
    formatter = ReportFormatter(use_color=use_color)

    if output_format == "json":
        return formatter.format_json(report)
    elif output_format == "compact":
        return formatter.format_compact(report)
    else:
        return formatter.format_human(report)
