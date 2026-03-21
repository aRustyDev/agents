"""CLI entry point for the Python extractor.

Usage:
    python -m ir_extract_python file.py
    python -m ir_extract_python --output ir.yaml file.py
    python -m ir_extract_python --enrich file.py
    python -m ir_extract_python --format json file.py
    python -m ir_extract_python --validate file.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

import yaml
from ir_core.base import ExtractConfig, ExtractionMode, SemanticEnrichmentLevel
from ir_core.models import IRVersion

from .extractor import PythonExtractor


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ir-extract-python",
        description="Extract IR from Python source code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract a single file to stdout (YAML)
    python -m ir_extract_python module.py

    # Extract with JSON output
    python -m ir_extract_python --format json module.py

    # Extract with semantic enrichment
    python -m ir_extract_python --enrich module.py

    # Extract with full pyright analysis
    python -m ir_extract_python --enrich --semantic-level full module.py

    # Write to output file
    python -m ir_extract_python -o output.yaml module.py

    # Validate without full extraction
    python -m ir_extract_python --validate module.py

    # Extract signatures only
    python -m ir_extract_python --mode signature-only module.py

    # Include expression-level details (Layer 0)
    python -m ir_extract_python --include-layer0 module.py
        """,
    )

    # Input file
    parser.add_argument(
        "file",
        type=Path,
        help="Python source file to extract",
    )

    # Output options
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)",
    )

    # Extraction options
    parser.add_argument(
        "--mode",
        choices=["full", "single-function", "type-only", "signature-only"],
        default="full",
        help="Extraction mode (default: full)",
    )
    parser.add_argument(
        "--enrich",
        action="store_true",
        help="Enable semantic enrichment with type analysis",
    )
    parser.add_argument(
        "--semantic-level",
        choices=["none", "basic", "full"],
        default="basic",
        help="Semantic enrichment level (default: basic)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Project root for import resolution",
    )
    parser.add_argument(
        "--include-layer0",
        action="store_true",
        help="Include expression-level details (Layer 0)",
    )
    parser.add_argument(
        "--resolve-imports",
        action="store_true",
        help="Attempt to resolve cross-file imports",
    )

    # Validation mode
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate source without full extraction",
    )

    # Verbosity
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )

    return parser


def mode_from_string(mode_str: str) -> ExtractionMode:
    """Convert mode string to ExtractionMode enum."""
    mapping = {
        "full": ExtractionMode.FULL_MODULE,
        "single-function": ExtractionMode.SINGLE_FUNCTION,
        "type-only": ExtractionMode.TYPE_ONLY,
        "signature-only": ExtractionMode.SIGNATURE_ONLY,
    }
    return mapping.get(mode_str, ExtractionMode.FULL_MODULE)


def semantic_level_from_string(level_str: str) -> SemanticEnrichmentLevel:
    """Convert semantic level string to enum."""
    mapping = {
        "none": SemanticEnrichmentLevel.NONE,
        "basic": SemanticEnrichmentLevel.BASIC,
        "full": SemanticEnrichmentLevel.FULL,
    }
    return mapping.get(level_str, SemanticEnrichmentLevel.BASIC)


def write_output(
    ir: IRVersion,
    output: TextIO,
    format: str,
    verbose: bool = False,
) -> None:
    """Write IR to output in specified format."""
    data = ir.model_dump(mode="json", exclude_none=True)

    if format == "json":
        json.dump(data, output, indent=2)
        output.write("\n")
    else:  # yaml
        yaml.dump(
            data,
            output,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )


def validate_source(extractor: PythonExtractor, source: str, path: str) -> int:
    """Validate source and print issues."""
    gaps = extractor.validate_source(source, path)

    if not gaps:
        print(f"OK: {path} - No issues detected")
        return 0

    print(f"Issues found in {path}:")
    for gap in gaps:
        severity = gap.severity.value.upper()
        print(f"  [{severity}] Line {gap.location}: {gap.description}")
        if gap.suggested_mitigations:
            for mitigation in gap.suggested_mitigations:
                print(f"    -> {mitigation}")

    return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Check input file exists
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    if not args.file.is_file():
        print(f"Error: Not a file: {args.file}", file=sys.stderr)
        return 1

    # Read source
    try:
        source = args.file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Create extractor
    extractor = PythonExtractor()

    # Validation mode
    if args.validate:
        return validate_source(extractor, source, str(args.file))

    # Build configuration
    semantic_level = SemanticEnrichmentLevel.NONE
    if args.enrich or args.semantic_level != "none":
        semantic_level = semantic_level_from_string(args.semantic_level)

    config = ExtractConfig(
        mode=mode_from_string(args.mode),
        include_layer0=args.include_layer0,
        semantic_level=semantic_level,
        resolve_imports=args.resolve_imports,
        project_root=args.project_root,
    )

    # Extract
    try:
        if args.verbose:
            print(f"Extracting: {args.file}", file=sys.stderr)
            print(f"  Mode: {config.mode.value}", file=sys.stderr)
            print(f"  Semantic: {config.semantic_level.value}", file=sys.stderr)

        ir = extractor.extract(source, str(args.file), config)

        if args.verbose:
            print(f"  Functions: {len(ir.functions)}", file=sys.stderr)
            print(f"  Types: {len(ir.types)}", file=sys.stderr)
            print(f"  Gaps: {len(ir.gaps)}", file=sys.stderr)

    except Exception as e:
        print(f"Extraction error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Output
    try:
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                write_output(ir, f, args.format, args.verbose)
            if not args.quiet:
                print(f"Wrote: {args.output}", file=sys.stderr)
        else:
            write_output(ir, sys.stdout, args.format, args.verbose)

    except Exception as e:
        print(f"Output error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
