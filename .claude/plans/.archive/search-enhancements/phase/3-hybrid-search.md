---
id: 33df6c11-d332-4948-9bbe-31c000099fa2
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 3: Hybrid Search Module"
status: pending
related:
  depends-on: [33e4f823-9e9d-4e9b-8e5d-62ab50d07466]
---

# Phase 3: Hybrid Search Module

**ID:** `phase-3`
**Dependencies:** None
**Status:** pending
**Effort:** Small

## Objective

Create a standalone search module that combines keyword and semantic results using Reciprocal Rank Fusion (RRF). This module is backend-agnostic — it merges ranked lists regardless of whether they come from Meilisearch, sqlite-vec, or any other source.

## Success Criteria

- [ ] `lib/search.ts` exports RRF merge function
- [ ] Merges two ranked result lists into a single relevance-ordered list
- [ ] Deduplicates semantic chunk results by parent entity ID
- [ ] Handles edge cases: one list empty, both empty, same item in both lists
- [ ] All tests pass

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Search module | `.scripts/lib/search.ts` | TypeScript |
| Test suite | `.scripts/test/search.test.ts` | TypeScript |

## Files

**Create:**
- `.scripts/lib/search.ts`
- `.scripts/test/search.test.ts`

**Modify:**
- None

## Tasks

### lib/search.ts
- [ ] Implement `rrfMerge(keywordResults, semanticResults, opts?)` — Reciprocal Rank Fusion

```typescript
interface RankedResult {
  id: string
  entityId?: string  // For chunk deduplication (chunk → parent entity)
  score?: number
  source: 'keyword' | 'semantic'
}

interface MergedResult {
  id: string
  rrfScore: number
  sources: ('keyword' | 'semantic')[]
  keywordRank?: number
  semanticRank?: number
}

interface RRFOptions {
  k?: number          // RRF constant (default: 60)
  limit?: number      // Max results (default: 10)
  deduplicateBy?: 'id' | 'entityId'  // Dedup semantic chunks by parent
}

function rrfMerge(
  keywordResults: RankedResult[],
  semanticResults: RankedResult[],
  opts?: RRFOptions,
): MergedResult[]
```

- [ ] RRF formula: `score = 1 / (k + rank)` where rank is 1-based position
- [ ] Sum scores across both lists for items appearing in both
- [ ] Deduplicate semantic results by `entityId` (keep highest-ranked chunk per entity)
- [ ] Sort final results by combined RRF score descending
- [ ] Apply limit

### lib/search.ts — Hybrid search orchestrator
- [ ] Implement `hybridSearch(query, opts)` — coordinates keyword + semantic search

```typescript
interface HybridSearchOpts {
  keywordSearch: (query: string) => Promise<RankedResult[]>
  semanticSearch?: (query: string) => Promise<RankedResult[]>  // Optional!
  rrfK?: number
  limit?: number
}

async function hybridSearch(
  query: string,
  opts: HybridSearchOpts,
): Promise<MergedResult[]>
```

- [ ] If `semanticSearch` is provided and returns results, merge via RRF
- [ ] If `semanticSearch` is not provided or returns empty, return keyword results only
- [ ] This is the graceful degradation point

### Tests
- [ ] Test RRF with two non-overlapping lists — interleaved by score
- [ ] Test RRF with overlapping items — boosted score for items in both
- [ ] Test RRF with one empty list — returns the other list's items
- [ ] Test RRF with both empty — returns empty
- [ ] Test deduplication by entityId — keeps highest-ranked chunk per entity
- [ ] Test k parameter affects ranking distribution
- [ ] Test limit parameter
- [ ] Test `hybridSearch` with semantic available — merges results
- [ ] Test `hybridSearch` without semantic — returns keyword only

## Notes

- RRF with k=60 is the standard value used by Elasticsearch, Meilisearch, and mdq
- This module has zero external dependencies — pure TypeScript logic
- The `hybridSearch` function accepts search functions as parameters, making it testable without any backend
- This module is reusable: works with Meilisearch, sqlite-vec, or any future search backend
