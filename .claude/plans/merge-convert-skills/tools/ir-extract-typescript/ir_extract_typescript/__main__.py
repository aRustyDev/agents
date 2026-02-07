"""CLI entry point for TypeScript extractor.

Usage:
    python -m ir_extract_typescript path/to/file.ts
    python -m ir_extract_typescript path/to/file.ts -o output.json
    python -m ir_extract_typescript file.ts --pretty --spans
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ir_core.base import ExtractConfig, ExtractionMode, SemanticEnrichmentLevel

from ir_extract_typescript import TypeScriptExtractor


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract TypeScript source code to IR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m ir_extract_typescript src/types.ts
    python -m ir_extract_typescript src/types.ts -o output.json
    python -m ir_extract_typescript src/types.ts --pretty
        """,
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input TypeScript file to extract",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    parser.add_argument(
        "--spans",
        action="store_true",
        help="Include source location spans",
    )
    parser.add_argument(
        "--layer0",
        action="store_true",
        help="Include expression-level details (Layer 0)",
    )
    parser.add_argument(
        "--semantic",
        choices=["none", "basic", "full"],
        default="basic",
        help="Semantic enrichment level",
    )
    parser.add_argument(
        "--mode",
        choices=["full_module", "single_function", "type_only", "signature_only"],
        default="full_module",
        help="Extraction mode",
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    if args.input.suffix not in {".ts", ".tsx", ".mts", ".cts"}:
        print(
            f"Warning: Input file may not be TypeScript: {args.input.suffix}",
            file=sys.stderr,
        )

    # Read source
    try:
        source = args.input.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Configure extraction
    config = ExtractConfig(
        mode=ExtractionMode(args.mode),
        include_layer0=args.layer0,
        semantic_level=SemanticEnrichmentLevel(args.semantic),
        preserve_spans=args.spans,
    )

    # Extract
    extractor = TypeScriptExtractor()
    try:
        ir = extractor.extract(source, str(args.input), config)
    except Exception as e:
        print(f"Extraction error: {e}", file=sys.stderr)
        return 1

    # Convert to JSON-serializable format
    output_data = ir.to_dict()

    # Format output
    if args.pretty:
        output_str = json.dumps(output_data, indent=2, ensure_ascii=False)
    else:
        output_str = json.dumps(output_data, ensure_ascii=False)

    # Write output
    if args.output:
        try:
            args.output.write_text(output_str, encoding="utf-8")
            print(f"Wrote IR to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return 1
    else:
        print(output_str)

    # Report gaps
    if ir.gaps:
        print(f"\nDetected {len(ir.gaps)} gap(s):", file=sys.stderr)
        for gap in ir.gaps:
            print(f"  [{gap.severity.value}] {gap.kind}: {gap.description}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
