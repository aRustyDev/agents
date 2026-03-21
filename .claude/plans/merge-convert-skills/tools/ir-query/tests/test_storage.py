"""Tests for IR storage operations."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ir_query.connection import DatabaseConnection
from ir_query.storage import IRStorage


class TestIRStorage:
    """Tests for IRStorage class."""

    def test_store_dict(self, test_connection: sqlite3.Connection) -> None:
        """Test storing an IR as dictionary."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {
                "id": "mod:test",
                "name": "test",
                "path": ["test"],
                "metadata": {
                    "source_file": "test.py",
                    "source_language": "python",
                },
            },
            "types": [],
            "functions": [
                {"id": "fn:main", "name": "main", "params": []},
            ],
            "bindings": [],
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "python"})

        assert ir_id > 0

    def test_store_extracts_language_from_module(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test that store extracts language from module metadata."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {
                "id": "mod:test",
                "name": "test",
                "metadata": {
                    "source_language": "rust",
                    "source_file": "lib.rs",
                },
            },
        }

        ir_id = storage.store(ir_data, metadata={})

        # Verify language was extracted
        cursor = test_connection.execute(
            "SELECT source_language FROM ir_versions WHERE id = ?",
            (ir_id,),
        )
        row = cursor.fetchone()
        assert row["source_language"] == "rust"

    def test_store_creates_units(self, test_connection: sqlite3.Connection) -> None:
        """Test that store creates IR units for each layer."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {"id": "mod:units", "name": "units"},
            "types": [{"id": "type:T", "name": "T"}],
            "functions": [{"id": "fn:f", "name": "f"}],
            "bindings": [{"id": "var:x", "name": "x"}],
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "python"})

        # Check units were created
        cursor = test_connection.execute(
            "SELECT layer, unit_type FROM ir_units WHERE version_id = ? ORDER BY layer DESC",
            (ir_id,),
        )
        units = cursor.fetchall()

        assert len(units) == 4  # module, type, function, binding
        layers = {u["layer"] for u in units}
        assert 4 in layers  # module
        assert 3 in layers  # type
        assert 2 in layers  # function
        assert 1 in layers  # binding

    def test_store_with_gaps(self, test_connection: sqlite3.Connection) -> None:
        """Test storing IR with gap markers."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {"id": "mod:gaps", "name": "gaps"},
            "functions": [{"id": "fn:f", "name": "f"}],
            "gaps": [
                {
                    "id": "gap:1",
                    "gap_type": "structural",
                    "description": "Test gap",
                    "source_concept": "dynamic typing",
                    "suggested_mitigations": ["Add type hints"],
                }
            ],
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "python"})

        # Verify gap was stored
        cursor = test_connection.execute(
            """
            SELECT g.gap_type, g.description
            FROM ir_gap_markers_v2 g
            JOIN ir_units u ON g.unit_id = u.id
            WHERE u.version_id = ?
            """,
            (ir_id,),
        )
        gaps = cursor.fetchall()
        assert len(gaps) == 1
        assert gaps[0]["gap_type"] == "structural"

    def test_store_with_annotations(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test storing IR with semantic annotations."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {"id": "mod:ann", "name": "ann"},
            "functions": [{"id": "fn:f", "name": "f"}],
            "annotations": [
                {
                    "id": "ann:1",
                    "target": "fn:f",
                    "kind": "inferred_type",
                    "value": {"type": "int"},
                    "confidence": 0.95,
                    "source": "inferred",
                }
            ],
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "python"})

        # Verify annotation was stored
        cursor = test_connection.execute(
            """
            SELECT a.annotation_type, a.confidence
            FROM ir_annotations a
            JOIN ir_units u ON a.unit_id = u.id
            WHERE u.version_id = ?
            """,
            (ir_id,),
        )
        anns = cursor.fetchall()
        assert len(anns) == 1
        assert anns[0]["annotation_type"] == "inferred_type"
        assert anns[0]["confidence"] == 0.95

    def test_retrieve(self, test_connection: sqlite3.Connection) -> None:
        """Test retrieving a stored IR."""
        storage = IRStorage(test_connection)

        # Store first
        ir_data = {
            "version": "ir-v1.0",
            "module": {"id": "mod:retrieve", "name": "retrieve"},
            "types": [{"id": "type:Point", "name": "Point"}],
            "functions": [{"id": "fn:distance", "name": "distance"}],
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "python"})

        # Retrieve
        retrieved = storage.retrieve(ir_id)

        assert retrieved is not None
        assert retrieved["version"] == "ir-v1.0"
        assert retrieved["module"] is not None
        assert len(retrieved["types"]) == 1
        assert len(retrieved["functions"]) == 1

    def test_retrieve_not_found(self, test_connection: sqlite3.Connection) -> None:
        """Test retrieving non-existing IR."""
        storage = IRStorage(test_connection)

        result = storage.retrieve(99999)

        assert result is None

    def test_retrieve_includes_gaps(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test that retrieve includes gap markers."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {"id": "mod:gaps2", "name": "gaps2"},
            "functions": [{"id": "fn:f", "name": "f"}],
            "gaps": [
                {
                    "gap_type": "lossy",
                    "description": "Type information lost",
                    "severity": "high",
                }
            ],
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "python"})
        retrieved = storage.retrieve(ir_id)

        assert "gaps" in retrieved
        assert len(retrieved["gaps"]) == 1

    def test_retrieve_includes_annotations(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test that retrieve includes annotations."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {"id": "mod:ann2", "name": "ann2"},
            "functions": [{"id": "fn:f", "name": "f"}],
            "annotations": [
                {
                    "kind": "ownership",
                    "value": {"owned": True},
                    "source": "explicit",
                }
            ],
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "rust"})
        retrieved = storage.retrieve(ir_id)

        assert "annotations" in retrieved
        assert len(retrieved["annotations"]) == 1

    def test_list_by_language(self, test_connection: sqlite3.Connection) -> None:
        """Test listing IR versions by language."""
        storage = IRStorage(test_connection)

        # Store multiple versions
        for i in range(3):
            storage.store(
                {
                    "version": "ir-v1.0",
                    "module": {"id": f"mod:list{i}", "name": f"list{i}"},
                },
                metadata={
                    "source_language": "python",
                    "source_file": f"file{i}.py",
                },
            )

        versions = storage.list_by_language("python")

        assert len(versions) >= 3
        assert all("unit_count" in v for v in versions)
        assert all("gap_count" in v for v in versions)

    def test_list_by_language_with_pagination(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test listing with limit and offset."""
        storage = IRStorage(test_connection)

        # Store multiple versions
        for i in range(5):
            storage.store(
                {
                    "version": "ir-v1.0",
                    "module": {"id": f"mod:page{i}", "name": f"page{i}"},
                },
                metadata={"source_language": "go"},
            )

        page1 = storage.list_by_language("go", limit=2, offset=0)
        page2 = storage.list_by_language("go", limit=2, offset=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0]["id"] != page2[0]["id"]

    def test_delete(self, test_connection: sqlite3.Connection) -> None:
        """Test deleting an IR version."""
        storage = IRStorage(test_connection)

        # Store first
        ir_id = storage.store(
            {
                "version": "ir-v1.0",
                "module": {"id": "mod:delete", "name": "delete"},
            },
            metadata={"source_language": "python"},
        )

        # Delete
        result = storage.delete(ir_id)

        assert result is True

        # Verify deleted
        retrieved = storage.retrieve(ir_id)
        assert retrieved is None

    def test_delete_not_found(self, test_connection: sqlite3.Connection) -> None:
        """Test deleting non-existing IR version."""
        storage = IRStorage(test_connection)

        result = storage.delete(99999)

        assert result is False

    def test_get_statistics(self, test_connection: sqlite3.Connection) -> None:
        """Test getting storage statistics."""
        storage = IRStorage(test_connection)

        # Store some data
        storage.store(
            {
                "version": "ir-v1.0",
                "module": {"id": "mod:stats", "name": "stats"},
                "types": [{"id": "type:T", "name": "T"}],
            },
            metadata={"source_language": "python"},
        )

        stats = storage.get_statistics()

        assert "total_versions" in stats
        assert "total_units" in stats
        assert "by_language" in stats
        assert "by_layer" in stats
        assert "latest_extraction" in stats

        assert stats["total_versions"] >= 1
        assert stats["total_units"] >= 2  # module + type


class TestIRStorageEdgeCases:
    """Edge case tests for IRStorage."""

    def test_store_empty_ir(self, test_connection: sqlite3.Connection) -> None:
        """Test storing minimal IR."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {"id": "mod:empty", "name": "empty"},
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "python"})

        assert ir_id > 0

    def test_store_with_complex_content(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test storing IR with complex nested content."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {
                "id": "mod:complex",
                "name": "complex",
                "nested": {
                    "deeply": {
                        "nested": {
                            "value": [1, 2, 3, {"key": "value"}]
                        }
                    }
                },
            },
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "python"})

        retrieved = storage.retrieve(ir_id)
        assert retrieved is not None
        assert "module" in retrieved

    def test_store_unicode_content(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test storing IR with unicode content."""
        storage = IRStorage(test_connection)

        ir_data = {
            "version": "ir-v1.0",
            "module": {
                "id": "mod:unicode",
                "name": "\u4e2d\u6587\u6a21\u5757",
                "description": "\u0420\u0443\u0441\u0441\u043a\u0438\u0439 \u0442\u0435\u043a\u0441\u0442",
            },
        }

        ir_id = storage.store(ir_data, metadata={"source_language": "python"})

        retrieved = storage.retrieve(ir_id)
        assert retrieved is not None
        assert retrieved["module"]["name"] == "\u4e2d\u6587\u6a21\u5757"

    def test_list_by_language_case_insensitive(
        self, test_connection: sqlite3.Connection
    ) -> None:
        """Test that language matching is case-insensitive."""
        storage = IRStorage(test_connection)

        storage.store(
            {"version": "ir-v1.0", "module": {"id": "mod:case", "name": "case"}},
            metadata={"source_language": "TypeScript"},
        )

        versions_upper = storage.list_by_language("TYPESCRIPT")
        versions_lower = storage.list_by_language("typescript")

        assert len(versions_upper) == len(versions_lower)

    def test_empty_database(self, empty_db_path: Path) -> None:
        """Test operations on empty database."""
        with DatabaseConnection(empty_db_path) as conn:
            storage = IRStorage(conn)

            assert storage.retrieve(1) is None
            assert storage.list_by_language("python") == []
            assert storage.delete(1) is False

            stats = storage.get_statistics()
            assert stats["total_versions"] == 0
            assert stats["total_units"] == 0
