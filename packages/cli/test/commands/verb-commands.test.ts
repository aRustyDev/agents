/**
 * Structural tests for the 8 verb-first command modules.
 *
 * These tests verify each module exports a valid Citty command definition
 * with the correct meta, positional args, and globalArgs. They do NOT
 * exercise runtime behavior (no ComponentManager calls).
 */
import { describe, expect, test } from 'bun:test'

const VERB_MODULES = ['add', 'remove', 'list', 'search', 'info', 'init', 'lint', 'update'] as const

// ---------------------------------------------------------------------------
// Shared structural checks for all 8 verbs
// ---------------------------------------------------------------------------

describe('verb command modules — shared structure', () => {
  for (const verb of VERB_MODULES) {
    test(`${verb} exports a valid Citty command`, async () => {
      const mod = await import(`../../src/commands/${verb}`)
      expect(mod.default).toBeDefined()
      expect(mod.default.meta).toBeDefined()
      expect(mod.default.meta.name).toBe(verb)
      expect(mod.default.meta.description?.length).toBeGreaterThan(0)
    })

    test(`${verb} has a 'type' positional arg`, async () => {
      const mod = await import(`../../src/commands/${verb}`)
      const typeArg = mod.default.args?.type
      expect(typeArg).toBeDefined()
      expect(typeArg.type).toBe('positional')
    })

    test(`${verb} inherits globalArgs (json, quiet, verbose)`, async () => {
      const mod = await import(`../../src/commands/${verb}`)
      const args = mod.default.args ?? {}
      expect(args.json).toBeDefined()
      expect(args.quiet).toBeDefined()
      expect(args.verbose).toBeDefined()
    })

    test(`${verb} has a run function`, async () => {
      const mod = await import(`../../src/commands/${verb}`)
      expect(typeof mod.default.run).toBe('function')
    })
  }
})

// ---------------------------------------------------------------------------
// Command-specific arg checks
// ---------------------------------------------------------------------------

describe('add command', () => {
  test('has source positional arg (required)', async () => {
    const mod = await import('../../src/commands/add')
    const source = mod.default.args?.source
    expect(source).toBeDefined()
    expect(source.type).toBe('positional')
    expect(source.required).toBe(true)
  })

  test('has copy, yes, agent, client args', async () => {
    const mod = await import('../../src/commands/add')
    const args = mod.default.args ?? {}
    expect(args.copy).toBeDefined()
    expect(args.yes).toBeDefined()
    expect(args.agent).toBeDefined()
    expect(args.client).toBeDefined()
  })

  test('type is required', async () => {
    const mod = await import('../../src/commands/add')
    expect(mod.default.args?.type?.required).toBe(true)
  })
})

describe('remove command', () => {
  test('has name positional arg (required)', async () => {
    const mod = await import('../../src/commands/remove')
    const name = mod.default.args?.name
    expect(name).toBeDefined()
    expect(name.type).toBe('positional')
    expect(name.required).toBe(true)
  })

  test('has agent arg (yes removed — prompts not yet implemented)', async () => {
    const mod = await import('../../src/commands/remove')
    const args = mod.default.args ?? {}
    expect(args.agent).toBeDefined()
    expect(args.yes).toBeUndefined()
  })
})

describe('list command', () => {
  test('type is optional', async () => {
    const mod = await import('../../src/commands/list')
    expect(mod.default.args?.type?.required).toBe(false)
  })

  test('has agent arg', async () => {
    const mod = await import('../../src/commands/list')
    expect(mod.default.args?.agent).toBeDefined()
  })
})

describe('search command', () => {
  test('has query positional arg (required)', async () => {
    const mod = await import('../../src/commands/search')
    const query = mod.default.args?.query
    expect(query).toBeDefined()
    expect(query.type).toBe('positional')
    expect(query.required).toBe(true)
  })

  test('has limit, page, verified args', async () => {
    const mod = await import('../../src/commands/search')
    const args = mod.default.args ?? {}
    expect(args.limit).toBeDefined()
    expect(args.page).toBeDefined()
    expect(args.verified).toBeDefined()
  })
})

