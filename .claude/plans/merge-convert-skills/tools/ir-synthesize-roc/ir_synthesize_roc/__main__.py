"""CLI entry point for Roc synthesizer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from ir_synthesize_roc import RocSynthesizer


def main() -> int:
    """Run the Roc synthesizer CLI."""
    parser = argparse.ArgumentParser(
        description="Synthesize Roc source code from IR"
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

    # Synthesize Roc code
    from ir_core.base import SynthConfig

    synthesizer = RocSynthesizer()
    config = SynthConfig()
    code = synthesizer.synthesize(ir, config)

    # Write output
    if args.output:
        args.output.write_text(code, encoding="utf-8")
    else:
        print(code)

    return 0


if __name__ == "__main__":
    sys.exit(main())
