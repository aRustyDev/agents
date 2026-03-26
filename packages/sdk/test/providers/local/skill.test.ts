import { describe, expect, test } from 'bun:test'
import { LocalSkillProvider } from '../../../src/providers/local'
import type { SkillOperations } from '../../../src/providers/local/skill-ops'

// ---------------------------------------------------------------------------
// Mock SkillOperations factory
// ---------------------------------------------------------------------------

function createMockOps(overrides?: Partial<SkillOperations>): SkillOperations {
  return {
    list: async () => ({
      ok: true,
      skills: [
        {
          name: 'beads',
          description: 'Issue tracker',
          source: 'local',
          path: '/tmp/skills/beads',
          agents: ['default'],
          tags: [],
          version: '0.1.0',
        },
        {
          name: 'gitlab-cicd',
          description: 'CI/CD pipelines',
          source: 'local',
          path: '/tmp/skills/gitlab-cicd',
          agents: ['default'],
          tags: [],
          version: '0.2.0',
        },
      ],
    }),
    add: async () => ({
      ok: true,
      installed: [
        {
          name: 'new-skill',
          source: 'test/repo',
          canonicalPath: '/tmp/skills/new-skill',
          agentLinks: ['/tmp/.claude/agents/default'],
        },
      ],
      warnings: [],
    }),
    remove: async () => [
      {
        skill: 'beads',
        removedFrom: ['/tmp/.claude/agents/default'],
        error: undefined,
      },
    ],
    info: async () => ({
      ok: true,
      value: {
        name: 'beads',
        path: '/tmp/skills/beads',
        source: 'local',
        sourceType: 'local',
        computedHash: 'abc123',
        lockHash: null,
        hashMatch: false,
        symlinkStatus: 'copy',
        installedAgents: ['default'],
        frontmatter: {
          name: 'beads',
          description: 'Issue tracker',
          version: '0.1.0',
          tags: [],
        },
      },
    }),
    ...overrides,
  }
}

// ---------------------------------------------------------------------------
// capabilities
// ---------------------------------------------------------------------------

