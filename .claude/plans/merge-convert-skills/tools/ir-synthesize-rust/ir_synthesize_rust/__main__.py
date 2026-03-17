"""CLI entry point for the Rust IR synthesizer.

Usage:
    python -m ir_synthesize_rust input.json [options]

Options:
    --output, -o    Output file for Rust code (default: stdout)
    --format, -f    Output format: source, formatted (default: formatted)
    --edition       Rust edition: 2015, 2018, 2021 (default: 2021)
    --line-length   Maximum line length (default: 100)
    --indent        Indent size in spaces (default: 4)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ir_core.base import OutputFormat, SynthConfig
from ir_core.models import IRVersion

from .synthesizer import RustSynthesizer


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Synthesize Rust code from IR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Path to IR JSON file",
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file (default: stdout)",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["source", "formatted"],
        default="formatted",
        help="Output format (default: formatted)",
    )

    parser.add_argument(
        "--edition",
        choices=["2015", "2018", "2021"],
        default="2021",
        help="Rust edition (default: 2021)",
    )

    parser.add_argument(
        "--line-length",
        type=int,
        default=100,
        help="Maximum line length (default: 100)",
    )

    parser.add_argument(
        "--indent",
        type=int,
        default=4,
        help="Indent size in spaces (default: 4)",
    )

    parser.add_argument(
        "--no-docstrings",
        action="store_true",
        help="Omit documentation comments",
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1

    # Read IR
    try:
        ir_data = json.loads(args.input.read_text(encoding="utf-8"))
        ir = IRVersion.model_validate(ir_data)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error loading IR: {e}", file=sys.stderr)
        return 1

    # Configure synthesis
    format_map = {
        "source": OutputFormat.SOURCE,
        "formatted": OutputFormat.FORMATTED,
    }

    config = SynthConfig(
        output_format=format_map[args.format],
        line_length=args.line_length,
        indent_size=args.indent,
        emit_docstrings=not args.no_docstrings,
        target_version=args.edition,
    )

    # Synthesize
    try:
        synthesizer = RustSynthesizer()
        code = synthesizer.synthesize(ir, config)
    except Exception as e:
        print(f"Error during synthesis: {e}", file=sys.stderr)
        return 1

    # Output
    if args.output:
        try:
            args.output.write_text(code, encoding="utf-8")
            print(f"Rust code written to: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return 1
    else:
        print(code)

    # Report summary
    gap_count = len(synthesizer.last_gaps)
    if gap_count > 0:
        print(f"\nWarning: {gap_count} gaps encountered during synthesis", file=sys.stderr)
        for gap in synthesizer.last_gaps[:5]:
            print(f"  - {gap.description}", file=sys.stderr)
        if gap_count > 5:
            print(f"  ... and {gap_count - 5} more", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