describe('info command', () => {
  test('has name positional arg (required)', async () => {
    const mod = await import('../../src/commands/info')
    const name = mod.default.args?.name
    expect(name).toBeDefined()
    expect(name.type).toBe('positional')
    expect(name.required).toBe(true)
  })

  test('type is required', async () => {
    const mod = await import('../../src/commands/info')
    expect(mod.default.args?.type?.required).toBe(true)
  })
})

describe('init command', () => {
  test('has optional name positional arg', async () => {
    const mod = await import('../../src/commands/init')
    const name = mod.default.args?.name
    expect(name).toBeDefined()
    expect(name.type).toBe('positional')
    expect(name.required).toBe(false)
  })

  test('has description and template args', async () => {
    const mod = await import('../../src/commands/init')
    const args = mod.default.args ?? {}
    expect(args.description).toBeDefined()
    expect(args.template).toBeDefined()
  })
})

describe('lint command', () => {
  test('type is optional', async () => {
    const mod = await import('../../src/commands/lint')
    expect(mod.default.args?.type?.required).toBe(false)
  })

  test('has optional name positional arg', async () => {
    const mod = await import('../../src/commands/lint')
    const name = mod.default.args?.name
    expect(name).toBeDefined()
    expect(name.type).toBe('positional')
    expect(name.required).toBe(false)
  })

  test('has output arg', async () => {
    const mod = await import('../../src/commands/lint')
    expect(mod.default.args?.output).toBeDefined()
  })
})

describe('update command', () => {
  test('type is optional', async () => {
    const mod = await import('../../src/commands/update')
    expect(mod.default.args?.type?.required).toBe(false)
  })

  test('has optional name positional arg', async () => {
    const mod = await import('../../src/commands/update')
    const name = mod.default.args?.name
    expect(name).toBeDefined()
    expect(name.type).toBe('positional')
    expect(name.required).toBe(false)
  })

  test('has copy and yes args', async () => {
    const mod = await import('../../src/commands/update')
    const args = mod.default.args ?? {}
    expect(args.copy).toBeDefined()
    expect(args.yes).toBeDefined()
  })
})

// ---------------------------------------------------------------------------
// Entrypoint wiring — verify agents.ts registers all expected subcommands
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Entrypoint wiring — verify verb modules are accessible via lazy import
// ---------------------------------------------------------------------------
// Note: We cannot import agents.ts directly because it calls runMain() at
// module scope. Instead we verify the lazy import pattern it uses works.
// We also avoid importing modules like catalog/kg that have side-effects
// sensitive to the import.meta context of the test runner.

describe('agents.ts entrypoint wiring', () => {
  test('all 8 verb modules resolve via the lazy import pattern', async () => {
    for (const verb of VERB_MODULES) {
      const cmd = await import(`../../src/commands/${verb}`).then((m) => m.default)
      expect(cmd).toBeDefined()
      expect(cmd.meta?.name).toBe(verb)
      expect(typeof cmd.run).toBe('function')
    }
  })

  test('agents.ts source contains all expected subcommand registrations', async () => {
    const fs = await import('node:fs')
    const path = await import('node:path')
    const agentsPath = path.resolve(import.meta.dir, '../../src/bin/agents.ts')
    const source = fs.readFileSync(agentsPath, 'utf-8')

    // Verify verb-first commands
    for (const verb of VERB_MODULES) {
      expect(source).toContain(`${verb}: () => import('../commands/${verb}')`)
    }

    // Verify legacy noun commands
    for (const noun of ['plugin', 'skill', 'mcp', 'kg', 'registry']) {
      expect(source).toContain(`${noun}: () => import('../commands/${noun}')`)
    }

    // Verify pipeline commands
    expect(source).toContain("catalog: () => import('../commands/catalog')")
  })
})
