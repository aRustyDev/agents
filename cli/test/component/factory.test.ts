import { describe, expect, test } from 'bun:test'
import { createComponentManager } from '../../lib/component/factory'

describe('createComponentManager', () => {
  test('returns a ComponentManager', () => {
    const manager = createComponentManager()
    expect(manager).toBeDefined()
    expect(typeof manager.search).toBe('function')
    expect(typeof manager.add).toBe('function')
    expect(typeof manager.list).toBe('function')
    expect(typeof manager.remove).toBe('function')
    expect(typeof manager.info).toBe('function')
    expect(typeof manager.publish).toBe('function')
  })

  test('has 7 providers registered', () => {
    const manager = createComponentManager()
    expect(manager.providers()).toHaveLength(7)
  })

  test('has local provider for skills', () => {
    const manager = createComponentManager()
    expect(manager.getProvider('local')).toBeDefined()
    expect(manager.getProvider('local')!.capabilities.search).toContain('skill')
  })

  test('has local-agent provider', () => {
    const manager = createComponentManager()
    expect(manager.getProvider('local-agent')).toBeDefined()
    expect(manager.getProvider('local-agent')!.capabilities.search).toContain('agent')
  })

  test('has local-plugin provider', () => {
    const manager = createComponentManager()
    expect(manager.getProvider('local-plugin')).toBeDefined()
    expect(manager.getProvider('local-plugin')!.capabilities.search).toContain('plugin')
  })

  test('has local-rule provider', () => {
    const manager = createComponentManager()
    expect(manager.getProvider('local-rule')).toBeDefined()
    expect(manager.getProvider('local-rule')!.capabilities.search).toContain('rule')
  })

  test('has local-command provider', () => {
    const manager = createComponentManager()
    expect(manager.getProvider('local-command')).toBeDefined()
    expect(manager.getProvider('local-command')!.capabilities.search).toContain('command')
  })

  test('has local-output-style provider', () => {
    const manager = createComponentManager()
    expect(manager.getProvider('local-output-style')).toBeDefined()
    expect(manager.getProvider('local-output-style')!.capabilities.search).toContain('output_style')
  })

  test('has smithery provider for mcp_server', () => {
    const manager = createComponentManager()
    expect(manager.getProvider('smithery')).toBeDefined()
    expect(manager.getProvider('smithery')!.capabilities.search).toContain('mcp_server')
  })

  test('findProviders routes skill search to local', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('search', 'skill')
    expect(providers.length).toBeGreaterThanOrEqual(1)
    expect(providers.some((p) => p.id === 'local')).toBe(true)
  })

  test('findProviders routes mcp_server search to smithery', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('search', 'mcp_server')
    expect(providers.some((p) => p.id === 'smithery')).toBe(true)
  })

  test('findProviders routes agent search to local-agent', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('search', 'agent')
    expect(providers.some((p) => p.id === 'local-agent')).toBe(true)
  })

  test('findProviders routes plugin search to local-plugin', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('search', 'plugin')
    expect(providers.some((p) => p.id === 'local-plugin')).toBe(true)
  })

  test('findProviders routes rule search to local-rule', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('search', 'rule')
    expect(providers.some((p) => p.id === 'local-rule')).toBe(true)
  })

  test('findProviders routes command search to local-command', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('search', 'command')
    expect(providers.some((p) => p.id === 'local-command')).toBe(true)
  })

  test('findProviders routes output_style search to local-output-style', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('search', 'output_style')
    expect(providers.some((p) => p.id === 'local-output-style')).toBe(true)
  })

  test('accepts cwd option', () => {
    const manager = createComponentManager({ cwd: '/tmp/test' })
    expect(manager.providers()).toHaveLength(7)
  })

  test('accepts smitheryBaseUrl option', () => {
    const manager = createComponentManager({ smitheryBaseUrl: 'https://custom.api.com' })
    const smithery = manager.getProvider('smithery')
    expect(smithery).toBeDefined()
  })

  test('findProviders routes publish mcp_server to smithery', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('publish', 'mcp_server')
    expect(providers.some((p) => p.id === 'smithery')).toBe(true)
  })

  test('local provider supports add for skill', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('add', 'skill')
    expect(providers.some((p) => p.id === 'local')).toBe(true)
  })

  test('local provider supports remove for skill', () => {
    const manager = createComponentManager()
    const providers = manager.findProviders('remove', 'skill')
    expect(providers.some((p) => p.id === 'local')).toBe(true)
  })

  test('provider ids are unique', () => {
    const manager = createComponentManager()
    const ids = manager.providers().map((p) => p.id)
    expect(new Set(ids).size).toBe(ids.length)
  })
})
