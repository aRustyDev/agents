import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdir, mkdtemp, readFile, rm, symlink, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { RemoveError, removeSkills } from '../lib/skill-remove'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'skill-remove-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

/**
 * Create a canonical skill directory with a minimal SKILL.md.
 */
async function createCanonicalSkill(cwd: string, name: string): Promise<string> {
  const dir = join(cwd, 'content', 'skills', name)
  await mkdir(dir, { recursive: true })
  await writeFile(
    join(dir, 'SKILL.md'),
    `---\nname: ${name}\ndescription: Test skill\nversion: 0.1.0\ntags: []\n---\n\n# ${name}\n`
  )
  return dir
}

/**
 * Create a lockfile with entries for the given skills.
 */
async function createLockfile(
  cwd: string,
  skills: Record<string, { source: string; sourceType: string; computedHash: string }>
): Promise<string> {
  const lockPath = join(cwd, 'skills-lock.json')
  await writeFile(lockPath, JSON.stringify({ version: 1, skills }, null, 2) + '\n')
  return lockPath
}

/**
 * Create an agent skills directory and symlink a skill into it.
 *
 * Uses `claude-code` agent by default, whose project-level skillsDir
 * is `.claude/skills`.
 */
async function createAgentLink(
  cwd: string,
  skillName: string,
  agentSkillsDir = '.claude/skills'
): Promise<string> {
  const agentDir = join(cwd, agentSkillsDir)
  await mkdir(agentDir, { recursive: true })
  const canonicalDir = join(cwd, 'content', 'skills', skillName)
  const linkPath = join(agentDir, skillName)
  await symlink(canonicalDir, linkPath)
  return linkPath
}

// ---------------------------------------------------------------------------
// removeSkills -- canonical removal
// ---------------------------------------------------------------------------

