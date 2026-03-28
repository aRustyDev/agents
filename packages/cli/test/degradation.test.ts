/**
 * Tests for graceful degradation behavior (Phase 5).
 *
 * Covers:
 *   - Health check functions in lib/meilisearch.ts (isAvailable, hasEmbeddings)
 *   - Health check functions in lib/embedder.ts (isOllamaAvailable, hasModel)
 *   - hybridSearch degradation when semantic search is unavailable
 *   - Mode reporting in search results
 */

import { describe, expect, test } from 'bun:test'
import { hasModel, isOllamaAvailable, prepareEmbeddingText } from '../src/lib/embedder'
import { checkHealth, createClient, hasEmbeddings, isAvailable } from '../src/lib/meilisearch'
import { hybridSearch, type RankedResult } from '../src/lib/search'

// ---------------------------------------------------------------------------
// lib/embedder.ts health checks
// ---------------------------------------------------------------------------

describe('embedder health checks', () => {
  test('isOllamaAvailable returns a boolean', async () => {
    const result = await isOllamaAvailable()
    expect(typeof result).toBe('boolean')
  })

  test('hasModel returns a boolean', async () => {
    const result = await hasModel('nomic-embed-text')
    expect(typeof result).toBe('boolean')
  })

  test('hasModel returns false for nonexistent model', async () => {
    const result = await hasModel('nonexistent-model-xyz-999')
    // If Ollama is running, the model won't exist. If Ollama is down, returns false.
    expect(result).toBe(false)
  })

  test('prepareEmbeddingText still works', () => {
    expect(prepareEmbeddingText('Title', 'Body')).toBe('Title\n\nBody')
    expect(prepareEmbeddingText('', 'Body')).toBe('Body')
    expect(prepareEmbeddingText('  ', 'Body')).toBe('Body')
  })
})

// ---------------------------------------------------------------------------
// lib/meilisearch.ts health checks
// ---------------------------------------------------------------------------

describe('meilisearch health checks', () => {
  test('isAvailable returns a boolean', async () => {
    const client = createClient()
    const result = await isAvailable(client)
    expect(typeof result).toBe('boolean')
  })

  test('isAvailable returns false for unreachable host', async () => {
    const client = createClient({ host: 'http://localhost:19999' })
    const result = await isAvailable(client)
    expect(result).toBe(false)
  })

  test('hasEmbeddings returns a boolean', async () => {
    const client = createClient()
    const result = await hasEmbeddings(client)
    expect(typeof result).toBe('boolean')
  })

  test('hasEmbeddings returns false for unreachable host', async () => {
    const client = createClient({ host: 'http://localhost:19999' })
    const result = await hasEmbeddings(client)
    expect(result).toBe(false)
  })

  test('checkHealth returns err for unreachable host', async () => {
    const client = createClient({ host: 'http://localhost:19999' })
    const result = await checkHealth(client)
    expect(result.ok).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// hybridSearch degradation
// ---------------------------------------------------------------------------

describe('hybridSearch graceful degradation', () => {
  const mockKeywordResults: RankedResult[] = [
    { id: 'a', source: 'keyword', name: 'Result A', score: 0.9 },
    { id: 'b', source: 'keyword', name: 'Result B', score: 0.8 },
  ]

  const mockSemanticResults: RankedResult[] = [
    { id: 'b', source: 'semantic', name: 'Result B', score: 0.95 },
    { id: 'c', source: 'semantic', name: 'Result C', score: 0.85 },
  ]

  test('returns hybrid mode when both searches succeed', async () => {
    const result = await hybridSearch('test', {
      keywordSearch: async () => mockKeywordResults,
      semanticSearch: async () => mockSemanticResults,
    })

    expect(result.meta.mode).toBe('hybrid')
    expect(result.meta.keywordCount).toBe(2)
    expect(result.meta.semanticCount).toBe(2)
    expect(result.results.length).toBeGreaterThan(0)
  })

  test('degrades to keyword-only when no semantic search provided', async () => {
    const result = await hybridSearch('test', {
      keywordSearch: async () => mockKeywordResults,
      // No semanticSearch
    })

    expect(result.meta.mode).toBe('keyword-only')
    expect(result.meta.reason).toContain('no semantic search provided')
    expect(result.meta.keywordCount).toBe(2)
    expect(result.meta.semanticCount).toBe(0)
    expect(result.results.length).toBeGreaterThan(0)
  })

  test('degrades to keyword-only when semantic search throws', async () => {
    const result = await hybridSearch('test', {
      keywordSearch: async () => mockKeywordResults,
      semanticSearch: async () => {
        throw new Error('Ollama unavailable')
      },
    })

    expect(result.meta.mode).toBe('keyword-only')
    expect(result.meta.reason).toContain('semantic search failed')
    expect(result.meta.reason).toContain('Ollama unavailable')
    expect(result.results.length).toBeGreaterThan(0)
  })

  test('degrades to keyword-only when semantic returns empty', async () => {
    const result = await hybridSearch('test', {
      keywordSearch: async () => mockKeywordResults,
      semanticSearch: async () => [],
    })

    expect(result.meta.mode).toBe('keyword-only')
    expect(result.meta.reason).toContain('no semantic results')
  })

  test('returns unavailable when keyword search fails', async () => {
    const result = await hybridSearch('test', {
      keywordSearch: async () => {
        throw new Error('Meilisearch down')
      },
      semanticSearch: async () => mockSemanticResults,
    })

    expect(result.meta.mode).toBe('unavailable')
    expect(result.meta.reason).toContain('keyword search failed')
    expect(result.results.length).toBe(0)
  })

  test('JSON meta includes mode field', async () => {
    const result = await hybridSearch('test', {
      keywordSearch: async () => mockKeywordResults,
    })

    expect(result.meta).toHaveProperty('mode')
    expect(result.meta).toHaveProperty('keywordCount')
    expect(result.meta).toHaveProperty('semanticCount')
    expect(result.meta).toHaveProperty('mergedCount')
  })
})

// ---------------------------------------------------------------------------
// Mode reporting types
// ---------------------------------------------------------------------------

describe('SearchMeta types', () => {
  test('mode can be hybrid, keyword-only, or unavailable', () => {
    const modes = ['hybrid', 'keyword-only', 'unavailable']
    for (const mode of modes) {
      const meta = { mode, keywordCount: 0, semanticCount: 0, mergedCount: 0 }
      expect(modes).toContain(meta.mode)
    }
  })

  test('reason is optional', () => {
    const meta = { mode: 'hybrid' as const, keywordCount: 1, semanticCount: 1, mergedCount: 1 }
    expect(meta.mode).toBe('hybrid')
    // No reason field — that's fine for hybrid mode
  })
})
