---
id: e55608bb-a654-46b6-a393-e43f20154ca1
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 5: Graceful Degradation"
status: pending
related:
  depends-on: [f05d12a2-b112-4b69-9a59-84110024d0d2]
---

# Phase 5: Graceful Degradation

**ID:** `phase-5`
**Dependencies:** phase-4
**Status:** pending
**Effort:** Small

## Objective

Add service health detection and user-friendly error messages so search commands degrade gracefully. Phase 3's `hybridSearch()` already handles the core degradation (semantic is optional) — this phase wraps it with service detection and actionable error messages.

## Success Criteria

- [ ] `ai-tools kg search` reports which mode it used (hybrid vs keyword-only) via `[info]` or `meta.mode` in JSON
- [ ] `ai-tools kg search` shows actionable error when Meilisearch is down ("Start with: just mcp-up")
- [ ] `ai-tools kg ingest --embed` warns and continues when Ollama is unavailable
- [ ] Health check functions exist for both Meilisearch and Ollama

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Health check utilities | `cli/lib/meilisearch.ts` (additions) | TypeScript |
| Ollama health check | `cli/lib/embedder.ts` (additions) | TypeScript |
| Mode reporting | `cli/commands/kg.ts` (modifications) | TypeScript |
| Tests | `cli/test/degradation.test.ts` | TypeScript |

## Files

**Create:**
- `cli/test/degradation.test.ts`

**Modify:**
- `cli/lib/meilisearch.ts` — add `isAvailable()`, `hasEmbeddings()`
- `cli/lib/embedder.ts` — add `isOllamaAvailable()`, `hasModel()`
- `cli/commands/kg.ts` — add mode reporting to search output

## Tasks

### Health checks (~20 lines each)
- [ ] `isAvailable(): Promise<boolean>` in `lib/meilisearch.ts` — fetch health endpoint
- [ ] `hasEmbeddings(): Promise<boolean>` in `lib/meilisearch.ts` — check chunks index has vectors
- [ ] `isOllamaAvailable(): Promise<boolean>` in `lib/embedder.ts` — check Ollama responds
- [ ] `hasModel(model: string): Promise<boolean>` in `lib/embedder.ts` — check model is pulled

### Actionable error messages
- [ ] Meilisearch down: `"Meilisearch not running. Start with: just mcp-up"`
- [ ] Ollama down: `"Ollama not running. Start with: ollama serve"`
- [ ] Model missing: `"Model not pulled. Run: ollama pull nomic-embed-text"`
- [ ] No embeddings: `"No embeddings indexed. Run: ai-tools kg embed"`

### Mode reporting in search command
- [ ] Add `SearchMeta` type: `{ mode: 'hybrid' | 'keyword-only'; reason?: string }`
- [ ] Human mode: `[info] Search mode: hybrid (keyword + semantic)` or `[info] Search mode: keyword-only (Ollama unavailable)`
- [ ] JSON mode: include `meta` field in response object

### Tests
- [ ] Mock unavailable Ollama → search returns keyword results with mode: 'keyword-only'
- [ ] Mock unavailable Meilisearch → returns error with actionable message
- [ ] Health check functions return correct boolean values

## Notes

- This phase is intentionally small — Phase 3's `hybridSearch()` already handles the core `semanticSearch` being undefined. This phase only adds detection + messaging.
- The `--require-embeddings` flag for CI can be added later if needed (YAGNI for now)
- Ingest without `--embed` already works by design (Phase 4) — this phase just adds the warning when `--embed` fails
