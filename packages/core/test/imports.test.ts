import { describe, expect, test } from 'bun:test'

describe('@agents/core barrel exports', () => {
  test('exports Result type and helpers', async () => {
    const mod = await import('@agents/core/types')
    expect(mod.ok).toBeDefined()
    expect(mod.err).toBeDefined()
    expect(mod.CliError).toBeDefined()
  })

  test('exports ComponentType system', async () => {
    const mod = await import('@agents/core/component/types')
    expect(mod.COMPONENT_TYPES).toBeDefined()
    expect(mod.parseComponentType).toBeDefined()
  })

  test('exports file-io', async () => {
    const mod = await import('@agents/core/file-io')
    expect(mod.readTextFile).toBeDefined()
  })

  test('exports config', async () => {
    const mod = await import('@agents/core/config')
    expect(mod.loadConfig).toBeDefined()
  })

  test('exports output', async () => {
    const mod = await import('@agents/core/output')
    expect(mod.createOutput).toBeDefined()
  })

  test('exports hash', async () => {
    const mod = await import('@agents/core/hash')
    expect(mod.hashDirectory).toBeDefined()
    expect(mod.computeHash).toBeDefined()
  })

  test('exports uuid', async () => {
    const mod = await import('@agents/core/uuid')
    expect(mod.uuid7).toBeDefined()
    expect(mod.uuid5).toBeDefined()
  })

  test('exports runtime', async () => {
    const mod = await import('@agents/core/runtime')
    expect(mod.currentDir).toBeDefined()
    expect(mod.readText).toBeDefined()
  })

  test('exports schemas', async () => {
    const mod = await import('@agents/core/schemas')
    expect(mod.LockfileV1).toBeDefined()
  })

  test('exports git', async () => {
    const mod = await import('@agents/core/git')
    expect(mod.cloneRepo).toBeDefined()
    expect(mod.lsRemote).toBeDefined()
  })

  test('exports github', async () => {
    const mod = await import('@agents/core/github')
    expect(mod.parseRepo).toBeDefined()
    expect(mod.GitHubTokenProvider).toBeDefined()
  })

  test('exports source-parser', async () => {
    const mod = await import('@agents/core/source-parser')
    expect(mod.parseSource).toBeDefined()
  })

  test('exports component/manager', async () => {
    const mod = await import('@agents/core/component/manager')
    expect(mod.ComponentManager).toBeDefined()
  })

  test('exports component/pagination', async () => {
    const mod = await import('@agents/core/component/pagination')
    expect(mod.paginateArray).toBeDefined()
    expect(mod.clampPage).toBeDefined()
  })

  test('barrel exports all modules', async () => {
    const mod = await import('@agents/core')
    // types
    expect(mod.ok).toBeDefined()
    expect(mod.err).toBeDefined()
    expect(mod.CliError).toBeDefined()
    // file-io
    expect(mod.readTextFile).toBeDefined()
    // config
    expect(mod.loadConfig).toBeDefined()
    // output
    expect(mod.createOutput).toBeDefined()
    // hash
    expect(mod.hashDirectory).toBeDefined()
    // uuid
    expect(mod.uuid7).toBeDefined()
    // runtime
    expect(mod.currentDir).toBeDefined()
    // schemas
    expect(mod.LockfileV1).toBeDefined()
    // component
    expect(mod.COMPONENT_TYPES).toBeDefined()
    expect(mod.ComponentManager).toBeDefined()
    // git
    expect(mod.cloneRepo).toBeDefined()
    // github
    expect(mod.parseRepo).toBeDefined()
    // source-parser
    expect(mod.parseSource).toBeDefined()
  })
})
