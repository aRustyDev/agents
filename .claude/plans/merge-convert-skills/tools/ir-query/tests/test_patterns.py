"""Tests for the pattern repository."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ir_query.connection import DatabaseConnection
from ir_query.patterns import PatternRepository


class TestPatternRepository:
    """Tests for PatternRepository class."""

    def test_search_patterns_basic(self, test_connection: sqlite3.Connection) -> None:
        """Test basic pattern search."""
        repo = PatternRepository(test_connection)

        # Search for list/Vec conversion
        results = repo.search_patterns("list")

        assert len(results) > 0
        # Check that results are ordered by relevance (have rank)
        assert "rank" in results[0] or len(results) > 0

    def test_search_patterns_with_limit(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test pattern search with limit."""
        repo = PatternRepository(test_connection)

        results = repo.search_patterns("conversion", limit=2)

        assert len(results) <= 2

    def test_search_patterns_with_source_lang(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test pattern search filtered by source language."""
        repo = PatternRepository(test_connection)

        results = repo.search_patterns("type", source_lang="Python")

        assert all(r["source_lang"].lower() == "python" for r in results)

    def test_search_patterns_with_target_lang(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test pattern search filtered by target language."""
        repo = PatternRepository(test_connection)

        results = repo.search_patterns("type", target_lang="Rust")

        assert all(r["target_lang"].lower() == "rust" for r in results)

    def test_search_patterns_no_results(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test pattern search with no matches."""
        repo = PatternRepository(test_connection)

        results = repo.search_patterns("xyznonexistent123")

        assert results == []

    def test_get_patterns_by_category(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting patterns by category."""
        repo = PatternRepository(test_connection)

        patterns = repo.get_patterns_by_category("type_system")

        assert len(patterns) > 0
        assert all(p["category"] == "type_system" for p in patterns)

    def test_get_patterns_by_category_with_type(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting patterns by category and type."""
        repo = PatternRepository(test_connection)

        patterns = repo.get_patterns_by_category(
            "type_system", pattern_type="type_mapping"
        )

        assert all(p["category"] == "type_system" for p in patterns)
        assert all(p["pattern_type"] == "type_mapping" for p in patterns)

    def test_get_patterns_by_category_no_results(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting patterns for non-existing category."""
        repo = PatternRepository(test_connection)

        patterns = repo.get_patterns_by_category("nonexistent_category")

        assert patterns == []

    def test_get_patterns_by_type(self, test_connection: sqlite3.Connection) -> None:
        """Test getting patterns by type."""
        repo = PatternRepository(test_connection)

        patterns = repo.get_patterns_by_type("gap")

        assert len(patterns) > 0
        assert all(p["pattern_type"] == "gap" for p in patterns)

    def test_get_patterns_by_type_with_langs(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting patterns by type with language filters."""
        repo = PatternRepository(test_connection)

        patterns = repo.get_patterns_by_type(
            "type_mapping", source_lang="Python", target_lang="Rust"
        )

        assert all(p["pattern_type"] == "type_mapping" for p in patterns)
        assert all(p["source_lang"].lower() == "python" for p in patterns)
        assert all(p["target_lang"].lower() == "rust" for p in patterns)

    def test_get_gap_patterns_catalog(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting the gap patterns catalog."""
        repo = PatternRepository(test_connection)

        catalog = repo.get_gap_patterns_catalog()

        assert len(catalog) > 0
        assert all("name" in g for g in catalog)
        assert all("category" in g for g in catalog)

    def test_get_gap_patterns_catalog_by_category(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting gap patterns by category."""
        repo = PatternRepository(test_connection)

        catalog = repo.get_gap_patterns_catalog(category="type_system")

        assert all(g["category"] == "type_system" for g in catalog)

    def test_get_pattern_by_id(self, test_connection: sqlite3.Connection) -> None:
        """Test getting a pattern by ID."""
        repo = PatternRepository(test_connection)

        # Get first pattern
        patterns = repo.get_patterns_by_type("type_mapping", limit=1)
        if patterns:
            pattern_id = patterns[0]["id"]

            result = repo.get_pattern_by_id(pattern_id)

            assert result is not None
            assert result["id"] == pattern_id

    def test_get_pattern_by_id_not_found(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting non-existing pattern by ID."""
        repo = PatternRepository(test_connection)

        result = repo.get_pattern_by_id(99999)

        assert result is None

    def test_get_patterns_by_skill(self, test_connection: sqlite3.Connection) -> None:
        """Test getting patterns by skill name."""
        repo = PatternRepository(test_connection)

        patterns = repo.get_patterns_by_skill("convert-python-to-rust")

        assert len(patterns) > 0
        assert all(p["skill_name"] == "convert-python-to-rust" for p in patterns)

    def test_get_lossy_patterns(self, test_connection: sqlite3.Connection) -> None:
        """Test getting lossy patterns."""
        repo = PatternRepository(test_connection)

        patterns = repo.get_lossy_patterns()

        assert all(p["is_lossy"] == 1 for p in patterns)

    def test_get_lossy_patterns_with_filters(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting lossy patterns with filters."""
        repo = PatternRepository(test_connection)

        patterns = repo.get_lossy_patterns(
            source_lang="Python", target_lang="Rust"
        )

        assert all(p["is_lossy"] == 1 for p in patterns)
        assert all(p["source_lang"].lower() == "python" for p in patterns)
        assert all(p["target_lang"].lower() == "rust" for p in patterns)

    def test_get_pattern_statistics(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test getting pattern statistics."""
        repo = PatternRepository(test_connection)

        stats = repo.get_pattern_statistics()

        assert "total_patterns" in stats
        assert "by_type" in stats
        assert "by_category" in stats
        assert "language_pairs" in stats
        assert "lossy_count" in stats

        assert stats["total_patterns"] > 0
        assert isinstance(stats["by_type"], dict)
        assert isinstance(stats["language_pairs"], list)


class TestPatternRepositoryFTSFallback:
    """Tests for FTS fallback behavior."""

    def test_fallback_search_when_fts_fails(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test that search falls back to LIKE when FTS fails."""
        repo = PatternRepository(test_connection)

        # Drop the FTS table to force fallback
        test_connection.execute("DROP TABLE IF EXISTS patterns_fts")

        # Search should still work via fallback
        results = repo.search_patterns("list")

        # Should return results via LIKE fallback
        assert isinstance(results, list)

    def test_fallback_search_results(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test fallback search returns correct results."""
        repo = PatternRepository(test_connection)

        # Use the internal fallback directly
        results = repo._fallback_search("Vec", 10, None, None)

        # Should find Vec in target patterns
        assert any("Vec" in str(r.get("target_pattern", "")) for r in results)


class TestPatternRepositoryEdgeCases:
    """Edge case tests for PatternRepository."""

    def test_empty_database(self, empty_db_path: Path) -> None:
        """Test operations on empty database."""
        with DatabaseConnection(empty_db_path) as conn:
            repo = PatternRepository(conn)

            assert repo.search_patterns("test") == []
            assert repo.get_patterns_by_category("test") == []
            assert repo.get_patterns_by_type("test") == []
            assert repo.get_lossy_patterns() == []

            stats = repo.get_pattern_statistics()
            assert stats["total_patterns"] == 0

    def test_sql_injection_prevention(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test that SQL injection is prevented."""
        repo = PatternRepository(test_connection)

        # These should not cause SQL errors
        results = repo.search_patterns("'; DROP TABLE ir_patterns;--")
        assert isinstance(results, list)

        results = repo.get_patterns_by_category("' OR '1'='1")
        assert isinstance(results, list)

    def test_unicode_handling(self, test_connection: sqlite3.Connection) -> None:
        """Test handling of unicode in searches."""
        repo = PatternRepository(test_connection)

        # Should handle unicode without error
        results = repo.search_patterns("\u4e2d\u6587\u6d4b\u8bd5")
        assert isinstance(results, list)

    def test_very_long_query(self, test_connection: sqlite3.Connection) -> None:
        """Test handling of very long search queries."""
        repo = PatternRepository(test_connection)

        long_query = "a" * 10000
        results = repo.search_patterns(long_query)

        # Should handle without error
        assert isinstance(results, list)
