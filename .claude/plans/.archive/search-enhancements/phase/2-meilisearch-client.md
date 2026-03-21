---
id: f10aecdc-fd97-422e-a113-56674c3e1fe5
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 2: Meilisearch Client"
status: pending
related:
  depends-on: [33e4f823-9e9d-4e9b-8e5d-62ab50d07466]
---

# Phase 2: Meilisearch Client

**ID:** `phase-2`
**Dependencies:** None
**Status:** pending
**Effort:** Medium

## Objective

Create a TypeScript Meilisearch client module that handles indexing, searching, and vector embedding storage. This replaces the Python sqlite-vec path with a pure-TypeScript alternative using the existing Meilisearch Docker service.

## Success Criteria

- [ ] `lib/meilisearch.ts` connects to running Meilisearch instance
- [ ] Can index all context entities (skills, plugins, commands, rules, agents)
- [ ] Can perform keyword search with typo tolerance, filtering, and highlighting
- [ ] Can store and query vector embeddings via Meilisearch's vector search
- [ ] Can check connectivity and report status
- [ ] Tests pass against a running Meilisearch instance (skip if unavailable)

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Meilisearch client module | `.scripts/lib/meilisearch.ts` | TypeScript |
| Test suite | `.scripts/test/meilisearch.test.ts` | TypeScript |

## Files

**Create:**
- `.scripts/lib/meilisearch.ts`
- `.scripts/test/meilisearch.test.ts`

**Modify:**
- `.scripts/package.json` — add `meilisearch` dependency

## Tasks

### Dependencies
- [ ] `bun add meilisearch` — official Meilisearch JS client

### lib/meilisearch.ts — Connection
- [ ] `createClient(opts?: { host?: string; apiKey?: string }): MeiliSearch` — defaults to `MEILI_HOST` env var or `http://localhost:7700`
- [ ] `checkHealth(): Promise<Result<{ status: string; version: string }>>` — verify Meilisearch is running
- [ ] `ensureIndexes(): Promise<void>` — create `documents` and `chunks` indexes if they don't exist

### lib/meilisearch.ts — Indexing
- [ ] `indexEntity(entity: IndexableEntity): Promise<void>` — add/update a single entity
- [ ] `indexAll(entities: IndexableEntity[]): Promise<{ indexed: number; errors: string[] }>` — batch index
- [ ] `deleteEntity(id: string): Promise<void>` — remove by ID

```typescript
interface IndexableEntity {
  id: string                    // Unique ID (slug or path-based)
  type: EntityType              // skill, plugin, command, etc.
  name: string
  title?: string
  description?: string
  content: string               // Full text content
  tags?: string[]
  filePath: string
  fileHash: string              // For change detection
  createdAt?: string
  updatedAt?: string
}
```

### lib/meilisearch.ts — Keyword search
- [ ] `searchKeyword(query: string, opts?: SearchOpts): Promise<SearchResult[]>` — full-text search
- [ ] Support filtering: `type`, `tags`, `updatedAfter`
- [ ] Support highlighting in results (cropped snippets)
- [ ] Support limit and offset

```typescript
interface SearchOpts {
  limit?: number
  offset?: number
  type?: EntityType
  tags?: string[]
  updatedAfter?: string
  sort?: 'updatedAt:desc' | 'updatedAt:asc'
}

interface SearchResult {
  id: string
  type: EntityType
  name: string
  description?: string
  snippet?: string              // Highlighted match snippet
  score?: number
  filePath: string
}
```

### lib/meilisearch.ts — Vector search
- [ ] `indexChunks(entityId: string, chunks: EmbeddedChunk[]): Promise<void>` — store chunks with vectors
- [ ] `searchSemantic(query: string, embedding: number[], opts?: SearchOpts): Promise<SearchResult[]>` — vector similarity search
- [ ] Chunks stored in separate `chunks` index with `_vectors.default` field

```typescript
interface EmbeddedChunk {
  id: string                    // entityId_chunkIndex
  entityId: string
  chunkIndex: number
  text: string
  embedding: number[]           // Vector from Ollama
}
```

### lib/meilisearch.ts — Index configuration
- [ ] Configure `documents` index: searchable attributes (name, description, content), filterable (type, tags), sortable (updatedAt)
- [ ] Configure `chunks` index: searchable attributes (text), filterable (entityId), vector dimensions (auto-detected from first embedding)
- [ ] Set ranking rules for relevance

### Tests
- [ ] Test `checkHealth()` — skip all tests if Meilisearch is not running
- [ ] Test `indexEntity()` + `searchKeyword()` round-trip
- [ ] Test filtering by type and tags
- [ ] Test highlighting in results
- [ ] Test `indexChunks()` + `searchSemantic()` round-trip (requires Ollama for embedding)
- [ ] Test `deleteEntity()` removes from both indexes

## Tasks (additional)

### Add Meilisearch to Docker compose
- [ ] Add Meilisearch service to `.docker/compose.yaml`
- [ ] Image: `getmeili/meilisearch:latest` (or pin a version)
- [ ] Port: `7700:7700`
- [ ] Volume: persist data to `.data/meilisearch/` (gitignored via `*.db` pattern)
- [ ] Environment: `MEILI_ENV=development`, `MEILI_NO_ANALYTICS=true`
- [ ] This consolidates Meilisearch startup into `just mcp-up` alongside crawl4ai

## Notes

- Meilisearch currently runs externally at `/private/etc/dotfiles/adam/services/databases/meilisearch/`
- After this phase, it will also be available via `just mcp-up` (Docker compose)
- Default host: `http://localhost:7700`, configurable via `MEILI_HOST`
- Default API key: none for development, configurable via `MEILI_MASTER_KEY`
- The `meilisearch` npm package is ~30KB, zero native deps, Bun-compatible
- Entity discovery reuses the same `ENTITY_PATTERNS` glob patterns from the Python `embed.py`
- File hash comparison (via `lib/hash.ts`) enables incremental indexing (skip unchanged files)
- Registry crawler output already goes to Meilisearch indices (at the dotfiles path) — this plan brings KG indexing into the same system
