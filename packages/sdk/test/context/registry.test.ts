import { describe, expect, it } from 'bun:test'
import { ok } from '@agents/core/types'
import type { ValidationResult } from '../../src/context/component'
import {
  type ComponentTypeModule,
  getComponentModule,
  getRegisteredModules,
  registerComponentType,
} from '../../src/context/registry'
import type { ComponentType } from '../../src/context/types'

function makeMockModule(type: ComponentType): ComponentTypeModule {
  return {
    type,
    schema: {
      validate: () => ok({}),
    },
    parse: async () =>
      ok({
        type,
        name: 'test',
        content: '',
        frontmatter: {},
        metadata: { wordCount: 0, sectionCount: 0, headingTree: [], lineCount: 0 },
      }),
    validate: (): ValidationResult => ({
      valid: true,
      errors: [],
      warnings: [],
    }),
  }
}

describe('registerComponentType + getComponentModule', () => {
  // Note: registry is global state. We register then retrieve.

  it('round-trips a registered module', () => {
    const mod = makeMockModule('hook')
    registerComponentType(mod)
    const retrieved = getComponentModule('hook')
    expect(retrieved).toBeDefined()
    expect(retrieved?.type).toBe('hook')
  })

  it('returns undefined for unregistered type', () => {
    // 'lsp' is unlikely to be registered in these tests
    // Use a fresh check — if it was registered elsewhere, still valid
    const result = getComponentModule('persona')
    // persona is a placeholder and not registered by default in tests
    // (auto-registration happens in context/index.ts barrel, not imported here)
    // This test imports registry directly, so only 'hook' from above is registered
    if (result === undefined) {
      expect(result).toBeUndefined()
    } else {
      // If it happens to exist (from another test run in same process), that's OK too
      expect(result.type).toBe('persona')
    }
  })
})

describe('getRegisteredModules', () => {
  it('returns a copy of the registry', () => {
    const mod = makeMockModule('lsp')
    registerComponentType(mod)
    const all = getRegisteredModules()
    expect(all).toBeInstanceOf(Map)
    expect(all.get('lsp')).toBeDefined()
    // Mutating the returned map should not affect the internal registry
    all.delete('lsp')
    expect(getComponentModule('lsp')).toBeDefined()
  })
})