describe('removeSkills -- canonical removal', () => {
  test('removes canonical directory when no agent filter is specified', async () => {
    const canonical = await createCanonicalSkill(tmp, 'test-skill')
    await createLockfile(tmp, {
      'test-skill': {
        source: 'local',
        sourceType: 'local',
        computedHash: 'a'.repeat(64),
      },
    })

    const results = await removeSkills(['test-skill'], { cwd: tmp, yes: true })

    expect(results).toHaveLength(1)
    expect(results[0]!.skill).toBe('test-skill')
    expect(results[0]!.canonicalRemoved).toBe(true)
    expect(results[0]!.error).toBeUndefined()
    expect(existsSync(canonical)).toBe(false)
  })

  test('removes multiple skills in a single call', async () => {
    await createCanonicalSkill(tmp, 'alpha')
    await createCanonicalSkill(tmp, 'beta')
    await createLockfile(tmp, {
      alpha: { source: 'x', sourceType: 'local', computedHash: 'a'.repeat(64) },
      beta: { source: 'y', sourceType: 'local', computedHash: 'b'.repeat(64) },
    })

    const results = await removeSkills(['alpha', 'beta'], { cwd: tmp, yes: true })

    expect(results).toHaveLength(2)
    expect(results[0]!.canonicalRemoved).toBe(true)
    expect(results[1]!.canonicalRemoved).toBe(true)
    expect(existsSync(join(tmp, 'content', 'skills', 'alpha'))).toBe(false)
    expect(existsSync(join(tmp, 'content', 'skills', 'beta'))).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// removeSkills -- not found
// ---------------------------------------------------------------------------

describe('removeSkills -- not found', () => {
  test('handles skill not found gracefully', async () => {
    await createLockfile(tmp, {})

    const results = await removeSkills(['nonexistent'], { cwd: tmp, yes: true })

    expect(results).toHaveLength(1)
    expect(results[0]!.removedFrom).toEqual([])
    expect(results[0]!.canonicalRemoved).toBe(false)
    expect(results[0]!.error).toContain('not found')
  })

  test('returns error for one missing and succeeds for one present', async () => {
    await createCanonicalSkill(tmp, 'exists')
    await createLockfile(tmp, {
      exists: { source: 'x', sourceType: 'local', computedHash: 'e'.repeat(64) },
    })

    const results = await removeSkills(['exists', 'missing'], { cwd: tmp, yes: true })

    expect(results).toHaveLength(2)
    expect(results[0]!.skill).toBe('exists')
    expect(results[0]!.canonicalRemoved).toBe(true)
    expect(results[0]!.error).toBeUndefined()
    expect(results[1]!.skill).toBe('missing')
    expect(results[1]!.error).toContain('not found')
  })
})

// ---------------------------------------------------------------------------
// removeSkills -- agent symlinks
// ---------------------------------------------------------------------------

describe('removeSkills -- agent symlinks', () => {
  test('removes agent symlink and canonical directory', async () => {
    const canonical = await createCanonicalSkill(tmp, 'linked-skill')
    const linkPath = await createAgentLink(tmp, 'linked-skill')

    await createLockfile(tmp, {
      'linked-skill': {
        source: 'local',
        sourceType: 'local',
        computedHash: 'b'.repeat(64),
      },
    })

    const results = await removeSkills(['linked-skill'], { cwd: tmp, yes: true })

    expect(results).toHaveLength(1)
    expect(results[0]!.canonicalRemoved).toBe(true)
    expect(existsSync(linkPath)).toBe(false)
    expect(existsSync(canonical)).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// removeSkills -- lockfile updates
// ---------------------------------------------------------------------------

describe('removeSkills -- lockfile updates', () => {
  test('removes the entry from the lockfile', async () => {
    await createCanonicalSkill(tmp, 'locked-skill')
    const lockPath = await createLockfile(tmp, {
      'locked-skill': {
        source: 'x',
        sourceType: 'local',
        computedHash: 'c'.repeat(64),
      },
      'other-skill': {
        source: 'y',
        sourceType: 'local',
        computedHash: 'd'.repeat(64),
      },
    })

    await removeSkills(['locked-skill'], { cwd: tmp, yes: true })

    const lockRaw = await readFile(lockPath, 'utf-8')
    const lock = JSON.parse(lockRaw)
    expect(lock.skills).not.toHaveProperty('locked-skill')
    expect(lock.skills).toHaveProperty('other-skill')
  })

  test('does not rewrite lockfile when nothing was removed from it', async () => {
    // Skill exists on disk but not in lockfile
    await createCanonicalSkill(tmp, 'unlocked')
    const lockPath = await createLockfile(tmp, {})
    const originalContent = await readFile(lockPath, 'utf-8')

    await removeSkills(['unlocked'], { cwd: tmp, yes: true })

    // lockUpdated should be false because there was no entry to remove
    const afterContent = await readFile(lockPath, 'utf-8')
    expect(afterContent).toBe(originalContent)
  })
})

// ---------------------------------------------------------------------------
// removeSkills -- missing lockfile
// ---------------------------------------------------------------------------

describe('removeSkills -- missing lockfile', () => {
  test('handles missing lockfile gracefully', async () => {
    await createCanonicalSkill(tmp, 'no-lock')

    const results = await removeSkills(['no-lock'], { cwd: tmp, yes: true })

    expect(results).toHaveLength(1)
    expect(results[0]!.canonicalRemoved).toBe(true)
    expect(results[0]!.lockUpdated).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// RemoveError
// ---------------------------------------------------------------------------

describe('RemoveError', () => {
  test('has correct code property', () => {
    const e = new RemoveError('not found', 'E_SKILL_NOT_FOUND')
    expect(e.code).toBe('E_SKILL_NOT_FOUND')
    expect(e.message).toBe('not found')
  })

  test('has correct display format', () => {
    const e = new RemoveError('not found', 'E_SKILL_NOT_FOUND', 'check the name')
    expect(e.display()).toContain('E_SKILL_NOT_FOUND')
    expect(e.display()).toContain('not found')
    expect(e.display()).toContain('check the name')
  })

  test('accepts all error codes', () => {
    const codes = [
      'E_SKILL_NOT_FOUND',
      'E_LOCK_UPDATE_FAILED',
      'E_FS_REMOVE_FAILED',
      'E_BROKEN_SYMLINK',
      'E_AGENT_NOT_FOUND',
    ] as const

    for (const code of codes) {
      const e = new RemoveError('test', code)
      expect(e.code).toBe(code)
    }
  })

  test('extends CliError', () => {
    const { CliError } = require('../lib/types')
    const e = new RemoveError('test', 'E_SKILL_NOT_FOUND')
    expect(e).toBeInstanceOf(CliError)
  })
})