describe('LocalSkillProvider capabilities', () => {
  test('declares skill support for all operations', () => {
    const provider = new LocalSkillProvider(createMockOps())

    expect(provider.id).toBe('local')
    expect(provider.displayName).toBe('Local Filesystem')
    expect(provider.capabilities.search).toContain('skill')
    expect(provider.capabilities.add).toContain('skill')
    expect(provider.capabilities.list).toContain('skill')
    expect(provider.capabilities.remove).toContain('skill')
    expect(provider.capabilities.info).toContain('skill')
  })

  test('publish is empty (not supported)', () => {
    const provider = new LocalSkillProvider(createMockOps())
    expect(provider.capabilities.publish).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// search
// ---------------------------------------------------------------------------

describe('LocalSkillProvider search', () => {
  test('finds installed skills by query', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.search({ query: 'beads' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('beads')
    expect(result.value.items[0]?.type).toBe('skill')
  })

  test('returns empty for unsupported type', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.search({ query: 'test', type: 'mcp-server' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
    expect(result.value.hasMore).toBe(false)
    expect(result.value.total).toBe(0)
  })

  test('returns all skills for empty query', async () => {
    const provider = new LocalSkillProvider(
      createMockOps({
        list: async () => ({
          ok: true,
          skills: [
            {
              name: 'alpha',
              description: 'A',
              source: 'local',
              path: '/tmp/a',
              agents: [],
              tags: [],
            },
            {
              name: 'beta',
              description: 'B',
              source: 'local',
              path: '/tmp/b',
              agents: [],
              tags: [],
            },
            {
              name: 'gamma',
              description: 'C',
              source: 'local',
              path: '/tmp/c',
              agents: [],
              tags: [],
            },
          ],
        }),
      })
    )
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(3)
    const names = result.value.items.map((c) => c.name).sort()
    expect(names).toEqual(['alpha', 'beta', 'gamma'])
  })

  test('paginates results', async () => {
    const provider = new LocalSkillProvider(
      createMockOps({
        list: async () => ({
          ok: true,
          skills: [
            {
              name: 'alpha',
              description: 'A',
              source: 'local',
              path: '/tmp/a',
              agents: [],
              tags: [],
            },
            {
              name: 'beta',
              description: 'B',
              source: 'local',
              path: '/tmp/b',
              agents: [],
              tags: [],
            },
            {
              name: 'gamma',
              description: 'C',
              source: 'local',
              path: '/tmp/c',
              agents: [],
              tags: [],
            },
          ],
        }),
      })
    )
    const result = await provider.search({ query: '', page: 1, limit: 2 })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(2)
    expect(result.value.hasMore).toBe(true)
    expect(result.value.total).toBe(3)
    expect(result.value.page).toBe(1)
    expect(result.value.pageSize).toBe(2)
  })

  test('searches by description', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.search({ query: 'pipeline' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('gitlab-cicd')
  })

  test('filters by name parameter', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.search({ query: '', name: 'beads' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('beads')
  })

  test('returns empty page when ops.list returns no skills', async () => {
    const provider = new LocalSkillProvider(
      createMockOps({
        list: async () => ({ ok: true, skills: [] }),
      })
    )
    const result = await provider.search({ query: 'anything' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// list
// ---------------------------------------------------------------------------

describe('LocalSkillProvider list', () => {
  test('returns installed skills', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.list('skill')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toHaveLength(2)
    const names = result.value.map((c) => c.name).sort()
    expect(names).toEqual(['beads', 'gitlab-cicd'])

    // Verify component shape
    const beads = result.value.find((c) => c.name === 'beads')!
    expect(beads.type).toBe('skill')
    expect(beads.description).toBe('Issue tracker')
    expect(beads.version).toBe('0.1.0')
    expect(beads.localPath).toBe('/tmp/skills/beads')
  })

  test('returns empty for unsupported type', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.list('mcp-server')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })

  test('returns empty when no skills exist', async () => {
    const provider = new LocalSkillProvider(
      createMockOps({
        list: async () => ({ ok: true, skills: [] }),
      })
    )
    const result = await provider.list('skill')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// info
// ---------------------------------------------------------------------------

describe('LocalSkillProvider info', () => {
  test('returns skill detail', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.info('beads', 'skill')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.type).toBe('skill')
    expect(result.value.name).toBe('beads')
    expect(result.value.description).toBe('Issue tracker')
    expect(result.value.version).toBe('0.1.0')
    expect(result.value.localPath).toBe('/tmp/skills/beads')
    // symlinkStatus 'copy' -> installMode 'copy'
    expect(result.value.installMode).toBe('copy')
  })

  test('returns error for missing skill', async () => {
    const provider = new LocalSkillProvider(
      createMockOps({
        info: async () => ({
          ok: false,
          error: { message: 'Skill not found: nonexistent' },
        }),
      })
    )
    const result = await provider.info('nonexistent', 'skill')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_COMPONENT_NOT_FOUND')
  })

  test('returns error for unsupported type', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.info('something', 'mcp-server')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })
})

// ---------------------------------------------------------------------------
// remove
// ---------------------------------------------------------------------------

describe('LocalSkillProvider remove', () => {
  test('removes installed skill via ops', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.remove('beads', 'skill')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.ok).toBe(true)
    expect(result.value.component).toBe('beads')
    expect(result.value.removedFrom).toEqual(['/tmp/.claude/agents/default'])
  })

  test('returns error message when skill not found', async () => {
    const provider = new LocalSkillProvider(
      createMockOps({
        remove: async () => [
          {
            skill: 'ghost',
            removedFrom: [],
            error: 'Skill "ghost" not found',
          },
        ],
      })
    )
    const result = await provider.remove('ghost', 'skill')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    // remove returns a result with an error message, not a Result error
    expect(result.value.ok).toBe(false)
    expect(result.value.error).toBeDefined()
  })

  test('returns error for unsupported type', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.remove('something', 'mcp-server')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })
})

// ---------------------------------------------------------------------------
// add
// ---------------------------------------------------------------------------

describe('LocalSkillProvider add', () => {
  test('installs skill via ops', async () => {
    const provider = new LocalSkillProvider(createMockOps())
    const result = await provider.add('/tmp/source/new-skill', {
      cwd: '/tmp/project',
      yes: true,
      copy: true,
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.ok).toBe(true)
    expect(result.value.components).toHaveLength(1)
    expect(result.value.components[0]?.name).toBe('new-skill')
    expect(result.value.components[0]?.type).toBe('skill')
  })

  test('returns error when ops.add fails', async () => {
    const provider = new LocalSkillProvider(
      createMockOps({
        add: async () => ({
          ok: false,
          error: undefined,
          installed: [],
          warnings: [],
        }),
      })
    )
    const result = await provider.add('/tmp/bad-source', {})

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })
})
