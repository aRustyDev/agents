"""CLI entry point for TypeScript synthesizer.

Usage:
    python -m ir_synthesize_typescript input.json
    python -m ir_synthesize_typescript input.json -o output.ts
    python -m ir_synthesize_typescript input.json --format formatted
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ir_core.base import OutputFormat, SynthConfig
from ir_core.models import IRVersion

from ir_synthesize_typescript import TypeScriptSynthesizer


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Synthesize TypeScript code from IR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m ir_synthesize_typescript ir.json
    python -m ir_synthesize_typescript ir.json -o output.ts
    python -m ir_synthesize_typescript ir.json --format formatted
        """,
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input IR JSON file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output TypeScript file (default: stdout)",
    )
    parser.add_argument(
        "--format",
        choices=["source", "formatted", "preserved"],
        default="formatted",
        help="Output format",
    )
    parser.add_argument(
        "--line-length",
        type=int,
        default=100,
        help="Maximum line length",
    )
    parser.add_argument(
        "--indent-size",
        type=int,
        default=2,
        help="Indentation size in spaces",
    )
    parser.add_argument(
        "--use-tabs",
        action="store_true",
        help="Use tabs instead of spaces",
    )
    parser.add_argument(
        "--no-types",
        action="store_true",
        help="Omit type annotations",
    )
    parser.add_argument(
        "--target",
        default="ES2022",
        help="Target ECMAScript version",
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Read IR
    try:
        with open(args.input, encoding="utf-8") as f:
            ir_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Convert to IRVersion
    try:
        ir = IRVersion.from_dict(ir_data)
    except Exception as e:
        print(f"Error parsing IR: {e}", file=sys.stderr)
        return 1

    # Configure synthesis
    config = SynthConfig(
        output_format=OutputFormat(args.format),
        line_length=args.line_length,
        indent_size=args.indent_size,
        use_tabs=args.use_tabs,
        emit_type_hints=not args.no_types,
        target_version=args.target,
    )

    # Synthesize
    synthesizer = TypeScriptSynthesizer()
    try:
        code = synthesizer.synthesize(ir, config)
    except Exception as e:
        print(f"Synthesis error: {e}", file=sys.stderr)
        return 1

    # Write output
    if args.output:
        try:
            args.output.write_text(code, encoding="utf-8")
            print(f"Wrote TypeScript to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return 1
    else:
        print(code)

    # Report gaps
    if synthesizer.last_gaps:
        print(f"\nDetected {len(synthesizer.last_gaps)} gap(s):", file=sys.stderr)
        for gap in synthesizer.last_gaps:
            print(
                f"  [{gap.severity.value}] {gap.kind}: {gap.description}",
                file=sys.stderr,
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
