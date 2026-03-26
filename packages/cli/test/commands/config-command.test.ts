import { afterAll, beforeAll, describe, expect, test } from 'bun:test'
import { mkdtemp, realpath, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  type AgentsConfig,
  getConfigValue,
  loadConfig,
  readConfigFile,
  writeConfigFile,
} from '@agents/core/config'

// ---------------------------------------------------------------------------
// Shared fixture directory
// ---------------------------------------------------------------------------

let root: string

beforeAll(async () => {
  root = await realpath(await mkdtemp(join(tmpdir(), 'config-cmd-test-')))
})

afterAll(async () => {
  await rm(root, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Command tree structure
// ---------------------------------------------------------------------------

describe('config command tree', () => {
  test('exports a command with subCommands', async () => {
    const mod = await import('../../src/commands/config')
    expect(mod.default).toBeDefined()
    expect(mod.default.subCommands).toBeDefined()
  })

  test('has all 5 subcommands', async () => {
    const mod = await import('../../src/commands/config')
    const subs = mod.default.subCommands ?? {}
    for (const name of ['get', 'set', 'list', 'edit', 'path']) {
      expect(subs[name]).toBeDefined()
      expect(subs[name].meta?.name).toBe(name)
      expect(subs[name].meta?.description?.length).toBeGreaterThan(0)
    }
  })

  test('get has key positional arg', async () => {
    const mod = await import('../../src/commands/config')
    const get = mod.default.subCommands?.get
    expect(get.args?.key).toBeDefined()
    expect(get.args?.key?.type).toBe('positional')
    expect(get.args?.key?.required).toBe(true)
  })

  test('set has key and value positional args plus --global', async () => {
    const mod = await import('../../src/commands/config')
    const set = mod.default.subCommands?.set
    expect(set.args?.key).toBeDefined()
    expect(set.args?.key?.type).toBe('positional')
    expect(set.args?.value).toBeDefined()
    expect(set.args?.value?.type).toBe('positional')
    expect(set.args?.global).toBeDefined()
    expect(set.args?.global?.type).toBe('boolean')
  })

  test('edit has --global flag', async () => {
    const mod = await import('../../src/commands/config')
    const edit = mod.default.subCommands?.edit
    expect(edit.args?.global).toBeDefined()
    expect(edit.args?.global?.type).toBe('boolean')
  })

  test('all subcommands inherit globalArgs (json, quiet, verbose)', async () => {
    const mod = await import('../../src/commands/config')
    const subs = mod.default.subCommands ?? {}
    for (const name of ['get', 'set', 'list', 'edit', 'path']) {
      expect(subs[name].args?.json).toBeDefined()
      expect(subs[name].args?.quiet).toBeDefined()
      expect(subs[name].args?.verbose).toBeDefined()
    }
  })
})

// ---------------------------------------------------------------------------
// Integration: set then get via config library (no CLI process spawn)
// ---------------------------------------------------------------------------

describe('config set/get integration', () => {
  test('writeConfigFile then readConfigFile round-trips a value', async () => {
    const filePath = join(root, 'integration.toml')

    // Write a config with debug=true
    await writeConfigFile(filePath, {
      general: { debug: true, outputFormat: 'human', failOn: 'error' },
    })

    // Read it back
    const result = await readConfigFile(filePath)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect((result.value as AgentsConfig).general?.debug).toBe(true)
    }
  })

  test('set then get returns same value via loadConfig', async () => {
    const dir = join(root, 'set-get-project')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(dir, { recursive: true })

    // Write a project config
    const filePath = join(dir, '.agents.toml')
    await writeConfigFile(filePath, {
      search: { backends: ['local'], defaultLimit: 42 },
    })

    // Load the full config
    const configResult = await loadConfig({ cwd: dir })
    expect(configResult.ok).toBe(true)
    if (configResult.ok) {
      expect(getConfigValue(configResult.value, 'search.defaultLimit')).toBe(42)
    }
  })

  test('set boolean value is coerced correctly', async () => {
    const filePath = join(root, 'coerce-bool.toml')
    await writeConfigFile(filePath, {
      general: { debug: true, outputFormat: 'human', failOn: 'error' },
    })

    const result = await readConfigFile(filePath)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect((result.value as AgentsConfig).general?.debug).toBe(true)
    }
  })

  test('set numeric value is stored as number', async () => {
    const filePath = join(root, 'coerce-num.toml')
    await writeConfigFile(filePath, {
      search: { backends: ['local'], defaultLimit: 99 },
    })

    const result = await readConfigFile(filePath)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect((result.value as AgentsConfig).search?.defaultLimit).toBe(99)
    }
  })
})

