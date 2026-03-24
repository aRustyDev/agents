import { describe, expect, it } from 'bun:test'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  type BackfillResult,
  type CatalogEntryWithTier1,
  extractKeywords,
  mergeBackfillResults,
} from '../lib/catalog'

// ---------------------------------------------------------------------------
// extractKeywords
// ---------------------------------------------------------------------------

describe('extractKeywords', () => {
  it('extracts terms from h1-h3 headings', () => {
    const content = '# React Components\n## State Management\n### Custom Hooks\n#### Deep Detail'
    const kw = extractKeywords(content)
    expect(kw).toContain('react')
    expect(kw).toContain('components')
    expect(kw).toContain('state')
    expect(kw).toContain('management')
    expect(kw).toContain('custom')
    expect(kw).toContain('hooks')
    // h4 should be excluded
    expect(kw).not.toContain('deep')
  })

  it('extracts terms from frontmatter description', () => {
    const content =
      '---\nname: test\ndescription: Build scalable REST APIs with Express\n---\n# Title'
    const kw = extractKeywords(content)
    expect(kw).toContain('build')
    expect(kw).toContain('scalable')
    expect(kw).toContain('rest')
    expect(kw).toContain('apis')
    expect(kw).toContain('express')
  })

  it('extracts code fence languages', () => {
    const content =
      '# Guide\n```typescript\nconst x = 1\n```\n```python\nprint("hi")\n```\n```bash\necho hi\n```'
    const kw = extractKeywords(content)
    expect(kw).toContain('typescript')
    expect(kw).toContain('python')
    expect(kw).toContain('bash')
  })

  it('excludes plain text/markdown code fences', () => {
    const content = '# Guide\n```text\nplain\n```\n```markdown\n# md\n```\n```md\nstuff\n```'
    const kw = extractKeywords(content)
    expect(kw).not.toContain('text')
    expect(kw).not.toContain('markdown')
    expect(kw).not.toContain('md')
  })

  it('filters stop words', () => {
    const content = '# How to Use the Framework for All Applications'
    const kw = extractKeywords(content)
    expect(kw).not.toContain('how')
    expect(kw).not.toContain('the')
    expect(kw).not.toContain('for')
    expect(kw).not.toContain('all')
    expect(kw).toContain('framework')
    expect(kw).toContain('applications')
  })

  it('deduplicates keywords', () => {
    const content = '# React\n## React Patterns\ndescription: React development'
    const kw = extractKeywords(content)
    const reactCount = kw.filter((k) => k === 'react').length
    expect(reactCount).toBe(1)
  })

  it('caps at 30 keywords', () => {
    const headings = Array.from({ length: 40 }, (_, i) => `## Keyword${i} Unique${i}`)
    const content = headings.join('\n')
    const kw = extractKeywords(content)
    expect(kw.length).toBeLessThanOrEqual(30)
  })

  it('returns empty array for empty content', () => {
    expect(extractKeywords('')).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// mergeBackfillResults
// ---------------------------------------------------------------------------

describe('mergeBackfillResults', () => {
  let tmpDir: string
  let catalogPath: string
  let errorLogPath: string

  function setup(entries: CatalogEntryWithTier1[]) {
    tmpDir = mkdtempSync(join(tmpdir(), 'backfill-test-'))
    catalogPath = join(tmpDir, 'catalog.ndjson')
    errorLogPath = join(tmpDir, 'errors.ndjson')
    writeFileSync(catalogPath, entries.map((e) => JSON.stringify(e)).join('\n') + '\n')
    writeFileSync(errorLogPath, '')
  }

  function readCatalog(): CatalogEntryWithTier1[] {
    const { readFileSync } = require('node:fs')
    return readFileSync(catalogPath, 'utf8')
      .trim()
      .split('\n')
      .filter(Boolean)
      .map((l: string) => JSON.parse(l))
  }

  it('fills missing headingTree without overwriting existing fields', () => {
    setup([
      {
        source: 'org/repo',
        skill: 'test',
        availability: 'available',
        wordCount: 100,
        keywords: ['existing'],
      } as CatalogEntryWithTier1,
    ])

    const results: BackfillResult[] = [
      {
        source: 'org/repo',
        skill: 'test',
        headingTree: [{ depth: 1, title: 'Title' }],
        keywords: ['new-keyword'],
      },
    ]

    const { updated } = mergeBackfillResults(catalogPath, errorLogPath, results)
    expect(updated).toBe(1)

    const entries = readCatalog()
    expect(entries[0].headingTree).toEqual([{ depth: 1, title: 'Title' }])
    // Existing keywords should NOT be overwritten
    expect(entries[0].keywords).toEqual(['existing'])
  })

  it('fills keywords when empty array', () => {
    setup([
      {
        source: 'org/repo',
        skill: 'test',
        availability: 'available',
        wordCount: 100,
        keywords: [],
      } as CatalogEntryWithTier1,
    ])

    const results: BackfillResult[] = [
      { source: 'org/repo', skill: 'test', keywords: ['react', 'hooks'] },
    ]

    const { updated } = mergeBackfillResults(catalogPath, errorLogPath, results)
    expect(updated).toBe(1)

    const entries = readCatalog()
    expect(entries[0].keywords).toEqual(['react', 'hooks'])
  })

  it('reclassifies batch_failed to download_failed', () => {
    setup([
      {
        source: 'org/repo',
        skill: 'broken',
        availability: 'available',
        lastErrorType: 'batch_failed',
        attemptCount: 2,
      } as CatalogEntryWithTier1,
    ])

    const results: BackfillResult[] = [
      {
        source: 'org/repo',
        skill: 'broken',
        error: 'clone failed: not found',
        errorType: 'download_failed',
        errorDetail: 'repo does not exist',
      },
    ]

    const { reclassified } = mergeBackfillResults(catalogPath, errorLogPath, results)
    expect(reclassified).toBe(1)

    const entries = readCatalog()
    expect(entries[0].lastErrorType).toBe('download_failed')
  })

  it('does not reclassify non-batch_failed errors', () => {
    setup([
      {
        source: 'org/repo',
        skill: 'timeout',
        availability: 'available',
        lastErrorType: 'download_timeout',
        attemptCount: 1,
      } as CatalogEntryWithTier1,
    ])

    const results: BackfillResult[] = [
      {
        source: 'org/repo',
        skill: 'timeout',
        error: 'clone failed',
        errorType: 'download_failed',
      },
    ]

    const { reclassified } = mergeBackfillResults(catalogPath, errorLogPath, results)
    expect(reclassified).toBe(0)

    const entries = readCatalog()
    expect(entries[0].lastErrorType).toBe('download_timeout') // unchanged
  })

  it('reports correct counts', () => {
    setup([
      {
        source: 'a/b',
        skill: 's1',
        availability: 'available',
        wordCount: 50,
      } as CatalogEntryWithTier1,
      {
        source: 'a/b',
        skill: 's2',
        availability: 'available',
        lastErrorType: 'batch_failed',
      } as CatalogEntryWithTier1,
      {
        source: 'c/d',
        skill: 's3',
        availability: 'available',
        wordCount: 100,
      } as CatalogEntryWithTier1,
    ])

    const results: BackfillResult[] = [
      { source: 'a/b', skill: 's1', headingTree: [{ depth: 1, title: 'T' }] },
      { source: 'a/b', skill: 's2', error: 'nope', errorType: 'invalid_source_entry' },
      { source: 'c/d', skill: 's3' }, // nothing to fill
    ]

    const { updated, reclassified, failed } = mergeBackfillResults(
      catalogPath,
      errorLogPath,
      results
    )
    expect(updated).toBe(1)
    expect(reclassified).toBe(1)
    expect(failed).toBe(1)
  })
})
