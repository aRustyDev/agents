/**
 * CLI configuration management.
 *
 * Subcommands:
 *   get <key>          - Show a config value
 *   set <key> <value>  - Set a config value
 *   list               - Show all config values with sources
 *   edit               - Open config in $EDITOR
 *   path               - Show config file paths
 */
import { execSync } from 'node:child_process'
import { defineCommand } from 'citty'
import {
  DEFAULT_CONFIG,
  getConfigValue,
  getProjectConfigPath,
  getUserConfigPath,
  loadConfig,
  readConfigFile,
  setConfigValue,
  writeConfigFile,
} from '../lib/config'
import { pathExists } from '../lib/file-io'
import { createOutput } from '../lib/output'
import { EXIT } from '../lib/types'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Auto-detect value type from CLI string input. */
function coerceValue(raw: string): unknown {
  if (raw === 'true') return true
  if (raw === 'false') return false
  if (/^\d+$/.test(raw)) return Number.parseInt(raw, 10)
  return raw
}

/** Flatten a nested config object into dotted-key/value pairs. */
function flattenConfig(
  obj: Record<string, unknown>,
  prefix = ''
): Array<{ key: string; value: unknown }> {
  const entries: Array<{ key: string; value: unknown }> = []
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key
    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
      entries.push(...flattenConfig(value as Record<string, unknown>, fullKey))
    } else {
      entries.push({ key: fullKey, value })
    }
  }
  return entries
}

/**
 * Determine the source of each config value by comparing against layers.
 * Returns 'project', 'user', or 'default'.
 */
function determineSource(
  key: string,
  projectConfig: Record<string, unknown>,
  userConfig: Record<string, unknown>
): string {
  // Check project config
  const parts = key.split('.')
  let current: unknown = projectConfig
  for (const part of parts) {
    if (current === null || current === undefined || typeof current !== 'object') {
      current = undefined
      break
    }
    current = (current as Record<string, unknown>)[part]
  }
  if (current !== undefined) return 'project'

  // Check user config
  current = userConfig
  for (const part of parts) {
    if (current === null || current === undefined || typeof current !== 'object') {
      current = undefined
      break
    }
    current = (current as Record<string, unknown>)[part]
  }
  if (current !== undefined) return 'user'

  return 'default'
}

// ---------------------------------------------------------------------------
// Command definition
// ---------------------------------------------------------------------------

