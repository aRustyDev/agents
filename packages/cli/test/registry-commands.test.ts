/**
 * CLI command wiring tests for the registry command module.
 *
 * These tests verify that the registry command is properly defined
 * with expected subcommands. Split from registry.test.ts during
 * test migration (the SDK-bound tests moved to @agents/sdk).
 */

import { describe, expect, test } from 'bun:test'

describe('registry command module', () => {
  test('exports a default defineCommand', async () => {
    const mod = await import('../src/commands/registry')
    expect(mod.default).toBeDefined()
    expect(mod.default.meta).toBeDefined()
    expect(mod.default.meta!.name).toBe('registry')
  })

  test('has crawl subcommand', async () => {
    const mod = await import('../src/commands/registry')
    expect(mod.default.subCommands).toBeDefined()
    expect(mod.default.subCommands!.crawl).toBeDefined()
  })

  test('has validate subcommand', async () => {
    const mod = await import('../src/commands/registry')
    expect(mod.default.subCommands!.validate).toBeDefined()
  })

  test('has stats subcommand', async () => {
    const mod = await import('../src/commands/registry')
    expect(mod.default.subCommands!.stats).toBeDefined()
  })
})
