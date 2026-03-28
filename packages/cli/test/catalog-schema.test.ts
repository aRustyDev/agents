import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  computeFileTree,
  computeLineCount,
  computeSectionMap,
  computeSkillSizeBytes,
  isSimpleSkill,
  mergeRepoManifest,
  migrateCatalogSchema,
  type RepoManifest,
  readRepoManifest,
  writeRepoManifest,
} from '../src/lib/catalog'

// ---------------------------------------------------------------------------
// computeSectionMap
// ---------------------------------------------------------------------------

describe('computeSectionMap', () => {
  test('extracts headings with line numbers', () => {
    const content = '# Title\n\nSome text\n\n## Section A\n\nMore text\n\n### Subsection\n'
    const map = computeSectionMap(content)
    expect(map).toEqual([
      { heading: 'Title', line: 1, depth: 1 },
      { heading: 'Section A', line: 5, depth: 2 },
      { heading: 'Subsection', line: 9, depth: 3 },
    ])
  })

  test('returns empty for content without headings', () => {
    expect(computeSectionMap('just text\nno headings\n')).toEqual([])
  })

  test('handles all heading depths', () => {
    const content = '# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6\n'
    const map = computeSectionMap(content)
    expect(map).toHaveLength(6)
    expect(map[5]).toEqual({ heading: 'H6', line: 6, depth: 6 })
  })
})

// ---------------------------------------------------------------------------
// computeLineCount
// ---------------------------------------------------------------------------

describe('computeLineCount', () => {
  test('counts lines', () => {
    expect(computeLineCount('line1\nline2\nline3\n')).toBe(4)
  })

  test('returns 0 for empty content', () => {
    expect(computeLineCount('')).toBe(0)
  })

  test('single line no newline', () => {
    expect(computeLineCount('hello')).toBe(1)
  })
})

// ---------------------------------------------------------------------------
// computeFileTree
// ---------------------------------------------------------------------------

describe('computeFileTree', () => {
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'filetree-'))
  })
  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  test('lists files recursively with relative paths', () => {
    writeFileSync(join(tmpDir, 'SKILL.md'), 'content')
    mkdirSync(join(tmpDir, 'resources'))
    writeFileSync(join(tmpDir, 'resources', 'guide.md'), 'guide')
    const tree = computeFileTree(tmpDir)
    expect(tree).toContain('SKILL.md')
    expect(tree).toContain(join('resources', 'guide.md'))
  })

  test('returns empty for nonexistent directory', () => {
    expect(computeFileTree('/tmp/nonexistent-dir-xyz')).toEqual([])
  })

  test('returns sorted paths', () => {
    writeFileSync(join(tmpDir, 'z.md'), '')
    writeFileSync(join(tmpDir, 'a.md'), '')
    writeFileSync(join(tmpDir, 'm.md'), '')
    const tree = computeFileTree(tmpDir)
    expect(tree).toEqual(['a.md', 'm.md', 'z.md'])
  })

  test('skips .git and node_modules', () => {
    mkdirSync(join(tmpDir, '.git'))
    writeFileSync(join(tmpDir, '.git', 'HEAD'), 'ref')
    mkdirSync(join(tmpDir, 'node_modules'))
    writeFileSync(join(tmpDir, 'node_modules', 'pkg.json'), '{}')
    writeFileSync(join(tmpDir, 'SKILL.md'), 'content')
    const tree = computeFileTree(tmpDir)
    expect(tree).toEqual(['SKILL.md'])
  })
})

// ---------------------------------------------------------------------------
// computeSkillSizeBytes
// ---------------------------------------------------------------------------

describe('computeSkillSizeBytes', () => {
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'skillsize-'))
  })
  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  test('sums file sizes recursively', () => {
    writeFileSync(join(tmpDir, 'a.txt'), 'hello') // 5 bytes
    writeFileSync(join(tmpDir, 'b.txt'), 'world!') // 6 bytes
    const size = computeSkillSizeBytes(tmpDir)
    expect(size).toBe(11)
  })

  test('returns 0 for nonexistent directory', () => {
    expect(computeSkillSizeBytes('/tmp/nonexistent-dir-xyz')).toBe(0)
  })

  test('includes subdirectory files', () => {
    mkdirSync(join(tmpDir, 'sub'))
    writeFileSync(join(tmpDir, 'root.txt'), 'aaa') // 3
    writeFileSync(join(tmpDir, 'sub', 'deep.txt'), 'bb') // 2
    expect(computeSkillSizeBytes(tmpDir)).toBe(5)
  })
})

// ---------------------------------------------------------------------------
// isSimpleSkill
// ---------------------------------------------------------------------------

