/**
 * CLI configuration with TOML storage and layered precedence.
 *
 * Precedence (highest wins):
 *   1. CLI flags (--debug, --json, --fail-on)
 *   2. Environment variables (AGENTS_*)
 *   3. Project config (.agents.toml in project root)
 *   4. User config (~/.config/agents/config.toml)
 *   5. Built-in defaults
 *
 * This module provides the read/write foundation. The `agents config`
 * command (Phase 8) will build interactive set/get/list on top of this.
 */

import { homedir } from 'node:os'
import { join } from 'node:path'
import * as TOML from 'smol-toml'
import * as v from 'valibot'
import { pathExists, readTextFile, writeTextFile } from './file-io'
import { CliError, err, ok, type Result } from './types'

// ---------------------------------------------------------------------------
// Schema
// ---------------------------------------------------------------------------

/** All configurable CLI settings. */
export interface AgentsConfig {
  /** General settings */
  general: {
    /** Enable debug output (default: false) */
    debug: boolean
    /** Default output format: 'human' | 'json' (default: 'human') */
    outputFormat: 'human' | 'json'
    /** Minimum severity to fail on: 'error' | 'warning' | 'none' (default: 'error') */
    failOn: 'error' | 'warning' | 'none'
  }
  /** Search backend configuration */
  search: {
    /** Enabled search backends */
    backends: string[]
    /** Default result limit */
    defaultLimit: number
  }
  /** Catalog settings */
  catalog: {
    /** Path to catalog NDJSON file */
    path: string
  }
}

/** Default configuration values. */
export const DEFAULT_CONFIG: Readonly<AgentsConfig> = {
  general: {
    debug: false,
    outputFormat: 'human',
    failOn: 'error',
  },
  search: {
    backends: ['local', 'smithery'],
    defaultLimit: 10,
  },
  catalog: {
    path: 'content/skills/.catalog.ndjson',
  },
}

// ---------------------------------------------------------------------------
// Validation schema (snake_case keys matching TOML convention)
// ---------------------------------------------------------------------------

const GeneralSchema = v.object({
  debug: v.optional(v.boolean()),
  output_format: v.optional(v.picklist(['human', 'json'])),
  fail_on: v.optional(v.picklist(['error', 'warning', 'none'])),
})

const SearchSchema = v.object({
  backends: v.optional(v.array(v.string())),
  default_limit: v.optional(v.pipe(v.number(), v.integer(), v.minValue(1))),
})

const CatalogSchema = v.object({
  path: v.optional(v.string()),
})

export const AgentsConfigTomlSchema = v.object({
  general: v.optional(GeneralSchema),
  search: v.optional(SearchSchema),
  catalog: v.optional(CatalogSchema),
})

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------

/** Get the user-level config path (~/.config/agents/config.toml). */
export function getUserConfigPath(): string {
  return join(homedir(), '.config', 'agents', 'config.toml')
}

/** Get the project-level config path (.agents.toml in given directory). */
export function getProjectConfigPath(cwd?: string): string {
  return join(cwd ?? process.cwd(), '.agents.toml')
}

// ---------------------------------------------------------------------------
// Key transformation (TOML snake_case <-> TypeScript camelCase)
// ---------------------------------------------------------------------------

/** Convert camelCase key to snake_case for TOML convention. */
function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, (m) => '_' + m.toLowerCase())
}

/** Convert snake_case key to camelCase for internal use. */
function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
}

/** Recursively transform all keys in an object. */
function transformKeys(
  obj: Record<string, unknown>,
  fn: (key: string) => string
): Record<string, unknown> {
  const result: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(obj)) {
    const newKey = fn(key)
    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
      result[newKey] = transformKeys(value as Record<string, unknown>, fn)
    } else {
      result[newKey] = value
    }
  }
  return result
}

// ---------------------------------------------------------------------------
// Read / Write TOML
// ---------------------------------------------------------------------------

/** Read and parse a TOML config file. Returns partial config (only keys present in file). */
export async function readConfigFile(path: string): Promise<Result<Partial<AgentsConfig>>> {
  if (!pathExists(path)) {
    return ok({})
  }
  const text = await readTextFile(path)
  if (!text.ok) return text as Result<never>
  try {
    const raw = TOML.parse(text.value)
    // Validate against schema (lenient: strip unknown keys)
    const validated = v.safeParse(AgentsConfigTomlSchema, raw)
    if (!validated.success) {
      // Warn but continue with what we can parse
      const issues = validated.issues.map((i) => i.message).join('; ')
      console.error(`Warning: config validation issues in ${path}: ${issues}`)
    }
    const cleaned = validated.success ? validated.output : raw
    // Transform snake_case TOML keys to camelCase
    const transformed = transformKeys(cleaned as Record<string, unknown>, snakeToCamel)
    return ok(transformed as Partial<AgentsConfig>)
  } catch (e) {
    return err(
      new CliError(
        `Failed to parse TOML config at ${path}: ${e instanceof Error ? e.message : String(e)}`,
        'E_PARSE_CONFIG'
      )
    )
  }
}

