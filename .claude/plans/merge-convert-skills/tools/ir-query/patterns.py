"""Pattern-specific queries for the IR database.

This module provides a repository pattern for querying IR patterns with
support for full-text search, category filtering, and pattern matching.

Example:
    from ir_query import PatternRepository, DatabaseConnection

    with DatabaseConnection("data/convert-skills.db") as conn:
        repo = PatternRepository(conn)

        # Full-text search
        results = repo.search_patterns("error handling")

        # Get by category
        patterns = repo.get_patterns_by_category("type_system")

        # Get all gap patterns
        gaps = repo.get_gap_patterns_catalog()
"""

from __future__ import annotations

import json
import logging
import sqlite3
from typing import Any

logger = logging.getLogger(__name__)

# Type alias for row data
RowDict = dict[str, Any]


class PatternRepository:
    """Repository for IR patterns.

    Provides specialized queries for pattern discovery and retrieval,
    including full-text search support via SQLite FTS5.

    Attributes:
        connection: Active SQLite connection.

    Example:
        with DatabaseConnection("data/convert-skills.db") as conn:
            repo = PatternRepository(conn)
            results = repo.search_patterns("ownership", limit=10)
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize the pattern repository.

        Args:
            connection: Active SQLite connection with row_factory set.
        """
        self._conn = connection

    def _row_to_dict(self, row: sqlite3.Row | None) -> RowDict | None:
        """Convert a sqlite3.Row to a dictionary."""
        if row is None:
            return None
        return dict(row)

    def _rows_to_dicts(self, rows: list[sqlite3.Row]) -> list[RowDict]:
        """Convert a list of sqlite3.Row objects to dictionaries."""
        return [dict(row) for row in rows]

    def search_patterns(
        self,
        query: str,
        *,
        limit: int = 10,
        source_lang: str | None = None,
        target_lang: str | None = None,
    ) -> list[RowDict]:
        """Full-text search of patterns.

        Uses SQLite FTS5 to search across source patterns, target patterns,
        and notes. Supports standard FTS5 query syntax.

        Args:
            query: Search query string. Supports:
                - Simple terms: "error handling"
                - Phrase matching: '"exact phrase"'
                - Boolean: "error AND handling"
                - Prefix: "hand*"
            limit: Maximum number of results. Default 10.
            source_lang: Optional filter by source language.
            target_lang: Optional filter by target language.

        Returns:
            List of pattern dictionaries with relevance ranking.
            Each dictionary includes:
                - id: Pattern ID
                - skill_name: Source skill
                - source_lang: Source language
                - target_lang: Target language
                - pattern_type: Pattern type
                - source_pattern: Source code pattern
                - target_pattern: Target code pattern
                - notes: Pattern notes
                - rank: FTS relevance score (lower is better)

        Example:
            # Search for ownership-related patterns
            results = repo.search_patterns("ownership borrow")

            # Search with language filter
            results = repo.search_patterns(
                "async",
                source_lang="python",
                target_lang="rust"
            )
        """
        try:
            # Build the FTS query
            sql = """
                SELECT
                    p.id, p.skill_name, p.source_lang, p.target_lang,
                    p.pattern_type, p.category, p.source_pattern,
                    p.target_pattern, p.is_lossy, p.severity,
                    p.mitigation, p.notes,
                    bm25(patterns_fts) as rank
                FROM patterns_fts fts
                JOIN ir_patterns p ON fts.rowid = p.id
                WHERE patterns_fts MATCH ?
            """
            params: list[Any] = [query]

            if source_lang:
                sql += " AND LOWER(p.source_lang) = LOWER(?)"
                params.append(source_lang)

            if target_lang:
                sql += " AND LOWER(p.target_lang) = LOWER(?)"
                params.append(target_lang)

            sql += " ORDER BY rank LIMIT ?"
            params.append(limit)

            cursor = self._conn.execute(sql, params)
            return self._rows_to_dicts(cursor.fetchall())

        except sqlite3.OperationalError as e:
            # FTS table might not exist or query syntax error
            logger.warning(f"FTS search failed, falling back to LIKE: {e}")
            return self._fallback_search(query, limit, source_lang, target_lang)

    def _fallback_search(
        self,
        query: str,
        limit: int,
        source_lang: str | None,
        target_lang: str | None,
    ) -> list[RowDict]:
        """Fallback search using LIKE when FTS is unavailable.

        Args:
            query: Search query string.
            limit: Maximum results.
            source_lang: Optional source language filter.
            target_lang: Optional target language filter.

        Returns:
            List of matching patterns.
        """
        like_pattern = f"%{query}%"

        sql = """
            SELECT
                id, skill_name, source_lang, target_lang,
                pattern_type, category, source_pattern,
                target_pattern, is_lossy, severity,
                mitigation, notes
            FROM ir_patterns
            WHERE (
                source_pattern LIKE ?
                OR target_pattern LIKE ?
                OR notes LIKE ?
            )
        """
        params: list[Any] = [like_pattern, like_pattern, like_pattern]

        if source_lang:
            sql += " AND LOWER(source_lang) = LOWER(?)"
            params.append(source_lang)

        if target_lang:
            sql += " AND LOWER(target_lang) = LOWER(?)"
            params.append(target_lang)

        sql += " ORDER BY pattern_type, id LIMIT ?"
        params.append(limit)

        cursor = self._conn.execute(sql, params)
        return self._rows_to_dicts(cursor.fetchall())

    def get_patterns_by_category(
        self,
        category: str,
        *,
        pattern_type: str | None = None,
        limit: int | None = None,
    ) -> list[RowDict]:
        """Get patterns by category.

        Categories organize patterns by conceptual area:
        - data_structures: Array, list, map transformations
        - control_flow: Loops, conditionals, pattern matching
        - type_system: Type mappings, generics, traits
        - memory: Ownership, borrowing, GC
        - concurrency: Async, threads, channels
        - effects: Errors, exceptions, monads
        - metaprogramming: Macros, reflection, codegen

        Args:
            category: Pattern category to filter by.
            pattern_type: Optional additional filter by pattern type.
            limit: Optional maximum number of results.

        Returns:
            List of pattern dictionaries matching the category.

        Example:
            # Get all type system patterns
            patterns = repo.get_patterns_by_category("type_system")

            # Get only gap patterns in memory category
            gaps = repo.get_patterns_by_category(
                "memory",
                pattern_type="gap"
            )
        """
        sql = """
            SELECT
                id, skill_name, source_lang, target_lang,
                pattern_type, category, source_pattern,
                target_pattern, is_lossy, severity,
                mitigation, notes, created_at
            FROM ir_patterns
            WHERE LOWER(category) = LOWER(?)
        """
        params: list[Any] = [category]

        if pattern_type:
            sql += " AND pattern_type = ?"
            params.append(pattern_type)

        sql += " ORDER BY pattern_type, source_lang, target_lang"

        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        cursor = self._conn.execute(sql, params)
        return self._rows_to_dicts(cursor.fetchall())

    def get_patterns_by_type(
        self,
        pattern_type: str,
        *,
        source_lang: str | None = None,
        target_lang: str | None = None,
        limit: int | None = None,
    ) -> list[RowDict]:
        """Get patterns by type.

        Pattern types indicate the nature of the pattern:
        - type_mapping: Direct type conversions
        - idiom: Idiomatic code translations
        - gap: Semantic gaps requiring attention
        - error: Error handling patterns
        - concurrency: Concurrency pattern translations

        Args:
            pattern_type: Pattern type to filter by.
            source_lang: Optional filter by source language.
            target_lang: Optional filter by target language.
            limit: Optional maximum number of results.

        Returns:
            List of pattern dictionaries matching the type.

        Example:
            # Get all gap patterns
            gaps = repo.get_patterns_by_type("gap")

            # Get type mappings for Python to Rust
            mappings = repo.get_patterns_by_type(
                "type_mapping",
                source_lang="python",
                target_lang="rust"
            )
        """
        sql = """
            SELECT
                id, skill_name, source_lang, target_lang,
                pattern_type, category, source_pattern,
                target_pattern, is_lossy, severity,
                mitigation, notes, created_at
            FROM ir_patterns
            WHERE pattern_type = ?
        """
        params: list[Any] = [pattern_type]

        if source_lang:
            sql += " AND LOWER(source_lang) = LOWER(?)"
            params.append(source_lang)

        if target_lang:
            sql += " AND LOWER(target_lang) = LOWER(?)"
            params.append(target_lang)

        sql += " ORDER BY category, source_lang, target_lang"

        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        cursor = self._conn.execute(sql, params)
        return self._rows_to_dicts(cursor.fetchall())

    def get_gap_patterns_catalog(
        self,
        *,
        category: str | None = None,
        limit: int | None = None,
    ) -> list[RowDict]:
        """Get the catalog of reusable gap patterns.

        Gap patterns are high-level descriptions of semantic gaps that
        appear across multiple language pairs. They include mitigation
        strategies and examples.

        Args:
            category: Optional filter by gap category.
            limit: Optional maximum number of results.

        Returns:
            List of gap pattern dictionaries with keys:
                - id: Gap pattern ID
                - name: Pattern name (e.g., "TS-001")
                - category: Gap category
                - description: Gap description
                - from_concept: Source language concept
                - to_concept: Target language concept
                - mitigation_strategy: How to address the gap
                - example_from: Example source code
                - example_to: Example target code

        Example:
            # Get all gap patterns
            catalog = repo.get_gap_patterns_catalog()

            # Get type system gaps only
            type_gaps = repo.get_gap_patterns_catalog(category="type_system")
        """
        sql = """
            SELECT
                id, name, category, description,
                from_concept, to_concept,
                mitigation_strategy, example_from, example_to
            FROM gap_patterns
        """
        params: list[Any] = []

        if category:
            sql += " WHERE category = ?"
            params.append(category)

        sql += " ORDER BY category, name"

        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        try:
            cursor = self._conn.execute(sql, params)
            return self._rows_to_dicts(cursor.fetchall())
        except sqlite3.OperationalError as e:
            logger.warning(f"Gap patterns query failed: {e}")
            return []

    def get_pattern_by_id(self, pattern_id: int) -> RowDict | None:
        """Get a specific pattern by ID.

        Args:
            pattern_id: The pattern ID to retrieve.

        Returns:
            Pattern dictionary, or None if not found.
        """
        cursor = self._conn.execute(
            """
            SELECT
                id, skill_name, source_lang, target_lang,
                pattern_type, category, source_pattern,
                target_pattern, is_lossy, severity,
                mitigation, notes, created_at
            FROM ir_patterns
            WHERE id = ?
            """,
            (pattern_id,),
        )
        return self._row_to_dict(cursor.fetchone())

    def get_patterns_by_skill(
        self,
        skill_name: str,
        *,
        limit: int | None = None,
    ) -> list[RowDict]:
        """Get all patterns from a specific skill file.

        Args:
            skill_name: Name of the skill (e.g., "convert-python-to-rust").
            limit: Optional maximum number of results.

        Returns:
            List of patterns extracted from the skill.
        """
        sql = """
            SELECT
                id, skill_name, source_lang, target_lang,
                pattern_type, category, source_pattern,
                target_pattern, is_lossy, severity,
                mitigation, notes, created_at
            FROM ir_patterns
            WHERE skill_name = ?
            ORDER BY pattern_type, id
        """
        params: list[Any] = [skill_name]

        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        cursor = self._conn.execute(sql, params)
        return self._rows_to_dicts(cursor.fetchall())

    def get_lossy_patterns(
        self,
        *,
        source_lang: str | None = None,
        target_lang: str | None = None,
        severity: str | None = None,
        limit: int | None = None,
    ) -> list[RowDict]:
        """Get patterns marked as lossy conversions.

        Lossy patterns indicate where information is lost during conversion
        and may require human review or alternative approaches.

        Args:
            source_lang: Optional filter by source language.
            target_lang: Optional filter by target language.
            severity: Optional filter by severity level.
            limit: Optional maximum number of results.

        Returns:
            List of lossy pattern dictionaries, ordered by severity.

        Example:
            # Get all lossy patterns for Python to Rust
            lossy = repo.get_lossy_patterns(
                source_lang="python",
                target_lang="rust"
            )
        """
        sql = """
            SELECT
                id, skill_name, source_lang, target_lang,
                pattern_type, category, source_pattern,
                target_pattern, is_lossy, severity,
                mitigation, notes, created_at
            FROM ir_patterns
            WHERE is_lossy = 1
        """
        params: list[Any] = []

        if source_lang:
            sql += " AND LOWER(source_lang) = LOWER(?)"
            params.append(source_lang)

        if target_lang:
            sql += " AND LOWER(target_lang) = LOWER(?)"
            params.append(target_lang)

        if severity:
            sql += " AND severity = ?"
            params.append(severity)

        sql += """ ORDER BY CASE severity
            WHEN 'impossible' THEN 1
            WHEN 'lossy' THEN 2
            WHEN 'structural' THEN 3
            WHEN 'idiomatic' THEN 4
        END, category, source_lang, target_lang"""

        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        cursor = self._conn.execute(sql, params)
        return self._rows_to_dicts(cursor.fetchall())

    def get_pattern_statistics(self) -> RowDict:
        """Get statistics about patterns in the database.

        Returns:
            Dictionary with pattern statistics:
                - total_patterns: Total number of patterns
                - by_type: Count by pattern type
                - by_category: Count by category
                - language_pairs: List of language pairs covered
                - lossy_count: Number of lossy patterns
        """
        stats: RowDict = {}

        # Total count
        cursor = self._conn.execute("SELECT COUNT(*) FROM ir_patterns")
        stats["total_patterns"] = cursor.fetchone()[0]

        # By type
        cursor = self._conn.execute(
            """
            SELECT pattern_type, COUNT(*) as count
            FROM ir_patterns
            GROUP BY pattern_type
            ORDER BY count DESC
            """
        )
        stats["by_type"] = {row["pattern_type"]: row["count"] for row in cursor.fetchall()}

        # By category
        cursor = self._conn.execute(
            """
            SELECT category, COUNT(*) as count
            FROM ir_patterns
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            """
        )
        stats["by_category"] = {row["category"]: row["count"] for row in cursor.fetchall()}

        # Language pairs
        cursor = self._conn.execute(
            """
            SELECT DISTINCT source_lang, target_lang, COUNT(*) as count
            FROM ir_patterns
            GROUP BY source_lang, target_lang
            ORDER BY count DESC
            """
        )
        stats["language_pairs"] = [
            {"source": row["source_lang"], "target": row["target_lang"], "count": row["count"]}
            for row in cursor.fetchall()
        ]

        # Lossy count
        cursor = self._conn.execute(
            "SELECT COUNT(*) FROM ir_patterns WHERE is_lossy = 1"
        )
        stats["lossy_count"] = cursor.fetchone()[0]

        return stats
