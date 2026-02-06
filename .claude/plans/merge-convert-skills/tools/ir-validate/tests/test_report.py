"""Tests for report generation."""

import json
import pytest

from ir_validate.errors import ValidationError
from ir_validate.report import (
    ReportFormatter,
    ValidationReport,
    ValidationSummary,
    format_report,
)


class TestValidationSummary:
    """Tests for ValidationSummary."""

    def test_from_empty_errors(self) -> None:
        """Test summary from empty error list."""
        summary = ValidationSummary.from_errors([])

        assert summary.total_errors == 0
        assert summary.total_warnings == 0
        assert summary.total_info == 0
        assert summary.passed is True
        assert summary.errors_by_category == {}

    def test_from_errors_with_errors(self) -> None:
        """Test summary from errors list."""
        errors = [
            ValidationError(code="V001-001", message="Error 1", location="$", severity="error"),
            ValidationError(code="V001-002", message="Error 2", location="$", severity="error"),
            ValidationError(code="V002-001", message="Warning 1", location="$", severity="warning"),
            ValidationError(code="V003-001", message="Info 1", location="$", severity="info"),
        ]

        summary = ValidationSummary.from_errors(errors)

        assert summary.total_errors == 2
        assert summary.total_warnings == 1
        assert summary.total_info == 1
        assert summary.passed is False
        assert summary.errors_by_category["V001"] == 2
        assert summary.errors_by_category["V002"] == 1
        assert summary.errors_by_category["V003"] == 1

    def test_only_warnings_still_passes(self) -> None:
        """Test that only warnings still counts as passed."""
        errors = [
            ValidationError(code="V002-001", message="Warning", location="$", severity="warning"),
        ]

        summary = ValidationSummary.from_errors(errors)
        assert summary.passed is True


class TestValidationReport:
    """Tests for ValidationReport."""

    def test_create_report(self) -> None:
        """Test report creation."""
        errors = [
            ValidationError(code="V001-001", message="Error", location="$", severity="error"),
        ]

        report = ValidationReport.create(
            errors=errors,
            file_path="/path/to/file.ir.yaml",
            schema_version="v1",
        )

        assert report.file_path == "/path/to/file.ir.yaml"
        assert report.schema_version == "v1"
        assert report.timestamp is not None
        assert len(report.errors) == 1
        assert report.summary.total_errors == 1

    def test_create_with_metadata(self) -> None:
        """Test report creation with extra metadata."""
        report = ValidationReport.create(
            errors=[],
            file_path=None,
            schema_version="v1",
            strict_mode="true",
            validator_version="1.0.0",
        )

        assert report.metadata["strict_mode"] == "true"
        assert report.metadata["validator_version"] == "1.0.0"


class TestReportFormatter:
    """Tests for ReportFormatter."""

    def test_format_human_passed(self) -> None:
        """Test human format for passed validation."""
        report = ValidationReport.create(errors=[], file_path="test.yaml")
        formatter = ReportFormatter(use_color=False)

        output = formatter.format_human(report)

        assert "IR Validation Report" in output
        assert "PASSED" in output
        assert "Errors: 0" in output

    def test_format_human_failed(self) -> None:
        """Test human format for failed validation."""
        errors = [
            ValidationError(
                code="V001-001",
                message="Missing field",
                location="$.modules[0]",
                severity="error",
                suggestion="Add the field",
            ),
        ]
        report = ValidationReport.create(errors=errors, file_path="test.yaml")
        formatter = ReportFormatter(use_color=False)

        output = formatter.format_human(report)

        assert "FAILED" in output
        assert "V001-001" in output
        assert "Missing field" in output
        assert "$.modules[0]" in output
        assert "Add the field" in output

    def test_format_human_with_color(self) -> None:
        """Test human format with ANSI colors."""
        errors = [
            ValidationError(code="V001-001", message="Error", location="$", severity="error"),
        ]
        report = ValidationReport.create(errors=errors)
        formatter = ReportFormatter(use_color=True)

        output = formatter.format_human(report)

        # Should contain ANSI escape codes
        assert "\033[" in output

    def test_format_json(self) -> None:
        """Test JSON format output."""
        errors = [
            ValidationError(code="V001-001", message="Error", location="$", severity="error"),
        ]
        report = ValidationReport.create(
            errors=errors,
            file_path="test.yaml",
            schema_version="v1",
        )
        formatter = ReportFormatter()

        output = formatter.format_json(report)
        parsed = json.loads(output)

        assert parsed["file_path"] == "test.yaml"
        assert parsed["schema_version"] == "v1"
        assert parsed["summary"]["passed"] is False
        assert len(parsed["errors"]) == 1
        assert parsed["errors"][0]["code"] == "V001-001"

    def test_format_compact(self) -> None:
        """Test compact format output."""
        errors = [
            ValidationError(code="V001-001", message="Error 1", location="$.a", severity="error"),
            ValidationError(code="V002-001", message="Error 2", location="$.b", severity="error"),
        ]
        report = ValidationReport.create(errors=errors, file_path="test.yaml")
        formatter = ReportFormatter()

        output = formatter.format_compact(report)
        lines = output.strip().split("\n")

        # Should have one line per error plus summary
        assert len(lines) == 3  # 2 errors + 1 summary

        # Each error line should follow format
        assert "test.yaml:$.a:error:V001-001:Error 1" in lines[0]
        assert "test.yaml:$.b:error:V002-001:Error 2" in lines[1]

        # Summary line
        assert lines[2].startswith("#")
        assert "FAIL" in lines[2]


class TestFormatReport:
    """Tests for format_report convenience function."""

    def test_format_report_human(self) -> None:
        """Test format_report with human format."""
        report = ValidationReport.create(errors=[], file_path="test.yaml")
        output = format_report(report, output_format="human", use_color=False)

        assert "IR Validation Report" in output

    def test_format_report_json(self) -> None:
        """Test format_report with JSON format."""
        report = ValidationReport.create(errors=[], file_path="test.yaml")
        output = format_report(report, output_format="json")

        parsed = json.loads(output)
        assert parsed["summary"]["passed"] is True

    def test_format_report_compact(self) -> None:
        """Test format_report with compact format."""
        report = ValidationReport.create(errors=[], file_path="test.yaml")
        output = format_report(report, output_format="compact")

        assert "# PASS" in output
