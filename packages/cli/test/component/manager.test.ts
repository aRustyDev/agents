import { describe, expect, test } from 'bun:test'
import { ComponentManager } from '@agents/core/component/manager'
import type {
  Component,
  ComponentAddOptions,
  ComponentAddResult,
  ComponentProvider,
  ComponentType,
  PaginatedResult,
  ProviderCapabilities,
  PublishOptions,
  PublishResult,
  RemoveResult,
  SearchParams,
} from '@agents/core/component/types'
import { CliError, err, ok, type Result } from '@agents/core/types'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeComponent(overrides: Partial<Component> = {}): Component {
  return {
    type: 'skill',
    name: 'test-skill',
    source: 'local',
    description: 'A test skill',
    ...overrides,
  }
}

function makeCapabilities(overrides: Partial<ProviderCapabilities> = {}): ProviderCapabilities {
  return {
    search: ['skill'] as ComponentType[],
    add: ['skill'] as ComponentType[],
    list: ['skill'] as ComponentType[],
    remove: ['skill'] as ComponentType[],
    publish: [],
    info: ['skill'] as ComponentType[],
    outdated: [],
    update: [],
    ...overrides,
  }
}

function mockProvider(
  id: string,
  opts: {
    searchResults?: Component[]
    listResults?: Component[]
    infoResult?: Component | null
    addResult?: ComponentAddResult
    removeResult?: RemoveResult
    publishResult?: PublishResult
    capabilities?: Partial<ProviderCapabilities>
    searchError?: boolean
  } = {}
): ComponentProvider {
  const searchItems = opts.searchResults ?? []
  const listItems = opts.listResults ?? []
  const capabilities = makeCapabilities(opts.capabilities)

  return {
    id,
    displayName: `Mock ${id}`,
    capabilities,

    async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
      if (opts.searchError) {
        return err(new CliError('provider error', 'E_SEARCH'))
      }
      return ok({
        items: searchItems,
        page: params.page ?? 1,
        pageSize: params.limit ?? 10,
        hasMore: false,
        total: searchItems.length,
      })
    },

    async add(_source: string, _opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
      if (opts.addResult) return ok(opts.addResult)
      return ok({
        ok: true,
        components: [],
        installedTo: ['/tmp/test'],
        warnings: [],
      })
    },

    async list(
      _type: ComponentType,
      _opts?: { cwd?: string; agent?: string }
    ): Promise<Result<Component[]>> {
      return ok(listItems)
    },

    async remove(
      _name: string,
      _type: ComponentType,
      _opts?: { cwd?: string; agent?: string }
    ): Promise<Result<RemoveResult>> {
      if (opts.removeResult) return ok(opts.removeResult)
      return ok({ ok: true, component: _name, removedFrom: ['/tmp/test'] })
    },

    async info(
      name: string,
      type: ComponentType,
      _opts?: { cwd?: string }
    ): Promise<Result<Component>> {
      if (opts.infoResult) return ok(opts.infoResult)
      if (opts.infoResult === null) {
        return err(new CliError(`Not found: ${name}`, 'E_NOT_FOUND'))
      }
      return ok(makeComponent({ name, type }))
    },

    async publish(_type: ComponentType, _opts: PublishOptions): Promise<Result<PublishResult>> {
      if (opts.publishResult) return ok(opts.publishResult)
      return err(new CliError('publish not supported', 'E_UNSUPPORTED'))
    },
  }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ComponentManager', () => {
  // -------------------------------------------------------------------------
  // register / getProvider / providers
  // -------------------------------------------------------------------------

  describe('register / getProvider / providers', () => {
    test('register and retrieve a provider', () => {
      const mgr = new ComponentManager()
      const p = mockProvider('local')
      mgr.register(p)
      expect(mgr.getProvider('local')).toBe(p)
    })

    test('getProvider returns undefined for unknown id', () => {
      const mgr = new ComponentManager()
      expect(mgr.getProvider('nope')).toBeUndefined()
    })

    test('providers returns all registered providers', () => {
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a'))
      mgr.register(mockProvider('b'))
      const ids = mgr.providers().map((p) => p.id)
      expect(ids).toEqual(['a', 'b'])
    })

    test('re-registering same id replaces provider', () => {
      const mgr = new ComponentManager()
      const p1 = mockProvider('a')
      const p2 = mockProvider('a')
      mgr.register(p1)
      mgr.register(p2)
      expect(mgr.providers()).toHaveLength(1)
      expect(mgr.getProvider('a')).toBe(p2)
    })
  })

  // -------------------------------------------------------------------------
  // findProviders
  // -------------------------------------------------------------------------

  describe('findProviders', () => {
    test('returns matching providers', () => {
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { capabilities: { search: ['skill'] } }))
      mgr.register(mockProvider('b', { capabilities: { search: ['mcp-server'] } }))
      const found = mgr.findProviders('search', 'skill')
      expect(found).toHaveLength(1)
      expect(found[0]?.id).toBe('a')
    })

    test('skips providers that do not support the type', () => {
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { capabilities: { add: ['plugin'] } }))
      const found = mgr.findProviders('add', 'skill')
      expect(found).toHaveLength(0)
    })

    test('returns multiple matching providers', () => {
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { capabilities: { list: ['skill'] } }))
      mgr.register(mockProvider('b', { capabilities: { list: ['skill'] } }))
      const found = mgr.findProviders('list', 'skill')
      expect(found).toHaveLength(2)
    })
  })

  // -------------------------------------------------------------------------
  // search
  // -------------------------------------------------------------------------

  describe('search', () => {
    test('aggregates across providers', async () => {
      const mgr = new ComponentManager()
      mgr.register(
        mockProvider('a', {
          searchResults: [makeComponent({ name: 'alpha', source: 'a' })],
        })
      )
      mgr.register(
        mockProvider('b', {
          searchResults: [makeComponent({ name: 'beta', source: 'b' })],
        })
      )
      const result = await mgr.search({ query: 'test' })
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.items).toHaveLength(2)
      const names = result.value.items.map((c) => c.name)
      expect(names).toContain('alpha')
      expect(names).toContain('beta')
    })

    test('filters by type', async () => {
      const mgr = new ComponentManager()
      mgr.register(
        mockProvider('a', {
          capabilities: { search: ['skill', 'mcp-server'] },
          searchResults: [
            makeComponent({ name: 'sk', type: 'skill', source: 'a' }),
            makeComponent({ name: 'mcp', type: 'mcp-server', source: 'a' }),
          ],
        })
      )
      const result = await mgr.search({ query: 'test', type: 'skill' })
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.items).toHaveLength(1)
      expect(result.value.items[0]?.name).toBe('sk')
    })

    test('skips providers that do not support the type', async () => {
      const mgr = new ComponentManager()
      mgr.register(
        mockProvider('skill-only', {
          capabilities: { search: ['skill'] },
          searchResults: [makeComponent({ name: 'from-skill-provider', source: 'so' })],
        })
      )
      mgr.register(
        mockProvider('mcp-only', {
          capabilities: { search: ['mcp-server'] },
          searchResults: [
            makeComponent({
              name: 'from-mcp-provider',
              type: 'mcp-server',
              source: 'mo',
            }),
          ],
        })
      )
      const result = await mgr.search({ query: 'test', type: 'skill' })
      expect(result.ok).toBe(true)
      if (!result.ok) return
      // Only the skill-only provider should be queried
      expect(result.value.items).toHaveLength(1)
      expect(result.value.items[0]?.name).toBe('from-skill-provider')
    })

    test('continues when one provider fails', async () => {
      const mgr = new ComponentManager()
      mgr.register(
        mockProvider('failing', {
          searchError: true,
        })
      )
      mgr.register(
        mockProvider('working', {
          searchResults: [makeComponent({ name: 'good', source: 'w' })],
        })
      )
      const result = await mgr.search({ query: 'test' })
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.items).toHaveLength(1)
      expect(result.value.items[0]?.name).toBe('good')
    })

    test('deduplicates by type:name:source', async () => {
      const shared = makeComponent({
        name: 'dupe',
        type: 'skill',
        source: 'registry',
      })
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { searchResults: [shared] }))
      mgr.register(mockProvider('b', { searchResults: [shared] }))
      const result = await mgr.search({ query: 'test' })
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.items).toHaveLength(1)
    })

    test('paginates correctly', async () => {
      const items = Array.from({ length: 5 }, (_, i) =>
        makeComponent({ name: `item-${i}`, source: `s${i}` })
      )
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { searchResults: items }))

      const result = await mgr.search({ query: 'test', page: 2, limit: 2 })
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.items).toHaveLength(2)
      expect(result.value.items[0]?.name).toBe('item-2')
      expect(result.value.items[1]?.name).toBe('item-3')
      expect(result.value.page).toBe(2)
      expect(result.value.pageSize).toBe(2)
      expect(result.value.hasMore).toBe(true)
      expect(result.value.total).toBe(5)
    })

    test('returns empty when no providers match', async () => {
      const mgr = new ComponentManager()
      const result = await mgr.search({ query: 'test', type: 'skill' })
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.items).toEqual([])
      expect(result.value.hasMore).toBe(false)
      expect(result.value.total).toBe(0)
    })
  })

  // -------------------------------------------------------------------------
  // add
  // -------------------------------------------------------------------------

  describe('add', () => {
    test('routes to first capable provider', async () => {
      const addResult: ComponentAddResult = {
        ok: true,
        components: [makeComponent({ name: 'added' })],
        installedTo: ['/agents/default'],
        warnings: [],
      }
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { addResult }))
      const result = await mgr.add('gh:user/skill', 'skill', {})
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.components[0]?.name).toBe('added')
    })

    test('returns E_NO_PROVIDER when none support the type', async () => {
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { capabilities: { add: ['mcp-server'] } }))
      const result = await mgr.add('gh:user/skill', 'skill', {})
      expect(result.ok).toBe(false)
      if (result.ok) return
      expect(result.error.code).toBe('E_NO_PROVIDER')
      expect(result.error.message).toContain('skill')
    })
  })

  // -------------------------------------------------------------------------
  // list
  // -------------------------------------------------------------------------

  describe('list', () => {
    test('aggregates across providers', async () => {
      const mgr = new ComponentManager()
      mgr.register(
        mockProvider('a', {
          listResults: [makeComponent({ name: 'a1', source: 'a' })],
        })
      )
      mgr.register(
        mockProvider('b', {
          listResults: [makeComponent({ name: 'b1', source: 'b' })],
        })
      )
      const result = await mgr.list('skill')
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value).toHaveLength(2)
      const names = result.value.map((c) => c.name)
      expect(names).toContain('a1')
      expect(names).toContain('b1')
    })

    test('ignores provider errors', async () => {
      const mgr = new ComponentManager()

      // Create a provider whose list() returns an error
      const failingProvider = mockProvider('failing', {
        listResults: [], // won't be used
      })
      // Override list to return error
      failingProvider.list = async () => err(new CliError('disk error', 'E_IO'))

      mgr.register(failingProvider)
      mgr.register(
        mockProvider('working', {
          listResults: [makeComponent({ name: 'survivor', source: 'w' })],
        })
      )

      const result = await mgr.list('skill')
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value).toHaveLength(1)
      expect(result.value[0]?.name).toBe('survivor')
    })
  })

  // -------------------------------------------------------------------------
  // info
  // -------------------------------------------------------------------------

  describe('info', () => {
    test('returns first successful result', async () => {
      const mgr = new ComponentManager()

      // First provider fails
      const failProvider = mockProvider('fail', { infoResult: null })
      mgr.register(failProvider)

      // Second provider succeeds
      const successComponent = makeComponent({
        name: 'found',
        source: 'registry',
      })
      mgr.register(mockProvider('success', { infoResult: successComponent }))

      const result = await mgr.info('found', 'skill')
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.name).toBe('found')
      expect(result.value.source).toBe('registry')
    })

    test('returns E_NOT_FOUND when all fail', async () => {
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { infoResult: null }))
      mgr.register(mockProvider('b', { infoResult: null }))
      const result = await mgr.info('ghost', 'skill')
      expect(result.ok).toBe(false)
      if (result.ok) return
      expect(result.error.code).toBe('E_NOT_FOUND')
      expect(result.error.message).toContain('ghost')
      expect(result.error.message).toContain('skill')
    })
  })

  // -------------------------------------------------------------------------
  // remove
  // -------------------------------------------------------------------------

  describe('remove', () => {
    test('routes to first capable provider', async () => {
      const removeResult: RemoveResult = {
        ok: true,
        component: 'old-skill',
        removedFrom: ['/agents/default'],
      }
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { removeResult }))
      const result = await mgr.remove('old-skill', 'skill')
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.component).toBe('old-skill')
      expect(result.value.removedFrom).toEqual(['/agents/default'])
    })

    test('returns E_NO_PROVIDER when none support the type', async () => {
      const mgr = new ComponentManager()
      mgr.register(mockProvider('a', { capabilities: { remove: ['mcp-server'] } }))
      const result = await mgr.remove('some-skill', 'skill')
      expect(result.ok).toBe(false)
      if (result.ok) return
      expect(result.error.code).toBe('E_NO_PROVIDER')
      expect(result.error.message).toContain('skill')
    })
  })

  // -------------------------------------------------------------------------
  // publish
  // -------------------------------------------------------------------------

  describe('publish', () => {
    test('routes to capable provider', async () => {
      const publishResult: PublishResult = {
        ok: true,
        registryUrl: 'https://smithery.ai/server/test-server',
        releaseId: 'rel-123',
        status: 'published',
        warnings: [],
      }
      const mgr = new ComponentManager()
      mgr.register(
        mockProvider('pub-provider', {
          capabilities: { publish: ['mcp-server'] },
          publishResult,
        })
      )
      const result = await mgr.publish('mcp-server', { name: 'test-server' })
      expect(result.ok).toBe(true)
      if (!result.ok) return
      expect(result.value.status).toBe('published')
      expect(result.value.registryUrl).toBe('https://smithery.ai/server/test-server')
      expect(result.value.releaseId).toBe('rel-123')
    })

    test('returns E_NO_PROVIDER when none registered', async () => {
      const mgr = new ComponentManager()
      const result = await mgr.publish('mcp-server', {})
      expect(result.ok).toBe(false)
      if (result.ok) return
      expect(result.error.code).toBe('E_NO_PROVIDER')
      expect(result.error.message).toContain('mcp-server')
    })

    test('returns E_NO_PROVIDER when no provider supports the type', async () => {
      const mgr = new ComponentManager()
      mgr.register(
        mockProvider('a', {
          capabilities: { publish: ['skill'] },
        })
      )
      const result = await mgr.publish('mcp-server', { name: 'test' })
      expect(result.ok).toBe(false)
      if (result.ok) return
      expect(result.error.code).toBe('E_NO_PROVIDER')
    })
  })
})
