#!/usr/bin/env python3
"""Knowledge graph embedding CLI.

Usage:
    embed.py ingest --all              # Ingest all context files
    embed.py ingest --type skill       # Ingest specific entity type
    embed.py ingest --file PATH        # Ingest single file
    embed.py check                     # List stale entities
    embed.py search "query"            # Semantic search
    embed.py similar SLUG              # Find similar entities
    embed.py similarity                # Compute similarity cache
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
        # Delete old vectors first (vec_chunks is a virtual table, no cascade)
        conn.execute('''
            DELETE FROM vec_chunks WHERE embedding_id IN (
                SELECT em.id FROM embedding_meta em
                JOIN chunks c ON em.chunk_id = c.id
                WHERE c.entity_id = ?
            )
        ''', (entity_id,))
        # Delete old chunks (cascades to embedding_meta)
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


def cmd_similarity(args):
    """Compute and cache similarity scores."""
    conn = get_connection()
    embedder = get_embedder(args.model)

    if args.entity:
        # Compute for single entity
        entity = conn.execute(
            'SELECT id FROM entities WHERE slug = ?',
            (args.entity,)
        ).fetchone()

        if not entity:
            print(f"Entity not found: {args.entity}")
            sys.exit(1)

        compute_entity_similarity(conn, entity[0], embedder, k=args.k)
    else:
        # Compute for all entities
        entities = conn.execute('SELECT id, slug FROM entities').fetchall()
        print(f"Computing similarity for {len(entities)} entities...")

        for i, (entity_id, slug) in enumerate(entities):
            compute_entity_similarity(conn, entity_id, embedder, k=args.k)
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(entities)}")

    conn.close()
    print("✓ Similarity cache updated")


def compute_entity_similarity(conn, entity_id: int, embedder, k: int = 20):
    """Compute and cache similarity for a single entity."""
    # Get entity's file-level embedding
    result = conn.execute('''
        SELECT vc.embedding, em.dimensions
        FROM vec_chunks vc
        JOIN embedding_meta em ON vc.embedding_id = em.id
        JOIN chunks c ON em.chunk_id = c.id
        WHERE c.entity_id = ? AND c.chunk_level = 'file'
        LIMIT 1
    ''', (entity_id,)).fetchone()

    if not result:
        return  # No embedding for this entity

    query_embedding, dimensions = result

    # Find nearest neighbors (excluding self)
    neighbors = conn.execute('''
        SELECT c.entity_id, vec_distance_cosine(?, vc.embedding) as distance
        FROM vec_chunks vc
        JOIN embedding_meta em ON vc.embedding_id = em.id
        JOIN chunks c ON em.chunk_id = c.id
        WHERE c.chunk_level = 'file' AND c.entity_id != ?
        ORDER BY distance
        LIMIT ?
    ''', (query_embedding, entity_id, k)).fetchall()

    # Clear old cache entries for this entity
    conn.execute(
        'DELETE FROM similarity_cache WHERE entity_a_id = ? AND similarity_type = ?',
        (entity_id, 'semantic')
    )

    # Insert new cache entries
    for neighbor_id, distance in neighbors:
        similarity = 1.0 - distance
        conn.execute('''
            INSERT OR REPLACE INTO similarity_cache
            (entity_a_id, entity_b_id, similarity_type, score, computed_at)
            VALUES (?, ?, 'semantic', ?, datetime('now'))
        ''', (entity_id, neighbor_id, similarity))

    conn.commit()


def cmd_similar(args):
    """Find similar entities."""
    conn = get_connection()

    # Look up entity
    entity = conn.execute(
        'SELECT id, name, entity_type FROM entities WHERE slug = ?',
        (args.entity,)
    ).fetchone()

    if not entity:
        print(f"Entity not found: {args.entity}")
        sys.exit(1)

    entity_id, name, entity_type = entity
    print(f"Similar to: {name} [{entity_type}]\n")

    # Query cache
    results = conn.execute('''
        SELECT e.entity_type, e.name, e.slug, sc.score
        FROM similarity_cache sc
        JOIN entities e ON sc.entity_b_id = e.id
        WHERE sc.entity_a_id = ? AND sc.similarity_type = 'semantic'
        ORDER BY sc.score DESC
        LIMIT ?
    ''', (entity_id, args.limit)).fetchall()

    if not results:
        print("No cached similarity data. Run: embed.py similarity")
        sys.exit(1)

    for i, (etype, ename, eslug, score) in enumerate(results, 1):
        print(f"{i}. [{etype}] {ename} (similarity: {score:.3f})")
        print(f"   Slug: {eslug}")
        print()

    conn.close()


def cmd_rebuild_embeddings(args):
    """Rebuild vec_chunks from existing chunks (after loading from dump).

    This regenerates vector embeddings for all chunks that have embedding_meta
    records but no corresponding vec_chunks entries.
    """
    conn = get_connection()
    embedder = get_embedder(args.model)

    # Find chunks that need embeddings (have embedding_meta but no vec_chunks)
    # Also handle case where vec_chunks table is empty/missing
    orphaned = conn.execute('''
        SELECT em.id, em.chunk_id, c.chunk_text
        FROM embedding_meta em
        JOIN chunks c ON em.chunk_id = c.id
        WHERE em.id NOT IN (SELECT embedding_id FROM vec_chunks)
        ORDER BY em.id
    ''').fetchall()

    if not orphaned:
        print("All embeddings are up to date")
        return

    print(f"Rebuilding {len(orphaned)} embeddings...")

    batch_size = 100
    for i in range(0, len(orphaned), batch_size):
        batch = orphaned[i:i+batch_size]
        texts = [row[2] for row in batch]
        embeddings = embedder.embed(texts)

        for (emb_id, chunk_id, _), embedding in zip(batch, embeddings):
            conn.execute(
                'INSERT INTO vec_chunks (embedding_id, embedding) VALUES (?, ?)',
                (emb_id, serialize_embedding(embedding))
            )

        conn.commit()
        print(f"  Processed {min(i+batch_size, len(orphaned))}/{len(orphaned)}")

    print(f"✓ Rebuilt {len(orphaned)} embeddings")
    conn.close()


def cmd_dump(args):
    """Dump database to SQL (delegates to init-db.py)."""
    from init_db import dump_database
    dump_database()


def main():
    parser = argparse.ArgumentParser(description='Knowledge graph embedding CLI')
    parser.add_argument('--model', default='st:all-MiniLM-L6-v2', help='Embedding model (use st: prefix for sentence-transformers)')
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

    # similarity
    p_similarity = subparsers.add_parser('similarity', help='Compute similarity cache')
    p_similarity.add_argument('--entity', help='Single entity slug to compute')
    p_similarity.add_argument('--k', type=int, default=20, help='Number of neighbors')
    p_similarity.set_defaults(func=cmd_similarity)

    # similar
    p_similar = subparsers.add_parser('similar', help='Find similar entities')
    p_similar.add_argument('entity', help='Entity slug')
    p_similar.add_argument('--limit', type=int, default=10, help='Max results')
    p_similar.set_defaults(func=cmd_similar)

    # rebuild-embeddings
    p_rebuild = subparsers.add_parser('rebuild-embeddings', help='Rebuild vec_chunks from existing chunks')
    p_rebuild.set_defaults(func=cmd_rebuild_embeddings)

    # dump
    p_dump = subparsers.add_parser('dump', help='Dump database to SQL')
    p_dump.set_defaults(func=cmd_dump)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
