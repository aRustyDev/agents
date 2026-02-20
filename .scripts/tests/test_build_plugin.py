"""Tests for build-plugin.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest import mock

import pytest

# Import module with hyphen in name using importlib
_module_path = Path(__file__).parent.parent / "build-plugin.py"
_spec = importlib.util.spec_from_file_location("build_plugin", _module_path)
_module = importlib.util.module_from_spec(_spec)
sys.modules["build_plugin"] = _module
_spec.loader.exec_module(_module)

# Now import from the loaded module
Plugin = _module.Plugin
SourceStatus = _module.SourceStatus
compute_hash = _module.compute_hash
format_hash = _module.format_hash
hash_directory = _module.hash_directory
hash_file = _module.hash_file
list_plugins = _module.list_plugins
main = _module.main
parse_hash = _module.parse_hash


class TestHashFunctions:
    """Test hash computation functions."""

    def test_hash_file(self, tmp_path: Path) -> None:
        """Test hashing a single file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        h = hash_file(test_file)
        assert len(h) == 64  # SHA256 hex length
        assert h == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    def test_hash_directory(self, tmp_path: Path) -> None:
        """Test hashing a directory."""
        (tmp_path / "a.txt").write_text("content a")
        (tmp_path / "b.txt").write_text("content b")
        h = hash_directory(tmp_path)
        assert len(h) == 64

    def test_hash_directory_deterministic(self, tmp_path: Path) -> None:
        """Test that directory hashing is deterministic."""
        (tmp_path / "z.txt").write_text("z content")
        (tmp_path / "a.txt").write_text("a content")
        h1 = hash_directory(tmp_path)
        h2 = hash_directory(tmp_path)
        assert h1 == h2

    def test_compute_hash_file(self, tmp_path: Path) -> None:
        """Test compute_hash for files."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        h = compute_hash(test_file)
        assert len(h) == 64

    def test_compute_hash_directory(self, tmp_path: Path) -> None:
        """Test compute_hash for directories."""
        (tmp_path / "file.txt").write_text("content")
        h = compute_hash(tmp_path)
        assert len(h) == 64

    def test_compute_hash_nonexistent(self, tmp_path: Path) -> None:
        """Test compute_hash raises for nonexistent paths."""
        with pytest.raises(ValueError, match="does not exist"):
            compute_hash(tmp_path / "nonexistent")

    def test_format_hash(self) -> None:
        """Test hash formatting."""
        assert format_hash("abc123") == "sha256:abc123"

    def test_parse_hash_with_prefix(self) -> None:
        """Test parsing hash with prefix."""
        assert parse_hash("sha256:abc123") == "abc123"

    def test_parse_hash_without_prefix(self) -> None:
        """Test parsing hash without prefix."""
        assert parse_hash("abc123") == "abc123"


class TestSourceStatus:
    """Test SourceStatus dataclass."""

    def test_status_fresh(self) -> None:
        """Test fresh status."""
        s = SourceStatus(
            local_path="test",
            source_path="source",
            expected_hash="abc",
            actual_hash="abc",
        )
        assert s.status == "fresh"
        assert s.icon == "✓"

    def test_status_stale(self) -> None:
        """Test stale status."""
        s = SourceStatus(
            local_path="test",
            source_path="source",
            expected_hash="abc",
            actual_hash="def",
        )
        assert s.status == "stale"
        assert s.icon == "⚠"

    def test_status_missing(self) -> None:
        """Test missing status."""
        s = SourceStatus(
            local_path="test",
            source_path="source",
            expected_hash="abc",
            actual_hash=None,
            missing=True,
        )
        assert s.status == "missing"
        assert s.icon == "✗"

    def test_status_forked(self) -> None:
        """Test forked status."""
        s = SourceStatus(
            local_path="test",
            source_path="source",
            expected_hash="abc",
            actual_hash="def",
            forked=True,
        )
        assert s.status == "forked"
        assert s.icon == "○"

    def test_status_no_hash(self) -> None:
        """Test no-hash status (legacy format)."""
        s = SourceStatus(
            local_path="test",
            source_path="source",
            expected_hash=None,
            actual_hash="abc",
        )
        assert s.status == "no-hash"
        assert s.icon == "?"


class TestPlugin:
    """Test Plugin class."""

    @pytest.fixture
    def plugin_dir(self, tmp_path: Path) -> Path:
        """Create a test plugin directory structure."""
        plugin = tmp_path / "test-plugin"
        plugin.mkdir()
        claude_plugin = plugin / ".claude-plugin"
        claude_plugin.mkdir()

        # Create source file
        source = tmp_path / "source.md"
        source.write_text("source content")

        # Create plugin.sources.json with extended format
        sources_json = claude_plugin / "plugin.sources.json"
        sources_json.write_text(
            json.dumps(
                {
                    "sources": {
                        "local.md": {
                            "source": str(source),
                            "hash": format_hash(compute_hash(source)),
                        }
                    }
                }
            )
        )

        return tmp_path

    def test_plugin_exists(self, plugin_dir: Path) -> None:
        """Test plugin existence check."""
        with mock.patch("build_plugin.PLUGINS_DIR", plugin_dir):
            plugin = Plugin("test-plugin")
            assert plugin.exists()

    def test_plugin_not_exists(self, tmp_path: Path) -> None:
        """Test plugin not found."""
        with mock.patch("build_plugin.PLUGINS_DIR", tmp_path):
            plugin = Plugin("nonexistent")
            assert not plugin.exists()

    def test_verify_sources_fresh(self, plugin_dir: Path) -> None:
        """Test verifying fresh sources."""
        with mock.patch("build_plugin.PLUGINS_DIR", plugin_dir):
            plugin = Plugin("test-plugin")
            sources = plugin.verify_sources()
            assert len(sources) == 1
            assert sources[0].status == "fresh"

    def test_verify_sources_stale(self, plugin_dir: Path) -> None:
        """Test verifying stale sources."""
        # Modify the source file
        source = plugin_dir / "source.md"
        source.write_text("modified content")

        with mock.patch("build_plugin.PLUGINS_DIR", plugin_dir):
            plugin = Plugin("test-plugin")
            sources = plugin.verify_sources()
            assert len(sources) == 1
            assert sources[0].status == "stale"

    def test_update_hash(self, plugin_dir: Path) -> None:
        """Test updating a hash."""
        # Modify the source file
        source = plugin_dir / "source.md"
        source.write_text("new content")

        with mock.patch("build_plugin.PLUGINS_DIR", plugin_dir):
            plugin = Plugin("test-plugin")
            new_hash = plugin.update_hash("local.md")
            assert new_hash == compute_hash(source)

            # Verify it's now fresh
            sources = plugin.verify_sources()
            assert sources[0].status == "fresh"


class TestCLI:
    """Test CLI commands."""

    def test_hash_command(self, tmp_path: Path) -> None:
        """Test hash command."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        result = main(["hash", str(test_file)])
        assert result == 0

    def test_hash_command_hex_only(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test hash command with --hex-only."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        result = main(["hash", str(test_file), "--hex-only"])
        assert result == 0
        captured = capsys.readouterr()
        assert not captured.out.startswith("sha256:")

    def test_hash_command_nonexistent(self, tmp_path: Path) -> None:
        """Test hash command with nonexistent file."""
        result = main(["hash", str(tmp_path / "nonexistent")])
        assert result == 1

    def test_check_command_json(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test check command with JSON output."""
        # Create plugin structure
        plugin = tmp_path / "test-plugin"
        plugin.mkdir()
        claude_plugin = plugin / ".claude-plugin"
        claude_plugin.mkdir()

        source = tmp_path / "source.md"
        source.write_text("content")

        sources_json = claude_plugin / "plugin.sources.json"
        sources_json.write_text(
            json.dumps(
                {
                    "sources": {
                        "local.md": {
                            "source": str(source),
                            "hash": format_hash(compute_hash(source)),
                        }
                    }
                }
            )
        )

        with mock.patch("build_plugin.PLUGINS_DIR", tmp_path):
            result = main(["check", "test-plugin", "--json"])
            assert result == 0

            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert output["plugin"] == "test-plugin"
            assert output["ok"] is True

    def test_check_all_command(self, tmp_path: Path) -> None:
        """Test check-all command."""
        # Create empty plugins directory
        with mock.patch("build_plugin.PLUGINS_DIR", tmp_path):
            result = main(["check-all"])
            assert result == 0


class TestListPlugins:
    """Test list_plugins function."""

    def test_list_plugins_empty(self, tmp_path: Path) -> None:
        """Test listing plugins in empty directory."""
        with mock.patch("build_plugin.PLUGINS_DIR", tmp_path):
            plugins = list_plugins()
            assert plugins == []

    def test_list_plugins_with_plugins(self, tmp_path: Path) -> None:
        """Test listing plugins."""
        # Create two plugins
        for name in ["plugin-a", "plugin-b"]:
            plugin = tmp_path / name
            plugin.mkdir()
            claude = plugin / ".claude-plugin"
            claude.mkdir()
            (claude / "plugin.sources.json").write_text("{}")

        with mock.patch("build_plugin.PLUGINS_DIR", tmp_path):
            plugins = list_plugins()
            assert plugins == ["plugin-a", "plugin-b"]

    def test_list_plugins_skips_hidden(self, tmp_path: Path) -> None:
        """Test that hidden directories are skipped."""
        hidden = tmp_path / ".template"
        hidden.mkdir()
        (hidden / ".claude-plugin").mkdir()
        (hidden / ".claude-plugin" / "plugin.sources.json").write_text("{}")

        with mock.patch("build_plugin.PLUGINS_DIR", tmp_path):
            plugins = list_plugins()
            assert plugins == []
