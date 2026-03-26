import { describe, expect, it } from 'bun:test'
import { err, ok } from '@agents/core/types'
import type {
  Component,
  ComponentAddResult,
  ComponentProvider,
  ProviderCapabilities,
} from '../../src/context/types'
import { ProviderManager } from '../../src/providers/manager'
import { SdkError } from '../../src/util/errors'

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

function makeFakeProvider(
  id: string,
  capabilities: Partial<ProviderCapabilities>,
  overrides?: Partial<ComponentProvider>
): ComponentProvider {
  const defaultCaps: ProviderCapabilities = {
    search: [],
    add: [],
    list: [],
    remove: [],
    publish: [],
    info: [],
    outdated: [],
    update: [],
  }
  return {
    id,
    displayName: id,
    capabilities: { ...defaultCaps, ...capabilities },
    search: async () => ok({ items: [], page: 1, pageSize: 10, hasMore: false, total: 0 }),
    add: async () => err(new SdkError('unsupported', 'E_PROVIDER_UNAVAILABLE')),
    list: async () => ok([]),
    remove: async () => err(new SdkError('unsupported', 'E_PROVIDER_UNAVAILABLE')),
    info: async () => err(new SdkError('unsupported', 'E_COMPONENT_NOT_FOUND')),
    publish: async () => err(new SdkError('unsupported', 'E_PROVIDER_UNAVAILABLE')),
    ...overrides,
  }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('ProviderManager', () => {
  describe('register / getProvider / providers', () => {
    it('registers and retrieves providers', () => {
      const manager = new ProviderManager()
      const p1 = makeFakeProvider('alpha', { search: ['skill'] })
      const p2 = makeFakeProvider('beta', { list: ['agent'] })

      manager.register(p1)
      manager.register(p2)

      expect(manager.getProvider('alpha')).toBe(p1)
      expect(manager.getProvider('beta')).toBe(p2)
      expect(manager.getProvider('gamma')).toBeUndefined()
      expect(manager.providers()).toHaveLength(2)
    })

    it('overwrites provider with same id', () => {
      const manager = new ProviderManager()
      const p1 = makeFakeProvider('alpha', { search: ['skill'] })
      const p2 = makeFakeProvider('alpha', { search: ['agent'] })

      manager.register(p1)
      manager.register(p2)

      expect(manager.providers()).toHaveLength(1)
      expect(manager.getProvider('alpha')).toBe(p2)
    })
  })

  describe('findProviders', () => {
    it('routes by capability and type', () => {
      const manager = new ProviderManager()
      manager.register(makeFakeProvider('a', { search: ['skill'], list: ['skill'] }))
      manager.register(makeFakeProvider('b', { search: ['agent'] }))
      manager.register(makeFakeProvider('c', { list: ['skill', 'agent'] }))

      expect(manager.findProviders('search', 'skill').map((p) => p.id)).toEqual(['a'])
      expect(manager.findProviders('search', 'agent').map((p) => p.id)).toEqual(['b'])
      expect(manager.findProviders('list', 'skill').map((p) => p.id)).toEqual(['a', 'c'])
      expect(manager.findProviders('list', 'agent').map((p) => p.id)).toEqual(['c'])
      expect(manager.findProviders('add', 'skill')).toHaveLength(0)
    })
  })

  describe('search', () => {
    it('fans out to all providers and deduplicates', async () => {
      const comp1 = makeComponent({ name: 'skill-a', source: 'local' })
      const comp2 = makeComponent({ name: 'skill-b', source: 'github' })
      const comp1dup = makeComponent({ name: 'skill-a', source: 'local' }) // duplicate

      const manager = new ProviderManager()
      manager.register(
        makeFakeProvider(
          'p1',
          { search: ['skill'] },
          {
            search: async () =>
              ok({ items: [comp1, comp2], page: 1, pageSize: 10, hasMore: false, total: 2 }),
          }
        )
      )
      manager.register(
        makeFakeProvider(
          'p2',
          { search: ['skill'] },
          {
            search: async () =>
              ok({ items: [comp1dup], page: 1, pageSize: 10, hasMore: false, total: 1 }),
          }
        )
      )

      const result = await manager.search({ query: '', type: 'skill' })
      expect(result.ok).toBe(true)
      if (result.ok) {
        expect(result.value.items).toHaveLength(2)
        expect(result.value.items.map((i) => i.name)).toEqual(['skill-a', 'skill-b'])
      }
    })

    it('returns empty page when no providers match', async () => {
      const manager = new ProviderManager()
      const result = await manager.search({ query: 'test', type: 'skill' })
      expect(result.ok).toBe(true)
      if (result.ok) {
        expect(result.value.items).toHaveLength(0)
        expect(result.value.total).toBe(0)
      }
    })

    it('handles provider errors gracefully', async () => {
      const comp = makeComponent()
      const manager = new ProviderManager()
      manager.register(
        makeFakeProvider(
          'good',
          { search: ['skill'] },
          {
            search: async () =>
              ok({ items: [comp], page: 1, pageSize: 10, hasMore: false, total: 1 }),
          }
        )
      )
      manager.register(
        makeFakeProvider(
          'bad',
          { search: ['skill'] },
          {
            search: async () => {
              throw new Error('boom')
            },
          }
        )
      )

      const result = await manager.search({ query: '', type: 'skill' })
      expect(result.ok).toBe(true)
      if (result.ok) {
        // Should still have results from the good provider
        expect(result.value.items).toHaveLength(1)
      }
    })
  })

  describe('add', () => {
    it('errors when no provider supports operation', async () => {
      const manager = new ProviderManager()
      const result = await manager.add('source', 'skill', {})
      expect(result.ok).toBe(false)
    })

    it('delegates to the first matching provider', async () => {
      const manager = new ProviderManager()
      const addResult: ComponentAddResult = {
        ok: true,
        components: [makeComponent()],
        installedTo: ['/test'],
        warnings: [],
      }
      manager.register(
        makeFakeProvider(
          'local',
          { add: ['skill'] },
          {
            add: async () => ok(addResult),
          }
        )
      )

      const result = await manager.add('source', 'skill', {})
      expect(result.ok).toBe(true)
      if (result.ok) {
        expect(result.value.components).toHaveLength(1)
      }
    })
  })

  describe('info', () => {
    it('returns error when no provider has the component', async () => {
      const manager = new ProviderManager()
      manager.register(
        makeFakeProvider(
          'p1',
          { info: ['skill'] },
          {
            info: async () => err(new SdkError('not found', 'E_COMPONENT_NOT_FOUND')),
          }
        )
      )

      const result = await manager.info('missing', 'skill')
      expect(result.ok).toBe(false)
    })

    it('returns component from first successful provider', async () => {
      const comp = makeComponent({ name: 'found-skill' })
      const manager = new ProviderManager()
      manager.register(
        makeFakeProvider(
          'p1',
          { info: ['skill'] },
          {
            info: async () => err(new SdkError('not found', 'E_COMPONENT_NOT_FOUND')),
          }
        )
      )
      manager.register(
        makeFakeProvider(
          'p2',
          { info: ['skill'] },
          {
            info: async () => ok(comp),
          }
        )
      )

      const result = await manager.info('found-skill', 'skill')
      expect(result.ok).toBe(true)
      if (result.ok) {
        expect(result.value.name).toBe('found-skill')
      }
    })
  })

  describe('remove', () => {
    it('errors when no provider supports removing type', async () => {
      const manager = new ProviderManager()
      const result = await manager.remove('test', 'skill')
      expect(result.ok).toBe(false)
    })
  })

  describe('publish', () => {
    it('errors when no provider supports publishing type', async () => {
      const manager = new ProviderManager()
      const result = await manager.publish('skill', {})
      expect(result.ok).toBe(false)
    })
  })
})
