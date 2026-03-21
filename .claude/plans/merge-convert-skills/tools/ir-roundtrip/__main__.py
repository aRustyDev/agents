"""CLI for the round-trip validation tool.

Usage:
    python -m ir_roundtrip validate file.py
    python -m ir_roundtrip validate --level l3 file.py
    python -m ir_roundtrip batch dir/ --report report.json
    python -m ir_roundtrip benchmark --samples 100

Commands:
    validate    Validate a single file
    batch       Validate multiple files
    benchmark   Run performance benchmarks
    compare     Compare two code files directly
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from .comparison import CodeComparator
from .report import ReportFormat, RoundTripReport
from .validator import PreservationLevel, RoundTripValidator


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="ir-roundtrip",
        description="Round-trip validation for Python -> IR -> Python conversion",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate round-trip for a single file",
    )
    validate_parser.add_argument(
        "file",
        type=Path,
        help="Python file to validate",
    )
    validate_parser.add_argument(
        "--level", "-l",
        choices=["l1", "l2", "l3"],
        default="l3",
        help="Preservation level to test (default: l3)",
    )
    validate_parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for synthesized code",
    )
    validate_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    validate_parser.add_argument(
        "--format",
        choices=["human", "json", "compact"],
        default="human",
        help="Output format (default: human)",
    )

    # batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Validate multiple files",
    )
    batch_parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing Python files",
    )
    batch_parser.add_argument(
        "--level", "-l",
        choices=["l1", "l2", "l3"],
        default="l3",
        help="Preservation level to test (default: l3)",
    )
    batch_parser.add_argument(
        "--report", "-r",
        type=Path,
        help="Output file for JSON report",
    )
    batch_parser.add_argument(
        "--format",
        choices=["human", "json", "markdown", "compact"],
        default="human",
        help="Output format (default: human)",
    )
    batch_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search directories recursively",
    )

    # benchmark command
    bench_parser = subparsers.add_parser(
        "benchmark",
        help="Run performance benchmarks",
    )
    bench_parser.add_argument(
        "--samples", "-n",
        type=int,
        default=100,
        help="Number of sample programs to generate (default: 100)",
    )
    bench_parser.add_argument(
        "--level", "-l",
        choices=["l1", "l2", "l3"],
        default="l3",
        help="Preservation level to test (default: l3)",
    )
    bench_parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for benchmark results",
    )

    # compare command
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare two code files directly",
    )
    compare_parser.add_argument(
        "source",
        type=Path,
        help="Source Python file",
    )
    compare_parser.add_argument(
        "target",
        type=Path,
        help="Target Python file",
    )
    compare_parser.add_argument(
        "--level", "-l",
        choices=["l1", "l2", "l3"],
        default="l3",
        help="Comparison level (default: l3)",
    )
    compare_parser.add_argument(
        "--diff",
        action="store_true",
        help="Show unified diff for L1 comparison",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "validate":
        return cmd_validate(args)
    elif args.command == "batch":
        return cmd_batch(args)
    elif args.command == "benchmark":
        return cmd_benchmark(args)
    elif args.command == "compare":
        return cmd_compare(args)
    else:
        parser.print_help()
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Handle validate command."""
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    source = args.file.read_text(encoding="utf-8")
    level = _parse_level(args.level)

    validator = RoundTripValidator()
    result = validator.validate(source, level, filename=str(args.file))

    # Output synthesized code if requested
    if args.output and result.target:
        args.output.write_text(result.target, encoding="utf-8")
        if args.verbose:
            print(f"Synthesized code written to: {args.output}")

    # Generate report
    report = RoundTripReport(title=f"Validation: {args.file.name}")
    format_map = {
        "human": ReportFormat.HUMAN,
        "json": ReportFormat.JSON,
        "compact": ReportFormat.COMPACT,
    }
    output = report.generate([result], format_map[args.format])
    print(output)

    # Verbose output
    if args.verbose and result.target:
        print("\n--- Synthesized Code ---")
        print(result.target)

    return 0 if result.passed else 1


