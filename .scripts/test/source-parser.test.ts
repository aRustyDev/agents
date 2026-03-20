import { describe, expect, it, test } from 'bun:test'
import type { ParsedSource } from '../lib/source-parser'
import {
  detectGitProtocol,
  getOwnerRepo,
  parseSource,
  resolveCloneUrl,
  sanitizeSubpath,
} from '../lib/source-parser'

// ---------------------------------------------------------------------------
// parseSource — short form
// ---------------------------------------------------------------------------

describe('parseSource — short form', () => {
  test('owner/repo', () => {
    const r = parseSource('owner/repo')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/owner/repo.git',
    })
  })

  test('owner/repo@skill-name (skill filter only)', () => {
    const r = parseSource('owner/repo@skill-name')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/owner/repo.git',
      skillFilter: 'skill-name',
    })
  })

  test('owner/repo#main (ref only)', () => {
    const r = parseSource('owner/repo#main')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/owner/repo.git',
      ref: 'main',
    })
  })

  test('owner/repo#v1.2.3 (semver ref)', () => {
    const r = parseSource('owner/repo#v1.2.3')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/owner/repo.git',
      ref: 'v1.2.3',
    })
  })

  test('owner/repo#abc1234 (commit-ish ref)', () => {
    const r = parseSource('owner/repo#abc1234')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/owner/repo.git',
      ref: 'abc1234',
    })
  })

  test('owner/repo#main:skills/foo (ref + subpath)', () => {
    const r = parseSource('owner/repo#main:skills/foo')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/owner/repo.git',
      ref: 'main',
      subpath: 'skills/foo',
    })
  })

  test('owner/repo#main:skills/foo@bar (ref + subpath + skill)', () => {
    const r = parseSource('owner/repo#main:skills/foo@bar')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/owner/repo.git',
      ref: 'main',
      subpath: 'skills/foo',
      skillFilter: 'bar',
    })
  })

  test('repo with dots: my.org/my.repo', () => {
    const r = parseSource('my.org/my.repo')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/my.org/my.repo.git',
    })
  })

  test('repo with hyphens: my-org/my-repo', () => {
    const r = parseSource('my-org/my-repo')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/my-org/my-repo.git',
    })
  })

  test('skill filter with special chars: owner/repo@my_skill-v2', () => {
    const r = parseSource('owner/repo@my_skill-v2')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/owner/repo.git',
      skillFilter: 'my_skill-v2',
    })
  })

  test('trims whitespace', () => {
    const r = parseSource('  owner/repo  ')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value.type).toBe('github')
    expect(r.value.url).toBe('https://github.com/owner/repo.git')
  })
})

// ---------------------------------------------------------------------------
// parseSource — GitHub tree URLs
// ---------------------------------------------------------------------------

describe('parseSource — GitHub tree URL', () => {
  test('github.com/o/r/tree/branch/path', () => {
    const r = parseSource('github.com/o/r/tree/branch/path')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/o/r.git',
      ref: 'branch',
      subpath: 'path',
    })
  })

  test('https://github.com/o/r/tree/main/deep/path', () => {
    const r = parseSource('https://github.com/o/r/tree/main/deep/path')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/o/r.git',
      ref: 'main',
      subpath: 'deep/path',
    })
  })

  test('GitHub tree URL without subpath', () => {
    const r = parseSource('https://github.com/o/r/tree/main')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'github',
      url: 'https://github.com/o/r.git',
      ref: 'main',
      subpath: undefined,
    })
  })
})

// ---------------------------------------------------------------------------
// parseSource — GitLab tree URLs
// ---------------------------------------------------------------------------

describe('parseSource — GitLab tree URL', () => {
  test('gitlab.com/o/r/-/tree/branch/path', () => {
    const r = parseSource('gitlab.com/o/r/-/tree/branch/path')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'gitlab',
      url: 'https://gitlab.com/o/r.git',
      ref: 'branch',
      subpath: 'path',
    })
  })

  test('https://gitlab.com/o/r/-/tree/develop/src/lib', () => {
    const r = parseSource('https://gitlab.com/o/r/-/tree/develop/src/lib')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'gitlab',
      url: 'https://gitlab.com/o/r.git',
      ref: 'develop',
      subpath: 'src/lib',
    })
  })

  test('GitLab tree URL without subpath', () => {
    const r = parseSource('https://gitlab.com/o/r/-/tree/main')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'gitlab',
      url: 'https://gitlab.com/o/r.git',
      ref: 'main',
      subpath: undefined,
    })
  })
})

