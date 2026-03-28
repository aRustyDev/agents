/**
 * Tests for external skill dependency management.
 *
 * Validates the core logic of lib/external-skills.ts and related
 * additions to lib/hash.ts and lib/schemas.ts WITHOUT making
 * network calls or GitHub API calls.
 */

import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import {
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readlinkSync,
  rmSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { lockKey } from '@agents/core/hash'
import {
  getStatus,
  readLock,
  readManifest,
  refreshLinks,
  writeLock,
} from '@agents/sdk/providers/local/external'
import {
  ExternalLockEntry,
  ExternalLockfile,
  ExternalSkillEntry,
  ExternalSourcesManifest,
} from '@agents/sdk/providers/local/schemas'
import * as v from 'valibot'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

let tempDir: string

function createTempDir(): string {
  const dir = join(
    tmpdir(),
    `ext-skills-test-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
  )
  mkdirSync(dir, { recursive: true })
  return dir
}

function writeYaml(dir: string, filename: string, content: string): void {
  mkdirSync(dir, { recursive: true })
  writeFileSync(join(dir, filename), content, 'utf-8')
}

function writeJson(dir: string, filename: string, data: unknown): void {
  mkdirSync(dir, { recursive: true })
  writeFileSync(join(dir, filename), JSON.stringify(data, null, 2) + '\n', 'utf-8')
}

function createSkillSnapshot(externalDir: string, source: string, skill: string): void {
  const dir = join(externalDir, source, skill)
  mkdirSync(dir, { recursive: true })
  writeFileSync(
    join(dir, 'SKILL.md'),
    `---\nname: ${skill}\ndescription: Test skill\n---\n\n# ${skill}\n`,
    'utf-8'
  )
}

// ---------------------------------------------------------------------------
// lockKey
// ---------------------------------------------------------------------------

describe('lockKey', () => {
  test('is deterministic: same input produces same output', () => {
    const k1 = lockKey('steveyegge/beads', 'beads')
    const k2 = lockKey('steveyegge/beads', 'beads')
    expect(k1).toBe(k2)
  })

  test('different inputs produce different keys', () => {
    const k1 = lockKey('steveyegge/beads', 'beads')
    const k2 = lockKey('vercel-labs/skills', 'find-skills')
    expect(k1).not.toBe(k2)
  })

  test('output is exactly 12 hex characters', () => {
    const key = lockKey('some-org/repo', 'their-skill')
    expect(key).toMatch(/^[a-f0-9]{12}$/)
  })

  test('different skills in same repo produce different keys', () => {
    const k1 = lockKey('org/repo', 'skill-a')
    const k2 = lockKey('org/repo', 'skill-b')
    expect(k1).not.toBe(k2)
  })

  test('same skill name in different repos produces different keys', () => {
    const k1 = lockKey('org-a/repo', 'skill')
    const k2 = lockKey('org-b/repo', 'skill')
    expect(k1).not.toBe(k2)
  })
})

// ---------------------------------------------------------------------------
// ExternalSkillEntry schema
// ---------------------------------------------------------------------------

describe('ExternalSkillEntry schema', () => {
  test('accepts passthrough entry', () => {
    const entry = {
      source: 'steveyegge/beads',
      skill: 'beads',
      passthrough: true,
    }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(true)
  })

  test('accepts derived entry', () => {
    const entry = {
      source: 'some-org/repo',
      skill: 'their-skill',
      passthrough: false,
      derived_by: ['my-local-skill'],
    }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(true)
  })

  test('accepts entry with ref', () => {
    const entry = {
      source: 'old-org/archived-repo',
      skill: 'legacy-skill',
      ref: 'v2.1.0',
      passthrough: false,
      derived_by: ['my-modern-skill'],
    }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(true)
  })

  test('rejects passthrough + derived_by together', () => {
    const entry = {
      source: 'org/repo',
      skill: 'skill',
      passthrough: true,
      derived_by: ['local-skill'],
    }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(false)
  })

  test('allows passthrough false with derived_by', () => {
    const entry = {
      source: 'org/repo',
      skill: 'skill',
      passthrough: false,
      derived_by: ['local-skill'],
    }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(true)
  })

  test('allows passthrough true without derived_by', () => {
    const entry = {
      source: 'org/repo',
      skill: 'skill',
      passthrough: true,
    }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(true)
  })

  test('allows passthrough true with empty derived_by', () => {
    const entry = {
      source: 'org/repo',
      skill: 'skill',
      passthrough: true,
      derived_by: [],
    }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(true)
  })

  test('rejects missing source', () => {
    const entry = { skill: 'beads', passthrough: true }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(false)
  })

  test('rejects missing skill', () => {
    const entry = { source: 'steveyegge/beads', passthrough: true }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(false)
  })

  test('rejects missing passthrough', () => {
    const entry = { source: 'steveyegge/beads', skill: 'beads' }
    const result = v.safeParse(ExternalSkillEntry, entry)
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// ExternalSourcesManifest schema
// ---------------------------------------------------------------------------

describe('ExternalSourcesManifest schema', () => {
  test('accepts manifest with multiple entries', () => {
    const manifest = {
      skills: {
        beads: {
          source: 'steveyegge/beads',
          skill: 'beads',
          passthrough: true,
        },
        'some-upstream': {
          source: 'some-org/repo',
          skill: 'their-skill',
          passthrough: false,
          derived_by: ['my-local-skill'],
        },
      },
    }
    const result = v.safeParse(ExternalSourcesManifest, manifest)
    expect(result.success).toBe(true)
  })

  test('accepts empty skills record', () => {
    const result = v.safeParse(ExternalSourcesManifest, { skills: {} })
    expect(result.success).toBe(true)
  })

  test('rejects missing skills key', () => {
    const result = v.safeParse(ExternalSourcesManifest, {})
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// ExternalLockEntry schema
// ---------------------------------------------------------------------------

describe('ExternalLockEntry schema', () => {
  test('accepts full lock entry', () => {
    const entry = {
      upstream_commit: '5045496bbe4b42d1',
      snapshot_hash: 'sha256:16b0efc72b43',
      last_synced: '2026-03-18T12:00:00Z',
      last_reviewed_commit: 'abc1234',
      drift_issue: 42,
    }
    const result = v.safeParse(ExternalLockEntry, entry)
    expect(result.success).toBe(true)
  })

  test('accepts minimal lock entry', () => {
    const entry = {
      upstream_commit: 'abc123',
      snapshot_hash: 'sha256:def456',
      last_synced: '2026-03-18T12:00:00Z',
    }
    const result = v.safeParse(ExternalLockEntry, entry)
    expect(result.success).toBe(true)
  })

  test('rejects missing upstream_commit', () => {
    const entry = {
      snapshot_hash: 'sha256:def456',
      last_synced: '2026-03-18T12:00:00Z',
    }
    const result = v.safeParse(ExternalLockEntry, entry)
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// ExternalLockfile schema
// ---------------------------------------------------------------------------

describe('ExternalLockfile schema', () => {
  test('accepts record of lock entries', () => {
    const lockfile = {
      a1b2c3d4e5f6: {
        upstream_commit: 'abc',
        snapshot_hash: 'sha256:def',
        last_synced: '2026-03-18T12:00:00Z',
      },
      f6e5d4c3b2a1: {
        upstream_commit: 'xyz',
        snapshot_hash: 'sha256:123',
        last_synced: '2026-03-15T09:00:00Z',
        drift_issue: 42,
      },
    }
    const result = v.safeParse(ExternalLockfile, lockfile)
    expect(result.success).toBe(true)
  })

  test('accepts empty record', () => {
    const result = v.safeParse(ExternalLockfile, {})
    expect(result.success).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// readManifest
// ---------------------------------------------------------------------------

describe('readManifest', () => {
  beforeEach(() => {
    tempDir = createTempDir()
  })

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true })
  })

  test('reads valid YAML with passthrough entry', () => {
    const yamlContent = `skills:
  beads:
    source: steveyegge/beads
    skill: beads
    passthrough: true
`
    writeYaml(tempDir, 'sources.yaml', yamlContent)

    const result = readManifest(tempDir)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.skills.beads).toBeDefined()
      expect(result.value.skills.beads!.passthrough).toBe(true)
      expect(result.value.skills.beads!.source).toBe('steveyegge/beads')
    }
  })

  test('reads valid YAML with derived entry', () => {
    const yamlContent = `skills:
  some-upstream:
    source: some-org/repo
    skill: their-skill
    passthrough: false
    derived_by:
      - my-local-skill
`
    writeYaml(tempDir, 'sources.yaml', yamlContent)

    const result = readManifest(tempDir)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.skills['some-upstream']!.passthrough).toBe(false)
      expect(result.value.skills['some-upstream']!.derived_by).toEqual(['my-local-skill'])
    }
  })

  test('fails validation when passthrough + derived_by together', () => {
    const yamlContent = `skills:
  broken:
    source: org/repo
    skill: skill
    passthrough: true
    derived_by:
      - local-skill
`
    writeYaml(tempDir, 'sources.yaml', yamlContent)

    const result = readManifest(tempDir)
    expect(result.ok).toBe(false)
  })

  test('returns error for missing file', () => {
    const result = readManifest(join(tempDir, 'nonexistent'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_MANIFEST_NOT_FOUND')
    }
  })

  test('returns error for invalid YAML', () => {
    writeYaml(tempDir, 'sources.yaml', '!!!invalid yaml{{{')

    const result = readManifest(tempDir)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_INVALID_YAML')
    }
  })

  test('reads entry with ref field', () => {
    const yamlContent = `skills:
  pinned:
    source: old-org/archived-repo
    skill: legacy-skill
    ref: v2.1.0
    passthrough: false
    derived_by:
      - my-modern-skill
`
    writeYaml(tempDir, 'sources.yaml', yamlContent)

    const result = readManifest(tempDir)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.skills.pinned!.ref).toBe('v2.1.0')
    }
  })
})

// ---------------------------------------------------------------------------
// readLock / writeLock
// ---------------------------------------------------------------------------

describe('readLock / writeLock', () => {
  beforeEach(() => {
    tempDir = createTempDir()
  })

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true })
  })

  test('returns empty object when file does not exist', () => {
    const lock = readLock(tempDir)
    expect(lock).toEqual({})
  })

  test('round-trip: write then read produces same data', () => {
    const data: Record<string, ExternalLockEntry> = {
      a1b2c3d4e5f6: {
        upstream_commit: '5045496bbe4b42d1',
        snapshot_hash: 'sha256:16b0efc72b43',
        last_synced: '2026-03-18T12:00:00Z',
      },
      f6e5d4c3b2a1: {
        upstream_commit: 'd0bd0a7e0d725661',
        snapshot_hash: 'sha256:def456789',
        last_synced: '2026-03-15T09:00:00Z',
        drift_issue: 42,
      },
    }

    writeLock(tempDir, data)
    const readBack = readLock(tempDir)

    expect(readBack).toEqual(data)
  })

  test('writes JSON with 2-space indent and trailing newline', () => {
    const data = {
      abc123def456: {
        upstream_commit: 'sha1',
        snapshot_hash: 'sha256:hash',
        last_synced: '2026-03-18T12:00:00Z',
      },
    }

    writeLock(tempDir, data)

    const raw = readFileSync(join(tempDir, 'sources.lock.json'), 'utf-8')

    // Verify trailing newline
    expect(raw.endsWith('\n')).toBe(true)

    // Verify 2-space indentation (check for "  " at start of a line)
    expect(raw).toContain('  "abc123def456"')

    // Verify it is valid JSON
    expect(() => JSON.parse(raw)).not.toThrow()
  })

  test('overwrites existing lock file', () => {
    const data1 = {
      key1: {
        upstream_commit: 'a',
        snapshot_hash: 'sha256:b',
        last_synced: '2026-01-01T00:00:00Z',
      },
    }
    const data2 = {
      key2: {
        upstream_commit: 'c',
        snapshot_hash: 'sha256:d',
        last_synced: '2026-02-01T00:00:00Z',
      },
    }

    writeLock(tempDir, data1)
    writeLock(tempDir, data2)

    const readBack = readLock(tempDir)
    expect(readBack).toEqual(data2)
    expect(readBack.key1).toBeUndefined()
  })

  test('creates directory if it does not exist', () => {
    const nestedDir = join(tempDir, 'nested', 'deep')
    const data = {
      key1: {
        upstream_commit: 'a',
        snapshot_hash: 'sha256:b',
        last_synced: '2026-01-01T00:00:00Z',
      },
    }

    writeLock(nestedDir, data)
    expect(existsSync(join(nestedDir, 'sources.lock.json'))).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// refreshLinks
// ---------------------------------------------------------------------------

describe('refreshLinks', () => {
  beforeEach(() => {
    tempDir = createTempDir()
  })

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true })
  })

  test('creates symlinks for passthrough entries', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    // Create manifest
    const yamlContent = `skills:
  beads:
    source: steveyegge/beads
    skill: beads
    passthrough: true
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)

    // Create snapshot directory
    createSkillSnapshot(externalDir, 'steveyegge/beads', 'beads')

    const result = await refreshLinks(externalDir, skillsDir)

    expect(result.created).toContain('beads')
    expect(result.broken.length).toBe(0)

    // Verify symlink exists
    const linkPath = join(skillsDir, 'beads')
    expect(existsSync(linkPath)).toBe(true)
    const stats = lstatSync(linkPath)
    expect(stats.isSymbolicLink()).toBe(true)
  })

  test('skips non-passthrough entries', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  derived-skill:
    source: org/repo
    skill: their-skill
    passthrough: false
    derived_by:
      - my-skill
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'org/repo', 'their-skill')

    const result = await refreshLinks(externalDir, skillsDir)

    expect(result.skipped).toContain('derived-skill')
    expect(result.created.length).toBe(0)
  })

  test('reports broken when snapshot directory does not exist', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  missing:
    source: org/repo
    skill: nonexistent
    passthrough: true
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    // Do NOT create the snapshot directory

    const result = await refreshLinks(externalDir, skillsDir)

    expect(result.broken).toContain('missing')
    expect(result.created.length).toBe(0)
  })

  test('updates symlink when target changes', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    // Create initial symlink pointing to wrong target
    const wrongTarget = join(externalDir, 'wrong', 'target')
    mkdirSync(wrongTarget, { recursive: true })
    const linkPath = join(skillsDir, 'beads')
    const { symlink } = await import('node:fs/promises')
    await symlink('wrong/target', linkPath)

    // Create correct manifest and snapshot
    const yamlContent = `skills:
  beads:
    source: steveyegge/beads
    skill: beads
    passthrough: true
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'steveyegge/beads', 'beads')

    const result = await refreshLinks(externalDir, skillsDir)

    // Should have been updated (not created, since symlink already existed)
    expect(result.updated.length + result.created.length).toBeGreaterThan(0)
  })

  test('returns empty results when no external skills configured', async () => {
    const externalDir = join(tempDir, '.external')

    const result = await refreshLinks(externalDir, tempDir)

    expect(result.created).toEqual([])
    expect(result.updated).toEqual([])
    expect(result.skipped).toEqual([])
    expect(result.broken).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// getStatus
// ---------------------------------------------------------------------------

describe('getStatus', () => {
  beforeEach(() => {
    tempDir = createTempDir()
  })

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true })
  })

  test('returns correct mode for passthrough entries', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  beads:
    source: steveyegge/beads
    skill: beads
    passthrough: true
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'steveyegge/beads', 'beads')

    const results = await getStatus(externalDir, skillsDir)

    expect(results.length).toBe(1)
    expect(results[0]!.mode).toBe('passthrough')
    expect(results[0]!.skill).toBe('beads')
  })

  test('returns correct mode for derived entries', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  upstream:
    source: org/repo
    skill: their-skill
    passthrough: false
    derived_by:
      - my-skill
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'org/repo', 'their-skill')

    const results = await getStatus(externalDir, skillsDir)

    expect(results.length).toBe(1)
    expect(results[0]!.mode).toBe('derived')
  })

  test('shows em-dash for symlink on derived entries', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  upstream:
    source: org/repo
    skill: their-skill
    passthrough: false
    derived_by:
      - my-skill
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'org/repo', 'their-skill')

    const results = await getStatus(externalDir, skillsDir)

    expect(results[0]!.symlink).toBe('\u2014')
  })

  test('shows symlink health for passthrough entries with existing symlink', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  beads:
    source: steveyegge/beads
    skill: beads
    passthrough: true
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'steveyegge/beads', 'beads')

    // Create the symlink
    await refreshLinks(externalDir, skillsDir)

    const results = await getStatus(externalDir, skillsDir)

    expect(results[0]!.symlink).toBe('healthy')
  })

  test('shows broken for passthrough without symlink', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  beads:
    source: steveyegge/beads
    skill: beads
    passthrough: true
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'steveyegge/beads', 'beads')
    // Do NOT create symlink

    const results = await getStatus(externalDir, skillsDir)

    expect(results[0]!.symlink).toBe('broken')
  })

  test('shows issue info from lock file', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  upstream:
    source: org/repo
    skill: their-skill
    passthrough: false
    derived_by:
      - my-skill
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'org/repo', 'their-skill')

    // Write lock with drift_issue
    const key = lockKey('org/repo', 'their-skill')
    const lockData: Record<string, ExternalLockEntry> = {
      [key]: {
        upstream_commit: 'abc123',
        snapshot_hash: 'sha256:def456',
        last_synced: '2026-03-18T12:00:00Z',
        drift_issue: 42,
      },
    }
    writeLock(externalDir, lockData)

    const results = await getStatus(externalDir, skillsDir)

    expect(results[0]!.issue).toBe('#42 open')
  })

  test('shows em-dash when no issue exists', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  beads:
    source: steveyegge/beads
    skill: beads
    passthrough: true
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'steveyegge/beads', 'beads')

    const results = await getStatus(externalDir, skillsDir)

    expect(results[0]!.issue).toBe('\u2014')
  })

  test('returns empty array when manifest does not exist', async () => {
    const results = await getStatus(join(tempDir, 'nonexistent'), tempDir)
    expect(results).toEqual([])
  })

  test('includes hash for skills with snapshots', async () => {
    const externalDir = join(tempDir, '.external')
    const skillsDir = tempDir

    const yamlContent = `skills:
  beads:
    source: steveyegge/beads
    skill: beads
    passthrough: true
`
    writeYaml(externalDir, 'sources.yaml', yamlContent)
    createSkillSnapshot(externalDir, 'steveyegge/beads', 'beads')

    const results = await getStatus(externalDir, skillsDir)

    expect(results[0]!.hash).toBeDefined()
    expect(results[0]!.hash).toMatch(/^[a-f0-9]{8}\.\.$/)
  })
})
