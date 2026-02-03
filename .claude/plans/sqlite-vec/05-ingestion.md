# Task 5: Implement entity ingestion pipeline

## Objective

Create the main CLI script that ingests context files into the knowledge graph database.

## Prerequisites

- Task 2 complete (database initialization)
- Task 3 complete (embedder module)
- Task 4 complete (chunker module)

## Steps

### 5.1 Create embed.py CLI

Create `scripts/embed.py`:

```python
#!/usr/bin/env python3
"""Knowledge graph embedding CLI.

Usage:
    embed.py ingest --all              # Ingest all context files
    embed.py ingest --type skill       # Ingest specific entity type
    embed.py ingest --file PATH        # Ingest single file
    embed.py check                     # List stale entities
    embed.py search "query"            # Semantic search
    embed.py dump                      # Dump database to SQL
"""

import argparse
import hashlib
import json
import sqlite3
import struct
import sys
from pathlib import Path
from typing import Optional

import sqlite_vec

from lib.chunker import chunk_file, Chunk
from lib.embedder import get_embedder, serialize_embedding

# Configuration
DB_PATH = Path('.data/mcp/knowledge-graph.db')
DUMP_PATH = Path('.data/mcp/knowledge-graph.sql')

# Entity type to file pattern mapping
ENTITY_PATTERNS = {
    'agent': ['context/agents/*.md'],
    'skill': ['context/skills/*/SKILL.md'],
    'command': ['context/commands/*.md', '.claude/commands/**/*.md'],
    'rule': ['context/rules/*.md', '.claude/rules/*.md'],
    'claude_md': ['**/CLAUDE.md'],
    'plugin': ['context/plugins/*/.claude-plugin/plugin.json'],
    'output_style': ['context/output-styles/*.md'],
    'mcp_server': [],  # Loaded from registry, not files
}


def get_connection() -> sqlite3.Connection:
    """Get database connection with sqlite-vec loaded."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def compute_file_hash(path: Path) -> str:
    """Compute SHA256 hash of file contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path_to_slug(path: Path, entity_type: str) -> str:
    """Generate slug from file path."""
    if entity_type == 'skill':
        # Use parent directory name
        return path.parent.name
    elif entity_type == 'plugin':
        # Use grandparent directory name
        return path.parent.parent.name
    else:
        # Use filename without extension
        return path.stem


def find_files(entity_type: str) -> list[Path]:
    """Find all files for an entity type."""
    patterns = ENTITY_PATTERNS.get(entity_type, [])
    files = []
    for pattern in patterns:
        files.extend(Path('.').glob(pattern))
    return sorted(set(files))


def ingest_file(
    conn: sqlite3.Connection,
    path: Path,
    entity_type: str,
    embedder,
    force: bool = False
) -> bool:
    """Ingest a single file into the database.

    Returns True if file was processed, False if skipped (no changes).
    """
    path = path.resolve().relative_to(Path('.').resolve())
    slug = path_to_slug(path, entity_type)
    file_hash = compute_file_hash(path)

    # Check if entity exists and is unchanged
    existing = conn.execute(
        'SELECT id, file_hash FROM entities WHERE slug = ?',
        (slug,)
    ).fetchone()

    if existing and existing[1] == file_hash and not force:
        return False  # No changes

    # Parse file content
    if path.suffix == '.json':
        content = path.read_text()
        metadata = json.loads(content)
        name = metadata.get('name', slug)
        chunks_data = []  # JSON files don't get chunked the same way
    else:
        parsed = chunk_file(path)
        content = parsed.content
        metadata = parsed.frontmatter
        name = metadata.get('name', slug)
        chunks_data = parsed.chunks

    # Start transaction
    if existing:
        entity_id = existing[0]
        # Delete old chunks and embeddings
        conn.execute('DELETE FROM chunks WHERE entity_id = ?', (entity_id,))
        # Update entity
        conn.execute('''
            UPDATE entities SET
                name = ?,
                file_path = ?,
                file_hash = ?,
                content = ?,
                metadata = ?,
                updated_at = datetime('now')
            WHERE id = ?
        ''', (name, str(path), file_hash, content, json.dumps(metadata), entity_id))
        print(f"  Updated: {slug}")
    else:
        # Insert new entity
        cursor = conn.execute('''
            INSERT INTO entities (entity_type, slug, name, file_path, file_hash, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entity_type, slug, name, str(path), file_hash, content, json.dumps(metadata)))
        entity_id = cursor.lastrowid
        print(f"  Created: {slug}")

    # Insert chunks and generate embeddings
    for chunk in chunks_data:
        # Insert chunk
        cursor = conn.execute('''
            INSERT INTO chunks (entity_id, chunk_level, chunk_index, chunk_text, heading)
            VALUES (?, ?, ?, ?, ?)
        ''', (entity_id, chunk.level, chunk.index, chunk.text, chunk.heading))
        chunk_id = cursor.lastrowid

        # Generate embedding
        embedding = embedder.embed_one(chunk.text)

        # Insert embedding metadata
        cursor = conn.execute('''
            INSERT INTO embedding_meta (chunk_id, model_name, dimensions)
            VALUES (?, ?, ?)
        ''', (chunk_id, embedder.model_name, embedder.dimensions))
        meta_id = cursor.lastrowid

        # Insert vector
        conn.execute('''
            INSERT INTO vec_chunks (embedding_id, embedding)
            VALUES (?, ?)
        ''', (meta_id, serialize_embedding(embedding)))

    conn.commit()
    return True


def cmd_ingest(args):
    """Ingest command handler."""
    conn = get_connection()
    embedder = get_embedder(args.model)

    print(f"Using embedder: {embedder.model_name} ({embedder.dimensions} dims)")

    if args.file:
        # Single file
        path = Path(args.file)
        if not path.exists():
            print(f"File not found: {path}")
            sys.exit(1)
        # Guess entity type from path
        entity_type = guess_entity_type(path)
        ingest_file(conn, path, entity_type, embedder, force=args.force)
    else:
        # Multiple files by type
        types_to_process = [args.type] if args.type else list(ENTITY_PATTERNS.keys())

        for entity_type in types_to_process:
            files = find_files(entity_type)
            if not files:
                continue

            print(f"\n{entity_type}s ({len(files)} files):")
            processed = 0
            for path in files:
                if ingest_file(conn, path, entity_type, embedder, force=args.force):
                    processed += 1

            if processed == 0:
                print("  (all up to date)")

    conn.close()


def guess_entity_type(path: Path) -> str:
    """Guess entity type from file path."""
    path_str = str(path)
    if '/agents/' in path_str:
        return 'agent'
    elif '/skills/' in path_str and path.name == 'SKILL.md':
        return 'skill'
    elif '/commands/' in path_str:
        return 'command'
    elif '/rules/' in path_str:
        return 'rule'
    elif path.name == 'CLAUDE.md':
        return 'claude_md'
    elif 'plugin.json' in path_str:
        return 'plugin'
    elif '/output-styles/' in path_str:
        return 'output_style'
    else:
        return 'unknown'


def cmd_check(args):
    """Check for stale entities."""
    conn = get_connection()

    stale = conn.execute('''
        SELECT slug, file_path, file_hash, updated_at
        FROM entities
        WHERE file_path IS NOT NULL
    ''').fetchall()

    print("Checking for stale entities...")
    stale_count = 0

    for slug, file_path, stored_hash, updated_at in stale:
        path = Path(file_path)
        if not path.exists():
            print(f"  MISSING: {slug} ({file_path})")
            stale_count += 1
        else:
            current_hash = compute_file_hash(path)
            if current_hash != stored_hash:
                print(f"  STALE: {slug} (modified since {updated_at})")
                stale_count += 1

    if stale_count == 0:
        print("All entities up to date")
    else:
        print(f"\n{stale_count} entities need re-ingestion")
        print("Run: uv run python scripts/embed.py ingest --all")

    conn.close()


def cmd_search(args):
    """Semantic search."""
    conn = get_connection()
    embedder = get_embedder(args.model)

    # Generate query embedding
    query_embedding = embedder.embed_one(args.query)

    # Search
    results = conn.execute('''
        SELECT
            e.entity_type,
            e.name,
            e.slug,
            c.chunk_level,
            c.heading,
            substr(c.chunk_text, 1, 200) as preview,
            vec_distance_cosine(?, vc.embedding) as distance
        FROM vec_chunks vc
        JOIN embedding_meta em ON vc.embedding_id = em.id
        JOIN chunks c ON em.chunk_id = c.id
        JOIN entities e ON c.entity_id = e.id
        WHERE c.chunk_level = 'file'
        ORDER BY distance
        LIMIT ?
    ''', (serialize_embedding(query_embedding), args.limit)).fetchall()

    print(f"Search results for: {args.query}\n")
    for i, (etype, name, slug, level, heading, preview, distance) in enumerate(results, 1):
        similarity = 1 - distance
        print(f"{i}. [{etype}] {name} (similarity: {similarity:.3f})")
        print(f"   Slug: {slug}")
        print(f"   Preview: {preview[:100]}...")
        print()

    conn.close()


def cmd_dump(args):
    """Dump database to SQL."""
    import subprocess
    result = subprocess.run(
        ['sqlite3', str(DB_PATH), '.dump'],
        capture_output=True,
        text=True
    )
    DUMP_PATH.write_text(result.stdout)
    print(f"Database dumped to {DUMP_PATH}")


def main():
    parser = argparse.ArgumentParser(description='Knowledge graph embedding CLI')
    parser.add_argument('--model', default='nomic-embed-text', help='Embedding model')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # ingest
    p_ingest = subparsers.add_parser('ingest', help='Ingest context files')
    p_ingest.add_argument('--all', action='store_true', help='Ingest all files')
    p_ingest.add_argument('--type', help='Entity type to ingest')
    p_ingest.add_argument('--file', help='Single file to ingest')
    p_ingest.add_argument('--force', action='store_true', help='Force re-ingestion')
    p_ingest.set_defaults(func=cmd_ingest)

    # check
    p_check = subparsers.add_parser('check', help='Check for stale entities')
    p_check.set_defaults(func=cmd_check)

    # search
    p_search = subparsers.add_parser('search', help='Semantic search')
    p_search.add_argument('query', help='Search query')
    p_search.add_argument('--limit', type=int, default=10, help='Max results')
    p_search.set_defaults(func=cmd_search)

    # dump
    p_dump = subparsers.add_parser('dump', help='Dump database to SQL')
    p_dump.set_defaults(func=cmd_dump)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
```

### 5.2 Test ingestion

```bash
# Initialize database first
uv run python scripts/init-db.py

# Ingest a single file
uv run python scripts/embed.py ingest --file context/agents/mcp-server-profiler.md

# Check what was created
uv run python -c "
import sqlite3
conn = sqlite3.connect('.data/mcp/knowledge-graph.db')
print('Entities:', conn.execute('SELECT count(*) FROM entities').fetchone()[0])
print('Chunks:', conn.execute('SELECT count(*) FROM chunks').fetchone()[0])
"

# Ingest all
uv run python scripts/embed.py ingest --all

# Test search
uv run python scripts/embed.py search "code analysis"
```

## Acceptance Criteria

- [ ] `embed.py ingest --file PATH` ingests single file
- [ ] `embed.py ingest --type skill` ingests all skills
- [ ] `embed.py ingest --all` ingests all entity types
- [ ] Re-running is idempotent (skips unchanged files)
- [ ] `--force` flag forces re-ingestion
- [ ] `embed.py check` lists stale entities
- [ ] `embed.py search "query"` returns ranked results
- [ ] `embed.py dump` creates SQL dump

## Files Created

- `scripts/embed.py`

## Next

→ [06-file-watcher.md](06-file-watcher.md)
