"""Database connection management for IR Query.

This module provides SQLite connection handling with context manager support,
connection pooling awareness, and robust error handling.

Example:
    from ir_query.connection import DatabaseConnection

    # Basic usage with context manager
    with DatabaseConnection("data/convert-skills.db") as conn:
        cursor = conn.execute("SELECT * FROM languages")
        rows = cursor.fetchall()

    # Check database existence
    db = DatabaseConnection("data/convert-skills.db")
    if db.exists():
        with db as conn:
            ...

    # Get database path
    print(db.path)  # Absolute path to database
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from types import TracebackType

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Exception raised for database-related errors.

    Attributes:
        message: Human-readable error description.
        cause: Original exception that caused this error.
        path: Database path if applicable.
    """

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        path: Path | None = None,
    ) -> None:
        """Initialize DatabaseError.

        Args:
            message: Human-readable error description.
            cause: Original exception that caused this error.
            path: Database path if applicable.
        """
        self.message = message
        self.cause = cause
        self.path = path
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation with cause if present."""
        if self.cause:
            return f"{self.message}: {self.cause}"
        return self.message


class DatabaseConnection:
    """SQLite connection with context manager support.

    This class provides a clean interface for database connections with:
    - Automatic connection management via context manager
    - Row factory support for dict-like access
    - Foreign key enforcement
    - Timeout configuration
    - Graceful error handling

    Attributes:
        path: Absolute path to the database file.

    Example:
        with DatabaseConnection("data/convert-skills.db") as conn:
            cursor = conn.execute("SELECT * FROM languages")
            for row in cursor:
                print(row["name"])
    """

    def __init__(
        self,
        db_path: str | Path,
        *,
        timeout: float = 30.0,
        row_factory: bool = True,
        check_same_thread: bool = True,
    ) -> None:
        """Initialize database connection configuration.

        Args:
            db_path: Path to the SQLite database file.
            timeout: Connection timeout in seconds. Default 30.0.
            row_factory: If True, use sqlite3.Row for dict-like access.
            check_same_thread: If True, enforce single-thread access.
        """
        self._path = Path(db_path).resolve()
        self._timeout = timeout
        self._row_factory = row_factory
        self._check_same_thread = check_same_thread
        self._connection: sqlite3.Connection | None = None

    @property
    def path(self) -> Path:
        """Return the absolute path to the database."""
        return self._path

    def exists(self) -> bool:
        """Check if the database file exists.

        Returns:
            True if the database file exists, False otherwise.
        """
        return self._path.exists()

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection.

        Returns:
            Configured SQLite connection.

        Raises:
            DatabaseError: If connection cannot be established.
        """
        try:
            conn = sqlite3.connect(
                str(self._path),
                timeout=self._timeout,
                check_same_thread=self._check_same_thread,
            )

            if self._row_factory:
                conn.row_factory = sqlite3.Row

            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")

            logger.debug(f"Connected to database: {self._path}")
            return conn

        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to connect to database",
                cause=e,
                path=self._path,
            ) from e

    def connect(self) -> sqlite3.Connection:
        """Establish a database connection.

        Returns:
            Active SQLite connection.

        Raises:
            DatabaseError: If the database does not exist or connection fails.
        """
        if not self.exists():
            raise DatabaseError(
                f"Database not found: {self._path}",
                path=self._path,
            )

        if self._connection is None:
            self._connection = self._create_connection()

        return self._connection

    def close(self) -> None:
        """Close the database connection if open."""
        if self._connection is not None:
            try:
                self._connection.close()
                logger.debug(f"Closed database connection: {self._path}")
            except sqlite3.Error as e:
                logger.warning(f"Error closing database connection: {e}")
            finally:
                self._connection = None

    def __enter__(self) -> sqlite3.Connection:
        """Enter context manager and return connection.

        Returns:
            Active SQLite connection.

        Raises:
            DatabaseError: If connection cannot be established.
        """
        return self.connect()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager and close connection.

        If an exception occurred, the connection is rolled back.
        Otherwise, the connection is committed.

        Args:
            exc_type: Exception type if an exception was raised.
            exc_val: Exception instance if an exception was raised.
            exc_tb: Traceback if an exception was raised.
        """
        if self._connection is not None:
            if exc_type is not None:
                # Rollback on error
                try:
                    self._connection.rollback()
                except sqlite3.Error:
                    pass
            else:
                # Commit on success
                try:
                    self._connection.commit()
                except sqlite3.Error as e:
                    logger.warning(f"Error committing transaction: {e}")

        self.close()

    def execute(
        self,
        sql: str,
        parameters: tuple | dict | None = None,
    ) -> sqlite3.Cursor:
        """Execute a SQL statement.

        This is a convenience method that connects if needed.

        Args:
            sql: SQL statement to execute.
            parameters: Optional parameters for the statement.

        Returns:
            Cursor for the executed statement.

        Raises:
            DatabaseError: If execution fails.
        """
        conn = self.connect()
        try:
            if parameters is None:
                return conn.execute(sql)
            return conn.execute(sql, parameters)
        except sqlite3.Error as e:
            raise DatabaseError(
                f"SQL execution failed: {sql[:100]}...",
                cause=e,
                path=self._path,
            ) from e

    def executemany(
        self,
        sql: str,
        parameters: list[tuple] | list[dict],
    ) -> sqlite3.Cursor:
        """Execute a SQL statement against multiple parameter sets.

        Args:
            sql: SQL statement to execute.
            parameters: List of parameter sets.

        Returns:
            Cursor for the executed statement.

        Raises:
            DatabaseError: If execution fails.
        """
        conn = self.connect()
        try:
            return conn.executemany(sql, parameters)
        except sqlite3.Error as e:
            raise DatabaseError(
                f"SQL batch execution failed: {sql[:100]}...",
                cause=e,
                path=self._path,
            ) from e

    def executescript(self, sql_script: str) -> sqlite3.Cursor:
        """Execute a SQL script containing multiple statements.

        Args:
            sql_script: SQL script to execute.

        Returns:
            Cursor for the executed script.

        Raises:
            DatabaseError: If execution fails.
        """
        conn = self.connect()
        try:
            return conn.executescript(sql_script)
        except sqlite3.Error as e:
            raise DatabaseError(
                "SQL script execution failed",
                cause=e,
                path=self._path,
            ) from e
