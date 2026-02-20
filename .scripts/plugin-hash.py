#!/usr/bin/env python3
"""
Compute content-addressed hashes for plugin components.

Usage:
    uv run python .scripts/plugin-hash.py <path>
    uv run python .scripts/plugin-hash.py <path> --verify <expected-hash>
    uv run python .scripts/plugin-hash.py --verify-sources <plugin-dir>
    uv run python .scripts/plugin-hash.py --help

Output format: sha256:<hex>

For directories, all files are hashed recursively in sorted order
to ensure deterministic output.
"""

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path


def hash_file(path: Path) -> str:
    """Compute SHA256 hash of a single file."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_directory(path: Path) -> str:
    """
    Compute SHA256 hash of a directory.

    All files are processed in sorted order (by relative path) for determinism.
    The hash includes both file paths and contents.
    """
    hasher = hashlib.sha256()

    # Collect all files, sorted by relative path for determinism
    files = sorted(path.rglob("*"))

    for file_path in files:
        if file_path.is_file():
            # Include relative path in hash for structure awareness
            rel_path = file_path.relative_to(path)
            hasher.update(str(rel_path).encode("utf-8"))
            hasher.update(b"\x00")  # Null separator

            # Include file content
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            hasher.update(b"\x00")  # Null separator between files

    return hasher.hexdigest()


def compute_hash(path: Path) -> str:
    """Compute hash for a file or directory."""
    if path.is_file():
        return hash_file(path)
    elif path.is_dir():
        return hash_directory(path)
    else:
        raise ValueError(f"Path does not exist: {path}")


def format_hash(hex_hash: str) -> str:
    """Format hash in standard output format."""
    return f"sha256:{hex_hash}"


def parse_hash(hash_str: str) -> str:
    """Parse hash string, stripping prefix if present."""
    if hash_str.startswith("sha256:"):
        return hash_str[7:]
    return hash_str


@dataclass
class SourceStatus:
    """Status of a source component."""

    local_path: str
    source_path: str
    expected_hash: str | None
    actual_hash: str | None
    forked: bool = False
    missing: bool = False

    @property
    def matches(self) -> bool:
        """True if hash matches or component is forked."""
        if self.forked:
            return True
        if self.missing:
            return False
        if self.expected_hash is None:
            return False  # No hash stored (legacy format)
        return self.expected_hash == self.actual_hash

    @property
    def status(self) -> str:
        """Human-readable status."""
        if self.forked:
            return "forked"
        if self.missing:
            return "missing"
        if self.expected_hash is None:
            return "no-hash"
        if self.matches:
            return "fresh"
        return "stale"


def verify_sources(plugin_dir: Path) -> list[SourceStatus]:
    """
    Verify all sources in a plugin's plugin.sources.json.

    Returns a list of SourceStatus objects for each source.
    """
    sources_file = plugin_dir / ".claude-plugin" / "plugin.sources.json"

    if not sources_file.exists():
        raise ValueError(f"No plugin.sources.json found at {sources_file}")

    with sources_file.open() as f:
        data = json.load(f)

    sources = data.get("sources", {})
    results = []

    for local_path, source_def in sources.items():
        # Handle both legacy (string) and extended (object) formats
        if isinstance(source_def, str):
            # Legacy format: just a path, no hash
            source_path = source_def
            expected_hash = None
            forked = False
        else:
            # Extended format: object with source, hash, forked
            source_path = source_def.get("source", "")
            expected_hash = source_def.get("hash")
            if expected_hash:
                expected_hash = parse_hash(expected_hash)
            forked = source_def.get("forked", False)

        # Check if source exists and compute hash
        source = Path(source_path)
        if not source.exists():
            results.append(
                SourceStatus(
                    local_path=local_path,
                    source_path=source_path,
                    expected_hash=expected_hash,
                    actual_hash=None,
                    forked=forked,
                    missing=True,
                )
            )
        else:
            actual_hash = compute_hash(source)
            results.append(
                SourceStatus(
                    local_path=local_path,
                    source_path=source_path,
                    expected_hash=expected_hash,
                    actual_hash=actual_hash,
                    forked=forked,
                    missing=False,
                )
            )

    return results


def _print_verify_sources_json(results: list[SourceStatus]) -> None:
    """Print verify-sources results in JSON format."""
    output = [
        {
            "local_path": r.local_path,
            "source_path": r.source_path,
            "expected_hash": format_hash(r.expected_hash) if r.expected_hash else None,
            "actual_hash": format_hash(r.actual_hash) if r.actual_hash else None,
            "status": r.status,
        }
        for r in results
    ]
    print(json.dumps(output, indent=2))


def _print_verify_sources_text(results: list[SourceStatus], plugin_name: str) -> int:
    """Print verify-sources results in text format. Returns exit code."""
    status_icons = {"fresh": "✓", "stale": "⚠", "missing": "✗", "forked": "○", "no-hash": "?"}
    counts = {s: len([r for r in results if r.status == s]) for s in status_icons}

    print(f"Plugin: {plugin_name}\n")
    for r in results:
        print(f"  {status_icons.get(r.status, '?')} {r.local_path} ({r.status})")

    print(
        f"\nSummary: {counts['fresh']} fresh, {counts['stale']} stale, "
        f"{counts['forked']} forked, {counts['no-hash']} no-hash, {counts['missing']} missing"
    )

    if counts["stale"] or counts["missing"]:
        return 1
    if counts["no-hash"]:
        return 2  # Warning: legacy format
    return 0


def _handle_verify_sources(args: argparse.Namespace) -> int:
    """Handle --verify-sources mode. Returns exit code."""
    results = verify_sources(args.verify_sources)
    if args.json:
        _print_verify_sources_json(results)
        return 0
    return _print_verify_sources_text(results, args.verify_sources.name)


def _handle_hash_mode(args: argparse.Namespace) -> int:
    """Handle hash/verify mode. Returns exit code."""
    hex_hash = compute_hash(args.path)

    if args.verify:
        expected = parse_hash(args.verify)
        if hex_hash == expected:
            if not args.quiet:
                print(f"✓ Hash matches: {format_hash(hex_hash)}")
            return 0
        print("✗ Hash mismatch!", file=sys.stderr)
        print(f"  Expected: {format_hash(expected)}", file=sys.stderr)
        print(f"  Actual:   {format_hash(hex_hash)}", file=sys.stderr)
        return 1

    print(hex_hash if args.hex_only else format_hash(hex_hash))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Build argument parser."""
    parser = argparse.ArgumentParser(
        description="Compute content-addressed hashes for plugin components.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python .scripts/plugin-hash.py context/commands/add-formula.md
  uv run python .scripts/plugin-hash.py --verify-sources context/plugins/homebrew-dev
        """,
    )
    parser.add_argument("path", type=Path, nargs="?", help="File or directory to hash")
    parser.add_argument(
        "--verify", type=str, metavar="HASH", help="Verify path matches expected hash"
    )
    parser.add_argument(
        "--verify-sources", type=Path, metavar="PLUGIN_DIR", help="Verify all sources in a plugin"
    )
    parser.add_argument(
        "--hex-only", action="store_true", help="Output just the hex hash without sha256: prefix"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress output on successful verification"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON format (for --verify-sources)"
    )
    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.verify_sources:
            sys.exit(_handle_verify_sources(args))

        if not args.path:
            parser.error("path is required unless using --verify-sources")

        sys.exit(_handle_hash_mode(args))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
