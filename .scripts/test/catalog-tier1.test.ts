/**
 * catalog-tier1.test.ts — Unit tests for catalog.ts Phase 4 (Tier 1 analysis)
 *
 * Run with: bun test .scripts/test/catalog-tier1.test.ts
 */

import { afterEach, beforeEach, describe, expect, it } from 'bun:test'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  type CatalogEntry,
  createBatches,
  detectForks,
  filterAvailable,
  formatBatchPrompt,
  mergeTier1Results,
  parseTier1Output,
  readCatalog,
  type Tier1Result,
} from '../lib/catalog'

// ---------------------------------------------------------------------------
// filterAvailable
// ---------------------------------------------------------------------------

describe('filterAvailable', () => {
  it('keeps only entries with availability === "available"', () => {
    const entries: CatalogEntry[] = [
      { source: 'org/a', skill: 'x', availability: 'available' },
      { source: 'org/b', skill: 'y', availability: 'not_found' },
      { source: 'org/c', skill: 'z', availability: 'available' },
      { source: 'org/d', skill: 'w', availability: 'archived' },
      { source: 'org/e', skill: 'v', availability: 'private' },
      { source: 'org/f', skill: 'u', availability: 'error' },
    ]

    const result = filterAvailable(entries)
    expect(result).toHaveLength(2)
    expect(result[0].source).toBe('org/a')
    expect(result[1].source).toBe('org/c')
  })

  it('returns empty array when no entries are available', () => {
    const entries: CatalogEntry[] = [{ source: 'org/a', skill: 'x', availability: 'not_found' }]
    expect(filterAvailable(entries)).toEqual([])
  })

  it('returns empty array for empty input', () => {
    expect(filterAvailable([])).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// createBatches
// ---------------------------------------------------------------------------

describe('createBatches', () => {
  it('splits entries into batches of the given size', () => {
    const entries: CatalogEntry[] = [
      { source: 'org/a', skill: 'x', availability: 'available' },
      { source: 'org/b', skill: 'y', availability: 'available' },
      { source: 'org/c', skill: 'z', availability: 'available' },
      { source: 'org/d', skill: 'w', availability: 'available' },
      { source: 'org/e', skill: 'v', availability: 'available' },
    ]

    const batches = createBatches(entries, 2)
    expect(batches).toHaveLength(3)
    expect(batches[0]).toHaveLength(2)
    expect(batches[1]).toHaveLength(2)
    expect(batches[2]).toHaveLength(1)
  })

  it('groups entries by source for repo locality', () => {
    const entries: CatalogEntry[] = [
      { source: 'org/z-repo', skill: 'a', availability: 'available' },
      { source: 'org/a-repo', skill: 'b', availability: 'available' },
      { source: 'org/z-repo', skill: 'c', availability: 'available' },
      { source: 'org/a-repo', skill: 'd', availability: 'available' },
    ]

    const batches = createBatches(entries, 2)
    // After sorting by source: org/a-repo entries come first
    expect(batches[0].every((e) => e.source === 'org/a-repo')).toBe(true)
    expect(batches[1].every((e) => e.source === 'org/z-repo')).toBe(true)
  })

  it('returns empty array for empty input', () => {
    expect(createBatches([], 5)).toEqual([])
  })

  it('throws on non-positive batch size', () => {
    expect(() => createBatches([], 0)).toThrow('batchSize must be positive')
    expect(() => createBatches([], -1)).toThrow('batchSize must be positive')
  })

  it('handles batch size larger than entry count', () => {
    const entries: CatalogEntry[] = [
      { source: 'org/a', skill: 'x', availability: 'available' },
      { source: 'org/b', skill: 'y', availability: 'available' },
    ]

    const batches = createBatches(entries, 100)
    expect(batches).toHaveLength(1)
    expect(batches[0]).toHaveLength(2)
  })

  it('does not mutate the input array', () => {
    const entries: CatalogEntry[] = [
      { source: 'org/b', skill: 'y', availability: 'available' },
      { source: 'org/a', skill: 'x', availability: 'available' },
    ]
    const originalOrder = entries.map((e) => e.source)

    createBatches(entries, 1)

    expect(entries.map((e) => e.source)).toEqual(originalOrder)
  })
})

// ---------------------------------------------------------------------------
// formatBatchPrompt
// ---------------------------------------------------------------------------

describe('formatBatchPrompt', () => {
  it('formats entries as org/repo@skill, newline-separated', () => {
    const batch: CatalogEntry[] = [
      { source: 'anthropics/skills', skill: 'pdf', availability: 'available' },
      { source: 'wshobson/agents', skill: 'research', availability: 'available' },
    ]

    const result = formatBatchPrompt(batch)
    expect(result).toBe('anthropics/skills@pdf\nwshobson/agents@research')
  })

  it('returns empty string for empty batch', () => {
    expect(formatBatchPrompt([])).toBe('')
  })

  it('handles single entry', () => {
    const batch: CatalogEntry[] = [
      { source: 'org/repo', skill: 'skill', availability: 'available' },
    ]
    expect(formatBatchPrompt(batch)).toBe('org/repo@skill')
  })
})

// ---------------------------------------------------------------------------
// parseTier1Output
// ---------------------------------------------------------------------------

describe('parseTier1Output', () => {
  it('parses valid NDJSON lines', () => {
    const stdout = [
      '{"source":"org/a","skill":"x","wordCount":500,"complexity":"moderate"}',
      '{"source":"org/b","skill":"y","error":"download failed"}',
    ].join('\n')

    const results = parseTier1Output(stdout)
    expect(results).toHaveLength(2)
    expect(results[0].source).toBe('org/a')
    expect(results[0].wordCount).toBe(500)
    expect(results[1].error).toBe('download failed')
  })

  it('skips blank lines', () => {
    const stdout = '\n{"source":"org/a","skill":"x"}\n\n'
    const results = parseTier1Output(stdout)
    expect(results).toHaveLength(1)
  })

  it('skips lines with invalid JSON', () => {
    const stdout = [
      '{"source":"org/a","skill":"x"}',
      'this is not json',
      '{"source":"org/b","skill":"y"}',
    ].join('\n')

    const results = parseTier1Output(stdout)
    expect(results).toHaveLength(2)
  })

  it('skips JSON objects missing source or skill', () => {
    const stdout = [
      '{"source":"org/a","skill":"x"}',
      '{"source":"org/b"}',
      '{"skill":"y"}',
      '{"foo":"bar"}',
    ].join('\n')

    const results = parseTier1Output(stdout)
    expect(results).toHaveLength(1)
    expect(results[0].source).toBe('org/a')
  })

  it('returns empty array for empty input', () => {
    expect(parseTier1Output('')).toEqual([])
  })

  it('preserves all Tier1 fields', () => {
    const line = JSON.stringify({
      source: 'org/repo',
      skill: 'my-skill',
      wordCount: 1250,
      sectionCount: 8,
      fileCount: 3,
      headingTree: [{ depth: 1, title: 'Main' }],
      keywords: ['rag', 'vector'],
      internalLinks: ['./assets/diagram.md'],
      externalLinks: ['https://docs.example.com'],
      complexity: 'moderate',
      progressiveDisclosure: true,
      pdTechniques: ['details-blocks'],
      bestPracticesMechanical: { score: 3, violations: [] },
      securityMechanical: { score: 4, concerns: [] },
      contentHash: 'sha256:abc123',
      tier2Reviewed: false,
    })

    const results = parseTier1Output(line)
    expect(results).toHaveLength(1)
    expect(results[0].wordCount).toBe(1250)
    expect(results[0].keywords).toEqual(['rag', 'vector'])
    expect(results[0].bestPracticesMechanical?.score).toBe(3)
    expect(results[0].contentHash).toBe('sha256:abc123')
  })
})

// ---------------------------------------------------------------------------
// detectForks
// ---------------------------------------------------------------------------

describe('detectForks', () => {
  it('marks entries with matching skill name and content hash as forks', () => {
    const results: Tier1Result[] = [
      { source: 'org-a/repo', skill: 'tinacms', contentHash: 'sha256:aaa' },
      { source: 'org-b/repo', skill: 'tinacms', contentHash: 'sha256:aaa' },
      { source: 'org-c/repo', skill: 'tinacms', contentHash: 'sha256:bbb' },
    ]

    const marked = detectForks(results)

    // org-b has the same hash as org-a -> fork
    expect(marked[1].possibleForkOf).toBe('org-a/repo')
    // org-c has a different hash -> not a fork
    expect(marked[2].possibleForkOf).toBeUndefined()
    // org-a is the first-seen -> not marked
    expect(marked[0].possibleForkOf).toBeUndefined()
  })

  it('does not mark entries with different skill names', () => {
    const results: Tier1Result[] = [
      { source: 'org-a/repo', skill: 'pdf', contentHash: 'sha256:aaa' },
      { source: 'org-b/repo', skill: 'xlsx', contentHash: 'sha256:aaa' },
    ]

    const marked = detectForks(results)
    expect(marked[0].possibleForkOf).toBeUndefined()
    expect(marked[1].possibleForkOf).toBeUndefined()
  })

  it('skips entries without contentHash', () => {
    const results: Tier1Result[] = [
      { source: 'org-a/repo', skill: 'skill', contentHash: 'sha256:aaa' },
      { source: 'org-b/repo', skill: 'skill' }, // no hash
    ]

    const marked = detectForks(results)
    expect(marked[0].possibleForkOf).toBeUndefined()
    expect(marked[1].possibleForkOf).toBeUndefined()
  })

  it('returns the same array reference (mutates in place)', () => {
    const results: Tier1Result[] = [
      { source: 'org/repo', skill: 'skill', contentHash: 'sha256:aaa' },
    ]

    const returned = detectForks(results)
    expect(returned).toBe(results)
  })

  it('handles empty input', () => {
    expect(detectForks([])).toEqual([])
  })

  it('handles multiple fork groups independently', () => {
    const results: Tier1Result[] = [
      { source: 'a/repo', skill: 'pdf', contentHash: 'sha256:111' },
      { source: 'b/repo', skill: 'pdf', contentHash: 'sha256:111' },
      { source: 'c/repo', skill: 'xlsx', contentHash: 'sha256:222' },
      { source: 'd/repo', skill: 'xlsx', contentHash: 'sha256:222' },
    ]

    const marked = detectForks(results)
    expect(marked[0].possibleForkOf).toBeUndefined()
    expect(marked[1].possibleForkOf).toBe('a/repo')
    expect(marked[2].possibleForkOf).toBeUndefined()
    expect(marked[3].possibleForkOf).toBe('c/repo')
  })
})

// ---------------------------------------------------------------------------
// readCatalog
// ---------------------------------------------------------------------------

describe('readCatalog', () => {
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'catalog-test-'))
  })

  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  it('reads NDJSON catalog entries', () => {
    const catalogPath = join(tmpDir, 'test.ndjson')
    const lines = [
      '{"source":"org/a","skill":"x","availability":"available"}',
      '{"source":"org/b","skill":"y","availability":"not_found"}',
    ].join('\n')
    writeFileSync(catalogPath, lines + '\n', 'utf8')

    const entries = readCatalog(catalogPath)
    expect(entries).toHaveLength(2)
    expect(entries[0].source).toBe('org/a')
    expect(entries[1].availability).toBe('not_found')
  })

  it('skips malformed lines', () => {
    const catalogPath = join(tmpDir, 'test.ndjson')
    writeFileSync(
      catalogPath,
      '{"source":"org/a","skill":"x","availability":"available"}\nnot-json\n',
      'utf8'
    )

    const entries = readCatalog(catalogPath)
    expect(entries).toHaveLength(1)
  })
})

