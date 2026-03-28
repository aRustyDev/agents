import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { listZip } from '@agents/core/archive'
import { packageSkill } from '@agents/sdk/context/skill/package'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'skill-package-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// packageSkill
// ---------------------------------------------------------------------------

describe('packageSkill', () => {
  test('creates zip from skill directory with SKILL.md', async () => {
    const skillDir = join(tmp, 'my-skill')
    await mkdir(skillDir, { recursive: true })
    await writeFile(
      join(skillDir, 'SKILL.md'),
      '---\nname: my-skill\ndescription: Test\n---\n# My Skill'
    )
    await writeFile(join(skillDir, 'helper.ts'), 'export const x = 1')

    const result = await packageSkill(skillDir)

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.skillName).toBe('my-skill')
    expect(result.value.fileCount).toBe(2)
    expect(existsSync(result.value.zipPath)).toBe(true)
  })

  test('fails if no SKILL.md', async () => {
    const skillDir = join(tmp, 'no-skill-md')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'readme.md'), '# Not a skill')

    const result = await packageSkill(skillDir)

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_VALIDATION_FAILED')
    expect(result.error.message).toContain('No SKILL.md')
  })

  test('excludes .git and .DS_Store', async () => {
    const skillDir = join(tmp, 'excl-skill')
    await mkdir(join(skillDir, '.git'), { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: excl\n---\n# Excl')
    await writeFile(join(skillDir, '.git', 'HEAD'), 'ref: refs/heads/main')
    await writeFile(join(skillDir, '.DS_Store'), 'junk')

    const zipPath = join(tmp, 'excl-skill.zip')
    const result = await packageSkill(skillDir, zipPath)

    expect(result.ok).toBe(true)
    if (!result.ok) return

    const listing = await listZip(result.value.zipPath)
    expect(listing.ok).toBe(true)
    if (!listing.ok) return
    expect(listing.value).toEqual(['SKILL.md'])
  })

  test('packaged zip contains expected files', async () => {
    const skillDir = join(tmp, 'full-skill')
    await mkdir(join(skillDir, 'examples'), { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: full\n---\n# Full')
    await writeFile(join(skillDir, 'examples', 'demo.ts'), 'console.log("demo")')
    await writeFile(join(skillDir, 'config.yaml'), 'key: value')

    const zipPath = join(tmp, 'full-skill.zip')
    const result = await packageSkill(skillDir, zipPath)

    expect(result.ok).toBe(true)
    if (!result.ok) return

    const listing = await listZip(result.value.zipPath)
    expect(listing.ok).toBe(true)
    if (!listing.ok) return
    expect(listing.value).toContain('SKILL.md')
    expect(listing.value).toContain('examples/demo.ts')
    expect(listing.value).toContain('config.yaml')
    expect(listing.value.length).toBe(3)
  })

  test('uses custom output path', async () => {
    const skillDir = join(tmp, 'custom-out')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: custom\n---\n# Custom')

    const customZip = join(tmp, 'dist', 'custom-output.zip')
    const result = await packageSkill(skillDir, customZip)

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.zipPath).toBe(customZip)
    expect(existsSync(customZip)).toBe(true)
  })

  test('supports additional exclude patterns', async () => {
    const skillDir = join(tmp, 'extra-excl')
    await mkdir(skillDir, { recursive: true })
    await writeFile(join(skillDir, 'SKILL.md'), '---\nname: extra\n---\n# Extra')
    await writeFile(join(skillDir, 'temp.log'), 'log data')

    const zipPath = join(tmp, 'extra-excl.zip')
    const result = await packageSkill(skillDir, zipPath, { exclude: ['*.log'] })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    const listing = await listZip(result.value.zipPath)
    expect(listing.ok).toBe(true)
    if (!listing.ok) return
    expect(listing.value).toEqual(['SKILL.md'])
  })
})
