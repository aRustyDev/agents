/**
 * Tests for the `agents doctor` command.
 *
 * Validates module structure, args, and that runChecks produces
 * a well-formed array of CheckResult objects.
 */
import { describe, expect, test } from 'bun:test'
import { resolve } from 'node:path'

/** Explicit project root to avoid import.meta resolution issues in full suite. */
const PROJECT_ROOT = resolve(import.meta.dir, '../../../..')

// ---------------------------------------------------------------------------
// Module structure
// ---------------------------------------------------------------------------

describe('doctor command — module structure', () => {
  test('exports a valid Citty command', async () => {
    const mod = await import('../../src/commands/doctor')
    expect(mod.default).toBeDefined()
    expect(mod.default.meta).toBeDefined()
    expect(mod.default.meta.name).toBe('doctor')
    expect(mod.default.meta.description?.length).toBeGreaterThan(0)
  })

  test('has a run function', async () => {
    const mod = await import('../../src/commands/doctor')
    expect(typeof mod.default.run).toBe('function')
  })

  test('inherits globalArgs (json, quiet, verbose)', async () => {
    const mod = await import('../../src/commands/doctor')
    const args = mod.default.args ?? {}
    expect(args.json).toBeDefined()
    expect(args.quiet).toBeDefined()
    expect(args.verbose).toBeDefined()
  })
})

// ---------------------------------------------------------------------------
// CheckResult interface
// ---------------------------------------------------------------------------

describe('doctor command — runChecks', () => {
  test('exports runChecks function', async () => {
    const mod = await import('../../src/commands/doctor')
    expect(typeof mod.runChecks).toBe('function')
  })

  test('runChecks returns an array', async () => {
    const { runChecks } = await import('../../src/commands/doctor')
    const results = await runChecks(PROJECT_ROOT)
    expect(Array.isArray(results)).toBe(true)
    expect(results.length).toBeGreaterThan(0)
  })

  test('each result has category, check, status, detail', async () => {
    const { runChecks } = await import('../../src/commands/doctor')
    const results = await runChecks(PROJECT_ROOT)
    for (const r of results) {
      expect(typeof r.category).toBe('string')
      expect(r.category.length).toBeGreaterThan(0)
      expect(typeof r.check).toBe('string')
      expect(r.check.length).toBeGreaterThan(0)
      expect(['ok', 'warn', 'error']).toContain(r.status)
      expect(typeof r.detail).toBe('string')
    }
  })

  test('status values are valid', async () => {
    const { runChecks } = await import('../../src/commands/doctor')
    const results = await runChecks(PROJECT_ROOT)
    const validStatuses = new Set(['ok', 'warn', 'error'])
    for (const r of results) {
      expect(validStatuses.has(r.status)).toBe(true)
    }
  })
})

// ---------------------------------------------------------------------------
// Runtime checks pass in test env (Bun is available)
// ---------------------------------------------------------------------------

describe('doctor command — runtime checks', () => {
  test('Bun is detected as ok', async () => {
    const { runChecks } = await import('../../src/commands/doctor')
    const results = await runChecks(PROJECT_ROOT)
    const bunCheck = results.find((r) => r.check === 'Bun')
    expect(bunCheck).toBeDefined()
    expect(bunCheck?.status).toBe('ok')
    expect(bunCheck?.detail).toMatch(/^v/)
  })

  test('Git is detected as ok', async () => {
    const { runChecks } = await import('../../src/commands/doctor')
    const results = await runChecks(PROJECT_ROOT)
    const gitCheck = results.find((r) => r.check === 'Git')
    expect(gitCheck).toBeDefined()
    expect(gitCheck?.status).toBe('ok')
  })

  test('categories include Runtime, Project, Config, Components', async () => {
    const { runChecks } = await import('../../src/commands/doctor')
    const results = await runChecks(PROJECT_ROOT)
    const categories = new Set(results.map((r) => r.category))
    expect(categories.has('Runtime')).toBe(true)
    expect(categories.has('Project')).toBe(true)
    expect(categories.has('Config')).toBe(true)
    expect(categories.has('Components')).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// CheckResult type export
// ---------------------------------------------------------------------------

describe('doctor command — CheckResult type', () => {
  test('CheckResult type is usable', async () => {
    // Just verify the type exports are accessible
    const result: import('../../src/commands/doctor').CheckResult = {
      category: 'Test',
      check: 'test check',
      status: 'ok',
      detail: 'test detail',
    }
    expect(result.category).toBe('Test')
    expect(result.status).toBe('ok')
  })
})
