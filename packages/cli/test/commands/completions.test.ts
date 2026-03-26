/**
 * Tests for the shell completions command module.
 *
 * Verifies the command structure and that each generator produces output
 * containing the expected commands, types, and shell-specific patterns.
 */
import { describe, expect, test } from 'bun:test'
import { COMPONENT_TYPES } from '@agents/sdk/context/types'

// ---------------------------------------------------------------------------
// Module structure
// ---------------------------------------------------------------------------

describe('completions command — structure', () => {
  test('exports a valid Citty command', async () => {
    const mod = await import('../../src/commands/completions')
    expect(mod.default).toBeDefined()
    expect(mod.default.meta?.name).toBe('completions')
    expect(mod.default.meta?.description?.length).toBeGreaterThan(0)
  })

  test('has bash, zsh, fish subcommands', async () => {
    const mod = await import('../../src/commands/completions')
    const subs = mod.default.subCommands as Record<string, unknown>
    expect(subs.bash).toBeDefined()
    expect(subs.zsh).toBeDefined()
    expect(subs.fish).toBeDefined()
  })

  test('exports generateBash, generateZsh, generateFish functions', async () => {
    const mod = await import('../../src/commands/completions')
    expect(typeof mod.generateBash).toBe('function')
    expect(typeof mod.generateZsh).toBe('function')
    expect(typeof mod.generateFish).toBe('function')
  })
})

// ---------------------------------------------------------------------------
// Bash completions
// ---------------------------------------------------------------------------

describe('generateBash', () => {
  test('contains all top-level commands', async () => {
    const { generateBash } = await import('../../src/commands/completions')
    const output = generateBash()
    for (const cmd of [
      'add',
      'remove',
      'list',
      'search',
      'info',
      'init',
      'lint',
      'update',
      'catalog',
      'config',
      'completions',
    ]) {
      expect(output).toContain(cmd)
    }
  })

  test('contains all component types', async () => {
    const { generateBash } = await import('../../src/commands/completions')
    const output = generateBash()
    for (const t of COMPONENT_TYPES) {
      expect(output).toContain(t)
    }
  })

  test('contains complete -F for agents', async () => {
    const { generateBash } = await import('../../src/commands/completions')
    const output = generateBash()
    expect(output).toContain('complete -F _agents_completions agents')
  })
})

// ---------------------------------------------------------------------------
// Zsh completions
// ---------------------------------------------------------------------------

describe('generateZsh', () => {
  test('contains component types', async () => {
    const { generateZsh } = await import('../../src/commands/completions')
    const output = generateZsh()
    for (const t of COMPONENT_TYPES) {
      expect(output).toContain(t)
    }
  })

  test('contains compdef for agents', async () => {
    const { generateZsh } = await import('../../src/commands/completions')
    const output = generateZsh()
    expect(output).toContain('compdef _agents agents')
  })

  test('contains #compdef agents header', async () => {
    const { generateZsh } = await import('../../src/commands/completions')
    const output = generateZsh()
    expect(output).toContain('#compdef agents')
  })
})

// ---------------------------------------------------------------------------
// Fish completions
// ---------------------------------------------------------------------------

describe('generateFish', () => {
  test('contains complete -c agents', async () => {
    const { generateFish } = await import('../../src/commands/completions')
    const output = generateFish()
    expect(output).toContain('complete -c agents')
  })

  test('contains all component types', async () => {
    const { generateFish } = await import('../../src/commands/completions')
    const output = generateFish()
    for (const t of COMPONENT_TYPES) {
      expect(output).toContain(t)
    }
  })

  test('contains catalog subcommands', async () => {
    const { generateFish } = await import('../../src/commands/completions')
    const output = generateFish()
    for (const sub of ['analyze', 'summary', 'forks', 'cleanup', 'errors']) {
      expect(output).toContain(sub)
    }
  })
})
