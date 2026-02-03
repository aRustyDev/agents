# ADR-002: Vector Index

## Status

Accepted

## Context

Semantic search is the primary query mechanism for:
- Finding components that cover a use case
- Detecting overlap between entities
- Similarity ranking for recommendations
- Decomposition analysis (internal embedding variance)

We need vector storage that:
- Integrates with SQLite (single database file)
- Supports BYOV (Bring Your Own Vectors) — arbitrary embedding models
- Handles multi-level embeddings (file, section, paragraph)
- Optionally supports quantization (int8, binary) for large-scale storage
- Works with standard sqlite3 CLI or Python

## Decision

**sqlite-vec** as the vector index extension.

### Rationale

1. **Same database file**: Vectors live alongside relational data, single backup/restore
2. **BYOV**: Pure storage — we generate embeddings externally with any model
3. **Quantization support**: float32, int8, and bit vectors for future optimization
4. **Distance functions**: Cosine, L2, Hamming built-in
5. **Filtered search**: Can JOIN with other tables for metadata filtering
6. **Active development**: Regular releases, good documentation

### Schema Pattern

```sql
-- Chunk storage (retains original text)
CREATE TABLE chunks (
  id INTEGER PRIMARY KEY,
  entity_id INTEGER REFERENCES entities(id),
  chunk_level TEXT,  -- 'file', 'section', 'paragraph'
  chunk_text TEXT
);

-- Embedding metadata (model tracking)
CREATE TABLE embedding_meta (
  id INTEGER PRIMARY KEY,
  chunk_id INTEGER REFERENCES chunks(id),
  model_name TEXT,
  dimensions INTEGER
);

-- Vector storage (virtual table)
CREATE VIRTUAL TABLE vec_chunks USING vec0(
  embedding_id INTEGER PRIMARY KEY,
  embedding FLOAT[384]
);
```

### Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Chroma | Separate database, doesn't integrate with SQLite |
| LanceDB | Different storage format, no sqlite3 CLI access |
| Pinecone/Weaviate | Cloud-hosted, not local-first |
| pgvector | Requires PostgreSQL |

## Consequences

- Embedding dimension must be declared at table creation (can create multiple tables for different dimensions)
- Extension must be loaded: Python `sqlite_vec.load(conn)` or CLI `.load vec0`
- macOS system sqlite3 cannot load extensions — use Python or Homebrew sqlite3
- Re-embedding requires DELETE + INSERT (no UPDATE for virtual tables)

## References

- [sqlite-vec GitHub](https://github.com/asg017/sqlite-vec)
- [Hybrid search with sqlite-vec](https://alexgarcia.xyz/blog/2024/sqlite-vec-hybrid-search/index.html)
