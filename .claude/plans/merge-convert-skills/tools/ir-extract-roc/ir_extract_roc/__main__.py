"""CLI entry point for Roc extractor."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from ir_extract_roc import RocExtractor


def main() -> int:
    """Run the Roc extractor CLI."""
    parser = argparse.ArgumentParser(
        description="Extract IR from Roc source code"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Roc source file to extract",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "yaml"],
        default="yaml",
        help="Output format (default: yaml)",
    )

    args = parser.parse_args()

    # Read source file
    source_path = args.file
    if not source_path.exists():
        print(f"Error: File not found: {source_path}", file=sys.stderr)
        return 1

    source = source_path.read_text(encoding="utf-8")

    # Extract IR
    from ir_core.base import ExtractConfig

    extractor = RocExtractor()
    config = ExtractConfig()
    ir = extractor.extract(source, str(source_path), config)

    # Serialize output
    if args.format == "json":
        output = json.dumps(ir.to_dict(), indent=2)
    else:
        output = yaml.safe_dump(ir.to_dict(), sort_keys=False, allow_unicode=True)

    # Write output
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
