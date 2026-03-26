import { describe, expect, test } from 'bun:test'
import { platform } from 'node:os'
import {
  CLIENT_IDS,
  CLIENT_REGISTRY,
  type ClientTransport,
  getClientConfig,
  getConfigPath,
} from '@agents/sdk/providers/clients/registry'

// ---------------------------------------------------------------------------
// Registry size
// ---------------------------------------------------------------------------

describe('CLIENT_REGISTRY', () => {
  test('has 19 entries', () => {
    expect(CLIENT_REGISTRY.size).toBe(19)
  })
})

// ---------------------------------------------------------------------------
// CLIENT_IDS
// ---------------------------------------------------------------------------

describe('CLIENT_IDS', () => {
  test('has 19 entries matching registry keys', () => {
    expect(CLIENT_IDS).toHaveLength(19)
    const registryKeys = [...CLIENT_REGISTRY.keys()]
    for (const id of CLIENT_IDS) {
      expect(registryKeys).toContain(id)
    }
    for (const key of registryKeys) {
      expect(CLIENT_IDS).toContain(key)
    }
  })
})

// ---------------------------------------------------------------------------
// getClientConfig
// ---------------------------------------------------------------------------

describe('getClientConfig', () => {
  test('returns config for known client', () => {
    const config = getClientConfig('claude-desktop')
    expect(config).toBeDefined()
    expect(config?.id).toBe('claude-desktop')
    expect(config?.displayName).toBe('Claude Desktop')
  })

  test('returns undefined for unknown client', () => {
    const config = getClientConfig('nonexistent-client')
    expect(config).toBeUndefined()
  })
})

// ---------------------------------------------------------------------------
// Required fields
// ---------------------------------------------------------------------------

describe('every client has required fields', () => {
  for (const [id, client] of CLIENT_REGISTRY) {
    test(`${id} has id, displayName, installMethod, supportedTransports`, () => {
      expect(client.id).toBeString()
      expect(client.id.length).toBeGreaterThan(0)
      expect(client.displayName).toBeString()
      expect(client.displayName.length).toBeGreaterThan(0)
      expect(['file', 'command']).toContain(client.installMethod)
      expect(Array.isArray(client.supportedTransports)).toBe(true)
      expect(client.supportedTransports.length).toBeGreaterThan(0)
    })
  }
})

// ---------------------------------------------------------------------------
// file-based clients have configPaths
// ---------------------------------------------------------------------------

describe('file-based clients have configPaths', () => {
  for (const [id, client] of CLIENT_REGISTRY) {
    if (client.installMethod === 'file') {
      test(`${id} has at least one config path`, () => {
        const paths = client.configPaths
        const hasSomePath =
          paths.darwin !== undefined || paths.win32 !== undefined || paths.linux !== undefined
        expect(hasSomePath).toBe(true)
      })
    }
  }
})

// ---------------------------------------------------------------------------
// command-based clients have command
// ---------------------------------------------------------------------------

describe('command-based clients have command', () => {
  for (const [id, client] of CLIENT_REGISTRY) {
    if (client.installMethod === 'command') {
      test(`${id} has command field`, () => {
        expect(client.command).toBeString()
        expect(client.command?.length).toBeGreaterThan(0)
      })
    }
  }
})

// ---------------------------------------------------------------------------
// getConfigPath
// ---------------------------------------------------------------------------

describe('getConfigPath', () => {
  test('returns a string for file-based clients on current platform', () => {
    // Pick file-based clients that have a path for the current platform
    const os = platform() as 'darwin' | 'win32' | 'linux'
    for (const [_id, client] of CLIENT_REGISTRY) {
      if (client.installMethod === 'file' && client.configPaths[os]) {
        const resolved = getConfigPath(client)
        expect(resolved).toBeString()
        // Paths starting with ~ should be expanded
        expect(resolved?.startsWith('~')).toBe(false)
      }
    }
  })

  test('returns undefined for command-based clients', () => {
    const commandClients = [...CLIENT_REGISTRY.values()].filter(
      (c) => c.installMethod === 'command'
    )
    expect(commandClients.length).toBeGreaterThan(0)
    for (const client of commandClients) {
      expect(getConfigPath(client)).toBeUndefined()
    }
  })
})

// ---------------------------------------------------------------------------
// claude-desktop has correct macOS path
// ---------------------------------------------------------------------------

describe('claude-desktop path verification', () => {
  test('has correct macOS path', () => {
    const client = getClientConfig('claude-desktop')
    expect(client).toBeDefined()
    expect(client?.configPaths.darwin).toBe(
      '~/Library/Application Support/Claude/claude_desktop_config.json'
    )
  })
})

// ---------------------------------------------------------------------------
// all transports are valid
// ---------------------------------------------------------------------------

describe('all transports are valid', () => {
  const validTransports: readonly ClientTransport[] = ['stdio', 'http', 'http-oauth']

  for (const [id, client] of CLIENT_REGISTRY) {
    test(`${id} has only valid transports`, () => {
      for (const transport of client.supportedTransports) {
        expect(validTransports).toContain(transport)
      }
    })
  }
})
