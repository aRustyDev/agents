#!/usr/bin/env python3
"""Initialize the knowledge graph database.

This script is idempotent - safe to run multiple times.
"""

import sqlite3
from pathlib import Path

import sqlite_vec

# Configuration
DB_DIR = Path('.data/mcp')
DB_PATH = DB_DIR / 'knowledge-graph.db'
SCHEMA_PATH = DB_DIR / 'knowledge-graph.schema.sql'
DUMP_PATH = DB_DIR / 'knowledge-graph.sql'

# Embedding model configuration
# Using sentence-transformers due to Ollama/Metal compatibility issues
DEFAULT_MODEL = 'all-MiniLM-L6-v2'
DEFAULT_DIMENSIONS = 384


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
            heading TEXT,
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
    """Load database from SQL dump if DB doesn't exist.

    After loading, vec_chunks must be regenerated via `kg-ingest --rebuild-embeddings`.
    """
    if DB_PATH.exists():
        print(f"Database exists at {DB_PATH}")
        return False

    if not DUMP_PATH.exists():
        print(f"No dump file at {DUMP_PATH}")
        return False

    print(f"Loading database from {DUMP_PATH}...")
    DB_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    conn.executescript(DUMP_PATH.read_text())
    conn.commit()
    conn.close()

    print("✓ Database loaded from dump")
    print("⚠ Run 'just kg-rebuild-embeddings' to regenerate vector embeddings")
    return True


# Tables that can be regenerated (not dumped)
REGENERATABLE_TABLES = [
    'vec_chunks',           # Regenerated from chunks via embedding
    'vec_chunks_rowids',    # Internal vec0 table
    'vec_chunks_chunks',    # Internal vec0 table
    'vec_chunks_vector_chunks00',  # Internal vec0 table
    'vec_chunks_info',      # Internal vec0 table
    'similarity_cache',     # Regenerated via kg-similarity
    'entities_fts',         # FTS index, rebuilt automatically
    'entities_fts_data',    # FTS internal
    'entities_fts_idx',     # FTS internal
    'entities_fts_config',  # FTS internal
    'entities_fts_docsize', # FTS internal
    'entities_fts_content', # FTS internal
]


def dump_database():
    """Dump essential tables to SQL file (skips regeneratable tables).

    This creates a smaller dump (~40MB vs ~160MB) by excluding:
    - vec_chunks (vector embeddings - regenerated from chunks)
    - similarity_cache (regenerated via kg-similarity)
    - entities_fts (FTS index - rebuilt on load)

    After loading, run `just kg-rebuild-embeddings` to regenerate vectors.
    """
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return False

    import subprocess

    # Get list of tables to dump (excluding regeneratable ones)
    conn = sqlite3.connect(str(DB_PATH))
    all_tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    conn.close()

    tables_to_dump = [
        t[0] for t in all_tables
        if t[0] not in REGENERATABLE_TABLES and not t[0].startswith('sqlite_')
    ]

    print(f"Dumping tables: {', '.join(tables_to_dump)}")
    print("Skipping data for: vec_chunks, similarity_cache, entities_fts*")

    # Build dump command for specific tables
    dump_commands = ['PRAGMA foreign_keys=OFF;', 'BEGIN TRANSACTION;']

    # Dump schema for all tables EXCEPT vec0 internal tables
    # We keep similarity_cache schema but not its data
    result = subprocess.run(
        ['sqlite3', str(DB_PATH), '.schema'],
        capture_output=True,
        text=True, check=False
    )
    if result.returncode != 0:
        print(f"Error getting schema: {result.stderr}")
        return False

    # Filter out vec0 internal tables and sqlite internal tables
    skip_schema_patterns = [
        'vec_chunks',  # Matches vec_chunks and all shadow tables
        'sqlite_sequence',  # SQLite internal, auto-recreated
    ]
    schema_lines = []
    skip_until_semicolon = False
    for line in result.stdout.split('\n'):
        # Check if this line starts a CREATE for a table we want to skip
        # Handle both quoted and unquoted table names
        should_skip = False
        for pattern in skip_schema_patterns:
            if (f'CREATE TABLE {pattern}' in line or
                f'CREATE TABLE "{pattern}' in line or
                f'CREATE TABLE IF NOT EXISTS "{pattern}' in line or
                f'CREATE VIRTUAL TABLE {pattern}' in line):
                should_skip = True
                break

        if should_skip:
            skip_until_semicolon = True

        if not skip_until_semicolon:
            schema_lines.append(line)

        if skip_until_semicolon and ';' in line:
            skip_until_semicolon = False

    dump_commands.append('\n'.join(schema_lines))

    # Dump data for each essential table
    for table in tables_to_dump:
        result = subprocess.run(
            ['sqlite3', str(DB_PATH), f'.mode insert {table}', f'SELECT * FROM {table};'],
            capture_output=True,
            text=True, check=False
        )
        if result.returncode != 0:
            print(f"Error dumping {table}: {result.stderr}")
            continue
        if result.stdout.strip():
            dump_commands.append(f'-- Table: {table}')
            dump_commands.append(result.stdout)

    dump_commands.append('COMMIT;')

    dump_content = '\n'.join(dump_commands)
    DUMP_PATH.write_text(dump_content)

    # Report size
    size_mb = DUMP_PATH.stat().st_size / 1024 / 1024
    print(f"✓ Database dumped to {DUMP_PATH} ({size_mb:.1f} MB)")

    if size_mb > 90:
        print(f"⚠ Warning: dump is {size_mb:.1f} MB, approaching GitHub's 100MB limit")

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
            print("Removed existing database")
        init_database()


if __name__ == '__main__':
    main()
