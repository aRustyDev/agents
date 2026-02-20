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


def update_source_hash(plugin_dir: Path, local_path: str) -> str:
    """
    Update the hash for a specific source in plugin.sources.json.

    Returns the new hash.
    """
    sources_file = plugin_dir / ".claude-plugin" / "plugin.sources.json"

    if not sources_file.exists():
        raise ValueError(f"No plugin.sources.json found at {sources_file}")

    with sources_file.open() as f:
        data = json.load(f)

    sources = data.get("sources", {})
    if local_path not in sources:
        raise ValueError(f"Component '{local_path}' not found in plugin.sources.json")

    source_def = sources[local_path]

    # Get source path from either format
    if isinstance(source_def, str):
        source_path = source_def
        # Convert to extended format
        sources[local_path] = {"source": source_path}
        source_def = sources[local_path]
    else:
        source_path = source_def.get("source", "")

    # Compute new hash
    source = Path(source_path)
    if not source.exists():
        raise ValueError(f"Source path does not exist: {source_path}")

    new_hash = compute_hash(source)
    source_def["hash"] = format_hash(new_hash)

    # Write back
    with sources_file.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    return new_hash


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


def _prompt_choice(valid_choices: dict[str, str]) -> str:
    """Prompt user for choice. Returns the action key (u/s/a) or raises KeyboardInterrupt."""
    choice_str = ", ".join(f"[{k.upper()}]{v}" for k, v in valid_choices.items())
    while True:
        choice = input(f"  {choice_str}? ").strip().lower()
        if choice in valid_choices or choice in [v.lower() for v in valid_choices.values()]:
            return choice[0]  # Return first letter
        print(f"  Invalid choice. Enter {', '.join(valid_choices.keys()).upper()}.")


def _handle_stale_source(plugin_dir: Path, r: SourceStatus) -> tuple[str, bool]:
    """Handle a stale source. Returns (action, updated)."""
    print(f"\n⚠ Stale: {r.local_path}")
    print(f"  Source: {r.source_path}")
    print(f"  Expected: {format_hash(r.expected_hash) if r.expected_hash else 'none'}")
    print(f"  Actual:   {format_hash(r.actual_hash) if r.actual_hash else 'none'}")

    choice = _prompt_choice({"u": "pdate hash", "s": "kip component", "a": "bort build"})
    if choice == "u":
        update_source_hash(plugin_dir, r.local_path)
        print(f"  ✓ Hash updated for {r.local_path}")
        return "continue", True
    if choice == "s":
        print(f"  → Skipping {r.local_path}")
        return "skip", False
    return "abort", False


def _handle_missing_source(r: SourceStatus) -> str:
    """Handle a missing source. Returns 'skip' or 'abort'."""
    print(f"\n✗ Missing: {r.local_path}")
    print(f"  Source: {r.source_path}")

    choice = _prompt_choice({"s": "kip component", "a": "bort build"})
    if choice == "s":
        print(f"  → Skipping {r.local_path}")
        return "skip"
    return "abort"


def _handle_interactive_verify(
    plugin_dir: Path, results: list[SourceStatus]
) -> tuple[int, list[str]]:
    """Handle interactive verification with prompts. Returns (exit_code, skip_list)."""
    skip_list: list[str] = []
    updated = False

    for r in results:
        if r.status == "stale":
            action, was_updated = _handle_stale_source(plugin_dir, r)
            updated = updated or was_updated
            if action == "skip":
                skip_list.append(r.local_path)
            elif action == "abort":
                return 1, []
        elif r.status == "missing":
            action = _handle_missing_source(r)
            if action == "skip":
                skip_list.append(r.local_path)
            elif action == "abort":
                return 1, []

    if updated:
        print("\n✓ plugin.sources.json updated")

    return 0, skip_list


def _handle_verify_sources(args: argparse.Namespace) -> int:
    """Handle --verify-sources mode. Returns exit code."""
    results = verify_sources(args.verify_sources)
    if args.json:
        _print_verify_sources_json(results)
        return 0
    if args.interactive:
        exit_code, skip_list = _handle_interactive_verify(args.verify_sources, results)
        if skip_list:
            print(f"\nSkipped: {', '.join(skip_list)}")
        return exit_code
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
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode for stale sources"
    )
    parser.add_argument(
        "--update-hash",
        type=str,
        metavar="COMPONENT",
        help="Update hash for a specific component (requires --verify-sources)",
    )
    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    try:
        # Update hash for single component
        if args.update_hash:
            if not args.verify_sources:
                parser.error("--update-hash requires --verify-sources")
            new_hash = update_source_hash(args.verify_sources, args.update_hash)
            print(f"✓ Updated {args.update_hash}: {format_hash(new_hash)}")
            sys.exit(0)

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
