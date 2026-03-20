import { afterEach, beforeEach, describe, expect, mock, test } from 'bun:test'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { SearchError, searchSkillsAPI } from '../lib/skill-search-api'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const originalFetch = globalThis.fetch

function mockFetch(impl: typeof globalThis.fetch) {
  globalThis.fetch = impl
}

function restoreFetch() {
  globalThis.fetch = originalFetch
}

/** Create a temp directory with a `.catalog.ndjson` file containing the given lines. */
function makeCatalog(lines: string[]): string {
  const dir = mkdtempSync(join(tmpdir(), 'skill-find-test-'))
  const path = join(dir, '.catalog.ndjson')
  writeFileSync(path, lines.join('\n'))
  return path
}

// ---------------------------------------------------------------------------
// skills-sh backend
// ---------------------------------------------------------------------------

describe('skills-sh backend', () => {
  afterEach(restoreFetch)

  test('returns normalized results', async () => {
    mockFetch(
      async () =>
        new Response(
          JSON.stringify([
            {
              name: 'beads',
              source: 'steveyegge/beads',
              description: 'Issue tracker',
              installs: 42,
            },
            { name: 'terraform', repo: 'hashicorp/terraform', url: 'https://example.com' },
          ]),
          { status: 200, headers: { 'content-type': 'application/json' } }
        )
    )

    const results = await searchSkillsAPI('beads', { source: 'skills-sh' })

    expect(results).toHaveLength(2)
    expect(results[0].name).toBe('beads')
    expect(results[0].source).toBe('steveyegge/beads')
    expect(results[0].description).toBe('Issue tracker')
    expect(results[0].installs).toBe(42)

    // Second item: `source` falls back to `repo` field
    expect(results[1].name).toBe('terraform')
    expect(results[1].source).toBe('hashicorp/terraform')
    expect(results[1].url).toBe('https://example.com')
  })

  test('429 rate limit returns empty', async () => {
    mockFetch(async () => new Response('Too Many Requests', { status: 429 }))

    const results = await searchSkillsAPI('beads', { source: 'skills-sh' })
    expect(results).toEqual([])
  })

  test('timeout returns empty', async () => {
    mockFetch(
      () =>
        new Promise((resolve) => {
          // Never resolves within the 3s timeout
          setTimeout(() => resolve(new Response('late')), 10_000)
        })
    )

    const results = await searchSkillsAPI('beads', { source: 'skills-sh' })
    expect(results).toEqual([])
  }, 10_000)

  test('network error returns empty', async () => {
    mockFetch(async () => {
      throw new TypeError('fetch failed')
    })

    const results = await searchSkillsAPI('beads', { source: 'skills-sh' })
    expect(results).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// auto mode
// ---------------------------------------------------------------------------

describe('auto mode', () => {
  afterEach(restoreFetch)

  test('fallback chain reaches catalog when fetch rejects', async () => {
    // Make fetch fail (blocks meilisearch + skills-sh)
    mockFetch(async () => {
      throw new TypeError('fetch failed')
    })

    const catalogPath = makeCatalog([
      JSON.stringify({
        name: 'fallback-skill',
        source: 'org/repo',
        description: 'Found via catalog',
      }),
    ])

    const results = await searchSkillsAPI('fallback', { catalogPath })

    expect(results.length).toBeGreaterThanOrEqual(1)
    expect(results[0].name).toBe('fallback-skill')
    expect(results[0].source).toBe('org/repo')
  })

  test('returns empty array when all backends fail', async () => {
    mockFetch(async () => {
      throw new TypeError('fetch failed')
    })

    // Point at a nonexistent catalog
    const results = await searchSkillsAPI('nothing', {
      catalogPath: '/tmp/nonexistent-catalog.ndjson',
    })

    expect(results).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// limit clamping
// ---------------------------------------------------------------------------

describe('limit clamping', () => {
  afterEach(restoreFetch)

  test('0 clamps to 1 without error', async () => {
    mockFetch(async (url) => {
      const u = new URL(typeof url === 'string' ? url : (url as Request).url)
      const limit = Number(u.searchParams.get('limit'))
      expect(limit).toBe(1)
      return new Response(JSON.stringify([{ name: 'a', source: 'x' }]), { status: 200 })
    })

    const results = await searchSkillsAPI('test', { source: 'skills-sh', limit: 0 })
    expect(results).toHaveLength(1)
  })

  test('500 clamps to 100', async () => {
    mockFetch(async (url) => {
      const u = new URL(typeof url === 'string' ? url : (url as Request).url)
      const limit = Number(u.searchParams.get('limit'))
      expect(limit).toBe(100)
      return new Response(JSON.stringify([]), { status: 200 })
    })

    const results = await searchSkillsAPI('test', { source: 'skills-sh', limit: 500 })
    expect(results.length).toBeLessThanOrEqual(100)
  })

  test('NaN defaults to 10', async () => {
    mockFetch(async (url) => {
      const u = new URL(typeof url === 'string' ? url : (url as Request).url)
      const limit = Number(u.searchParams.get('limit'))
      expect(limit).toBe(10)
      return new Response(JSON.stringify([]), { status: 200 })
    })

    const results = await searchSkillsAPI('test', { source: 'skills-sh', limit: NaN })
    expect(results).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// empty query
// ---------------------------------------------------------------------------

describe('empty query', () => {
  test('returns empty array immediately', async () => {
    const results = await searchSkillsAPI('')
    expect(results).toEqual([])
  })

  test('whitespace-only query returns empty array', async () => {
    const results = await searchSkillsAPI('   ')
    expect(results).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// catalog backend
// ---------------------------------------------------------------------------

describe('catalog backend', () => {
  test('matches case-insensitively on name', async () => {
    const catalogPath = makeCatalog([
      JSON.stringify({ name: 'TypeScript-Pro', source: 'org/ts', description: 'TS skill' }),
      JSON.stringify({ name: 'golang-dev', source: 'org/go', description: 'Go skill' }),
    ])

    const results = await searchSkillsAPI('typescript', {
      source: 'catalog',
      catalogPath,
    })

    expect(results).toHaveLength(1)
    expect(results[0].name).toBe('TypeScript-Pro')
  })

  test('matches case-insensitively on description', async () => {
    const catalogPath = makeCatalog([
      JSON.stringify({
        name: 'some-skill',
        source: 'org/repo',
        description: 'Helps with KUBERNETES deployments',
      }),
    ])

    const results = await searchSkillsAPI('kubernetes', {
      source: 'catalog',
      catalogPath,
    })

    expect(results).toHaveLength(1)
    expect(results[0].description).toBe('Helps with KUBERNETES deployments')
  })

  test('skips malformed JSON lines', async () => {
    const catalogPath = makeCatalog([
      '{ broken json',
      JSON.stringify({ name: 'valid-skill', source: 'org/repo', description: 'OK' }),
      '',
      'not json at all',
    ])

    const results = await searchSkillsAPI('valid', {
      source: 'catalog',
      catalogPath,
    })

    expect(results).toHaveLength(1)
    expect(results[0].name).toBe('valid-skill')
  })

  test('returns empty when catalog file does not exist', async () => {
    const results = await searchSkillsAPI('anything', {
      source: 'catalog',
      catalogPath: '/tmp/this-does-not-exist.ndjson',
    })
    expect(results).toEqual([])
  })

  test('respects limit', async () => {
    const lines = Array.from({ length: 20 }, (_, i) =>
      JSON.stringify({ name: `skill-${i}`, source: 'org/repo', description: `match skill-${i}` })
    )
    const catalogPath = makeCatalog(lines)

    const results = await searchSkillsAPI('skill', {
      source: 'catalog',
      catalogPath,
      limit: 5,
    })

    expect(results).toHaveLength(5)
  })
})

// ---------------------------------------------------------------------------
// SearchError
// ---------------------------------------------------------------------------

describe('SearchError', () => {
  test('has backend field and correct code', () => {
    const error = new SearchError('boom', 'skills-sh', 'try again')
    expect(error.backend).toBe('skills-sh')
    expect(error.code).toBe('SEARCH_SKILLS_SH')
    expect(error.hint).toBe('try again')
    expect(error.message).toBe('boom')
  })

  test('meilisearch backend code', () => {
    const error = new SearchError('down', 'meilisearch')
    expect(error.code).toBe('SEARCH_MEILISEARCH')
    expect(error.backend).toBe('meilisearch')
  })

  test('catalog backend code', () => {
    const error = new SearchError('missing', 'catalog')
    expect(error.code).toBe('SEARCH_CATALOG')
  })

  test('display() includes code and message', () => {
    const error = new SearchError('connection refused', 'skills-sh', 'check network')
    const output = error.display()
    expect(output).toContain('SEARCH_SKILLS_SH')
    expect(output).toContain('connection refused')
    expect(output).toContain('check network')
  })
})
