import { afterEach, beforeEach, describe, expect, it } from 'bun:test'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { type CatalogManager, createCatalog } from '../../src/catalog/manager'
import { NdjsonStore } from '../../src/catalog/ndjson/index'
import type { CatalogEntry, DiscoveryResult } from '../../src/catalog/types'

function makeEntry(
  overrides: Partial<CatalogEntry> & { source: string; name: string }
): CatalogEntry {
  return {
    type: 'skill',
    availability: 'available',
    ...overrides,
  }
}

describe('NdjsonStore', () => {
  let dir: string
  let store: NdjsonStore

  beforeEach(() => {
    dir = mkdtempSync(join(tmpdir(), 'ndjson-store-'))
    store = new NdjsonStore({ catalogPath: join(dir, 'catalog.ndjson') })
  })

  afterEach(async () => {
    await store.close()
    rmSync(dir, { recursive: true, force: true })
  })

  it('has backend "ndjson"', () => {
    expect(store.backend).toBe('ndjson')
  })

  it('round-trips entries (write then read)', async () => {
    const entries = [
      makeEntry({ source: 'local', name: 'foo' }),
      makeEntry({ source: 'local', name: 'bar', type: 'agent' }),
    ]
    const upsertResult = await store.upsert(entries)
    expect(upsertResult.ok).toBe(true)

    const queryResult = await store.query({})
    expect(queryResult.ok).toBe(true)
    if (queryResult.ok) {
      expect(queryResult.value).toHaveLength(2)
    }
  })

  it('query filters by type', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'skill1', type: 'skill' }),
      makeEntry({ source: 'local', name: 'agent1', type: 'agent' }),
      makeEntry({ source: 'local', name: 'skill2', type: 'skill' }),
    ])

    const result = await store.query({ type: 'skill' })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(2)
      expect(result.value.every((e) => e.type === 'skill')).toBe(true)
    }
  })

  it('query filters by source substring', async () => {
    await store.upsert([
      makeEntry({ source: 'github/org/repo', name: 'a' }),
      makeEntry({ source: 'local', name: 'b' }),
      makeEntry({ source: 'github/org/other', name: 'c' }),
    ])

    const result = await store.query({ source: 'github' })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(2)
    }
  })

  it('query filters by availability', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'a', availability: 'available' }),
      makeEntry({ source: 'local', name: 'b', availability: 'archived' }),
    ])

    const result = await store.query({ availability: 'available' })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(1)
      expect(result.value[0].name).toBe('a')
    }
  })

  it('query supports limit and offset', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'a' }),
      makeEntry({ source: 'local', name: 'b' }),
      makeEntry({ source: 'local', name: 'c' }),
    ])

    const result = await store.query({ limit: 2, offset: 1 })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(2)
      expect(result.value[0].name).toBe('b')
    }
  })

  it('query matches by name via query string', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'kubernetes-deploy' }),
      makeEntry({ source: 'local', name: 'docker-build' }),
    ])

    const result = await store.query({ query: 'kubernetes' })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(1)
      expect(result.value[0].name).toBe('kubernetes-deploy')
    }
  })

  it('get returns specific entry', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'target' }),
      makeEntry({ source: 'local', name: 'other' }),
    ])

    const result = await store.get('local', 'target')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBeDefined()
      expect(result.value?.name).toBe('target')
    }
  })

  it('get returns undefined for missing entry', async () => {
    const result = await store.get('local', 'nonexistent')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBeUndefined()
    }
  })

  it('upsert adds new entries', async () => {
    const result = await store.upsert([
      makeEntry({ source: 'local', name: 'new1' }),
      makeEntry({ source: 'local', name: 'new2' }),
    ])
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toBe(2)

    const count = await store.count()
    expect(count.ok).toBe(true)
    if (count.ok) expect(count.value).toBe(2)
  })

  it('upsert updates existing entry by source+name', async () => {
    await store.upsert([makeEntry({ source: 'local', name: 'item', availability: 'available' })])

    await store.upsert([makeEntry({ source: 'local', name: 'item', availability: 'archived' })])

    const result = await store.get('local', 'item')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value?.availability).toBe('archived')
    }

    const count = await store.count()
    expect(count.ok).toBe(true)
    if (count.ok) expect(count.value).toBe(1)
  })

  it('remove deletes entry', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'keep' }),
      makeEntry({ source: 'local', name: 'remove-me' }),
    ])

    const removeResult = await store.remove('local', 'remove-me')
    expect(removeResult.ok).toBe(true)
    if (removeResult.ok) expect(removeResult.value).toBe(true)

    const count = await store.count()
    expect(count.ok).toBe(true)
    if (count.ok) expect(count.value).toBe(1)

    const remaining = await store.get('local', 'keep')
    expect(remaining.ok).toBe(true)
    if (remaining.ok) expect(remaining.value).toBeDefined()
  })

  it('remove returns false for missing entry', async () => {
    const result = await store.remove('local', 'nonexistent')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toBe(false)
  })

  it('count returns correct number', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'a' }),
      makeEntry({ source: 'local', name: 'b' }),
      makeEntry({ source: 'local', name: 'c' }),
    ])

    const result = await store.count()
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toBe(3)
  })

  it('count respects filter', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'a', type: 'skill' }),
      makeEntry({ source: 'local', name: 'b', type: 'agent' }),
      makeEntry({ source: 'local', name: 'c', type: 'skill' }),
    ])

    const result = await store.count({ type: 'skill' })
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toBe(2)
  })

  it('findStale identifies stale entries', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'current', contentHash: 'abc123' }),
      makeEntry({ source: 'local', name: 'stale', contentHash: 'old-hash' }),
      makeEntry({ source: 'local', name: 'unknown' }),
    ])

    const upstream = new Map<string, string>()
    upstream.set('local::current', 'abc123')
    upstream.set('local::stale', 'new-hash')

    const result = await store.findStale(upstream)
    expect(result.ok).toBe(true)
    if (result.ok) {
      const byName = new Map(result.value.map((r) => [r.name, r]))
      expect(byName.get('current')?.status).toBe('current')
      expect(byName.get('stale')?.status).toBe('stale')
      expect(byName.get('unknown')?.status).toBe('unknown')
    }
  })

  it('merge adds new and updates existing entries', async () => {
    await store.upsert([makeEntry({ source: 'local', name: 'existing', type: 'skill' })])

    const discoveries: DiscoveryResult[] = [
      {
        source: 'local',
        name: 'existing',
        type: 'agent',
        mechanical: { wordCount: 100 },
      },
      {
        source: 'local',
        name: 'brand-new',
        type: 'skill',
        mechanical: { wordCount: 50 },
      },
    ]

    const result = await store.merge(discoveries)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.updated).toBe(1)
      expect(result.value.added).toBe(1)
    }

    const all = await store.query({})
    expect(all.ok).toBe(true)
    if (all.ok) {
      expect(all.value).toHaveLength(2)
      const existing = all.value.find((e) => e.name === 'existing')
      expect(existing?.type).toBe('agent')
      expect(existing?.mechanical?.wordCount).toBe(100)
    }
  })

  it('appendErrors writes to error log', async () => {
    const errorLogPath = join(dir, 'errors.ndjson')
    const storeWithErrors = new NdjsonStore({
      catalogPath: join(dir, 'catalog2.ndjson'),
      errorLogPath,
    })

    const result = await storeWithErrors.appendErrors([
      {
        source: 'local',
        name: 'broken',
        runId: 'run-1',
        error: 'timeout',
        errorType: 'E_TIMEOUT',
        errorDetail: 'connection timed out',
        attemptCount: 1,
        lastAttemptAt: '2026-01-01T00:00:00Z',
      },
    ])
    expect(result.ok).toBe(true)

    // Verify error was written by reading the file
    const { readFileSync } = await import('node:fs')
    const content = readFileSync(errorLogPath, 'utf-8')
    expect(content).toContain('broken')
    expect(content).toContain('timeout')

    await storeWithErrors.close()
  })
})

