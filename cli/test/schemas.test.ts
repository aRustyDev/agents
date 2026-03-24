import { describe, expect, test } from 'bun:test'
import { readFile } from 'node:fs/promises'
import * as v from 'valibot'
import {
  ComponentRecord,
  detectUnknownPluginFields,
  KNOWN_PLUGIN_FIELDS,
  LockfileV1,
  LspConfig,
  LspServerEntry,
  MarketplaceEntry,
  MarketplaceManifest,
  McpConfig,
  McpServerEntry,
  PluginAuthor,
  PluginManifest,
  PluginSource,
  PluginSourceExtended,
  PluginSourceLegacy,
  PluginSourcePlanning,
  PluginSourcesManifest,
  SkillFrontmatter,
  SkillLockEntry,
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
const WORKTREE = `${REPO_ROOT}`

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

  test('parses real skills-lock.json from content/skills/', async () => {
    const data = await readJson(`${REPO_ROOT}/content/skills/skills-lock.json`)
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
    const result = v.safeParse(PluginSourceLegacy, 'content/commands/foo.md')
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
      source: 'content/skills/lang-swift-dev/SKILL.md',
      hash: 'sha256:964e09bc408c52c70ffbc99884131a0c6065a2455aefef0294a30b74bc104d1b',
      forked: false,
    }
    const result = v.safeParse(PluginSourceExtended, entry)
    expect(result.success).toBe(true)
  })

  test('accepts entry with only source', () => {
    const entry = { source: 'content/skills/foo/SKILL.md' }
    const result = v.safeParse(PluginSourceExtended, entry)
    expect(result.success).toBe(true)
  })

  test('accepts forked entry with forked_at', () => {
    const entry = {
      source: 'content/skills/foo/SKILL.md',
      hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000',
      forked: true,
      forked_at: '2025-01-15T12:00:00Z',
    }
    const result = v.safeParse(PluginSourceExtended, entry)
    expect(result.success).toBe(true)
  })

  test('rejects invalid hash format', () => {
    const entry = {
      source: 'content/skills/foo/SKILL.md',
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
    const result = v.safeParse(PluginSource, 'content/foo.md')
    expect(result.success).toBe(true)
  })

  test('accepts extended object', () => {
    const result = v.safeParse(PluginSource, {
      source: 'content/foo.md',
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
      `${WORKTREE}/content/plugins/blog-workflow/.claude-plugin/plugin.sources.json`
    )
    const result = v.safeParse(PluginSourcesManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(Object.keys(result.output.sources).length).toBeGreaterThanOrEqual(0)
    }
  })

  test('parses real swiftui-dev plugin.sources.json', async () => {
    const data = await readJson(
      `${WORKTREE}/content/plugins/frontend/swiftui-dev/.claude-plugin/plugin.sources.json`
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
      `${WORKTREE}/content/plugins/.template/.claude-plugin/plugin.sources.json`
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
      `${WORKTREE}/content/plugins/blog-workflow/.claude-plugin/plugin.json`
    )
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.name).toBe('blog-workflow')
      expect(result.output.version).toBe('4.1.0')
      expect(result.output.author?.name).toBe('Adam Smith')
      expect(result.output.keywords).toContain('blog')
    }
  })

  test('parses real swiftui-dev plugin.json', async () => {
    const data = await readJson(
      `${WORKTREE}/content/plugins/frontend/swiftui-dev/.claude-plugin/plugin.json`
    )
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.name).toBe('swiftui-dev')
      expect(result.output.keywords).toContain('swiftui')
      expect(result.output.skills!.length).toBe(7)
    }
  })

  test('parses real job-hunting plugin.json', async () => {
    const data = await readJson(
      `${WORKTREE}/content/plugins/job-hunting/.claude-plugin/plugin.json`
    )
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.name).toBe('job-hunting')
    }
  })

  test('rejects invalid semver', () => {
    const data = { name: 'test', version: 'not-semver', description: 'Test' }
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(false)
  })

  test('rejects missing required fields', () => {
    const data = { name: 'test' }
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(false)
  })

  test('accepts minimal manifest (no author)', () => {
    const data = { name: 'minimal', version: '1.0.0', description: 'A minimal plugin' }
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
  })

  test('accepts manifest with author', () => {
    const data = {
      name: 'with-author',
      version: '1.0.0',
      description: 'Plugin with author',
      author: { name: 'Test Author' },
    }
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
  })

  test('platformSkills field passes schema but detectUnknownPluginFields catches it', () => {
    // This was the v3.0.0 blog-workflow bug
    const data = {
      name: 'test',
      version: '1.0.0',
      description: 'Test',
      platformSkills: [{ name: 'astro', path: './skills/astro/SKILL.md' }],
    }
    // Schema accepts it (extra fields pass through via safeParse)
    const result = v.safeParse(PluginManifest, data)
    expect(result.success).toBe(true)
    // But detectUnknownPluginFields catches it
    const unknown = detectUnknownPluginFields(data)
    expect(unknown).toContain('platformSkills')
  })

  test('mcpServers field in plugin.json is detected as unknown', () => {
    const data = { name: 'test', version: '1.0.0', description: 'Test', mcpServers: './.mcp.json' }
    const unknown = detectUnknownPluginFields(data)
    expect(unknown).toContain('mcpServers')
  })

  test('lspServers field in plugin.json is detected as unknown', () => {
    const data = { name: 'test', version: '1.0.0', description: 'Test', lspServers: './.lsp.json' }
    const unknown = detectUnknownPluginFields(data)
    expect(unknown).toContain('lspServers')
  })
})

