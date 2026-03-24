import { afterAll, afterEach, beforeAll, describe, expect, test } from 'bun:test'
import { mkdtemp, realpath, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  DEFAULT_CONFIG,
  deepMerge,
  getConfigValue,
  getProjectConfigPath,
  getUserConfigPath,
  loadConfig,
  readConfigFile,
  readEnvConfig,
  setConfigValue,
  writeConfigFile,
  type AgentsConfig,
} from '../../src/lib/config'
import { writeTextFile } from '../../src/lib/file-io'

// ---------------------------------------------------------------------------
// Shared fixture directory
// ---------------------------------------------------------------------------

let root: string

beforeAll(async () => {
  root = await realpath(await mkdtemp(join(tmpdir(), 'config-test-')))
})

afterAll(async () => {
  await rm(root, { recursive: true, force: true })
})

// Clean up env vars after each test
const envVarsToClean = [
  'AGENTS_DEBUG',
  'AGENTS_OUTPUT',
  'AGENTS_FAIL_ON',
  'AGENTS_SEARCH_BACKENDS',
  'AGENTS_SEARCH_LIMIT',
  'AGENTS_CATALOG_PATH',
]

afterEach(() => {
  for (const key of envVarsToClean) {
    delete process.env[key]
  }
})

// ---------------------------------------------------------------------------
// DEFAULT_CONFIG
// ---------------------------------------------------------------------------

describe('DEFAULT_CONFIG', () => {
  test('has expected shape', () => {
    expect(DEFAULT_CONFIG.general).toBeDefined()
    expect(DEFAULT_CONFIG.general.debug).toBe(false)
    expect(DEFAULT_CONFIG.general.outputFormat).toBe('human')
    expect(DEFAULT_CONFIG.general.failOn).toBe('error')
    expect(DEFAULT_CONFIG.search).toBeDefined()
    expect(DEFAULT_CONFIG.search.backends).toEqual(['local', 'smithery'])
    expect(DEFAULT_CONFIG.search.defaultLimit).toBe(10)
    expect(DEFAULT_CONFIG.catalog).toBeDefined()
    expect(DEFAULT_CONFIG.catalog.path).toBe('content/skills/.catalog.ndjson')
  })
})

// ---------------------------------------------------------------------------
// Path helpers
// ---------------------------------------------------------------------------

describe('getUserConfigPath', () => {
  test('returns path under ~/.config/agents/', () => {
    const path = getUserConfigPath()
    expect(path).toContain('.config')
    expect(path).toContain('agents')
    expect(path).toEndWith('config.toml')
  })
})

describe('getProjectConfigPath', () => {
  test('returns .agents.toml in given directory', () => {
    const path = getProjectConfigPath('/some/project')
    expect(path).toBe('/some/project/.agents.toml')
  })

  test('defaults to cwd when no argument given', () => {
    const path = getProjectConfigPath()
    expect(path).toEndWith('.agents.toml')
    expect(path).toContain(process.cwd())
  })
})

// ---------------------------------------------------------------------------
// readConfigFile / writeConfigFile
// ---------------------------------------------------------------------------

describe('readConfigFile', () => {
  test('returns empty object for missing file', async () => {
    const result = await readConfigFile(join(root, 'missing.toml'))
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toEqual({})
    }
  })

  test('parses valid TOML with snake_case keys', async () => {
    const path = join(root, 'valid.toml')
    await writeTextFile(path, '[general]\ndebug = true\noutput_format = "json"\n')

    const result = await readConfigFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect((result.value as AgentsConfig).general?.debug).toBe(true)
      expect((result.value as AgentsConfig).general?.outputFormat).toBe('json')
    }
  })

  test('returns error for invalid TOML', async () => {
    const path = join(root, 'invalid.toml')
    await writeTextFile(path, '[general\ndebug = true')

    const result = await readConfigFile(path)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_PARSE_CONFIG')
    }
  })
})

