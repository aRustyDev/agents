"""CLI entry point for the Rust IR extractor.

Usage:
    python -m ir_extract_rust path/to/file.rs [options]

Options:
    --output, -o    Output file for IR (default: stdout)
    --format, -f    Output format: json (default), yaml
    --pretty        Pretty-print JSON output
    --mode, -m      Extraction mode: full, single_function, type_only, signature_only
    --semantic      Semantic enrichment level: none, basic, full
    --spans         Include source spans in output
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ir_core.base import ExtractConfig, ExtractionMode, SemanticEnrichmentLevel

from .extractor import RustExtractor


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract IR from Rust source code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Path to Rust source file",
    )

    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file (default: stdout)",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["json", "yaml"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["full", "single_function", "type_only", "signature_only"],
        default="full",
        help="Extraction mode (default: full)",
    )

    parser.add_argument(
        "--semantic",
        choices=["none", "basic", "full"],
        default="basic",
        help="Semantic enrichment level (default: basic)",
    )

    parser.add_argument(
        "--spans",
        action="store_true",
        help="Include source spans in output",
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1

    if not args.input.suffix == ".rs":
        print(f"Warning: File does not have .rs extension: {args.input}", file=sys.stderr)

    # Read source
    try:
        source = args.input.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Configure extraction
    mode_map = {
        "full": ExtractionMode.FULL_MODULE,
        "single_function": ExtractionMode.SINGLE_FUNCTION,
        "type_only": ExtractionMode.TYPE_ONLY,
        "signature_only": ExtractionMode.SIGNATURE_ONLY,
    }

    semantic_map = {
        "none": SemanticEnrichmentLevel.NONE,
        "basic": SemanticEnrichmentLevel.BASIC,
        "full": SemanticEnrichmentLevel.FULL,
    }

    config = ExtractConfig(
        mode=mode_map[args.mode],
        semantic_level=semantic_map[args.semantic],
        preserve_spans=args.spans,
    )

    # Extract
    try:
        extractor = RustExtractor()
        ir = extractor.extract(source, str(args.input), config)
    except Exception as e:
        print(f"Error during extraction: {e}", file=sys.stderr)
        return 1

    # Serialize
    ir_dict = ir.model_dump(mode="json", exclude_none=True)

    if args.format == "json":
        indent = 2 if args.pretty else None
        output = json.dumps(ir_dict, indent=indent, ensure_ascii=False)
    elif args.format == "yaml":
        try:
            import yaml
            output = yaml.dump(ir_dict, default_flow_style=False, allow_unicode=True)
        except ImportError:
            print("Error: PyYAML not installed. Use --format json or install pyyaml.", file=sys.stderr)
            return 1

    # Output
    if args.output:
        try:
            args.output.write_text(output, encoding="utf-8")
            print(f"IR written to: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return 1
    else:
        print(output)

    # Report summary
    type_count = len(ir.types)
    func_count = len(ir.functions)
    gap_count = len(ir.gaps)

    print(
        f"\nExtracted: {type_count} types, {func_count} functions, {gap_count} gaps",
        file=sys.stderr,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