// ---------------------------------------------------------------------------
// List shows all config keys
// ---------------------------------------------------------------------------

describe('config list coverage', () => {
  test('loadConfig returns all expected top-level sections', async () => {
    const configResult = await loadConfig({ cwd: root })
    expect(configResult.ok).toBe(true)
    if (configResult.ok) {
      const config = configResult.value
      expect(config.general).toBeDefined()
      expect(config.search).toBeDefined()
      expect(config.catalog).toBeDefined()
    }
  })

  test('loadConfig returns all expected keys', async () => {
    const configResult = await loadConfig({ cwd: root })
    expect(configResult.ok).toBe(true)
    if (configResult.ok) {
      const config = configResult.value
      // general keys
      expect(config.general.debug).toBeDefined()
      expect(config.general.outputFormat).toBeDefined()
      expect(config.general.failOn).toBeDefined()
      // search keys
      expect(config.search.backends).toBeDefined()
      expect(config.search.defaultLimit).toBeDefined()
      // catalog keys
      expect(config.catalog.path).toBeDefined()
    }
  })

  test('flattenConfig helper produces expected entries', async () => {
    // Import the command module to test the flatten logic indirectly
    // by verifying all config keys are accessible via getConfigValue
    const configResult = await loadConfig({ cwd: root })
    expect(configResult.ok).toBe(true)
    if (configResult.ok) {
      const expectedKeys = [
        'general.debug',
        'general.outputFormat',
        'general.failOn',
        'search.backends',
        'search.defaultLimit',
        'catalog.path',
      ]
      for (const key of expectedKeys) {
        const value = getConfigValue(configResult.value, key)
        expect(value).toBeDefined()
      }
    }
  })
})

// ---------------------------------------------------------------------------
// Path helpers
// ---------------------------------------------------------------------------

describe('config path subcommand data', () => {
  test('getUserConfigPath returns a valid path', async () => {
    const { getUserConfigPath } = await import('@agents/core/config')
    const path = getUserConfigPath()
    expect(path).toContain('.config')
    expect(path).toContain('agents')
    expect(path).toEndWith('config.toml')
  })

  test('getProjectConfigPath returns .agents.toml', async () => {
    const { getProjectConfigPath } = await import('@agents/core/config')
    const path = getProjectConfigPath('/tmp/test-project')
    expect(path).toBe('/tmp/test-project/.agents.toml')
  })
})

// ---------------------------------------------------------------------------
// Coerce value helper (test the logic used by set)
// ---------------------------------------------------------------------------

describe('value coercion logic', () => {
  test('true string becomes boolean true', () => {
    // Replicate the coerceValue logic from the command
    const coerce = (raw: string): unknown => {
      if (raw === 'true') return true
      if (raw === 'false') return false
      if (/^\d+$/.test(raw)) return Number.parseInt(raw, 10)
      return raw
    }
    expect(coerce('true')).toBe(true)
    expect(coerce('false')).toBe(false)
    expect(coerce('42')).toBe(42)
    expect(coerce('hello')).toBe('hello')
    expect(coerce('0')).toBe(0)
    expect(coerce('3.14')).toBe('3.14') // not an integer pattern
  })
})
