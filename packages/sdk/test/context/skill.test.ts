import { afterAll, beforeAll, describe, expect, it } from 'bun:test'
import { mkdir, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { skillModule } from '../../src/context/skill'
import { parseSkill } from '../../src/context/skill/parser'

const TMP_DIR = join(tmpdir(), `sdk-skill-test-${Date.now()}`)

beforeAll(async () => {
  await mkdir(TMP_DIR, { recursive: true })
})

afterAll(async () => {
  await rm(TMP_DIR, { recursive: true, force: true })
})

describe('parseSkill', () => {
  it('parses valid SKILL.md with frontmatter', async () => {
    const path = join(TMP_DIR, 'valid-SKILL.md')
    await writeFile(
      path,
      `---
name: test-skill
description: A test skill
tags:
  - testing
  - demo
---
# Test Skill

This is the body of the skill.

## Usage

Use it like this.
`
    )

    const result = await parseSkill(path)
    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.type).toBe('skill')
    expect(result.value.name).toBe('test-skill')
    expect(result.value.frontmatter.name).toBe('test-skill')
    expect(result.value.frontmatter.description).toBe('A test skill')
    expect(result.value.frontmatter.tags).toEqual(['testing', 'demo'])
    expect(result.value.metadata.sectionCount).toBe(2)
    expect(result.value.metadata.wordCount).toBeGreaterThan(0)
    expect(result.value.metadata.lineCount).toBeGreaterThan(0)
  })

  it('returns error for missing file', async () => {
    const result = await parseSkill(join(TMP_DIR, 'nonexistent.md'))
    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_COMPONENT_NOT_FOUND')
  })

  it('returns error for invalid frontmatter (missing required fields)', async () => {
    const path = join(TMP_DIR, 'invalid-SKILL.md')
    await writeFile(
      path,
      `---
tags:
  - no-name
---
# Missing Name

No name or description in frontmatter.
`
    )

    const result = await parseSkill(path)
    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_SCHEMA_INVALID')
  })
})

describe('skillModule', () => {
  it('has correct type', () => {
    expect(skillModule.type).toBe('skill')
  })

  it('validate succeeds for valid component', () => {
    const component = {
      type: 'skill' as const,
      name: 'test',
      content: '# Test',
      frontmatter: {
        name: 'test',
        description: 'A test skill',
        tags: ['testing'],
      },
      metadata: {
        wordCount: 1,
        sectionCount: 1,
        headingTree: [{ depth: 1, title: 'Test' }],
        lineCount: 1,
      },
    }
    const result = skillModule.validate(component)
    expect(result.valid).toBe(true)
    expect(result.errors).toHaveLength(0)
  })

  it('validate warns when tags are missing', () => {
    const component = {
      type: 'skill' as const,
      name: 'test',
      content: '# Test',
      frontmatter: {
        name: 'test',
        description: 'A test skill',
      },
      metadata: {
        wordCount: 1,
        sectionCount: 1,
        headingTree: [{ depth: 1, title: 'Test' }],
        lineCount: 1,
      },
    }
    const result = skillModule.validate(component)
    expect(result.valid).toBe(true)
    expect(result.warnings.length).toBeGreaterThan(0)
  })
})
