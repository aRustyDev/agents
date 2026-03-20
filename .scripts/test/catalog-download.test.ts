// .scripts/test/catalog-download.test.ts
import { describe, expect, it } from 'bun:test'
import { validateCatalogSource } from '../lib/catalog-download'

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