def cmd_batch(args: argparse.Namespace) -> int:
    """Handle batch command."""
    if not args.directory.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        return 1

    # Find Python files
    pattern = "**/*.py" if args.recursive else "*.py"
    files = list(args.directory.glob(pattern))

    if not files:
        print(f"No Python files found in: {args.directory}", file=sys.stderr)
        return 1

    print(f"Found {len(files)} Python files", file=sys.stderr)

    level = _parse_level(args.level)
    validator = RoundTripValidator()

    # Load sources
    sources: list[tuple[str, str]] = []
    for f in files:
        try:
            source = f.read_text(encoding="utf-8")
            sources.append((str(f), source))
        except Exception as e:
            print(f"Warning: Could not read {f}: {e}", file=sys.stderr)

    # Progress callback
    def progress(current: int, total: int) -> None:
        if total > 0:
            pct = current * 100 // total
            print(f"\rProgress: {current}/{total} ({pct}%)", end="", file=sys.stderr)

    # Validate
    results = validator.validate_batch(sources, level, progress_callback=progress)
    print("", file=sys.stderr)  # Newline after progress

    # Generate report
    report = RoundTripReport(title=f"Batch Validation: {args.directory}")
    format_map = {
        "human": ReportFormat.HUMAN,
        "json": ReportFormat.JSON,
        "markdown": ReportFormat.MARKDOWN,
        "compact": ReportFormat.COMPACT,
    }
    output = report.generate(results, format_map[args.format])
    print(output)

    # Write JSON report if requested
    if args.report:
        json_data = report.generate_json(results)
        args.report.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        print(f"\nJSON report written to: {args.report}", file=sys.stderr)

    # Return non-zero if any failures
    failed = sum(1 for r in results if not r.passed)
    return 1 if failed > 0 else 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    """Handle benchmark command."""
    print(f"Running benchmark with {args.samples} samples at level {args.level}")

    level = _parse_level(args.level)
    validator = RoundTripValidator()

    # Generate sample programs
    samples = _generate_benchmark_samples(args.samples)

    results: list[dict[str, Any]] = []
    total_time = 0.0
    passed = 0

    for i, (name, source) in enumerate(samples):
        start = time.perf_counter()
        result = validator.validate(source, level, filename=name)
        elapsed = (time.perf_counter() - start) * 1000

        total_time += elapsed
        if result.passed:
            passed += 1

        results.append({
            "name": name,
            "passed": result.passed,
            "duration_ms": elapsed,
        })

        # Progress
        print(f"\r{i + 1}/{args.samples}", end="", file=sys.stderr)

    print("", file=sys.stderr)

    # Summary
    avg_time = total_time / len(samples) if samples else 0
    pass_rate = passed * 100 / len(samples) if samples else 0

    print("\nBenchmark Results")
    print("=" * 40)
    print(f"  Samples:    {len(samples)}")
    print(f"  Passed:     {passed} ({pass_rate:.1f}%)")
    print(f"  Total time: {total_time:.1f}ms")
    print(f"  Avg time:   {avg_time:.2f}ms per sample")

    # Write detailed results if requested
    if args.output:
        output_data = {
            "summary": {
                "samples": len(samples),
                "passed": passed,
                "pass_rate": pass_rate,
                "total_time_ms": total_time,
                "avg_time_ms": avg_time,
            },
            "results": results,
        }
        args.output.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
        print(f"\nResults written to: {args.output}")

    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """Handle compare command."""
    if not args.source.exists():
        print(f"Error: Source file not found: {args.source}", file=sys.stderr)
        return 1

    if not args.target.exists():
        print(f"Error: Target file not found: {args.target}", file=sys.stderr)
        return 1

    source = args.source.read_text(encoding="utf-8")
    target = args.target.read_text(encoding="utf-8")

    comparator = CodeComparator()

    if args.level == "l1":
        result = comparator.compare_l1_syntactic(source, target)
    elif args.level == "l2":
        result = comparator.compare_l2_operational(source, target)
    else:
        # For L3, we need test inputs - use empty list for now
        result = comparator.compare_l3_semantic(source, target, [])

    # Output
    print(f"Comparison: {args.source.name} vs {args.target.name}")
    print(f"Level: {args.level.upper()}")
    print(f"Equivalent: {result.equivalent}")
    print()

    if result.ast_differences:
        print(f"AST Differences ({len(result.ast_differences)}):")
        for diff in result.ast_differences:
            print(f"  - {diff}")

    if result.semantic_differences:
        print(f"\nSemantic Differences ({len(result.semantic_differences)}):")
        for diff in result.semantic_differences:
            print(f"  - {diff}")

    if args.diff and result.source_ast_dump and result.target_ast_dump:
        print("\nUnified Diff:")
        print(result.unified_diff())

    return 0 if result.equivalent else 1


def _parse_level(level_str: str) -> PreservationLevel:
    """Parse preservation level from string."""
    mapping = {
        "l1": PreservationLevel.L1_SYNTACTIC,
        "l2": PreservationLevel.L2_OPERATIONAL,
        "l3": PreservationLevel.L3_SEMANTIC,
    }
    return mapping[level_str.lower()]


def _generate_benchmark_samples(count: int) -> list[tuple[str, str]]:
    """Generate sample programs for benchmarking."""
    samples: list[tuple[str, str]] = []

    # Simple function samples
    for i in range(count // 3):
        samples.append((
            f"simple_{i}.py",
            f'''def func_{i}(x: int) -> int:
    """Simple function {i}."""
    return x + {i}
'''
        ))

    # Class samples
    for i in range(count // 3):
        samples.append((
            f"class_{i}.py",
            f'''class Class{i}:
    """Sample class {i}."""

    def __init__(self, value: int) -> None:
        self.value = value

    def get_value(self) -> int:
        """Get the value."""
        return self.value + {i}
'''
        ))

    # Complex samples
    remaining = count - len(samples)
    for i in range(remaining):
        samples.append((
            f"complex_{i}.py",
            f'''from typing import List

def process_{i}(items: List[int]) -> List[int]:
    """Process items with filtering and mapping."""
    result = []
    for item in items:
        if item > {i}:
            result.append(item * 2)
    return result

def recursive_{i}(n: int) -> int:
    """Recursive function."""
    if n <= 1:
        return {i}
    return n + recursive_{i}(n - 1)
'''
        ))

    return samples


if __name__ == "__main__":
    sys.exit(main())
