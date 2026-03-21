---
id: a62e81bd-0b5a-4e00-837a-791140ba3ab7
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 6: Knowledge Graph"
status: pending
related:
  depends-on: [1105f062-33cf-4eff-a759-f17fb55296c3]
---

# Phase 6: Knowledge Graph

**ID:** `phase-6`
**Dependencies:** phase-1
**Status:** pending
**Effort:** Large

## Objective

Port the knowledge graph system (SQLite + sqlite-vec embeddings) from Python to TypeScript. This is the highest-risk phase due to sqlite-vec compatibility with better-sqlite3 under Bun. If the extension doesn't load, the KG stays in Python as a fallback.

## Success Criteria

- [ ] `better-sqlite3` loads the sqlite-vec extension under Bun successfully
- [ ] `ai-tools kg init` creates the database with correct schema including vec0 virtual tables
- [ ] `ai-tools kg ingest --all` produces embeddings identical to Python (same model + input = same vectors)
- [ ] `ai-tools kg search <query>` returns the same top-K results as Python for identical queries
- [ ] `ai-tools kg dump` / `ai-tools kg load` round-trips correctly
- [ ] `ai-tools kg stats` shows correct entity/chunk/embedding counts
- [ ] `ai-tools kg watch` detects file changes and re-embeds automatically
- [ ] All justfile `kg-*` recipes point to TypeScript

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Database module | `cli/lib/db.ts` | TypeScript |
| Embedder module | `cli/lib/embedder.ts` | TypeScript |
| KG commands | `cli/commands/kg.ts` | TypeScript |
| Integration tests | `cli/test/{db,embedder,kg}.test.ts` | TypeScript |

## Files

**Create:**
- `cli/lib/db.ts`
- `cli/lib/embedder.ts`
- `cli/test/db.test.ts`
- `cli/test/embedder.test.ts`
- `cli/test/kg.test.ts`

**Modify:**
- `cli/commands/kg.ts` (replace stub with full implementation)
- `justfile` (update kg-* recipes)

## Tasks

### Gate: sqlite-vec smoke test
- [ ] Write a standalone script that loads sqlite-vec via `better-sqlite3` under Bun
- [ ] Test: create vec0 virtual table, insert a vector, query by cosine distance
- [ ] If this fails: **STOP** — keep KG in Python, skip remaining tasks, update PLAN.md

### lib/db.ts
- [ ] Implement `openDb()` — open database, load sqlite-vec extension
- [ ] Implement `initSchema()` — idempotent CREATE TABLE for entities, chunks, embedding_meta, relationships, similarity_cache
- [ ] Implement `ensureVecTables()` — CREATE VIRTUAL TABLE vec_chunks using vec0
- [ ] Implement `dumpToSql()` — export to SQL, excluding regeneratable tables (vec_chunks, similarity_cache, entities_fts*)
- [ ] Implement `loadFromSql()` — import from SQL dump, rebuild vec_chunks via re-embedding
- [ ] Write tests: init, insert, query, dump/load round-trip

### lib/embedder.ts
- [ ] Implement `Embedder` interface (modelName, dimensions, embed, embedOne)
- [ ] Implement `createOllamaEmbedder()` — wraps `ollama` npm package
- [ ] Implement `serializeEmbedding()` — Float32Array to Buffer (struct pack equivalent)
- [ ] Implement `deserializeEmbedding()` — Buffer to Float32Array
- [ ] Write parity test: embed same text with Python and TS, compare vectors

### commands/kg.ts
- [ ] Implement `init` subcommand — calls db.initSchema, reports status
- [ ] Implement `ingest` subcommand — find files by entity type, chunk, embed, store
- [ ] Implement `search` subcommand — embed query, cosine distance search via vec0
- [ ] Implement `similar` subcommand — find entities similar to a given slug
- [ ] Implement `stats` subcommand — count entities, chunks, embeddings, cache entries
- [ ] Implement `dump` subcommand — calls db.dumpToSql
- [ ] Implement `load` subcommand — calls db.loadFromSql
- [ ] Implement `watch` subcommand — `Bun.watch()` on context dirs, auto-ingest on change

### Parity validation
- [ ] Ingest same set of files with both Python and TS
- [ ] Run same search queries, compare top-10 results (entity slugs and scores)
- [ ] Dump from Python, load in TS, verify search still works
- [ ] Dump from TS, load in Python, verify search still works (cross-compat)

### Justfile cutover
- [ ] Update `kg-init` recipe
- [ ] Update `kg-ingest` recipe
- [ ] Update `kg-search` recipe
- [ ] Update `kg-stats` recipe
- [ ] Update `kg-dump` recipe
- [ ] Update `kg-load` recipe
- [ ] Update `kg-watch` recipe

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No results found (search), stale entities (check) |
| 2 | Process error (DB, extension load failure, Ollama unavailable) |

## Notes

- The gate task is the most important — run it first, before writing any other code in this phase
- `better-sqlite3` is synchronous, which simplifies query code (no await needed for DB operations)
- Float32Array is the natural TypeScript equivalent of Python's `list[float]` for embeddings
- The `ollama` npm package mirrors the Python client's API shape
- The `sentence-transformers` fallback is intentionally dropped — Ollama is the sole backend
- If the gate fails, update PLAN.md Phase 6 status to `skipped` and Phase 7 to keep Python deps for KG
- File watching: prefer `Bun.watch()` (built-in) over `chokidar` (external dep)
