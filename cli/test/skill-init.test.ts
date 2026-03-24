import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { initSkill, validateSkillName } from '../lib/skill-init'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'skill-init-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// validateSkillName
// ---------------------------------------------------------------------------

describe('validateSkillName', () => {
  test('accepts valid kebab-case names', () => {
    expect(validateSkillName('my-skill')).toBeUndefined()
    expect(validateSkillName('lang-rust-dev')).toBeUndefined()
    expect(validateSkillName('ab')).toBeUndefined()
    expect(validateSkillName('a1')).toBeUndefined()
    expect(validateSkillName('skill123')).toBeUndefined()
  })

  test('rejects empty name', () => {
    const error = validateSkillName('')
    expect(error).toBeDefined()
    expect(error!.code).toBe('E_INVALID_NAME')
  })

  test('rejects single character name', () => {
    const error = validateSkillName('a')
    expect(error).toBeDefined()
    expect(error!.code).toBe('E_INVALID_NAME')
  })

  test('rejects names starting with a digit', () => {
    const error = validateSkillName('1skill')
    expect(error).toBeDefined()
    expect(error!.code).toBe('E_INVALID_NAME')
  })

  test('rejects names with uppercase letters', () => {
    const error = validateSkillName('MySkill')
    expect(error).toBeDefined()
    expect(error!.code).toBe('E_INVALID_NAME')
  })

  test('rejects names ending with hyphen', () => {
    const error = validateSkillName('my-skill-')
    expect(error).toBeDefined()
    expect(error!.code).toBe('E_INVALID_NAME')
  })

  test('rejects names with underscores', () => {
    const error = validateSkillName('my_skill')
    expect(error).toBeDefined()
    expect(error!.code).toBe('E_INVALID_NAME')
  })

  test('rejects names with spaces', () => {
    const error = validateSkillName('my skill')
    expect(error).toBeDefined()
    expect(error!.code).toBe('E_INVALID_NAME')
  })

  test('rejects names starting with hyphen', () => {
    const error = validateSkillName('-skill')
    expect(error).toBeDefined()
    expect(error!.code).toBe('E_INVALID_NAME')
  })
})

// ---------------------------------------------------------------------------
// initSkill -- built-in template
// ---------------------------------------------------------------------------

describe('initSkill -- built-in template', () => {
  test('creates a skill directory with SKILL.md using built-in template', async () => {
    const baseDir = join(tmp, 'skills')

    const result = await initSkill('my-new-skill', {
      cwd: tmp,
      baseDir,
      description: 'A brand new skill for testing',
    })

    expect(result.ok).toBe(true)
    expect(result.skillDir).toBeDefined()
    expect(result.skillPath).toBeDefined()

    // Verify the file was created
    expect(existsSync(result.skillPath!)).toBe(true)

    // Verify content
    const content = await readFile(result.skillPath!, 'utf-8')
    expect(content).toContain('name: my-new-skill')
    expect(content).toContain('description: A brand new skill for testing')
    expect(content).toContain('version: 0.1.0')
    expect(content).toContain('# my-new-skill')
  })

  test('uses default description when none provided', async () => {
    const baseDir = join(tmp, 'skills')

    const result = await initSkill('auto-desc', {
      cwd: tmp,
      baseDir,
    })

    expect(result.ok).toBe(true)
    const content = await readFile(result.skillPath!, 'utf-8')
    expect(content).toContain('description: A new skill called auto-desc')
  })

  test('uses default baseDir (content/skills) when not specified', async () => {
    const result = await initSkill('default-dir', {
      cwd: tmp,
      description: 'Test default dir',
    })

    expect(result.ok).toBe(true)
    expect(result.skillDir).toBe(join(tmp, 'content', 'skills', 'default-dir'))
  })
})

// ---------------------------------------------------------------------------
// initSkill -- custom template
// ---------------------------------------------------------------------------

describe('initSkill -- custom template', () => {
  test('uses explicit template file when provided', async () => {
    // Create a custom template
    const templateDir = join(tmp, 'templates')
    await mkdir(templateDir, { recursive: true })
    const templatePath = join(templateDir, 'custom.tmpl')
    await writeFile(
      templatePath,
      `---
name: {{name}}
description: {{description}}
version: 1.0.0
tags: [custom]
---

# Custom: {{name}}

This is a custom template for {{description}}.
`
    )

    const baseDir = join(tmp, 'skills')
    const result = await initSkill('custom-skill', {
      cwd: tmp,
      baseDir,
      description: 'Custom templated skill',
      template: templatePath,
    })

    expect(result.ok).toBe(true)
    const content = await readFile(result.skillPath!, 'utf-8')
    expect(content).toContain('version: 1.0.0')
    expect(content).toContain('tags: [custom]')
    expect(content).toContain('# Custom: custom-skill')
  })

  test('uses project default template from cli/templates/', async () => {
    // Create the project template
    const templateDir = join(tmp, 'cli', 'templates')
    await mkdir(templateDir, { recursive: true })
    await writeFile(
      join(templateDir, 'SKILL.md.tmpl'),
      `---
name: {{name}}
description: {{description}}
version: 0.0.1
tags: [project-default]
---

# {{name}} (project template)
`
    )

    const baseDir = join(tmp, 'skills')
    const result = await initSkill('project-skill', {
      cwd: tmp,
      baseDir,
      description: 'Project template test',
    })

    expect(result.ok).toBe(true)
    const content = await readFile(result.skillPath!, 'utf-8')
    expect(content).toContain('tags: [project-default]')
    expect(content).toContain('# project-skill (project template)')
  })
})

// ---------------------------------------------------------------------------
// initSkill -- error cases
// ---------------------------------------------------------------------------

describe('initSkill -- error cases', () => {
  test('returns error when directory already exists', async () => {
    const baseDir = join(tmp, 'skills')
    const existingDir = join(baseDir, 'existing-skill')
    await mkdir(existingDir, { recursive: true })

    const result = await initSkill('existing-skill', {
      cwd: tmp,
      baseDir,
    })

    expect(result.ok).toBe(false)
    expect(result.error).toBeDefined()
    expect(result.error!.code).toBe('E_DIR_EXISTS')
  })

  test('returns error for invalid skill names', async () => {
    const invalidNames = ['', 'a', 'MySkill', '1bad', 'under_score', 'trail-']

    for (const name of invalidNames) {
      const result = await initSkill(name, {
        cwd: tmp,
        baseDir: join(tmp, 'skills'),
      })
      expect(result.ok).toBe(false)
      expect(result.error!.code).toBe('E_INVALID_NAME')
    }
  })

  test('returns error when template produces invalid frontmatter', async () => {
    // Create a template with missing required fields
    const templateDir = join(tmp, 'templates')
    await mkdir(templateDir, { recursive: true })
    const templatePath = join(templateDir, 'bad.tmpl')
    await writeFile(
      templatePath,
      `---
version: 1.0.0
---

# No name or description in frontmatter
`
    )

    const result = await initSkill('bad-template', {
      cwd: tmp,
      baseDir: join(tmp, 'skills'),
      template: templatePath,
    })

    expect(result.ok).toBe(false)
    expect(result.error!.code).toBe('E_TEMPLATE_INVALID')
  })
})
