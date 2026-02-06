"""Tests for the RoundTripReport class.

Tests cover:
- Human-readable report generation
- JSON report generation
- Markdown report generation
- Compact report generation
- Summary statistics
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from ir_roundtrip.validator import (
    RoundTripResult,
    PreservationLevel,
    ValidationStatus,
)
from ir_roundtrip.comparison import CompareResult, ASTDifference, DifferenceKind
from ir_roundtrip.report import (
    RoundTripReport,
    ReportFormat,
    ReportSummary,
)


class TestReportSummary:
    """Tests for ReportSummary class."""

    def test_empty_results(self) -> None:
        """Test summary for empty results."""
        summary = ReportSummary.from_results([])

        assert summary.total == 0
        assert summary.passed == 0
        assert summary.pass_rate == 0.0

    def test_all_passed(self) -> None:
        """Test summary when all pass."""
        results = [
            RoundTripResult(
                status=ValidationStatus.PASSED,
                level=PreservationLevel.L3_SEMANTIC,
                source="",
                duration_ms=10.0,
            )
            for _ in range(5)
        ]
        summary = ReportSummary.from_results(results)

        assert summary.total == 5
        assert summary.passed == 5
        assert summary.failed == 0
        assert summary.pass_rate == 100.0

    def test_mixed_results(self) -> None:
        """Test summary with mixed results."""
        results = [
            RoundTripResult(
                status=ValidationStatus.PASSED,
                level=PreservationLevel.L3_SEMANTIC,
                source="",
                duration_ms=10.0,
            ),
            RoundTripResult(
                status=ValidationStatus.FAILED,
                level=PreservationLevel.L3_SEMANTIC,
                source="",
                duration_ms=20.0,
            ),
            RoundTripResult(
                status=ValidationStatus.ERROR,
                level=PreservationLevel.L3_SEMANTIC,
                source="",
                duration_ms=5.0,
            ),
            RoundTripResult(
                status=ValidationStatus.SKIPPED,
                level=PreservationLevel.L3_SEMANTIC,
                source="",
                duration_ms=0.0,
            ),
        ]
        summary = ReportSummary.from_results(results)

        assert summary.total == 4
        assert summary.passed == 1
        assert summary.failed == 1
        assert summary.errors == 1
        assert summary.skipped == 1
        assert summary.pass_rate == 25.0
        assert summary.duration_ms == 35.0


class TestRoundTripReport:
    """Tests for RoundTripReport class."""

    @pytest.fixture
    def sample_results(self) -> list[RoundTripResult]:
        """Create sample results for testing."""
        return [
            RoundTripResult(
                status=ValidationStatus.PASSED,
                level=PreservationLevel.L3_SEMANTIC,
                source="def add(a, b): return a + b",
                target="def add(a, b): return a + b",
                duration_ms=15.5,
            ),
            RoundTripResult(
                status=ValidationStatus.FAILED,
                level=PreservationLevel.L1_SYNTACTIC,
                source="def foo(): pass",
                target="def foo():\n    pass",
                failure_reason="Whitespace difference",
                duration_ms=8.2,
                comparison=CompareResult(
                    equivalent=False,
                    level="L1_SYNTACTIC",
                    ast_differences=[
                        ASTDifference(
                            kind=DifferenceKind.AST_STRUCTURE,
                            location="root",
                            description="Different formatting",
                        )
                    ],
                ),
            ),
        ]


class TestHumanFormat:
    """Tests for human-readable report format."""

    def test_basic_human_format(self, sample_results: list[RoundTripResult]) -> None:
        """Test basic human-readable output."""
        report = RoundTripReport()
        output = report.generate(sample_results, ReportFormat.HUMAN, use_color=False)

        assert "Round-Trip Validation Report" in output
        assert "Summary" in output
        assert "Total:" in output
        assert "Passed:" in output
        assert "Results" in output

    def test_human_format_with_color(
        self, sample_results: list[RoundTripResult]
    ) -> None:
        """Test human-readable output with color codes."""
        report = RoundTripReport()
        output = report.generate(sample_results, ReportFormat.HUMAN, use_color=True)

        # Should contain ANSI escape codes
        assert "\033[" in output

    def test_human_format_shows_failures(
        self, sample_results: list[RoundTripResult]
    ) -> None:
        """Test that failures are shown in human format."""
        report = RoundTripReport()
        output = report.generate(sample_results, ReportFormat.HUMAN, use_color=False)

        assert "FAIL" in output
        assert "Whitespace difference" in output


class TestJSONFormat:
    """Tests for JSON report format."""

    def test_json_format_valid(self, sample_results: list[RoundTripResult]) -> None:
        """Test that JSON output is valid."""
        report = RoundTripReport()
        output = report.generate(sample_results, ReportFormat.JSON)

        # Should be valid JSON
        data = json.loads(output)
        assert "title" in data
        assert "summary" in data
        assert "results" in data

    def test_json_format_structure(
        self, sample_results: list[RoundTripResult]
    ) -> None:
        """Test JSON structure."""
        report = RoundTripReport()
        data = report.generate_json(sample_results)

        assert data["summary"]["total"] == 2
        assert data["summary"]["passed"] == 1
        assert data["summary"]["failed"] == 1
        assert len(data["results"]) == 2

    def test_json_result_fields(self, sample_results: list[RoundTripResult]) -> None:
        """Test fields in JSON result entries."""
        report = RoundTripReport()
        data = report.generate_json(sample_results)

        result = data["results"][0]
        assert "status" in result
        assert "level" in result
        assert "duration_ms" in result
        assert "source_hash" in result

    def test_json_comparison_included(
        self, sample_results: list[RoundTripResult]
    ) -> None:
        """Test that comparison details are in JSON."""
        report = RoundTripReport()
        data = report.generate_json(sample_results)

        # Second result has comparison data
        result = data["results"][1]
        assert "comparison" in result
        assert result["comparison"]["equivalent"] is False


class TestMarkdownFormat:
    """Tests for Markdown report format."""

    def test_markdown_format_headers(
        self, sample_results: list[RoundTripResult]
    ) -> None:
        """Test Markdown headers."""
        report = RoundTripReport()
        output = report.generate(sample_results, ReportFormat.MARKDOWN)

        assert "# " in output  # H1 header
        assert "## Summary" in output
        assert "## Results" in output

    def test_markdown_format_table(
        self, sample_results: list[RoundTripResult]
    ) -> None:
        """Test Markdown table formatting."""
        report = RoundTripReport()
        output = report.generate(sample_results, ReportFormat.MARKDOWN)

        # Should have table structure
        assert "|" in output
        assert "---" in output

    def test_markdown_format_failure_details(
        self, sample_results: list[RoundTripResult]
    ) -> None:
        """Test that failures have detail sections."""
        report = RoundTripReport()
        output = report.generate(sample_results, ReportFormat.MARKDOWN)

        assert "## Failure Details" in output or "Failure" in output


class TestCompactFormat:
    """Tests for compact report format."""

    def test_compact_format_one_line_per_result(
        self, sample_results: list[RoundTripResult]
    ) -> None:
        """Test compact format has one line per result."""
        report = RoundTripReport()
        output = report.generate(sample_results, ReportFormat.COMPACT)

        lines = [l for l in output.strip().split("\n") if l]
        # 2 results + 1 empty line + 1 summary line = at least 3 non-empty lines
        assert len(lines) >= 3

    def test_compact_format_summary_line(
        self, sample_results: list[RoundTripResult]
    ) -> None:
        """Test compact format has summary line."""
        report = RoundTripReport()
        output = report.generate(sample_results, ReportFormat.COMPACT)

        assert "Total:" in output
        assert "Passed:" in output


class TestEmptyResults:
    """Tests for reports with empty results."""

    def test_human_format_empty(self) -> None:
        """Test human format with no results."""
        report = RoundTripReport()
        output = report.generate([], ReportFormat.HUMAN)

        assert "Total:   0" in output
        assert "Pass Rate: 0.0%" in output

    def test_json_format_empty(self) -> None:
        """Test JSON format with no results."""
        report = RoundTripReport()
        data = report.generate_json([])

        assert data["summary"]["total"] == 0
        assert len(data["results"]) == 0

    def test_markdown_format_empty(self) -> None:
        """Test Markdown format with no results."""
        report = RoundTripReport()
        output = report.generate([], ReportFormat.MARKDOWN)

        assert "Total | 0" in output


class TestCustomTitle:
    """Tests for custom report titles."""

    def test_custom_title_in_human(self) -> None:
        """Test custom title in human format."""
        report = RoundTripReport(title="Custom Report Title")
        output = report.generate([], ReportFormat.HUMAN)

        assert "Custom Report Title" in output

    def test_custom_title_in_json(self) -> None:
        """Test custom title in JSON format."""
        report = RoundTripReport(title="Custom Report Title")
        data = report.generate_json([])

        assert data["title"] == "Custom Report Title"

    def test_custom_title_in_markdown(self) -> None:
        """Test custom title in Markdown format."""
        report = RoundTripReport(title="Custom Report Title")
        output = report.generate([], ReportFormat.MARKDOWN)

        assert "# Custom Report Title" in output


@pytest.fixture
def sample_results() -> list[RoundTripResult]:
    """Create sample results for testing."""
    return [
        RoundTripResult(
            status=ValidationStatus.PASSED,
            level=PreservationLevel.L3_SEMANTIC,
            source="def add(a, b): return a + b",
            target="def add(a, b): return a + b",
            duration_ms=15.5,
        ),
        RoundTripResult(
            status=ValidationStatus.FAILED,
            level=PreservationLevel.L1_SYNTACTIC,
            source="def foo(): pass",
            target="def foo():\n    pass",
            failure_reason="Whitespace difference",
            duration_ms=8.2,
            comparison=CompareResult(
                equivalent=False,
                level="L1_SYNTACTIC",
                ast_differences=[
                    ASTDifference(
                        kind=DifferenceKind.AST_STRUCTURE,
                        location="root",
                        description="Different formatting",
                    )
                ],
            ),
        ),
    ]
