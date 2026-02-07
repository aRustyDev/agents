"""CLI entry point for Go synthesizer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from ir_synthesize_golang import GolangSynthesizer


def main() -> int:
    """Run the Go synthesizer CLI."""
    parser = argparse.ArgumentParser(
        description="Synthesize Go source code from IR"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="IR file to synthesize (YAML or JSON)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--no-format",
        action="store_true",
        help="Skip gofmt formatting",
    )

    args = parser.parse_args()

    # Read IR file
    ir_path = args.file
    if not ir_path.exists():
        print(f"Error: File not found: {ir_path}", file=sys.stderr)
        return 1

    content = ir_path.read_text(encoding="utf-8")

    # Parse IR
    try:
        ir_dict = yaml.safe_load(content)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML: {e}", file=sys.stderr)
        return 1

    # Convert to IRVersion
    from ir_core.models import IRVersion

    ir = IRVersion.from_dict(ir_dict)

    # Synthesize Go code
    from ir_core.base import SynthConfig

    synthesizer = GolangSynthesizer()
    config = SynthConfig(format=not args.no_format)
    code = synthesizer.synthesize(ir, config)

    # Write output
    if args.output:
        args.output.write_text(code, encoding="utf-8")
    else:
        print(code)

    return 0


if __name__ == "__main__":
    sys.exit(main())