describe('CatalogManager', () => {
  let dir: string
  let store: NdjsonStore
  let manager: CatalogManager

  beforeEach(() => {
    dir = mkdtempSync(join(tmpdir(), 'catalog-mgr-'))
    store = new NdjsonStore({ catalogPath: join(dir, 'catalog.ndjson') })
    manager = createCatalog({ store })
  })

  afterEach(async () => {
    await store.close()
    rmSync(dir, { recursive: true, force: true })
  })

  it('stats computed correctly', async () => {
    await store.upsert([
      makeEntry({ source: 'local', name: 'a', type: 'skill', availability: 'available' }),
      makeEntry({ source: 'local', name: 'b', type: 'agent', availability: 'available' }),
      makeEntry({
        source: 'local',
        name: 'c',
        type: 'skill',
        availability: 'archived',
        analysis: { complexity: 'simple' },
      }),
      makeEntry({
        source: 'local',
        name: 'd',
        type: 'skill',
        availability: 'available',
        errorCount: 3,
      }),
    ])

    const result = await manager.stats()
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.total).toBe(4)
      expect(result.value.byType['skill']).toBe(3)
      expect(result.value.byType['agent']).toBe(1)
      expect(result.value.byAvailability['available']).toBe(3)
      expect(result.value.byAvailability['archived']).toBe(1)
      expect(result.value.analyzed).toBe(1)
      expect(result.value.withErrors).toBe(1)
    }
  })

  it('query delegates to store', async () => {
    await store.upsert([makeEntry({ source: 'local', name: 'x' })])

    const result = await manager.query({})
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toHaveLength(1)
      expect(result.value[0].name).toBe('x')
    }
  })

  it('get delegates to store', async () => {
    await store.upsert([makeEntry({ source: 'local', name: 'y' })])

    const result = await manager.get('local', 'y')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toBeDefined()
      expect(result.value?.name).toBe('y')
    }
  })

  it('sync delegates to store merge', async () => {
    const discoveries: DiscoveryResult[] = [
      { source: 'local', name: 'synced', type: 'skill', mechanical: { wordCount: 42 } },
    ]

    const result = await manager.sync(discoveries)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.added).toBe(1)
    }
  })
})
