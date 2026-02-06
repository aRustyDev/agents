"""Validation report generation.

This module provides report generation for round-trip validation results.
Reports can be generated in multiple formats:

- Human-readable (text with optional color)
- JSON (machine-readable)
- Markdown (for documentation)

Example:
    report = RoundTripReport()
    results = [validator.validate(source) for source in sources]

    # Human-readable output
    print(report.generate(results))

    # JSON for CI/CD
    json_data = report.generate_json(results)

    # Markdown for documentation
    md = report.generate_markdown(results)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .validator import RoundTripResult, ValidationStatus, PreservationLevel


class ReportFormat(str, Enum):
    """Output format for reports.

    Attributes:
        HUMAN: Human-readable text with optional ANSI colors
        JSON: Machine-readable JSON
        MARKDOWN: Markdown format for documentation
        COMPACT: One-line-per-result format
    """

    HUMAN = "human"
    JSON = "json"
    MARKDOWN = "markdown"
    COMPACT = "compact"


@dataclass
class ReportSummary:
    """Summary statistics for a validation report.

    Attributes:
        total: Total number of validations
        passed: Number that passed
        failed: Number that failed
        errors: Number that had errors
        skipped: Number that were skipped
        duration_ms: Total duration in milliseconds
        pass_rate: Percentage that passed
    """

    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration_ms: float = 0.0

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate as a percentage."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100

    @classmethod
    def from_results(cls, results: list[RoundTripResult]) -> ReportSummary:
        """Create summary from validation results."""
        summary = cls(total=len(results))

        for result in results:
            if result.status == ValidationStatus.PASSED:
                summary.passed += 1
            elif result.status == ValidationStatus.FAILED:
                summary.failed += 1
            elif result.status == ValidationStatus.ERROR:
                summary.errors += 1
            elif result.status == ValidationStatus.SKIPPED:
                summary.skipped += 1

            summary.duration_ms += result.duration_ms

        return summary


class RoundTripReport:
    """Generate reports for round-trip validation results.

    This class provides multiple output formats for validation results,
    suitable for different use cases:

    - Terminal output (with colors)
    - CI/CD pipeline consumption (JSON)
    - Documentation generation (Markdown)

    Example:
        report = RoundTripReport()

        # Generate human-readable report
        text = report.generate(results, use_color=True)
        print(text)

        # Generate JSON for CI
        data = report.generate_json(results)
        with open("report.json", "w") as f:
            json.dump(data, f)
    """

    # ANSI color codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "cyan": "\033[36m",
    }

    def __init__(self, title: str = "Round-Trip Validation Report") -> None:
        """Initialize the report generator.

        Args:
            title: Report title
        """
        self.title = title

    def generate(
        self,
        results: list[RoundTripResult],
        format: ReportFormat = ReportFormat.HUMAN,
        use_color: bool = True,
    ) -> str:
        """Generate a report in the specified format.

        Args:
            results: List of validation results
            format: Output format
            use_color: Whether to use ANSI colors (for HUMAN format)

        Returns:
            Formatted report string
        """
        if format == ReportFormat.HUMAN:
            return self._generate_human(results, use_color)
        elif format == ReportFormat.JSON:
            return json.dumps(self.generate_json(results), indent=2)
        elif format == ReportFormat.MARKDOWN:
            return self._generate_markdown(results)
        elif format == ReportFormat.COMPACT:
            return self._generate_compact(results)
        else:
            raise ValueError(f"Unknown format: {format}")

    def generate_json(self, results: list[RoundTripResult]) -> dict[str, Any]:
        """Generate machine-readable JSON report.

        Args:
            results: List of validation results

        Returns:
            Dictionary suitable for JSON serialization
        """
        summary = ReportSummary.from_results(results)

        return {
            "title": self.title,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total": summary.total,
                "passed": summary.passed,
                "failed": summary.failed,
                "errors": summary.errors,
                "skipped": summary.skipped,
                "pass_rate": summary.pass_rate,
                "duration_ms": summary.duration_ms,
            },
            "results": [
                self._result_to_json(r) for r in results
            ],
        }

    def _generate_human(
        self,
        results: list[RoundTripResult],
        use_color: bool,
    ) -> str:
        """Generate human-readable report."""
        lines: list[str] = []
        c = self.COLORS if use_color else {k: "" for k in self.COLORS}

        # Header
        lines.append(f"{c['bold']}{self.title}{c['reset']}")
        lines.append("=" * len(self.title))
        lines.append("")

        # Summary
        summary = ReportSummary.from_results(results)
        lines.append(f"{c['bold']}Summary{c['reset']}")
        lines.append("-" * 7)
        lines.append(f"  Total:   {summary.total}")

        pass_color = c['green'] if summary.passed > 0 else c['reset']
        lines.append(f"  Passed:  {pass_color}{summary.passed}{c['reset']}")

        fail_color = c['red'] if summary.failed > 0 else c['reset']
        lines.append(f"  Failed:  {fail_color}{summary.failed}{c['reset']}")

        error_color = c['yellow'] if summary.errors > 0 else c['reset']
        lines.append(f"  Errors:  {error_color}{summary.errors}{c['reset']}")

        lines.append(f"  Skipped: {summary.skipped}")
        lines.append(f"  Pass Rate: {summary.pass_rate:.1f}%")
        lines.append(f"  Duration: {summary.duration_ms:.1f}ms")
        lines.append("")

        # Results detail
        if results:
            lines.append(f"{c['bold']}Results{c['reset']}")
            lines.append("-" * 7)

            for i, result in enumerate(results, 1):
                status_str, status_color = self._status_display(result.status, c)
                lines.append(
                    f"  {i}. [{status_color}{status_str}{c['reset']}] "
                    f"{result.level.value.upper()} "
                    f"({result.duration_ms:.1f}ms)"
                )

                if result.failure_reason:
                    lines.append(f"      Reason: {result.failure_reason}")

                if result.comparison and result.comparison.ast_differences:
                    lines.append(f"      AST diffs: {len(result.comparison.ast_differences)}")
                    for diff in result.comparison.ast_differences[:3]:
                        lines.append(f"        - {diff}")
                    if len(result.comparison.ast_differences) > 3:
                        more = len(result.comparison.ast_differences) - 3
                        lines.append(f"        ... and {more} more")

                if result.comparison and result.comparison.semantic_differences:
                    lines.append(f"      Semantic diffs: {len(result.comparison.semantic_differences)}")
                    for diff in result.comparison.semantic_differences[:3]:
                        lines.append(f"        - {diff}")
                    if len(result.comparison.semantic_differences) > 3:
                        more = len(result.comparison.semantic_differences) - 3
                        lines.append(f"        ... and {more} more")

                lines.append("")

        return "\n".join(lines)

    def _generate_markdown(self, results: list[RoundTripResult]) -> str:
        """Generate Markdown report."""
        lines: list[str] = []
        summary = ReportSummary.from_results(results)

        # Header
        lines.append(f"# {self.title}")
        lines.append("")
        lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
        lines.append("")

        # Summary table
        lines.append("## Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total | {summary.total} |")
        lines.append(f"| Passed | {summary.passed} |")
        lines.append(f"| Failed | {summary.failed} |")
        lines.append(f"| Errors | {summary.errors} |")
        lines.append(f"| Skipped | {summary.skipped} |")
        lines.append(f"| Pass Rate | {summary.pass_rate:.1f}% |")
        lines.append(f"| Duration | {summary.duration_ms:.1f}ms |")
        lines.append("")

        # Results
        if results:
            lines.append("## Results")
            lines.append("")
            lines.append("| # | Status | Level | Duration | Details |")
            lines.append("|---|--------|-------|----------|---------|")

            for i, result in enumerate(results, 1):
                status_emoji = self._status_emoji(result.status)
                details = result.failure_reason or "OK"
                lines.append(
                    f"| {i} | {status_emoji} {result.status.value} | "
                    f"{result.level.value.upper()} | "
                    f"{result.duration_ms:.1f}ms | {details} |"
                )

            lines.append("")

        # Failures detail
        failures = [r for r in results if r.status == ValidationStatus.FAILED]
        if failures:
            lines.append("## Failure Details")
            lines.append("")

            for i, result in enumerate(failures, 1):
                lines.append(f"### Failure {i}")
                lines.append("")

                if result.comparison:
                    if result.comparison.ast_differences:
                        lines.append("**AST Differences:**")
                        lines.append("")
                        for diff in result.comparison.ast_differences:
                            lines.append(f"- {diff}")
                        lines.append("")

                    if result.comparison.semantic_differences:
                        lines.append("**Semantic Differences:**")
                        lines.append("")
                        for diff in result.comparison.semantic_differences:
                            lines.append(f"- {diff}")
                        lines.append("")

        return "\n".join(lines)

    def _generate_compact(self, results: list[RoundTripResult]) -> str:
        """Generate compact one-line-per-result output."""
        lines: list[str] = []

        for result in results:
            lines.append(result.summary())

        # Add summary line
        summary = ReportSummary.from_results(results)
        lines.append("")
        lines.append(
            f"Total: {summary.total} | "
            f"Passed: {summary.passed} | "
            f"Failed: {summary.failed} | "
            f"Errors: {summary.errors} | "
            f"Rate: {summary.pass_rate:.1f}%"
        )

        return "\n".join(lines)

    def _result_to_json(self, result: RoundTripResult) -> dict[str, Any]:
        """Convert a single result to JSON-serializable dict."""
        data: dict[str, Any] = {
            "status": result.status.value,
            "level": result.level.value,
            "duration_ms": result.duration_ms,
            "timestamp": result.timestamp.isoformat(),
            "source_hash": result.source_hash,
        }

        if result.target_hash:
            data["target_hash"] = result.target_hash

        if result.failure_reason:
            data["failure_reason"] = result.failure_reason

        if result.comparison:
            data["comparison"] = {
                "equivalent": result.comparison.equivalent,
                "summary": result.comparison.summary,
                "ast_difference_count": len(result.comparison.ast_differences),
                "semantic_difference_count": len(result.comparison.semantic_differences),
            }

            if result.comparison.ast_differences:
                data["comparison"]["ast_differences"] = [
                    str(d) for d in result.comparison.ast_differences[:10]
                ]

            if result.comparison.semantic_differences:
                data["comparison"]["semantic_differences"] = [
                    str(d) for d in result.comparison.semantic_differences[:10]
                ]

        if result.gaps:
            data["gaps"] = [
                {
                    "id": g.id,
                    "type": g.gap_type.value if hasattr(g.gap_type, 'value') else str(g.gap_type),
                    "severity": g.severity.value if hasattr(g.severity, 'value') else str(g.severity),
                    "description": g.description,
                }
                for g in result.gaps
            ]

        return data

    def _status_display(
        self,
        status: ValidationStatus,
        colors: dict[str, str],
    ) -> tuple[str, str]:
        """Get status display string and color."""
        mapping = {
            ValidationStatus.PASSED: ("PASS", colors["green"]),
            ValidationStatus.FAILED: ("FAIL", colors["red"]),
            ValidationStatus.ERROR: ("ERROR", colors["yellow"]),
            ValidationStatus.SKIPPED: ("SKIP", colors["cyan"]),
        }
        return mapping.get(status, ("???", colors["reset"]))

    def _status_emoji(self, status: ValidationStatus) -> str:
        """Get status emoji for Markdown."""
        mapping = {
            ValidationStatus.PASSED: "v",
            ValidationStatus.FAILED: "x",
            ValidationStatus.ERROR: "!",
            ValidationStatus.SKIPPED: "-",
        }
        return mapping.get(status, "?")
