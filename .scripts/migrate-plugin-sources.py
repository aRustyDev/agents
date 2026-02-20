#!/usr/bin/env python3
"""
Migrate plugin.sources.json to extended format with hashes.

Usage:
    uv run python .scripts/migrate-plugin-sources.py <plugin-dir>
    uv run python .scripts/migrate-plugin-sources.py --all
    uv run python .scripts/migrate-plugin-sources.py --check

Examples:
    uv run python .scripts/migrate-plugin-sources.py context/plugins/homebrew-dev
    uv run python .scripts/migrate-plugin-sources.py --all --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# Constants
PLUGINS_DIR = Path("context/plugins")
HASH_PREFIX = "sha256:"


def hash_file(path: Path) -> str:
    """Compute SHA256 hash of a single file."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_directory(path: Path) -> str:
    """Compute SHA256 hash of a directory (sorted, deterministic)."""
    hasher = hashlib.sha256()
    for file_path in sorted(path.rglob("*")):
        if file_path.is_file():
            rel_path = file_path.relative_to(path)
            hasher.update(str(rel_path).encode("utf-8"))
            hasher.update(b"\x00")
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            hasher.update(b"\x00")
    return hasher.hexdigest()


def compute_hash(path: Path) -> str:
    """Compute hash for a file or directory."""
    if path.is_file():
        return hash_file(path)
    if path.is_dir():
        return hash_directory(path)
    raise ValueError(f"Path does not exist: {path}")


def format_hash(hex_hash: str) -> str:
    """Format hash with prefix."""
    return f"{HASH_PREFIX}{hex_hash}"


@dataclass
class MigrationResult:
    """Result of migrating a plugin."""

    plugin_name: str
    converted: int = 0
    already_extended: int = 0
    missing_sources: list[str] | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.missing_sources is None:
            self.missing_sources = []

    @property
    def success(self) -> bool:
        """True if migration succeeded."""
        return self.error is None


def is_legacy_format(source_def: str | dict) -> bool:
    """Check if source definition is in legacy format (string path)."""
    return isinstance(source_def, str)


def is_list_format(sources: dict | list) -> bool:
    """Check if sources is in list format (planning, not buildable)."""
    return isinstance(sources, list)


