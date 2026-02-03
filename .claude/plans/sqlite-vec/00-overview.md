# sqlite-vec Implementation Plan

## Overview

Implement semantic search and knowledge graph capabilities using SQLite with the sqlite-vec extension.

## Goal

Enable semantic search, similarity detection, and relationship analysis across all context components (skills, agents, rules, plugins, MCP servers, etc.).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    File System                               │
│  context/agents/*.md  context/skills/*/SKILL.md  etc.       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Embedding Pipeline                        │
│  scripts/embed.py + scripts/lib/{chunker,embedder}.py       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLite + sqlite-vec                       │
│  .data/mcp/knowledge-graph.db                               │
│  Tables: entities, chunks, embedding_meta, vec_chunks       │
└─────────────────────────────────────────────────────────────┘
```

## Tasks

| # | Task | Blocked By | Status |
|---|------|------------|--------|
| 1 | [Install sqlite-vec](01-install-sqlite-vec.md) | - | pending |
| 2 | [Initialize database](02-init-database.md) | 1 | pending |
| 3 | [Implement embedder](03-embedder.md) | 1 | pending |
| 4 | [Implement chunker](04-chunker.md) | - | pending |
| 5 | [Implement ingestion pipeline](05-ingestion.md) | 2, 3, 4 | pending |
| 6 | [Implement file watcher](06-file-watcher.md) | 5 | pending |
| 7 | [Implement similarity cache](07-similarity-cache.md) | 5 | pending |
| 8 | [Add justfile targets](08-justfile.md) | 5 | pending |
| 9 | [End-to-end testing](09-testing.md) | 6, 7, 8 | pending |

## Entry Point

After all tasks complete, the system is started via:

```bash
just init
```

Which runs: `brew bundle` → `uv sync` → `ollama pull` → `scripts/init-db.py`

## References

- ADR docs: `docs/src/adr/*.md`
- Schema: `.data/mcp/knowledge-graph.schema.sql`
- Pipeline design: `docs/src/embedding-pipeline.md`
- Query patterns: `docs/src/sql/common-queries.md`
