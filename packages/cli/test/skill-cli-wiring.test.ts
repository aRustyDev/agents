import { describe, expect, test } from 'bun:test'

describe('skill CLI wiring', () => {
  test('skill command module exports a command with subCommands', async () => {
    const mod = await import('../src/commands/skill')
    const cmd = mod.default
    expect(cmd).toBeDefined()
    expect(cmd.subCommands).toBeDefined()
  })

  test('foundation subcommands are registered', async () => {
    const mod = await import('../src/commands/skill')
    const subs = mod.default.subCommands ?? {}
    for (const name of ['validate', 'hash', 'lint', 'check-all', 'deps', 'catalog']) {
      expect(subs[name]).toBeDefined()
    }
  })

  test('verb subcommands have been extracted to top-level modules', async () => {
    const mod = await import('../src/commands/skill')
    const subs = mod.default.subCommands ?? {}
    // These verb commands were moved to top-level verb modules in Phase 7
    const extracted = ['add', 'init', 'list', 'find', 'outdated', 'update', 'remove', 'info']
    for (const name of extracted) {
      expect(subs[name]).toBeUndefined()
    }
  })
})
