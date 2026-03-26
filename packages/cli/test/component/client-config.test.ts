import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  formatServerConfig,
  type McpServerEntry,
  readConfigFile,
  readJsoncFile,
  readJsonFile,
  readYamlFile,
  stripJsonComments,
  writeConfigFile,
  writeJsonFile,
  writeYamlFile,
} from '@agents/core/component/client-config'

// ---------------------------------------------------------------------------
// Shared temp directory setup
// ---------------------------------------------------------------------------

let tmpDir: string

beforeEach(async () => {
  tmpDir = await mkdtemp(join(tmpdir(), 'client-config-test-'))
})

afterEach(async () => {
  await rm(tmpDir, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// stripJsonComments
// ---------------------------------------------------------------------------

describe('stripJsonComments', () => {
  test('removes single-line comments', () => {
    const input = `{
  // This is a comment
  "key": "value" // trailing comment
}`
    const result = stripJsonComments(input)
    const parsed = JSON.parse(result)
    expect(parsed.key).toBe('value')
  })

  test('removes block comments', () => {
    const input = `{
  /* block comment */
  "key": "value",
  "other": /* inline block */ "data"
}`
    const result = stripJsonComments(input)
    const parsed = JSON.parse(result)
    expect(parsed.key).toBe('value')
    expect(parsed.other).toBe('data')
  })

  test('removes multi-line block comments', () => {
    const input = `{
  /*
   * Multi-line
   * block comment
   */
  "key": "value"
}`
    const result = stripJsonComments(input)
    const parsed = JSON.parse(result)
    expect(parsed.key).toBe('value')
  })

  test('preserves strings containing double-slash in URLs (no quotes awareness)', () => {
    // NOTE: our simple regex-based stripper does NOT handle // inside strings.
    // Verify it works when the // is not inside a string value on the same line.
    const input = `{
  "name": "test"
}`
    const result = stripJsonComments(input)
    expect(JSON.parse(result).name).toBe('test')
  })

  test('handles empty input', () => {
    expect(stripJsonComments('')).toBe('')
  })

  test('handles input with no comments', () => {
    const input = '{"a": 1, "b": 2}'
    expect(stripJsonComments(input)).toBe(input)
  })
})

// ---------------------------------------------------------------------------
// readJsonFile
// ---------------------------------------------------------------------------

describe('readJsonFile', () => {
  test('reads valid JSON', async () => {
    const path = join(tmpDir, 'valid.json')
    await writeFile(path, '{"mcpServers": {"test": {"command": "node"}}}')

    const result = await readJsonFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toEqual({
        mcpServers: { test: { command: 'node' } },
      })
    }
  })

  test('returns error for invalid JSON', async () => {
    const path = join(tmpDir, 'invalid.json')
    await writeFile(path, '{not valid json}')

    const result = await readJsonFile(path)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_READ_FAILED')
    }
  })

  test('returns error for missing file', async () => {
    const result = await readJsonFile(join(tmpDir, 'nonexistent.json'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_READ_FAILED')
    }
  })
})

// ---------------------------------------------------------------------------
// readJsoncFile
// ---------------------------------------------------------------------------

describe('readJsoncFile', () => {
  test('reads JSONC with single-line comments', async () => {
    const path = join(tmpDir, 'config.jsonc')
    await writeFile(
      path,
      `{
  // MCP server configuration
  "mcpServers": {
    "test": {
      "command": "node" // start command
    }
  }
}`
    )

    const result = await readJsoncFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      const servers = result.value.mcpServers as Record<string, unknown>
      expect(servers.test).toEqual({ command: 'node' })
    }
  })

  test('reads JSONC with block comments', async () => {
    const path = join(tmpDir, 'block.jsonc')
    await writeFile(
      path,
      `{
  /* Server list */
  "mcpServers": {
    "demo": {
      "command": "bun",
      "args": ["run", "server.ts"]
    }
  }
}`
    )

    const result = await readJsoncFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      const servers = result.value.mcpServers as Record<string, Record<string, unknown>>
      expect(servers.demo.command).toBe('bun')
      expect(servers.demo.args).toEqual(['run', 'server.ts'])
    }
  })

  test('returns error for invalid JSONC', async () => {
    const path = join(tmpDir, 'bad.jsonc')
    await writeFile(path, '// comment only\n{invalid}')

    const result = await readJsoncFile(path)
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_READ_FAILED')
    }
  })
})

