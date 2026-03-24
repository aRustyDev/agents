import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { LocalProvider } from '../../lib/component/provider-local'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'provider-local-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Fixture helpers
// ---------------------------------------------------------------------------

async function createSkill(baseDir: string, name: string, desc = 'Test skill'): Promise<void> {
  const skillDir = join(baseDir, 'content', 'skills', name)
  await mkdir(skillDir, { recursive: true })
  await writeFile(
    join(skillDir, 'SKILL.md'),
    `---\nname: ${name}\ndescription: ${desc}\ntags: []\nversion: 0.1.0\n---\n\n# ${name}\n`
  )
}

// ---------------------------------------------------------------------------
// capabilities
// ---------------------------------------------------------------------------

describe('LocalProvider capabilities', () => {
  test('declares skill support for all operations', () => {
    const provider = new LocalProvider(tmp)

    expect(provider.id).toBe('local')
    expect(provider.displayName).toBe('Local Filesystem')
    expect(provider.capabilities.search).toContain('skill')
    expect(provider.capabilities.add).toContain('skill')
    expect(provider.capabilities.list).toContain('skill')
    expect(provider.capabilities.remove).toContain('skill')
    expect(provider.capabilities.info).toContain('skill')
  })

  test('publish is empty (not supported)', () => {
    const provider = new LocalProvider(tmp)
    expect(provider.capabilities.publish).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// search
// ---------------------------------------------------------------------------

describe('LocalProvider search', () => {
  test('finds installed skills by query', async () => {
    await createSkill(tmp, 'beads', 'Issue tracker')
    await createSkill(tmp, 'gitlab-cicd', 'CI/CD pipelines')

    const provider = new LocalProvider(tmp)
    const result = await provider.search({ query: 'beads' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('beads')
    expect(result.value.items[0]?.type).toBe('skill')
  })

  test('returns empty for unsupported type', async () => {
    await createSkill(tmp, 'some-skill')

    const provider = new LocalProvider(tmp)
    const result = await provider.search({ query: 'test', type: 'mcp_server' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
    expect(result.value.hasMore).toBe(false)
    expect(result.value.total).toBe(0)
  })

  test('returns all skills for empty query', async () => {
    await createSkill(tmp, 'alpha')
    await createSkill(tmp, 'beta')
    await createSkill(tmp, 'gamma')

    const provider = new LocalProvider(tmp)
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(3)
    const names = result.value.items.map((c) => c.name).sort()
    expect(names).toEqual(['alpha', 'beta', 'gamma'])
  })

  test('paginates results', async () => {
    await createSkill(tmp, 'alpha')
    await createSkill(tmp, 'beta')
    await createSkill(tmp, 'gamma')

    const provider = new LocalProvider(tmp)
    const result = await provider.search({ query: '', page: 1, limit: 2 })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(2)
    expect(result.value.hasMore).toBe(true)
    expect(result.value.total).toBe(3)
    expect(result.value.page).toBe(1)
    expect(result.value.pageSize).toBe(2)
  })

  test('searches by description', async () => {
    await createSkill(tmp, 'beads', 'Issue tracker for persistent tasks')
    await createSkill(tmp, 'gitlab-cicd', 'CI/CD pipeline management')

    const provider = new LocalProvider(tmp)
    const result = await provider.search({ query: 'pipeline' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('gitlab-cicd')
  })

  test('filters by name parameter', async () => {
    await createSkill(tmp, 'alpha')
    await createSkill(tmp, 'beta')

    const provider = new LocalProvider(tmp)
    const result = await provider.search({ query: '', name: 'alpha' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('alpha')
  })

  test('returns empty page when no skills dir exists', async () => {
    // tmp is empty, no content/skills/
    const provider = new LocalProvider(tmp)
    const result = await provider.search({ query: 'anything' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// list
// ---------------------------------------------------------------------------

describe('LocalProvider list', () => {
  test('returns installed skills', async () => {
    await createSkill(tmp, 'beads', 'Issue tracker')
    await createSkill(tmp, 'pnpm', 'Package manager')

    const provider = new LocalProvider(tmp)
    const result = await provider.list('skill', { cwd: tmp })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(2)
    const names = result.value.map((c) => c.name).sort()
    expect(names).toEqual(['beads', 'pnpm'])

    // Verify component shape
    const beads = result.value.find((c) => c.name === 'beads')!
    expect(beads.type).toBe('skill')
    expect(beads.description).toBe('Issue tracker')
    expect(beads.version).toBe('0.1.0')
    expect(beads.localPath).toBe(join(tmp, 'content', 'skills', 'beads'))
  })

  test('returns empty for unsupported type', async () => {
    await createSkill(tmp, 'some-skill')

    const provider = new LocalProvider(tmp)
    const result = await provider.list('mcp_server')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })

  test('returns empty when no skills exist', async () => {
    const provider = new LocalProvider(tmp)
    const result = await provider.list('skill')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// info
// ---------------------------------------------------------------------------

describe('LocalProvider info', () => {
  test('returns skill detail', async () => {
    await createSkill(tmp, 'beads', 'Issue tracker')

    const provider = new LocalProvider(tmp)
    const result = await provider.info('beads', 'skill', { cwd: tmp })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.type).toBe('skill')
    expect(result.value.name).toBe('beads')
    expect(result.value.description).toBe('Issue tracker')
    expect(result.value.version).toBe('0.1.0')
    expect(result.value.localPath).toBe(join(tmp, 'content', 'skills', 'beads'))
    // Not a symlink, so installMode should be 'copy'
    expect(result.value.installMode).toBe('copy')
  })

  test('returns error for missing skill', async () => {
    const provider = new LocalProvider(tmp)
    const result = await provider.info('nonexistent', 'skill', { cwd: tmp })

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_SKILL_NOT_FOUND')
  })

  test('returns error for unsupported type', async () => {
    const provider = new LocalProvider(tmp)
    const result = await provider.info('something', 'mcp_server', { cwd: tmp })

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_UNSUPPORTED_TYPE')
  })
})

// ---------------------------------------------------------------------------
// remove
// ---------------------------------------------------------------------------

describe('LocalProvider remove', () => {
  test('removes installed skill', async () => {
    await createSkill(tmp, 'to-remove')

    // Verify skill exists before removal
    expect(existsSync(join(tmp, 'content', 'skills', 'to-remove'))).toBe(true)

    const provider = new LocalProvider(tmp)
    const result = await provider.remove('to-remove', 'skill', { cwd: tmp })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.ok).toBe(true)
    expect(result.value.component).toBe('to-remove')

    // Verify skill is gone from canonical location
    expect(existsSync(join(tmp, 'content', 'skills', 'to-remove'))).toBe(false)
  })

  test('returns error message when skill not found', async () => {
    const provider = new LocalProvider(tmp)
    const result = await provider.remove('ghost', 'skill', { cwd: tmp })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    // removeSkills returns a result with an error message, not an exception
    expect(result.value.ok).toBe(false)
    expect(result.value.error).toBeDefined()
  })

  test('returns error for unsupported type', async () => {
    const provider = new LocalProvider(tmp)
    const result = await provider.remove('something', 'mcp_server', {
      cwd: tmp,
    })

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_UNSUPPORTED_TYPE')
  })
})

// ---------------------------------------------------------------------------
// add
// ---------------------------------------------------------------------------

describe('LocalProvider add', () => {
  test('installs from local path', async () => {
    // Create a source directory with a SKILL.md (outside the project tree)
    const sourceDir = join(tmp, 'external-source', 'my-new-skill')
    await mkdir(sourceDir, { recursive: true })
    await writeFile(
      join(sourceDir, 'SKILL.md'),
      '---\nname: my-new-skill\ndescription: A brand new skill\ntags: []\nversion: 1.0.0\n---\n\n# my-new-skill\n'
    )

    const provider = new LocalProvider(tmp)
    const result = await provider.add(sourceDir, {
      cwd: tmp,
      yes: true,
      copy: true,
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.ok).toBe(true)
    expect(result.value.components).toHaveLength(1)
    expect(result.value.components[0]?.name).toBe('my-new-skill')
    expect(result.value.components[0]?.type).toBe('skill')

    // Verify the skill was actually installed to the canonical path
    const canonicalPath = join(tmp, 'content', 'skills', 'my-new-skill')
    expect(existsSync(canonicalPath)).toBe(true)
    expect(existsSync(join(canonicalPath, 'SKILL.md'))).toBe(true)
  })
})