// ---------------------------------------------------------------------------
// Unknown field detection
// ---------------------------------------------------------------------------

describe('detectUnknownPluginFields', () => {
  test('returns empty for valid fields only', () => {
    const data = { name: 'test', version: '1.0.0', description: 'Test', commands: [] }
    expect(detectUnknownPluginFields(data)).toEqual([])
  })

  test('detects platformSkills as unknown', () => {
    const data = { name: 'test', platformSkills: [] }
    expect(detectUnknownPluginFields(data)).toContain('platformSkills')
  })

  test('detects mcpServers and lspServers as unknown', () => {
    const data = { name: 'test', mcpServers: './.mcp.json', lspServers: './.lsp.json' }
    const unknown = detectUnknownPluginFields(data)
    expect(unknown).toContain('mcpServers')
    expect(unknown).toContain('lspServers')
  })

  test('ignores all known fields', () => {
    const data: Record<string, unknown> = {}
    for (const field of KNOWN_PLUGIN_FIELDS) {
      data[field] = 'test'
    }
    expect(detectUnknownPluginFields(data)).toEqual([])
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

// ---------------------------------------------------------------------------
// LspConfig
// ---------------------------------------------------------------------------

describe('LspServerEntry', () => {
  test('accepts valid entry with command and extensionToLanguage', () => {
    const entry = {
      command: 'typescript-language-server',
      args: ['--stdio'],
      extensionToLanguage: { '.ts': 'typescript', '.tsx': 'typescriptreact' },
    }
    const result = v.safeParse(LspServerEntry, entry)
    expect(result.success).toBe(true)
  })

  test('accepts entry without optional args', () => {
    const entry = {
      command: 'pylsp',
      extensionToLanguage: { '.py': 'python' },
    }
    const result = v.safeParse(LspServerEntry, entry)
    expect(result.success).toBe(true)
  })

  test('rejects entry missing command', () => {
    const entry = {
      extensionToLanguage: { '.py': 'python' },
    }
    const result = v.safeParse(LspServerEntry, entry)
    expect(result.success).toBe(false)
  })

  test('rejects entry missing extensionToLanguage', () => {
    const entry = {
      command: 'pylsp',
    }
    const result = v.safeParse(LspServerEntry, entry)
    expect(result.success).toBe(false)
  })
})

describe('LspConfig', () => {
  test('accepts valid config with multiple servers', () => {
    const config = {
      lspServers: {
        typescript: {
          command: 'typescript-language-server',
          args: ['--stdio'],
          extensionToLanguage: { '.ts': 'typescript', '.tsx': 'typescriptreact' },
        },
        python: {
          command: 'pylsp',
          extensionToLanguage: { '.py': 'python' },
        },
      },
    }
    const result = v.safeParse(LspConfig, config)
    expect(result.success).toBe(true)
  })

  test('accepts config with empty servers', () => {
    const config = { lspServers: {} }
    const result = v.safeParse(LspConfig, config)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(Object.keys(result.output.lspServers)).toHaveLength(0)
    }
  })

  test('rejects config missing lspServers key', () => {
    const config = { servers: {} }
    const result = v.safeParse(LspConfig, config)
    expect(result.success).toBe(false)
  })

  test('rejects server entry with invalid shape', () => {
    const config = {
      lspServers: {
        broken: { command: 123 },
      },
    }
    const result = v.safeParse(LspConfig, config)
    expect(result.success).toBe(false)
  })

  test('empty lspServers object is valid schema-wise but validatePlugin warns', () => {
    // This was the actual blog-workflow bug: {"lspServers": {}} passed JSON parse
    // but Claude Code expected command + extensionToLanguage
    const data = { lspServers: {} }
    const result = v.safeParse(LspConfig, data)
    expect(result.success).toBe(true)
    // validatePlugin separately warns about empty servers
  })

  test('rejects server entry missing command', () => {
    const data = { lspServers: { 'my-lsp': { extensionToLanguage: { '.ts': 'typescript' } } } }
    const result = v.safeParse(LspConfig, data)
    expect(result.success).toBe(false)
  })

  test('rejects server entry missing extensionToLanguage', () => {
    const data = { lspServers: { 'my-lsp': { command: 'typescript-language-server' } } }
    const result = v.safeParse(LspConfig, data)
    expect(result.success).toBe(false)
  })

  test('rejects wrong top-level key', () => {
    // Someone writes "lsp" instead of "lspServers"
    const data = { lsp: { 'my-lsp': { command: 'tsc', extensionToLanguage: {} } } }
    const result = v.safeParse(LspConfig, data)
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// McpConfig
// ---------------------------------------------------------------------------

describe('McpServerEntry', () => {
  test('accepts full server entry', () => {
    const entry = {
      command: 'npx',
      args: ['-y', '@mcp/server'],
      env: { API_KEY: 'test-key' },
    }
    const result = v.safeParse(McpServerEntry, entry)
    expect(result.success).toBe(true)
  })

  test('accepts minimal server entry', () => {
    const entry = { command: 'mcp-server-stdio' }
    const result = v.safeParse(McpServerEntry, entry)
    expect(result.success).toBe(true)
  })

  test('rejects entry missing command', () => {
    const entry = { args: ['--flag'] }
    const result = v.safeParse(McpServerEntry, entry)
    expect(result.success).toBe(false)
  })
})

describe('McpConfig', () => {
  test('accepts flat mcpServers format', () => {
    const config = {
      mcpServers: {
        crawl4ai: {
          command: 'npx',
          args: ['-y', 'crawl4ai-mcp'],
          env: { CRAWL4AI_API_KEY: 'test' },
        },
      },
    }
    const result = v.safeParse(McpConfig, config)
    expect(result.success).toBe(true)
  })

  test('accepts nested mcp.servers format', () => {
    const config = {
      mcp: {
        servers: {
          crawl4ai: {
            command: 'npx',
            args: ['-y', 'crawl4ai-mcp'],
          },
        },
      },
    }
    const result = v.safeParse(McpConfig, config)
    expect(result.success).toBe(true)
  })

  test('accepts flat format with empty servers', () => {
    const config = { mcpServers: {} }
    const result = v.safeParse(McpConfig, config)
    expect(result.success).toBe(true)
  })

  test('accepts nested format with empty servers', () => {
    const config = { mcp: { servers: {} } }
    const result = v.safeParse(McpConfig, config)
    expect(result.success).toBe(true)
  })

  test('rejects config with neither format', () => {
    const config = { servers: {} }
    const result = v.safeParse(McpConfig, config)
    expect(result.success).toBe(false)
  })

  test('rejects server entry missing command', () => {
    const data = { mcpServers: { 'my-mcp': { args: ['--port', '3000'] } } }
    const result = v.safeParse(McpConfig, data)
    expect(result.success).toBe(false)
  })

  test('rejects empty object (no mcpServers or mcp key)', () => {
    const data = {}
    const result = v.safeParse(McpConfig, data)
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// MarketplaceManifest
// ---------------------------------------------------------------------------

describe('MarketplaceEntry', () => {
  test('accepts valid entry', () => {
    const entry = {
      name: 'test-plugin',
      source: './content/plugins/test-plugin',
      description: 'A test plugin',
      version: '1.0.0',
      author: { name: 'Test Author', email: 'test@example.com' },
      keywords: ['test'],
      license: 'MIT',
      homepage: 'https://example.com',
      repository: 'https://github.com/test/repo.git',
    }
    const result = v.safeParse(MarketplaceEntry, entry)
    expect(result.success).toBe(true)
  })

  test('accepts entry with prerelease semver', () => {
    const entry = {
      name: 'beta-plugin',
      source: './content/plugins/beta',
      description: 'Beta',
      version: '1.0.0-beta.1',
      author: { name: 'Author' },
      keywords: [],
      license: 'MIT',
      homepage: 'https://example.com',
      repository: 'https://github.com/test/repo',
    }
    const result = v.safeParse(MarketplaceEntry, entry)
    expect(result.success).toBe(true)
  })

  test('rejects invalid semver version', () => {
    const entry = {
      name: 'bad-version',
      source: './content/plugins/bad',
      description: 'Bad',
      version: 'not-semver',
      author: { name: 'Author' },
      keywords: [],
      license: 'MIT',
      homepage: 'https://example.com',
      repository: 'https://github.com/test/repo',
    }
    const result = v.safeParse(MarketplaceEntry, entry)
    expect(result.success).toBe(false)
  })

  test('rejects missing required fields', () => {
    const entry = { name: 'incomplete' }
    const result = v.safeParse(MarketplaceEntry, entry)
    expect(result.success).toBe(false)
  })
})

describe('MarketplaceManifest', () => {
  test('parses real marketplace.json from repo', async () => {
    const data = await readJson(`${REPO_ROOT}/.claude-plugin/marketplace.json`)
    const result = v.safeParse(MarketplaceManifest, data)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.output.plugins.length).toBeGreaterThan(0)
      expect(result.output.owner.name).toBe('aRustyDev')
    }
  })

  test('accepts valid manifest', () => {
    const manifest = {
      name: 'test-marketplace',
      owner: { name: 'Test Owner', email: 'test@example.com' },
      plugins: [
        {
          name: 'plugin-a',
          source: './plugins/a',
          description: 'Plugin A',
          version: '1.0.0',
          author: { name: 'Author' },
          keywords: ['a'],
          license: 'MIT',
          homepage: 'https://example.com/a',
          repository: 'https://github.com/test/a',
        },
      ],
    }
    const result = v.safeParse(MarketplaceManifest, manifest)
    expect(result.success).toBe(true)
  })

  test('accepts manifest with empty plugins array', () => {
    const manifest = {
      name: 'empty',
      owner: { name: 'Owner' },
      plugins: [],
    }
    const result = v.safeParse(MarketplaceManifest, manifest)
    expect(result.success).toBe(true)
  })

  test('rejects manifest missing owner', () => {
    const manifest = { name: 'no-owner', plugins: [] }
    const result = v.safeParse(MarketplaceManifest, manifest)
    expect(result.success).toBe(false)
  })

  test('rejects manifest with invalid plugin entry', () => {
    const manifest = {
      name: 'bad-entry',
      owner: { name: 'Owner' },
      plugins: [{ name: 'incomplete' }],
    }
    const result = v.safeParse(MarketplaceManifest, manifest)
    expect(result.success).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// SkillFrontmatter — additional edge case tests
// ---------------------------------------------------------------------------

describe('SkillFrontmatter (edge cases)', () => {
  test('rejects non-string tags', () => {
    const fm = {
      name: 'bad-tags',
      description: 'Has bad tags',
      tags: [1, 2, 3],
    }
    const result = v.safeParse(SkillFrontmatter, fm)
    expect(result.success).toBe(false)
  })

  test('rejects nested object in place of string field', () => {
    // The Astro platform: bug — a nested object where a string is expected
    const fm = {
      name: 'nested-obj',
      description: 'Has nested object',
      version: { major: 1, minor: 0, patch: 0 },
    }
    const result = v.safeParse(SkillFrontmatter, fm)
    expect(result.success).toBe(false)
  })

  test('rejects tags as a string instead of array', () => {
    const fm = {
      name: 'string-tags',
      description: 'Tags should be array',
      tags: 'not-an-array',
    }
    const result = v.safeParse(SkillFrontmatter, fm)
    expect(result.success).toBe(false)
  })

  test('allows nested objects via passthrough for extra fields (Astro platform bug)', () => {
    // This was the blog-workflow platform skill bug -- nested `platform:` object
    // The schema accepts it since 'platform' is not a defined field and Valibot
    // strips unknown keys by default with v.object.
    // The validator would warn on non-standard nested objects at runtime.
    const fm = {
      name: 'platform-astro',
      description: 'Astro config',
      platform: { name: 'astro', paths: { published: 'src/' } },
    }
    const result = v.safeParse(SkillFrontmatter, fm)
    // Valibot v.object strips unknown keys, so this succeeds (platform key ignored)
    expect(result.success).toBe(true)
  })
})