// ---------------------------------------------------------------------------
// mergeTier1Results
// ---------------------------------------------------------------------------

describe('mergeTier1Results', () => {
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'catalog-merge-'))
  })

  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  it('merges Tier1 fields into existing catalog entries', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    writeFileSync(
      catalogPath,
      '{"source":"org/a","skill":"x","availability":"available"}\n',
      'utf8'
    )

    const results: Tier1Result[] = [
      {
        source: 'org/a',
        skill: 'x',
        wordCount: 500,
        complexity: 'moderate',
        contentHash: 'sha256:abc',
      },
    ]

    mergeTier1Results(catalogPath, results)

    const content = readFileSync(catalogPath, 'utf8')
    const lines = content.trim().split('\n')
    expect(lines).toHaveLength(1)

    const merged = JSON.parse(lines[0])
    expect(merged.source).toBe('org/a')
    expect(merged.skill).toBe('x')
    expect(merged.availability).toBe('available')
    expect(merged.wordCount).toBe(500)
    expect(merged.complexity).toBe('moderate')
    expect(merged.contentHash).toBe('sha256:abc')
  })

  it('appends entries that do not exist in the catalog', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    writeFileSync(
      catalogPath,
      '{"source":"org/a","skill":"x","availability":"available"}\n',
      'utf8'
    )

    const results: Tier1Result[] = [{ source: 'org/b', skill: 'y', wordCount: 300 }]

    mergeTier1Results(catalogPath, results)

    const content = readFileSync(catalogPath, 'utf8')
    const lines = content.trim().split('\n')
    expect(lines).toHaveLength(2)

    const appended = JSON.parse(lines[1])
    expect(appended.source).toBe('org/b')
    expect(appended.skill).toBe('y')
    expect(appended.availability).toBe('available')
    expect(appended.wordCount).toBe(300)
  })

  it('creates file if catalog does not exist', () => {
    const catalogPath = join(tmpDir, 'new-catalog.ndjson')

    const results: Tier1Result[] = [{ source: 'org/a', skill: 'x', wordCount: 100 }]

    mergeTier1Results(catalogPath, results)

    const content = readFileSync(catalogPath, 'utf8')
    const lines = content.trim().split('\n')
    expect(lines).toHaveLength(1)

    const entry = JSON.parse(lines[0])
    expect(entry.source).toBe('org/a')
    expect(entry.availability).toBe('available')
  })

  it('handles merging multiple results at once', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    const existing =
      [
        '{"source":"org/a","skill":"x","availability":"available"}',
        '{"source":"org/b","skill":"y","availability":"available"}',
        '{"source":"org/c","skill":"z","availability":"not_found"}',
      ].join('\n') + '\n'
    writeFileSync(catalogPath, existing, 'utf8')

    const results: Tier1Result[] = [
      { source: 'org/a', skill: 'x', wordCount: 100 },
      { source: 'org/b', skill: 'y', wordCount: 200 },
      { source: 'org/d', skill: 'w', wordCount: 400 },
    ]

    mergeTier1Results(catalogPath, results)

    const content = readFileSync(catalogPath, 'utf8')
    const lines = content.trim().split('\n')
    expect(lines).toHaveLength(4) // 3 existing + 1 new

    const entries = lines.map((l) => JSON.parse(l))
    expect(entries[0].wordCount).toBe(100) // merged
    expect(entries[1].wordCount).toBe(200) // merged
    expect(entries[2].availability).toBe('not_found') // unchanged
    expect(entries[3].source).toBe('org/d') // appended
  })

  it('preserves existing fields when merging', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    writeFileSync(
      catalogPath,
      '{"source":"org/a","skill":"x","availability":"available","customField":"keep"}\n',
      'utf8'
    )

    const results: Tier1Result[] = [{ source: 'org/a', skill: 'x', wordCount: 500 }]

    mergeTier1Results(catalogPath, results)

    const content = readFileSync(catalogPath, 'utf8')
    const merged = JSON.parse(content.trim())
    expect(merged.customField).toBe('keep')
    expect(merged.wordCount).toBe(500)
  })
})
