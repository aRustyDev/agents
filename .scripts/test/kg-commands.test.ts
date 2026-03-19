/**
 * Tests for the kg command module.
 *
 * Covers:
 *   - Module structure and exports
 *   - Entity pattern discovery (verifies globs find real files)
 *   - Entity ID generation from file paths
 *   - Subcommand presence
 *
 * Does NOT test actual Meilisearch integration (see test/meilisearch.test.ts).
 */

import { describe, expect, test } from 'bun:test'
import { resolve } from 'node:path'
import {
  discoverFiles,
  ENTITY_PATTERNS,
  ENTITY_TYPES,
  entityIdFromPath,
  PROJECT_ROOT,
} from '../commands/kg'

// ---------------------------------------------------------------------------
// Module structure
// ---------------------------------------------------------------------------

describe('kg command module', () => {
  test('exports a default defineCommand with subCommands', async () => {
    const mod = await import('../commands/kg')
    expect(mod.default).toBeDefined()
    expect(mod.default.meta?.name).toBe('kg')
    expect(mod.default.subCommands).toBeDefined()
  })

  test('has all expected subcommands', async () => {
    const mod = await import('../commands/kg')
    const subCommands = mod.default.subCommands!
    const names = Object.keys(subCommands)
    expect(names).toContain('init')
    expect(names).toContain('ingest')
    expect(names).toContain('search')
    expect(names).toContain('embed')
    expect(names).toContain('similar')
    expect(names).toContain('stats')
    expect(names).toContain('dump')
    expect(names).toContain('load')
    expect(names).toContain('watch')
  })

  test('exports ENTITY_PATTERNS', async () => {
    const mod = await import('../commands/kg')
    expect(mod.ENTITY_PATTERNS).toBeDefined()
    expect(typeof mod.ENTITY_PATTERNS).toBe('object')
  })

  test('exports ENTITY_TYPES', async () => {
    const mod = await import('../commands/kg')
    expect(Array.isArray(mod.ENTITY_TYPES)).toBe(true)
    expect(mod.ENTITY_TYPES.length).toBeGreaterThan(0)
  })

  test('exports discoverFiles function', async () => {
    const mod = await import('../commands/kg')
    expect(typeof mod.discoverFiles).toBe('function')
  })

  test('exports entityIdFromPath function', async () => {
    const mod = await import('../commands/kg')
    expect(typeof mod.entityIdFromPath).toBe('function')
  })

  test('exports PROJECT_ROOT', async () => {
    const mod = await import('../commands/kg')
    expect(typeof mod.PROJECT_ROOT).toBe('string')
    expect(mod.PROJECT_ROOT.length).toBeGreaterThan(0)
  })
})

// ---------------------------------------------------------------------------
// ENTITY_PATTERNS
// ---------------------------------------------------------------------------

describe('ENTITY_PATTERNS', () => {
  test('contains expected entity types', () => {
    expect(ENTITY_PATTERNS).toHaveProperty('skill')
    expect(ENTITY_PATTERNS).toHaveProperty('plugin')
    expect(ENTITY_PATTERNS).toHaveProperty('command')
    expect(ENTITY_PATTERNS).toHaveProperty('rule')
    expect(ENTITY_PATTERNS).toHaveProperty('agent')
    expect(ENTITY_PATTERNS).toHaveProperty('claude_md')
    expect(ENTITY_PATTERNS).toHaveProperty('output_style')
  })

  test('each entity type has at least one glob pattern', () => {
    for (const [type, patterns] of Object.entries(ENTITY_PATTERNS)) {
      expect(patterns.length).toBeGreaterThan(0)
    }
  })

  test('all patterns are strings', () => {
    for (const patterns of Object.values(ENTITY_PATTERNS)) {
      for (const p of patterns) {
        expect(typeof p).toBe('string')
      }
    }
  })
})

// ---------------------------------------------------------------------------
// ENTITY_TYPES
// ---------------------------------------------------------------------------

describe('ENTITY_TYPES', () => {
  test('is an array of strings', () => {
    expect(Array.isArray(ENTITY_TYPES)).toBe(true)
    for (const t of ENTITY_TYPES) {
      expect(typeof t).toBe('string')
    }
  })

  test('matches keys of ENTITY_PATTERNS', () => {
    const patternKeys = Object.keys(ENTITY_PATTERNS).sort()
    const types = [...ENTITY_TYPES].sort()
    expect(types).toEqual(patternKeys)
  })
})