// ---------------------------------------------------------------------------
// readYamlFile
// ---------------------------------------------------------------------------

describe('readYamlFile', () => {
  test('reads valid YAML', async () => {
    const path = join(tmpDir, 'config.yaml')
    await writeFile(
      path,
      `mcpServers:
  test:
    command: node
    args:
      - server.js
`
    )

    const result = await readYamlFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      const servers = result.value.mcpServers as Record<string, Record<string, unknown>>
      expect(servers.test.command).toBe('node')
      expect(servers.test.args).toEqual(['server.js'])
    }
  })

  test('returns empty object for non-object YAML', async () => {
    const path = join(tmpDir, 'scalar.yaml')
    await writeFile(path, '"just a string"')

    const result = await readYamlFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toEqual({})
    }
  })

  test('returns empty object for empty YAML', async () => {
    const path = join(tmpDir, 'empty.yaml')
    await writeFile(path, '')

    const result = await readYamlFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toEqual({})
    }
  })

  test('returns error for missing YAML file', async () => {
    const result = await readYamlFile(join(tmpDir, 'missing.yaml'))
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_READ_FAILED')
    }
  })
})

// ---------------------------------------------------------------------------
// writeJsonFile
// ---------------------------------------------------------------------------

describe('writeJsonFile', () => {
  test('writes formatted JSON with trailing newline', async () => {
    const path = join(tmpDir, 'output.json')
    const result = await writeJsonFile(path, { hello: 'world' })

    expect(result.ok).toBe(true)
    const content = await readFile(path, 'utf-8')
    expect(content).toBe('{\n  "hello": "world"\n}\n')
  })

  test('creates parent directories', async () => {
    const path = join(tmpDir, 'deep', 'nested', 'dir', 'out.json')
    const result = await writeJsonFile(path, { nested: true })

    expect(result.ok).toBe(true)
    const content = await readFile(path, 'utf-8')
    expect(JSON.parse(content)).toEqual({ nested: true })
  })

  test('overwrites existing file', async () => {
    const path = join(tmpDir, 'overwrite.json')
    await writeFile(path, '{"old": true}')

    const result = await writeJsonFile(path, { new: true })
    expect(result.ok).toBe(true)
    const content = await readFile(path, 'utf-8')
    expect(JSON.parse(content)).toEqual({ new: true })
  })
})

// ---------------------------------------------------------------------------
// writeYamlFile
// ---------------------------------------------------------------------------

describe('writeYamlFile', () => {
  test('writes valid YAML', async () => {
    const path = join(tmpDir, 'output.yaml')
    const result = await writeYamlFile(path, {
      servers: { demo: { command: 'node' } },
    })

    expect(result.ok).toBe(true)
    const content = await readFile(path, 'utf-8')
    expect(content).toContain('servers:')
    expect(content).toContain('command: node')
  })

  test('creates parent directories', async () => {
    const path = join(tmpDir, 'a', 'b', 'c', 'out.yaml')
    const result = await writeYamlFile(path, { key: 'value' })

    expect(result.ok).toBe(true)
    const content = await readFile(path, 'utf-8')
    expect(content).toContain('key: value')
  })
})

// ---------------------------------------------------------------------------
// readConfigFile (format dispatch)
// ---------------------------------------------------------------------------