export default defineCommand({
  meta: { name: 'config', description: 'Manage CLI configuration' },
  subCommands: {
    // ----- get -----
    get: defineCommand({
      meta: { name: 'get', description: 'Show a config value' },
      args: {
        ...globalArgs,
        key: {
          type: 'positional',
          description: 'Config key (dotted path, e.g. general.debug)',
          required: true,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const configResult = await loadConfig()
        if (!configResult.ok) {
          out.error(configResult.error.message)
          process.exit(EXIT.ERROR)
        }

        const value = getConfigValue(configResult.value, args.key as string)
        if (value === undefined) {
          out.error(`Unknown config key: ${args.key}`)
          process.exit(EXIT.ERROR)
        }

        if (args.json) {
          out.raw(value)
        } else {
          out.info(`${args.key} = ${JSON.stringify(value)}`)
        }
      },
    }),

    // ----- set -----
    set: defineCommand({
      meta: { name: 'set', description: 'Set a config value' },
      args: {
        ...globalArgs,
        key: {
          type: 'positional',
          description: 'Config key (dotted path, e.g. general.debug)',
          required: true,
        },
        value: {
          type: 'positional',
          description: 'Value to set',
          required: true,
        },
        global: {
          type: 'boolean',
          description: 'Write to user config (~/.config/agents/config.toml) instead of project',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const key = args.key as string
        const rawValue = args.value as string
        const isGlobal = args.global as boolean

        const filePath = isGlobal ? getUserConfigPath() : getProjectConfigPath()

        // Read existing file config (partial)
        const existingResult = await readConfigFile(filePath)
        if (!existingResult.ok) {
          out.error(existingResult.error.message)
          process.exit(EXIT.ERROR)
        }

        const coerced = coerceValue(rawValue)

        // Apply the change using setConfigValue on a full config, then extract the partial
        // We need to work with the partial config from the file, not the merged one
        const existing = existingResult.value
        // Build a minimal config with defaults so setConfigValue can navigate the path
        const tempConfig = JSON.parse(JSON.stringify(DEFAULT_CONFIG))
        // Merge existing file values on top
        for (const [section, values] of Object.entries(existing)) {
          if (typeof values === 'object' && values !== null) {
            tempConfig[section] = { ...tempConfig[section], ...values }
          }
        }
        const updated = setConfigValue(tempConfig, key, coerced)

        // Extract only the sections that were in the file or contain the new key
        const topSection = key.split('.')[0] ?? ''
        const partialToWrite: Record<string, unknown> = {}
        // Keep all existing sections
        for (const section of Object.keys(existing)) {
          partialToWrite[section] = (updated as Record<string, unknown>)[section]
        }
        // Ensure the section containing the new key is included
        if (!partialToWrite[topSection]) {
          partialToWrite[topSection] = (updated as Record<string, unknown>)[topSection]
        }

        const writeResult = await writeConfigFile(filePath, partialToWrite)
        if (!writeResult.ok) {
          out.error(writeResult.error.message)
          process.exit(EXIT.ERROR)
        }

        if (args.json) {
          out.raw({ key, value: coerced, file: filePath })
        } else {
          out.success(`Set ${key} = ${JSON.stringify(coerced)} in ${filePath}`)
        }
      },
    }),

    // ----- list -----
    list: defineCommand({
      meta: { name: 'list', description: 'Show all config values with sources' },
      args: {
        ...globalArgs,
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

        const configResult = await loadConfig()
        if (!configResult.ok) {
          out.error(configResult.error.message)
          process.exit(EXIT.ERROR)
        }

        if (args.json) {
          out.raw(configResult.value)
          return
        }

        // Read individual layers for source attribution
        const userConfigResult = await readConfigFile(getUserConfigPath())
        const projectConfigResult = await readConfigFile(getProjectConfigPath())

        const userConfig = userConfigResult.ok
          ? (userConfigResult.value as Record<string, unknown>)
          : {}
        const projectConfig = projectConfigResult.ok
          ? (projectConfigResult.value as Record<string, unknown>)
          : {}

        const flat = flattenConfig(configResult.value as unknown as Record<string, unknown>)
        const rows = flat.map((entry) => ({
          key: entry.key,
          value: JSON.stringify(entry.value),
          source: determineSource(entry.key, projectConfig, userConfig),
        }))

        out.table(rows, ['key', 'value', 'source'])
      },
    }),

    // ----- edit -----
    edit: defineCommand({
      meta: { name: 'edit', description: 'Open config file in $EDITOR' },
      args: {
        ...globalArgs,
        global: {
          type: 'boolean',
          description: 'Edit user config (~/.config/agents/config.toml) instead of project',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const isGlobal = args.global as boolean
        const filePath = isGlobal ? getUserConfigPath() : getProjectConfigPath()

        // Create file with defaults if it doesn't exist
        if (!pathExists(filePath)) {
          const writeResult = await writeConfigFile(filePath, DEFAULT_CONFIG)
          if (!writeResult.ok) {
            out.error(writeResult.error.message)
            process.exit(EXIT.ERROR)
          }
          out.info(`Created ${filePath} with defaults`)
        }

        const editor = process.env.EDITOR || 'vi'
        try {
          execSync(`${editor} ${filePath}`, { stdio: 'inherit' })
        } catch (e) {
          out.error(`Failed to open editor: ${e instanceof Error ? e.message : String(e)}`)
          process.exit(EXIT.ERROR)
        }
      },
    }),

    // ----- path -----
    path: defineCommand({
      meta: { name: 'path', description: 'Show config file paths' },
      args: {
        ...globalArgs,
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })

        const userPath = getUserConfigPath()
        const projectPath = getProjectConfigPath()
        const userExists = pathExists(userPath)
        const projectExists = pathExists(projectPath)

        if (args.json) {
          out.raw({
            user: { path: userPath, exists: userExists },
            project: { path: projectPath, exists: projectExists },
          })
          return
        }

        out.info(`User config:    ${userPath} ${userExists ? '(exists)' : '(not found)'}`)
        out.info(`Project config: ${projectPath} ${projectExists ? '(exists)' : '(not found)'}`)
      },
    }),
  },
})