// ---------------------------------------------------------------------------
// parseSource — local paths
// ---------------------------------------------------------------------------

describe('parseSource — local paths', () => {
  test('./local/path (relative dot)', () => {
    const r = parseSource('./local/path')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'local',
      localPath: './local/path',
    })
  })

  test('../parent/path (relative dot-dot)', () => {
    const r = parseSource('../parent/path')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'local',
      localPath: '../parent/path',
    })
  })

  test('/absolute/path', () => {
    const r = parseSource('/absolute/path')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'local',
      localPath: '/absolute/path',
    })
  })

  test('. (current directory)', () => {
    const r = parseSource('.')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'local',
      localPath: '.',
    })
  })
})

// ---------------------------------------------------------------------------
// parseSource — git URLs
// ---------------------------------------------------------------------------

describe('parseSource — git URLs', () => {
  test('SSH URL: git@host:repo.git', () => {
    const r = parseSource('git@host:repo.git')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'git',
      url: 'git@host:repo.git',
    })
  })

  test('SSH URL with org: git@github.com:org/repo.git', () => {
    const r = parseSource('git@github.com:org/repo.git')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'git',
      url: 'git@github.com:org/repo.git',
    })
  })

  test('HTTPS .git URL: https://host/repo.git', () => {
    const r = parseSource('https://host/repo.git')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'git',
      url: 'https://host/repo.git',
    })
  })

  test('HTTPS .git URL with path: https://github.com/org/repo.git', () => {
    const r = parseSource('https://github.com/org/repo.git')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'git',
      url: 'https://github.com/org/repo.git',
    })
  })
})

// ---------------------------------------------------------------------------
// parseSource — well-known URLs
// ---------------------------------------------------------------------------

describe('parseSource — well-known URLs', () => {
  test('https://example.com/skills', () => {
    const r = parseSource('https://example.com/skills')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'well-known',
      url: 'https://example.com/skills',
    })
  })

  test('http://localhost:3000/api/skills', () => {
    const r = parseSource('http://localhost:3000/api/skills')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toEqual({
      type: 'well-known',
      url: 'http://localhost:3000/api/skills',
    })
  })
})

// ---------------------------------------------------------------------------
// parseSource — error cases
// ---------------------------------------------------------------------------

describe('parseSource — errors', () => {
  test('empty string returns E_INVALID_SOURCE', () => {
    const r = parseSource('')
    expect(r.ok).toBe(false)
    if (r.ok) return
    expect(r.error.code).toBe('E_INVALID_SOURCE')
    expect(r.error.message).toBe('Empty source string')
  })

  test('whitespace only returns E_INVALID_SOURCE', () => {
    const r = parseSource('   ')
    expect(r.ok).toBe(false)
    if (r.ok) return
    expect(r.error.code).toBe('E_INVALID_SOURCE')
    expect(r.error.message).toBe('Empty source string')
  })

  test('unrecognized string returns E_INVALID_SOURCE', () => {
    const r = parseSource('not-a-valid-source')
    expect(r.ok).toBe(false)
    if (r.ok) return
    expect(r.error.code).toBe('E_INVALID_SOURCE')
    expect(r.error.hint).toContain('Expected')
  })

  test('path traversal in subpath returns E_UNSAFE_SUBPATH', () => {
    const r = parseSource('owner/repo#main:../../etc/passwd')
    expect(r.ok).toBe(false)
    if (r.ok) return
    expect(r.error.code).toBe('E_UNSAFE_SUBPATH')
    expect(r.error.message).toContain('..')
  })
})

// ---------------------------------------------------------------------------
// getOwnerRepo
// ---------------------------------------------------------------------------

