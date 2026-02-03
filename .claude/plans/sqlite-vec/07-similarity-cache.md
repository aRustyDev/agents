# Task 7: Implement similarity cache computation

## Objective

Add similarity cache computation to the embedding pipeline for fast similarity lookups.

## Prerequisites

- Task 5 complete (ingestion pipeline)

## Steps

### 7.1 Add similarity command to embed.py

Add to `scripts/embed.py`:

```python
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


# Add to argparse in main():
p_similarity = subparsers.add_parser('similarity', help='Compute similarity cache')
p_similarity.add_argument('--entity', help='Single entity slug to compute')
p_similarity.add_argument('--k', type=int, default=20, help='Number of neighbors')
p_similarity.set_defaults(func=cmd_similarity)
```

### 7.2 Add similar command for lookups

Add to `scripts/embed.py`:

```python
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


# Add to argparse in main():
p_similar = subparsers.add_parser('similar', help='Find similar entities')
p_similar.add_argument('entity', help='Entity slug')
p_similar.add_argument('--limit', type=int, default=10, help='Max results')
p_similar.set_defaults(func=cmd_similar)
```

### 7.3 Test similarity computation

```bash
# Compute for all entities
uv run python scripts/embed.py similarity

# Query similar entities
uv run python scripts/embed.py similar mcp-server-profiler

# Compute for single entity
uv run python scripts/embed.py similarity --entity mcp-registry-scanner
```

## Acceptance Criteria

- [ ] `embed.py similarity` computes cache for all entities
- [ ] `embed.py similarity --entity SLUG` computes for single entity
- [ ] `embed.py similar SLUG` returns cached similar entities
- [ ] Similarity scores are in range [0, 1]
- [ ] Cache is updated on re-computation

## Files Modified

- `scripts/embed.py` (add similarity and similar commands)

## Next

→ [08-justfile.md](08-justfile.md)
