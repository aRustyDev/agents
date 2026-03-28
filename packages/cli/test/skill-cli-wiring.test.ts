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

  test('verb subcommands exist as backward-compat aliases', async () => {
    const mod = await import('../src/commands/skill')
    const subs = mod.default.subCommands ?? {}
    // These verb commands are now backward-compat aliases that proxy to verb-first modules
    const aliased = ['add', 'init', 'list', 'search', 'find', 'outdated', 'update', 'remove', 'info']
    for (const name of aliased) {
      expect(subs[name]).toBeDefined()
    }
  })
})
