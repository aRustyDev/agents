import { describe, expect, test } from 'bun:test'
import { hybridSearch, type MergedResult, type RankedResult, rrfMerge } from '../lib/search'

// ---------------------------------------------------------------------------
// Test data
// ---------------------------------------------------------------------------

const keywordResults: RankedResult[] = [
  { id: 'doc-1', source: 'keyword', name: 'Alpha' },
  { id: 'doc-2', source: 'keyword', name: 'Beta' },
  { id: 'doc-3', source: 'keyword', name: 'Gamma' },
]

const semanticResults: RankedResult[] = [
  { id: 'doc-2', source: 'semantic', name: 'Beta' },
  { id: 'doc-4', source: 'semantic', name: 'Delta' },
  { id: 'doc-1', source: 'semantic', name: 'Alpha' },
]

// ---------------------------------------------------------------------------
// rrfMerge
// ---------------------------------------------------------------------------

describe('rrfMerge', () => {
  test('two non-overlapping lists are interleaved by RRF score', () => {
    const kw: RankedResult[] = [
      { id: 'a', source: 'keyword' },
      { id: 'b', source: 'keyword' },
      { id: 'c', source: 'keyword' },
    ]
    const sem: RankedResult[] = [
      { id: 'x', source: 'semantic' },
      { id: 'y', source: 'semantic' },
      { id: 'z', source: 'semantic' },
    ]

    const merged = rrfMerge(kw, sem, { limit: 20 })

    expect(merged.length).toBe(6)
    // Items at same position in their respective lists should have equal RRF scores.
    // rank 1 items (a and x) tied, then rank 2 (b and y) tied, then rank 3 (c and z) tied.
    // With deterministic tie-breaking by id: a < x, b < y, c < z
    expect(merged[0].id).toBe('a')
    expect(merged[1].id).toBe('x')
    expect(merged[2].id).toBe('b')
    expect(merged[3].id).toBe('y')
    expect(merged[4].id).toBe('c')
    expect(merged[5].id).toBe('z')

    // Each item appears in only one source
    for (const r of merged) {
      expect(r.sources.length).toBe(1)
    }
  })

  test('overlapping items get boosted (higher RRF score)', () => {
    const merged = rrfMerge(keywordResults, semanticResults, { limit: 20 })

    // doc-1 and doc-2 appear in both lists, so they should have higher scores
    const scores = new Map(merged.map((r) => [r.id, r.rrfScore]))

    // doc-2 is rank 2 in keyword and rank 1 in semantic
    // doc-1 is rank 1 in keyword and rank 3 in semantic
    // Both should score higher than doc-3 (keyword only, rank 3) and doc-4 (semantic only, rank 2)
    expect(scores.get('doc-2')!).toBeGreaterThan(scores.get('doc-3')!)
    expect(scores.get('doc-2')!).toBeGreaterThan(scores.get('doc-4')!)
    expect(scores.get('doc-1')!).toBeGreaterThan(scores.get('doc-3')!)
    expect(scores.get('doc-1')!).toBeGreaterThan(scores.get('doc-4')!)
  })

  test('one empty keyword list returns semantic items', () => {
    const merged = rrfMerge([], semanticResults, { limit: 20 })

    expect(merged.length).toBe(3)
    expect(merged[0].id).toBe('doc-2')
    expect(merged[0].sources).toEqual(['semantic'])
    expect(merged[0].semanticRank).toBe(1)
    expect(merged[0].keywordRank).toBeUndefined()
  })

  test('one empty semantic list returns keyword items', () => {
    const merged = rrfMerge(keywordResults, [], { limit: 20 })

    expect(merged.length).toBe(3)
    expect(merged[0].id).toBe('doc-1')
    expect(merged[0].sources).toEqual(['keyword'])
    expect(merged[0].keywordRank).toBe(1)
    expect(merged[0].semanticRank).toBeUndefined()
  })

  test('both empty returns empty array', () => {
    const merged = rrfMerge([], [])
    expect(merged).toEqual([])
  })

  test('deduplication by entityId keeps highest-ranked chunk per entity', () => {
    const sem: RankedResult[] = [
      { id: 'chunk-1a', entityId: 'entity-1', source: 'semantic', score: 0.9 },
      { id: 'chunk-2a', entityId: 'entity-2', source: 'semantic', score: 0.8 },
      { id: 'chunk-1b', entityId: 'entity-1', source: 'semantic', score: 0.7 },
      { id: 'chunk-2b', entityId: 'entity-2', source: 'semantic', score: 0.6 },
    ]

    const merged = rrfMerge([], sem, {
      deduplicateBy: 'entityId',
      limit: 20,
    })

    // Only 2 results (one per entity), keeping highest-ranked chunk
    expect(merged.length).toBe(2)
    expect(merged[0].id).toBe('chunk-1a')
    expect(merged[1].id).toBe('chunk-2a')
  })

  test('deduplication by entityId falls back to id when entityId is missing', () => {
    const sem: RankedResult[] = [
      { id: 'no-entity-1', source: 'semantic' },
      { id: 'no-entity-2', source: 'semantic' },
    ]

    const merged = rrfMerge([], sem, {
      deduplicateBy: 'entityId',
      limit: 20,
    })

    // Both should appear since they have unique ids (entityId falls back to id)
    expect(merged.length).toBe(2)
  })

  test('lower k gives more weight to top results', () => {
    const kw: RankedResult[] = [
      { id: 'top', source: 'keyword' },
      { id: 'bottom', source: 'keyword' },
    ]

    // With low k, the gap between rank 1 and rank 2 scores is larger
    const lowK = rrfMerge(kw, [], { k: 1, limit: 20 })
    const highK = rrfMerge(kw, [], { k: 100, limit: 20 })

    const lowKGap = lowK[0].rrfScore - lowK[1].rrfScore
    const highKGap = highK[0].rrfScore - highK[1].rrfScore

    expect(lowKGap).toBeGreaterThan(highKGap)
  })

  test('limit parameter respects max results', () => {
    const many: RankedResult[] = Array.from({ length: 20 }, (_, i) => ({
      id: `item-${i}`,
      source: 'keyword' as const,
    }))

    const merged = rrfMerge(many, [], { limit: 5 })
    expect(merged.length).toBe(5)
  })

  test('default limit is 10', () => {
    const many: RankedResult[] = Array.from({ length: 20 }, (_, i) => ({
      id: `item-${i}`,
      source: 'keyword' as const,
    }))

    const merged = rrfMerge(many, [])
    expect(merged.length).toBe(10)
  })

  test('pass-through fields are preserved in merged results', () => {
    const kw: RankedResult[] = [{ id: 'doc-1', source: 'keyword', name: 'Alpha', path: '/a' }]
    const sem: RankedResult[] = [
      { id: 'doc-1', source: 'semantic', name: 'Alpha-semantic', category: 'test' },
    ]

    const merged = rrfMerge(kw, sem, { limit: 10 })

    expect(merged[0].name).toBe('Alpha') // keyword takes precedence
    expect(merged[0].path).toBe('/a') // keyword-only field preserved
    expect(merged[0].category).toBe('test') // semantic-only field preserved
  })

  test('keyword fields take precedence over semantic for conflicts', () => {
    const kw: RankedResult[] = [{ id: 'doc-1', source: 'keyword', title: 'Keyword Title' }]
    const sem: RankedResult[] = [{ id: 'doc-1', source: 'semantic', title: 'Semantic Title' }]

    const merged = rrfMerge(kw, sem, { limit: 10 })
    expect(merged[0].title).toBe('Keyword Title')
  })

  test('keywordRank and semanticRank are tracked correctly', () => {
    const merged = rrfMerge(keywordResults, semanticResults, { limit: 20 })

    const doc1 = merged.find((r) => r.id === 'doc-1')!
    expect(doc1.keywordRank).toBe(1)
    expect(doc1.semanticRank).toBe(3)

    const doc2 = merged.find((r) => r.id === 'doc-2')!
    expect(doc2.keywordRank).toBe(2)
    expect(doc2.semanticRank).toBe(1)

    const doc3 = merged.find((r) => r.id === 'doc-3')!
    expect(doc3.keywordRank).toBe(3)
    expect(doc3.semanticRank).toBeUndefined()

    const doc4 = merged.find((r) => r.id === 'doc-4')!
    expect(doc4.keywordRank).toBeUndefined()
    expect(doc4.semanticRank).toBe(2)
  })

  test('sources array shows which backends contributed', () => {
    const merged = rrfMerge(keywordResults, semanticResults, { limit: 20 })

    const doc1 = merged.find((r) => r.id === 'doc-1')!
    expect(doc1.sources).toContain('keyword')
    expect(doc1.sources).toContain('semantic')
    expect(doc1.sources.length).toBe(2)

    const doc3 = merged.find((r) => r.id === 'doc-3')!
    expect(doc3.sources).toEqual(['keyword'])

    const doc4 = merged.find((r) => r.id === 'doc-4')!
    expect(doc4.sources).toEqual(['semantic'])
  })

  test('RRF score is computed correctly for k=60', () => {
    const kw: RankedResult[] = [{ id: 'a', source: 'keyword' }]
    const sem: RankedResult[] = [{ id: 'a', source: 'semantic' }]

    const merged = rrfMerge(kw, sem, { k: 60, limit: 10 })

    // rank 1 in both lists: 1/(60+1) + 1/(60+1) = 2/61
    const expected = 2 / 61
    expect(merged[0].rrfScore).toBeCloseTo(expected, 10)
  })
})

