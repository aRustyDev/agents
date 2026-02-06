"""CLI entry point for IR Query.

Usage:
    python -m ir_query patterns python rust
    python -m ir_query gaps python rust
    python -m ir_query store file.ir.yaml
    python -m ir_query profile python
    python -m ir_query taxonomy
    python -m ir_query stats

Commands:
    patterns    Get patterns for a language pair conversion
    gaps        Get semantic gaps between languages
    decisions   Get decision points for human review
    profile     Get language profile information
    taxonomy    Show language family taxonomy
    store       Store an IR file in the database
    retrieve    Retrieve an IR by ID
    stats       Show database statistics
    search      Full-text search of patterns
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Find project root for default database path
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "convert-skills.db"


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ir-query",
        description="Query interface for IR-related data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Database path (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--format",
        choices=["json", "human", "compact"],
        default="human",
        help="Output format (default: human)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # patterns command
    patterns_parser = subparsers.add_parser(
        "patterns",
        help="Get patterns for a language pair conversion",
    )
    patterns_parser.add_argument("source", help="Source language")
    patterns_parser.add_argument("target", help="Target language")
    patterns_parser.add_argument(
        "--type",
        dest="pattern_type",
        help="Filter by pattern type (type_mapping, idiom, gap, error, concurrency)",
    )
    patterns_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum results (default: 50)",
    )

    # gaps command
    gaps_parser = subparsers.add_parser(
        "gaps",
        help="Get semantic gaps between languages",
    )
    gaps_parser.add_argument("source", help="Source language")
    gaps_parser.add_argument("target", help="Target language")
    gaps_parser.add_argument(
        "--category",
        help="Filter by gap category",
    )
    gaps_parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        help="Filter by severity",
    )
    gaps_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum results (default: 50)",
    )

    # decisions command
    decisions_parser = subparsers.add_parser(
        "decisions",
        help="Get decision points requiring human input",
    )
    decisions_parser.add_argument("source", help="Source language")
    decisions_parser.add_argument("target", help="Target language")
    decisions_parser.add_argument(
        "--limit",
        type=int,
        help="Maximum results",
    )

    # profile command
    profile_parser = subparsers.add_parser(
        "profile",
        help="Get language profile information",
    )
    profile_parser.add_argument("language", help="Language name")

    # taxonomy command
    subparsers.add_parser(
        "taxonomy",
        help="Show language family taxonomy",
    )

    # store command
    store_parser = subparsers.add_parser(
        "store",
        help="Store an IR file in the database",
    )
    store_parser.add_argument("file", type=Path, help="IR file to store (YAML or JSON)")
    store_parser.add_argument(
        "--language",
        help="Override source language",
    )

    # retrieve command
    retrieve_parser = subparsers.add_parser(
        "retrieve",
        help="Retrieve an IR by ID",
    )
    retrieve_parser.add_argument("id", type=int, help="IR version ID")

    # stats command
    subparsers.add_parser(
        "stats",
        help="Show database statistics",
    )

    # search command
    search_parser = subparsers.add_parser(
        "search",
        help="Full-text search of patterns",
    )
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--source",
        help="Filter by source language",
    )
    search_parser.add_argument(
        "--target",
        help="Filter by target language",
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum results (default: 10)",
    )

    return parser


def format_output(
    data: Any,
    output_format: str,
    use_color: bool = True,
) -> str:
    """Format output data for display.

    Args:
        data: Data to format.
        output_format: Format type (json, human, compact).
        use_color: Whether to use ANSI colors.

    Returns:
        Formatted string.
    """
    if output_format == "json":
        return json.dumps(data, indent=2, default=str)

    if output_format == "compact":
        return json.dumps(data, separators=(",", ":"), default=str)

    # Human-readable format
    if isinstance(data, list):
        if not data:
            return "No results found."

        lines = []
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                lines.append(f"\n--- Result {i} ---")
                for key, value in item.items():
                    if value is not None:
                        lines.append(f"  {key}: {value}")
            else:
                lines.append(str(item))
        return "\n".join(lines)

    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"\n{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"\n{key}: ({len(value)} items)")
                for item in value[:10]:  # Show first 10
                    if isinstance(item, dict):
                        lines.append(f"  - {item}")
                    else:
                        lines.append(f"  - {item}")
                if len(value) > 10:
                    lines.append(f"  ... and {len(value) - 10} more")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    return str(data)


def cmd_patterns(args: argparse.Namespace) -> int:
    """Handle patterns command."""
    from .connection import DatabaseConnection, DatabaseError
    from .queries import IRQueryInterface

    try:
        with DatabaseConnection(args.db) as conn:
            query = IRQueryInterface(conn)
            results = query.get_patterns_for_conversion(
                args.source,
                args.target,
                pattern_type=args.pattern_type,
                limit=args.limit,
            )

            use_color = not args.no_color and sys.stdout.isatty()
            print(format_output(results, args.format, use_color))
            return 0

    except DatabaseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_gaps(args: argparse.Namespace) -> int:
    """Handle gaps command."""
    from .connection import DatabaseConnection, DatabaseError
    from .queries import IRQueryInterface

    try:
        with DatabaseConnection(args.db) as conn:
            query = IRQueryInterface(conn)
            results = query.get_gap_patterns(
                args.source,
                args.target,
                gap_category=args.category,
                severity=args.severity,
                limit=args.limit,
            )

            use_color = not args.no_color and sys.stdout.isatty()
            print(format_output(results, args.format, use_color))
            return 0

    except DatabaseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_decisions(args: argparse.Namespace) -> int:
    """Handle decisions command."""
    from .connection import DatabaseConnection, DatabaseError
    from .queries import IRQueryInterface

    try:
        with DatabaseConnection(args.db) as conn:
            query = IRQueryInterface(conn)
            results = query.get_decision_points(
                args.source,
                args.target,
                limit=args.limit,
            )

            use_color = not args.no_color and sys.stdout.isatty()
            print(format_output(results, args.format, use_color))
            return 0

    except DatabaseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_profile(args: argparse.Namespace) -> int:
    """Handle profile command."""
    from .connection import DatabaseConnection, DatabaseError
    from .queries import IRQueryInterface

    try:
        with DatabaseConnection(args.db) as conn:
            query = IRQueryInterface(conn)
            result = query.get_language_profile(args.language)

            if result is None:
                print(f"Language not found: {args.language}", file=sys.stderr)
                return 1

            use_color = not args.no_color and sys.stdout.isatty()
            print(format_output(result, args.format, use_color))
            return 0

    except DatabaseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_taxonomy(args: argparse.Namespace) -> int:
    """Handle taxonomy command."""
    from .connection import DatabaseConnection, DatabaseError
    from .queries import IRQueryInterface

    try:
        with DatabaseConnection(args.db) as conn:
            query = IRQueryInterface(conn)
            result = query.get_family_taxonomy()

            use_color = not args.no_color and sys.stdout.isatty()
            print(format_output(result, args.format, use_color))
            return 0

    except DatabaseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_store(args: argparse.Namespace) -> int:
    """Handle store command."""
    import yaml

    from .connection import DatabaseConnection, DatabaseError
    from .storage import IRStorage

    ir_file = args.file
    if not ir_file.exists():
        print(f"File not found: {ir_file}", file=sys.stderr)
        return 1

    # Load IR file
    try:
        content = ir_file.read_text(encoding="utf-8")
        if ir_file.suffix in (".yaml", ".yml"):
            ir_data = yaml.safe_load(content)
        else:
            ir_data = json.loads(content)
    except Exception as e:
        print(f"Failed to parse file: {e}", file=sys.stderr)
        return 1

    try:
        with DatabaseConnection(args.db) as conn:
            storage = IRStorage(conn)
            ir_id = storage.store(
                ir_data,
                metadata={
                    "source_file": str(ir_file),
                    "source_language": args.language,
                },
            )

            print(f"Stored IR with ID: {ir_id}")
            return 0

    except DatabaseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_retrieve(args: argparse.Namespace) -> int:
    """Handle retrieve command."""
    from .connection import DatabaseConnection, DatabaseError
    from .storage import IRStorage

    try:
        with DatabaseConnection(args.db) as conn:
            storage = IRStorage(conn)
            result = storage.retrieve(args.id)

            if result is None:
                print(f"IR not found: {args.id}", file=sys.stderr)
                return 1

            use_color = not args.no_color and sys.stdout.isatty()
            print(format_output(result, args.format, use_color))
            return 0

    except DatabaseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_stats(args: argparse.Namespace) -> int:
    """Handle stats command."""
    from .connection import DatabaseConnection, DatabaseError
    from .patterns import PatternRepository
    from .storage import IRStorage

    try:
        with DatabaseConnection(args.db) as conn:
            # Get pattern statistics
            pattern_repo = PatternRepository(conn)
            pattern_stats = pattern_repo.get_pattern_statistics()

            # Get storage statistics
            storage = IRStorage(conn)
            storage_stats = storage.get_statistics()

            result = {
                "patterns": pattern_stats,
                "storage": storage_stats,
            }

            use_color = not args.no_color and sys.stdout.isatty()
            print(format_output(result, args.format, use_color))
            return 0

    except DatabaseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_search(args: argparse.Namespace) -> int:
    """Handle search command."""
    from .connection import DatabaseConnection, DatabaseError
    from .patterns import PatternRepository

    try:
        with DatabaseConnection(args.db) as conn:
            repo = PatternRepository(conn)
            results = repo.search_patterns(
                args.query,
                limit=args.limit,
                source_lang=args.source,
                target_lang=args.target,
            )

            use_color = not args.no_color and sys.stdout.isatty()
            print(format_output(results, args.format, use_color))
            return 0

    except DatabaseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


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

    command_handlers = {
        "patterns": cmd_patterns,
        "gaps": cmd_gaps,
        "decisions": cmd_decisions,
        "profile": cmd_profile,
        "taxonomy": cmd_taxonomy,
        "store": cmd_store,
        "retrieve": cmd_retrieve,
        "stats": cmd_stats,
        "search": cmd_search,
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
