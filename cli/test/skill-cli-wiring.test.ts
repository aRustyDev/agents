import { describe, expect, test } from 'bun:test'

describe('skill CLI wiring', () => {
  test('skill command module exports a command with subCommands', async () => {
    const mod = await import('../commands/skill')
    const cmd = mod.default
    expect(cmd).toBeDefined()
    expect(cmd.subCommands).toBeDefined()
  })

  test('all new subcommands are registered', async () => {
    const mod = await import('../commands/skill')
    const subs = mod.default.subCommands ?? {}
    const expected = ['add', 'init', 'list', 'find', 'outdated', 'update', 'remove', 'info']
    for (const name of expected) {
      expect(subs[name]).toBeDefined()
      expect(subs[name].meta?.name).toBe(name)
      expect(subs[name].meta?.description?.length).toBeGreaterThan(0)
    }
  })

  test('existing subcommands still present', async () => {
    const mod = await import('../commands/skill')
    const subs = mod.default.subCommands ?? {}
    for (const name of ['validate', 'hash', 'lint', 'check-all', 'deps', 'catalog']) {
      expect(subs[name]).toBeDefined()
    }
  })
})