describe('writeConfigFile', () => {
  test('writes and round-trips correctly', async () => {
    const path = join(root, 'roundtrip.toml')
    const config: Partial<AgentsConfig> = {
      general: {
        debug: true,
        outputFormat: 'json',
        failOn: 'warning',
      },
      search: {
        backends: ['local'],
        defaultLimit: 20,
      },
    }

    const writeResult = await writeConfigFile(path, config)
    expect(writeResult.ok).toBe(true)

    const readResult = await readConfigFile(path)
    expect(readResult.ok).toBe(true)
    if (readResult.ok) {
      const parsed = readResult.value as AgentsConfig
      expect(parsed.general?.debug).toBe(true)
      expect(parsed.general?.outputFormat).toBe('json')
      expect(parsed.general?.failOn).toBe('warning')
      expect(parsed.search?.backends).toEqual(['local'])
      expect(parsed.search?.defaultLimit).toBe(20)
    }
  })

  test('produces snake_case keys in TOML output', async () => {
    const path = join(root, 'snake-output.toml')
    const config: Partial<AgentsConfig> = {
      general: {
        debug: false,
        outputFormat: 'json',
        failOn: 'warning',
      },
      search: {
        backends: ['local'],
        defaultLimit: 25,
      },
    }

    await writeConfigFile(path, config)
    const raw = await (await import('../../src/lib/file-io')).readTextFile(path)
    expect(raw.ok).toBe(true)
    if (raw.ok) {
      expect(raw.value).toContain('output_format')
      expect(raw.value).toContain('fail_on')
      expect(raw.value).toContain('default_limit')
      // Should NOT contain camelCase keys
      expect(raw.value).not.toContain('outputFormat')
      expect(raw.value).not.toContain('failOn')
      expect(raw.value).not.toContain('defaultLimit')
    }
  })
})

describe('readConfigFile snake_case support', () => {
  test('reads snake_case TOML and maps to camelCase', async () => {
    const path = join(root, 'snake-input.toml')
    await writeTextFile(path, '[general]\noutput_format = "json"\nfail_on = "warning"\n\n[search]\ndefault_limit = 42\n')

    const result = await readConfigFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      const parsed = result.value as AgentsConfig
      expect(parsed.general?.outputFormat).toBe('json')
      expect(parsed.general?.failOn).toBe('warning')
      expect(parsed.search?.defaultLimit).toBe(42)
    }
  })
})

// ---------------------------------------------------------------------------
// readEnvConfig
// ---------------------------------------------------------------------------

describe('readEnvConfig', () => {
  test('returns empty object when no env vars set', () => {
    const config = readEnvConfig()
    expect(Object.keys(config).length).toBe(0)
  })

  test('picks up boolean env var', () => {
    process.env.AGENTS_DEBUG = 'true'
    const config = readEnvConfig() as AgentsConfig
    expect(config.general?.debug).toBe(true)
  })

  test('coerces false string to boolean', () => {
    process.env.AGENTS_DEBUG = 'false'
    const config = readEnvConfig() as AgentsConfig
    expect(config.general?.debug).toBe(false)
  })

  test('coerces numeric string to number', () => {
    process.env.AGENTS_SEARCH_LIMIT = '25'
    const config = readEnvConfig() as AgentsConfig
    expect(config.search?.defaultLimit).toBe(25)
  })

  test('splits comma-separated values into array', () => {
    process.env.AGENTS_SEARCH_BACKENDS = 'local, smithery, custom'
    const config = readEnvConfig() as AgentsConfig
    expect(config.search?.backends).toEqual(['local', 'smithery', 'custom'])
  })

  test('reads string value directly', () => {
    process.env.AGENTS_OUTPUT = 'json'
    const config = readEnvConfig() as AgentsConfig
    expect(config.general?.outputFormat).toBe('json')
  })
})

// ---------------------------------------------------------------------------
// deepMerge
// ---------------------------------------------------------------------------

describe('deepMerge', () => {
  test('merges nested objects', () => {
    const target = { a: { b: 1, c: 2 }, d: 3 }
    const source = { a: { b: 10 } }
    const result = deepMerge(target, source)
    expect(result).toEqual({ a: { b: 10, c: 2 }, d: 3 })
  })

  test('does not mutate target', () => {
    const target = { a: { b: 1 } }
    const original = JSON.parse(JSON.stringify(target))
    deepMerge(target, { a: { b: 99 } })
    expect(target).toEqual(original)
  })

  test('replaces arrays (not deep merging)', () => {
    const target = { arr: [1, 2, 3] } as Record<string, unknown>
    const source = { arr: [4, 5] } as Record<string, unknown>
    const result = deepMerge(target, source)
    expect(result.arr).toEqual([4, 5])
  })

  test('ignores undefined and null values', () => {
    const target = { a: 1, b: 2 } as Record<string, unknown>
    const source = { a: undefined, b: null } as Record<string, unknown>
    const result = deepMerge(target, source)
    expect(result.a).toBe(1)
    expect(result.b).toBe(2)
  })
})

