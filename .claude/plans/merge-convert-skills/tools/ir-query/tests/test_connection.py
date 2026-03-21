"""Tests for database connection management."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from ir_query.connection import DatabaseConnection, DatabaseError


class TestDatabaseConnection:
    """Tests for DatabaseConnection class."""

    def test_init_with_string_path(self, test_db_path: Path) -> None:
        """Test initialization with string path."""
        conn = DatabaseConnection(str(test_db_path))
        assert conn.path == test_db_path

    def test_init_with_path_object(self, test_db_path: Path) -> None:
        """Test initialization with Path object."""
        conn = DatabaseConnection(test_db_path)
        assert conn.path == test_db_path

    def test_path_is_absolute(self, test_db_path: Path) -> None:
        """Test that path is converted to absolute."""
        # Use relative path
        conn = DatabaseConnection("./test.db")
        assert conn.path.is_absolute()

    def test_exists_true(self, test_db_path: Path) -> None:
        """Test exists() returns True for existing database."""
        conn = DatabaseConnection(test_db_path)
        assert conn.exists() is True

    def test_exists_false(self) -> None:
        """Test exists() returns False for non-existing database."""
        conn = DatabaseConnection("/nonexistent/path.db")
        assert conn.exists() is False

    def test_context_manager_success(self, test_db_path: Path) -> None:
        """Test context manager successful operation."""
        with DatabaseConnection(test_db_path) as conn:
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_context_manager_commits(self, test_db_path: Path) -> None:
        """Test that context manager commits on success."""
        with DatabaseConnection(test_db_path) as conn:
            conn.execute(
                "INSERT INTO ir_versions (source_language, source_path) VALUES (?, ?)",
                ("test", "/test/path.py"),
            )

        # Verify data persisted
        with DatabaseConnection(test_db_path) as conn:
            cursor = conn.execute(
                "SELECT source_language FROM ir_versions WHERE source_path = ?",
                ("/test/path.py",),
            )
            row = cursor.fetchone()
            assert row is not None
            assert row["source_language"] == "test"

    def test_context_manager_rollback_on_error(self, test_db_path: Path) -> None:
        """Test that context manager rolls back on error."""
        try:
            with DatabaseConnection(test_db_path) as conn:
                conn.execute(
                    "INSERT INTO ir_versions (source_language, source_path) VALUES (?, ?)",
                    ("rollback_test", "/rollback/path.py"),
                )
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify data was rolled back
        with DatabaseConnection(test_db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM ir_versions WHERE source_path = ?",
                ("/rollback/path.py",),
            )
            row = cursor.fetchone()
            assert row is None

    def test_connect_nonexistent_raises_error(self) -> None:
        """Test that connect() raises DatabaseError for non-existing database."""
        conn = DatabaseConnection("/nonexistent/database.db")
        with pytest.raises(DatabaseError) as exc_info:
            conn.connect()
        assert "not found" in str(exc_info.value).lower()

    def test_execute_with_params(self, test_db_path: Path) -> None:
        """Test execute with parameters."""
        with DatabaseConnection(test_db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM languages WHERE tier = ?",
                (1,),
            )
            rows = cursor.fetchall()
            assert len(rows) > 0

    def test_execute_error_handling(self, test_db_path: Path) -> None:
        """Test execute with invalid SQL raises DatabaseError."""
        db_conn = DatabaseConnection(test_db_path)
        with db_conn as conn:
            # First ensure we have a connection via context manager
            pass

        # Now test with explicit connection
        with DatabaseConnection(test_db_path) as conn:
            with pytest.raises(sqlite3.Error):
                conn.execute("SELECT * FROM nonexistent_table")

    def test_row_factory_enabled(self, test_db_path: Path) -> None:
        """Test that row_factory is enabled by default."""
        with DatabaseConnection(test_db_path) as conn:
            cursor = conn.execute("SELECT name FROM languages LIMIT 1")
            row = cursor.fetchone()
            assert isinstance(row, sqlite3.Row)
            # Should be accessible by name
            assert "name" in row.keys()

    def test_row_factory_disabled(self, test_db_path: Path) -> None:
        """Test row_factory can be disabled."""
        with DatabaseConnection(test_db_path, row_factory=False) as conn:
            cursor = conn.execute("SELECT name FROM languages LIMIT 1")
            row = cursor.fetchone()
            assert isinstance(row, tuple)

    def test_foreign_keys_enabled(self, test_db_path: Path) -> None:
        """Test that foreign keys are enabled."""
        with DatabaseConnection(test_db_path) as conn:
            cursor = conn.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_close_method(self, test_db_path: Path) -> None:
        """Test explicit close method."""
        db = DatabaseConnection(test_db_path)
        conn = db.connect()
        assert conn is not None
        db.close()
        # Should not raise

    def test_double_close(self, test_db_path: Path) -> None:
        """Test that double close does not raise."""
        db = DatabaseConnection(test_db_path)
        db.connect()
        db.close()
        db.close()  # Should not raise


class TestDatabaseError:
    """Tests for DatabaseError class."""

    def test_basic_error(self) -> None:
        """Test basic error creation."""
        err = DatabaseError("Test message")
        assert str(err) == "Test message"
        assert err.cause is None
        assert err.path is None

    def test_error_with_cause(self) -> None:
        """Test error with cause exception."""
        cause = ValueError("Original error")
        err = DatabaseError("Wrapped error", cause=cause)
        assert "Wrapped error" in str(err)
        assert "Original error" in str(err)
        assert err.cause is cause

    def test_error_with_path(self) -> None:
        """Test error with database path."""
        path = Path("/some/database.db")
        err = DatabaseError("Path error", path=path)
        assert err.path == path
