import { describe, expect, test } from 'bun:test'

describe('component command tree', () => {
  test('exports a command with subCommands', async () => {
    const mod = await import('../../src/commands/component')
    expect(mod.default).toBeDefined()
    expect(mod.default.subCommands).toBeDefined()
  })

  test('has search and list subcommands', async () => {
    const mod = await import('../../src/commands/component')
    const subs = mod.default.subCommands ?? {}
    expect(subs.search).toBeDefined()
    expect(subs.search.meta?.name).toBe('search')
    expect(subs.search.meta?.description?.length).toBeGreaterThan(0)
    expect(subs.list).toBeDefined()
    expect(subs.list.meta?.name).toBe('list')
    expect(subs.list.meta?.description?.length).toBeGreaterThan(0)
  })

  test('search has query, type, limit, page args', async () => {
    const mod = await import('../../src/commands/component')
    const search = (mod.default.subCommands ?? {}).search
    expect(search.args?.query).toBeDefined()
    expect(search.args?.type).toBeDefined()
    expect(search.args?.limit).toBeDefined()
    expect(search.args?.page).toBeDefined()
  })

  test('list has type arg', async () => {
    const mod = await import('../../src/commands/component')
    const list = (mod.default.subCommands ?? {}).list
    expect(list.args?.type).toBeDefined()
  })

  test('both subcommands inherit globalArgs', async () => {
    const mod = await import('../../src/commands/component')
    const subs = mod.default.subCommands ?? {}
    for (const name of ['search', 'list']) {
      expect(subs[name].args?.json).toBeDefined()
      expect(subs[name].args?.quiet).toBeDefined()
      expect(subs[name].args?.verbose).toBeDefined()
    }
  })

  test('search query is required', async () => {
    const mod = await import('../../src/commands/component')
    const search = (mod.default.subCommands ?? {}).search
    expect(search.args?.query?.required).toBe(true)
  })
})
