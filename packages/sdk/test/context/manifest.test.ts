import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import {
  detectSourceFormat,
  normalizeSource,
  readPluginManifest,
  readPluginSources,
  readSkillFrontmatter,
} from '@agents/sdk/context/manifest'

// Base paths for real test files
const WORKTREE = resolve(import.meta.dir, '../../../..')

// Temp directory created fresh before each test group
let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'manifest-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// readPluginManifest — real files
// ---------------------------------------------------------------------------

describe('readPluginManifest', () => {
  test('reads real blog-workflow plugin', async () => {
    const result = await readPluginManifest(`${WORKTREE}/content/plugins/blog-workflow`)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('blog-workflow')
      expect(result.value.version).toBe('4.1.0')
      expect(result.value.description).toContain('blog')
      expect(result.value.author?.name).toBe('Adam Smith')
      expect(result.value.commands!.length).toBeGreaterThan(0)
    }
  })

  test('reads real swiftui-dev plugin', async () => {
    const result = await readPluginManifest(`${WORKTREE}/content/plugins/frontend/swiftui-dev`)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('swiftui-dev')
      expect(result.value.keywords).toContain('swiftui')
      expect(result.value.skills!.length).toBe(7)
    }
  })

  test('reads real job-hunting plugin', async () => {
    const result = await readPluginManifest(`${WORKTREE}/content/plugins/job-hunting`)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('job-hunting')
      expect(result.value.version).toBe('0.1.3')
    }
  })

  test('returns error for non-existent plugin', async () => {
    const result = await readPluginManifest(join(tmp, 'nonexistent'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_MANIFEST_NOT_FOUND')
    }
  })

  test('returns error for invalid JSON', async () => {
    const pluginDir = join(tmp, '.claude-plugin')
    await mkdir(pluginDir, { recursive: true })
    await writeFile(join(pluginDir, 'plugin.json'), '{ bad json }')

    const result = await readPluginManifest(tmp)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_INVALID_JSON')
    }
  })

  test('returns error for invalid manifest structure', async () => {
    const pluginDir = join(tmp, '.claude-plugin')
    await mkdir(pluginDir, { recursive: true })
    await writeFile(
      join(pluginDir, 'plugin.json'),
      JSON.stringify({ name: 'test' }) // missing required fields
    )

    const result = await readPluginManifest(tmp)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_VALIDATION_FAILED')
    }
  })
})

// ---------------------------------------------------------------------------
// readPluginSources — real files
// ---------------------------------------------------------------------------

describe('readPluginSources', () => {
  test('reads real blog-workflow sources', async () => {
    const result = await readPluginSources(`${WORKTREE}/content/plugins/blog-workflow`)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.sources).toBeDefined()
      // blog-workflow has at least the feedback style source
      const keys = Object.keys(result.value.sources)
      expect(keys.length).toBeGreaterThanOrEqual(1)
    }
  })

  test('reads real swiftui-dev sources', async () => {
    const result = await readPluginSources(`${WORKTREE}/content/plugins/frontend/swiftui-dev`)
    expect(result.ok).toBe(true)
    if (result.ok) {
      // swiftui-dev has 3 sources
      expect(Object.keys(result.value.sources)).toHaveLength(3)
      // All entries should be extended format objects with source and hash
      for (const source of Object.values(result.value.sources)) {
        expect(typeof source).toBe('object')
      }
    }
  })

  test('returns empty manifest for plugin with no sources file', async () => {
    // Create a plugin dir without plugin.sources.json
    const pluginDir = join(tmp, '.claude-plugin')
    await mkdir(pluginDir, { recursive: true })
    // Do NOT create plugin.sources.json

    const result = await readPluginSources(tmp)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(Object.keys(result.value.sources)).toHaveLength(0)
    }
  })

  test('handles empty sources gracefully', async () => {
    const result = await readPluginSources(`${WORKTREE}/content/plugins/job-hunting`)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(Object.keys(result.value.sources)).toHaveLength(0)
    }
  })

  test('returns error for invalid JSON', async () => {
    const pluginDir = join(tmp, '.claude-plugin')
    await mkdir(pluginDir, { recursive: true })
    await writeFile(join(pluginDir, 'plugin.sources.json'), '{ bad }')

    const result = await readPluginSources(tmp)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_INVALID_JSON')
    }
  })
})

// ---------------------------------------------------------------------------
// readSkillFrontmatter — real files
// ---------------------------------------------------------------------------

