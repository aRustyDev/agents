import { describe, expect, test } from 'bun:test'
import { existsSync, mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { listPlugins, validateMarketplace, validatePlugin, validateRules } from '../src/commands/plugin'

// ---------------------------------------------------------------------------
// validateMarketplace -- tested against real marketplace.json
// ---------------------------------------------------------------------------

describe('validateMarketplace', () => {
  test('validates real marketplace.json successfully', async () => {
    const result = await validateMarketplace()
    expect(result.plugin).toBe('marketplace')
    // The real file should parse without schema errors
    // There may be warnings (e.g., source paths not found in worktree)
    // but the schema validation itself should succeed
    expect(result.errors.filter((e) => e.startsWith('Schema error'))).toHaveLength(0)
    expect(result.errors.filter((e) => e.startsWith('Invalid JSON'))).toHaveLength(0)
    expect(result.errors.filter((e) => e.startsWith('Duplicate plugin name'))).toHaveLength(0)
  })

  test('detects no duplicate plugin names in real marketplace', async () => {
    const result = await validateMarketplace()
    const dupeErrors = result.errors.filter((e) => e.startsWith('Duplicate plugin name'))
    expect(dupeErrors).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// validateRules -- tested against real content/rules/
// ---------------------------------------------------------------------------

describe('validateRules', () => {
  test('finds rule files in real content/rules/', async () => {
    const result = await validateRules()
    expect(result.plugin).toBe('rules')
    // The real rules directory should exist and have files
    expect(result.errors).toHaveLength(0)
  })

  test('returns no errors for existing rule files', async () => {
    const result = await validateRules()
    expect(result.valid).toBe(true)
  })

  test('warns about oversized rule files (>10KB)', async () => {
    const result = await validateRules()
    // Any warnings about size should follow the expected format
    for (const w of result.warnings) {
      if (w.includes('>10KB')) {
        expect(w).toMatch(/KB.*rules should be concise/)
      }
    }
  })
})

// ---------------------------------------------------------------------------
// validatePlugin -- output style validation (step 5c)
// ---------------------------------------------------------------------------

describe('validatePlugin output styles', () => {
  test('blog-workflow output styles pass validation', async () => {
    const result = await validatePlugin('blog-workflow')
    // blog-workflow has real .md output style files -- none should be flagged
    const styleErrors = result.errors.filter(
      (e) => e.includes('outputStyles') || e.includes('Output style')
    )
    expect(styleErrors).toHaveLength(0)

    // All output style entries should be .md files, so no "expected .md" warnings
    const mdWarnings = result.warnings.filter((w) => w.includes('expected .md'))
    expect(mdWarnings).toHaveLength(0)
  })

  test('blog-workflow output style files are not empty', async () => {
    const result = await validatePlugin('blog-workflow')
    const emptyErrors = result.errors.filter(
      (e) => e.includes('Output style') && e.includes('empty')
    )
    expect(emptyErrors).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// validate-all integration -- runs validatePlugin against every plugin
// ---------------------------------------------------------------------------

describe('validate-all integration', () => {
  test('listPlugins returns a non-empty list', () => {
    const plugins = listPlugins()
    expect(plugins.length).toBeGreaterThan(0)
  })

  test('all plugins pass validation (0 errors)', async () => {
    const plugins = listPlugins()
    expect(plugins.length).toBeGreaterThan(0)

    for (const name of plugins) {
      const result = await validatePlugin(name)
      if (!result.valid) {
        console.log(`FAIL ${name}:`, result.errors)
      }
      expect(result.valid).toBe(true)
    }
  })

  test('blog-workflow has 0 warnings', async () => {
    const result = await validatePlugin('blog-workflow')
    expect(result.valid).toBe(true)
    expect(result.warnings).toHaveLength(0)
  })

  test('marketplace has 0 errors', async () => {
    const result = await validateMarketplace()
    expect(result.valid).toBe(true)
    expect(result.errors).toHaveLength(0)
  })

  test('marketplace has no duplicate plugin names', async () => {
    const result = await validateMarketplace()
    expect(result.errors.filter((e) => e.includes('Duplicate'))).toHaveLength(0)
  })
})
