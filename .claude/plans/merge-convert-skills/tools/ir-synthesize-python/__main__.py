"""Command-line interface for the Python synthesizer.

Usage:
    python -m ir_synthesize_python ir.yaml
    python -m ir_synthesize_python --format --level idiomatic ir.yaml
    python -m ir_synthesize_python --output output.py ir.yaml

Examples:
    # Synthesize from YAML IR file
    python -m ir_synthesize_python extracted.yaml

    # Synthesize with formatting and output to file
    python -m ir_synthesize_python --format --output module.py extracted.yaml

    # Use idiomatic preservation level
    python -m ir_synthesize_python --level idiomatic extracted.yaml

    # Show what would be generated without writing
    python -m ir_synthesize_python --dry-run extracted.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

import yaml

from ir_core.base import SynthConfig, OutputFormat
from ir_core.models import IRVersion

from .synthesizer import PythonSynthesizer, PreservationMode


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ir-synthesize-python",
        description="Generate Python source code from IR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s extracted.yaml                    Synthesize and print to stdout
  %(prog)s -o module.py extracted.yaml       Write to file
  %(prog)s --format extracted.yaml           Format with black
  %(prog)s --level idiomatic extracted.yaml  Use idiomatic patterns
  %(prog)s --no-types extracted.yaml         Omit type hints
        """,
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Path to IR file (YAML or JSON)",
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output file path (default: stdout)",
    )

    parser.add_argument(
        "-f", "--format",
        action="store_true",
        help="Format output with black/ruff",
    )

    parser.add_argument(
        "--level",
        type=str,
        choices=["correct", "idiomatic", "optimized"],
        default="idiomatic",
        help="Preservation level (default: idiomatic)",
    )

    parser.add_argument(
        "--no-types",
        action="store_true",
        help="Omit type hints",
    )

    parser.add_argument(
        "--no-docstrings",
        action="store_true",
        help="Omit docstrings",
    )

    parser.add_argument(
        "--line-length",
        type=int,
        default=88,
        help="Maximum line length (default: 88)",
    )

    parser.add_argument(
        "--target-version",
        type=str,
        default="3.11",
        help="Target Python version (default: 3.11)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing",
    )

    parser.add_argument(
        "--show-gaps",
        action="store_true",
        help="Show synthesis gaps in output",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    return parser


def load_ir(path: Path) -> IRVersion:
    """Load IR from a file.

    Args:
        path: Path to IR file (YAML or JSON)

    Returns:
        IRVersion object

    Raises:
        ValueError: If file format is unsupported
        FileNotFoundError: If file doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"IR file not found: {path}")

    content = path.read_text(encoding="utf-8")

    if path.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(content)
    elif path.suffix == ".json":
        data = json.loads(content)
    else:
        # Try YAML first, then JSON
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError:
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Could not parse IR file: {e}") from e

    return IRVersion.model_validate(data)


def write_output(
    code: str,
    output: Path | None,
    dry_run: bool = False,
    stream: TextIO = sys.stdout,
) -> None:
    """Write output to file or stream.

    Args:
        code: Generated code
        output: Output file path or None for stdout
        dry_run: If True, don't actually write
        stream: Output stream for stdout mode
    """
    if dry_run:
        print("--- DRY RUN ---", file=sys.stderr)
        print(code, file=stream)
        return

    if output:
        output.write_text(code, encoding="utf-8")
        print(f"Wrote {len(code)} bytes to {output}", file=sys.stderr)
    else:
        print(code, file=stream)


def main(args: list[str] | None = None) -> int:
    """Main entry point.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    parsed = parser.parse_args(args)

    try:
        # Load IR
        if parsed.verbose:
            print(f"Loading IR from {parsed.input}", file=sys.stderr)

        ir = load_ir(parsed.input)

        if parsed.verbose:
            print(f"Loaded IR version {ir.version}", file=sys.stderr)
            print(f"  Types: {len(ir.types)}", file=sys.stderr)
            print(f"  Functions: {len(ir.functions)}", file=sys.stderr)
            print(f"  Gaps: {len(ir.gaps)}", file=sys.stderr)

        # Create config
        output_format = OutputFormat.FORMATTED if parsed.format else OutputFormat.SOURCE

        config = SynthConfig(
            output_format=output_format,
            line_length=parsed.line_length,
            emit_type_hints=not parsed.no_types,
            emit_docstrings=not parsed.no_docstrings,
            target_version=parsed.target_version,
            custom_options={
                "preservation_mode": parsed.level,
            },
        )

        # Synthesize
        if parsed.verbose:
            print(f"Synthesizing with level={parsed.level}", file=sys.stderr)

        synthesizer = PythonSynthesizer()
        code = synthesizer.synthesize(ir, config)

        # Show gaps if requested
        if parsed.show_gaps and synthesizer.last_gaps:
            print("--- Synthesis Gaps ---", file=sys.stderr)
            for gap in synthesizer.last_gaps:
                print(f"  [{gap.severity.value}] {gap.description}", file=sys.stderr)
            print("---", file=sys.stderr)

        # Output
        write_output(code, parsed.output, parsed.dry_run)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