describe('getOwnerRepo', () => {
  test('extracts owner/repo from GitHub URL', () => {
    const parsed: ParsedSource = {
      type: 'github',
      url: 'https://github.com/owner/repo.git',
    }
    expect(getOwnerRepo(parsed)).toBe('owner/repo')
  })

  test('extracts owner/repo from GitLab URL', () => {
    const parsed: ParsedSource = {
      type: 'gitlab',
      url: 'https://gitlab.com/org/project.git',
    }
    expect(getOwnerRepo(parsed)).toBe('org/project')
  })

  test('returns null for local source (no URL)', () => {
    const parsed: ParsedSource = {
      type: 'local',
      localPath: './some/path',
    }
    expect(getOwnerRepo(parsed)).toBeNull()
  })

  test('returns null for well-known URL without github/gitlab pattern', () => {
    const parsed: ParsedSource = {
      type: 'well-known',
      url: 'https://example.com/skills',
    }
    expect(getOwnerRepo(parsed)).toBeNull()
  })

  test('returns null for SSH URL without github/gitlab domain', () => {
    const parsed: ParsedSource = {
      type: 'git',
      url: 'git@custom-host:org/repo.git',
    }
    expect(getOwnerRepo(parsed)).toBeNull()
  })

  test('handles GitHub HTTPS .git URL', () => {
    const parsed: ParsedSource = {
      type: 'git',
      url: 'https://github.com/aRustyDev/ai.git',
    }
    expect(getOwnerRepo(parsed)).toBe('aRustyDev/ai')
  })
})

// ---------------------------------------------------------------------------
// sanitizeSubpath
// ---------------------------------------------------------------------------

describe('sanitizeSubpath', () => {
  test('passes through simple path', () => {
    const r = sanitizeSubpath('skills/foo')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toBe('skills/foo')
  })

  test('single segment path', () => {
    const r = sanitizeSubpath('skills')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toBe('skills')
  })

  test('normalizes double slashes', () => {
    const r = sanitizeSubpath('skills//foo')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toBe('skills/foo')
  })

  test('strips trailing slash', () => {
    const r = sanitizeSubpath('skills/foo/')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toBe('skills/foo')
  })

  test('strips leading slash', () => {
    const r = sanitizeSubpath('/skills/foo')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toBe('skills/foo')
  })

  test('rejects .. traversal at start', () => {
    const r = sanitizeSubpath('../etc/passwd')
    expect(r.ok).toBe(false)
    if (r.ok) return
    expect(r.error.code).toBe('E_UNSAFE_SUBPATH')
  })

  test('rejects .. traversal in middle', () => {
    const r = sanitizeSubpath('skills/../../../etc/passwd')
    expect(r.ok).toBe(false)
    if (r.ok) return
    expect(r.error.code).toBe('E_UNSAFE_SUBPATH')
  })

  test('allows single dot segment', () => {
    const r = sanitizeSubpath('skills/./foo')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toBe('skills/./foo')
  })

  test('allows segments containing dots', () => {
    const r = sanitizeSubpath('skills/my.skill/v2.0')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(r.value).toBe('skills/my.skill/v2.0')
  })
})

// ---------------------------------------------------------------------------
// parseSource — roundtrip with getOwnerRepo
// ---------------------------------------------------------------------------

describe('parseSource + getOwnerRepo roundtrip', () => {
  test('short form round-trips owner/repo', () => {
    const r = parseSource('aRustyDev/ai')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(getOwnerRepo(r.value)).toBe('aRustyDev/ai')
  })

  test('GitHub tree URL round-trips owner/repo', () => {
    const r = parseSource('https://github.com/aRustyDev/ai/tree/main/context/skills')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(getOwnerRepo(r.value)).toBe('aRustyDev/ai')
    expect(r.value.ref).toBe('main')
    expect(r.value.subpath).toBe('context/skills')
  })

  test('local path has no owner/repo', () => {
    const r = parseSource('./local')
    expect(r.ok).toBe(true)
    if (!r.ok) return
    expect(getOwnerRepo(r.value)).toBeNull()
  })
})

// ---------------------------------------------------------------------------
// resolveCloneUrl
// ---------------------------------------------------------------------------

describe('resolveCloneUrl', () => {
  it('returns HTTPS URL by default', () => {
    expect(resolveCloneUrl('anthropics/skills')).toBe('https://github.com/anthropics/skills.git')
  })

  it('returns SSH URL when protocol is ssh', () => {
    expect(resolveCloneUrl('anthropics/skills', 'ssh')).toBe('git@github.com:anthropics/skills.git')
  })

  it('returns HTTPS URL when protocol is https', () => {
    expect(resolveCloneUrl('anthropics/skills', 'https')).toBe(
      'https://github.com/anthropics/skills.git'
    )
  })

  it('handles owner/repo with dots and hyphens', () => {
    expect(resolveCloneUrl('my-org/my.repo', 'ssh')).toBe('git@github.com:my-org/my.repo.git')
  })
})

describe('detectGitProtocol', () => {
  it('returns a valid GitProtocol value', () => {
    expect(['ssh', 'https']).toContain(detectGitProtocol())
  })
})
