import { describe, expect, test } from 'bun:test'
import {
  COMPONENT_TYPE_META,
  COMPONENT_TYPES,
  type Component,
  type ComponentAddOptions,
  type ComponentAddResult,
  type ComponentProvider,
  type ComponentType,
  type ComponentTypeMetadata,
  getActiveTypes,
  getComponentMeta,
  isComponentType,
  type PaginatedResult,
  type ProviderCapabilities,
  type PublishOptions,
  type PublishResult,
  parseComponentType,
  type RemoveResult,
  type SearchParams,
  toComponentType,
  toEntityType,
} from '@agents/core/component/types'

// ---------------------------------------------------------------------------
// COMPONENT_TYPES
// ---------------------------------------------------------------------------

describe('COMPONENT_TYPES', () => {
  test('contains exactly 12 types', () => {
    expect(COMPONENT_TYPES).toHaveLength(12)
  })

  test('includes all expected component types in order', () => {
    const expected = [
      'skill',
      'agent',
      'persona',
      'lsp',
      'mcp-server',
      'mcp-client',
      'mcp-tool',
      'rule',
      'hook',
      'plugin',
      'output-style',
      'command',
    ]
    expect([...COMPONENT_TYPES]).toEqual(expected)
  })

  test('is a readonly tuple (const assertion)', () => {
    // Attempting to mutate should be a type error at compile time;
    // at runtime the array is still a regular frozen-in-spirit tuple.
    expect(Array.isArray(COMPONENT_TYPES)).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// isComponentType
// ---------------------------------------------------------------------------

describe('isComponentType', () => {
  test('returns true for every valid ComponentType', () => {
    for (const t of COMPONENT_TYPES) {
      expect(isComponentType(t)).toBe(true)
    }
  })

  test('returns false for invalid strings', () => {
    expect(isComponentType('widget')).toBe(false)
    expect(isComponentType('')).toBe(false)
    expect(isComponentType('SKILL')).toBe(false) // case-sensitive
    expect(isComponentType('mcp_server')).toBe(false) // underscore, not hyphen
    expect(isComponentType('output_style')).toBe(false) // underscore, not hyphen
    expect(isComponentType('claude_md')).toBe(false) // removed from component types
  })

  test('narrows type after guard', () => {
    const value: string = 'skill'
    if (isComponentType(value)) {
      // After narrowing, value is ComponentType -- assign to typed binding
      const ct: ComponentType = value
      expect(ct).toBe('skill')
    } else {
      // Should not reach here for 'skill'
      expect(true).toBe(false)
    }
  })
})

// ---------------------------------------------------------------------------
// parseComponentType
// ---------------------------------------------------------------------------

describe('parseComponentType', () => {
  test('parses exact matches', () => {
    expect(parseComponentType('skill')).toBe('skill')
    expect(parseComponentType('mcp-server')).toBe('mcp-server')
    expect(parseComponentType('output-style')).toBe('output-style')
  })

  test('normalizes underscores to hyphens', () => {
    expect(parseComponentType('mcp_server')).toBe('mcp-server')
    expect(parseComponentType('output_style')).toBe('output-style')
    expect(parseComponentType('mcp_client')).toBe('mcp-client')
  })

  test('normalizes spaces to hyphens', () => {
    expect(parseComponentType('mcp server')).toBe('mcp-server')
    expect(parseComponentType('output style')).toBe('output-style')
  })

  test('normalizes uppercase to lowercase', () => {
    expect(parseComponentType('SKILL')).toBe('skill')
    expect(parseComponentType('MCP-SERVER')).toBe('mcp-server')
  })

  test('returns undefined for invalid input', () => {
    expect(parseComponentType('widget')).toBeUndefined()
    expect(parseComponentType('')).toBeUndefined()
    expect(parseComponentType('claude_md')).toBeUndefined()
  })
})

// ---------------------------------------------------------------------------
// getComponentMeta
// ---------------------------------------------------------------------------

describe('getComponentMeta', () => {
  test('returns metadata for each component type', () => {
    for (const t of COMPONENT_TYPES) {
      const meta = getComponentMeta(t)
      expect(meta).toBeDefined()
      expect(meta.name).toBe(t)
    }
  })

  test('skill metadata has expected values', () => {
    const meta = getComponentMeta('skill')
    expect(meta.pluralName).toBe('skills')
    expect(meta.placeholder).toBe(false)
    expect(meta.providers).toContain('local')
  })

  test('persona is a placeholder type', () => {
    const meta = getComponentMeta('persona')
    expect(meta.placeholder).toBe(true)
    expect(meta.providers).toEqual([])
  })

  test('mcp-server has smithery provider', () => {
    const meta = getComponentMeta('mcp-server')
    expect(meta.providers).toContain('smithery')
    expect(meta.placeholder).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// getActiveTypes
// ---------------------------------------------------------------------------

describe('getActiveTypes', () => {
  test('returns only non-placeholder types', () => {
    const active = getActiveTypes()
    for (const t of active) {
      expect(COMPONENT_TYPE_META[t].placeholder).toBe(false)
    }
  })

  test('excludes placeholder types', () => {
    const active = getActiveTypes()
    expect(active).not.toContain('persona')
    expect(active).not.toContain('lsp')
    expect(active).not.toContain('mcp-client')
    expect(active).not.toContain('mcp-tool')
    expect(active).not.toContain('hook')
  })

  test('includes known active types', () => {
    const active = getActiveTypes()
    expect(active).toContain('skill')
    expect(active).toContain('agent')
    expect(active).toContain('mcp-server')
    expect(active).toContain('rule')
    expect(active).toContain('plugin')
    expect(active).toContain('output-style')
    expect(active).toContain('command')
  })

  test('excludes hook (placeholder until provider exists)', () => {
    const active = getActiveTypes()
    expect(active).not.toContain('hook')
  })

  test('returns 7 active types', () => {
    expect(getActiveTypes()).toHaveLength(7)
  })
})

// ---------------------------------------------------------------------------
// COMPONENT_TYPE_META
// ---------------------------------------------------------------------------

describe('COMPONENT_TYPE_META', () => {
  test('has metadata for every component type', () => {
    for (const t of COMPONENT_TYPES) {
      expect(COMPONENT_TYPE_META[t]).toBeDefined()
    }
  })

  test('each entry has required fields', () => {
    for (const t of COMPONENT_TYPES) {
      const meta: ComponentTypeMetadata = COMPONENT_TYPE_META[t]
      expect(meta.name).toBe(t)
      expect(typeof meta.pluralName).toBe('string')
      expect(typeof meta.discoveryPattern).toBe('string')
      expect(Array.isArray(meta.providers)).toBe(true)
      expect(typeof meta.placeholder).toBe('boolean')
    }
  })
})

// ---------------------------------------------------------------------------
// Component interface
// ---------------------------------------------------------------------------

describe('Component', () => {
  test('minimal component has required fields only', () => {
    const c: Component = {
      type: 'skill',
      name: 'typescript-pro',
      source: 'local',
      description: 'TypeScript development skill',
    }
    expect(c.type).toBe('skill')
    expect(c.name).toBe('typescript-pro')
    expect(c.source).toBe('local')
    expect(c.description).toBe('TypeScript development skill')
    // Optional fields are undefined
    expect(c.version).toBeUndefined()
    expect(c.author).toBeUndefined()
    expect(c.tags).toBeUndefined()
    expect(c.verified).toBeUndefined()
  })

  test('full component includes all optional fields', () => {
    const c: Component = {
      type: 'mcp-server',
      name: 'context7',
      source: 'registry',
      description: 'Documentation retrieval server',
      version: '1.2.0',
      author: 'aRustyDev',
      url: 'https://github.com/aRustyDev/context7',
      tags: ['docs', 'retrieval'],
      installs: 1500,
      stars: 42,
      verified: true,
      namespace: 'arustydev',
      transport: 'stdio',
      configSchema: { port: { type: 'number', default: 3000 } },
      installedAt: '/home/user/.claude/mcp',
      installedAgents: ['default', 'research'],
      installMode: 'symlink',
      localPath: '/opt/mcp/context7',
    }
    expect(c.type).toBe('mcp-server')
    expect(c.version).toBe('1.2.0')
    expect(c.tags).toEqual(['docs', 'retrieval'])
    expect(c.installs).toBe(1500)
    expect(c.stars).toBe(42)
    expect(c.verified).toBe(true)
    expect(c.namespace).toBe('arustydev')
    expect(c.transport).toBe('stdio')
    expect(c.configSchema).toEqual({ port: { type: 'number', default: 3000 } })
    expect(c.installedAt).toBe('/home/user/.claude/mcp')
    expect(c.installedAgents).toEqual(['default', 'research'])
    expect(c.installMode).toBe('symlink')
    expect(c.localPath).toBe('/opt/mcp/context7')
  })

  test('installMode accepts only copy or symlink', () => {
    const copy: Component = {
      type: 'rule',
      name: 'no-any',
      source: 'local',
      description: 'Disallow any',
      installMode: 'copy',
    }
    const symlink: Component = {
      type: 'rule',
      name: 'no-any',
      source: 'local',
      description: 'Disallow any',
      installMode: 'symlink',
    }
    expect(copy.installMode).toBe('copy')
    expect(symlink.installMode).toBe('symlink')
  })
})

// ---------------------------------------------------------------------------
// SearchParams
// ---------------------------------------------------------------------------

describe('SearchParams', () => {
  test('requires only query', () => {
    const params: SearchParams = { query: 'typescript' }
    expect(params.query).toBe('typescript')
    expect(params.type).toBeUndefined()
    expect(params.limit).toBeUndefined()
    expect(params.page).toBeUndefined()
  })

  test('accepts all optional filters', () => {
    const params: SearchParams = {
      query: 'mcp',
      type: 'mcp-server',
      limit: 20,
      page: 2,
      agent: 'research',
      name: 'context7',
      namespace: 'arustydev',
      verified: true,
    }
    expect(params.type).toBe('mcp-server')
    expect(params.limit).toBe(20)
    expect(params.page).toBe(2)
    expect(params.agent).toBe('research')
    expect(params.name).toBe('context7')
    expect(params.namespace).toBe('arustydev')
    expect(params.verified).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// PaginatedResult
// ---------------------------------------------------------------------------

describe('PaginatedResult', () => {
  test('wraps items with pagination metadata', () => {
    const result: PaginatedResult<Component> = {
      items: [
        { type: 'skill', name: 'a', source: 'local', description: 'A skill' },
        { type: 'skill', name: 'b', source: 'local', description: 'B skill' },
      ],
      page: 1,
      pageSize: 10,
      hasMore: false,
    }
    expect(result.items).toHaveLength(2)
    expect(result.page).toBe(1)
    expect(result.pageSize).toBe(10)
    expect(result.hasMore).toBe(false)
    expect(result.total).toBeUndefined()
  })

  test('total is optional', () => {
    const result: PaginatedResult<string> = {
      items: ['x'],
      page: 1,
      pageSize: 5,
      hasMore: true,
      total: 100,
    }
    expect(result.total).toBe(100)
  })

  test('works with empty items', () => {
    const result: PaginatedResult<Component> = {
      items: [],
      page: 1,
      pageSize: 10,
      hasMore: false,
      total: 0,
    }
    expect(result.items).toHaveLength(0)
    expect(result.total).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// ProviderCapabilities
// ---------------------------------------------------------------------------

describe('ProviderCapabilities', () => {
  test('has all 8 operation categories', () => {
    const caps: ProviderCapabilities = {
      search: ['skill', 'mcp-server'],
      add: ['skill', 'mcp-server'],
      list: ['skill', 'mcp-server', 'agent'],
      remove: ['skill'],
      publish: [],
      info: ['skill', 'mcp-server'],
      outdated: ['skill'],
      update: ['skill'],
    }

    const keys = Object.keys(caps)
    expect(keys).toHaveLength(8)
    expect(keys).toContain('search')
    expect(keys).toContain('add')
    expect(keys).toContain('list')
    expect(keys).toContain('remove')
    expect(keys).toContain('publish')
    expect(keys).toContain('info')
    expect(keys).toContain('outdated')
    expect(keys).toContain('update')
  })

  test('capabilities can be empty arrays', () => {
    const caps: ProviderCapabilities = {
      search: [],
      add: [],
      list: [],
      remove: [],
      publish: [],
      info: [],
      outdated: [],
      update: [],
    }
    for (const key of Object.keys(caps) as (keyof ProviderCapabilities)[]) {
      expect(caps[key]).toHaveLength(0)
    }
  })

  test('capabilities arrays contain valid ComponentTypes', () => {
    const caps: ProviderCapabilities = {
      search: COMPONENT_TYPES,
      add: ['skill'],
      list: ['mcp-server', 'agent'],
      remove: ['plugin'],
      publish: ['skill'],
      info: COMPONENT_TYPES,
      outdated: ['skill', 'plugin'],
      update: ['skill', 'plugin'],
    }
    // Every entry in search should be a valid ComponentType
    for (const t of caps.search) {
      expect(isComponentType(t)).toBe(true)
    }
  })
})

// ---------------------------------------------------------------------------
// ComponentAddOptions
// ---------------------------------------------------------------------------

describe('ComponentAddOptions', () => {
  test('all fields are optional', () => {
    const opts: ComponentAddOptions = {}
    expect(opts.agents).toBeUndefined()
    expect(opts.copy).toBeUndefined()
    expect(opts.yes).toBeUndefined()
    expect(opts.cwd).toBeUndefined()
    expect(opts.global).toBeUndefined()
    expect(opts.client).toBeUndefined()
    expect(opts.config).toBeUndefined()
  })

  test('accepts all fields', () => {
    const opts: ComponentAddOptions = {
      agents: ['default', 'research'],
      copy: true,
      yes: true,
      cwd: '/tmp/project',
      global: false,
      client: 'claude-code',
      config: { port: 3000 },
    }
    expect(opts.agents).toEqual(['default', 'research'])
    expect(opts.copy).toBe(true)
    expect(opts.global).toBe(false)
    expect(opts.config).toEqual({ port: 3000 })
  })
})

// ---------------------------------------------------------------------------
// ComponentAddResult
// ---------------------------------------------------------------------------

describe('ComponentAddResult', () => {
  test('uses components (plural) as array of Component', () => {
    const result: ComponentAddResult = {
      ok: true,
      components: [
        {
          type: 'skill',
          name: 'ts-pro',
          source: 'registry',
          description: 'TS skill',
        },
        {
          type: 'rule',
          name: 'no-any',
          source: 'registry',
          description: 'No any rule',
        },
      ],
      installedTo: ['/home/user/.claude/skills', '/home/user/.claude/rules'],
      warnings: [],
    }
    expect(result.ok).toBe(true)
    expect(result.components).toHaveLength(2)
    expect(result.components[0].type).toBe('skill')
    expect(result.components[1].type).toBe('rule')
    expect(result.installedTo).toHaveLength(2)
    expect(result.warnings).toHaveLength(0)
    expect(result.error).toBeUndefined()
  })

  test('failure result includes error message', () => {
    const result: ComponentAddResult = {
      ok: false,
      components: [],
      installedTo: [],
      warnings: ['partial install'],
      error: 'Network timeout',
    }
    expect(result.ok).toBe(false)
    expect(result.error).toBe('Network timeout')
    expect(result.warnings).toEqual(['partial install'])
  })
})

// ---------------------------------------------------------------------------
// RemoveResult
// ---------------------------------------------------------------------------

describe('RemoveResult', () => {
  test('successful removal', () => {
    const result: RemoveResult = {
      ok: true,
      component: 'typescript-pro',
      removedFrom: ['/home/user/.claude/skills/typescript-pro'],
    }
    expect(result.ok).toBe(true)
    expect(result.component).toBe('typescript-pro')
    expect(result.removedFrom).toHaveLength(1)
    expect(result.error).toBeUndefined()
  })

  test('failed removal includes error', () => {
    const result: RemoveResult = {
      ok: false,
      component: 'nonexistent',
      removedFrom: [],
      error: 'Component not found',
    }
    expect(result.ok).toBe(false)
    expect(result.error).toBe('Component not found')
  })
})

// ---------------------------------------------------------------------------
// PublishOptions
// ---------------------------------------------------------------------------

describe('PublishOptions', () => {
  test('all fields are optional', () => {
    const opts: PublishOptions = {}
    expect(opts.name).toBeUndefined()
    expect(opts.namespace).toBeUndefined()
    expect(opts.apiKey).toBeUndefined()
    expect(opts.externalUrl).toBeUndefined()
    expect(opts.configSchema).toBeUndefined()
    expect(opts.bundleDir).toBeUndefined()
    expect(opts.dryRun).toBeUndefined()
    expect(opts.cwd).toBeUndefined()
  })

  test('accepts all fields', () => {
    const opts: PublishOptions = {
      name: 'arustydev/my-server',
      namespace: 'arustydev',
      apiKey: 'sk-test-123',
      externalUrl: 'https://mcp.example.com/sse',
      configSchema: { port: { type: 'number', default: 3000 } },
      bundleDir: '/tmp/build/dist',
      dryRun: true,
      cwd: '/home/user/project',
    }
    expect(opts.name).toBe('arustydev/my-server')
    expect(opts.namespace).toBe('arustydev')
    expect(opts.apiKey).toBe('sk-test-123')
    expect(opts.externalUrl).toBe('https://mcp.example.com/sse')
    expect(opts.configSchema).toEqual({ port: { type: 'number', default: 3000 } })
    expect(opts.bundleDir).toBe('/tmp/build/dist')
    expect(opts.dryRun).toBe(true)
    expect(opts.cwd).toBe('/home/user/project')
  })
})

// ---------------------------------------------------------------------------
// PublishResult
// ---------------------------------------------------------------------------

describe('PublishResult', () => {
  test('successful publish result', () => {
    const result: PublishResult = {
      ok: true,
      registryUrl: 'https://smithery.ai/server/arustydev/my-server',
      releaseId: 'rel-abc-123',
      status: 'published',
      warnings: [],
    }
    expect(result.ok).toBe(true)
    expect(result.status).toBe('published')
    expect(result.registryUrl).toBe('https://smithery.ai/server/arustydev/my-server')
    expect(result.releaseId).toBe('rel-abc-123')
    expect(result.error).toBeUndefined()
    expect(result.warnings).toHaveLength(0)
  })

  test('pending publish result', () => {
    const result: PublishResult = {
      ok: true,
      status: 'pending',
      warnings: ['Build queued, deployment in progress'],
    }
    expect(result.ok).toBe(true)
    expect(result.status).toBe('pending')
    expect(result.registryUrl).toBeUndefined()
    expect(result.warnings).toHaveLength(1)
  })

  test('failed publish result includes error', () => {
    const result: PublishResult = {
      ok: false,
      status: 'failed',
      error: 'Authentication failed: invalid API key',
      warnings: ['Config schema validation skipped'],
    }
    expect(result.ok).toBe(false)
    expect(result.status).toBe('failed')
    expect(result.error).toBe('Authentication failed: invalid API key')
    expect(result.warnings).toEqual(['Config schema validation skipped'])
  })

  test('status accepts only valid literal types', () => {
    const published: PublishResult = { ok: true, status: 'published', warnings: [] }
    const pending: PublishResult = { ok: true, status: 'pending', warnings: [] }
    const failed: PublishResult = { ok: false, status: 'failed', warnings: [] }
    expect(published.status).toBe('published')
    expect(pending.status).toBe('pending')
    expect(failed.status).toBe('failed')
  })
})

// ---------------------------------------------------------------------------
// ComponentProvider (structural typing)
// ---------------------------------------------------------------------------

describe('ComponentProvider', () => {
  test('can define a provider satisfying the interface', () => {
    // Structural check: an object literal that satisfies ComponentProvider
    const provider: ComponentProvider = {
      id: 'test-provider',
      displayName: 'Test Provider',
      capabilities: {
        search: ['skill'],
        add: ['skill'],
        list: ['skill'],
        remove: ['skill'],
        publish: [],
        info: ['skill'],
        outdated: [],
        update: [],
      },
      search: async () => ({
        ok: true as const,
        value: { items: [], page: 1, pageSize: 10, hasMore: false },
      }),
      add: async () => ({
        ok: true as const,
        value: { ok: true, components: [], installedTo: [], warnings: [] },
      }),
      list: async () => ({ ok: true as const, value: [] }),
      remove: async () => ({
        ok: true as const,
        value: { ok: true, component: 'x', removedFrom: [] },
      }),
      info: async () => ({
        ok: true as const,
        value: {
          type: 'skill' as const,
          name: 'x',
          source: 'test',
          description: 'test',
        },
      }),
      publish: async () => ({
        ok: true as const,
        value: { ok: true, status: 'published' as const, warnings: [] },
      }),
    }

    expect(provider.id).toBe('test-provider')
    expect(provider.displayName).toBe('Test Provider')
    expect(provider.capabilities.search).toEqual(['skill'])
  })

  test('provider methods return Result types', async () => {
    const provider: ComponentProvider = {
      id: 'mock',
      displayName: 'Mock',
      capabilities: {
        search: [],
        add: [],
        list: [],
        remove: [],
        publish: [],
        info: [],
        outdated: [],
        update: [],
      },
      search: async () => ({
        ok: false as const,
        error: {
          message: 'not implemented',
          code: 'E_NOT_IMPL',
          display: () => '',
        } as any,
      }),
      add: async () => ({
        ok: false as const,
        error: {
          message: 'not implemented',
          code: 'E_NOT_IMPL',
          display: () => '',
        } as any,
      }),
      list: async () => ({
        ok: false as const,
        error: {
          message: 'not implemented',
          code: 'E_NOT_IMPL',
          display: () => '',
        } as any,
      }),
      remove: async () => ({
        ok: false as const,
        error: {
          message: 'not implemented',
          code: 'E_NOT_IMPL',
          display: () => '',
        } as any,
      }),
      info: async () => ({
        ok: false as const,
        error: {
          message: 'not implemented',
          code: 'E_NOT_IMPL',
          display: () => '',
        } as any,
      }),
      publish: async () => ({
        ok: false as const,
        error: {
          message: 'not implemented',
          code: 'E_NOT_IMPL',
          display: () => '',
        } as any,
      }),
    }

    const result = await provider.search({ query: 'test' })
    expect(result.ok).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// toEntityType / toComponentType bridge
// ---------------------------------------------------------------------------

describe('toEntityType', () => {
  test('maps shared types correctly', () => {
    expect(toEntityType('skill')).toBe('skill')
    expect(toEntityType('agent')).toBe('agent')
    expect(toEntityType('plugin')).toBe('plugin')
    expect(toEntityType('rule')).toBe('rule')
    expect(toEntityType('command')).toBe('command')
    expect(toEntityType('mcp-server')).toBe('mcp_server')
    expect(toEntityType('output-style')).toBe('output_style')
  })

  test('returns undefined for placeholder types with no KG mapping', () => {
    expect(toEntityType('persona')).toBeUndefined()
    expect(toEntityType('lsp')).toBeUndefined()
    expect(toEntityType('mcp-client')).toBeUndefined()
    expect(toEntityType('mcp-tool')).toBeUndefined()
  })
})

describe('toComponentType', () => {
  test('maps shared types correctly', () => {
    expect(toComponentType('skill')).toBe('skill')
    expect(toComponentType('agent')).toBe('agent')
    expect(toComponentType('plugin')).toBe('plugin')
    expect(toComponentType('rule')).toBe('rule')
    expect(toComponentType('command')).toBe('command')
    expect(toComponentType('mcp_server')).toBe('mcp-server')
    expect(toComponentType('output_style')).toBe('output-style')
  })

  test('returns undefined for claude_md (KG-only type)', () => {
    expect(toComponentType('claude_md')).toBeUndefined()
  })
})

describe('EntityType <-> ComponentType round-trip', () => {
  test('round-trips correctly for all shared types', () => {
    const sharedComponentTypes: ComponentType[] = [
      'skill',
      'agent',
      'plugin',
      'rule',
      'command',
      'mcp-server',
      'output-style',
    ]
    for (const ct of sharedComponentTypes) {
      const et = toEntityType(ct)
      expect(et).toBeDefined()
      expect(toComponentType(et!)).toBe(ct)
    }
  })
})
