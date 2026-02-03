# Task 2: Initialize knowledge graph database with schema

## Objective

Create the SQLite database initialization script that applies the schema and creates vec0 virtual tables.

## Prerequisites

- Task 1 complete (sqlite-vec installed)
- Schema file exists: `.data/mcp/knowledge-graph.schema.sql`

## Steps

### 2.1 Create init-db.py script

Create `scripts/init-db.py`:

```python
#!/usr/bin/env python3
"""Initialize the knowledge graph database.

This script is idempotent - safe to run multiple times.
"""

import sqlite3
import sqlite_vec
from pathlib import Path

# Configuration
DB_DIR = Path('.data/mcp')
DB_PATH = DB_DIR / 'knowledge-graph.db'
SCHEMA_PATH = DB_DIR / 'knowledge-graph.schema.sql'
DUMP_PATH = DB_DIR / 'knowledge-graph.sql'

# Embedding model configuration
DEFAULT_MODEL = 'nomic-embed-text'
DEFAULT_DIMENSIONS = 768


def init_database():
    """Initialize the database with schema and vec0 tables."""
    # Ensure directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Connect and load sqlite-vec
    conn = sqlite3.connect(str(DB_PATH))
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    # Enable foreign keys
    conn.execute('PRAGMA foreign_keys = ON')

    # Check if already initialized
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='entities'"
    ).fetchone()

    if tables:
        print(f"Database already initialized at {DB_PATH}")
        # Still ensure vec0 tables exist (they might have been dropped)
        _ensure_vec_tables(conn)
        return conn

    # Apply schema from file
    if SCHEMA_PATH.exists():
        print(f"Applying schema from {SCHEMA_PATH}...")
        schema_sql = SCHEMA_PATH.read_text()
        conn.executescript(schema_sql)
    else:
        print(f"Warning: Schema file not found at {SCHEMA_PATH}")
        print("Creating minimal schema...")
        _create_minimal_schema(conn)

    # Create vec0 virtual tables
    _ensure_vec_tables(conn)

    conn.commit()
    print(f"✓ Database initialized at {DB_PATH}")
    return conn


def _ensure_vec_tables(conn):
    """Create vec0 virtual tables if they don't exist."""
    # Check if vec_chunks exists
    vec_table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='vec_chunks'"
    ).fetchone()

    if not vec_table:
        print(f"Creating vec0 table with {DEFAULT_DIMENSIONS} dimensions...")
        conn.execute(f'''
            CREATE VIRTUAL TABLE vec_chunks USING vec0(
                embedding_id INTEGER PRIMARY KEY,
                embedding FLOAT[{DEFAULT_DIMENSIONS}]
            )
        ''')
        print("✓ vec_chunks table created")


def _create_minimal_schema(conn):
    """Create minimal schema if schema file is missing."""
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY,
            entity_type TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            file_path TEXT,
            file_hash TEXT,
            content TEXT,
            metadata JSON,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
            chunk_level TEXT NOT NULL,
            chunk_index INTEGER,
            chunk_text TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS embedding_meta (
            id INTEGER PRIMARY KEY,
            chunk_id INTEGER REFERENCES chunks(id) ON DELETE CASCADE,
            model_name TEXT NOT NULL,
            dimensions INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY,
            from_entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
            to_entity_id INTEGER REFERENCES entities(id) ON DELETE CASCADE,
            rel_type TEXT NOT NULL,
            UNIQUE(from_entity_id, to_entity_id, rel_type)
        );

        CREATE TABLE IF NOT EXISTS similarity_cache (
            id INTEGER PRIMARY KEY,
            entity_a_id INTEGER,
            entity_b_id INTEGER,
            similarity_type TEXT,
            score REAL,
            computed_at TEXT DEFAULT (datetime('now')),
            UNIQUE(entity_a_id, entity_b_id, similarity_type)
        );
    ''')


def load_from_dump():
    """Load database from SQL dump if DB doesn't exist."""
    if DB_PATH.exists():
        print(f"Database exists at {DB_PATH}")
        return False

    if not DUMP_PATH.exists():
        print(f"No dump file at {DUMP_PATH}")
        return False

    print(f"Loading database from {DUMP_PATH}...")
    DB_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript(DUMP_PATH.read_text())
    conn.close()

    print(f"✓ Database loaded from dump")
    return True


def dump_database():
    """Dump database to SQL file."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return False

    import subprocess
    result = subprocess.run(
        ['sqlite3', str(DB_PATH), '.dump'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error dumping database: {result.stderr}")
        return False

    DUMP_PATH.write_text(result.stdout)
    print(f"✓ Database dumped to {DUMP_PATH}")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Initialize knowledge graph database')
    parser.add_argument('--dump', action='store_true', help='Dump database to SQL')
    parser.add_argument('--load', action='store_true', help='Load database from SQL dump')
    parser.add_argument('--force', action='store_true', help='Force re-initialization')
    args = parser.parse_args()

    if args.dump:
        dump_database()
    elif args.load:
        load_from_dump()
        init_database()  # Ensure vec0 tables exist
    else:
        if args.force and DB_PATH.exists():
            DB_PATH.unlink()
            print(f"Removed existing database")
        init_database()


if __name__ == '__main__':
    main()
```

### 2.2 Make script executable

```bash
chmod +x scripts/init-db.py
```

### 2.3 Test initialization

```bash
# First run - creates database
uv run python scripts/init-db.py

# Second run - idempotent, no changes
uv run python scripts/init-db.py

# Verify tables exist
uv run python -c "
import sqlite3
import sqlite_vec
conn = sqlite3.connect('.data/mcp/knowledge-graph.db')
conn.enable_load_extension(True)
sqlite_vec.load(conn)
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print('Tables:', [t[0] for t in tables])
"
```

### 2.4 Test dump/load cycle

```bash
# Dump
uv run python scripts/init-db.py --dump

# Remove DB
rm .data/mcp/knowledge-graph.db

# Load from dump
uv run python scripts/init-db.py --load

# Verify
uv run python scripts/init-db.py
```

## Acceptance Criteria

- [ ] `scripts/init-db.py` creates database with all tables from schema
- [ ] Running twice is idempotent (no errors, no duplicate tables)
- [ ] `vec_chunks` virtual table is created with correct dimensions (768)
- [ ] `--dump` creates `.data/mcp/knowledge-graph.sql`
- [ ] `--load` restores database from dump
- [ ] `just init` runs without errors (calls this script)

## Files Created

- `scripts/init-db.py`

## Next

→ [03-embedder.md](03-embedder.md)
