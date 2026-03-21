---
id: 33e4f823-9e9d-4e9b-8e5d-62ab50d07466
project:
  id: 00000000-0000-0000-0000-000000000000
title: Search Enhancements — Meilisearch + Hybrid Search
status: archived
tags: [search, meilisearch, hybrid, embeddings]
related:
  depends-on: [bcb4f31b-e0a1-4bf5-af73-d36426442250]
---

# Search Enhancements — Meilisearch + Hybrid Search

**Created:** 2026-03-18
**Updated:** 2026-03-19
**Owner:** aRustyDev

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Pure-TypeScript search path via Meilisearch (no Python dependency) | Yes | `ai-tools kg search` works without `uv run python` |
| 2 | Hybrid search combining keyword + semantic results | Yes | RRF-merged results outperform keyword-only in relevance |
| 3 | Improved chunking with overlap and title context for better embeddings | Yes | Chunk overlap parameter available; title prepended to embedded text |
| 4 | Graceful degradation — search works without embeddings | Yes | `ai-tools kg search` returns keyword results when Ollama is down |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Search runtimes | Python only (sqlite-vec) | TypeScript (Meilisearch) + Python fallback | TS path missing |
| Search modes | Vector-only (semantic) | Hybrid (keyword + semantic via RRF) | No keyword search |
| Chunk overlap | 0 tokens | 64 tokens (~256 chars) | No overlap |
| Embedding context | Chunk text only | Title + chunk text | No title prefix |
| Embedding requirement | Required (search fails without it) | Optional (keyword fallback) | No degradation |

## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-1 | Chunker Improvements | **done** | - | Overlap parameter works, title prepend in embedder |
| phase-2 | Meilisearch Client | **done** | - | Index/search/embed against running Meilisearch |
| phase-3 | Hybrid Search Module | **done** | - | RRF merges keyword + semantic results |
| phase-4 | KG Commands Integration | **done** | phase-2, phase-3 | `ai-tools kg` commands work via Meilisearch |
| phase-5 | Graceful Degradation | **done** | phase-4 | Search works without embeddings |

### Phase Details

1. [Phase 1: Chunker Improvements](./phase/1-chunker-improvements.md)
2. [Phase 2: Meilisearch Client](./phase/2-meilisearch-client.md)
3. [Phase 3: Hybrid Search Module](./phase/3-hybrid-search.md)
4. [Phase 4: KG Commands Integration](./phase/4-kg-commands.md)
5. [Phase 5: Graceful Degradation](./phase/5-graceful-degradation.md)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Meilisearch Docker service not running | Medium | Medium | `ai-tools kg search` checks connectivity first, falls back to error with `just mcp-up` hint |
| Embedding quality differs between sqlite-vec and Meilisearch vector storage | Low | Low | Same Ollama model + same chunking = same embeddings; storage format differs but similarity math is equivalent |
| Meilisearch vector search performance at scale | Low | Medium | Meilisearch handles millions of documents; our corpus is <10K chunks |

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Planning complete | 2026-03-18 | 2026-03-18 |
| Phase 1 complete (chunker) | | 2026-03-19 |
| Phase 2 complete (meilisearch client) | | 2026-03-19 |
| Phase 3 complete (hybrid search) | | 2026-03-19 |
| Phase 4 complete (kg commands) | | 2026-03-19 |
| Phase 5 complete (degradation) | | 2026-03-19 |

## Rollback Strategy

Meilisearch is additive — the Python KG system remains untouched. If Meilisearch proves problematic, the `ai-tools kg` commands can be reverted to stubs pointing back to Python. No data migration is needed since Meilisearch indexes are rebuilt from source files.

## Notes

- Meilisearch currently runs externally (dotfiles); Phase 2 adds it to `.docker/compose.yaml` for `just mcp-up`
- The `meilisearch` npm package is the official JS client
- Phases 1 and 2 can run in parallel (no dependencies between them)
- This work builds on ADR-011 (Bun/TS migration) — the KG was the one system that couldn't migrate due to sqlite-vec; Meilisearch provides the alternative path
- mdq (aaronshaf/mdq) validated this architecture: Bun + Meilisearch + Ollama + hybrid search works well