def migrate_plugin(plugin_dir: Path, *, dry_run: bool = False) -> MigrationResult:
    """
    Migrate a plugin's sources.json to extended format.

    Args:
        plugin_dir: Path to plugin directory
        dry_run: If True, don't write changes

    Returns:
        MigrationResult with migration status
    """
    plugin_name = plugin_dir.name
    result = MigrationResult(plugin_name=plugin_name)

    sources_file = plugin_dir / ".claude-plugin" / "plugin.sources.json"
    if not sources_file.exists():
        result.error = "No plugin.sources.json found"
        return result

    try:
        with sources_file.open() as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result.error = f"Invalid JSON: {e}"
        return result

    sources = data.get("sources", {})

    # Skip list format (planning/roadmap plugins)
    if is_list_format(sources):
        result.error = "Plugin uses list format (planning), not buildable"
        return result

    # Process each source
    for local_path, source_def in sources.items():
        if is_legacy_format(source_def):
            # Convert legacy format to extended format
            source_path = source_def
            sources[local_path] = {"source": source_path}
            entry = sources[local_path]
            result.converted += 1
        else:
            entry = source_def
            result.already_extended += 1

        # Compute hash if not present or if forked
        if not entry.get("forked", False):
            source_path = entry.get("source", "")
            source = Path(source_path)
            if source.exists():
                new_hash = compute_hash(source)
                entry["hash"] = format_hash(new_hash)
            else:
                result.missing_sources.append(local_path)

    # Write updated file if any changes made
    has_changes = result.converted > 0 or result.already_extended > 0
    if not dry_run and has_changes:
        with sources_file.open("w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    return result


def list_plugins() -> list[Path]:
    """List all plugin directories with plugin.sources.json."""
    plugins = []
    for plugin_dir in PLUGINS_DIR.iterdir():
        if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
            sources_file = plugin_dir / ".claude-plugin" / "plugin.sources.json"
            if sources_file.exists():
                plugins.append(plugin_dir)
    return sorted(plugins)


def check_migration_status() -> None:
    """Check migration status of all plugins."""
    plugins = list_plugins()
    if not plugins:
        print("No plugins found")
        return

    print(f"Checking {len(plugins)} plugins...\n")

    legacy_count = 0
    extended_count = 0
    list_count = 0
    error_count = 0

    for plugin_dir in plugins:
        sources_file = plugin_dir / ".claude-plugin" / "plugin.sources.json"
        try:
            with sources_file.open() as f:
                data = json.load(f)
            sources = data.get("sources", {})

            if is_list_format(sources):
                print(f"  ○ {plugin_dir.name}: list format (planning)")
                list_count += 1
            elif any(is_legacy_format(s) for s in sources.values()):
                legacy = sum(1 for s in sources.values() if is_legacy_format(s))
                print(f"  ⚠ {plugin_dir.name}: {legacy} legacy, needs migration")
                legacy_count += 1
            else:
                # Check if all have hashes
                missing_hash = sum(1 for s in sources.values() if not s.get("hash"))
                if missing_hash:
                    print(f"  ⚠ {plugin_dir.name}: {missing_hash} missing hashes")
                    legacy_count += 1
                else:
                    print(f"  ✓ {plugin_dir.name}: extended format")
                    extended_count += 1
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ✗ {plugin_dir.name}: error ({e})")
            error_count += 1

    print(
        f"\nSummary: {extended_count} extended, {legacy_count} legacy, "
        f"{list_count} list, {error_count} error"
    )

    if legacy_count > 0:
        print("\nRun with --all to migrate all plugins")


def cmd_migrate(args: argparse.Namespace) -> int:  # noqa: PLR0911, PLR0912
    """Migrate command handler."""
    if args.check:
        check_migration_status()
        return 0

    if args.all:
        plugins = list_plugins()
        if not plugins:
            print("No plugins found")
            return 0

        print(f"Migrating {len(plugins)} plugins...\n")
        failed = []

        for plugin_dir in plugins:
            result = migrate_plugin(plugin_dir, dry_run=args.dry_run)
            if result.success:
                status = "dry-run" if args.dry_run else "migrated"
                if result.converted > 0:
                    print(f"  ✓ {result.plugin_name}: {result.converted} converted ({status})")
                elif result.already_extended > 0:
                    print(f"  ○ {result.plugin_name}: already extended")
                else:
                    print(f"  ○ {result.plugin_name}: no sources")
                if result.missing_sources:
                    print(f"      ⚠ Missing: {', '.join(result.missing_sources)}")
            else:
                print(f"  ✗ {result.plugin_name}: {result.error}")
                failed.append(result.plugin_name)

        print(
            f"\n{'✓' if not failed else '✗'} {len(plugins) - len(failed)}/{len(plugins)} plugins OK"
        )
        if failed:
            print(f"\nFailed: {', '.join(failed)}")
            return 1
        return 0

    # Single plugin migration
    plugin_dir = Path(args.plugin_dir)
    if not plugin_dir.exists():
        print(f"Error: Plugin directory not found: {plugin_dir}", file=sys.stderr)
        return 1

    result = migrate_plugin(plugin_dir, dry_run=args.dry_run)

    if result.success:
        status = "dry-run" if args.dry_run else "migrated"
        print(f"Plugin: {result.plugin_name}")
        print(f"  Converted: {result.converted}")
        print(f"  Already extended: {result.already_extended}")
        if result.missing_sources:
            print(f"  Missing sources: {', '.join(result.missing_sources)}")
        print(f"\n✓ Migration {status}")
        return 0
    else:
        print(f"Error: {result.error}", file=sys.stderr)
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate plugin.sources.json to extended format with hashes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "plugin_dir",
        nargs="?",
        help="Plugin directory to migrate",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Migrate all plugins",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check migration status without making changes",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args(argv)

    if not args.plugin_dir and not args.all and not args.check:
        parser.error("Either plugin_dir, --all, or --check is required")

    return cmd_migrate(args)


if __name__ == "__main__":
    sys.exit(main())
