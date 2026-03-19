import { describe, expect, test } from 'bun:test'
import { readFile } from 'node:fs/promises'
import * as v from 'valibot'
import {
  SkillLockEntry,
  LockfileV1,
  PluginSourceLegacy,
  PluginSourceExtended,
  PluginSourcePlanning,
  PluginSource,
  PluginSourcesManifest,
  PluginManifest,
  PluginAuthor,
  SkillFrontmatter,
  ComponentRecord,
  StatusMessage,
} from '../lib/schemas'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Read and parse a JSON file, returning the parsed object. */
async function readJson(path: string): Promise<unknown> {
  const raw = await readFile(path, 'utf-8')
  return JSON.parse(raw)
}

// Base paths for real test files
const REPO_ROOT = '/private/etc/infra/pub/ai'
const WORKTREE = `${REPO_ROOT}/.worktrees/ts-migration`

// ---------------------------------------------------------------------------
// SkillLockEntry
// ---------------------------------------------------------------------------

describe('SkillLockEntry', () => {
  test('accepts valid entry', () => {
    const entry = {
      source: 'steveyegge/beads',
      sourceType: 'github',
      computedHash: '16b0efc72b43177e1ad05e3f2e04132d266033e220834fd692369c65a15f8f39',
    }
    const result = v.safeParse(SkillLockEntry, entry)
    expect(result.success).toBe(true)
  })

  test('rejects hash with sha256: prefix', () => {
    const entry = {
      source: 'steveyegge/beads',
      sourceType: 'github',
      computedHash: 'sha256:16b0efc72b43177e1ad05e3f2e04132d266033e220834fd692369c65a15f8f39',
    }
    const result = v.safeParse(SkillLockEntry, entry)
    expect(result.success).toBe(false)
  })

  test('rejects short hash', () => {
    const entry = {
      source: 'steveyegge/beads',
      sourceType: 'github',
      computedHash: 'abc123',
    }
    const result = v.safeParse(SkillLockEntry, entry)
    expect(result.success).toBe(false)
  })

  test('rejects uppercase hex', () => {
    const entry = {
      source: 'test/repo',
      sourceType: 'github',
      computedHash: '16B0EFC72B43177E1AD05E3F2E04132D266033E220834FD692369C65A15F8F39',
    }
    const result = v.safeParse(SkillLockEntry, entry)
    expect(result.success).toBe(false)
  })

  test('rejects missing fields', () => {
    const result = v.safeParse(SkillLockEntry, { source: 'test' })
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// LockfileV1 — tested against REAL files
// ---------------------------------------------------------------------------

describe('LockfileV1', () => {
  test('parses real skills-lock.json from repo root', async () => {
    const data = await readJson(`${REPO_ROOT}/skills-lock.json`)
    const result = v.safeParse(LockfileV1, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.version).toBe(1)
      expect(Object.keys(result.output.skills).length).toBeGreaterThan(0)
    }
  })

  test('parses real skills-lock.json from context/skills/', async () => {
    const data = await readJson(`${REPO_ROOT}/context/skills/skills-lock.json`)
    const result = v.safeParse(LockfileV1, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.version).toBe(1)
      expect(result.output.skills.beads).toBeDefined()
    }
  })

  test('rejects wrong version', () => {
    const data = { version: 2, skills: {} }
    const result = v.safeParse(LockfileV1, data)
    expect(result.success).toBe(false)
  })

  test('rejects missing version', () => {
    const data = { skills: {} }
    const result = v.safeParse(LockfileV1, data)
    expect(result.success).toBe(false)
  })

  test('accepts empty skills record', () => {
    const data = { version: 1, skills: {} }
    const result = v.safeParse(LockfileV1, data)
    expect(result.success).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// Plugin source formats
// ---------------------------------------------------------------------------

describe('PluginSourceLegacy', () => {
  test('accepts a string path', () => {
    const result = v.safeParse(PluginSourceLegacy, 'context/commands/foo.md')
    expect(result.success).toBe(true)
  })

  test('rejects non-string', () => {
    const result = v.safeParse(PluginSourceLegacy, 42)
    expect(result.success).toBe(false)
  })
})

describe('PluginSourceExtended', () => {
  test('accepts full extended entry', () => {
    const entry = {
      source: 'context/skills/lang-swift-dev/SKILL.md',
      hash: 'sha256:964e09bc408c52c70ffbc99884131a0c6065a2455aefef0294a30b74bc104d1b',
      forked: false,
    }
    const result = v.safeParse(PluginSourceExtended, entry)
    expect(result.success).toBe(true)
  })

  test('accepts entry with only source', () => {
    const entry = { source: 'context/skills/foo/SKILL.md' }
    const result = v.safeParse(PluginSourceExtended, entry)
    expect(result.success).toBe(true)
  })

  test('accepts forked entry with forked_at', () => {
    const entry = {
      source: 'context/skills/foo/SKILL.md',
      hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
      forked: true,
      forked_at: '2025-01-15T12:00:00Z',
    }
    const result = v.safeParse(PluginSourceExtended, entry)
    expect(result.success).toBe(true)
  })

  test('rejects invalid hash format', () => {
    const entry = {
      source: 'context/skills/foo/SKILL.md',
      hash: 'md5:abc123',
    }
    const result = v.safeParse(PluginSourceExtended, entry)
    expect(result.success).toBe(false)
  })
})

describe('PluginSourcePlanning', () => {
  test('accepts planning entry', () => {
    const entry = {
      type: 'extend',
      base: 'https://github.com/example/repo',
      notes: 'Adapt for specific use case',
    }
    const result = v.safeParse(PluginSourcePlanning, entry)
    expect(result.success).toBe(true)
  })

  test('accepts minimal planning entry', () => {
    const entry = { type: 'create' }
    const result = v.safeParse(PluginSourcePlanning, entry)
    expect(result.success).toBe(true)
  })
})

describe('PluginSource (union)', () => {
  test('accepts legacy string', () => {
    const result = v.safeParse(PluginSource, 'context/foo.md')
    expect(result.success).toBe(true)
  })

  test('accepts extended object', () => {
    const result = v.safeParse(PluginSource, {
      source: 'context/foo.md',
      hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
    })
    expect(result.success).toBe(true)
  })

  test('accepts planning object', () => {
    const result = v.safeParse(PluginSource, { type: 'extend' })
    expect(result.success).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// PluginSourcesManifest — tested against REAL files
// ---------------------------------------------------------------------------

describe('PluginSourcesManifest', () => {
  test('parses real blog-workflow plugin.sources.json', async () => {
    const data = await readJson(
      `${WORKTREE}/context/plugins/blog-workflow/.claude-plugin/plugin.sources.json`,
    )
    const result = v.safeParse(PluginSourcesManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(Object.keys(result.output.sources).length).toBeGreaterThanOrEqual(0)
    }
  })

  test('parses real swiftui-dev plugin.sources.json', async () => {
    const data = await readJson(
      `${WORKTREE}/context/plugins/frontend/swiftui-dev/.claude-plugin/plugin.sources.json`,
    )
    const result = v.safeParse(PluginSourcesManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      // swiftui-dev has 3 sources with hashes
      expect(Object.keys(result.output.sources).length).toBe(3)
    }
  })

  test('parses empty sources manifest', async () => {
    const data = await readJson(
      `${WORKTREE}/context/plugins/.template/.claude-plugin/plugin.sources.json`,
    )
    const result = v.safeParse(PluginSourcesManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(Object.keys(result.output.sources)).toHaveLength(0)
    }
  })
})

// ---------------------------------------------------------------------------
// PluginManifest — tested against REAL files
// ---------------------------------------------------------------------------

describe('PluginManifest', () => {
  test('parses real blog-workflow plugin.json', async () => {
    const data = await readJson(
      `${WORKTREE}/context/plugins/blog-workflow/.claude-plugin/plugin.json`,
    )
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.name).toBe('blog-workflow')
      expect(result.output.version).toBe('3.0.0')
      expect(result.output.author.name).toBe('Adam Smith')
      expect(result.output.keywords).toContain('blog')
    }
  })

  test('parses real swiftui-dev plugin.json', async () => {
    const data = await readJson(
      `${WORKTREE}/context/plugins/frontend/swiftui-dev/.claude-plugin/plugin.json`,
    )
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.name).toBe('swiftui-dev')
      expect(result.output.keywords).toContain('swiftui')
      expect(result.output.skills!.length).toBe(7)
    }
  })

  test('parses real blog-workflow plugin.json with platformSkills', async () => {
    const data = await readJson(
      `${WORKTREE}/context/plugins/blog-workflow/.claude-plugin/plugin.json`,
    )
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.platformSkills).toBeDefined()
      expect(result.output.platformSkills!.length).toBeGreaterThan(0)
      expect(result.output.platformSkills![0]!.name).toBe('astro')
    }
  })

  test('parses real job-hunting plugin.json', async () => {
    const data = await readJson(
      `${WORKTREE}/context/plugins/job-hunting/.claude-plugin/plugin.json`,
    )
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.name).toBe('job-hunting')
    }
  })

  test('rejects invalid semver', () => {
    const data = {
      name: 'test',
      version: 'not-semver',
      description: 'Test',
      author: { name: 'Test' },
    }
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(false)
  })

  test('rejects missing required fields', () => {
    const data = { name: 'test' }
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(false)
  })

  test('accepts minimal manifest', () => {
    const data = {
      name: 'minimal',
      version: '1.0.0',
      description: 'A minimal plugin',
      author: { name: 'Test Author' },
    }
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// PluginAuthor
// ---------------------------------------------------------------------------

describe('PluginAuthor', () => {
  test('accepts full author', () => {
    const author = {
      name: 'Adam Smith',
      email: 'developer@gh.arusty.dev',
      url: 'https://im.arusty.dev',
    }
    const result = v.safeParse(PluginAuthor, author)
    expect(result.success).toBe(true)
  })

  test('accepts name-only author', () => {
    const result = v.safeParse(PluginAuthor, { name: 'Test' })
    expect(result.success).toBe(true)
  })

  test('rejects missing name', () => {
    const result = v.safeParse(PluginAuthor, { email: 'test@test.com' })
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// SkillFrontmatter
// ---------------------------------------------------------------------------

describe('SkillFrontmatter', () => {
  test('accepts minimal frontmatter', () => {
    const fm = { name: 'test-skill', description: 'A test skill' }
    const result = v.safeParse(SkillFrontmatter, fm)
    expect(result.success).toBe(true)
  })

  test('accepts frontmatter with all optional fields', () => {
    const fm = {
      name: 'full-skill',
      description: 'Complete example',
      version: '1.0.0',
      author: 'Test Author <test@example.com>',
      license: 'MIT',
      tags: ['test', 'example'],
      source: 'github',
      created: '2025-01-01',
      updated: '2025-06-01',
      globs: ['**/*.ts'],
      'allowed-tools': 'Read,Bash(bd:*)',
    }
    const result = v.safeParse(SkillFrontmatter, fm)
    expect(result.success).toBe(true)
  })

  test('rejects missing name', () => {
    const fm = { description: 'No name' }
    const result = v.safeParse(SkillFrontmatter, fm)
    expect(result.success).toBe(false)
  })

  test('rejects missing description', () => {
    const fm = { name: 'no-desc' }
    const result = v.safeParse(SkillFrontmatter, fm)
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// ComponentRecord
// ---------------------------------------------------------------------------

describe('ComponentRecord', () => {
  test('accepts full record', () => {
    const record = {
      id: 'abc123',
      name: 'test-component',
      type: 'skill',
      description: 'A test component',
      author: 'Test Author',
      canonical_url: 'https://example.com/component',
      github_url: 'https://github.com/test/repo',
      star_count: 42,
      source_type: 'github',
      source_name: 'test/repo',
      tags: ['test'],
      discovered_at: '2025-01-01T00:00:00Z',
    }
    const result = v.safeParse(ComponentRecord, record)
    expect(result.success).toBe(true)
  })

  test('accepts minimal record', () => {
    const record = {
      id: '1',
      name: 'test',
      type: 'skill',
      description: 'desc',
      source_type: 'local',
      source_name: 'repo',
    }
    const result = v.safeParse(ComponentRecord, record)
    expect(result.success).toBe(true)
  })

  test('rejects missing required fields', () => {
    const result = v.safeParse(ComponentRecord, { id: '1' })
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// StatusMessage
// ---------------------------------------------------------------------------

describe('StatusMessage', () => {
  test('accepts success message', () => {
    const msg = { status: 'success', message: 'All checks passed' }
    const result = v.safeParse(StatusMessage, msg)
    expect(result.success).toBe(true)
  })

  test('accepts error message with data', () => {
    const msg = {
      status: 'error',
      message: 'Build failed',
      data: { errors: ['missing source'] },
    }
    const result = v.safeParse(StatusMessage, msg)
    expect(result.success).toBe(true)
  })

  test('accepts all status values', () => {
    for (const status of ['success', 'error', 'warning', 'info'] as const) {
      const result = v.safeParse(StatusMessage, { status, message: 'test' })
      expect(result.success).toBe(true)
    }
  })

  test('rejects invalid status', () => {
    const msg = { status: 'unknown', message: 'test' }
    const result = v.safeParse(StatusMessage, msg)
    expect(result.success).toBe(false)
  })

  test('rejects missing message', () => {
    const msg = { status: 'success' }
    const result = v.safeParse(StatusMessage, msg)
    expect(result.success).toBe(false)
  })
})
