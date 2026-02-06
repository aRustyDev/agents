"""IR storage operations for extracted IR units.

This module provides storage and retrieval operations for IR units,
with support for the IRVersion model from ir-core.

Example:
    from ir_query import IRStorage, DatabaseConnection

    with DatabaseConnection("data/convert-skills.db") as conn:
        storage = IRStorage(conn)

        # Store an IR version
        ir_id = storage.store(ir_version, {"source_file": "main.py"})

        # Retrieve by ID
        ir = storage.retrieve(ir_id)

        # List by language
        python_irs = storage.list_by_language("python")
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from types import TracebackType

logger = logging.getLogger(__name__)

# Type alias for row data
RowDict = dict[str, Any]


class IRVersionProtocol(Protocol):
    """Protocol for IRVersion-like objects.

    This allows the storage module to work with any object that has
    the required attributes, not just the specific IRVersion class.
    """

    version: str

    @property
    def module(self) -> Any:
        """Module structure."""
        ...

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Serialize to dictionary."""
        ...

    def content_hash(self) -> str:
        """Compute content hash."""
        ...


class IRStorage:
    """Storage for extracted IR units.

    Provides operations for storing, retrieving, and querying IR units
    in the database. Supports both raw dictionaries and IRVersion model
    objects from ir-core.

    Attributes:
        connection: Active SQLite connection.

    Example:
        with DatabaseConnection("data/convert-skills.db") as conn:
            storage = IRStorage(conn)

            # Store with dict
            ir_id = storage.store_dict(
                ir_data,
                metadata={"source_file": "main.py", "language": "python"}
            )

            # Retrieve
            ir = storage.retrieve(ir_id)
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Initialize IR storage.

        Args:
            connection: Active SQLite connection with row_factory set.
        """
        self._conn = connection

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content.

        Args:
            content: Content to hash.

        Returns:
            First 16 characters of hex-encoded SHA-256 hash.
        """
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def store(
        self,
        ir: IRVersionProtocol | dict[str, Any],
        metadata: RowDict,
    ) -> int:
        """Store IR with metadata, return ID.

        Stores an IR version along with its metadata. The IR can be
        either an IRVersion model object or a raw dictionary.

        Args:
            ir: IRVersion object or dictionary containing IR data.
            metadata: Metadata dictionary with optional keys:
                - source_file: Path to source file
                - source_language: Language name
                - extraction_tool_version: Tool version string
                - notes: Additional notes

        Returns:
            ID of the created IR version.

        Raises:
            ValueError: If required metadata is missing.

        Example:
            # Store IRVersion object
            ir_id = storage.store(
                ir_version,
                metadata={"source_file": "main.py", "source_language": "python"}
            )

            # Store dict
            ir_id = storage.store(
                {"version": "ir-v1.0", "module": {...}},
                metadata={"source_language": "rust"}
            )
        """
        # Handle IRVersion protocol objects
        if hasattr(ir, "model_dump"):
            ir_dict = ir.model_dump(mode="json", exclude_none=True)
            content_hash = ir.content_hash() if hasattr(ir, "content_hash") else None
        else:
            ir_dict = ir
            content_hash = None

        # Extract or compute hash
        if content_hash is None:
            canonical = json.dumps(ir_dict, sort_keys=True, separators=(",", ":"))
            content_hash = self._compute_hash(canonical)

        # Get source language
        source_language = metadata.get("source_language")
        if source_language is None and "module" in ir_dict:
            module = ir_dict["module"]
            if isinstance(module, dict) and "metadata" in module:
                source_language = module["metadata"].get("source_language")

        # Get source path
        source_path = metadata.get("source_file")
        if source_path is None and "module" in ir_dict:
            module = ir_dict["module"]
            if isinstance(module, dict) and "metadata" in module:
                source_path = module["metadata"].get("source_file")

        # Create IR version record
        cursor = self._conn.execute(
            """
            INSERT INTO ir_versions (
                source_language, source_path,
                extraction_tool_version, notes
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                source_language,
                source_path,
                metadata.get("extraction_tool_version", "ir-query/1.0"),
                metadata.get("notes"),
            ),
        )
        version_id = cursor.lastrowid

        # Store IR units by layer
        self._store_ir_layers(version_id, ir_dict)

        logger.debug(f"Stored IR version {version_id} from {source_path}")
        return version_id or 0

    def _store_ir_layers(self, version_id: int, ir_dict: dict[str, Any]) -> None:
        """Store IR units for each layer.

        Args:
            version_id: Parent IR version ID.
            ir_dict: IR dictionary containing layer data.
        """
        # Layer 4: Module
        if "module" in ir_dict:
            self._store_unit(
                version_id,
                layer=4,
                unit_type="module",
                content=ir_dict["module"],
            )

        # Layer 3: Types
        for type_def in ir_dict.get("types", []):
            self._store_unit(
                version_id,
                layer=3,
                unit_type="type",
                content=type_def,
            )

        # Layer 2: Functions
        for func in ir_dict.get("functions", []):
            self._store_unit(
                version_id,
                layer=2,
                unit_type="function",
                content=func,
            )

        # Layer 1: Bindings
        for binding in ir_dict.get("bindings", []):
            self._store_unit(
                version_id,
                layer=1,
                unit_type="binding",
                content=binding,
            )

        # Layer 0: Expressions (if present)
        for expr in ir_dict.get("expressions", []):
            self._store_unit(
                version_id,
                layer=0,
                unit_type="expression",
                content=expr,
            )

        # Cross-cutting: Gap markers
        for gap in ir_dict.get("gaps", []):
            self._store_gap_marker(version_id, gap)

        # Cross-cutting: Annotations
        for annotation in ir_dict.get("annotations", []):
            self._store_annotation(version_id, annotation)

    def _store_unit(
        self,
        version_id: int,
        layer: int,
        unit_type: str,
        content: dict[str, Any],
    ) -> int:
        """Store a single IR unit.

        Args:
            version_id: Parent IR version ID.
            layer: IR layer number (0-4).
            unit_type: Unit type string.
            content: Unit content dictionary.

        Returns:
            ID of the created unit.
        """
        content_json = json.dumps(content, sort_keys=True)
        content_hash = self._compute_hash(content_json)

        try:
            cursor = self._conn.execute(
                """
                INSERT INTO ir_units (
                    version_id, layer, unit_type,
                    content_hash, content_json
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (version_id, layer, unit_type, content_hash, content_json),
            )
            return cursor.lastrowid or 0
        except sqlite3.IntegrityError:
            # Duplicate content hash
            logger.debug(f"Duplicate unit: {unit_type} with hash {content_hash}")
            return 0

    def _store_gap_marker(
        self,
        version_id: int,
        gap: dict[str, Any],
    ) -> int:
        """Store a gap marker.

        Args:
            version_id: Parent IR version ID.
            gap: Gap marker dictionary.

        Returns:
            ID of the created gap marker.
        """
        # First, get the unit ID (use the first unit for this version)
        cursor = self._conn.execute(
            "SELECT id FROM ir_units WHERE version_id = ? LIMIT 1",
            (version_id,),
        )
        row = cursor.fetchone()
        if row is None:
            logger.warning(f"No units found for version {version_id}")
            return 0

        unit_id = row[0]

        # Check if v2 table exists and use it
        try:
            cursor = self._conn.execute(
                """
                INSERT INTO ir_gap_markers_v2 (
                    unit_id, gap_type, description, source_concept,
                    mitigations, gap_pattern_id, severity,
                    target_concept, preservation_level, automation_level,
                    affected_layers
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    unit_id,
                    gap.get("gap_type", "structural"),
                    gap.get("description", ""),
                    gap.get("source_concept", ""),
                    json.dumps(gap.get("suggested_mitigations", [])),
                    gap.get("gap_pattern_id"),
                    gap.get("severity", "medium"),
                    gap.get("target_concept"),
                    gap.get("preservation_level", 2),
                    gap.get("automation_level", "partial"),
                    json.dumps(gap.get("affected_layers", [])),
                ),
            )
            return cursor.lastrowid or 0
        except sqlite3.OperationalError:
            # Fall back to original table
            cursor = self._conn.execute(
                """
                INSERT INTO ir_gap_markers (
                    unit_id, gap_type, description,
                    source_concept, mitigations
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    unit_id,
                    gap.get("gap_type", "structural"),
                    gap.get("description", ""),
                    gap.get("source_concept", ""),
                    json.dumps(gap.get("suggested_mitigations", [])),
                ),
            )
            return cursor.lastrowid or 0

    def _store_annotation(
        self,
        version_id: int,
        annotation: dict[str, Any],
    ) -> int:
        """Store a semantic annotation.

        Args:
            version_id: Parent IR version ID.
            annotation: Annotation dictionary.

        Returns:
            ID of the created annotation.
        """
        # Get unit ID for the annotation target
        target = annotation.get("target", "")
        cursor = self._conn.execute(
            "SELECT id FROM ir_units WHERE version_id = ? LIMIT 1",
            (version_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return 0

        unit_id = row[0]

        cursor = self._conn.execute(
            """
            INSERT INTO ir_annotations (
                unit_id, annotation_type, annotation_value,
                confidence, source
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                unit_id,
                annotation.get("kind", "unknown"),
                json.dumps(annotation.get("value", {})),
                annotation.get("confidence", 1.0),
                annotation.get("source", "explicit"),
            ),
        )
        return cursor.lastrowid or 0

    def retrieve(self, ir_id: int) -> RowDict | None:
        """Retrieve IR by ID.

        Reconstructs the full IR structure from the database, including
        all units, gap markers, and annotations.

        Args:
            ir_id: IR version ID to retrieve.

        Returns:
            Dictionary with complete IR data, or None if not found:
                - version: IR schema version
                - metadata: IR version metadata
                - module: Layer 4 module data
                - types: Layer 3 type definitions
                - functions: Layer 2 functions
                - bindings: Layer 1 bindings
                - expressions: Layer 0 expressions
                - gaps: Gap markers
                - annotations: Semantic annotations

        Example:
            ir = storage.retrieve(123)
            if ir:
                print(f"Module: {ir['module']['name']}")
                print(f"Types: {len(ir['types'])}")
        """
        # Get version metadata
        cursor = self._conn.execute(
            """
            SELECT
                id, source_language, source_path,
                extraction_tool_version, notes, created_at
            FROM ir_versions
            WHERE id = ?
            """,
            (ir_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        result: RowDict = {
            "version": "ir-v1.0",
            "metadata": {
                "id": row["id"],
                "source_language": row["source_language"],
                "source_path": row["source_path"],
                "extraction_tool_version": row["extraction_tool_version"],
                "notes": row["notes"],
                "created_at": row["created_at"],
            },
            "module": None,
            "types": [],
            "functions": [],
            "bindings": [],
            "expressions": [],
            "gaps": [],
            "annotations": [],
        }

        # Get units by layer
        cursor = self._conn.execute(
            """
            SELECT id, layer, unit_type, content_hash, content_json
            FROM ir_units
            WHERE version_id = ?
            ORDER BY layer DESC, id
            """,
            (ir_id,),
        )

        for row in cursor.fetchall():
            content = json.loads(row["content_json"])
            layer = row["layer"]
            unit_type = row["unit_type"]

            if layer == 4 and unit_type == "module":
                result["module"] = content
            elif layer == 3:
                result["types"].append(content)
            elif layer == 2:
                result["functions"].append(content)
            elif layer == 1:
                result["bindings"].append(content)
            elif layer == 0:
                result["expressions"].append(content)

        # Get gap markers
        result["gaps"] = self._get_gap_markers(ir_id)

        # Get annotations
        result["annotations"] = self._get_annotations(ir_id)

        return result

    def _get_gap_markers(self, ir_id: int) -> list[RowDict]:
        """Get gap markers for an IR version.

        Args:
            ir_id: IR version ID.

        Returns:
            List of gap marker dictionaries.
        """
        try:
            # Try v2 table first
            cursor = self._conn.execute(
                """
                SELECT
                    g.id, g.gap_type, g.description, g.source_concept,
                    g.mitigations, g.gap_pattern_id, g.severity,
                    g.target_concept, g.preservation_level, g.automation_level,
                    g.affected_layers
                FROM ir_gap_markers_v2 g
                JOIN ir_units u ON g.unit_id = u.id
                WHERE u.version_id = ?
                ORDER BY g.id
                """,
                (ir_id,),
            )
            gaps = []
            for row in cursor.fetchall():
                gap = dict(row)
                if gap.get("mitigations"):
                    try:
                        gap["mitigations"] = json.loads(gap["mitigations"])
                    except json.JSONDecodeError:
                        pass
                if gap.get("affected_layers"):
                    try:
                        gap["affected_layers"] = json.loads(gap["affected_layers"])
                    except json.JSONDecodeError:
                        pass
                gaps.append(gap)
            return gaps
        except sqlite3.OperationalError:
            # Fall back to v1 table
            cursor = self._conn.execute(
                """
                SELECT
                    g.id, g.gap_type, g.description,
                    g.source_concept, g.mitigations
                FROM ir_gap_markers g
                JOIN ir_units u ON g.unit_id = u.id
                WHERE u.version_id = ?
                ORDER BY g.id
                """,
                (ir_id,),
            )
            gaps = []
            for row in cursor.fetchall():
                gap = dict(row)
                if gap.get("mitigations"):
                    try:
                        gap["mitigations"] = json.loads(gap["mitigations"])
                    except json.JSONDecodeError:
                        pass
                gaps.append(gap)
            return gaps

    def _get_annotations(self, ir_id: int) -> list[RowDict]:
        """Get annotations for an IR version.

        Args:
            ir_id: IR version ID.

        Returns:
            List of annotation dictionaries.
        """
        cursor = self._conn.execute(
            """
            SELECT
                a.id, a.annotation_type as kind, a.annotation_value as value,
                a.confidence, a.source
            FROM ir_annotations a
            JOIN ir_units u ON a.unit_id = u.id
            WHERE u.version_id = ?
            ORDER BY a.id
            """,
            (ir_id,),
        )
        annotations = []
        for row in cursor.fetchall():
            ann = dict(row)
            if ann.get("value"):
                try:
                    ann["value"] = json.loads(ann["value"])
                except json.JSONDecodeError:
                    pass
            annotations.append(ann)
        return annotations

    def list_by_language(
        self,
        language: str,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[RowDict]:
        """List IR units by source language.

        Returns a summary of IR versions extracted from the specified
        language, without the full content.

        Args:
            language: Source language name.
            limit: Optional maximum number of results.
            offset: Number of results to skip. Default 0.

        Returns:
            List of IR version summaries with keys:
                - id: IR version ID
                - source_language: Language name
                - source_path: Source file path
                - created_at: Extraction timestamp
                - unit_count: Number of units in this version
                - gap_count: Number of gap markers

        Example:
            versions = storage.list_by_language("python", limit=20)
            for v in versions:
                print(f"{v['source_path']}: {v['unit_count']} units")
        """
        sql = """
            SELECT
                v.id, v.source_language, v.source_path,
                v.extraction_tool_version, v.notes, v.created_at,
                COUNT(DISTINCT u.id) as unit_count,
                COUNT(DISTINCT g.id) as gap_count
            FROM ir_versions v
            LEFT JOIN ir_units u ON u.version_id = v.id
            LEFT JOIN ir_gap_markers g ON g.unit_id = u.id
            WHERE LOWER(v.source_language) = LOWER(?)
            GROUP BY v.id
            ORDER BY v.created_at DESC
        """
        params: list[Any] = [language]

        if limit:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        cursor = self._conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def delete(self, ir_id: int) -> bool:
        """Delete an IR version and all associated data.

        This is a cascading delete that removes the version, all units,
        gap markers, and annotations.

        Args:
            ir_id: IR version ID to delete.

        Returns:
            True if deletion was successful, False if not found.

        Example:
            if storage.delete(123):
                print("Deleted successfully")
        """
        # Check if exists
        cursor = self._conn.execute(
            "SELECT id FROM ir_versions WHERE id = ?",
            (ir_id,),
        )
        if cursor.fetchone() is None:
            return False

        # Delete (cascade will handle units, markers, annotations)
        self._conn.execute(
            "DELETE FROM ir_versions WHERE id = ?",
            (ir_id,),
        )
        logger.debug(f"Deleted IR version {ir_id}")
        return True

    def get_statistics(self) -> RowDict:
        """Get storage statistics.

        Returns:
            Dictionary with storage statistics:
                - total_versions: Total IR versions stored
                - total_units: Total IR units stored
                - by_language: Dict of language -> version count
                - by_layer: Dict of layer -> unit count
                - latest_extraction: Most recent extraction timestamp
        """
        stats: RowDict = {}

        # Total versions
        cursor = self._conn.execute("SELECT COUNT(*) FROM ir_versions")
        stats["total_versions"] = cursor.fetchone()[0]

        # Total units
        cursor = self._conn.execute("SELECT COUNT(*) FROM ir_units")
        stats["total_units"] = cursor.fetchone()[0]

        # By language
        cursor = self._conn.execute(
            """
            SELECT source_language, COUNT(*) as count
            FROM ir_versions
            WHERE source_language IS NOT NULL
            GROUP BY source_language
            ORDER BY count DESC
            """
        )
        stats["by_language"] = {
            row["source_language"]: row["count"]
            for row in cursor.fetchall()
        }

        # By layer
        cursor = self._conn.execute(
            """
            SELECT layer, COUNT(*) as count
            FROM ir_units
            GROUP BY layer
            ORDER BY layer DESC
            """
        )
        stats["by_layer"] = {row["layer"]: row["count"] for row in cursor.fetchall()}

        # Latest extraction
        cursor = self._conn.execute(
            "SELECT MAX(created_at) as latest FROM ir_versions"
        )
        row = cursor.fetchone()
        stats["latest_extraction"] = row["latest"] if row else None

        return stats
