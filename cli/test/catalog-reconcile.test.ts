import { describe, expect, test } from 'bun:test'
import type { CatalogEntryWithTier1 } from '../lib/catalog'
import type {
  DiscoveredSkillResult,
  RepoDiscoveryResult,
  RepoManifest,
} from '../lib/catalog-discover'
import { detectMoveRenames, reconcile } from '../lib/catalog-reconcile'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeManifest(repo: string, skills: string[]): RepoManifest {
  return {
    repo,
    clonedAt: '2026-03-23T00:00:00Z',
    headSha: 'abc123',
    totalFiles: 10,
    repoSizeBytes: 1024,
    archived: false,
    skillCount: skills.length,
    skills,
  }
}

function makeDiscoveredSkill(source: string, skill: string, path: string): DiscoveredSkillResult {
  return {
    source,
    skill,
    mechanical: {
      discoveredPath: path,
      lastSeenAt: '2026-03-23T00:00:00Z',
      wordCount: 100,
      sectionCount: 3,
      fileCount: 1,
      headingTree: [{ depth: 1, title: skill }],
      contentHash: `sha256:${skill.padEnd(64, '0')}`,
      keywords: [skill],
    },
  }
}

function makeCatalogEntry(
  source: string,
  skill: string,
  opts?: { discoveredPath?: string; contentHash?: string }
): CatalogEntryWithTier1 {
  return {
    source,
    skill,
    availability: 'available',
    wordCount: 100,
    discoveredPath: opts?.discoveredPath,
    contentHash: opts?.contentHash,
  } as CatalogEntryWithTier1
}

function makeDiscoveryResult(
  source: string,
  skills: DiscoveredSkillResult[],
  missing?: Array<{ source: string; skill: string }>
): RepoDiscoveryResult {
  return {
    manifest: makeManifest(
      source,
      skills.map((s) => s.skill)
    ),
    skills,
    missing: missing ?? [],
    errors: [],
  }
}

// ---------------------------------------------------------------------------
// reconcile — basic cases
// ---------------------------------------------------------------------------

describe('reconcile', () => {
  test('detects unchanged/updated skills', () => {
    const catalog = [makeCatalogEntry('org/repo', 'foo', { discoveredPath: 'skills/foo' })]
    const discovery = [
      makeDiscoveryResult('org/repo', [makeDiscoveredSkill('org/repo', 'foo', 'skills/foo')]),
    ]

    const report = reconcile(catalog, discovery)
    expect(report.updated).toHaveLength(1)
    expect(report.updated[0].skill).toBe('foo')
    expect(report.moved).toHaveLength(0)
    expect(report.added).toHaveLength(0)
    expect(report.removed).toHaveLength(0)
  })

  test('detects moved skills (same name, different path)', () => {
    const catalog = [makeCatalogEntry('org/repo', 'foo', { discoveredPath: 'skills/foo' })]
    const discovery = [
      makeDiscoveryResult('org/repo', [
        makeDiscoveredSkill('org/repo', 'foo', 'context/skills/foo'),
      ]),
    ]

    const report = reconcile(catalog, discovery)
    expect(report.moved).toHaveLength(1)
    expect(report.moved[0].movedFrom).toBe('skills/foo')
    expect(report.moved[0].discovered?.mechanical.discoveredPath).toBe('context/skills/foo')
  })

  test('detects added skills (in repo but not catalog)', () => {
    const catalog: CatalogEntryWithTier1[] = []
    const discovery = [
      makeDiscoveryResult('org/repo', [makeDiscoveredSkill('org/repo', 'new-skill', 'skills/new')]),
    ]

    const report = reconcile(catalog, discovery)
    expect(report.added).toHaveLength(1)
    expect(report.added[0].skill).toBe('new-skill')
  })

  test('detects removed skills (in catalog but not repo)', () => {
    const catalog = [makeCatalogEntry('org/repo', 'gone')]
    const discovery = [makeDiscoveryResult('org/repo', [])] // no skills found

    const report = reconcile(catalog, discovery)
    expect(report.removed).toHaveLength(1)
    expect(report.removed[0].skill).toBe('gone')
  })

  test('does not mark as removed if repo had clone errors', () => {
    const catalog = [makeCatalogEntry('org/repo', 'maybe-gone')]
    const discovery: RepoDiscoveryResult[] = [
      {
        manifest: makeManifest('org/repo', []),
        skills: [],
        missing: [{ source: 'org/repo', skill: 'maybe-gone' }],
        errors: [{ source: 'org/repo', error: 'clone failed', errorType: 'download_failed' }],
      },
    ]

    const report = reconcile(catalog, discovery)
    expect(report.removed).toHaveLength(0) // not removed because clone failed
    expect(report.errors).toHaveLength(1)
  })

  test('detects renamed skills (same path, different name)', () => {
    const catalog = [makeCatalogEntry('org/repo', 'old-name', { discoveredPath: 'skills/foo' })]
    const discovery = [
      makeDiscoveryResult('org/repo', [makeDiscoveredSkill('org/repo', 'new-name', 'skills/foo')]),
    ]

    const report = reconcile(catalog, discovery)
    expect(report.renamed).toHaveLength(1)
    expect(report.renamed[0].skill).toBe('new-name')
    expect(report.renamed[0].renamedFrom).toBe('old-name')
  })

  test('handles mixed results from multiple repos', () => {
    const catalog = [
      makeCatalogEntry('a/repo', 'skill-a', { discoveredPath: 'skills/a' }),
      makeCatalogEntry('b/repo', 'skill-b'),
    ]
    const discovery = [
      makeDiscoveryResult('a/repo', [makeDiscoveredSkill('a/repo', 'skill-a', 'skills/a')]),
      makeDiscoveryResult('b/repo', [makeDiscoveredSkill('b/repo', 'skill-c', 'skills/c')]),
    ]

    const report = reconcile(catalog, discovery)
    expect(report.updated).toHaveLength(1) // skill-a unchanged
    expect(report.added).toHaveLength(1) // skill-c is new
    expect(report.removed).toHaveLength(1) // skill-b is gone
  })

  test('is idempotent', () => {
    const catalog = [makeCatalogEntry('org/repo', 'foo', { discoveredPath: 'skills/foo' })]
    const discovery = [
      makeDiscoveryResult('org/repo', [makeDiscoveredSkill('org/repo', 'foo', 'skills/foo')]),
    ]

    const r1 = reconcile(catalog, discovery)
    const r2 = reconcile(catalog, discovery)
    expect(r1.updated.length).toBe(r2.updated.length)
    expect(r1.moved.length).toBe(r2.moved.length)
    expect(r1.added.length).toBe(r2.added.length)
    expect(r1.removed.length).toBe(r2.removed.length)
  })
})

