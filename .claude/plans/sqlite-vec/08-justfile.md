# Task 8: Add justfile targets for knowledge graph operations

## Objective

Add convenient justfile targets for common knowledge graph operations.

## Prerequisites

- Task 5 complete (ingestion pipeline)

## Steps

### 8.1 Add targets to justfile

Add to `justfile` (in the `mcp` group section):

```just
# Knowledge graph operations

# Initialize knowledge graph database
[group('kg')]
kg-init:
    @uv run python scripts/init-db.py

# Ingest all context files into knowledge graph
[group('kg')]
kg-ingest:
    @uv run python scripts/embed.py ingest --all

# Check for stale entities
[group('kg')]
kg-check:
    @uv run python scripts/embed.py check

# Semantic search
[group('kg')]
kg-search query:
    @uv run python scripts/embed.py search "{{ query }}"

# Find similar entities
[group('kg')]
kg-similar entity:
    @uv run python scripts/embed.py similar "{{ entity }}"

# Compute similarity cache
[group('kg')]
kg-similarity:
    @uv run python scripts/embed.py similarity

# Watch for changes and auto-embed
[group('kg')]
kg-watch:
    @uv run python scripts/watch-embed.py

# Dump knowledge graph to SQL
[group('kg')]
kg-dump:
    @uv run python scripts/embed.py dump

# Load knowledge graph from SQL dump
[group('kg')]
kg-load:
    @uv run python scripts/init-db.py --load

# Show knowledge graph statistics
[group('kg')]
kg-stats:
    @echo "Knowledge Graph Statistics:"
    @uv run python -c "
import sqlite3
import sqlite_vec
conn = sqlite3.connect('.data/mcp/knowledge-graph.db')
conn.enable_load_extension(True)
sqlite_vec.load(conn)

entities = conn.execute('SELECT entity_type, count(*) FROM entities GROUP BY entity_type').fetchall()
chunks = conn.execute('SELECT count(*) FROM chunks').fetchone()[0]
embeddings = conn.execute('SELECT count(*) FROM embedding_meta').fetchone()[0]
similarity = conn.execute('SELECT count(*) FROM similarity_cache').fetchone()[0]

print(f'  Entities:')
for etype, count in entities:
    print(f'    {etype}: {count}')
print(f'  Chunks: {chunks}')
print(f'  Embeddings: {embeddings}')
print(f'  Similarity cache: {similarity}')
"

# Force re-embed all entities
[group('kg')]
kg-rebuild:
    @echo "Rebuilding knowledge graph..."
    @rm -f .data/mcp/knowledge-graph.db
    @just kg-init
    @just kg-ingest
    @just kg-similarity
    @just kg-dump
    @echo "✓ Knowledge graph rebuilt"
```

### 8.2 Update init target

Modify the `_init-db` target to use the new kg-init:

```just
[private]
_init-db:
    @echo "Initializing knowledge graph database..."
    @just kg-init
```

### 8.3 Test targets

```bash
# Initialize
just kg-init

# Ingest
just kg-ingest

# Statistics
just kg-stats

# Search
just kg-search "code analysis"

# Watch (Ctrl+C to stop)
just kg-watch
```

## Acceptance Criteria

- [ ] `just kg-init` initializes database
- [ ] `just kg-ingest` ingests all context files
- [ ] `just kg-check` shows stale entities
- [ ] `just kg-search "query"` performs semantic search
- [ ] `just kg-similar entity` finds similar entities
- [ ] `just kg-similarity` computes similarity cache
- [ ] `just kg-watch` starts file watcher
- [ ] `just kg-dump` creates SQL dump
- [ ] `just kg-load` loads from dump
- [ ] `just kg-stats` shows statistics
- [ ] `just kg-rebuild` does full rebuild
- [ ] `just init` includes database initialization

## Files Modified

- `justfile`

## Next

→ [09-testing.md](09-testing.md)
