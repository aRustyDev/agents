/**
 * Client config I/O -- read/write MCP server entries in AI client config files.
 *
 * Supports JSON, JSONC (comments stripped without external deps), and YAML formats.
 */

import { existsSync, mkdirSync } from 'node:fs'
import { readFile, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import { CliError, err, ok, type Result } from '../types'
import { type ClientTransport, getClientConfig, getConfigPath } from './clients'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface McpServerEntry {
  readonly name: string
  readonly transport: ClientTransport
  readonly url?: string
  readonly command?: string
  readonly args?: string[]
  readonly env?: Record<string, string>
}

// ---------------------------------------------------------------------------
// JSON / JSONC / YAML helpers (exported for testability)
// ---------------------------------------------------------------------------

/**
 * Strip single-line (`//`) and block (`/* ... *​/`) comments from JSONC text.
 *
 * This is intentionally simple: it does NOT attempt to handle `//` or `/*`
 * that appear inside JSON string values. For the config files we target
 * (Claude Desktop, Cursor, OpenCode, ...) this is perfectly adequate.
 */
export function stripJsonComments(text: string): string {
  // Remove block comments first (they may span lines)
  let result = text.replace(/\/\*[\s\S]*?\*\//g, '')
  // Then remove single-line comments
  result = result.replace(/\/\/.*$/gm, '')
  return result
}

export async function readJsonFile(path: string): Promise<Result<Record<string, unknown>>> {
  try {
    const raw = await readFile(path, 'utf-8')
    return ok(JSON.parse(raw))
  } catch (e) {
    return err(
      new CliError(
        `Failed to read JSON: ${path}`,
        'E_READ_FAILED',
        e instanceof Error ? e.message : String(e)
      )
    )
  }
}

export async function readJsoncFile(path: string): Promise<Result<Record<string, unknown>>> {
  try {
    const raw = await readFile(path, 'utf-8')
    return ok(JSON.parse(stripJsonComments(raw)))
  } catch (e) {
    return err(
      new CliError(
        `Failed to read JSONC: ${path}`,
        'E_READ_FAILED',
        e instanceof Error ? e.message : String(e)
      )
    )
  }
}

export async function readYamlFile(path: string): Promise<Result<Record<string, unknown>>> {
  try {
    const yaml = await import('js-yaml')
    const raw = await readFile(path, 'utf-8')
    const data = yaml.load(raw)
    if (typeof data !== 'object' || data === null) return ok({})
    return ok(data as Record<string, unknown>)
  } catch (e) {
    return err(
      new CliError(
        `Failed to read YAML: ${path}`,
        'E_READ_FAILED',
        e instanceof Error ? e.message : String(e)
      )
    )
  }
}

export async function writeJsonFile(
  path: string,
  data: Record<string, unknown>
): Promise<Result<void>> {
  try {
    mkdirSync(dirname(path), { recursive: true })
    await writeFile(path, `${JSON.stringify(data, null, 2)}\n`)
    return ok(undefined)
  } catch (e) {
    return err(
      new CliError(
        `Failed to write: ${path}`,
        'E_WRITE_FAILED',
        e instanceof Error ? e.message : String(e)
      )
    )
  }
}

export async function writeYamlFile(
  path: string,
  data: Record<string, unknown>
): Promise<Result<void>> {
  try {
    const yaml = await import('js-yaml')
    mkdirSync(dirname(path), { recursive: true })
    await writeFile(path, yaml.dump(data, { lineWidth: 120 }))
    return ok(undefined)
  } catch (e) {
    return err(
      new CliError(
        `Failed to write YAML: ${path}`,
        'E_WRITE_FAILED',
        e instanceof Error ? e.message : String(e)
      )
    )
  }
}

// ---------------------------------------------------------------------------
// Format dispatch
// ---------------------------------------------------------------------------

export function readConfigFile(
  path: string,
  format: string
): Promise<Result<Record<string, unknown>>> {
  switch (format) {
    case 'yaml':
      return readYamlFile(path)
    case 'jsonc':
      return readJsoncFile(path)
    default:
      return readJsonFile(path)
  }
}

export function writeConfigFile(
  path: string,
  format: string,
  data: Record<string, unknown>
): Promise<Result<void>> {
  switch (format) {
    case 'yaml':
      return writeYamlFile(path, data)
    default:
      return writeJsonFile(path, data)
  }
}

// ---------------------------------------------------------------------------
// MCP server entry formatting
// ---------------------------------------------------------------------------

export function formatServerConfig(entry: McpServerEntry): Record<string, unknown> {
  if (entry.transport === 'stdio') {
    return {
      command: entry.command ?? '',
      args: entry.args ?? [],
      ...(entry.env && Object.keys(entry.env).length > 0 ? { env: entry.env } : {}),
    }
  }
  // http or http-oauth
  return {
    type: entry.transport === 'http-oauth' ? 'http' : entry.transport,
    url: entry.url ?? '',
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/** Read the full client config file. Returns `{}` when the file does not exist. */
export async function readClientConfig(clientId: string): Promise<Result<Record<string, unknown>>> {
  const client = getClientConfig(clientId)
  if (!client) return err(new CliError(`Unknown client: ${clientId}`, 'E_UNKNOWN_CLIENT'))
  if (client.installMethod !== 'file')
    return err(new CliError(`Client ${clientId} uses command-based install`, 'E_COMMAND_CLIENT'))

  const path = getConfigPath(client)
  if (!path)
    return err(new CliError(`No config path for ${clientId} on this platform`, 'E_NO_PATH'))
  if (!existsSync(path)) return ok({}) // missing file = empty config

  return readConfigFile(path, client.format ?? 'json')
}

/** Write an MCP server entry to a client's config file. */
export async function writeServerToClient(
  clientId: string,
  serverName: string,
  entry: McpServerEntry
): Promise<Result<void>> {
  const client = getClientConfig(clientId)
  if (!client) return err(new CliError(`Unknown client: ${clientId}`, 'E_UNKNOWN_CLIENT'))
  if (client.installMethod !== 'file')
    return err(new CliError(`Client ${clientId} uses command-based install`, 'E_COMMAND_CLIENT'))

  const path = getConfigPath(client)
  if (!path)
    return err(new CliError(`No config path for ${clientId} on this platform`, 'E_NO_PATH'))

  // Read existing config (or start with empty object)
  const existing = existsSync(path)
    ? await readConfigFile(path, client.format ?? 'json')
    : ok({} as Record<string, unknown>)
  if (!existing.ok) return err(existing.error)

  const config = existing.value

  // Determine the servers key (most clients use "mcpServers", some vary)
  const serversKey = client.fieldOverrides?.mcpServers ?? 'mcpServers'
  const servers = (config[serversKey] ?? {}) as Record<string, unknown>
  servers[serverName] = formatServerConfig(entry)
  config[serversKey] = servers

  return writeConfigFile(path, client.format ?? 'json', config)
}

/** Remove an MCP server entry from a client's config file. */
export async function removeServerFromClient(
  clientId: string,
  serverName: string
): Promise<Result<void>> {
  const client = getClientConfig(clientId)
  if (!client) return err(new CliError(`Unknown client: ${clientId}`, 'E_UNKNOWN_CLIENT'))
  if (client.installMethod !== 'file')
    return err(new CliError(`Client ${clientId} uses command-based install`, 'E_COMMAND_CLIENT'))

  const path = getConfigPath(client)
  if (!path || !existsSync(path)) return ok(undefined) // nothing to remove

  const existing = await readConfigFile(path, client.format ?? 'json')
  if (!existing.ok) return err(existing.error)

  const config = existing.value
  const serversKey = client.fieldOverrides?.mcpServers ?? 'mcpServers'
  const servers = (config[serversKey] ?? {}) as Record<string, unknown>
  delete servers[serverName]
  config[serversKey] = servers

  return writeConfigFile(path, client.format ?? 'json', config)
}

/** List MCP server entries from a client's config file. */
export async function listServersInClient(clientId: string): Promise<Result<McpServerEntry[]>> {
  const configResult = await readClientConfig(clientId)
  if (!configResult.ok) return err(configResult.error)

  const config = configResult.value
  const client = getClientConfig(clientId)!
  const serversKey = client.fieldOverrides?.mcpServers ?? 'mcpServers'
  const servers = (config[serversKey] ?? {}) as Record<string, Record<string, unknown>>

  return ok(
    Object.entries(servers).map(([name, entry]) => ({
      name,
      transport: (entry.type === 'http'
        ? 'http'
        : entry.command
          ? 'stdio'
          : 'http') as ClientTransport,
      url: entry.url as string | undefined,
      command: entry.command as string | undefined,
      args: Array.isArray(entry.args) ? entry.args.map(String) : undefined,
      env:
        typeof entry.env === 'object' && entry.env !== null
          ? (entry.env as Record<string, string>)
          : undefined,
    }))
  )
}
