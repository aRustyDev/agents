/**
 * Hybrid search module -- combines keyword and semantic search results
 * using Reciprocal Rank Fusion (RRF).
 *
 * Backend-agnostic: works with any search backend that returns ranked results.
 * Zero external dependencies -- pure TypeScript logic.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface RankedResult {
  id: string
  entityId?: string // For chunk deduplication (chunk -> parent entity)
  score?: number // Original score from the backend (informational)
  source: 'keyword' | 'semantic'
  [key: string]: unknown // Pass through additional fields
}

export interface MergedResult {
  id: string
  rrfScore: number
  sources: ('keyword' | 'semantic')[]
  keywordRank?: number // 1-based position in keyword results
  semanticRank?: number // 1-based position in semantic results
  [key: string]: unknown // Merged pass-through fields
}

export interface RRFOptions {
  k?: number // RRF constant (default: 60)
  limit?: number // Max results (default: 10)
  deduplicateBy?: 'id' | 'entityId' // Dedup semantic chunks by parent
}

export type SearchMode = 'hybrid' | 'keyword-only' | 'unavailable'

export interface SearchMeta {
  mode: SearchMode
  reason?: string
  keywordCount: number
  semanticCount: number
  mergedCount: number
}

export interface HybridSearchResult {
  results: MergedResult[]
  meta: SearchMeta
}

export interface HybridSearchOpts {
  keywordSearch: (query: string) => Promise<RankedResult[]>
  semanticSearch?: (query: string) => Promise<RankedResult[]>
  rrfK?: number
  limit?: number
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/** Fields that belong to MergedResult and should not be overwritten by pass-through. */
const RESERVED_KEYS = new Set(['id', 'rrfScore', 'sources', 'keywordRank', 'semanticRank'])

/**
 * Deduplicate a ranked result list by a given key.
 * For each unique key value, keeps only the first (highest-ranked) entry.
 */
function deduplicateByKey(results: RankedResult[], key: 'id' | 'entityId'): RankedResult[] {
  const seen = new Set<string>()
  const out: RankedResult[] = []

  for (const r of results) {
    const dedupKey = key === 'entityId' ? (r.entityId ?? r.id) : r.id
    if (!seen.has(dedupKey)) {
      seen.add(dedupKey)
      out.push(r)
    }
  }

  return out
}

/**
 * Copy pass-through fields from a RankedResult into a MergedResult accumulator.
 * Keyword fields take precedence over semantic fields for conflicts.
 */
function mergePassthrough(
  target: Record<string, unknown>,
  source: RankedResult,
  overwrite: boolean
): void {
  for (const [key, value] of Object.entries(source)) {
    if (RESERVED_KEYS.has(key) || key === 'source' || key === 'score') continue
    if (overwrite || !(key in target)) {
      target[key] = value
    }
  }
}

// ---------------------------------------------------------------------------
// rrfMerge
// ---------------------------------------------------------------------------

/**
 * Merge two ranked result lists using Reciprocal Rank Fusion.
 * RRF score = sum(1 / (k + rank)) across all lists where the item appears.
 *
 * @param keywordResults - Results from keyword/full-text search
 * @param semanticResults - Results from vector/semantic search
 * @param opts - RRF options (k constant, limit, deduplication)
 */
