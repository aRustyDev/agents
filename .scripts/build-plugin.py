#!/usr/bin/env python3
"""
Plugin build system with content-addressed hashing.

Usage:
    uv run python .scripts/build-plugin.py build <name> [options]
    uv run python .scripts/build-plugin.py check <name>
    uv run python .scripts/build-plugin.py update <name>
    uv run python .scripts/build-plugin.py hash <path>

Commands:
    build   Build a plugin (copy sources, verify hashes)
    check   Verify plugin hashes without building
    update  Update all hashes in plugin.sources.json
    hash    Compute hash for a file or directory
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# Constants
PLUGINS_DIR = Path("context/plugins")
HASH_PREFIX = "sha256:"


# =============================================================================
# Hash computation
# =============================================================================


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


def parse_hash(hash_str: str) -> str:
    """Strip hash prefix if present."""
    if hash_str.startswith(HASH_PREFIX):
        return hash_str[len(HASH_PREFIX) :]
    return hash_str


# =============================================================================
# Source status
# =============================================================================


@dataclass
class SourceStatus:
    """Status of a source component."""

    local_path: str
    source_path: str
    expected_hash: str | None
    actual_hash: str | None
    forked: bool = False
    forked_at: str | None = None
    missing: bool = False

    @property
    def status(self) -> str:
        """Human-readable status."""
        if self.forked:
            return "forked"
        if self.missing:
            return "missing"
        if self.expected_hash is None:
            return "no-hash"
        if self.expected_hash == self.actual_hash:
            return "fresh"
        return "stale"

    @property
    def icon(self) -> str:
        """Status icon."""
        return {"fresh": "✓", "stale": "⚠", "missing": "✗", "forked": "○", "no-hash": "?"}.get(
            self.status, "?"
        )


# =============================================================================
# Build result
# =============================================================================


@dataclass
class BuildResult:
    """Result of a build operation."""

    plugin_name: str
    sources: list[SourceStatus] = field(default_factory=list)
    copied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """True if build succeeded."""
        return len(self.errors) == 0

    def print_summary(self) -> None:
        """Print build summary."""
        print(f"\nBuilding plugin: {self.plugin_name}\n")
        print("Components:")
        for s in self.sources:
            print(f"  {s.icon} {s.local_path} ({s.status})")

        print("\nActions:")
        if self.updated:
            print(f"  Updated: {len(self.updated)} component(s)")
        if self.skipped:
            print(f"  Skipped: {len(self.skipped)} forked")
        fresh = [s for s in self.sources if s.status == "fresh"]
        if fresh:
            print(f"  Fresh: {len(fresh)} component(s)")
        if self.copied:
            print(f"  Copied: {len(self.copied)} component(s)")

        if self.errors:
            print("\nErrors:")
            for err in self.errors:
                print(f"  ✗ {err}")
            print("\n✗ Build failed")
        else:
            print("\n✓ Plugin built successfully")


# =============================================================================
# Plugin operations
# =============================================================================


class Plugin:
    """Plugin manager."""

    def __init__(self, name: str):
        self.name = name
        self.dir = PLUGINS_DIR / name
        self.sources_file = self.dir / ".claude-plugin" / "plugin.sources.json"

    def exists(self) -> bool:
        """Check if plugin exists."""
        return self.sources_file.exists()

    def load_sources(self) -> dict:
        """Load plugin.sources.json."""
        if not self.sources_file.exists():
            raise ValueError(f"Plugin not found: {self.name}")
        with self.sources_file.open() as f:
            return json.load(f)

    def save_sources(self, data: dict) -> None:
        """Save plugin.sources.json."""
        with self.sources_file.open("w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    def get_source_status(self, local_path: str, source_def: str | dict) -> SourceStatus:
        """Get status for a single source."""
        if isinstance(source_def, str):
            source_path = source_def
            expected_hash = None
            forked = False
            forked_at = None
        else:
            source_path = source_def.get("source", "")
            expected_hash = source_def.get("hash")
            if expected_hash:
                expected_hash = parse_hash(expected_hash)
            forked = source_def.get("forked", False)
            forked_at = source_def.get("forked_at")

        source = Path(source_path)
        if not source.exists():
            return SourceStatus(
                local_path=local_path,
                source_path=source_path,
                expected_hash=expected_hash,
                actual_hash=None,
                forked=forked,
                forked_at=forked_at,
                missing=True,
            )

        actual_hash = compute_hash(source)
        return SourceStatus(
            local_path=local_path,
            source_path=source_path,
            expected_hash=expected_hash,
            actual_hash=actual_hash,
            forked=forked,
            forked_at=forked_at,
        )

    def verify_sources(self) -> list[SourceStatus]:
        """Verify all sources."""
        data = self.load_sources()
        sources = data.get("sources", {})
        return [self.get_source_status(lp, sd) for lp, sd in sources.items()]

    def update_hash(self, local_path: str) -> str:
        """Update hash for a single component."""
        data = self.load_sources()
        sources = data.get("sources", {})

        if local_path not in sources:
            raise ValueError(f"Component not found: {local_path}")

        source_def = sources[local_path]
        if isinstance(source_def, str):
            source_path = source_def
            sources[local_path] = {"source": source_path}
            source_def = sources[local_path]
        else:
            source_path = source_def.get("source", "")

        source = Path(source_path)
        if not source.exists():
            raise ValueError(f"Source not found: {source_path}")

        new_hash = compute_hash(source)
        source_def["hash"] = format_hash(new_hash)
        self.save_sources(data)
        return new_hash

    def update_all_hashes(self) -> list[str]:
        """Update hashes for all components."""
        updated = []
        data = self.load_sources()
        sources = data.get("sources", {})

        for local_path, source_def in sources.items():
            # Convert legacy format to extended format
            if isinstance(source_def, str):
                source_path = source_def
                sources[local_path] = {"source": source_path}
            else:
                source_path = source_def.get("source", "")

            entry = sources[local_path]
            if entry.get("forked"):
                continue

            source = Path(source_path)
            if source.exists():
                new_hash = compute_hash(source)
                entry["hash"] = format_hash(new_hash)
                updated.append(local_path)

        self.save_sources(data)
        return updated

    def copy_source(self, local_path: str, source_path: str) -> None:
        """Copy a source to the plugin directory."""
        target = self.dir / local_path
        source = Path(source_path)

        target.parent.mkdir(parents=True, exist_ok=True)

        if source.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)

    def _handle_stale_interactive(self, stale: list[SourceStatus], result: BuildResult) -> bool:
        """Handle stale sources interactively. Returns False if aborted."""
        for s in stale:
            action = self._prompt_stale(s)
            if action == "update":
                self.update_hash(s.local_path)
                result.updated.append(s.local_path)
            elif action == "skip":
                result.skipped.append(s.local_path)
            elif action == "abort":
                result.errors.append("Build aborted by user")
                return False
        return True

    def _copy_all_sources(self, result: BuildResult) -> None:
        """Copy all non-skipped sources to plugin directory."""
        data = self.load_sources()
        sources = data.get("sources", {})
        for local_path, source_def in sources.items():
            if local_path in result.skipped:
                continue
            source_path = source_def if isinstance(source_def, str) else source_def.get("source")
            if source_path and Path(source_path).exists():
                self.copy_source(local_path, source_path)
                result.copied.append(local_path)

    def build(
        self,
        *,
        force: bool = False,
        check_only: bool = False,
        update_hashes: bool = False,
        interactive: bool = True,
    ) -> BuildResult:
        """Build the plugin."""
        result = BuildResult(plugin_name=self.name)
        result.sources = self.verify_sources()

        # Categorize sources by status
        statuses = ("stale", "missing", "no-hash", "forked")
        by_status = {s: [x for x in result.sources if x.status == s] for s in statuses}

        # Handle missing sources
        for s in by_status["missing"]:
            result.errors.append(f"Missing source: {s.source_path}")
        if result.errors and not force:
            return result

        # Handle stale sources
        stale = by_status["stale"]
        if stale and not force and not update_hashes:
            if check_only:
                result.errors.extend(f"Stale: {s.local_path}" for s in stale)
                return result
            if interactive:
                if not self._handle_stale_interactive(stale, result):
                    return result
            else:
                result.errors.extend(f"Stale: {s.local_path}" for s in stale)
                return result

        # Update hashes if requested
        if update_hashes or force:
            for s in stale + by_status["no-hash"]:
                if not s.forked and not s.missing:
                    self.update_hash(s.local_path)
                    result.updated.append(s.local_path)

        # Track forked components as skipped
        result.skipped.extend(s.local_path for s in by_status["forked"])

        if not check_only:
            self._copy_all_sources(result)

        return result

    def _prompt_stale(self, s: SourceStatus) -> str:
        """Prompt user for stale source action."""
        print(f"\n⚠ Stale: {s.local_path}")
        print(f"  Source: {s.source_path}")
        print(f"  Expected: {format_hash(s.expected_hash) if s.expected_hash else 'none'}")
        print(f"  Actual:   {format_hash(s.actual_hash) if s.actual_hash else 'none'}")

        while True:
            choice = input("  [U]pdate hash, [S]kip component, [A]bort build? ").strip().lower()
            if choice in ("u", "update"):
                return "update"
            if choice in ("s", "skip"):
                return "skip"
            if choice in ("a", "abort"):
                return "abort"
            print("  Invalid choice. Enter U, S, or A.")


# =============================================================================
# CLI commands
# =============================================================================


def cmd_build(args: argparse.Namespace) -> int:
    """Build command."""
    plugin = Plugin(args.name)
    if not plugin.exists():
        print(f"Error: Plugin not found: {args.name}", file=sys.stderr)
        return 1

    result = plugin.build(
        force=args.force,
        check_only=args.check_only,
        update_hashes=args.update_hashes,
        interactive=not args.force and not args.check_only and not args.update_hashes,
    )

    result.print_summary()
    return 0 if result.success else 1


def cmd_check(args: argparse.Namespace) -> int:
    """Check command."""
    plugin = Plugin(args.name)
    if not plugin.exists():
        print(f"Error: Plugin not found: {args.name}", file=sys.stderr)
        return 1

    sources = plugin.verify_sources()

    print(f"Plugin: {plugin.name}\n")
    for s in sources:
        print(f"  {s.icon} {s.local_path} ({s.status})")

    counts = {}
    for s in sources:
        counts[s.status] = counts.get(s.status, 0) + 1

    print(
        f"\nSummary: {counts.get('fresh', 0)} fresh, {counts.get('stale', 0)} stale, "
        f"{counts.get('forked', 0)} forked, {counts.get('no-hash', 0)} no-hash, "
        f"{counts.get('missing', 0)} missing"
    )

    if counts.get("stale", 0) or counts.get("missing", 0):
        return 1
    if counts.get("no-hash", 0):
        print("\n⚠ Warning: Plugin uses legacy format without hashes")
        return 0
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """Update command."""
    plugin = Plugin(args.name)
    if not plugin.exists():
        print(f"Error: Plugin not found: {args.name}", file=sys.stderr)
        return 1

    print(f"Updating hashes for {args.name}...")
    updated = plugin.update_all_hashes()

    for local_path in updated:
        print(f"  ✓ {local_path}")

    print(f"\n✓ Updated {len(updated)} component(s)")
    return 0


def cmd_hash(args: argparse.Namespace) -> int:
    """Hash command."""
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        return 1

    hex_hash = compute_hash(path)
    if args.hex_only:
        print(hex_hash)
    else:
        print(format_hash(hex_hash))
    return 0


# =============================================================================
# Main
# =============================================================================


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Plugin build system with content-addressed hashing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build command
    build_parser = subparsers.add_parser("build", help="Build a plugin")
    build_parser.add_argument("name", help="Plugin name")
    build_parser.add_argument(
        "--force", "-f", action="store_true", help="Force rebuild, update hashes"
    )
    build_parser.add_argument("--check-only", "-c", action="store_true", help="Verify hashes only")
    build_parser.add_argument(
        "--update-hashes", "-u", action="store_true", help="Update hashes without prompting"
    )
    build_parser.set_defaults(func=cmd_build)

    # check command
    check_parser = subparsers.add_parser("check", help="Verify plugin hashes")
    check_parser.add_argument("name", help="Plugin name")
    check_parser.set_defaults(func=cmd_check)

    # update command
    update_parser = subparsers.add_parser("update", help="Update all hashes")
    update_parser.add_argument("name", help="Plugin name")
    update_parser.set_defaults(func=cmd_update)

    # hash command
    hash_parser = subparsers.add_parser("hash", help="Compute hash for a path")
    hash_parser.add_argument("path", help="File or directory to hash")
    hash_parser.add_argument("--hex-only", action="store_true", help="Output hex only, no prefix")
    hash_parser.set_defaults(func=cmd_hash)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
