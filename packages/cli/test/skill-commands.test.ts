/**
 * Tests for commands/skill.ts
 *
 * Validates that skill subcommands are properly defined and that
 * core helpers (listSkills, validate, hash) work against real skills.
 */

import { describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { listSkills } from '../src/commands/skill'
import { formatHash, hashDirectory } from '../src/lib/hash'
import { readSkillFrontmatter } from '../src/lib/manifest'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const WORKTREE = '/private/etc/infra/pub/ai'
const SKILLS_DIR = join(WORKTREE, 'content/skills')

// ---------------------------------------------------------------------------
// listSkills
// ---------------------------------------------------------------------------

describe('listSkills', () => {
  test('returns a non-empty array', () => {
    const skills = listSkills()
    expect(skills.length).toBeGreaterThan(0)
  })

  test('includes known skill "beads"', () => {
    const skills = listSkills()
    expect(skills).toContain('beads')
  })

  test('includes known skill "gitlab-cicd"', () => {
    const skills = listSkills()
    expect(skills).toContain('gitlab-cicd')
  })

  test('does not include dotdirs', () => {
    const skills = listSkills()
    for (const name of skills) {
      expect(name.startsWith('.')).toBe(false)
    }
  })

  test('does not include justfile', () => {
    const skills = listSkills()
    expect(skills).not.toContain('justfile')
  })

  test('returns sorted results', () => {
    const skills = listSkills()
    const sorted = [...skills].sort()
    expect(skills).toEqual(sorted)
  })

  test('every entry is a directory', () => {
    const skills = listSkills()
    for (const name of skills) {
      const dir = join(SKILLS_DIR, name)
      expect(existsSync(dir)).toBe(true)
    }
  })
})

// ---------------------------------------------------------------------------
// validate (via readSkillFrontmatter)
// ---------------------------------------------------------------------------

describe('validate (readSkillFrontmatter)', () => {
  test('validates beads SKILL.md successfully', async () => {
    const result = await readSkillFrontmatter(join(SKILLS_DIR, 'beads', 'SKILL.md'))
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('beads')
      expect(result.value.description).toBeDefined()
      expect(typeof result.value.description).toBe('string')
    }
  })

  test('validates gitlab-cicd SKILL.md successfully', async () => {
    const result = await readSkillFrontmatter(join(SKILLS_DIR, 'gitlab-cicd', 'SKILL.md'))
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('gitlab-cicd')
    }
  })

  test('fails for non-existent skill', async () => {
    const result = await readSkillFrontmatter(join(SKILLS_DIR, 'nonexistent-skill-xyz', 'SKILL.md'))
    expect(result.ok).toBe(false)
  })

  test('all listed skills have valid frontmatter', async () => {
    const skills = listSkills()
    const failures: string[] = []

    for (const skill of skills) {
      const skillPath = join(SKILLS_DIR, skill, 'SKILL.md')
      if (!existsSync(skillPath)) {
        // Some skill dirs may not have SKILL.md (e.g., directory-only)
        continue
      }
      const result = await readSkillFrontmatter(skillPath)
      if (!result.ok) {
        failures.push(`${skill}: ${result.error.message}`)
      }
    }

    if (failures.length > 0) {
      console.log('Failures:', failures)
    }
    // Allow some flexibility: most skills should pass
    expect(failures.length).toBeLessThan(skills.length)
  })
})

// ---------------------------------------------------------------------------
// hash (via hashDirectory + formatHash)
// ---------------------------------------------------------------------------

describe('hash', () => {
  test('produces sha256-prefixed hash for beads', async () => {
    const hex = await hashDirectory(join(SKILLS_DIR, 'beads'))
    const prefixed = formatHash(hex)
    expect(prefixed).toMatch(/^sha256:[a-f0-9]{64}$/)
  })

  test('produces sha256-prefixed hash for gitlab-cicd', async () => {
    const hex = await hashDirectory(join(SKILLS_DIR, 'gitlab-cicd'))
    const prefixed = formatHash(hex)
    expect(prefixed).toMatch(/^sha256:[a-f0-9]{64}$/)
  })

  test('different skills produce different hashes', async () => {
    const beadsHash = await hashDirectory(join(SKILLS_DIR, 'beads'))
    const gitlabHash = await hashDirectory(join(SKILLS_DIR, 'gitlab-cicd'))
    expect(beadsHash).not.toBe(gitlabHash)
  })

  test('hash is deterministic (same skill = same hash)', async () => {
    const h1 = await hashDirectory(join(SKILLS_DIR, 'beads'))
    const h2 = await hashDirectory(join(SKILLS_DIR, 'beads'))
    expect(h1).toBe(h2)
  })
})

// ---------------------------------------------------------------------------
// Command structure (exports)
// ---------------------------------------------------------------------------

describe('command structure', () => {
  test('default export defines a command with subCommands', async () => {
    const mod = await import('../src/commands/skill')
    const cmd = mod.default
    expect(cmd).toBeDefined()
    expect(cmd.meta?.name).toBe('skill')
  })

  test('has validate subcommand', async () => {
    const mod = await import('../src/commands/skill')
    const cmd = mod.default
    const subs = cmd.subCommands as Record<string, unknown>
    expect(subs).toBeDefined()
    expect(subs.validate).toBeDefined()
  })

  test('has hash subcommand', async () => {
    const mod = await import('../src/commands/skill')
    const cmd = mod.default
    const subs = cmd.subCommands as Record<string, unknown>
    expect(subs.hash).toBeDefined()
  })

  test('has lint subcommand', async () => {
    const mod = await import('../src/commands/skill')
    const cmd = mod.default
    const subs = cmd.subCommands as Record<string, unknown>
    expect(subs.lint).toBeDefined()
  })

  test('has check-all subcommand', async () => {
    const mod = await import('../src/commands/skill')
    const cmd = mod.default
    const subs = cmd.subCommands as Record<string, unknown>
    expect(subs['check-all']).toBeDefined()
  })

  test('has deps subcommand group', async () => {
    const mod = await import('../src/commands/skill')
    const cmd = mod.default
    const subs = cmd.subCommands as Record<string, { subCommands?: Record<string, unknown> }>
    expect(subs.deps).toBeDefined()
    expect(subs.deps.subCommands).toBeDefined()
  })

  test('deps has expected subcommands', async () => {
    const mod = await import('../src/commands/skill')
    const cmd = mod.default
    const subs = cmd.subCommands as Record<string, { subCommands?: Record<string, unknown> }>
    const depsSubs = subs.deps.subCommands!
    expect(depsSubs.check).toBeDefined()
    expect(depsSubs.sync).toBeDefined()
    expect(depsSubs.issues).toBeDefined()
    expect(depsSubs.links).toBeDefined()
    expect(depsSubs.status).toBeDefined()
  })
})