export function rrfMerge(
  keywordResults: RankedResult[],
  semanticResults: RankedResult[],
  opts?: RRFOptions
): MergedResult[] {
  const k = opts?.k ?? 60
  const limit = opts?.limit ?? 10

  // Optionally deduplicate semantic results by entityId
  const dedupedSemantic =
    opts?.deduplicateBy === 'entityId'
      ? deduplicateByKey(semanticResults, 'entityId')
      : semanticResults

  // Accumulator: id -> partial MergedResult (built up incrementally)
  const acc = new Map<string, Record<string, unknown>>()

  // Process keyword results (1-based rank)
  for (let i = 0; i < keywordResults.length; i++) {
    const r = keywordResults[i]
    const rank = i + 1
    const rrfContribution = 1 / (k + rank)

    if (!acc.has(r.id)) {
      const entry: Record<string, unknown> = {
        id: r.id,
        rrfScore: 0,
        sources: [],
        keywordRank: undefined,
        semanticRank: undefined,
      }
      acc.set(r.id, entry)
    }

    const entry = acc.get(r.id)!
    entry.rrfScore = (entry.rrfScore as number) + rrfContribution
    entry.keywordRank = rank
    ;(entry.sources as string[]).push('keyword')

    // Keyword fields overwrite (highest precedence)
    mergePassthrough(entry, r, true)
  }

  // Process semantic results (1-based rank)
  for (let i = 0; i < dedupedSemantic.length; i++) {
    const r = dedupedSemantic[i]
    const rank = i + 1
    const rrfContribution = 1 / (k + rank)

    if (!acc.has(r.id)) {
      const entry: Record<string, unknown> = {
        id: r.id,
        rrfScore: 0,
        sources: [],
        keywordRank: undefined,
        semanticRank: undefined,
      }
      acc.set(r.id, entry)
    }

    const entry = acc.get(r.id)!
    entry.rrfScore = (entry.rrfScore as number) + rrfContribution
    entry.semanticRank = rank

    if (!(entry.sources as string[]).includes('semantic')) {
      ;(entry.sources as string[]).push('semantic')
    }

    // Semantic fields only fill gaps (keyword takes precedence)
    mergePassthrough(entry, r, false)
  }

  // Sort by RRF score descending, then by id for deterministic tie-breaking
  const sorted = [...acc.values()].sort((a, b) => {
    const scoreDiff = (b.rrfScore as number) - (a.rrfScore as number)
    if (scoreDiff !== 0) return scoreDiff
    return (a.id as string).localeCompare(b.id as string)
  })

  return sorted.slice(0, limit) as MergedResult[]
}

// ---------------------------------------------------------------------------
// hybridSearch
// ---------------------------------------------------------------------------

/**
 * Orchestrate a hybrid search: run keyword and optional semantic search,
 * merge results via RRF, report which mode was used.
 */
export async function hybridSearch(
  query: string,
  opts: HybridSearchOpts
): Promise<HybridSearchResult> {
  const { keywordSearch, semanticSearch, rrfK, limit } = opts

  // Run keyword search
  let keywordResults: RankedResult[]
  try {
    keywordResults = await keywordSearch(query)
  } catch (e) {
    // Keyword search failed -- nothing to fall back to
    return {
      results: [],
      meta: {
        mode: 'unavailable',
        reason: `keyword search failed: ${e instanceof Error ? e.message : String(e)}`,
        keywordCount: 0,
        semanticCount: 0,
        mergedCount: 0,
      },
    }
  }

  // If no semantic search function provided, return keyword-only
  if (!semanticSearch) {
    const results = rrfMerge(keywordResults, [], { k: rrfK, limit })
    return {
      results,
      meta: {
        mode: 'keyword-only',
        reason: 'no semantic search provided',
        keywordCount: keywordResults.length,
        semanticCount: 0,
        mergedCount: results.length,
      },
    }
  }

  // Try semantic search
  let semanticResults: RankedResult[]
  try {
    semanticResults = await semanticSearch(query)
  } catch (e) {
    // Semantic search failed -- graceful degradation to keyword-only
    const results = rrfMerge(keywordResults, [], { k: rrfK, limit })
    return {
      results,
      meta: {
        mode: 'keyword-only',
        reason: `semantic search failed: ${e instanceof Error ? e.message : String(e)}`,
        keywordCount: keywordResults.length,
        semanticCount: 0,
        mergedCount: results.length,
      },
    }
  }

  // Semantic returned but empty
  if (semanticResults.length === 0) {
    const results = rrfMerge(keywordResults, [], { k: rrfK, limit })
    return {
      results,
      meta: {
        mode: 'keyword-only',
        reason: 'no semantic results',
        keywordCount: keywordResults.length,
        semanticCount: 0,
        mergedCount: results.length,
      },
    }
  }

  // Both available -- hybrid merge
  const results = rrfMerge(keywordResults, semanticResults, { k: rrfK, limit })
  return {
    results,
    meta: {
      mode: 'hybrid',
      keywordCount: keywordResults.length,
      semanticCount: semanticResults.length,
      mergedCount: results.length,
    },
  }
}
