/**
 * Static registry of AI client definitions.
 *
 * Each entry describes an AI-powered IDE or CLI tool that can consume MCP
 * servers. The registry captures config file paths (per OS), the config
 * file format, and which MCP transport protocols the client supports.
 *
 * Data sourced from Smithery CLI's `config/clients.ts`.
 */

import { homedir, platform } from 'node:os'
import { join } from 'node:path'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type ClientTransport = 'stdio' | 'http' | 'http-oauth'
export type ClientFormat = 'json' | 'jsonc' | 'yaml'
export type InstallMethod = 'file' | 'command'

export interface ClientConfig {
  readonly id: string
  readonly displayName: string
  readonly installMethod: InstallMethod
  readonly format?: ClientFormat
  readonly configPaths: {
    readonly darwin?: string
    readonly win32?: string
    readonly linux?: string
  }
  /** Shell command template for command-based clients (e.g. "claude mcp add"). */
  readonly command?: string
  readonly supportedTransports: readonly ClientTransport[]
  /** JSON key overrides when the client uses non-standard field names. */
  readonly fieldOverrides?: Record<string, string>
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Platform-specific Application Support / AppData / config path fragments. */
const HOME = '~'

/** macOS: ~/Library/Application Support/<app> */
const macAppSupport = (app: string, file: string): string =>
  `${HOME}/Library/Application Support/${app}/${file}`

/** Windows: %APPDATA%/<app> (stored as ~/AppData/Roaming/<app>) */
const winAppData = (app: string, file: string): string => `${HOME}/AppData/Roaming/${app}/${file}`

/** Linux (and fallback): ~/.config/<app> */
const linuxConfig = (app: string, file: string): string => `${HOME}/.config/${app}/${file}`

/** VS Code globalStorage path (extensions store settings here) */
const vscodeGlobalStorage = (
  extensionId: string,
  settingsDir: string,
  file: string
): {
  darwin: string
  win32: string
  linux: string
} => ({
  darwin: macAppSupport('Code/User/globalStorage', `${extensionId}/${settingsDir}/${file}`),
  win32: winAppData('Code/User/globalStorage', `${extensionId}/${settingsDir}/${file}`),
  linux: linuxConfig('Code/User/globalStorage', `${extensionId}/${settingsDir}/${file}`),
})

// ---------------------------------------------------------------------------
// Client definitions
// ---------------------------------------------------------------------------

const clients: readonly ClientConfig[] = [
  // -- Claude Desktop -------------------------------------------------------
  {
    id: 'claude-desktop',
    displayName: 'Claude Desktop',
    installMethod: 'file',
    format: 'json',
    configPaths: {
      darwin: macAppSupport('Claude', 'claude_desktop_config.json'),
      win32: winAppData('Claude', 'claude_desktop_config.json'),
      linux: linuxConfig('Claude', 'claude_desktop_config.json'),
    },
    supportedTransports: ['stdio', 'http-oauth'],
  },

  // -- Claude Code ----------------------------------------------------------
  {
    id: 'claude-code',
    displayName: 'Claude Code',
    installMethod: 'command',
    configPaths: {},
    command: 'claude mcp add',
    supportedTransports: ['stdio', 'http', 'http-oauth'],
  },

  // -- Cursor ---------------------------------------------------------------
  {
    id: 'cursor',
    displayName: 'Cursor',
    installMethod: 'file',
    format: 'json',
    configPaths: {
      darwin: `${HOME}/.cursor/mcp.json`,
      win32: `${HOME}/.cursor/mcp.json`,
      linux: `${HOME}/.cursor/mcp.json`,
    },
    supportedTransports: ['stdio', 'http-oauth'],
  },

  // -- Windsurf -------------------------------------------------------------
  {
    id: 'windsurf',
    displayName: 'Windsurf',
    installMethod: 'file',
    format: 'json',
    configPaths: {
      darwin: `${HOME}/.codeium/windsurf/mcp_config.json`,
      win32: `${HOME}/.codeium/windsurf/mcp_config.json`,
      linux: `${HOME}/.codeium/windsurf/mcp_config.json`,
    },
    supportedTransports: ['stdio', 'http'],
  },

  // -- VS Code --------------------------------------------------------------
  {
    id: 'vscode',
    displayName: 'VS Code',
    installMethod: 'command',
    configPaths: {},
    command: 'code --add-mcp',
    supportedTransports: ['stdio', 'http-oauth'],
  },

  // -- VS Code Insiders -----------------------------------------------------
  {
    id: 'vscode-insiders',
    displayName: 'VS Code Insiders',
    installMethod: 'command',
    configPaths: {},
    command: 'code-insiders --add-mcp',
    supportedTransports: ['stdio', 'http-oauth'],
  },

  // -- Cline ----------------------------------------------------------------
  {
    id: 'cline',
    displayName: 'Cline',
    installMethod: 'file',
    format: 'json',
    configPaths: vscodeGlobalStorage(
      'saoudrizwan.claude-dev',
      'settings',
      'cline_mcp_settings.json'
    ),
    supportedTransports: ['stdio', 'http'],
  },

  // -- Roo Code -------------------------------------------------------------
  {
    id: 'roo-code',
    displayName: 'Roo Code',
    installMethod: 'file',
    format: 'json',
    configPaths: vscodeGlobalStorage('rooveterinaryinc.roo-cline', 'settings', 'mcp_settings.json'),
    supportedTransports: ['stdio', 'http'],
  },

  // -- Continue -------------------------------------------------------------
  {
    id: 'continue',
    displayName: 'Continue',
    installMethod: 'file',
    format: 'json',
    configPaths: {
      darwin: `${HOME}/.continue/config.json`,
      win32: `${HOME}/.continue/config.json`,
      linux: `${HOME}/.continue/config.json`,
    },
    supportedTransports: ['stdio'],
  },

  // -- Zed ------------------------------------------------------------------
  {
    id: 'zed',
    displayName: 'Zed',
    installMethod: 'file',
    format: 'json',
    configPaths: {
      darwin: `${HOME}/.config/zed/settings.json`,
      win32: `${HOME}/.config/zed/settings.json`,
      linux: `${HOME}/.config/zed/settings.json`,
    },
    supportedTransports: ['stdio'],
  },

  // -- Goose ----------------------------------------------------------------
  {
    id: 'goose',
    displayName: 'Goose',
    installMethod: 'file',
    format: 'yaml',
    configPaths: {
      darwin: `${HOME}/.config/goose/config.yaml`,
      win32: winAppData('goose', 'config.yaml'),
      linux: `${HOME}/.config/goose/config.yaml`,
    },
    supportedTransports: ['stdio'],
  },

  // -- OpenCode -------------------------------------------------------------
  {
    id: 'opencode',
    displayName: 'OpenCode',
    installMethod: 'file',
    format: 'jsonc',
    configPaths: {
      darwin: `${HOME}/.config/opencode/config.jsonc`,
      win32: winAppData('opencode', 'config.jsonc'),
      linux: `${HOME}/.config/opencode/config.jsonc`,
    },
    supportedTransports: ['stdio'],
  },

  // -- Witsy ----------------------------------------------------------------
  {
    id: 'witsy',
    displayName: 'Witsy',
    installMethod: 'file',
    format: 'json',
    configPaths: {
      darwin: macAppSupport('Witsy', 'settings.json'),
      win32: winAppData('Witsy', 'settings.json'),
      linux: linuxConfig('Witsy', 'settings.json'),
    },
    supportedTransports: ['stdio', 'http'],
  },

  // -- Enconvo --------------------------------------------------------------
  {
    id: 'enconvo',
    displayName: 'Enconvo',
    installMethod: 'file',
    format: 'json',
    configPaths: {
      darwin: macAppSupport('Enconvo', 'mcp_config.json'),
      win32: winAppData('Enconvo', 'mcp_config.json'),
      linux: linuxConfig('Enconvo', 'mcp_config.json'),
    },
    supportedTransports: ['stdio'],
  },

  // -- Coterm ---------------------------------------------------------------
  {
    id: 'coterm',
    displayName: 'Coterm',
    installMethod: 'file',
    format: 'json',
    configPaths: {
      darwin: macAppSupport('Coterm', 'mcp_config.json'),
      win32: winAppData('Coterm', 'mcp_config.json'),
      linux: linuxConfig('Coterm', 'mcp_config.json'),
    },
    supportedTransports: ['stdio'],
  },

  // -- LibreChat ------------------------------------------------------------
  {
    id: 'librechat',
    displayName: 'LibreChat',
    installMethod: 'file',
    format: 'yaml',
    configPaths: {
      darwin: 'librechat.yaml',
      win32: 'librechat.yaml',
      linux: 'librechat.yaml',
    },
    supportedTransports: ['stdio'],
  },

  // -- Superinterface -------------------------------------------------------
  {
    id: 'superinterface',
    displayName: 'Superinterface',
    installMethod: 'file',
    format: 'json',
    configPaths: {
      darwin: 'superinterface.json',
      win32: 'superinterface.json',
      linux: 'superinterface.json',
    },
    supportedTransports: ['stdio', 'http'],
  },

  // -- Gemini CLI -----------------------------------------------------------
  {
    id: 'gemini-cli',
    displayName: 'Gemini CLI',
    installMethod: 'command',
    configPaths: {},
    command: 'gemini mcp add',
    supportedTransports: ['stdio', 'http'],
  },

  // -- Codex CLI ------------------------------------------------------------
  {
    id: 'codex',
    displayName: 'Codex CLI',
    installMethod: 'command',
    configPaths: {},
    command: 'codex mcp add',
    supportedTransports: ['stdio', 'http'],
  },
] as const

// ---------------------------------------------------------------------------
// Registry
// ---------------------------------------------------------------------------

/** Immutable map of client ID to ClientConfig. */
export const CLIENT_REGISTRY: ReadonlyMap<string, ClientConfig> = new Map(
  clients.map((c) => [c.id, c])
)

/** Ordered list of all known client IDs. */
export const CLIENT_IDS: readonly string[] = clients.map((c) => c.id)

// ---------------------------------------------------------------------------
// Lookup helpers
// ---------------------------------------------------------------------------

/** Return the ClientConfig for a given ID, or undefined if not found. */
export function getClientConfig(id: string): ClientConfig | undefined {
  return CLIENT_REGISTRY.get(id)
}

/**
 * Resolve the config file path for the current platform.
 *
 * - Expands `~` to the real home directory.
 * - Returns `undefined` for command-based clients or when the current
 *   platform has no path defined.
 */
export function getConfigPath(client: ClientConfig): string | undefined {
  const os = platform() as 'darwin' | 'win32' | 'linux'
  const raw = client.configPaths[os]
  if (!raw) return undefined

  // Expand leading ~ to the user's home directory
  if (raw.startsWith('~')) {
    return join(homedir(), raw.slice(1))
  }

  return raw
}
