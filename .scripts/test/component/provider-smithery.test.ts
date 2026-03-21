import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { SmitheryProvider } from '../../lib/component/provider-smithery'

// ---------------------------------------------------------------------------
// Fetch mock helpers
// ---------------------------------------------------------------------------

let originalFetch: typeof globalThis.fetch

beforeEach(() => {
  originalFetch = globalThis.fetch
})

afterEach(() => {
  globalThis.fetch = originalFetch
})

function mockFetch(handler: (url: string, init?: RequestInit) => Promise<Response>): void {
  globalThis.fetch = handler as typeof globalThis.fetch
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

// ---------------------------------------------------------------------------
// search: returns normalized MCP server results
// ---------------------------------------------------------------------------

describe('SmitheryProvider search', () => {
  test('returns normalized MCP server results', async () => {
    mockFetch(async () =>
      jsonResponse({
        servers: [
          {
            qualifiedName: '@anthropic/claude-code',
            description: 'Claude Code MCP server',
            displayName: 'Claude Code',
            useCount: 1234,
            verified: true,
          },
          {
            qualifiedName: '@modelcontextprotocol/everything',
            description: 'Everything server for testing',
            displayName: 'Everything',
            useCount: 567,
            verified: false,
          },
        ],
      })
    )

    const provider = new SmitheryProvider()
    const result = await provider.search({ query: 'claude' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(2)

    const first = result.value.items[0]!
    expect(first.type).toBe('mcp_server')
    expect(first.name).toBe('@anthropic/claude-code')
    expect(first.source).toBe('smithery://@anthropic/claude-code')
    expect(first.description).toBe('Claude Code MCP server')
    expect(first.url).toBe('https://smithery.ai/server/@anthropic/claude-code')
    expect(first.installs).toBe(1234)
    expect(first.verified).toBe(true)
    expect(first.namespace).toBe('@anthropic')

    const second = result.value.items[1]!
    expect(second.verified).toBe(false)
    expect(second.installs).toBe(567)
  })

  // ---------------------------------------------------------------------------
  // search: returns empty for non-mcp_server type
  // ---------------------------------------------------------------------------

  test('returns empty for non-mcp_server type', async () => {
    // fetch should NOT be called for type mismatches
    mockFetch(async () => {
      throw new Error('fetch should not be called')
    })

    const provider = new SmitheryProvider()
    const result = await provider.search({ query: 'test', type: 'skill' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
    expect(result.value.hasMore).toBe(false)
    expect(result.value.total).toBe(0)
  })

  // ---------------------------------------------------------------------------
  // search: returns empty on 429 rate limit
  // ---------------------------------------------------------------------------

  test('returns empty on 429 rate limit', async () => {
    mockFetch(async () => new Response('Too Many Requests', { status: 429 }))

    const provider = new SmitheryProvider()
    const result = await provider.search({ query: 'test' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
    expect(result.value.hasMore).toBe(false)
  })

  // ---------------------------------------------------------------------------
  // search: returns empty on timeout
  // ---------------------------------------------------------------------------

  test('returns empty on timeout', async () => {
    mockFetch(async (_url, init) => {
      // Wait for the abort signal to fire
      return new Promise<Response>((_resolve, reject) => {
        if (init?.signal) {
          init.signal.addEventListener('abort', () => {
            reject(new DOMException('The operation was aborted.', 'AbortError'))
          })
        }
      })
    })

    // Use a provider with a very short timeout to speed up the test.
    // The default is 3s but the abort logic is the same.
    const provider = new SmitheryProvider()
    const result = await provider.search({ query: 'slow' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
  })

  // ---------------------------------------------------------------------------
  // search: returns empty on network error
  // ---------------------------------------------------------------------------

  test('returns empty on network error', async () => {
    mockFetch(async () => {
      throw new TypeError('fetch failed')
    })

    const provider = new SmitheryProvider()
    const result = await provider.search({ query: 'test' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
  })

  // ---------------------------------------------------------------------------
  // search: passes query and pagination params
  // ---------------------------------------------------------------------------

  test('passes query and pagination params', async () => {
    let capturedUrl = ''

    mockFetch(async (url) => {
      capturedUrl = url
      return jsonResponse({ servers: [] })
    })

    const provider = new SmitheryProvider()
    await provider.search({
      query: 'database',
      page: 3,
      limit: 25,
      verified: true,
      namespace: '@acme',
    })

    const parsed = new URL(capturedUrl)
    expect(parsed.pathname).toBe('/api/v1/servers')
    expect(parsed.searchParams.get('q')).toBe('database')
    expect(parsed.searchParams.get('page')).toBe('3')
    expect(parsed.searchParams.get('pageSize')).toBe('25')
    expect(parsed.searchParams.get('verified')).toBe('true')
    expect(parsed.searchParams.get('namespace')).toBe('@acme')
  })

  // ---------------------------------------------------------------------------
  // search: handles missing fields gracefully
  // ---------------------------------------------------------------------------

  test('handles missing fields gracefully', async () => {
    mockFetch(async () =>
      jsonResponse({
        servers: [{ name: 'bare-server' }],
      })
    )

    const provider = new SmitheryProvider()
    const result = await provider.search({ query: '' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)

    const item = result.value.items[0]!
    expect(item.type).toBe('mcp_server')
    expect(item.name).toBe('bare-server')
    expect(item.source).toBe('smithery://bare-server')
    expect(item.description).toBe('')
    expect(item.url).toBeUndefined()
    expect(item.installs).toBeUndefined()
    expect(item.verified).toBeUndefined()
    expect(item.namespace).toBeUndefined()
  })

  // ---------------------------------------------------------------------------
  // search: supports custom baseUrl
  // ---------------------------------------------------------------------------

  test('supports custom baseUrl', async () => {
    let capturedUrl = ''

    mockFetch(async (url) => {
      capturedUrl = url
      return jsonResponse({ servers: [] })
    })

    const provider = new SmitheryProvider({
      baseUrl: 'https://custom.example.com/v2',
    })
    await provider.search({ query: 'test' })

    expect(capturedUrl).toContain('https://custom.example.com/v2/servers')
  })

  // ---------------------------------------------------------------------------
  // search: hasMore true when results fill the page
  // ---------------------------------------------------------------------------

  test('hasMore true when results fill the page', async () => {
    const servers = Array.from({ length: 5 }, (_, i) => ({
      qualifiedName: `@ns/server-${i}`,
      description: `Server ${i}`,
    }))

    mockFetch(async () => jsonResponse({ servers }))

    const provider = new SmitheryProvider()
    const result = await provider.search({ query: 'server', limit: 5 })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(5)
    expect(result.value.hasMore).toBe(true)
    expect(result.value.pageSize).toBe(5)
  })

  // ---------------------------------------------------------------------------
  // search: hasMore false when results are fewer than limit
  // ---------------------------------------------------------------------------

  test('hasMore false when results are fewer than limit', async () => {
    const servers = [{ qualifiedName: '@ns/only-one', description: 'Solo' }]

    mockFetch(async () => jsonResponse({ servers }))

    const provider = new SmitheryProvider()
    const result = await provider.search({ query: 'solo', limit: 10 })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.hasMore).toBe(false)
  })

  // ---------------------------------------------------------------------------
  // search: returns empty on non-ok HTTP status
  // ---------------------------------------------------------------------------

  test('returns empty on non-ok HTTP status (500)', async () => {
    mockFetch(async () => new Response('Internal Server Error', { status: 500 }))

    const provider = new SmitheryProvider()
    const result = await provider.search({ query: 'broken' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toEqual([])
  })

  // ---------------------------------------------------------------------------
  // search: handles response that is a plain array (not {servers: [...]})
  // ---------------------------------------------------------------------------

  test('handles response that is a plain array', async () => {
    mockFetch(async () =>
      jsonResponse([
        {
          qualifiedName: '@flat/array-server',
          description: 'Flat array response',
        },
      ])
    )

    const provider = new SmitheryProvider()
    const result = await provider.search({ query: 'flat' })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.items).toHaveLength(1)
    expect(result.value.items[0]?.name).toBe('@flat/array-server')
  })
})

// ---------------------------------------------------------------------------
// capabilities
// ---------------------------------------------------------------------------

describe('SmitheryProvider capabilities', () => {
  test('only supports mcp_server search', () => {
    const provider = new SmitheryProvider()

    expect(provider.id).toBe('smithery')
    expect(provider.displayName).toBe('Smithery Registry')
    expect(provider.capabilities.search).toEqual(['mcp_server'])
    expect(provider.capabilities.add).toEqual([])
    expect(provider.capabilities.list).toEqual([])
    expect(provider.capabilities.remove).toEqual([])
    expect(provider.capabilities.publish).toEqual(['mcp_server'])
    expect(provider.capabilities.info).toEqual([])
    expect(provider.capabilities.outdated).toEqual([])
    expect(provider.capabilities.update).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// unsupported operations
// ---------------------------------------------------------------------------

describe('SmitheryProvider unsupported operations', () => {
  test('add returns error', async () => {
    const provider = new SmitheryProvider()
    const result = await provider.add('some-source', {})

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_UNSUPPORTED')
    expect(result.error.message).toContain('add')
  })

  test('remove returns error', async () => {
    const provider = new SmitheryProvider()
    const result = await provider.remove('some-server', 'mcp_server')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_UNSUPPORTED')
    expect(result.error.message).toContain('remove')
  })

  test('info returns error', async () => {
    const provider = new SmitheryProvider()
    const result = await provider.info('some-server', 'mcp_server')

    expect(result.ok).toBe(false)
    if (result.ok) return

    expect(result.error.code).toBe('E_UNSUPPORTED')
    expect(result.error.message).toContain('info')
  })

  test('list returns empty array (not error)', async () => {
    const provider = new SmitheryProvider()
    const result = await provider.list('mcp_server')

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value).toEqual([])
  })
})

// ---------------------------------------------------------------------------
// publish
// ---------------------------------------------------------------------------

describe('SmitheryProvider publish', () => {
  test('publishes external URL to Smithery', async () => {
    mockFetch(async (url: string, init?: RequestInit) => {
      const urlStr = String(url)
      // Initial POST to create release
      if (init?.method === 'POST' && urlStr.includes('/releases')) {
        return jsonResponse({ deploymentId: 'dep-123' })
      }
      // GET poll for deployment status
      if (urlStr.includes('/releases/dep-123')) {
        return jsonResponse({ status: 'SUCCESS', mcpUrl: 'https://server.smithery.ai/ns/test/mcp' })
      }
      return jsonResponse({}, 404)
    })

    const provider = new SmitheryProvider()
    const result = await provider.publish('mcp_server', {
      name: 'ns/test-server',
      apiKey: 'test-key',
      externalUrl: 'https://my-server.com/mcp',
    })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.status).toBe('published')
      expect(result.value.registryUrl).toContain('smithery.ai')
    }
  })

  test('returns error for non-mcp_server type', async () => {
    const provider = new SmitheryProvider()
    const result = await provider.publish('skill', { name: 'ns/test', apiKey: 'key' })
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_UNSUPPORTED')
  })

  test('returns error when no API key', async () => {
    const origEnv = process.env.SMITHERY_API_KEY
    delete process.env.SMITHERY_API_KEY
    try {
      const provider = new SmitheryProvider()
      const result = await provider.publish('mcp_server', { name: 'ns/test' })
      expect(result.ok).toBe(false)
      if (!result.ok) expect(result.error.code).toBe('E_AUTH_REQUIRED')
    } finally {
      if (origEnv) process.env.SMITHERY_API_KEY = origEnv
    }
  })

  test('returns error when no name provided', async () => {
    const provider = new SmitheryProvider()
    const result = await provider.publish('mcp_server', { apiKey: 'key' })
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_MISSING_NAME')
  })

  test('supports dry run', async () => {
    const provider = new SmitheryProvider()
    const result = await provider.publish('mcp_server', {
      name: 'ns/test',
      apiKey: 'key',
      externalUrl: 'https://example.com',
      dryRun: true,
    })
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value.warnings).toContain('Dry run -- no changes made')
  })

  test('capabilities includes mcp_server in publish', () => {
    const provider = new SmitheryProvider()
    expect(provider.capabilities.publish).toContain('mcp_server')
  })
})
