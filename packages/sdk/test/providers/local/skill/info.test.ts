import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { skillInfo as _skillInfo, InfoError } from '@agents/sdk/providers/local/skill/info'
import { createMockResolver } from '../../../_utils/mock-resolver'

/** Convenience wrapper — auto-injects a mock agent resolver. */
const skillInfo = (name: string, opts?: Parameters<typeof _skillInfo>[2]) =>
  _skillInfo(createMockResolver(), name, opts)

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'skill-info-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// skillInfo -- full metadata
// ---------------------------------------------------------------------------

describe('skillInfo', () => {
  test('returns full metadata for installed skill', async () => {
    const skillDir = join(tmp, 'content', 'skills', 'beads')
    await mkdir(skillDir, { recursive: true })
    await writeFile(
      join(skillDir, 'SKILL.md'),
      '---\nname: beads\ndescription: Issue tracker\n---\n# Beads'
    )
    await writeFile(
      join(tmp, 'skills-lock.json'),
      JSON.stringify({
        version: 1,
        skills: {
          beads: {
            source: 'steveyegge/beads',
            sourceType: 'github',
            computedHash: 'a'.repeat(64),
          },
        },
      })
    )

    const result = await skillInfo('beads', { cwd: tmp })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('beads')
      expect(result.value.frontmatter?.name).toBe('beads')
      expect(result.value.frontmatter?.description).toBe('Issue tracker')
      expect(result.value.source).toBe('steveyegge/beads')
      expect(result.value.sourceType).toBe('github')
      expect(result.value.symlinkStatus).toBe('copy')
    }
  })

  test('returns error for nonexistent skill', async () => {
    const result = await skillInfo('nonexistent', { cwd: tmp })
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_SKILL_NOT_FOUND')
      expect(result.error.message).toContain('nonexistent')
    }
  })

  test('handles missing lock file gracefully', async () => {
    const skillDir = join(tmp, 'content', 'skills', 'no-lock')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: no-lock\ndescription: Test\n---\n')

    const result = await skillInfo('no-lock', { cwd: tmp })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.source).toBeNull()
      expect(result.value.sourceType).toBeNull()
      expect(result.value.lockHash).toBeNull()
      expect(result.value.hashMatch).toBe(false)
    }
  })

  test('detects hash mismatch', async () => {
    const skillDir = join(tmp, 'content', 'skills', 'drifted')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: drifted\ndescription: Changed\n---\n')
    await writeFile(
      join(tmp, 'skills-lock.json'),
      JSON.stringify({
        version: 1,
        skills: {
          drifted: {
            source: 'local',
            sourceType: 'local',
            computedHash: 'b'.repeat(64),
          },
        },
      })
    )

    const result = await skillInfo('drifted', { cwd: tmp })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.hashMatch).toBe(false)
      expect(result.value.computedHash).not.toBeNull()
      expect(result.value.lockHash).toBe('b'.repeat(64))
    }
  })

  test('handles missing frontmatter', async () => {
    const skillDir = join(tmp, 'content', 'skills', 'bad-fm')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '# No frontmatter here')

    const result = await skillInfo('bad-fm', { cwd: tmp })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.frontmatter).toBeNull()
    }
  })

  test('handles missing SKILL.md file', async () => {
    const skillDir = join(tmp, 'content', 'skills', 'no-skillmd')
    await mkdir(skillDir, { recursive: true })
    // Directory exists but no SKILL.md inside

    const result = await skillInfo('no-skillmd', { cwd: tmp })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.frontmatter).toBeNull()
      expect(result.value.name).toBe('no-skillmd')
    }
  })

  test('JSON-serializable output', async () => {
    const skillDir = join(tmp, 'content', 'skills', 'json-test')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: json-test\ndescription: Test\n---\n')

    const result = await skillInfo('json-test', { cwd: tmp })
    expect(result.ok).toBe(true)
    if (result.ok) {
      const serialized = JSON.stringify(result.value)
      const parsed = JSON.parse(serialized)
      expect(parsed.name).toBe('json-test')
      expect(parsed.path).toBe(result.value.path)
      expect(parsed.symlinkStatus).toBe('copy')
    }
  })

  test('computes live hash for skill directory', async () => {
    const skillDir = join(tmp, 'content', 'skills', 'hashed')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: hashed\ndescription: Hash test\n---\n')

    const result = await skillInfo('hashed', { cwd: tmp })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.computedHash).not.toBeNull()
      expect(result.value.computedHash).toHaveLength(64)
      // Hex digest: only 0-9a-f
      expect(result.value.computedHash).toMatch(/^[a-f0-9]{64}$/)
    }
  })

  test('hashMatch is true when hashes agree', async () => {
    // First create the skill and get its hash
    const skillDir = join(tmp, 'content', 'skills', 'matched')
    await mkdir(skillDir, { recursive: true })
    await writeFile(
      join(skillDir, 'SKILL.md'),
      '---\nname: matched\ndescription: Matching hashes\n---\n'
    )

    // Compute the actual hash first
    const { hashDirectory } = await import('@agents/core/hash')
    const actualHash = await hashDirectory(skillDir)

    // Write a lockfile with the matching hash
    await writeFile(
      join(tmp, 'skills-lock.json'),
      JSON.stringify({
        version: 1,
        skills: {
          matched: {
            source: 'local',
            sourceType: 'local',
            computedHash: actualHash,
          },
        },
      })
    )

    const result = await skillInfo('matched', { cwd: tmp })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.hashMatch).toBe(true)
      expect(result.value.computedHash).toBe(actualHash)
      expect(result.value.lockHash).toBe(actualHash)
    }
  })

  test('skill with no lock entry for that name', async () => {
    // Lock file exists but does not have the skill we are querying
    const skillDir = join(tmp, 'content', 'skills', 'unlisted')
    await mkdir(skillDir, { recursive: true })
    await writeFile(
      join(skillDir, 'SKILL.md'),
      '---\nname: unlisted\ndescription: Not in lock\n---\n'
    )
    await writeFile(
      join(tmp, 'skills-lock.json'),
      JSON.stringify({
        version: 1,
        skills: {
          'other-skill': {
            source: 'example/other',
            sourceType: 'github',
            computedHash: 'c'.repeat(64),
          },
        },
      })
    )

    const result = await skillInfo('unlisted', { cwd: tmp })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.source).toBeNull()
      expect(result.value.lockHash).toBeNull()
      expect(result.value.hashMatch).toBe(false)
    }
  })
})

// ---------------------------------------------------------------------------
// InfoError
// ---------------------------------------------------------------------------

describe('InfoError', () => {
  test('has correct code and message', () => {
    const e = new InfoError('not found', 'E_SKILL_NOT_FOUND')
    expect(e.code).toBe('E_SKILL_NOT_FOUND')
    expect(e.message).toBe('not found')
  })

  test('accepts optional hint and cause', () => {
    const cause = new Error('underlying')
    const e = new InfoError('bad lock', 'E_LOCK_READ_FAILED', 'check the file', cause)
    expect(e.hint).toBe('check the file')
    expect(e.cause).toBe(cause)
  })

  test('display() formats code and message', () => {
    const e = new InfoError('mismatch', 'E_DISK_MISMATCH', 'run sync')
    expect(e.display()).toBe('error[E_DISK_MISMATCH]: mismatch\n  hint: run sync')
  })

  test('display() without hint omits hint line', () => {
    const e = new InfoError('invalid', 'E_FRONTMATTER_INVALID')
    expect(e.display()).toBe('error[E_FRONTMATTER_INVALID]: invalid')
  })
})