describe('readSkillFrontmatter', () => {
  test('reads real beads SKILL.md', async () => {
    const result = await readSkillFrontmatter(`${WORKTREE}/content/skills/beads/SKILL.md`)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('beads')
      expect(result.value.description).toContain('issue tracker')
      expect(result.value.version).toBeDefined()
      expect(result.value['allowed-tools']).toBe('Read,Bash(bd:*)')
    }
  })

  test('reads real gitlab-cicd SKILL.md', async () => {
    const result = await readSkillFrontmatter(`${WORKTREE}/content/skills/gitlab-cicd/SKILL.md`)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('gitlab-cicd')
      expect(result.value.globs).toBeDefined()
      expect(result.value.globs!.length).toBeGreaterThan(0)
      expect(result.value.version).toBe('1.0.0')
    }
  })

  test('returns error for non-existent file', async () => {
    const result = await readSkillFrontmatter(join(tmp, 'nonexistent.md'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_SKILL_NOT_FOUND')
    }
  })

  test('returns error for file without frontmatter', async () => {
    const path = join(tmp, 'no-frontmatter.md')
    await writeFile(path, '# No Frontmatter\n\nJust content.')

    const result = await readSkillFrontmatter(path)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_NO_FRONTMATTER')
    }
  })

  test('returns error for invalid frontmatter (missing name)', async () => {
    const path = join(tmp, 'bad-fm.md')
    await writeFile(path, '---\ndescription: test\n---\n# Bad')

    const result = await readSkillFrontmatter(path)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_VALIDATION_FAILED')
    }
  })

  test('parses frontmatter with all optional fields', async () => {
    const path = join(tmp, 'full.md')
    await writeFile(
      path,
      [
        '---',
        'name: full-skill',
        'description: A skill with all fields',
        'version: 2.0.0',
        'author: Test Author',
        'license: MIT',
        'tags:',
        '  - test',
        '  - full',
        'globs:',
        '  - "**/*.ts"',
        'allowed-tools: Read,Write',
        '---',
        '',
        '# Full Skill',
      ].join('\n')
    )

    const result = await readSkillFrontmatter(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('full-skill')
      expect(result.value.tags).toEqual(['test', 'full'])
      expect(result.value.globs).toEqual(['**/*.ts'])
      expect(result.value['allowed-tools']).toBe('Read,Write')
    }
  })
})

// ---------------------------------------------------------------------------
// detectSourceFormat
// ---------------------------------------------------------------------------

describe('detectSourceFormat', () => {
  test('detects legacy string format', () => {
    expect(detectSourceFormat('content/commands/foo.md')).toBe('legacy')
  })

  test('detects extended object format', () => {
    expect(
      detectSourceFormat({
        source: 'content/skills/foo/SKILL.md',
        hash: 'sha256:abc',
      })
    ).toBe('extended')
  })

  test('detects planning object format', () => {
    expect(
      detectSourceFormat({
        type: 'extend',
        base: 'https://github.com/example/repo',
      })
    ).toBe('planning')
  })

  test('prefers extended over planning when both source and type present', () => {
    // If an object has `source`, it is extended regardless of other fields
    expect(
      detectSourceFormat({
        source: 'path/to/file',
        type: 'extend',
      })
    ).toBe('extended')
  })

  test('returns legacy for null', () => {
    expect(detectSourceFormat(null)).toBe('legacy')
  })

  test('returns legacy for number', () => {
    expect(detectSourceFormat(42)).toBe('legacy')
  })

  test('returns legacy for empty object', () => {
    expect(detectSourceFormat({})).toBe('legacy')
  })
})

// ---------------------------------------------------------------------------
// normalizeSource
// ---------------------------------------------------------------------------

describe('normalizeSource', () => {
  test('normalizes legacy string to extended', () => {
    const result = normalizeSource('content/commands/foo.md')
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.source).toBe('content/commands/foo.md')
      expect(result.value.hash).toBeUndefined()
      expect(result.value.forked).toBeUndefined()
    }
  })

  test('normalizes planning to extended with forked=true', () => {
    const result = normalizeSource({
      type: 'extend',
      base: 'https://github.com/example/repo',
    })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.source).toBe('')
      expect(result.value.forked).toBe(true)
    }
  })

  test('passes through valid extended format', () => {
    const entry = {
      source: 'content/skills/foo/SKILL.md',
      hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
      forked: false,
    }
    const result = normalizeSource(entry)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.source).toBe('content/skills/foo/SKILL.md')
      expect(result.value.hash).toBe(
        'sha256:0000000000000000000000000000000000000000000000000000000000000000'
      )
      expect(result.value.forked).toBe(false)
    }
  })

  test('passes through extended format with forked_at', () => {
    const entry = {
      source: 'content/skills/foo/SKILL.md',
      hash: 'sha256:' + 'a'.repeat(64),
      forked: true,
      forked_at: '2025-01-15T12:00:00Z',
    }
    const result = normalizeSource(entry)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.forked).toBe(true)
      expect(result.value.forked_at).toBe('2025-01-15T12:00:00Z')
    }
  })

  test('normalizes minimal planning entry', () => {
    const result = normalizeSource({ type: 'create' })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.source).toBe('')
      expect(result.value.forked).toBe(true)
    }
  })
})
