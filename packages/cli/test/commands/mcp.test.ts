import { describe, expect, test } from 'bun:test'

describe('mcp command tree', () => {
  test('exports a command with subCommands', async () => {
    const mod = await import('../../src/commands/mcp')
    expect(mod.default).toBeDefined()
    expect(mod.default.subCommands).toBeDefined()
  })

  test('has all 6 subcommands', async () => {
    const mod = await import('../../src/commands/mcp')
    const subs = mod.default.subCommands ?? {}
    for (const name of ['search', 'add', 'list', 'remove', 'info', 'publish']) {
      expect(subs[name]).toBeDefined()
      expect(subs[name].meta?.name).toBe(name)
      expect(subs[name].meta?.description?.length).toBeGreaterThan(0)
    }
  })

  test('search has query, limit, page, verified, namespace args', async () => {
    const mod = await import('../../src/commands/mcp')
    const search = (mod.default.subCommands ?? {}).search
    expect(search.args?.query).toBeDefined()
    expect(search.args?.limit).toBeDefined()
    expect(search.args?.page).toBeDefined()
    expect(search.args?.verified).toBeDefined()
    expect(search.args?.namespace).toBeDefined()
  })

  test('add has source, client, name, transport args', async () => {
    const mod = await import('../../src/commands/mcp')
    const add = (mod.default.subCommands ?? {}).add
    expect(add.args?.source).toBeDefined()
    expect(add.args?.client).toBeDefined()
    expect(add.args?.name).toBeDefined()
    expect(add.args?.transport).toBeDefined()
  })

  test('list requires --client', async () => {
    const mod = await import('../../src/commands/mcp')
    const list = (mod.default.subCommands ?? {}).list
    expect(list.args?.client).toBeDefined()
  })

  test('publish has name, url, bundle-dir, api-key, dry-run args', async () => {
    const mod = await import('../../src/commands/mcp')
    const publish = (mod.default.subCommands ?? {}).publish
    expect(publish.args?.name).toBeDefined()
    expect(publish.args?.url).toBeDefined()
    expect(publish.args?.['bundle-dir']).toBeDefined()
    expect(publish.args?.['api-key']).toBeDefined()
    expect(publish.args?.['dry-run']).toBeDefined()
  })

  test('all subcommands inherit globalArgs (json, quiet, verbose)', async () => {
    const mod = await import('../../src/commands/mcp')
    const subs = mod.default.subCommands ?? {}
    for (const name of ['search', 'add', 'list', 'remove', 'info', 'publish']) {
      expect(subs[name].args?.json).toBeDefined()
      expect(subs[name].args?.quiet).toBeDefined()
      expect(subs[name].args?.verbose).toBeDefined()
    }
  })
})