// ---------------------------------------------------------------------------
// loadConfig
// ---------------------------------------------------------------------------

describe('loadConfig', () => {
  test('returns defaults when no config files or env vars exist', async () => {
    const dir = join(root, 'empty-project')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(dir, { recursive: true })

    const result = await loadConfig({ cwd: dir })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.general.debug).toBe(false)
      expect(result.value.general.outputFormat).toBe('human')
      expect(result.value.search.defaultLimit).toBe(10)
    }
  })

  test('project config overrides defaults', async () => {
    const dir = join(root, 'project-override')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(dir, { recursive: true })

    await writeTextFile(
      join(dir, '.agents.toml'),
      '[general]\ndebug = true\n\n[search]\ndefault_limit = 50\n'
    )

    const result = await loadConfig({ cwd: dir })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.general.debug).toBe(true)
      expect(result.value.search.defaultLimit).toBe(50)
      // Other values stay at defaults
      expect(result.value.general.outputFormat).toBe('human')
    }
  })

  test('env vars override project config', async () => {
    const dir = join(root, 'env-override')
    const { mkdir } = await import('node:fs/promises')
    await mkdir(dir, { recursive: true })

    await writeTextFile(
      join(dir, '.agents.toml'),
      '[general]\ndebug = false\n'
    )

    process.env.AGENTS_DEBUG = 'true'

    const result = await loadConfig({ cwd: dir })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.general.debug).toBe(true)
    }
  })
})

// ---------------------------------------------------------------------------
// getConfigValue
// ---------------------------------------------------------------------------

describe('getConfigValue', () => {
  test('retrieves nested value by dotted path', () => {
    expect(getConfigValue(DEFAULT_CONFIG, 'general.debug')).toBe(false)
    expect(getConfigValue(DEFAULT_CONFIG, 'search.defaultLimit')).toBe(10)
    expect(getConfigValue(DEFAULT_CONFIG, 'catalog.path')).toBe('content/skills/.catalog.ndjson')
  })

  test('returns undefined for non-existent path', () => {
    expect(getConfigValue(DEFAULT_CONFIG, 'general.nonexistent')).toBeUndefined()
    expect(getConfigValue(DEFAULT_CONFIG, 'no.such.path')).toBeUndefined()
  })

  test('retrieves top-level section', () => {
    const section = getConfigValue(DEFAULT_CONFIG, 'general')
    expect(section).toEqual({
      debug: false,
      outputFormat: 'human',
      failOn: 'error',
    })
  })
})

// ---------------------------------------------------------------------------
// setConfigValue
// ---------------------------------------------------------------------------

describe('setConfigValue', () => {
  test('sets nested value by dotted path', () => {
    const updated = setConfigValue(DEFAULT_CONFIG as AgentsConfig, 'general.debug', true)
    expect(updated.general.debug).toBe(true)
  })

  test('does not mutate original config', () => {
    const original = JSON.parse(JSON.stringify(DEFAULT_CONFIG)) as AgentsConfig
    const updated = setConfigValue(original, 'general.debug', true)
    expect(original.general.debug).toBe(false)
    expect(updated.general.debug).toBe(true)
  })

  test('sets deeply nested new path', () => {
    const config = JSON.parse(JSON.stringify(DEFAULT_CONFIG)) as AgentsConfig
    const updated = setConfigValue(config, 'search.defaultLimit', 99)
    expect(updated.search.defaultLimit).toBe(99)
    expect(config.search.defaultLimit).toBe(10)
  })

  test('creates intermediate objects if needed', () => {
    const config = JSON.parse(JSON.stringify(DEFAULT_CONFIG)) as AgentsConfig
    // Force a missing intermediate
    ;(config as Record<string, unknown>).newSection = undefined
    const updated = setConfigValue(config, 'newSection.key', 'value')
    expect((updated as Record<string, unknown> & { newSection: { key: string } }).newSection.key).toBe('value')
  })
})
