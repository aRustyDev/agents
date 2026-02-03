# ADR-006: Version Control Strategy

## Status

Accepted

## Context

The knowledge graph database must be:
- Backed up (recoverable from git clone)
- Distributable (others can use this project)
- Reproducible (same data on any machine after clone)

Binary SQLite files don't diff well in git. We need a text-based representation.

## Decision

**SQL dump** as the version-controlled artifact.

### File Structure

```
.data/
├── mcp/
│   ├── knowledge-graph.db      # Working database (gitignored)
│   └── knowledge-graph.sql     # Text dump (version controlled)
└── .gitignore
```

### Dump Format

```bash
# Dump to text (after any modification)
sqlite3 .data/mcp/knowledge-graph.db .dump > .data/mcp/knowledge-graph.sql

# Load from text (on clone or reset)
sqlite3 .data/mcp/knowledge-graph.db < .data/mcp/knowledge-graph.sql
```

### Automation

```bash
# justfile target
dump-db:
    sqlite3 .data/mcp/knowledge-graph.db .dump > .data/mcp/knowledge-graph.sql

load-db:
    rm -f .data/mcp/knowledge-graph.db
    sqlite3 .data/mcp/knowledge-graph.db < .data/mcp/knowledge-graph.sql

# Post-modification hook in embedding pipeline
def save_and_dump(conn):
    conn.commit()
    subprocess.run(['sqlite3', DB_PATH, '.dump'],
                   stdout=open(DUMP_PATH, 'w'))
```

### What Gets Dumped

| Table | Included | Notes |
|-------|----------|-------|
| `entities` | Yes | Core data |
| `chunks` | Yes | Retained text for re-embedding |
| `embedding_meta` | Yes | Model tracking |
| `vec_chunks` | **No** | Regenerated from chunks + model |
| `relationships` | Yes | Explicit edges |
| `similarity_cache` | **No** | Recomputed on load |
| `entities_fts` | **No** | FTS index, rebuilt on load |

### Load Script

```python
# scripts/load-db.py
def load_database():
    # Remove stale DB
    DB_PATH.unlink(missing_ok=True)

    # Load SQL dump
    subprocess.run(['sqlite3', DB_PATH], stdin=open(DUMP_PATH))

    # Rebuild FTS index
    conn.execute("INSERT INTO entities_fts(entities_fts) VALUES('rebuild')")

    # Regenerate vectors (from stored chunks)
    regenerate_all_embeddings()

    # Recompute similarity cache
    recompute_similarity_cache()
```

### Rationale

1. **Text dumps are git-friendly**: Can see what changed (new entities, updated metadata)
2. **Vectors excluded**: Large, regeneratable, model-dependent
3. **Chunks retained**: Enables re-embedding without re-parsing files
4. **Load script handles reconstruction**: Vectors and caches rebuilt on clone

### Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Git LFS for .db | Still binary, no meaningful diffs |
| JSON export | More complex than SQL, no schema preservation |
| Multiple CSVs | Harder to maintain referential integrity |
| DVC | Overkill for this use case |

## Consequences

- Must run `dump-db` after modifications (automate in hooks)
- Clone requires `load-db` before use (documented in README)
- Vector regeneration on clone takes time (acceptable tradeoff)
- SQL dump can get large — consider splitting tables if needed

## References

- [SQLite .dump command](https://sqlite.org/cli.html#converting_an_entire_database_to_a_text_file)
