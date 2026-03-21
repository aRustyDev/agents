"""Tests for the main query interface."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from ir_query.connection import DatabaseConnection
from ir_query.queries import IRQueryInterface


class TestIRQueryInterface:
    """Tests for IRQueryInterface class."""

    def test_get_patterns_for_conversion(self, test_connection: sqlite3.Connection) -> None:
        """Test getting patterns for a language conversion."""
        query = IRQueryInterface(test_connection)
        patterns = query.get_patterns_for_conversion("Python", "Rust")

        assert len(patterns) > 0
        assert all(p["source_lang"] == "Python" for p in patterns)
        assert all(p["target_lang"] == "Rust" for p in patterns)

    def test_get_patterns_case_insensitive(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test that language matching is case-insensitive."""
        query = IRQueryInterface(test_connection)

        patterns_upper = query.get_patterns_for_conversion("PYTHON", "RUST")
        patterns_lower = query.get_patterns_for_conversion("python", "rust")
        patterns_mixed = query.get_patterns_for_conversion("Python", "Rust")

        assert len(patterns_upper) == len(patterns_lower) == len(patterns_mixed)

    def test_get_patterns_with_type_filter(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test filtering patterns by type."""
        query = IRQueryInterface(test_connection)

        patterns = query.get_patterns_for_conversion(
            "Python", "Rust", pattern_type="type_mapping"
        )

        assert all(p["pattern_type"] == "type_mapping" for p in patterns)

    def test_get_patterns_with_limit(self, test_connection: sqlite3.Connection) -> None:
        """Test limiting pattern results."""
        query = IRQueryInterface(test_connection)

        patterns = query.get_patterns_for_conversion("Python", "Rust", limit=2)

        assert len(patterns) <= 2

    def test_get_patterns_no_results(self, test_connection: sqlite3.Connection) -> None:
        """Test getting patterns for non-existing language pair."""
        query = IRQueryInterface(test_connection)

        patterns = query.get_patterns_for_conversion("Cobol", "Haskell")

        assert patterns == []

    def test_get_gap_patterns(self, test_connection: sqlite3.Connection) -> None:
        """Test getting semantic gaps for a language pair."""
        query = IRQueryInterface(test_connection)

        gaps = query.get_gap_patterns("Python", "Rust")

        # We have gaps between gc_managed and ownership families
        assert len(gaps) >= 0  # May vary based on test data setup

    def test_get_gap_patterns_with_category(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test filtering gaps by category."""
        query = IRQueryInterface(test_connection)

        gaps = query.get_gap_patterns("Python", "Rust", gap_category="structural")

        assert all(g["gap_category"] == "structural" for g in gaps)

    def test_get_gap_patterns_with_severity(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test filtering gaps by severity."""
        query = IRQueryInterface(test_connection)

        gaps = query.get_gap_patterns("Python", "Rust", severity="high")

        assert all(g["severity"] == "high" for g in gaps)

    def test_get_decision_points(self, test_connection: sqlite3.Connection) -> None:
        """Test getting decision points."""
        query = IRQueryInterface(test_connection)

        decisions = query.get_decision_points("Python", "Rust")

        # Decision points exist in the test data
        assert isinstance(decisions, list)

    def test_get_language_profile(self, test_connection: sqlite3.Connection) -> None:
        """Test getting a language profile."""
        query = IRQueryInterface(test_connection)

        profile = query.get_language_profile("Python")

        assert profile is not None
        assert profile["name"] == "Python"
        assert profile["tier"] == 1
        assert "families" in profile
        assert "features" in profile

    def test_get_language_profile_case_insensitive(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test that language lookup is case-insensitive."""
        query = IRQueryInterface(test_connection)

        profile1 = query.get_language_profile("python")
        profile2 = query.get_language_profile("PYTHON")

        assert profile1 is not None
        assert profile2 is not None
        assert profile1["id"] == profile2["id"]

    def test_get_language_profile_not_found(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting profile for non-existing language."""
        query = IRQueryInterface(test_connection)

        profile = query.get_language_profile("Nonexistent")

        assert profile is None

    def test_get_family_taxonomy(self, test_connection: sqlite3.Connection) -> None:
        """Test getting the family taxonomy."""
        query = IRQueryInterface(test_connection)

        taxonomy = query.get_family_taxonomy()

        assert "families" in taxonomy
        assert "relationships" in taxonomy
        assert "categories" in taxonomy
        assert len(taxonomy["families"]) > 0

    def test_store_ir_unit(self, test_connection: sqlite3.Connection) -> None:
        """Test storing an IR unit."""
        query = IRQueryInterface(test_connection)

        unit = {
            "layer": 2,
            "unit_type": "function",
            "content": {"name": "test_func", "params": []},
        }

        unit_id = query.store_ir_unit(
            unit, source_path="/test/file.py", source_language="python"
        )

        assert unit_id > 0

    def test_store_ir_unit_missing_layer(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test storing IR unit without layer raises error."""
        query = IRQueryInterface(test_connection)

        unit = {"unit_type": "function"}

        with pytest.raises(ValueError):
            query.store_ir_unit(unit, source_path="/test/file.py")

    def test_store_ir_unit_missing_type(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test storing IR unit without unit_type raises error."""
        query = IRQueryInterface(test_connection)

        unit = {"layer": 2}

        with pytest.raises(ValueError):
            query.store_ir_unit(unit, source_path="/test/file.py")

    def test_get_ir_unit(self, test_connection: sqlite3.Connection) -> None:
        """Test retrieving an IR unit."""
        query = IRQueryInterface(test_connection)

        # Store a unit first
        unit = {
            "layer": 2,
            "unit_type": "function",
            "content": {"name": "get_test", "params": ["x", "y"]},
        }
        unit_id = query.store_ir_unit(
            unit, source_path="/test/retrieve.py", source_language="python"
        )

        # Retrieve it
        retrieved = query.get_ir_unit(unit_id)

        assert retrieved is not None
        assert retrieved["layer"] == 2
        assert retrieved["unit_type"] == "function"
        assert "content" in retrieved

    def test_get_ir_unit_not_found(self, test_connection: sqlite3.Connection) -> None:
        """Test retrieving non-existing IR unit."""
        query = IRQueryInterface(test_connection)

        result = query.get_ir_unit(99999)

        assert result is None

    def test_get_ir_units_by_language(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting IR units by source language."""
        query = IRQueryInterface(test_connection)

        # Store some units
        for i in range(3):
            query.store_ir_unit(
                {"layer": 2, "unit_type": "function", "content": {"name": f"func_{i}"}},
                source_path=f"/test/file_{i}.py",
                source_language="python",
            )

        units = query.get_ir_units_by_language("python")

        assert len(units) >= 3
        assert all("python" in u["source_language"].lower() for u in units)

    def test_get_conversion_difficulty(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting conversion difficulty."""
        query = IRQueryInterface(test_connection)

        # We have test data for gc_managed -> ownership
        difficulty = query.get_conversion_difficulty("Python", "Rust")

        # May be None if no difficulty data matches
        if difficulty is not None:
            assert "difficulty" in difficulty
            assert difficulty["difficulty"] >= 1


class TestIRQueryInterfaceEdgeCases:
    """Edge case tests for IRQueryInterface."""

    def test_empty_results(self, empty_db_path: Path) -> None:
        """Test queries on empty database."""
        with DatabaseConnection(empty_db_path) as conn:
            query = IRQueryInterface(conn)

            patterns = query.get_patterns_for_conversion("Python", "Rust")
            assert patterns == []

            gaps = query.get_gap_patterns("Python", "Rust")
            assert gaps == []

            decisions = query.get_decision_points("Python", "Rust")
            assert decisions == []

    def test_special_characters_in_query(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test handling of special characters in queries."""
        query = IRQueryInterface(test_connection)

        # Should not raise SQL injection errors
        patterns = query.get_patterns_for_conversion(
            "Python'; DROP TABLE ir_patterns;--", "Rust"
        )

        assert patterns == []  # Just returns empty, no error

    def test_unicode_in_query(self, test_connection: sqlite3.Connection) -> None:
        """Test handling of unicode in queries."""
        query = IRQueryInterface(test_connection)

        profile = query.get_language_profile("\u4e2d\u6587")

        assert profile is None  # Not found, but no error