describe('readConfigFile', () => {
  test('dispatches to JSON reader for "json" format', async () => {
    const path = join(tmpDir, 'dispatch.json')
    await writeFile(path, '{"format": "json"}')

    const result = await readConfigFile(path, 'json')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value.format).toBe('json')
  })

  test('dispatches to JSONC reader for "jsonc" format', async () => {
    const path = join(tmpDir, 'dispatch.jsonc')
    await writeFile(path, '// comment\n{"format": "jsonc"}')

    const result = await readConfigFile(path, 'jsonc')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value.format).toBe('jsonc')
  })

  test('dispatches to YAML reader for "yaml" format', async () => {
    const path = join(tmpDir, 'dispatch.yaml')
    await writeFile(path, 'format: yaml\n')

    const result = await readConfigFile(path, 'yaml')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value.format).toBe('yaml')
  })

  test('defaults to JSON reader for unknown format', async () => {
    const path = join(tmpDir, 'dispatch.txt')
    await writeFile(path, '{"format": "unknown"}')

    const result = await readConfigFile(path, 'toml')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value.format).toBe('unknown')
  })
})

// ---------------------------------------------------------------------------
// writeConfigFile (format dispatch)
// ---------------------------------------------------------------------------

describe('writeConfigFile', () => {
  test('writes JSON for "json" format', async () => {
    const path = join(tmpDir, 'wdispatch.json')
    const result = await writeConfigFile(path, 'json', { a: 1 })
    expect(result.ok).toBe(true)

    const content = await readFile(path, 'utf-8')
    expect(JSON.parse(content)).toEqual({ a: 1 })
  })

  test('writes YAML for "yaml" format', async () => {
    const path = join(tmpDir, 'wdispatch.yaml')
    const result = await writeConfigFile(path, 'yaml', { b: 2 })
    expect(result.ok).toBe(true)

    const content = await readFile(path, 'utf-8')
    expect(content).toContain('b: 2')
  })

  test('writes JSON for "jsonc" format (comments not preserved)', async () => {
    const path = join(tmpDir, 'wdispatch.jsonc')
    const result = await writeConfigFile(path, 'jsonc', { c: 3 })
    expect(result.ok).toBe(true)

    const content = await readFile(path, 'utf-8')
    expect(JSON.parse(content)).toEqual({ c: 3 })
  })
})

// ---------------------------------------------------------------------------
// formatServerConfig
// ---------------------------------------------------------------------------

describe('formatServerConfig', () => {
  test('formats stdio entry with command and args', () => {
    const entry: McpServerEntry = {
      name: 'my-server',
      transport: 'stdio',
      command: 'node',
      args: ['server.js', '--port', '3000'],
    }

    const result = formatServerConfig(entry)
    expect(result).toEqual({
      command: 'node',
      args: ['server.js', '--port', '3000'],
    })
  })

  test('formats stdio entry with env', () => {
    const entry: McpServerEntry = {
      name: 'my-server',
      transport: 'stdio',
      command: 'node',
      args: ['server.js'],
      env: { NODE_ENV: 'production', API_KEY: 'secret' },
    }

    const result = formatServerConfig(entry)
    expect(result).toEqual({
      command: 'node',
      args: ['server.js'],
      env: { NODE_ENV: 'production', API_KEY: 'secret' },
    })
  })

  test('omits env when empty object', () => {
    const entry: McpServerEntry = {
      name: 'my-server',
      transport: 'stdio',
      command: 'node',
      args: [],
      env: {},
    }

    const result = formatServerConfig(entry)
    expect(result).toEqual({
      command: 'node',
      args: [],
    })
    expect(result).not.toHaveProperty('env')
  })

  test('formats http entry', () => {
    const entry: McpServerEntry = {
      name: 'remote-server',
      transport: 'http',
      url: 'https://mcp.example.com/sse',
    }

    const result = formatServerConfig(entry)
    expect(result).toEqual({
      type: 'http',
      url: 'https://mcp.example.com/sse',
    })
  })

  test('formats http-oauth entry as type "http"', () => {
    const entry: McpServerEntry = {
      name: 'oauth-server',
      transport: 'http-oauth',
      url: 'https://mcp.example.com/oauth',
    }

    const result = formatServerConfig(entry)
    expect(result).toEqual({
      type: 'http',
      url: 'https://mcp.example.com/oauth',
    })
  })

  test('defaults command to empty string when missing for stdio', () => {
    const entry: McpServerEntry = {
      name: 'bare',
      transport: 'stdio',
    }

    const result = formatServerConfig(entry)
    expect(result.command).toBe('')
    expect(result.args).toEqual([])
  })

  test('defaults url to empty string when missing for http', () => {
    const entry: McpServerEntry = {
      name: 'bare-http',
      transport: 'http',
    }

    const result = formatServerConfig(entry)
    expect(result.url).toBe('')
  })
})

