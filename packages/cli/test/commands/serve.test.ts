/**
 * Tests for the `agents serve` command.
 *
 * Validates module structure, args, and mode flags.
 * Does NOT start an actual server.
 */
import { describe, expect, test } from 'bun:test'

// ---------------------------------------------------------------------------
// Module structure
// ---------------------------------------------------------------------------

describe('serve command — module structure', () => {
  test('exports a valid Citty command', async () => {
    const mod = await import('../../src/commands/serve')
    expect(mod.default).toBeDefined()
    expect(mod.default.meta).toBeDefined()
    expect(mod.default.meta.name).toBe('serve')
    expect(mod.default.meta.description?.length).toBeGreaterThan(0)
  })

  test('has a run function', async () => {
    const mod = await import('../../src/commands/serve')
    expect(typeof mod.default.run).toBe('function')
  })

  test('inherits globalArgs (json, quiet, verbose)', async () => {
    const mod = await import('../../src/commands/serve')
    const args = mod.default.args ?? {}
    expect(args.json).toBeDefined()
    expect(args.quiet).toBeDefined()
    expect(args.verbose).toBeDefined()
  })
})

// ---------------------------------------------------------------------------
// Args validation
// ---------------------------------------------------------------------------

describe('serve command — args', () => {
  test('has --web flag (boolean)', async () => {
    const mod = await import('../../src/commands/serve')
    const args = mod.default.args ?? {}
    expect(args.web).toBeDefined()
    expect(args.web.type).toBe('boolean')
  })

  test('has --api flag (boolean)', async () => {
    const mod = await import('../../src/commands/serve')
    const args = mod.default.args ?? {}
    expect(args.api).toBeDefined()
    expect(args.api.type).toBe('boolean')
  })

  test('has --port flag (string, default 3000)', async () => {
    const mod = await import('../../src/commands/serve')
    const args = mod.default.args ?? {}
    expect(args.port).toBeDefined()
    expect(args.port.type).toBe('string')
    expect(args.port.default).toBe('3000')
  })

  test('--port has alias p', async () => {
    const mod = await import('../../src/commands/serve')
    const args = mod.default.args ?? {}
    expect(args.port.alias).toBe('p')
  })

  test('--web defaults to false', async () => {
    const mod = await import('../../src/commands/serve')
    const args = mod.default.args ?? {}
    expect(args.web.default).toBe(false)
  })

  test('--api defaults to false', async () => {
    const mod = await import('../../src/commands/serve')
    const args = mod.default.args ?? {}
    expect(args.api.default).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// Meta
// ---------------------------------------------------------------------------

describe('serve command — meta', () => {
  test('name is serve', async () => {
    const mod = await import('../../src/commands/serve')
    expect(mod.default.meta.name).toBe('serve')
  })

  test('description mentions server', async () => {
    const mod = await import('../../src/commands/serve')
    expect(mod.default.meta.description?.toLowerCase()).toContain('server')
  })
})
