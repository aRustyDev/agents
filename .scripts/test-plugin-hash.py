#!/usr/bin/env python3
"""Test plugin hash computation."""

import json

# Import from plugin-hash module
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Can't import directly due to hyphen, use importlib
import importlib.util

spec = importlib.util.spec_from_file_location(
    "plugin_hash", Path(__file__).parent / "plugin-hash.py"
)
plugin_hash = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plugin_hash)


def test_hash_file():
    """Test hashing a single file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello, World!")
        f.flush()
        path = Path(f.name)

    try:
        hash1 = plugin_hash.hash_file(path)
        hash2 = plugin_hash.hash_file(path)

        assert hash1 == hash2, "Hash should be deterministic"
        assert len(hash1) == 64, "SHA256 hash should be 64 hex chars"
        print(f"✓ test_hash_file: {hash1[:16]}...")
    finally:
        path.unlink()


def test_hash_directory():
    """Test hashing a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create some files
        (tmppath / "a.txt").write_text("File A content")
        (tmppath / "b.txt").write_text("File B content")
        subdir = tmppath / "sub"
        subdir.mkdir()
        (subdir / "c.txt").write_text("File C content")

        hash1 = plugin_hash.hash_directory(tmppath)
        hash2 = plugin_hash.hash_directory(tmppath)

        assert hash1 == hash2, "Directory hash should be deterministic"
        assert len(hash1) == 64, "SHA256 hash should be 64 hex chars"
        print(f"✓ test_hash_directory: {hash1[:16]}...")


def test_hash_directory_order_independent():
    """Test that directory hash is order-independent (sorted)."""
    with (
        tempfile.TemporaryDirectory() as tmpdir1,
        tempfile.TemporaryDirectory() as tmpdir2,
    ):
        tmppath1 = Path(tmpdir1)
        tmppath2 = Path(tmpdir2)

        # Create files in different order
        (tmppath1 / "b.txt").write_text("B")
        (tmppath1 / "a.txt").write_text("A")

        (tmppath2 / "a.txt").write_text("A")
        (tmppath2 / "b.txt").write_text("B")

        hash1 = plugin_hash.hash_directory(tmppath1)
        hash2 = plugin_hash.hash_directory(tmppath2)

        assert hash1 == hash2, "Hash should be same regardless of creation order"
        print("✓ test_hash_directory_order_independent")


def test_hash_changes_with_content():
    """Test that hash changes when content changes."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Original content")
        f.flush()
        path = Path(f.name)

    try:
        hash1 = plugin_hash.hash_file(path)

        # Modify file
        path.write_text("Modified content")
        hash2 = plugin_hash.hash_file(path)

        assert hash1 != hash2, "Hash should change when content changes"
        print("✓ test_hash_changes_with_content")
    finally:
        path.unlink()


def test_format_hash():
    """Test hash formatting."""
    hex_hash = "abc123"
    formatted = plugin_hash.format_hash(hex_hash)
    assert formatted == "sha256:abc123"
    print("✓ test_format_hash")


def test_parse_hash():
    """Test hash parsing."""
    assert plugin_hash.parse_hash("sha256:abc123") == "abc123"
    assert plugin_hash.parse_hash("abc123") == "abc123"
    print("✓ test_parse_hash")


def test_verify_sources():
    """Test verify_sources with a mock plugin."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_dir = Path(tmpdir)
        claude_plugin_dir = plugin_dir / ".claude-plugin"
        claude_plugin_dir.mkdir()

        # Create a source file
        source_dir = plugin_dir / "sources"
        source_dir.mkdir()
        source_file = source_dir / "test.md"
        source_file.write_text("Test content")

        # Get actual hash
        actual_hash = plugin_hash.compute_hash(source_file)

        # Create plugin.sources.json with correct hash
        sources_json = {
            "sources": {
                "test.md": {
                    "source": str(source_file),
                    "hash": f"sha256:{actual_hash}",
                }
            }
        }
        (claude_plugin_dir / "plugin.sources.json").write_text(json.dumps(sources_json))

        results = plugin_hash.verify_sources(plugin_dir)
        assert len(results) == 1
        assert results[0].status == "fresh"
        print("✓ test_verify_sources (fresh)")

        # Modify source to make it stale
        source_file.write_text("Modified content")
        results = plugin_hash.verify_sources(plugin_dir)
        assert results[0].status == "stale"
        print("✓ test_verify_sources (stale)")


def test_verify_sources_legacy_format():
    """Test verify_sources with legacy format (no hashes)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_dir = Path(tmpdir)
        claude_plugin_dir = plugin_dir / ".claude-plugin"
        claude_plugin_dir.mkdir()

        # Create a source file
        source_dir = plugin_dir / "sources"
        source_dir.mkdir()
        source_file = source_dir / "test.md"
        source_file.write_text("Test content")

        # Create plugin.sources.json with legacy format (just path)
        sources_json = {"sources": {"test.md": str(source_file)}}
        (claude_plugin_dir / "plugin.sources.json").write_text(json.dumps(sources_json))

        results = plugin_hash.verify_sources(plugin_dir)
        assert len(results) == 1
        assert results[0].status == "no-hash"
        print("✓ test_verify_sources_legacy_format")


def test_verify_sources_forked():
    """Test verify_sources with forked component."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_dir = Path(tmpdir)
        claude_plugin_dir = plugin_dir / ".claude-plugin"
        claude_plugin_dir.mkdir()

        source_dir = plugin_dir / "sources"
        source_dir.mkdir()
        source_file = source_dir / "test.md"
        source_file.write_text("Test content")

        # Create plugin.sources.json with forked=true
        sources_json = {
            "sources": {
                "test.md": {
                    "source": str(source_file),
                    "hash": "sha256:wronghash",
                    "forked": True,
                }
            }
        }
        (claude_plugin_dir / "plugin.sources.json").write_text(json.dumps(sources_json))

        results = plugin_hash.verify_sources(plugin_dir)
        assert len(results) == 1
        assert results[0].status == "forked"
        assert results[0].matches  # Forked components always "match"
        print("✓ test_verify_sources_forked")


def main():
    """Run all tests."""
    print("Testing plugin-hash.py\n")

    test_hash_file()
    test_hash_directory()
    test_hash_directory_order_independent()
    test_hash_changes_with_content()
    test_format_hash()
    test_parse_hash()
    test_verify_sources()
    test_verify_sources_legacy_format()
    test_verify_sources_forked()

    print("\n✓ All tests passed!")


if __name__ == "__main__":
    main()