// ---------------------------------------------------------------------------
// detectMoveRenames — contentHash preservation
// ---------------------------------------------------------------------------

describe('detectMoveRenames', () => {
  test('promotes add+remove to move when contentHash matches', () => {
    const hash = 'sha256:matching_hash'.padEnd(71, '0')
    const catalog = [
      makeCatalogEntry('org/repo', 'old-name', { discoveredPath: 'old/path', contentHash: hash }),
    ]

    const disc = makeDiscoveredSkill('org/repo', 'new-name', 'new/path')
    disc.mechanical.contentHash = hash

    const report = {
      unchanged: [],
      updated: [],
      moved: [],
      added: [
        { source: 'org/repo', skill: 'new-name', action: 'added' as const, discovered: disc },
      ],
      removed: [{ source: 'org/repo', skill: 'old-name', action: 'removed' as const }],
      renamed: [],
      errors: [],
    }

    detectMoveRenames(report, catalog)

    expect(report.added).toHaveLength(0) // promoted out of added
    expect(report.removed).toHaveLength(0) // promoted out of removed
    expect(report.moved).toHaveLength(1)
    expect(report.moved[0].skill).toBe('new-name')
    expect(report.moved[0].renamedFrom).toBe('old-name')
    expect(report.moved[0].movedFrom).toBe('old/path')
  })

  test('does not promote when contentHash differs', () => {
    const catalog = [
      makeCatalogEntry('org/repo', 'old', {
        discoveredPath: 'old/path',
        contentHash: 'sha256:aaa',
      }),
    ]

    const disc = makeDiscoveredSkill('org/repo', 'new', 'new/path')
    disc.mechanical.contentHash = 'sha256:bbb'

    const report = {
      unchanged: [],
      updated: [],
      moved: [],
      added: [{ source: 'org/repo', skill: 'new', action: 'added' as const, discovered: disc }],
      removed: [{ source: 'org/repo', skill: 'old', action: 'removed' as const }],
      renamed: [],
      errors: [],
    }

    detectMoveRenames(report, catalog)

    expect(report.added).toHaveLength(1) // not promoted
    expect(report.removed).toHaveLength(1) // not promoted
    expect(report.moved).toHaveLength(0)
  })
})
