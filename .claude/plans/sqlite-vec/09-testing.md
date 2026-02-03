# Task 9: End-to-end testing

## Objective

Verify the complete pipeline works from initialization through search and similarity.

## Prerequisites

- All previous tasks complete

## Test Cases

### 9.1 Fresh initialization

```bash
# Remove existing database
rm -f .data/mcp/knowledge-graph.db .data/mcp/knowledge-graph.sql

# Initialize from scratch
just init

# Expected: No errors, database created
```

**Verify:**
- [ ] `just init` completes without errors
- [ ] `.data/mcp/knowledge-graph.db` exists
- [ ] `ollama list` shows nomic-embed-text

### 9.2 Ingest all files

```bash
just kg-ingest
```

**Verify:**
- [ ] All entity types processed (agents, skills, commands, rules, etc.)
- [ ] No errors during embedding generation
- [ ] `just kg-stats` shows reasonable counts

### 9.3 Semantic search

```bash
just kg-search "code analysis"
just kg-search "kubernetes deployment"
just kg-search "file operations"
```

**Verify:**
- [ ] Results are returned and ranked by similarity
- [ ] Results are relevant to query
- [ ] Different queries return different results

### 9.4 Similarity cache

```bash
just kg-similarity
just kg-similar mcp-server-profiler
```

**Verify:**
- [ ] Similarity computation completes for all entities
- [ ] `kg-similar` returns related entities
- [ ] Similarity scores are reasonable (0-1 range)

### 9.5 Idempotency

```bash
# Run ingestion twice
just kg-ingest
just kg-ingest

# Second run should be fast (no changes)
```

**Verify:**
- [ ] Second run says "(all up to date)" for each type
- [ ] No duplicate entities created

### 9.6 File watcher

```bash
# Terminal 1
just kg-watch

# Terminal 2
echo "# Test" >> context/agents/mcp-server-profiler.md
git checkout context/agents/mcp-server-profiler.md
```

**Verify:**
- [ ] Watcher detects modification
- [ ] File is re-embedded
- [ ] Reverting triggers another re-embed

### 9.7 Dump and load cycle

```bash
# Dump
just kg-dump
cat .data/mcp/knowledge-graph.sql | head -50

# Remove database
rm .data/mcp/knowledge-graph.db

# Load from dump
just kg-load

# Verify
just kg-stats
just kg-search "code analysis"
```

**Verify:**
- [ ] Dump creates valid SQL file
- [ ] Load restores database
- [ ] Search works after restore
- [ ] Stats match pre-dump values

### 9.8 Force rebuild

```bash
just kg-rebuild
```

**Verify:**
- [ ] Old database removed
- [ ] Fresh database created
- [ ] All entities re-ingested
- [ ] Similarity cache recomputed
- [ ] Dump created

### 9.9 Stale detection

```bash
# Manually corrupt a hash
uv run python -c "
import sqlite3
conn = sqlite3.connect('.data/mcp/knowledge-graph.db')
conn.execute(\"UPDATE entities SET file_hash = 'invalid' WHERE rowid = 1\")
conn.commit()
"

# Check for stale
just kg-check
```

**Verify:**
- [ ] Stale entity is detected and reported
- [ ] Running `kg-ingest` fixes it

## Summary Checklist

| Test | Status |
|------|--------|
| Fresh initialization | [ ] |
| Ingest all files | [ ] |
| Semantic search | [ ] |
| Similarity cache | [ ] |
| Idempotency | [ ] |
| File watcher | [ ] |
| Dump and load cycle | [ ] |
| Force rebuild | [ ] |
| Stale detection | [ ] |

## Troubleshooting

### Ollama not running
```bash
ollama serve  # Start in separate terminal
```

### sqlite-vec not loading
```bash
uv run python -c "import sqlite_vec; print('OK')"
```

### No embeddings generated
```bash
# Check if model is available
ollama list | grep nomic-embed-text

# Pull if missing
ollama pull nomic-embed-text
```

### Database locked errors
```bash
# Find processes using the database
lsof .data/mcp/knowledge-graph.db

# Kill if necessary (careful!)
```

## Done!

Once all tests pass, the sqlite-vec implementation is complete.

The knowledge graph is ready for:
- Semantic search across all context components
- Finding similar entities
- Relationship analysis
- Integration with agents and commands
