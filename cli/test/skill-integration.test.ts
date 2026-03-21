/**
 * Integration tests for the skill management lifecycle.
 *
 * Each test creates an isolated temp directory that mimics a real project
 * structure, then exercises multiple modules end-to-end.  No writes are
 * made to real project directories.
 */

import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Create a minimal project layout with a skills-lock.json. */
async function setupProject(dir: string): Promise<void> {
  await mkdir(join(dir, 'context', 'skills'), { recursive: true })
  await writeFile(
    join(dir, 'skills-lock.json'),
    `${JSON.stringify({ version: 1, skills: {} }, null, 2)}\n`
  )
}

/**
 * Create a source directory containing a valid SKILL.md.
 *
 * The source structure matches what `addSkill` expects when passed a local
 * path: the SKILL.md lives directly in the given directory so that the
 * fallback recursive scan in `discoverSkills` can find it.
 */
async function createSourceSkill(
  baseDir: string,
  name: string,
  description = 'Test skill'
): Promise<string> {
  await mkdir(baseDir, { recursive: true })
  await writeFile(
    join(baseDir, 'SKILL.md'),
    [
      '---',
      `name: ${name}`,
      `description: ${description}`,
      'version: 0.1.0',
      'tags: []',
      '---',
      '',
      `# ${name}`,
      '',
      description,
      '',
    ].join('\n')
  )
  return baseDir
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

describe('skill lifecycle integration', () => {
  let tmp: string

  beforeEach(async () => {
    tmp = await mkdtemp(join(tmpdir(), 'skill-integration-'))
    await setupProject(tmp)
  })

  afterEach(async () => {
    await rm(tmp, { recursive: true, force: true })
  })

  // -------------------------------------------------------------------------
  // Test 1: init -> list -> info -> remove lifecycle
  // -------------------------------------------------------------------------

  test('init -> list -> info -> remove lifecycle', async () => {
    const { initSkill } = await import('../lib/skill-init')
    const { listSkills } = await import('../lib/skill-list')
    const { skillInfo } = await import('../lib/skill-info')
    const { removeSkills } = await import('../lib/skill-remove')

    // 1. Init a new skill
    const initResult = await initSkill('my-test-skill', {
      cwd: tmp,
      description: 'Integration test skill',
    })
    expect(initResult.ok).toBe(true)
    expect(initResult.skillDir).toBeDefined()
    if (initResult.skillDir) {
      expect(existsSync(initResult.skillDir)).toBe(true)
    }
    if (initResult.skillPath) {
      expect(existsSync(initResult.skillPath)).toBe(true)
    }

    // 2. List skills -- should find it
    const listResult = await listSkills({ cwd: tmp })
    expect(listResult.ok).toBe(true)
    expect(listResult.skills.some((s) => s.name === 'my-test-skill')).toBe(true)

    // 3. Info -- should return metadata
    const infoResult = await skillInfo('my-test-skill', { cwd: tmp })
    expect(infoResult.ok).toBe(true)
    if (infoResult.ok) {
      expect(infoResult.value.frontmatter?.description).toBe('Integration test skill')
      expect(infoResult.value.symlinkStatus).toBe('copy')
    }

    // 4. Remove
    const removeResult = await removeSkills(['my-test-skill'], { cwd: tmp, yes: true })
    expect(removeResult).toHaveLength(1)
    expect(removeResult[0]?.canonicalRemoved).toBe(true)
    expect(existsSync(join(tmp, 'context', 'skills', 'my-test-skill'))).toBe(false)

    // 5. List again -- should be gone
    const listAfter = await listSkills({ cwd: tmp })
    expect(listAfter.skills.some((s) => s.name === 'my-test-skill')).toBe(false)
  })

  // -------------------------------------------------------------------------
  // Test 2: add from local source -> list -> remove
  // -------------------------------------------------------------------------

  test('add from local source -> list -> remove', async () => {
    const { addSkill } = await import('../lib/skill-add')
    const { listSkills } = await import('../lib/skill-list')
    const { removeSkills } = await import('../lib/skill-remove')

    // Create a source skill
    const sourceDir = join(tmp, 'external-source')
    await createSourceSkill(sourceDir, 'ext-skill', 'External skill')

    // Add it (agents: [] to avoid auto-detection of real agents)
    const addResult = await addSkill(sourceDir, {
      cwd: tmp,
      agents: [],
      copy: true,
      yes: true,
    })
    expect(addResult.ok).toBe(true)
    expect(addResult.installed).toHaveLength(1)
    expect(addResult.installed[0]?.name).toBe('ext-skill')

    // List should include it
    const listResult = await listSkills({ cwd: tmp })
    expect(listResult.ok).toBe(true)
    expect(listResult.skills.some((s) => s.name === 'ext-skill')).toBe(true)

    // Remove
    await removeSkills(['ext-skill'], { cwd: tmp, yes: true })
    const listAfter = await listSkills({ cwd: tmp })
    expect(listAfter.skills.some((s) => s.name === 'ext-skill')).toBe(false)
  })

  // -------------------------------------------------------------------------
  // Test 3: add same skill twice is idempotent
  // -------------------------------------------------------------------------

  test('add same skill twice is idempotent', async () => {
    const { addSkill } = await import('../lib/skill-add')
    const { listSkills } = await import('../lib/skill-list')

    const sourceDir = join(tmp, 'idem-source')
    await createSourceSkill(sourceDir, 'idem-skill', 'Idempotent skill')

    await addSkill(sourceDir, { cwd: tmp, agents: [], copy: true, yes: true })
    await addSkill(sourceDir, { cwd: tmp, agents: [], copy: true, yes: true })

    const listResult = await listSkills({ cwd: tmp })
    const matches = listResult.skills.filter((s) => s.name === 'idem-skill')
    expect(matches).toHaveLength(1) // No duplicates
  })

  // -------------------------------------------------------------------------
  // Test 4: remove all skills results in clean lock file
  // -------------------------------------------------------------------------

  test('remove all skills results in clean lock file', async () => {
    const { addSkill } = await import('../lib/skill-add')
    const { removeSkills } = await import('../lib/skill-remove')

    // Add two skills
    for (const name of ['alpha', 'beta']) {
      const dir = join(tmp, `source-${name}`)
      await createSourceSkill(dir, name, `${name} skill`)
      await addSkill(dir, { cwd: tmp, agents: [], copy: true, yes: true })
    }

    // Verify both are in lockfile
    const lockBefore = JSON.parse(await readFile(join(tmp, 'skills-lock.json'), 'utf-8'))
    expect(Object.keys(lockBefore.skills)).toHaveLength(2)

    // Remove both
    await removeSkills(['alpha', 'beta'], { cwd: tmp, yes: true })

    // Lock should be clean
    const lockAfter = JSON.parse(await readFile(join(tmp, 'skills-lock.json'), 'utf-8'))
    expect(Object.keys(lockAfter.skills)).toHaveLength(0)
  })

  // -------------------------------------------------------------------------
  // Test 5: init with invalid name fails gracefully
  // -------------------------------------------------------------------------

  test('init with invalid name does not create files', async () => {
    const { initSkill } = await import('../lib/skill-init')

    // "INVALID-NAME" has uppercase letters -- rejected by NAME_RE
    const result = await initSkill('INVALID-NAME', { cwd: tmp })
    expect(result.ok).toBe(false)
    expect(result.error).toBeDefined()
    expect(result.error?.code).toBe('E_INVALID_NAME')
    // The invalid skill directory should not have been created
    expect(existsSync(join(tmp, 'context', 'skills', 'INVALID-NAME'))).toBe(false)
  })

  // -------------------------------------------------------------------------
  // Test 6: info on non-existent skill returns error
  // -------------------------------------------------------------------------

  test('info on non-existent skill returns clean error', async () => {
    const { skillInfo } = await import('../lib/skill-info')
    const result = await skillInfo('ghost', { cwd: tmp })
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_SKILL_NOT_FOUND')
    }
  })

  // -------------------------------------------------------------------------
  // Test 7: checkOutdated with empty lock returns empty
  // -------------------------------------------------------------------------

  test('checkOutdated with empty lock returns empty array', async () => {
    const { checkOutdated } = await import('../lib/skill-outdated')
    const results = await checkOutdated({ cwd: tmp })
    expect(results).toEqual([])
  })

  // -------------------------------------------------------------------------
  // Test 8: all modules return JSON-serializable output
  // -------------------------------------------------------------------------

  test('all module results are JSON-serializable', async () => {
    const { initSkill } = await import('../lib/skill-init')
    const { listSkills } = await import('../lib/skill-list')
    const { skillInfo } = await import('../lib/skill-info')

    await initSkill('json-skill', {
      cwd: tmp,
      description: 'JSON test',
    })

    // initSkill result
    const initResult = await initSkill('json-skill2', {
      cwd: tmp,
      description: 'JSON test 2',
    })
    expect(() => JSON.stringify(initResult)).not.toThrow()

    // listSkills result
    const listResult = await listSkills({ cwd: tmp })
    expect(() => JSON.stringify(listResult)).not.toThrow()

    // skillInfo result
    const infoResult = await skillInfo('json-skill', { cwd: tmp })
    expect(infoResult.ok).toBe(true)
    if (infoResult.ok) {
      expect(() => JSON.stringify(infoResult.value)).not.toThrow()
    }
  })

  // -------------------------------------------------------------------------
  // Test 9: add from local then info shows lock metadata
  // -------------------------------------------------------------------------

  test('add from local populates lock metadata visible in info', async () => {
    const { addSkill } = await import('../lib/skill-add')
    const { skillInfo } = await import('../lib/skill-info')

    const sourceDir = join(tmp, 'meta-source')
    await createSourceSkill(sourceDir, 'meta-skill', 'Metadata test')

    await addSkill(sourceDir, { cwd: tmp, agents: [], copy: true, yes: true })

    const infoResult = await skillInfo('meta-skill', { cwd: tmp })
    expect(infoResult.ok).toBe(true)
    if (infoResult.ok) {
      const detail = infoResult.value
      expect(detail.name).toBe('meta-skill')
      expect(detail.source).toBe(sourceDir)
      expect(detail.sourceType).toBe('local')
      expect(detail.lockHash).toBeDefined()
      expect(detail.computedHash).toBeDefined()
      // Hash should match since we just installed it
      expect(detail.hashMatch).toBe(true)
    }
  })

  // -------------------------------------------------------------------------
  // Test 10: remove non-existent skill does not error hard
  // -------------------------------------------------------------------------

  test('remove non-existent skill returns graceful result', async () => {
    const { removeSkills } = await import('../lib/skill-remove')

    const results = await removeSkills(['no-such-skill'], { cwd: tmp, yes: true })
    expect(results).toHaveLength(1)
    expect(results[0]?.skill).toBe('no-such-skill')
    expect(results[0]?.canonicalRemoved).toBe(false)
    expect(results[0]?.removedFrom).toHaveLength(0)
    // Should report an error string
    expect(results[0]?.error).toBeDefined()
  })

  // -------------------------------------------------------------------------
  // Test 11: list on empty project returns empty array
  // -------------------------------------------------------------------------

  test('list on empty project returns ok with empty skills', async () => {
    const { listSkills } = await import('../lib/skill-list')
    const result = await listSkills({ cwd: tmp })
    expect(result.ok).toBe(true)
    expect(result.skills).toEqual([])
  })

  // -------------------------------------------------------------------------
  // Test 12: init then init same name fails
  // -------------------------------------------------------------------------

  test('init same skill name twice fails on second call', async () => {
    const { initSkill } = await import('../lib/skill-init')

    const first = await initSkill('dup-skill', { cwd: tmp, description: 'First' })
    expect(first.ok).toBe(true)

    const second = await initSkill('dup-skill', { cwd: tmp, description: 'Second' })
    expect(second.ok).toBe(false)
    expect(second.error?.code).toBe('E_DIR_EXISTS')
  })

  // -------------------------------------------------------------------------
  // Test 13: add from local with no SKILL.md fails
  // -------------------------------------------------------------------------

  test('add from source with no SKILL.md returns error', async () => {
    const { addSkill } = await import('../lib/skill-add')

    const emptyDir = join(tmp, 'empty-source')
    await mkdir(emptyDir, { recursive: true })
    await writeFile(join(emptyDir, 'README.md'), '# Not a skill\n')

    const result = await addSkill(emptyDir, {
      cwd: tmp,
      agents: [],
      yes: true,
    })
    expect(result.ok).toBe(false)
    expect(result.error?.code).toBe('E_NO_SKILLS')
  })

  // -------------------------------------------------------------------------
  // Test 14: checkOutdated with populated lock (local source)
  // -------------------------------------------------------------------------

  test('checkOutdated reports current for freshly-added local skill', async () => {
    const { addSkill } = await import('../lib/skill-add')
    const { checkOutdated } = await import('../lib/skill-outdated')

    const sourceDir = join(tmp, 'fresh-source')
    await createSourceSkill(sourceDir, 'fresh-skill', 'Fresh')

    await addSkill(sourceDir, { cwd: tmp, agents: [], copy: true, yes: true })

    const results = await checkOutdated({ cwd: tmp })
    expect(results.length).toBeGreaterThanOrEqual(1)

    const freshResult = results.find((r) => r.skill === 'fresh-skill')
    expect(freshResult).toBeDefined()
    // Freshly added: the hash in the lockfile should match what is on disk
    expect(freshResult?.status).toBe('current')
  })
})
