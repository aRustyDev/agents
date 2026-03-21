---
id: a7c3f210-4e85-4b9a-b1d2-9f8e7d6c5a43
project:
  id: 00000000-0000-0000-0000-000000000000
title: Search Enhancements Roadmap
status: draft
tags: [roadmap, search, meilisearch]
related:
  depends-on: [33e4f823-9e9d-4e9b-8e5d-62ab50d07466]
---

# Search Enhancements Roadmap

## Issues

Epic: `ai-0nr`

| Phase | Issue | Milestone | Status |
|-------|-------|-----------|--------|
| phase-1 | `ai-5cg` | v0.1.0 | open (ready) |
| phase-2 | `ai-l61` | v0.1.0 | open (ready) |
| phase-3 | `ai-dsg` | v0.1.0 | open (ready) |
| phase-4 | `ai-mv0` | v0.2.0 | open (blocked by 1,2,3) |
| phase-5 | `ai-21m` | v0.2.0 | open (blocked by 4) |

## Milestones

| Milestone | Description | Version Bump |
|-----------|-------------|--------------|
| v0.1.0 | Foundation: chunker improvements + Meilisearch client + hybrid search | minor |
| v0.2.0 | KG commands working via Meilisearch with graceful degradation | minor |

## Dependencies

```
phase-1 (chunker) ────────────────────────────────┐
phase-2 (meilisearch) ───────────────────────────→ phase-4 (kg commands) → phase-5 (degradation)
phase-3 (hybrid search / RRF) ────────────────────┘
```

Phases 1, 2, 3 can all run in parallel. Phase 4 depends on all three. Phase 5 depends on 4.
