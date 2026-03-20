import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, symlink, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { listSkills } from '../lib/skill-list'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'skill-list-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

async function createSkill(
  baseDir: string,
  name: string,
  opts: { description?: string; version?: string; tags?: string[] } = {}
): Promise<void> {
  const skillDir = join(baseDir, 'context', 'skills', name)
  await mkdir(skillDir, { recursive: true })

  const description = opts.description ?? `${name} skill`
  const version = opts.version ?? '0.1.0'
  const tags = opts.tags ?? []

  await writeFile(
    join(skillDir, 'SKILL.md'),
    `---\nname: ${name}\ndescription: ${description}\nversion: ${version}\ntags: [${tags.join(', ')}]\n---\n\n# ${name}\n`
  )
}

async function createAgentSkillLink(
  projectDir: string,
  agentDir: string,
  skillName: string
): Promise<void> {
  const agentSkillPath = join(projectDir, agentDir, skillName)
  const canonicalPath = join(projectDir, 'context', 'skills', skillName)
  await mkdir(join(projectDir, agentDir), { recursive: true })
  await symlink(canonicalPath, agentSkillPath)
}

// ---------------------------------------------------------------------------
// listSkills -- discovers skills
// ---------------------------------------------------------------------------

describe('listSkills -- discovery', () => {
  test('discovers skills in context/skills/', async () => {
    await createSkill(tmp, 'beads', {
      description: 'Issue tracker',
      version: '1.0.0',
      tags: ['tools'],
    })
    await createSkill(tmp, 'gitlab-cicd', {
      description: 'CI/CD pipelines',
    })

    const result = await listSkills({ cwd: tmp })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(2)

    const names = result.skills.map((s) => s.name).sort()
    expect(names).toEqual(['beads', 'gitlab-cicd'])

    // Check metadata is populated
    const beads = result.skills.find((s) => s.name === 'beads')!
    expect(beads.description).toBe('Issue tracker')
    expect(beads.version).toBe('1.0.0')
    expect(beads.path).toBe(join(tmp, 'context', 'skills', 'beads'))
  })

  test('returns empty array for nonexistent skills directory', async () => {
    // tmp has no context/skills/ directory
    const result = await listSkills({ cwd: tmp })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(0)
  })

  test('returns empty array for empty skills directory', async () => {
    await mkdir(join(tmp, 'context', 'skills'), { recursive: true })

    const result = await listSkills({ cwd: tmp })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(0)
  })

  test('skips directories without SKILL.md', async () => {
    // Create a directory that is not a skill
    await mkdir(join(tmp, 'context', 'skills', 'not-a-skill'), { recursive: true })
    await writeFile(join(tmp, 'context', 'skills', 'not-a-skill', 'README.md'), '# Not a skill\n')

    // Create a real skill
    await createSkill(tmp, 'real-skill')

    const result = await listSkills({ cwd: tmp })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(1)
    expect(result.skills[0]!.name).toBe('real-skill')
  })

  test('skips skills with invalid frontmatter', async () => {
    // Create a skill with valid frontmatter
    await createSkill(tmp, 'good-skill')

    // Create a skill with invalid frontmatter (missing required fields)
    const badDir = join(tmp, 'context', 'skills', 'bad-skill')
    await mkdir(badDir, { recursive: true })
    await writeFile(
      join(badDir, 'SKILL.md'),
      `---\nversion: 0.1.0\n---\n\n# Missing name and description\n`
    )

    const result = await listSkills({ cwd: tmp })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(1)
    expect(result.skills[0]!.name).toBe('good-skill')
  })
})

// ---------------------------------------------------------------------------
// listSkills -- agent detection
// ---------------------------------------------------------------------------

describe('listSkills -- agent detection', () => {
  test('detects agents that have the skill installed', async () => {
    await createSkill(tmp, 'multi-agent')

    // Simulate agent installations with symlinks
    await createAgentSkillLink(tmp, '.claude/skills', 'multi-agent')
    await createAgentSkillLink(tmp, '.agents/skills', 'multi-agent') // cursor

    const result = await listSkills({ cwd: tmp })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(1)
    expect(result.skills[0]!.agents.length).toBeGreaterThanOrEqual(1)
    expect(result.skills[0]!.agents).toContain('claude-code')
  })

  test('returns empty agents array when no agent has the skill', async () => {
    await createSkill(tmp, 'orphan-skill')

    const result = await listSkills({ cwd: tmp })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(1)
    expect(result.skills[0]!.agents).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// listSkills -- filters
// ---------------------------------------------------------------------------

describe('listSkills -- filters', () => {
  test('filters by agent name', async () => {
    await createSkill(tmp, 'claude-only')
    await createSkill(tmp, 'no-agent')

    // Only create a claude-code link for claude-only
    await createAgentSkillLink(tmp, '.claude/skills', 'claude-only')

    const result = await listSkills({ cwd: tmp, agent: 'claude-code' })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(1)
    expect(result.skills[0]!.name).toBe('claude-only')
  })

  test('filters by skill name (case-insensitive)', async () => {
    await createSkill(tmp, 'target-skill')
    await createSkill(tmp, 'other-skill')

    const result = await listSkills({ cwd: tmp, skill: 'Target-Skill' })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(1)
    expect(result.skills[0]!.name).toBe('target-skill')
  })

  test('combines agent and skill filters', async () => {
    await createSkill(tmp, 'both-match')
    await createSkill(tmp, 'wrong-name')
    await createSkill(tmp, 'no-agent-match')

    await createAgentSkillLink(tmp, '.claude/skills', 'both-match')
    await createAgentSkillLink(tmp, '.claude/skills', 'wrong-name')

    const result = await listSkills({
      cwd: tmp,
      agent: 'claude-code',
      skill: 'both-match',
    })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(1)
    expect(result.skills[0]!.name).toBe('both-match')
  })

  test('returns empty when agent filter matches no skills', async () => {
    await createSkill(tmp, 'some-skill')

    const result = await listSkills({ cwd: tmp, agent: 'zed' })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// listSkills -- custom skillsDir
// ---------------------------------------------------------------------------

describe('listSkills -- custom skillsDir', () => {
  test('accepts a custom skills directory path', async () => {
    const customDir = join(tmp, 'my-skills')
    await mkdir(customDir, { recursive: true })

    // Create a skill in the custom directory
    const skillDir = join(customDir, 'custom-located')
    await mkdir(skillDir, { recursive: true })
    await writeFile(
      join(skillDir, 'SKILL.md'),
      `---\nname: custom-located\ndescription: Custom dir test\n---\n\n# custom-located\n`
    )

    const result = await listSkills({ cwd: tmp, skillsDir: customDir })

    expect(result.ok).toBe(true)
    expect(result.skills).toHaveLength(1)
    expect(result.skills[0]!.name).toBe('custom-located')
  })
})