/** Write a partial config to a TOML file. */
export async function writeConfigFile(
  path: string,
  config: Partial<AgentsConfig>
): Promise<Result<void>> {
  try {
    const snakeCased = transformKeys(config as Record<string, unknown>, camelToSnake)
    const content = TOML.stringify(snakeCased)
    return writeTextFile(path, content)
  } catch (e) {
    return err(
      new CliError(
        `Failed to write config to ${path}: ${e instanceof Error ? e.message : String(e)}`,
        'E_WRITE_CONFIG'
      )
    )
  }
}

// ---------------------------------------------------------------------------
// Environment variable mapping
// ---------------------------------------------------------------------------

/** Map of env vars to config paths. */
const ENV_MAP: Record<string, string> = {
  AGENTS_DEBUG: 'general.debug',
  AGENTS_OUTPUT: 'general.outputFormat',
  AGENTS_FAIL_ON: 'general.failOn',
  AGENTS_SEARCH_BACKENDS: 'search.backends',
  AGENTS_SEARCH_LIMIT: 'search.defaultLimit',
  AGENTS_CATALOG_PATH: 'catalog.path',
}

/** Read config values from environment variables. */
export function readEnvConfig(): Partial<AgentsConfig> {
  const config: Record<string, unknown> = {}

  for (const [envVar, configPath] of Object.entries(ENV_MAP)) {
    const value = process.env[envVar]
    if (value === undefined) continue

    const parts = configPath.split('.')
    let current: Record<string, unknown> = config
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i]!
      if (!current[part]) current[part] = {}
      current = current[part] as Record<string, unknown>
    }

    const key = parts[parts.length - 1]!
    // Type coercion for known types
    if (value === 'true') current[key] = true
    else if (value === 'false') current[key] = false
    else if (/^\d+$/.test(value)) current[key] = Number.parseInt(value, 10)
    else if (value.includes(',')) current[key] = value.split(',').map((s) => s.trim())
    else current[key] = value
  }

  return config as Partial<AgentsConfig>
}

// ---------------------------------------------------------------------------
// Merged configuration
// ---------------------------------------------------------------------------

/** Deep merge utility: source values override target values. */
export function deepMerge<T extends Record<string, unknown>>(target: T, source: Partial<T>): T {
  const result = { ...target }
  for (const [key, value] of Object.entries(source)) {
    if (value !== undefined && value !== null) {
      if (
        typeof value === 'object' &&
        !Array.isArray(value) &&
        typeof (result as Record<string, unknown>)[key] === 'object'
      ) {
        ;(result as Record<string, unknown>)[key] = deepMerge(
          (result as Record<string, unknown>)[key] as Record<string, unknown>,
          value as Record<string, unknown>
        )
      } else {
        ;(result as Record<string, unknown>)[key] = value
      }
    }
  }
  return result
}

/**
 * Load the fully resolved configuration using the precedence chain.
 *
 * Reads: defaults -> user config -> project config -> env vars
 * CLI flags are NOT applied here -- they override at the command handler level.
 */
export async function loadConfig(opts?: { cwd?: string }): Promise<Result<AgentsConfig>> {
  let config: AgentsConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG)) as AgentsConfig

  // Layer 1: User config (~/.config/agents/config.toml)
  const userPath = getUserConfigPath()
  const userConfig = await readConfigFile(userPath)
  if (!userConfig.ok) {
    console.error(
      `Warning: Failed to parse user config at ${userPath}: ${userConfig.error.message}`
    )
  } else if (Object.keys(userConfig.value).length > 0) {
    config = deepMerge(config, userConfig.value)
  }

  // Layer 2: Project config (.agents.toml)
  const projectPath = getProjectConfigPath(opts?.cwd)
  const projectConfig = await readConfigFile(projectPath)
  if (!projectConfig.ok) {
    console.error(
      `Warning: Failed to parse project config at ${projectPath}: ${projectConfig.error.message}`
    )
  } else if (Object.keys(projectConfig.value).length > 0) {
    config = deepMerge(config, projectConfig.value)
  }

  // Layer 3: Environment variables
  const envConfig = readEnvConfig()
  if (Object.keys(envConfig).length > 0) {
    config = deepMerge(config, envConfig)
  }

  return ok(config)
}

/**
 * Get a single config value by dotted path (e.g., 'general.debug').
 * Returns the value or undefined if not found.
 */
export function getConfigValue(config: AgentsConfig, path: string): unknown {
  const parts = path.split('.')
  let current: unknown = config
  for (const part of parts) {
    if (current === null || current === undefined || typeof current !== 'object') return undefined
    current = (current as Record<string, unknown>)[part]
  }
  return current
}

/**
 * Set a single config value by dotted path.
 * Returns a new config object (does not mutate the original).
 */
export function setConfigValue(config: AgentsConfig, path: string, value: unknown): AgentsConfig {
  const parts = path.split('.')
  const result = JSON.parse(JSON.stringify(config)) as AgentsConfig
  let current: Record<string, unknown> = result as unknown as Record<string, unknown>
  for (let i = 0; i < parts.length - 1; i++) {
    const part = parts[i]!
    if (!current[part] || typeof current[part] !== 'object') {
      current[part] = {}
    }
    current = current[part] as Record<string, unknown>
  }
  current[parts[parts.length - 1]!] = value
  return result
}
