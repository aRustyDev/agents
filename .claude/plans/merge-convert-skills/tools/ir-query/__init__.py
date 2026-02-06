"""IR Query - Database query interface for IR-related data.

This module provides a clean query interface for accessing the Convert Skills
IR Research Database. It supports queries for patterns, semantic gaps, decision
points, language profiles, and IR units.

Architecture:
    - DatabaseConnection: SQLite connection with context manager support
    - IRQueryInterface: Main query interface for IR data
    - PatternRepository: Pattern-specific queries with FTS support
    - IRStorage: Storage operations for IR units

Usage:
    from ir_query import IRQueryInterface, DatabaseConnection

    with DatabaseConnection("data/convert-skills.db") as conn:
        query = IRQueryInterface(conn)
        patterns = query.get_patterns_for_conversion("python", "rust")
        gaps = query.get_gap_patterns("python", "rust")

CLI:
    python -m ir_query patterns python rust
    python -m ir_query gaps python rust
    python -m ir_query store file.ir.yaml
    python -m ir_query profile python

See Also:
    - schema.sql: Database schema definition
    - seed_test_data.py: Test data seeding script
    - ir-core: IR data models
"""

__version__ = "1.0.0"

from .connection import DatabaseConnection, DatabaseError
from .queries import IRQueryInterface
from .patterns import PatternRepository
from .storage import IRStorage

__all__ = [
    "DatabaseConnection",
    "DatabaseError",
    "IRQueryInterface",
    "PatternRepository",
    "IRStorage",
]
