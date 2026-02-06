"""CLI entry point for IR validation.

Usage:
    python -m ir_validate check file.ir.yaml
    python -m ir_validate check --schema v1 file.ir.yaml
    python -m ir_validate batch dir/
    python -m ir_validate check --format json file.ir.yaml
"""

import argparse
import sys
from pathlib import Path
from typing import Literal

from .errors import ValidationException
from .validator import IRValidator, ValidationResult


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ir-validate",
        description="Validate IR (Intermediate Representation) documents",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # check command
    check_parser = subparsers.add_parser("check", help="Validate a single IR file")
    check_parser.add_argument("file", type=Path, help="IR file to validate (YAML or JSON)")
    check_parser.add_argument(
        "--schema",
        default="v1",
        help="Schema version to use (default: v1)",
    )
    check_parser.add_argument(
        "--format",
        choices=["human", "json", "compact"],
        default="human",
        help="Output format (default: human)",
    )
    check_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    check_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output",
    )
    check_parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Skip JSON schema validation",
    )
    check_parser.add_argument(
        "--skip-references",
        action="store_true",
        help="Skip reference integrity checks",
    )
    check_parser.add_argument(
        "--skip-consistency",
        action="store_true",
        help="Skip cross-layer consistency checks",
    )

    # batch command
    batch_parser = subparsers.add_parser("batch", help="Validate multiple IR files")
    batch_parser.add_argument("directory", type=Path, help="Directory containing IR files")
    batch_parser.add_argument(
        "--pattern",
        default="*.ir.yaml",
        help="Glob pattern for IR files (default: *.ir.yaml)",
    )
    batch_parser.add_argument(
        "--schema",
        default="v1",
        help="Schema version to use (default: v1)",
    )
    batch_parser.add_argument(
        "--format",
        choices=["human", "json", "compact"],
        default="human",
        help="Output format (default: human)",
    )
    batch_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    batch_parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure",
    )
    batch_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output",
    )

    return parser


def cmd_check(args: argparse.Namespace) -> int:
    """Handle the check command.

    Args:
        args: Parsed command line arguments.

    Returns:
        Exit code (0 for success, 1 for validation errors, 2 for exceptions).
    """
    validator = IRValidator(
        schema_version=args.schema,
        strict=args.strict,
        skip_schema=args.skip_schema,
        skip_references=args.skip_references,
        skip_consistency=args.skip_consistency,
    )

    try:
        result = validator.validate_file(args.file)
    except ValidationException as e:
        print(f"Error: {e}", file=sys.stderr)
        if e.cause:
            print(f"Caused by: {e.cause}", file=sys.stderr)
        return 2

    output_format: Literal["human", "json", "compact"] = args.format
    use_color = not args.no_color and sys.stdout.isatty()

    print(result.format(output_format=output_format, use_color=use_color))

    return 0 if result.is_valid else 1


def cmd_batch(args: argparse.Namespace) -> int:
    """Handle the batch command.

    Args:
        args: Parsed command line arguments.

    Returns:
        Exit code (0 for all passed, 1 for any failures).
    """
    directory = args.directory
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory", file=sys.stderr)
        return 2

    # Find all IR files
    pattern = args.pattern
    files = list(directory.rglob(pattern))

    if not files:
        print(f"No files matching '{pattern}' found in {directory}")
        return 0

    validator = IRValidator(
        schema_version=args.schema,
        strict=args.strict,
    )

    output_format: Literal["human", "json", "compact"] = args.format
    use_color = not args.no_color and sys.stdout.isatty()

    total_files = len(files)
    passed_files = 0
    failed_files = 0
    error_files = 0

    results: list[tuple[Path, ValidationResult | None, str | None]] = []

    for file_path in sorted(files):
        try:
            result = validator.validate_file(file_path)
            results.append((file_path, result, None))

            if result.is_valid:
                passed_files += 1
            else:
                failed_files += 1
                if args.fail_fast:
                    break
        except ValidationException as e:
            results.append((file_path, None, str(e)))
            error_files += 1
            if args.fail_fast:
                break

    # Output results
    if output_format == "json":
        import json

        output = {
            "summary": {
                "total": total_files,
                "passed": passed_files,
                "failed": failed_files,
                "errors": error_files,
            },
            "files": [],
        }
        for file_path, result, error in results:
            if error:
                output["files"].append({"file": str(file_path), "error": error})
            elif result:
                output["files"].append({
                    "file": str(file_path),
                    "passed": result.is_valid,
                    "error_count": result.error_count,
                    "warning_count": result.warning_count,
                })
        print(json.dumps(output, indent=2))
    else:
        # Human or compact format
        for file_path, result, error in results:
            if error:
                print(f"\n{'=' * 60}")
                print(f"File: {file_path}")
                print(f"Error: {error}")
            elif result:
                if not result.is_valid or output_format == "human":
                    print(result.format(output_format=output_format, use_color=use_color))

        # Summary
        if use_color:
            if failed_files or error_files:
                status = "\033[91mFAILED\033[0m"
            else:
                status = "\033[92mPASSED\033[0m"
        else:
            status = "FAILED" if (failed_files or error_files) else "PASSED"

        print(f"\n{'=' * 60}")
        print(f"Batch Validation {status}")
        print(f"Files: {total_files} total, {passed_files} passed, {failed_files} failed, {error_files} errors")

    return 0 if (failed_files == 0 and error_files == 0) else 1


def main() -> int:
    """Main entry point.

    Returns:
        Exit code.
    """
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "check":
        return cmd_check(args)
    elif args.command == "batch":
        return cmd_batch(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
