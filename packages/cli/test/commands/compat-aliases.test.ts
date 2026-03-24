/**
 * Tests for backward-compatibility aliases (noun-first -> verb-first migration).
 *
 * Verifies that:
 * - Compat aliases exist on skill.ts subCommands
 * - Each alias has the expected meta description containing "deprecated"
 * - Each alias has a run function
 * - The nounAlias / deprecatedCommand helpers produce valid Citty commands
 */
import { describe, expect, test } from 'bun:test'
import { deprecatedCommand, nounAlias } from '../../src/commands/compat'

// ---------------------------------------------------------------------------
// skill.ts backward-compat aliases — structural checks
// ---------------------------------------------------------------------------

describe('skill backward-compat aliases', () => {
  const VERB_ALIASES = ['add', 'init', 'list', 'search', 'info', 'update', 'remove'] as const
  const SKILL_SPECIFIC_ALIASES = ['find', 'outdated'] as const

  test('all verb aliases are registered as subcommands', async () => {
    const mod = await import('../../src/commands/skill')
    const subs = mod.default.subCommands ?? {}
    for (const name of VERB_ALIASES) {
      expect(subs[name]).toBeDefined()
    }
  })

  test('skill-specific aliases are registered as subcommands', async () => {
    const mod = await import('../../src/commands/skill')
    const subs = mod.default.subCommands ?? {}
    for (const name of SKILL_SPECIFIC_ALIASES) {
      expect(subs[name]).toBeDefined()
    }
  })

  test('each alias description indicates deprecation', async () => {
    const mod = await import('../../src/commands/skill')
    const subs = mod.default.subCommands as Record<string, { meta?: { description?: string } }>
    const all = [...VERB_ALIASES, ...SKILL_SPECIFIC_ALIASES]
    for (const name of all) {
      const desc = subs[name]?.meta?.description ?? ''
      expect(desc.toLowerCase()).toContain('deprecated')
    }
  })

  test('each alias has a run function', async () => {
    const mod = await import('../../src/commands/skill')
    const subs = mod.default.subCommands as Record<string, { run?: unknown }>
    const all = [...VERB_ALIASES, ...SKILL_SPECIFIC_ALIASES]
    for (const name of all) {
      expect(typeof subs[name]?.run).toBe('function')
    }
  })

  test('foundation subcommands still exist alongside aliases', async () => {
    const mod = await import('../../src/commands/skill')
    const subs = mod.default.subCommands ?? {}
    for (const name of ['validate', 'hash', 'lint', 'check-all', 'deps', 'catalog']) {
      expect(subs[name]).toBeDefined()
    }
  })
})

// ---------------------------------------------------------------------------
// compat.ts helpers — unit tests
// ---------------------------------------------------------------------------

describe('nounAlias helper', () => {
  test('creates a command with the verb as its name', () => {
    const cmd = nounAlias('skill', 'add', {
      source: { type: 'positional', description: 'src', required: true },
    })
    expect(cmd.meta?.name).toBe('add')
  })

  test('description mentions deprecation', () => {
    const cmd = nounAlias('skill', 'list')
    expect(cmd.meta?.description?.toLowerCase()).toContain('deprecated')
  })

  test('description points to verb-first usage', () => {
    const cmd = nounAlias('plugin', 'remove')
    expect(cmd.meta?.description).toContain('agents remove plugin')
  })

  test('has globalArgs (json, quiet, verbose)', () => {
    const cmd = nounAlias('skill', 'info')
    const args = cmd.args ?? {}
    expect(args.json).toBeDefined()
    expect(args.quiet).toBeDefined()
    expect(args.verbose).toBeDefined()
  })

  test('includes extra args when provided', () => {
    const cmd = nounAlias('skill', 'add', {
      source: { type: 'positional', description: 'src', required: true },
      copy: { type: 'boolean', description: 'Copy', default: false },
    })
    const args = cmd.args ?? {}
    expect(args.source).toBeDefined()
    expect(args.copy).toBeDefined()
  })

  test('has a run function', () => {
    const cmd = nounAlias('skill', 'add')
    expect(typeof cmd.run).toBe('function')
  })
})

describe('deprecatedCommand helper', () => {
  test('creates a command with the correct name', () => {
    const cmd = deprecatedCommand(
      'agents skill find', 'agents search skill', 'find',
      { query: { type: 'positional', description: 'q' } },
      async () => {},
    )
    expect(cmd.meta?.name).toBe('find')
  })

  test('description mentions deprecation', () => {
    const cmd = deprecatedCommand(
      'agents skill outdated', 'agents update skill --check', 'outdated',
      {},
      async () => {},
    )
    expect(cmd.meta?.description?.toLowerCase()).toContain('deprecated')
  })

  test('has a run function', () => {
    const cmd = deprecatedCommand(
      'agents skill find', 'agents search skill', 'find',
      {},
      async () => {},
    )
    expect(typeof cmd.run).toBe('function')
  })

  test('calls the handler when run is invoked', async () => {
    let called = false
    const cmd = deprecatedCommand(
      'agents skill test', 'agents test skill', 'test-cmd',
      {},
      async () => { called = true },
    )
    // Suppress stderr output during test
    const origError = console.error
    console.error = () => {}
    try {
      await cmd.run!({ args: { json: false, quiet: true } } as never)
    } finally {
      console.error = origError
    }
    expect(called).toBe(true)
  })
})
