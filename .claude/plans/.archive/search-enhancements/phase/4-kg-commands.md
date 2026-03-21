---
id: f05d12a2-b112-4b69-9a59-84110024d0d2
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 4: KG Commands Integration"
status: pending
related:
  depends-on: [f10aecdc-fd97-422e-a113-56674c3e1fe5, 33df6c11-d332-4948-9bbe-31c000099fa2]
---

# Phase 4: KG Commands Integration

**ID:** `phase-4`
**Dependencies:** phase-2, phase-3
**Status:** pending
**Effort:** Medium

## Objective

Replace the `ai-tools kg` command stubs with working implementations that use Meilisearch for indexing and hybrid search. This makes `ai-tools kg` fully functional in TypeScript without depending on Python.

## Success Criteria

- [ ] `ai-tools kg init` creates Meilisearch indexes with correct configuration
- [ ] `ai-tools kg ingest --all` indexes all context entities into Meilisearch
- [ ] `ai-tools kg search <query>` returns hybrid search results (keyword + semantic when available)
- [ ] `ai-tools kg stats` shows entity counts from Meilisearch
- [ ] `ai-tools kg ingest` uses file hashes for incremental indexing (skips unchanged files)
- [ ] All commands support `--json` output mode
- [ ] Justfile `kg-*` recipes can optionally point to TypeScript (via env var or flag)

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Updated KG commands | `.scripts/commands/kg.ts` | TypeScript |
| Updated justfile | `justfile` | Just |
| Integration tests | `.scripts/test/kg-commands.test.ts` | TypeScript |

## Files

**Create:**
- `.scripts/test/kg-commands.test.ts`

**Modify:**
- `.scripts/commands/kg.ts` — replace stubs with Meilisearch-backed implementations
- `justfile` — add `kg-search-ts` recipe (or update existing recipes with backend flag)

## Tasks

### commands/kg.ts — init
- [ ] Call `ensureIndexes()` from `lib/meilisearch.ts`
- [ ] Report index status (created vs already exists)
- [ ] Check Meilisearch health first, exit with helpful error if down

### commands/kg.ts — ingest
- [ ] Discover files using `ENTITY_PATTERNS` (same globs as Python embed.py)
- [ ] For each file: read content, parse frontmatter, compute hash
- [ ] Skip files whose hash matches the previously indexed hash (incremental)
- [ ] Chunk content via `lib/chunker.ts` (with overlap)
- [ ] Index entity into Meilisearch `documents` index
- [ ] If `--embed` or `--all`: generate embeddings via Ollama, index chunks with vectors
- [ ] Show progress via spinner/progress bar
- [ ] Report: indexed N entities, skipped M unchanged, embedded K chunks

### commands/kg.ts — search
- [ ] Parse query from positional arg
- [ ] Call `hybridSearch()` from `lib/search.ts`
  - Keyword search: `searchKeyword()` from `lib/meilisearch.ts`
  - Semantic search (if available): embed query via Ollama, `searchSemantic()` from `lib/meilisearch.ts`
- [ ] Display results: table with Name, Type, Score, Snippet
- [ ] `--json` outputs array of SearchResult objects
- [ ] `--limit` controls result count

### commands/kg.ts — stats
- [ ] Query Meilisearch for index stats (document count, chunk count)
- [ ] Show: entities by type, total chunks, embedding status
- [ ] `--json` outputs stats object

### commands/kg.ts — embed
- [ ] Standalone embedding command (separate from ingest)
- [ ] Re-embeds all indexed entities without re-indexing from files
- [ ] Useful when: switching models, Ollama was unavailable during ingest, or embeddings need refresh
- [ ] `--model <name>` to specify embedding model (default: nomic-embed-text)
- [ ] `--reset` to clear existing embeddings and regenerate all
- [ ] Uses chunks from `documents` index, generates vectors, stores in `chunks` index

### commands/kg.ts — similar
- [ ] Embed the target entity's content
- [ ] Search semantically for similar entities
- [ ] Exclude the target entity from results

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No results found (search), stale entities (check) |
| 2 | Process error (Meilisearch down, Ollama unavailable) |

### Justfile integration
- [ ] Add `kg-search-ts` recipe pointing to `ai-tools kg search`
- [ ] Keep existing `kg-search` recipe pointing to Python (backward compat)
- [ ] Add `KG_BACKEND` env var: `python` (default) or `meilisearch`
- [ ] When `KG_BACKEND=meilisearch`, `kg-search` delegates to TypeScript

### Entity discovery patterns
- [ ] Port `ENTITY_PATTERNS` from Python embed.py to TypeScript

```typescript
const ENTITY_PATTERNS: Record<EntityType, string[]> = {
  skill: ['context/skills/*/SKILL.md'],
  plugin: ['context/plugins/*/.claude-plugin/plugin.json'],
  command: ['context/commands/*.md', '.claude/commands/**/*.md'],
  rule: ['context/rules/*.md', 'context/rules/**/*.md'],
  agent: ['context/agents/*.md'],
  claude_md: ['**/CLAUDE.md'],
  output_style: ['context/output-styles/*.md'],
  mcp_server: [],
}
```

## Notes

- Meilisearch must be running (`just mcp-up`) for these commands to work
- The `--embed` flag on `ingest` is what triggers Ollama embedding generation
- Without `--embed`, only keyword search works (graceful degradation — Phase 5)
- The Python KG system remains available as a fallback via `KG_BACKEND=python`
- Incremental indexing uses the same hash approach as the plugin build system