describe('isSimpleSkill', () => {
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'simple-'))
  })
  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  test('true when only SKILL.md exists', () => {
    writeFileSync(join(tmpDir, 'SKILL.md'), 'content')
    expect(isSimpleSkill(tmpDir)).toBe(true)
  })

  test('false when additional files exist', () => {
    writeFileSync(join(tmpDir, 'SKILL.md'), 'content')
    writeFileSync(join(tmpDir, 'README.md'), 'readme')
    expect(isSimpleSkill(tmpDir)).toBe(false)
  })

  test('false when subdirectories exist', () => {
    writeFileSync(join(tmpDir, 'SKILL.md'), 'content')
    mkdirSync(join(tmpDir, 'resources'))
    expect(isSimpleSkill(tmpDir)).toBe(false)
  })

  test('false for nonexistent directory', () => {
    expect(isSimpleSkill('/tmp/nonexistent-dir-xyz')).toBe(false)
  })

  test('false for empty directory', () => {
    expect(isSimpleSkill(tmpDir)).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// RepoManifest I/O
// ---------------------------------------------------------------------------

describe('RepoManifest I/O', () => {
  let tmpDir: string
  let manifestPath: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'manifest-'))
    manifestPath = join(tmpDir, 'repos.ndjson')
  })
  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  const sampleManifest: RepoManifest = {
    repo: 'org/repo',
    clonedAt: '2026-03-23T00:00:00Z',
    headSha: 'abc123',
    totalFiles: 42,
    repoSizeBytes: 1024,
    archived: false,
    skillCount: 3,
    skills: ['skill-a', 'skill-b', 'skill-c'],
  }

  test('write and read roundtrips', () => {
    writeRepoManifest(manifestPath, [sampleManifest])
    const read = readRepoManifest(manifestPath)
    expect(read).toHaveLength(1)
    expect(read[0].repo).toBe('org/repo')
    expect(read[0].skills).toEqual(['skill-a', 'skill-b', 'skill-c'])
  })

  test('read returns empty for nonexistent file', () => {
    expect(readRepoManifest('/tmp/nonexistent.ndjson')).toEqual([])
  })

  test('merge updates existing entry', () => {
    writeRepoManifest(manifestPath, [sampleManifest])
    const updated = { ...sampleManifest, headSha: 'def456', skillCount: 5 }
    mergeRepoManifest(manifestPath, updated)
    const read = readRepoManifest(manifestPath)
    expect(read).toHaveLength(1)
    expect(read[0].headSha).toBe('def456')
  })

  test('merge appends new entry', () => {
    writeRepoManifest(manifestPath, [sampleManifest])
    const another: RepoManifest = { ...sampleManifest, repo: 'other/repo' }
    mergeRepoManifest(manifestPath, another)
    const read = readRepoManifest(manifestPath)
    expect(read).toHaveLength(2)
  })
})

// ---------------------------------------------------------------------------
// migrateCatalogSchema
// ---------------------------------------------------------------------------

describe('migrateCatalogSchema', () => {
  let tmpDir: string
  let catalogPath: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'migrate-'))
    catalogPath = join(tmpDir, 'catalog.ndjson')
  })
  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  test('renames source_invalid to invalid_source_entry', () => {
    const entries = [
      { source: 'a/b', skill: 's1', availability: 'available', lastErrorType: 'source_invalid' },
      { source: 'c/d', skill: 's2', availability: 'available', lastErrorType: 'download_failed' },
    ]
    writeFileSync(catalogPath, `${entries.map((e) => JSON.stringify(e)).join('\n')}\n`)

    const count = migrateCatalogSchema(catalogPath)
    expect(count).toBe(1)

    const { readFileSync } = require('node:fs')
    const lines = readFileSync(catalogPath, 'utf8').trim().split('\n')
    const migrated = JSON.parse(lines[0])
    expect(migrated.lastErrorType).toBe('invalid_source_entry')
    // Other entries unchanged
    expect(JSON.parse(lines[1]).lastErrorType).toBe('download_failed')
  })

  test('returns 0 for nonexistent catalog', () => {
    expect(migrateCatalogSchema('/tmp/nonexistent.ndjson')).toBe(0)
  })

  test('idempotent — running twice has no effect', () => {
    const entries = [
      { source: 'a/b', skill: 's1', availability: 'available', lastErrorType: 'source_invalid' },
    ]
    writeFileSync(catalogPath, `${entries.map((e) => JSON.stringify(e)).join('\n')}\n`)

    migrateCatalogSchema(catalogPath)
    const second = migrateCatalogSchema(catalogPath)
    expect(second).toBe(0)
  })
})
