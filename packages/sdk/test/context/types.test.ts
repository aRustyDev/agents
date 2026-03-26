import { describe, expect, it } from 'bun:test'
import {
  COMPONENT_TYPE_META,
  COMPONENT_TYPES,
  getActiveTypes,
  isComponentType,
  parseComponentType,
} from '../../src/context/types'

describe('COMPONENT_TYPES', () => {
  it('has 12 entries', () => {
    expect(COMPONENT_TYPES).toHaveLength(12)
  })

  it('contains all expected types', () => {
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
    for (const t of expected) {
      expect(COMPONENT_TYPES).toContain(t)
    }
  })
})

describe('isComponentType', () => {
  it('returns true for valid types', () => {
    expect(isComponentType('skill')).toBe(true)
    expect(isComponentType('mcp-server')).toBe(true)
    expect(isComponentType('output-style')).toBe(true)
  })

  it('returns false for invalid types', () => {
    expect(isComponentType('banana')).toBe(false)
    expect(isComponentType('SKILL')).toBe(false)
    expect(isComponentType('')).toBe(false)
  })
})

describe('parseComponentType', () => {
  it('normalizes underscores to hyphens', () => {
    expect(parseComponentType('mcp_server')).toBe('mcp-server')
    expect(parseComponentType('output_style')).toBe('output-style')
    expect(parseComponentType('mcp_client')).toBe('mcp-client')
  })

  it('normalizes case', () => {
    expect(parseComponentType('SKILL')).toBe('skill')
    expect(parseComponentType('Plugin')).toBe('plugin')
    expect(parseComponentType('MCP-SERVER')).toBe('mcp-server')
  })

  it('normalizes spaces to hyphens', () => {
    expect(parseComponentType('mcp server')).toBe('mcp-server')
    expect(parseComponentType('output style')).toBe('output-style')
  })

  it('returns undefined for invalid types', () => {
    expect(parseComponentType('banana')).toBeUndefined()
    expect(parseComponentType('')).toBeUndefined()
  })
})

describe('getActiveTypes', () => {
  it('returns non-placeholder types', () => {
    const active = getActiveTypes()
    // placeholder types: persona, lsp, mcp-client, mcp-tool, hook
    expect(active).not.toContain('persona')
    expect(active).not.toContain('lsp')
    expect(active).not.toContain('mcp-client')
    expect(active).not.toContain('mcp-tool')
    expect(active).not.toContain('hook')
  })

  it('includes implemented types', () => {
    const active = getActiveTypes()
    expect(active).toContain('skill')
    expect(active).toContain('agent')
    expect(active).toContain('plugin')
    expect(active).toContain('rule')
    expect(active).toContain('mcp-server')
    expect(active).toContain('command')
    expect(active).toContain('output-style')
  })

  it('returns 7 active types', () => {
    expect(getActiveTypes()).toHaveLength(7)
  })
})

describe('COMPONENT_TYPE_META', () => {
  it('has metadata for every type', () => {
    for (const type of COMPONENT_TYPES) {
      expect(COMPONENT_TYPE_META[type]).toBeDefined()
      expect(COMPONENT_TYPE_META[type].name).toBe(type)
    }
  })
})
