"""Tests for the CLI interface."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ir_query.__main__ import (
    create_parser,
    format_output,
    main,
)


class TestCLIParser:
    """Tests for CLI argument parser."""

    def test_create_parser(self) -> None:
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None

    def test_patterns_command(self) -> None:
        """Test patterns command parsing."""
        parser = create_parser()
        args = parser.parse_args(["patterns", "python", "rust"])

        assert args.command == "patterns"
        assert args.source == "python"
        assert args.target == "rust"

    def test_patterns_with_options(self) -> None:
        """Test patterns command with options."""
        parser = create_parser()
        args = parser.parse_args([
            "patterns", "python", "rust",
            "--type", "gap",
            "--limit", "10"
        ])

        assert args.pattern_type == "gap"
        assert args.limit == 10

    def test_gaps_command(self) -> None:
        """Test gaps command parsing."""
        parser = create_parser()
        args = parser.parse_args(["gaps", "python", "rust"])

        assert args.command == "gaps"
        assert args.source == "python"
        assert args.target == "rust"

    def test_gaps_with_options(self) -> None:
        """Test gaps command with options."""
        parser = create_parser()
        args = parser.parse_args([
            "gaps", "python", "rust",
            "--category", "type_system",
            "--severity", "high"
        ])

        assert args.category == "type_system"
        assert args.severity == "high"

    def test_profile_command(self) -> None:
        """Test profile command parsing."""
        parser = create_parser()
        args = parser.parse_args(["profile", "python"])

        assert args.command == "profile"
        assert args.language == "python"

    def test_store_command(self) -> None:
        """Test store command parsing."""
        parser = create_parser()
        args = parser.parse_args(["store", "test.ir.yaml"])

        assert args.command == "store"
        assert args.file == Path("test.ir.yaml")

    def test_retrieve_command(self) -> None:
        """Test retrieve command parsing."""
        parser = create_parser()
        args = parser.parse_args(["retrieve", "123"])

        assert args.command == "retrieve"
        assert args.id == 123

    def test_search_command(self) -> None:
        """Test search command parsing."""
        parser = create_parser()
        args = parser.parse_args(["search", "ownership"])

        assert args.command == "search"
        assert args.query == "ownership"

    def test_global_options(self) -> None:
        """Test global options parsing."""
        parser = create_parser()
        args = parser.parse_args([
            "--db", "/custom/path.db",
            "--format", "json",
            "--no-color",
            "stats"
        ])

        assert args.db == Path("/custom/path.db")
        assert args.format == "json"
        assert args.no_color is True


class TestFormatOutput:
    """Tests for output formatting."""

    def test_format_json(self) -> None:
        """Test JSON format output."""
        data = {"key": "value", "list": [1, 2, 3]}
        output = format_output(data, "json")

        parsed = json.loads(output)
        assert parsed == data

    def test_format_compact(self) -> None:
        """Test compact format output."""
        data = {"key": "value"}
        output = format_output(data, "compact")

        assert " " not in output  # No pretty printing
        assert '"key":"value"' in output

    def test_format_human_dict(self) -> None:
        """Test human format for dict."""
        data = {"name": "test", "value": 42}
        output = format_output(data, "human")

        assert "name:" in output
        assert "test" in output
        assert "value:" in output
        assert "42" in output

    def test_format_human_list(self) -> None:
        """Test human format for list."""
        data = [
            {"id": 1, "name": "first"},
            {"id": 2, "name": "second"},
        ]
        output = format_output(data, "human")

        assert "Result 1" in output
        assert "Result 2" in output
        assert "first" in output
        assert "second" in output

    def test_format_human_empty_list(self) -> None:
        """Test human format for empty list."""
        output = format_output([], "human")

        assert "No results" in output

    def test_format_human_nested(self) -> None:
        """Test human format for nested dict."""
        data = {
            "outer": {
                "inner": "value"
            }
        }
        output = format_output(data, "human")

        assert "outer:" in output
        assert "inner:" in output

    def test_format_human_long_list(self) -> None:
        """Test human format truncates long lists."""
        data = {
            "items": list(range(20))
        }
        output = format_output(data, "human")

        assert "... and" in output  # Truncation indicator


class TestCLICommands:
    """Tests for CLI command execution."""

    def test_main_no_command(self) -> None:
        """Test main with no command shows help."""
        with patch("sys.argv", ["ir-query"]):
            result = main()
            assert result == 0

    def test_main_patterns_missing_db(self, tmp_path: Path) -> None:
        """Test patterns command with missing database."""
        fake_db = tmp_path / "nonexistent.db"
        with patch("sys.argv", [
            "ir-query",
            "--db", str(fake_db),
            "patterns", "python", "rust"
        ]):
            result = main()
            assert result == 1  # Error exit

    def test_main_patterns_success(self, test_db_path: Path) -> None:
        """Test patterns command success."""
        with patch("sys.argv", [
            "ir-query",
            "--db", str(test_db_path),
            "--format", "json",
            "patterns", "python", "rust"
        ]):
            result = main()
            assert result == 0

    def test_main_gaps_success(self, test_db_path: Path) -> None:
        """Test gaps command success."""
        with patch("sys.argv", [
            "ir-query",
            "--db", str(test_db_path),
            "--format", "json",
            "gaps", "python", "rust"
        ]):
            result = main()
            assert result == 0

    def test_main_profile_success(self, test_db_path: Path) -> None:
        """Test profile command success."""
        with patch("sys.argv", [
            "ir-query",
            "--db", str(test_db_path),
            "--format", "json",
            "profile", "python"
        ]):
            result = main()
            assert result == 0

    def test_main_profile_not_found(self, test_db_path: Path) -> None:
        """Test profile command with non-existing language."""
        with patch("sys.argv", [
            "ir-query",
            "--db", str(test_db_path),
            "profile", "nonexistent"
        ]):
            result = main()
            assert result == 1

    def test_main_stats_success(self, test_db_path: Path) -> None:
        """Test stats command success."""
        with patch("sys.argv", [
            "ir-query",
            "--db", str(test_db_path),
            "--format", "json",
            "stats"
        ]):
            result = main()
            assert result == 0

    def test_main_search_success(self, test_db_path: Path) -> None:
        """Test search command success."""
        with patch("sys.argv", [
            "ir-query",
            "--db", str(test_db_path),
            "--format", "json",
            "search", "list"
        ]):
            result = main()
            assert result == 0

    def test_main_retrieve_not_found(self, test_db_path: Path) -> None:
        """Test retrieve command with non-existing ID."""
        with patch("sys.argv", [
            "ir-query",
            "--db", str(test_db_path),
            "retrieve", "99999"
        ]):
            result = main()
            assert result == 1

    def test_main_store_file_not_found(self, test_db_path: Path) -> None:
        """Test store command with non-existing file."""
        with patch("sys.argv", [
            "ir-query",
            "--db", str(test_db_path),
            "store", "/nonexistent/file.yaml"
        ]):
            result = main()
            assert result == 1

    def test_main_store_success(self, test_db_path: Path) -> None:
        """Test store command success."""
        # Create a test IR file
        ir_file = Path(tempfile.mktemp(suffix=".json"))
        ir_file.write_text(json.dumps({
            "version": "ir-v1.0",
            "module": {"id": "mod:test", "name": "test"}
        }))

        try:
            with patch("sys.argv", [
                "ir-query",
                "--db", str(test_db_path),
                "store", str(ir_file),
                "--language", "python"
            ]):
                result = main()
                assert result == 0
        finally:
            ir_file.unlink()