// ---------------------------------------------------------------------------
// hybridSearch
// ---------------------------------------------------------------------------

describe('hybridSearch', () => {
  test('both search functions return results -> mode: hybrid', async () => {
    const result = await hybridSearch('test query', {
      keywordSearch: async () => keywordResults,
      semanticSearch: async () => semanticResults,
      limit: 20,
    })

    expect(result.meta.mode).toBe('hybrid')
    expect(result.meta.keywordCount).toBe(3)
    expect(result.meta.semanticCount).toBe(3)
    expect(result.results.length).toBeGreaterThan(0)
    expect(result.meta.mergedCount).toBe(result.results.length)
  })

  test('only keyword provided -> mode: keyword-only', async () => {
    const result = await hybridSearch('test query', {
      keywordSearch: async () => keywordResults,
      limit: 20,
    })

    expect(result.meta.mode).toBe('keyword-only')
    expect(result.meta.reason).toBe('no semantic search provided')
    expect(result.meta.keywordCount).toBe(3)
    expect(result.meta.semanticCount).toBe(0)
    expect(result.results.length).toBe(3)
  })

  test('semantic provided but returns empty -> mode: keyword-only', async () => {
    const result = await hybridSearch('test query', {
      keywordSearch: async () => keywordResults,
      semanticSearch: async () => [],
      limit: 20,
    })

    expect(result.meta.mode).toBe('keyword-only')
    expect(result.meta.reason).toBe('no semantic results')
    expect(result.meta.keywordCount).toBe(3)
    expect(result.meta.semanticCount).toBe(0)
  })

  test('semantic provided but throws error -> mode: keyword-only with error info', async () => {
    const result = await hybridSearch('test query', {
      keywordSearch: async () => keywordResults,
      semanticSearch: async () => {
        throw new Error('embedding model unavailable')
      },
      limit: 20,
    })

    expect(result.meta.mode).toBe('keyword-only')
    expect(result.meta.reason).toContain('semantic search failed')
    expect(result.meta.reason).toContain('embedding model unavailable')
    expect(result.meta.keywordCount).toBe(3)
    expect(result.meta.semanticCount).toBe(0)
    expect(result.results.length).toBe(3)
  })

  test('both search functions fail -> mode: unavailable', async () => {
    const result = await hybridSearch('test query', {
      keywordSearch: async () => {
        throw new Error('database connection lost')
      },
      semanticSearch: async () => semanticResults,
    })

    expect(result.meta.mode).toBe('unavailable')
    expect(result.meta.reason).toContain('keyword search failed')
    expect(result.meta.reason).toContain('database connection lost')
    expect(result.results).toEqual([])
    expect(result.meta.keywordCount).toBe(0)
    expect(result.meta.semanticCount).toBe(0)
    expect(result.meta.mergedCount).toBe(0)
  })

  test('limit option passed through to rrfMerge', async () => {
    const manyKeyword: RankedResult[] = Array.from({ length: 20 }, (_, i) => ({
      id: `kw-${i}`,
      source: 'keyword' as const,
    }))
    const manySemantic: RankedResult[] = Array.from({ length: 20 }, (_, i) => ({
      id: `sem-${i}`,
      source: 'semantic' as const,
    }))

    const result = await hybridSearch('test query', {
      keywordSearch: async () => manyKeyword,
      semanticSearch: async () => manySemantic,
      limit: 5,
    })

    expect(result.results.length).toBe(5)
    expect(result.meta.mergedCount).toBe(5)
  })

  test('rrfK option passed through to rrfMerge', async () => {
    const kw: RankedResult[] = [
      { id: 'a', source: 'keyword' },
      { id: 'b', source: 'keyword' },
    ]

    const resultLowK = await hybridSearch('q', {
      keywordSearch: async () => kw,
      rrfK: 1,
      limit: 20,
    })

    const resultHighK = await hybridSearch('q', {
      keywordSearch: async () => kw,
      rrfK: 100,
      limit: 20,
    })

    // Different k values produce different score distributions
    const lowKGap = resultLowK.results[0].rrfScore - resultLowK.results[1].rrfScore
    const highKGap = resultHighK.results[0].rrfScore - resultHighK.results[1].rrfScore
    expect(lowKGap).toBeGreaterThan(highKGap)
  })

  test('meta.keywordCount and meta.semanticCount reflect actual result counts', async () => {
    const kw: RankedResult[] = [
      { id: 'a', source: 'keyword' },
      { id: 'b', source: 'keyword' },
    ]
    const sem: RankedResult[] = [
      { id: 'x', source: 'semantic' },
      { id: 'y', source: 'semantic' },
      { id: 'z', source: 'semantic' },
    ]

    const result = await hybridSearch('q', {
      keywordSearch: async () => kw,
      semanticSearch: async () => sem,
      limit: 20,
    })

    expect(result.meta.keywordCount).toBe(2)
    expect(result.meta.semanticCount).toBe(3)
    expect(result.meta.mergedCount).toBe(5)
  })

  test('keyword-only results are still RRF-scored', async () => {
    const result = await hybridSearch('q', {
      keywordSearch: async () => keywordResults,
      limit: 20,
    })

    // Even without semantic, items should have RRF scores
    for (const r of result.results) {
      expect(r.rrfScore).toBeGreaterThan(0)
    }
  })

  test('semantic throws non-Error value -> graceful degradation', async () => {
    const result = await hybridSearch('q', {
      keywordSearch: async () => keywordResults,
      semanticSearch: async () => {
        throw 'string error'
      },
      limit: 20,
    })

    expect(result.meta.mode).toBe('keyword-only')
    expect(result.meta.reason).toContain('semantic search failed')
    expect(result.meta.reason).toContain('string error')
  })
})
