#!/usr/bin/env python3
"""Test runner script for the integration test suite.

This script provides a convenient way to run the test suite with various options.

Usage:
    # Run all tests
    python run_tests.py

    # Run specific test file
    python run_tests.py test_integration.py

    # Run with markers
    python run_tests.py --markers "integration and not slow"

    # Run with coverage
    python run_tests.py --coverage

    # Run in parallel
    python run_tests.py --parallel
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run the test suite."""
    parser = argparse.ArgumentParser(description="Run integration tests")
    parser.add_argument(
        "tests",
        nargs="*",
        default=["."],
        help="Test files or directories to run",
    )
    parser.add_argument(
        "-m", "--markers",
        default=None,
        help="Pytest marker expression",
    )
    parser.add_argument(
        "-k", "--keyword",
        default=None,
        help="Pytest keyword expression",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=1,
        help="Increase verbosity",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip slow tests",
    )
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests",
    )
    parser.add_argument(
        "--preservation-only",
        action="store_true",
        help="Run only preservation level tests",
    )

    args = parser.parse_args()

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add test paths
    test_dir = Path(__file__).parent
    for test in args.tests:
        if not Path(test).is_absolute():
            cmd.append(str(test_dir / test))
        else:
            cmd.append(test)

    # Add verbosity
    cmd.append("-" + "v" * args.verbose)

    # Add markers
    markers = []
    if args.quick:
        markers.append("not slow")
    if args.integration_only:
        markers.append("integration")
    if args.preservation_only:
        markers.append("preservation")
    if args.markers:
        markers.append(args.markers)

    if markers:
        cmd.extend(["-m", " and ".join(markers)])

    # Add keyword filter
    if args.keyword:
        cmd.extend(["-k", args.keyword])

    # Add coverage
    if args.coverage:
        tools_dir = test_dir.parent / "tools"
        cmd.extend([
            "--cov", str(tools_dir / "ir-core"),
            "--cov", str(tools_dir / "ir-extract-python"),
            "--cov", str(tools_dir / "ir-synthesize-python"),
            "--cov", str(tools_dir / "ir-validate"),
            "--cov", str(tools_dir / "ir-query"),
            "--cov-report", "html",
            "--cov-report", "term",
        ])

    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", "auto"])

    # Add other useful options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "-ra",
    ])

    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)

    # Run pytest
    result = subprocess.run(cmd, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