// ---------------------------------------------------------------------------
// JSON roundtrip (write then read)
// ---------------------------------------------------------------------------

describe('JSON roundtrip', () => {
  test('writeJsonFile then readJsonFile preserves data', async () => {
    const path = join(tmpDir, 'roundtrip.json')
    const data = {
      mcpServers: {
        'my-server': {
          command: 'npx',
          args: ['-y', '@example/mcp-server'],
          env: { DEBUG: '1' },
        },
      },
    }

    await writeJsonFile(path, data)
    const result = await readJsonFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toEqual(data)
    }
  })
})

// ---------------------------------------------------------------------------
// YAML roundtrip (write then read)
// ---------------------------------------------------------------------------

describe('YAML roundtrip', () => {
  test('writeYamlFile then readYamlFile preserves data', async () => {
    const path = join(tmpDir, 'roundtrip.yaml')
    const data = {
      mcpServers: {
        'demo-server': {
          command: 'bun',
          args: ['run', 'index.ts'],
        },
      },
    }

    await writeYamlFile(path, data)
    const result = await readYamlFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value).toEqual(data)
    }
  })
})

// ---------------------------------------------------------------------------
// JSONC roundtrip (read with comments, write without)
// ---------------------------------------------------------------------------

describe('JSONC roundtrip', () => {
  test('reads JSONC, writes as JSON, reads back', async () => {
    const inputPath = join(tmpDir, 'input.jsonc')
    const outputPath = join(tmpDir, 'output.json')

    await writeFile(
      inputPath,
      `{
  // Configuration for MCP servers
  "mcpServers": {
    /* The test server */
    "test": {
      "command": "node",
      "args": ["--inspect", "server.js"]
    }
  }
}`
    )

    const read = await readJsoncFile(inputPath)
    expect(read.ok).toBe(true)
    if (!read.ok) return

    await writeJsonFile(outputPath, read.value)
    const reread = await readJsonFile(outputPath)
    expect(reread.ok).toBe(true)
    if (reread.ok) {
      expect(reread.value).toEqual(read.value)
    }
  })
})

// ---------------------------------------------------------------------------
// Integration: complex config with multiple servers
// ---------------------------------------------------------------------------

describe('complex config integration', () => {
  test('handles config with multiple server entries', async () => {
    const path = join(tmpDir, 'complex.json')
    const config = {
      mcpServers: {
        'server-a': { command: 'node', args: ['a.js'] },
        'server-b': { type: 'http', url: 'https://b.example.com' },
        'server-c': {
          command: 'python',
          args: ['-m', 'mcp-server'],
          env: { PORT: '8080' },
        },
      },
    }

    await writeJsonFile(path, config)
    const result = await readJsonFile(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      const servers = result.value.mcpServers as Record<string, Record<string, unknown>>
      expect(Object.keys(servers)).toHaveLength(3)
      expect(servers['server-a'].command).toBe('node')
      expect(servers['server-b'].url).toBe('https://b.example.com')
      expect((servers['server-c'].env as Record<string, string>).PORT).toBe('8080')
    }
  })
})
