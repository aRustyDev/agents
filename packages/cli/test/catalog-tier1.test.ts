/**
 * catalog-tier1.test.ts — Unit tests for catalog.ts Phase 4 (Tier 1 analysis)
 *
 * Run with: bun test cli/test/catalog-tier1.test.ts
 */

import { afterEach, beforeEach, describe, expect, it } from 'bun:test'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  appendError,
  appendErrors,
  type CatalogEntry,
  type CatalogEntryWithTier1,
  computeContentHash,
  computeFileCount,
  computeHeadingTree,
  computeSectionCount,
  computeWordCount,
  createBatches,
  detectForks,
  type ErrorRecord,
  filterAvailable,
  filterForProcessing,
  formatBatchPrompt,
  getErrorsForSkill,
  mergeTier1Results,
  parseTier1Output,
  readCatalog,
  readErrorLog,
  type Tier1Result,
  type Tier1ResultWithTransient,
  validateBatchResults,
} from '../src/lib/catalog'

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

  it('merges Tier1 fields into existing catalog entries (success)', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    const errorLogPath = join(tmpDir, 'errors.ndjson')
    writeFileSync(
      catalogPath,
      '{"source":"org/a","skill":"x","availability":"available"}\n',
      'utf8'
    )

    const results: Tier1ResultWithTransient[] = [
      {
        source: 'org/a',
        skill: 'x',
        wordCount: 500,
        complexity: 'moderate',
        contentHash: 'sha256:abc',
      },
    ]

    mergeTier1Results(catalogPath, errorLogPath, results)

    const content = readFileSync(catalogPath, 'utf8')
    const lines = content.trim().split('\n')
    expect(lines).toHaveLength(1)

    const merged = JSON.parse(lines[0])
    expect(merged.source).toBe('org/a')
    expect(merged.wordCount).toBe(500)
    expect(merged.attemptCount).toBe(0)
    // No error log file should be created for successes
    expect(require('node:fs').existsSync(errorLogPath)).toBe(false)
  })

  it('routes failures to error log and increments attemptCount', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    const errorLogPath = join(tmpDir, 'errors.ndjson')
    writeFileSync(
      catalogPath,
      '{"source":"org/a","skill":"x","availability":"available"}\n',
      'utf8'
    )

    const results: Tier1ResultWithTransient[] = [
      {
        source: 'org/a',
        skill: 'x',
        error: 'download failed: 404',
        errorType: 'download_failed',
        errorDetail: 'HTTP 404',
        retryable: true,
        runId: 'run-1',
        batchId: 'batch-1',
        analyzedAt: '2026-01-01T00:00:00Z',
      },
    ]

    mergeTier1Results(catalogPath, errorLogPath, results)

    // Catalog entry should have error cache fields, NOT error/errorDetail
    const catalog = JSON.parse(readFileSync(catalogPath, 'utf8').trim())
    expect(catalog.attemptCount).toBe(1)
    expect(catalog.lastErrorType).toBe('download_failed')
    expect(catalog.retryable).toBe(true)
    expect(catalog.error).toBeUndefined()
    expect(catalog.errorDetail).toBeUndefined()

    // Error log should have the detail
    const errors = readErrorLog(errorLogPath)
    expect(errors).toHaveLength(1)
    expect(errors[0].errorType).toBe('download_failed')
    expect(errors[0].errorDetail).toBe('HTTP 404')
  })

  it('success clears error cache fields and resets attemptCount', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    const errorLogPath = join(tmpDir, 'errors.ndjson')
    writeFileSync(
      catalogPath,
      '{"source":"org/a","skill":"x","availability":"available","attemptCount":2,"lastErrorType":"download_failed","retryable":true}\n',
      'utf8'
    )

    const results: Tier1ResultWithTransient[] = [
      { source: 'org/a', skill: 'x', wordCount: 500, contentHash: 'sha256:abc' },
    ]

    mergeTier1Results(catalogPath, errorLogPath, results)

    const merged = JSON.parse(readFileSync(catalogPath, 'utf8').trim())
    expect(merged.attemptCount).toBe(0)
    expect(merged.lastErrorType).toBeUndefined()
    expect(merged.retryable).toBeUndefined()
    expect(merged.wordCount).toBe(500)
  })

  it('appends entries that do not exist in the catalog', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    const errorLogPath = join(tmpDir, 'errors.ndjson')
    writeFileSync(
      catalogPath,
      '{"source":"org/a","skill":"x","availability":"available"}\n',
      'utf8'
    )

    const results: Tier1ResultWithTransient[] = [{ source: 'org/b', skill: 'y', wordCount: 300 }]

    mergeTier1Results(catalogPath, errorLogPath, results)

    const content = readFileSync(catalogPath, 'utf8')
    const lines = content.trim().split('\n')
    expect(lines).toHaveLength(2)

    const appended = JSON.parse(lines[1])
    expect(appended.source).toBe('org/b')
    expect(appended.availability).toBe('available')
    expect(appended.wordCount).toBe(300)
  })

  it('creates file if catalog does not exist', () => {
    const catalogPath = join(tmpDir, 'new-catalog.ndjson')
    const errorLogPath = join(tmpDir, 'errors.ndjson')

    const results: Tier1ResultWithTransient[] = [{ source: 'org/a', skill: 'x', wordCount: 100 }]

    mergeTier1Results(catalogPath, errorLogPath, results)

    const content = readFileSync(catalogPath, 'utf8')
    const entry = JSON.parse(content.trim())
    expect(entry.source).toBe('org/a')
    expect(entry.availability).toBe('available')
  })

  it('handles mix of successes and failures', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    const errorLogPath = join(tmpDir, 'errors.ndjson')
    const existing =
      [
        '{"source":"org/a","skill":"x","availability":"available"}',
        '{"source":"org/b","skill":"y","availability":"available"}',
      ].join('\n') + '\n'
    writeFileSync(catalogPath, existing, 'utf8')

    const results: Tier1ResultWithTransient[] = [
      { source: 'org/a', skill: 'x', wordCount: 100, contentHash: 'sha256:aaa' },
      {
        source: 'org/b',
        skill: 'y',
        error: 'timeout',
        errorType: 'analysis_timeout',
        retryable: true,
        runId: 'r1',
        batchId: 'b1',
        analyzedAt: '2026-01-01T00:00:00Z',
      },
    ]

    mergeTier1Results(catalogPath, errorLogPath, results)

    const lines = readFileSync(catalogPath, 'utf8').trim().split('\n')
    const entries = lines.map((l) => JSON.parse(l))
    expect(entries[0].wordCount).toBe(100)
    expect(entries[0].attemptCount).toBe(0)
    expect(entries[1].attemptCount).toBe(1)
    expect(entries[1].lastErrorType).toBe('analysis_timeout')
    expect(entries[1].error).toBeUndefined()

    const errors = readErrorLog(errorLogPath)
    expect(errors).toHaveLength(1)
    expect(errors[0].source).toBe('org/b')
  })

  it('preserves existing fields when merging', () => {
    const catalogPath = join(tmpDir, 'catalog.ndjson')
    const errorLogPath = join(tmpDir, 'errors.ndjson')
    writeFileSync(
      catalogPath,
      '{"source":"org/a","skill":"x","availability":"available","customField":"keep"}\n',
      'utf8'
    )

    const results: Tier1ResultWithTransient[] = [{ source: 'org/a', skill: 'x', wordCount: 500 }]

    mergeTier1Results(catalogPath, errorLogPath, results)

    const merged = JSON.parse(readFileSync(catalogPath, 'utf8').trim())
    expect(merged.customField).toBe('keep')
    expect(merged.wordCount).toBe(500)
  })
})

