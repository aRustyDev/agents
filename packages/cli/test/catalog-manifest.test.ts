import { describe, expect, test } from 'bun:test'
import type { CatalogEntryWithTier1 } from '../src/lib/catalog'
import type { DiscoveredSkillResult } from '../src/lib/catalog-discover'
import { buildManifest, buildManifestFromEntry, formatManifestBatch } from '../src/lib/catalog-manifest'

const sampleDiscovery: DiscoveredSkillResult = {
  source: 'org/repo',
  skill: 'test-skill',
  mechanical: {
    discoveredPath: 'skills/test-skill',
    lastSeenAt: '2026-03-23T00:00:00Z',
    wordCount: 500,
    sectionCount: 5,
    fileCount: 3,
    headingTree: [
      { depth: 1, title: 'Test Skill' },
      { depth: 2, title: 'Setup' },
    ],
    contentHash: 'sha256:abc123',
    keywords: ['test', 'skill', 'typescript'],
    sectionMap: [
      { heading: 'Test Skill', line: 1, depth: 1 },
      { heading: 'Setup', line: 5, depth: 2 },
    ],
    fileTree: ['SKILL.md', 'resources/guide.md', 'examples/basic.ts'],
    skillSizeBytes: 4096,
    isSimple: false,
  },
}

const sampleContent = '---\nname: test-skill\n---\n# Test Skill\n\n## Setup\n\nDo stuff.'

describe('buildManifest', () => {
  test('builds manifest from discovery result + content', () => {
    const manifest = buildManifest(sampleDiscovery, sampleContent)
    expect(manifest.source).toBe('org/repo')
    expect(manifest.skill).toBe('test-skill')
    expect(manifest.content).toBe(sampleContent)
    expect(manifest.wordCount).toBe(500)
    expect(manifest.sectionCount).toBe(5)
    expect(manifest.fileCount).toBe(3)
    expect(manifest.headingTree).toHaveLength(2)
    expect(manifest.sectionMap).toHaveLength(2)
    expect(manifest.fileTree).toHaveLength(3)
    expect(manifest.contentHash).toBe('sha256:abc123')
    expect(manifest.mechanicalKeywords).toEqual(['test', 'skill', 'typescript'])
    expect(manifest.isSimple).toBe(false)
  })
})

describe('buildManifestFromEntry', () => {
  test('builds manifest from catalog entry + content', () => {
    const entry: CatalogEntryWithTier1 = {
      source: 'org/repo',
      skill: 'from-entry',
      availability: 'available',
      wordCount: 200,
      sectionCount: 2,
      fileCount: 1,
      headingTree: [{ depth: 1, title: 'From Entry' }],
      contentHash: 'sha256:def456',
      keywords: ['entry', 'test'],
      isSimple: true,
    } as CatalogEntryWithTier1

    const manifest = buildManifestFromEntry(entry, '# From Entry\nContent.')
    expect(manifest.source).toBe('org/repo')
    expect(manifest.skill).toBe('from-entry')
    expect(manifest.wordCount).toBe(200)
    expect(manifest.mechanicalKeywords).toEqual(['entry', 'test'])
    expect(manifest.isSimple).toBe(true)
  })

  test('handles missing optional fields', () => {
    const entry: CatalogEntryWithTier1 = {
      source: 'org/repo',
      skill: 'minimal',
      availability: 'available',
    } as CatalogEntryWithTier1

    const manifest = buildManifestFromEntry(entry, '')
    expect(manifest.wordCount).toBe(0)
    expect(manifest.headingTree).toEqual([])
    expect(manifest.mechanicalKeywords).toEqual([])
  })
})

describe('formatManifestBatch', () => {
  test('formats manifests as NDJSON', () => {
    const manifest = buildManifest(sampleDiscovery, sampleContent)
    const formatted = formatManifestBatch([manifest])
    const parsed = JSON.parse(formatted)
    expect(parsed.source).toBe('org/repo')
    expect(parsed.skill).toBe('test-skill')
    expect(parsed.content).toContain('# Test Skill')
    expect(parsed.wordCount).toBe(500)
  })

  test('truncates content over 50K chars', () => {
    const longContent = 'x'.repeat(60_000)
    const manifest = buildManifest(sampleDiscovery, longContent)
    const formatted = formatManifestBatch([manifest])
    const parsed = JSON.parse(formatted)
    expect(parsed.content.length).toBeLessThan(55_000)
    expect(parsed.content).toContain('[... truncated at 50K chars ...]')
  })

  test('formats multiple manifests as separate lines', () => {
    const m1 = buildManifest(sampleDiscovery, 'content 1')
    const m2 = buildManifest({ ...sampleDiscovery, skill: 'other' }, 'content 2')
    const formatted = formatManifestBatch([m1, m2])
    const lines = formatted.trim().split('\n')
    expect(lines).toHaveLength(2)
    expect(JSON.parse(lines[0]).skill).toBe('test-skill')
    expect(JSON.parse(lines[1]).skill).toBe('other')
  })
})
