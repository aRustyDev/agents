// cli/test/catalog-stale.test.ts
import { describe, expect, it } from 'bun:test'
import type { CatalogEntryWithTier1 } from '../src/lib/catalog'
import { identifyStaleEntries, type StaleCheckResult } from '../src/lib/catalog-stale'

describe('identifyStaleEntries', () => {
  it('flags entries where upstream treeSha differs from stored treeSha', () => {
    const entries: CatalogEntryWithTier1[] = [
      {
        source: 'org/repo',
        skill: 'skill-a',
        availability: 'available',
        treeSha: 'abc123old',
        wordCount: 500,
        attemptCount: 0,
      } as CatalogEntryWithTier1,
    ]

    const upstreamHashes = new Map([['org/repo:skill-a', 'def456new']])

    const results = identifyStaleEntries(entries, upstreamHashes)
    expect(results).toHaveLength(1)
    expect(results[0].status).toBe('stale')
    expect(results[0].localHash).toBe('abc123old')
    expect(results[0].remoteHash).toBe('def456new')
  })

  it('skips entries without treeSha', () => {
    const entries: CatalogEntryWithTier1[] = [
      {
        source: 'org/repo',
        skill: 'no-hash',
        availability: 'available',
        wordCount: 500,
      } as CatalogEntryWithTier1,
    ]

    const results = identifyStaleEntries(entries, new Map())
    expect(results).toHaveLength(0)
  })

  it('marks as current when treeSha matches', () => {
    const sha = 'abc123same'
    const entries: CatalogEntryWithTier1[] = [
      {
        source: 'org/repo',
        skill: 'current',
        availability: 'available',
        treeSha: sha,
        wordCount: 500,
        attemptCount: 0,
      } as CatalogEntryWithTier1,
    ]

    const results = identifyStaleEntries(entries, new Map([['org/repo:current', sha]]))
    expect(results).toHaveLength(1)
    expect(results[0].status).toBe('current')
  })
})