// ---------------------------------------------------------------------------
// Error Log Functions
// ---------------------------------------------------------------------------

describe('appendError / appendErrors', () => {
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'error-log-'))
  })

  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  const makeRecord = (skill: string): ErrorRecord => ({
    source: 'org/repo',
    skill,
    runId: 'run-1',
    batchId: 'batch-1',
    timestamp: '2026-01-01T00:00:00Z',
    errorType: 'download_failed',
    errorDetail: 'HTTP 404',
    retryable: true,
  })

  it('appendError creates file and writes single record', () => {
    const logPath = join(tmpDir, 'errors.ndjson')
    appendError(logPath, makeRecord('skill-a'))

    const records = readErrorLog(logPath)
    expect(records).toHaveLength(1)
    expect(records[0].skill).toBe('skill-a')
  })

  it('appendErrors writes multiple records in one call', () => {
    const logPath = join(tmpDir, 'errors.ndjson')
    appendErrors(logPath, [makeRecord('a'), makeRecord('b'), makeRecord('c')])

    const records = readErrorLog(logPath)
    expect(records).toHaveLength(3)
  })

  it('appendErrors is a no-op for empty array', () => {
    const logPath = join(tmpDir, 'errors.ndjson')
    appendErrors(logPath, [])
    expect(require('node:fs').existsSync(logPath)).toBe(false)
  })

  it('readErrorLog returns empty array for missing file', () => {
    expect(readErrorLog(join(tmpDir, 'nonexistent.ndjson'))).toEqual([])
  })

  it('getErrorsForSkill filters by source and skill', () => {
    const logPath = join(tmpDir, 'errors.ndjson')
    appendErrors(logPath, [
      makeRecord('a'),
      { ...makeRecord('b'), source: 'other/repo' },
      makeRecord('a'),
    ])

    const filtered = getErrorsForSkill(logPath, 'org/repo', 'a')
    expect(filtered).toHaveLength(2)
    expect(filtered.every((r) => r.skill === 'a')).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// Mechanical Compute Functions
// ---------------------------------------------------------------------------

describe('computeContentHash', () => {
  it('returns sha256:<hex> format', () => {
    const hash = computeContentHash('hello world')
    expect(hash).toMatch(/^sha256:[a-f0-9]{64}$/)
  })

  it('returns consistent hash for same input', () => {
    expect(computeContentHash('test')).toBe(computeContentHash('test'))
  })

  it('returns different hashes for different inputs', () => {
    expect(computeContentHash('a')).not.toBe(computeContentHash('b'))
  })

  it('handles empty string', () => {
    const hash = computeContentHash('')
    expect(hash).toMatch(/^sha256:[a-f0-9]{64}$/)
  })
})

describe('computeWordCount', () => {
  it('counts words split by whitespace', () => {
    expect(computeWordCount('hello world foo')).toBe(3)
  })

  it('handles multiple whitespace types', () => {
    expect(computeWordCount('hello\tworld\nfoo  bar')).toBe(4)
  })

  it('returns 0 for empty string', () => {
    expect(computeWordCount('')).toBe(0)
  })

  it('returns 0 for whitespace-only string', () => {
    expect(computeWordCount('   \n\t  ')).toBe(0)
  })

  it('counts single word', () => {
    expect(computeWordCount('hello')).toBe(1)
  })
})

describe('computeSectionCount', () => {
  it('counts headings at all levels', () => {
    const md = '# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6\n'
    expect(computeSectionCount(md)).toBe(6)
  })

  it('does not count lines starting with # but no space', () => {
    expect(computeSectionCount('#hashtag\n## Real Heading\n')).toBe(1)
  })

  it('returns 0 for no headings', () => {
    expect(computeSectionCount('Just text\nMore text\n')).toBe(0)
  })

  it('returns 0 for empty string', () => {
    expect(computeSectionCount('')).toBe(0)
  })
})

describe('computeHeadingTree', () => {
  it('extracts depth and title from headings', () => {
    const md = '# Main\n## Sub\n### Deep\n'
    const tree = computeHeadingTree(md)
    expect(tree).toEqual([
      { depth: 1, title: 'Main' },
      { depth: 2, title: 'Sub' },
      { depth: 3, title: 'Deep' },
    ])
  })

  it('returns empty array for no headings', () => {
    expect(computeHeadingTree('no headings here')).toEqual([])
  })

  it('handles heading with trailing whitespace', () => {
    const tree = computeHeadingTree('## Title   \n')
    expect(tree[0].title).toBe('Title')
  })

  it('handles empty string', () => {
    expect(computeHeadingTree('')).toEqual([])
  })
})

describe('computeFileCount', () => {
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'filecount-'))
  })

  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  it('counts files in a flat directory', () => {
    writeFileSync(join(tmpDir, 'a.txt'), 'a')
    writeFileSync(join(tmpDir, 'b.txt'), 'b')
    expect(computeFileCount(tmpDir)).toBe(2)
  })

  it('counts files recursively', () => {
    const { mkdirSync: mkS } = require('node:fs')
    mkS(join(tmpDir, 'sub'))
    writeFileSync(join(tmpDir, 'a.txt'), 'a')
    writeFileSync(join(tmpDir, 'sub', 'b.txt'), 'b')
    expect(computeFileCount(tmpDir)).toBe(2)
  })

  it('returns 0 for nonexistent directory', () => {
    expect(computeFileCount(join(tmpDir, 'nope'))).toBe(0)
  })

  it('returns 0 for empty directory', () => {
    const { mkdirSync: mkS } = require('node:fs')
    const emptyDir = join(tmpDir, 'empty')
    mkS(emptyDir)
    expect(computeFileCount(emptyDir)).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// filterForProcessing
// ---------------------------------------------------------------------------

describe('filterForProcessing', () => {
  const make = (overrides: Partial<CatalogEntryWithTier1>): CatalogEntryWithTier1 =>
    ({
      source: 'org/repo',
      skill: 'x',
      availability: 'available' as const,
      ...overrides,
    }) as CatalogEntryWithTier1

  it('default: skips analyzed entries (wordCount + attemptCount=0)', () => {
    const entries = [make({ wordCount: 500, attemptCount: 0 })]
    expect(filterForProcessing(entries)).toHaveLength(0)
  })

  it('default: includes unattempted entries (no wordCount, no attemptCount)', () => {
    const entries = [make({})]
    expect(filterForProcessing(entries)).toHaveLength(1)
  })

  it('default: includes retryable entries under attempt limit', () => {
    const entries = [make({ attemptCount: 1, retryable: true })]
    expect(filterForProcessing(entries)).toHaveLength(1)
  })

  it('default: excludes entries at attempt limit', () => {
    const entries = [make({ attemptCount: 2, retryable: true })]
    expect(filterForProcessing(entries)).toHaveLength(0)
  })

  it('default: excludes non-retryable entries', () => {
    const entries = [make({ attemptCount: 1, retryable: false })]
    expect(filterForProcessing(entries)).toHaveLength(0)
  })

  it('default: excludes non-available entries', () => {
    const entries = [make({ availability: 'not_found' as const })]
    expect(filterForProcessing(entries)).toHaveLength(0)
  })

  it('--force: includes all available entries', () => {
    const entries = [
      make({ wordCount: 500, attemptCount: 0 }),
      make({ attemptCount: 5, retryable: false, skill: 'y' }),
      make({ skill: 'z' }),
    ]
    expect(filterForProcessing(entries, { force: true })).toHaveLength(3)
  })

  it('--force: still excludes non-available', () => {
    const entries = [make({ availability: 'not_found' as const })]
    expect(filterForProcessing(entries, { force: true })).toHaveLength(0)
  })

  it('--retry-errors: only retryable with attemptCount > 0', () => {
    const entries = [
      make({ attemptCount: 1, retryable: true }),
      make({ skill: 'y' }), // unattempted — excluded
      make({ attemptCount: 1, retryable: false, skill: 'z' }), // not retryable
    ]
    const result = filterForProcessing(entries, { retryErrors: true })
    expect(result).toHaveLength(1)
    expect(result[0].skill).toBe('x')
  })

  it('--retry-errors --force: all errored, ignoring limits', () => {
    const entries = [
      make({ attemptCount: 5, retryable: false }),
      make({ attemptCount: 1, retryable: true, skill: 'y' }),
      make({ skill: 'z' }), // unattempted — excluded
    ]
    const result = filterForProcessing(entries, { retryErrors: true, force: true })
    expect(result).toHaveLength(2)
  })

  it('backward compat: entries without attemptCount treated as 0', () => {
    const entries = [make({})] // no attemptCount field
    expect(filterForProcessing(entries)).toHaveLength(1) // unattempted
  })
})

// ---------------------------------------------------------------------------
// validateBatchResults
// ---------------------------------------------------------------------------

describe('validateBatchResults', () => {
  it('reports no issues for clean results', () => {
    const results: Tier1Result[] = [
      {
        source: 'org/a',
        skill: 'x',
        wordCount: 500,
        contentHash: 'sha256:abc',
        keywords: ['k1'],
      },
    ]
    const report = validateBatchResults(results)
    expect(report.total).toBe(1)
    expect(report.issues).toHaveLength(0)
    expect(report.missingContentHash).toBe(0)
  })

  it('detects missing contentHash', () => {
    const results: Tier1Result[] = [
      { source: 'org/a', skill: 'x', wordCount: 500, keywords: ['k1'] },
    ]
    const report = validateBatchResults(results)
    expect(report.missingContentHash).toBe(1)
    expect(report.issues.length).toBeGreaterThan(0)
  })

  it('detects pending contentHash', () => {
    const results: Tier1Result[] = [
      {
        source: 'org/a',
        skill: 'x',
        wordCount: 500,
        contentHash: 'sha256:pending',
        keywords: ['k1'],
      },
    ]
    const report = validateBatchResults(results)
    expect(report.pendingContentHash).toBe(1)
  })

  it('detects missing keywords', () => {
    const results: Tier1Result[] = [
      { source: 'org/a', skill: 'x', wordCount: 500, contentHash: 'sha256:abc' },
    ]
    const report = validateBatchResults(results)
    expect(report.missingKeywords).toBe(1)
  })

  it('ignores error results (no wordCount)', () => {
    const results: Tier1Result[] = [
      { source: 'org/a', skill: 'x' }, // no wordCount — error entry, skip validation
    ]
    const report = validateBatchResults(results)
    expect(report.total).toBe(0)
    expect(report.issues).toHaveLength(0)
  })
})