// ---------------------------------------------------------------------------
// entityIdFromPath
// ---------------------------------------------------------------------------

describe('entityIdFromPath', () => {
  test('replaces slashes with underscores', () => {
    expect(entityIdFromPath('context/skills/beads/SKILL.md')).toBe('context_skills_beads_SKILL')
  })

  test('strips file extension', () => {
    const id = entityIdFromPath('context/rules/agent/hooks.md')
    expect(id).toBe('context_rules_agent_hooks')
    expect(id).not.toContain('.md')
  })

  test('handles single filename', () => {
    expect(entityIdFromPath('CLAUDE.md')).toBe('CLAUDE')
  })

  test('handles deeply nested paths', () => {
    expect(entityIdFromPath('a/b/c/d/e.ts')).toBe('a_b_c_d_e')
  })

  test('handles paths with multiple dots', () => {
    expect(entityIdFromPath('context/file.test.md')).toBe('context_file.test')
  })

  test('handles json extension', () => {
    expect(entityIdFromPath('context/plugins/foo/.claude-plugin/plugin.json')).toBe(
      'context_plugins_foo_.claude-plugin_plugin'
    )
  })
})

// ---------------------------------------------------------------------------
// PROJECT_ROOT
// ---------------------------------------------------------------------------

describe('PROJECT_ROOT', () => {
  test('is an absolute path', () => {
    expect(PROJECT_ROOT.startsWith('/')).toBe(true)
  })

  test('contains expected parent directory', () => {
    // PROJECT_ROOT should point to the repo root (two levels up from commands/)
    expect(PROJECT_ROOT).toContain('infra/pub/ai')
    expect(PROJECT_ROOT).not.toContain('.scripts')
  })
})

// ---------------------------------------------------------------------------
// discoverFiles
// ---------------------------------------------------------------------------

describe('discoverFiles', () => {
  test('discovers skill files in the real repo', async () => {
    const files = await discoverFiles(['skill'])
    expect(files.length).toBeGreaterThan(0)

    // All discovered files should have type "skill"
    for (const f of files) {
      expect(f.type).toBe('skill')
    }

    // At least one should match the SKILL.md pattern
    const hasSkillMd = files.some((f) => f.relPath.endsWith('SKILL.md'))
    expect(hasSkillMd).toBe(true)
  })

  test('discovers rule files in the real repo', async () => {
    const files = await discoverFiles(['rule'])
    expect(files.length).toBeGreaterThan(0)

    for (const f of files) {
      expect(f.type).toBe('rule')
    }

    // Rules should be .md files
    const hasMd = files.some((f) => f.relPath.endsWith('.md'))
    expect(hasMd).toBe(true)
  })

  test('discovers CLAUDE.md', async () => {
    const files = await discoverFiles(['claude_md'])
    expect(files.length).toBeGreaterThan(0)

    const claudeMd = files.find((f) => f.relPath === 'CLAUDE.md')
    expect(claudeMd).toBeDefined()
    expect(claudeMd!.type).toBe('claude_md')
  })

  test('discovers output style files', async () => {
    const files = await discoverFiles(['output_style'])
    expect(files.length).toBeGreaterThan(0)

    for (const f of files) {
      expect(f.type).toBe('output_style')
    }
  })

  test('discovers all entity types when no filter specified', async () => {
    const files = await discoverFiles()
    expect(files.length).toBeGreaterThan(0)

    // Should have multiple types represented
    const types = new Set(files.map((f) => f.type))
    expect(types.size).toBeGreaterThan(1)
  })

  test('returns absolute paths for absPath', async () => {
    const files = await discoverFiles(['skill'])
    for (const f of files) {
      expect(f.absPath.startsWith('/')).toBe(true)
    }
  })

  test('returns relative paths for relPath', async () => {
    const files = await discoverFiles(['skill'])
    for (const f of files) {
      expect(f.relPath.startsWith('/')).toBe(false)
    }
  })

  test('absPath resolves relative to PROJECT_ROOT', async () => {
    const files = await discoverFiles(['skill'])
    for (const f of files) {
      expect(f.absPath).toBe(resolve(PROJECT_ROOT, f.relPath))
    }
  })

  test('deduplicates files discovered by multiple patterns', async () => {
    // Rules have multiple patterns; should not return duplicates
    const files = await discoverFiles(['rule'])
    const paths = files.map((f) => f.relPath)
    const unique = new Set(paths)
    expect(paths.length).toBe(unique.size)
  })
})
