import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import {
  type DiscoveredSkill,
  discoverSkills,
  filterSkills,
} from '@agents/sdk/context/skill/discovery'

// Worktree root for integration tests
const WORKTREE = resolve(import.meta.dir, '../../..')

// Temp directory created fresh before each test
let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'skill-discovery-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

async function createSkill(dir: string, name: string, description = 'Test skill'): Promise<void> {
  await mkdir(dir, { recursive: true })
  await writeFile(
    join(dir, 'SKILL.md'),
    `---\nname: ${name}\ndescription: ${description}\n---\n\n# ${name}\n`
  )
}

// ---------------------------------------------------------------------------
// discoverSkills -- happy paths
// ---------------------------------------------------------------------------

describe('discoverSkills', () => {
  test('discovers skills in content/skills/ directory', async () => {
    await createSkill(join(tmp, 'content/skills/my-skill'), 'my-skill', 'First test skill')
    await createSkill(join(tmp, 'content/skills/other'), 'other', 'Second test skill')

    const result = await discoverSkills(tmp)
    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(2)

    const names = result.value.map((s) => s.name).sort()
    expect(names).toEqual(['my-skill', 'other'])

    // Verify relative paths are computed from basePath
    for (const skill of result.value) {
      expect(skill.relativePath).toStartWith('content/skills/')
      expect(skill.path).toStartWith(tmp)
      expect(skill.frontmatter.name).toBe(skill.name)
    }
  })

  // ---------------------------------------------------------------------------
  // Edge cases
  // ---------------------------------------------------------------------------

  test('respects maxDepth and does not find deeply nested skills', async () => {
    // Create a skill at depth 8 (a/b/c/d/e/f/g/h/SKILL.md)
    const deepDir = join(tmp, 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
    await createSkill(deepDir, 'deep-skill')

    const result = await discoverSkills(tmp, undefined, { maxDepth: 3 })
    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(0)
  })

  test('returns ok with empty array when no skills found', async () => {
    // tmp is empty
    const result = await discoverSkills(tmp)
    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(0)
  })

  test('returns error for nonexistent path', async () => {
    const result = await discoverSkills(join(tmp, 'does-not-exist'))
    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_DISCOVERY_PATH')
    expect(result.error.hint).toBeDefined()
  })

  test('restricts search to subpath', async () => {
    await createSkill(join(tmp, 'skills', 'a'), 'skill-a')
    await createSkill(join(tmp, 'other', 'b'), 'skill-b')

    const result = await discoverSkills(tmp, 'skills')
    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]!.name).toBe('skill-a')
    // Relative path is still from basePath (tmp), not from subpath
    expect(result.value[0]!.relativePath).toStartWith('skills/')
  })

  test('skips SKILL.md files with invalid frontmatter', async () => {
    // One valid skill
    await createSkill(join(tmp, 'content/skills/good'), 'good-skill')

    // One SKILL.md without any frontmatter
    const badDir = join(tmp, 'content/skills/bad')
    await mkdir(badDir, { recursive: true })
    await writeFile(join(badDir, 'SKILL.md'), '# No Frontmatter\n\nJust content.\n')

    const result = await discoverSkills(tmp)
    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]!.name).toBe('good-skill')
  })

  test('uses fallback scan when no priority dirs exist', async () => {
    // Put skills in a non-standard directory structure
    await createSkill(join(tmp, 'custom', 'alpha'), 'alpha')
    await createSkill(join(tmp, 'custom', 'beta'), 'beta')

    const result = await discoverSkills(tmp)
    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(2)
    const names = result.value.map((s) => s.name).sort()
    expect(names).toEqual(['alpha', 'beta'])
  })

  test('skips hidden directories', async () => {
    await createSkill(join(tmp, '.hidden', 'secret'), 'secret-skill')
    await createSkill(join(tmp, 'visible'), 'visible-skill')

    const result = await discoverSkills(tmp)
    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(1)
    expect(result.value[0]!.name).toBe('visible-skill')
  })
})

// ---------------------------------------------------------------------------
// filterSkills
// ---------------------------------------------------------------------------

describe('filterSkills', () => {
  // Build a minimal set of mock skills for filter tests
  function mockSkill(name: string): DiscoveredSkill {
    return {
      path: `/fake/${name}/SKILL.md`,
      relativePath: `${name}/SKILL.md`,
      frontmatter: { name, description: `${name} skill` },
      name,
    }
  }

  test('filters by name case-insensitively', () => {
    const skills = [mockSkill('Beads'), mockSkill('gitlab-cicd'), mockSkill('pnpm')]

    const filtered = filterSkills(skills, ['beads', 'PNPM'])
    expect(filtered).toHaveLength(2)

    const names = filtered.map((s) => s.name).sort()
    expect(names).toEqual(['Beads', 'pnpm'])
  })

  test('returns empty when no names match', () => {
    const skills = [mockSkill('alpha'), mockSkill('beta')]
    const filtered = filterSkills(skills, ['gamma', 'delta'])
    expect(filtered).toHaveLength(0)
  })

  test('returns empty for empty skills array', () => {
    const filtered = filterSkills([], ['anything'])
    expect(filtered).toHaveLength(0)
  })

  test('returns empty for empty names array', () => {
    const skills = [mockSkill('alpha')]
    const filtered = filterSkills(skills, [])
    expect(filtered).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// Integration: real project structure
// ---------------------------------------------------------------------------

describe('integration', () => {
  test('discovers skills in actual worktree', async () => {
    const result = await discoverSkills(WORKTREE)
    expect(result.ok).toBe(true)
    if (!result.ok) return

    // Should find a non-trivial number of skills
    expect(result.value.length).toBeGreaterThan(2)

    // Verify known skills are present
    const names = result.value.map((s) => s.name)
    expect(names).toContain('beads')
    expect(names).toContain('gitlab-cicd')

    // Every discovered skill should have valid structure
    for (const skill of result.value) {
      expect(skill.path).toBeTruthy()
      expect(skill.relativePath).toBeTruthy()
      expect(skill.name).toBeTruthy()
      expect(skill.frontmatter.name).toBe(skill.name)
      expect(skill.frontmatter.description).toBeTruthy()
    }
  })
})
