// .scripts/test/catalog-download.test.ts

import { afterEach, beforeEach, describe, expect, it } from 'bun:test'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { downloadSkill, validateCatalogSource } from '../lib/catalog-download'

describe('validateCatalogSource', () => {
  it('accepts valid org/repo format', () => {
    const result = validateCatalogSource('anthropics/skills')
    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.ownerRepo).toBe('anthropics/skills')
  })

  it('accepts org/repo#ref (pinned)', () => {
    const result = validateCatalogSource('anthropics/skills#v1.2.0')
    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.ownerRepo).toBe('anthropics/skills')
    expect(result.value.ref).toBe('v1.2.0')
  })

  it('accepts GitHub tree URL (pinned)', () => {
    const result = validateCatalogSource('https://github.com/org/repo/tree/main/skills/my-skill')
    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.ownerRepo).toBe('org/repo')
    expect(result.value.ref).toBe('main')
    expect(result.value.subpath).toBe('skills/my-skill')
  })

  it('resolves SSH clone URL when protocol is ssh', () => {
    const result = validateCatalogSource('anthropics/skills', 'ssh')
    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.cloneUrl).toBe('git@github.com:anthropics/skills.git')
  })

  it('resolves HTTPS clone URL by default', () => {
    const result = validateCatalogSource('anthropics/skills', 'https')
    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.cloneUrl).toContain('https://github.com/')
  })

  it('rejects filesystem paths', () => {
    const result = validateCatalogSource('/tmp/worktrees/skill-inspect-11/.claude/skills/foo')
    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_NOT_GITHUB')
  })

  it('rejects empty strings', () => {
    const result = validateCatalogSource('')
    expect(result.ok).toBe(false)
  })

  it('accepts org/repo with dots and hyphens', () => {
    const result = validateCatalogSource('my-org/my.repo-name')
    expect(result.ok).toBe(true)
  })

  it('rejects non-GitHub URLs', () => {
    const result = validateCatalogSource('https://gitlab.com/org/repo')
    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_NOT_GITHUB')
  })
})

describe('downloadSkill', () => {
  // These test the local-path code path (no network)
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'dl-test-'))
  })
  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  it('downloads from a local directory with SKILL.md', async () => {
    // Create a fake skill
    const skillDir = join(tmpDir, 'my-skill')
    mkdirSync(skillDir, { recursive: true })
    writeFileSync(
      join(skillDir, 'SKILL.md'),
      '---\nname: my-skill\ndescription: test\n---\n# My Skill\nSome content here.'
    )

    const result = await downloadSkill('test-org/test-repo', 'my-skill', {
      localOverride: skillDir,
    })

    expect(result.path).toBeTruthy()
    expect(result.contentHash).toMatch(/^sha256:[a-f0-9]{64}$/)
    expect(result.wordCount).toBeGreaterThan(0)
    expect(result.sectionCount).toBe(1)
    expect(result.error).toBeUndefined()
  })

  it('returns error for missing SKILL.md', async () => {
    mkdirSync(join(tmpDir, 'empty-skill'), { recursive: true })

    const result = await downloadSkill('test-org/test-repo', 'empty-skill', {
      localOverride: join(tmpDir, 'empty-skill'),
    })

    expect(result.path).toBeNull()
    expect(result.error).toBeDefined()
    expect(result.errorType).toBe('download_failed')
  })

  it('returns error for invalid source format', async () => {
    const result = await downloadSkill('/tmp/bad/path', 'skill', {})
    expect(result.path).toBeNull()
    expect(result.errorType).toBe('source_invalid')
  })

  it('computes all mechanical fields on success', async () => {
    const skillDir = join(tmpDir, 'metrics-skill')
    mkdirSync(skillDir, { recursive: true })
    writeFileSync(
      join(skillDir, 'SKILL.md'),
      '---\nname: metrics-skill\ndescription: test\n---\n# H1\n## H2\n### H3\nword1 word2 word3'
    )
    writeFileSync(join(skillDir, 'extra.md'), 'extra file')

    const result = await downloadSkill('org/repo', 'metrics-skill', {
      localOverride: skillDir,
    })

    expect(result.contentHash).toMatch(/^sha256:/)
    expect(result.wordCount).toBeGreaterThan(0)
    expect(result.sectionCount).toBe(3)
    expect(result.fileCount).toBe(2)
    expect(result.headingTree).toHaveLength(3)
    expect(result.headingTree?.[0]).toEqual({ depth: 1, title: 'H1' })
  })
})
