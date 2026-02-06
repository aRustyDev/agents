"""Main query interface for IR-related data.

This module provides the primary query interface for accessing IR data
from the Convert Skills database. It supports queries for patterns,
semantic gaps, decision points, and language profiles.

Example:
    from ir_query import IRQueryInterface, DatabaseConnection

    with DatabaseConnection("data/convert-skills.db") as conn:
        query = IRQueryInterface(conn)

        # Get patterns for a conversion
        patterns = query.get_patterns_for_conversion("python", "rust")

        # Get semantic gaps
        gaps = query.get_gap_patterns("python", "rust")

        # Get decision points
        decisions = query.get_decision_points("python", "rust")

        # Get language profile
        profile = query.get_language_profile("python")
"""

from __future__ import annotations

import json
import logging
import sqlite3
from typing import Any

logger = logging.getLogger(__name__)

# Type alias for row data returned from queries
RowDict = dict[str, Any]


class IRQueryInterface:
    """Query interface for IR-related data.

    This class provides methods for querying patterns, gaps, decision points,
    IR units, and language profiles from the database.

    Attributes:
        connection: Active SQLite connection.

    Example:
        with DatabaseConnection("data/convert-skills.db") as conn:
            query = IRQueryInterface(conn)
            patterns = query.get_patterns_for_conversion("python", "rust")
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize the query interface.

        Args:
            connection: Active SQLite connection with row_factory set.
        """
        self._conn = connection

    def _row_to_dict(self, row: sqlite3.Row | None) -> RowDict | None:
        """Convert a sqlite3.Row to a dictionary.

        Args:
            row: SQLite row object.

        Returns:
            Dictionary representation of the row, or None if row is None.
        """
        if row is None:
            return None
        return dict(row)

    def _rows_to_dicts(self, rows: list[sqlite3.Row]) -> list[RowDict]:
        """Convert a list of sqlite3.Row objects to dictionaries.

        Args:
            rows: List of SQLite row objects.

        Returns:
            List of dictionary representations.
        """
        return [dict(row) for row in rows]

    def get_patterns_for_conversion(
        self,
        source: str,
        target: str,
        *,
        pattern_type: str | None = None,
        limit: int | None = None,
    ) -> list[RowDict]:
        """Get patterns applicable to a source->target conversion.

        Queries the ir_patterns table for patterns matching the specified
        language pair. Results include the pattern details, severity, and
        any mitigation strategies.

        Args:
            source: Source language (e.g., "python", "typescript").
            target: Target language (e.g., "rust", "go").
            pattern_type: Optional filter by pattern type (type_mapping,
                idiom, gap, error, concurrency).
            limit: Optional maximum number of results.

        Returns:
            List of pattern dictionaries with keys:
                - id: Pattern ID
                - skill_name: Source skill name
                - source_lang: Source language
                - target_lang: Target language
                - pattern_type: Pattern type
                - category: Pattern category
                - source_pattern: Source code pattern
                - target_pattern: Target code pattern
                - is_lossy: Whether conversion is lossy
                - severity: Gap severity
                - mitigation: Mitigation strategy
                - notes: Additional notes

        Example:
            patterns = query.get_patterns_for_conversion("python", "rust")
            for p in patterns:
                print(f"{p['pattern_type']}: {p['source_pattern']}")
        """
        sql = """
            SELECT
                id, skill_name, source_lang, target_lang,
                pattern_type, category, source_pattern, target_pattern,
                is_lossy, severity, mitigation, notes, created_at
            FROM ir_patterns
            WHERE LOWER(source_lang) = LOWER(?)
              AND LOWER(target_lang) = LOWER(?)
        """
        params: list[Any] = [source, target]

        if pattern_type:
            sql += " AND pattern_type = ?"
            params.append(pattern_type)

        sql += " ORDER BY pattern_type, id"

        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        cursor = self._conn.execute(sql, params)
        return self._rows_to_dicts(cursor.fetchall())

    def get_gap_patterns(
        self,
        source: str,
        target: str,
        *,
        gap_category: str | None = None,
        severity: str | None = None,
        limit: int | None = None,
    ) -> list[RowDict]:
        """Get known semantic gaps for a language pair.

        Queries the semantic_gaps and gap_patterns tables to find gaps
        that may occur when converting between the specified languages.
        Uses language families to find applicable gaps.

        Args:
            source: Source language (e.g., "python").
            target: Target language (e.g., "rust").
            gap_category: Optional filter by gap category (impossible,
                lossy, structural, idiomatic, runtime, semantic).
            severity: Optional filter by severity (critical, high,
                medium, low).
            limit: Optional maximum number of results.

        Returns:
            List of gap dictionaries with keys:
                - id: Gap ID
                - gap_category: Gap category
                - concept: Affected concept
                - description: Gap description
                - severity: Gap severity
                - mitigation: Mitigation strategy
                - automation_level: Automation level
                - from_family: Source language family
                - to_family: Target language family

        Example:
            gaps = query.get_gap_patterns("python", "rust")
            for g in gaps:
                if g['severity'] == 'critical':
                    print(f"Critical gap: {g['concept']}")
        """
        # First, get the family IDs for the languages
        sql = """
            SELECT DISTINCT
                sg.id, sg.gap_category, sg.concept, sg.description,
                sg.severity, sg.mitigation, sg.automation_level,
                ff.name as from_family, tf.name as to_family,
                sg.notes
            FROM semantic_gaps sg
            JOIN families ff ON sg.from_family_id = ff.id
            JOIN families tf ON sg.to_family_id = tf.id
            JOIN language_families slf ON slf.family_id = ff.id
            JOIN language_families tlf ON tlf.family_id = tf.id
            JOIN languages sl ON sl.id = slf.language_id
            JOIN languages tl ON tl.id = tlf.language_id
            WHERE LOWER(sl.name) = LOWER(?)
              AND LOWER(tl.name) = LOWER(?)
        """
        params: list[Any] = [source, target]

        if gap_category:
            sql += " AND sg.gap_category = ?"
            params.append(gap_category)

        if severity:
            sql += " AND sg.severity = ?"
            params.append(severity)

        sql += " ORDER BY CASE sg.severity "
        sql += " WHEN 'critical' THEN 1 "
        sql += " WHEN 'high' THEN 2 "
        sql += " WHEN 'medium' THEN 3 "
        sql += " WHEN 'low' THEN 4 END, sg.concept"

        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        try:
            cursor = self._conn.execute(sql, params)
            return self._rows_to_dicts(cursor.fetchall())
        except sqlite3.OperationalError as e:
            # Tables might not exist; return empty list
            logger.warning(f"Gap query failed (tables may not exist): {e}")
            return []

    def get_decision_points(
        self,
        source: str,
        target: str,
        *,
        limit: int | None = None,
    ) -> list[RowDict]:
        """Get decision points requiring human input for a conversion.

        Decision points are situations where automated conversion cannot
        make a deterministic choice and requires human guidance.

        Args:
            source: Source language (e.g., "python").
            target: Target language (e.g., "rust").
            limit: Optional maximum number of results.

        Returns:
            List of decision point dictionaries with keys:
                - id: Decision point ID
                - name: Decision point name
                - description: What decision is needed
                - options: JSON array of possible options
                - guidance: Guidance for making the decision
                - applicable_gaps: JSON array of related gap IDs
                - pattern_id: Related pattern ID
                - severity: Gap severity

        Example:
            decisions = query.get_decision_points("python", "rust")
            for d in decisions:
                print(f"{d['name']}: {d['description']}")
                print(f"  Options: {d['options']}")
        """
        # Get decision points linked to patterns for this language pair
        sql = """
            SELECT DISTINCT
                dp.id, dp.name, dp.description,
                dp.options, dp.guidance, dp.applicable_gaps,
                ip.id as pattern_id, ip.severity
            FROM decision_points dp
            LEFT JOIN ir_patterns ip
                ON ip.source_lang = ?
                AND ip.target_lang = ?
            WHERE dp.id IN (
                SELECT DISTINCT decision_point_id
                FROM ir_gap_markers_v2
                WHERE decision_point_id IS NOT NULL
            )
            OR EXISTS (
                SELECT 1 FROM ir_patterns p
                WHERE LOWER(p.source_lang) = LOWER(?)
                  AND LOWER(p.target_lang) = LOWER(?)
            )
        """
        params: list[Any] = [source, target, source, target]

        sql += " ORDER BY dp.name"

        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        try:
            cursor = self._conn.execute(sql, params)
            results = self._rows_to_dicts(cursor.fetchall())

            # Parse JSON fields
            for result in results:
                if result.get("options"):
                    try:
                        result["options"] = json.loads(result["options"])
                    except json.JSONDecodeError:
                        pass
                if result.get("applicable_gaps"):
                    try:
                        result["applicable_gaps"] = json.loads(
                            result["applicable_gaps"]
                        )
                    except json.JSONDecodeError:
                        pass

            return results
        except sqlite3.OperationalError as e:
            logger.warning(f"Decision point query failed: {e}")
            return []

    def store_ir_unit(
        self,
        ir_unit: RowDict,
        source_path: str,
        *,
        source_language: str | None = None,
    ) -> int:
        """Store an extracted IR unit, return ID.

        Creates an IR version entry and stores the IR unit data. The unit
        content is stored as JSON for flexible querying.

        Args:
            ir_unit: Dictionary containing IR unit data with keys:
                - layer: IR layer number (0-4)
                - unit_type: Unit type (module, type, function, binding, expression)
                - content: Unit content (will be JSON-serialized)
            source_path: Path to the source file.
            source_language: Optional source language name.

        Returns:
            ID of the created IR unit.

        Raises:
            ValueError: If required fields are missing.

        Example:
            unit_id = query.store_ir_unit(
                {
                    "layer": 2,
                    "unit_type": "function",
                    "content": {"name": "main", ...}
                },
                source_path="src/main.py",
                source_language="python"
            )
        """
        import hashlib

        # Validate required fields
        if "layer" not in ir_unit:
            raise ValueError("IR unit must have 'layer' field")
        if "unit_type" not in ir_unit:
            raise ValueError("IR unit must have 'unit_type' field")

        # Create IR version
        cursor = self._conn.execute(
            """
            INSERT INTO ir_versions (source_language, source_path, extraction_tool_version)
            VALUES (?, ?, ?)
            """,
            (source_language, source_path, "ir-query/1.0"),
        )
        version_id = cursor.lastrowid

        # Prepare content
        content = ir_unit.get("content", ir_unit)
        content_json = json.dumps(content, sort_keys=True)
        content_hash = hashlib.sha256(content_json.encode()).hexdigest()[:16]

        # Insert IR unit
        cursor = self._conn.execute(
            """
            INSERT INTO ir_units (version_id, layer, unit_type, content_hash, content_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                version_id,
                ir_unit["layer"],
                ir_unit["unit_type"],
                content_hash,
                content_json,
            ),
        )

        return cursor.lastrowid or 0

    def get_ir_unit(self, unit_id: int) -> RowDict | None:
        """Retrieve an IR unit by ID.

        Args:
            unit_id: ID of the IR unit to retrieve.

        Returns:
            Dictionary with IR unit data, or None if not found.
            Keys include:
                - id: Unit ID
                - version_id: Parent version ID
                - layer: IR layer number
                - unit_type: Unit type
                - content_hash: Content hash
                - content: Parsed JSON content

        Example:
            unit = query.get_ir_unit(123)
            if unit:
                print(f"Layer {unit['layer']}: {unit['unit_type']}")
        """
        cursor = self._conn.execute(
            """
            SELECT
                u.id, u.version_id, u.layer, u.unit_type,
                u.content_hash, u.content_json,
                v.source_language, v.source_path, v.created_at
            FROM ir_units u
            JOIN ir_versions v ON u.version_id = v.id
            WHERE u.id = ?
            """,
            (unit_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        result = self._row_to_dict(row)
        if result and result.get("content_json"):
            try:
                result["content"] = json.loads(result["content_json"])
            except json.JSONDecodeError:
                result["content"] = None
            del result["content_json"]

        return result

    def get_language_profile(self, language: str) -> RowDict | None:
        """Get language profile data.

        Returns comprehensive information about a language including
        its families, features, and syntax patterns.

        Args:
            language: Language name (e.g., "python", "rust").

        Returns:
            Dictionary with language profile data, or None if not found.
            Keys include:
                - id: Language ID
                - name: Language name
                - version: Language version
                - tier: Support tier (1-3)
                - description: Language description
                - families: List of family names
                - features: Dict of feature dimensions
                - syntax: Dict of syntax patterns
                - gaps: List of inherent language gaps

        Example:
            profile = query.get_language_profile("python")
            if profile:
                print(f"Python tier: {profile['tier']}")
                print(f"Families: {profile['families']}")
        """
        # Get base language info
        cursor = self._conn.execute(
            """
            SELECT
                id, name, version, tier, description,
                popularity_tiobe, popularity_so, github_repos,
                created_at
            FROM languages
            WHERE LOWER(name) = LOWER(?)
            """,
            (language,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        result = self._row_to_dict(row)
        if result is None:
            return None

        lang_id = result["id"]

        # Get families
        cursor = self._conn.execute(
            """
            SELECT f.name, f.category, lf.is_primary
            FROM families f
            JOIN language_families lf ON f.id = lf.family_id
            WHERE lf.language_id = ?
            ORDER BY lf.is_primary DESC, f.name
            """,
            (lang_id,),
        )
        result["families"] = [
            {"name": row["name"], "category": row["category"], "primary": row["is_primary"]}
            for row in cursor.fetchall()
        ]

        # Get features grouped by dimension
        cursor = self._conn.execute(
            """
            SELECT dimension, feature, value, notes
            FROM language_features
            WHERE language_id = ?
            ORDER BY dimension, feature
            """,
            (lang_id,),
        )
        features: dict[str, list[RowDict]] = {}
        for row in cursor.fetchall():
            dim = row["dimension"]
            if dim not in features:
                features[dim] = []
            features[dim].append({
                "feature": row["feature"],
                "value": row["value"],
                "notes": row["notes"],
            })
        result["features"] = features

        # Get syntax patterns
        cursor = self._conn.execute(
            """
            SELECT pattern_name, pattern, notes
            FROM language_syntax
            WHERE language_id = ?
            ORDER BY pattern_name
            """,
            (lang_id,),
        )
        result["syntax"] = {
            row["pattern_name"]: {"pattern": row["pattern"], "notes": row["notes"]}
            for row in cursor.fetchall()
        }

        # Get language-specific gaps
        cursor = self._conn.execute(
            """
            SELECT gap_description, severity, workaround
            FROM language_gaps
            WHERE language_id = ?
            ORDER BY CASE severity
                WHEN 'major' THEN 1
                WHEN 'moderate' THEN 2
                WHEN 'minor' THEN 3
            END
            """,
            (lang_id,),
        )
        result["gaps"] = [
            {
                "description": row["gap_description"],
                "severity": row["severity"],
                "workaround": row["workaround"],
            }
            for row in cursor.fetchall()
        ]

        return result

    def get_family_taxonomy(self) -> RowDict:
        """Get complete language family taxonomy.

        Returns the full taxonomy of language families including
        categories, characteristics, and relationships.

        Returns:
            Dictionary with taxonomy data:
                - families: List of family entries
                - relationships: List of family relationships
                - categories: Dict mapping category -> list of families

        Example:
            taxonomy = query.get_family_taxonomy()
            for family in taxonomy['families']:
                print(f"{family['name']}: {family['category']}")
        """
        # Get all families with characteristics
        cursor = self._conn.execute(
            """
            SELECT
                f.id, f.name, f.category, f.description,
                GROUP_CONCAT(
                    fc.dimension || ':' || fc.characteristic || '=' || fc.value,
                    '; '
                ) as characteristics
            FROM families f
            LEFT JOIN family_characteristics fc ON f.id = fc.family_id
            GROUP BY f.id
            ORDER BY f.category, f.name
            """
        )

        families = []
        categories: dict[str, list[str]] = {}

        for row in cursor.fetchall():
            family = {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "description": row["description"],
                "characteristics": {},
            }

            # Parse characteristics string
            if row["characteristics"]:
                for char in row["characteristics"].split("; "):
                    if ":" in char and "=" in char:
                        dim_char, value = char.rsplit("=", 1)
                        dim, char_name = dim_char.split(":", 1)
                        if dim not in family["characteristics"]:
                            family["characteristics"][dim] = {}
                        family["characteristics"][dim][char_name] = value

            families.append(family)

            # Track by category
            cat = row["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(row["name"])

        # Get relationships
        cursor = self._conn.execute(
            """
            SELECT
                ff.name as from_family,
                tf.name as to_family,
                fr.relationship_type,
                fr.notes
            FROM family_relationships fr
            JOIN families ff ON fr.from_family_id = ff.id
            JOIN families tf ON fr.to_family_id = tf.id
            ORDER BY ff.name, fr.relationship_type, tf.name
            """
        )
        relationships = self._rows_to_dicts(cursor.fetchall())

        return {
            "families": families,
            "relationships": relationships,
            "categories": categories,
        }

    def get_ir_units_by_language(
        self,
        language: str,
        *,
        layer: int | None = None,
        unit_type: str | None = None,
        limit: int | None = None,
    ) -> list[RowDict]:
        """Get IR units by source language.

        Args:
            language: Source language name.
            layer: Optional filter by IR layer (0-4).
            unit_type: Optional filter by unit type.
            limit: Optional maximum number of results.

        Returns:
            List of IR unit dictionaries.
        """
        sql = """
            SELECT
                u.id, u.version_id, u.layer, u.unit_type,
                u.content_hash, u.content_json,
                v.source_language, v.source_path, v.created_at
            FROM ir_units u
            JOIN ir_versions v ON u.version_id = v.id
            WHERE LOWER(v.source_language) = LOWER(?)
        """
        params: list[Any] = [language]

        if layer is not None:
            sql += " AND u.layer = ?"
            params.append(layer)

        if unit_type:
            sql += " AND u.unit_type = ?"
            params.append(unit_type)

        sql += " ORDER BY u.layer, u.id"

        if limit:
            sql += " LIMIT ?"
            params.append(limit)

        cursor = self._conn.execute(sql, params)
        results = self._rows_to_dicts(cursor.fetchall())

        # Parse JSON content
        for result in results:
            if result.get("content_json"):
                try:
                    result["content"] = json.loads(result["content_json"])
                except json.JSONDecodeError:
                    result["content"] = None
                del result["content_json"]

        return results

    def get_conversion_difficulty(
        self,
        source: str,
        target: str,
    ) -> RowDict | None:
        """Get conversion difficulty between two languages.

        Uses family-level difficulty data to estimate conversion
        complexity.

        Args:
            source: Source language name.
            target: Target language name.

        Returns:
            Dictionary with difficulty data, or None if not available:
                - difficulty: 1=easy, 2=moderate, 3=hard, 4=very_hard
                - notes: Additional notes
                - semantic_gaps: List of major semantic gaps
                - from_family: Source family name
                - to_family: Target family name
        """
        sql = """
            SELECT
                fcd.difficulty,
                fcd.notes,
                fcd.semantic_gaps,
                ff.name as from_family,
                tf.name as to_family
            FROM family_conversion_difficulty fcd
            JOIN families ff ON fcd.from_family_id = ff.id
            JOIN families tf ON fcd.to_family_id = tf.id
            JOIN language_families slf ON slf.family_id = ff.id
            JOIN language_families tlf ON tlf.family_id = tf.id
            JOIN languages sl ON sl.id = slf.language_id
            JOIN languages tl ON tl.id = tlf.language_id
            WHERE LOWER(sl.name) = LOWER(?)
              AND LOWER(tl.name) = LOWER(?)
              AND slf.is_primary = 1
              AND tlf.is_primary = 1
        """

        try:
            cursor = self._conn.execute(sql, (source, target))
            row = cursor.fetchone()
            if row is None:
                return None

            result = self._row_to_dict(row)
            if result and result.get("semantic_gaps"):
                try:
                    result["semantic_gaps"] = json.loads(result["semantic_gaps"])
                except json.JSONDecodeError:
                    pass
            return result
        except sqlite3.OperationalError as e:
            logger.warning(f"Difficulty query failed: {e}")
            return None
