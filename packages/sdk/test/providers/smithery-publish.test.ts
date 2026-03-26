import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync, mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { pollDeployment, publishToSmithery } from '../../src/providers/smithery/publish'

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

function mockFetch(
  handler: (url: string | URL | Request, init?: RequestInit) => Promise<Response>
): void {
  globalThis.fetch = handler as typeof globalThis.fetch
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function textResponse(body: string, status: number): Response {
  return new Response(body, { status })
}

// ---------------------------------------------------------------------------
// Temp bundle directory helpers
// ---------------------------------------------------------------------------

function makeTmpBundleDir(manifest?: Record<string, unknown>): string {
  const dir = join(
    tmpdir(),
    `smithery-publish-test-${Date.now()}-${Math.random().toString(36).slice(2)}`
  )
  mkdirSync(dir, { recursive: true })
  if (manifest) {
    writeFileSync(join(dir, 'manifest.json'), JSON.stringify(manifest))
  }
  return dir
}

function cleanupDir(dir: string): void {
  if (existsSync(dir)) {
    rmSync(dir, { recursive: true, force: true })
  }
}

// ---------------------------------------------------------------------------
// Base options
// ---------------------------------------------------------------------------

const BASE_URL = 'https://test.smithery.local/api/v1'
const BASE_OPTS = {
  qualifiedName: 'test-ns/test-server',
  apiKey: 'sk-test-key-123',
  baseUrl: BASE_URL,
} as const

// ---------------------------------------------------------------------------
// publishToSmithery -- External URL mode
// ---------------------------------------------------------------------------

describe('publishToSmithery -- external URL', () => {
  test('sends correct payload and returns registryUrl on immediate success', async () => {
    let capturedUrl = ''
    let capturedBody = ''
    let capturedHeaders: Record<string, string> = {}

    mockFetch(async (url, init) => {
      capturedUrl = String(url)
      capturedBody = (init?.body as string) ?? ''
      capturedHeaders = Object.fromEntries(
        Object.entries(init?.headers ?? {}).map(([k, v]) => [k, String(v)])
      )
      // No deploymentId -- immediate success
      return jsonResponse({})
    })

    const result = await publishToSmithery({
      ...BASE_OPTS,
      externalUrl: 'https://my-server.example.com/mcp',
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.ok).toBe(true)
    expect(result.value.status).toBe('published')
    expect(result.value.registryUrl).toBe('https://smithery.ai/server/test-ns/test-server')

    // Verify request
    expect(capturedUrl).toContain('/servers/test-ns%2Ftest-server/releases')
    expect(capturedHeaders['Content-Type']).toBe('application/json')
    expect(capturedHeaders['Authorization']).toBe('Bearer sk-test-key-123')

    const parsed = JSON.parse(capturedBody)
    const payload = JSON.parse(parsed.payload)
    expect(payload.type).toBe('external')
    expect(payload.upstreamUrl).toBe('https://my-server.example.com/mcp')
  })

  test('returns published after poll SUCCESS', async () => {
    let callCount = 0

    mockFetch(async (url) => {
      callCount++
      const urlStr = String(url)
      // First call: publish -- returns deploymentId
      if (urlStr.includes('/releases') && !urlStr.includes('/releases/deploy-123')) {
        return jsonResponse({ deploymentId: 'deploy-123' })
      }
      // Second call: poll -- returns SUCCESS
      return jsonResponse({
        status: 'SUCCESS',
        mcpUrl: 'https://smithery.ai/server/test-ns/test-server',
      })
    })

    const result = await publishToSmithery({
      ...BASE_OPTS,
      externalUrl: 'https://my-server.example.com/mcp',
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.ok).toBe(true)
    expect(result.value.status).toBe('published')
    expect(result.value.releaseId).toBe('deploy-123')
    expect(callCount).toBe(2)
  })

  test('returns E_SERVER_NOT_FOUND on 404', async () => {
    mockFetch(async () => textResponse('Not Found', 404))

    const result = await publishToSmithery({
      ...BASE_OPTS,
      externalUrl: 'https://my-server.example.com/mcp',
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_COMPONENT_NOT_FOUND')
  })

  test('returns E_AUTH_FAILED on 401', async () => {
    mockFetch(async () => textResponse('Unauthorized', 401))

    const result = await publishToSmithery({
      ...BASE_OPTS,
      externalUrl: 'https://my-server.example.com/mcp',
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })

  test('returns E_RATE_LIMITED on 429', async () => {
    mockFetch(async () => textResponse('Too Many Requests', 429))

    const result = await publishToSmithery({
      ...BASE_OPTS,
      externalUrl: 'https://my-server.example.com/mcp',
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_PROVIDER_TIMEOUT')
  })

  test('returns E_API_ERROR on 500', async () => {
    mockFetch(async () => textResponse('Internal Server Error', 500))

    const result = await publishToSmithery({
      ...BASE_OPTS,
      externalUrl: 'https://my-server.example.com/mcp',
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
    expect(result.error.message).toContain('HTTP 500')
  })
})

// ---------------------------------------------------------------------------
// publishToSmithery -- validation
// ---------------------------------------------------------------------------

describe('publishToSmithery -- validation', () => {
  test('invalid qualified name (no slash) returns E_INVALID_NAME', async () => {
    const result = await publishToSmithery({
      ...BASE_OPTS,
      qualifiedName: 'no-slash-name',
      externalUrl: 'https://example.com/mcp',
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_VALIDATION_FAILED')
    expect(result.error.message).toContain('no-slash-name')
  })

  test('dry run validates without sending (no fetch called)', async () => {
    let fetchCalled = false
    mockFetch(async () => {
      fetchCalled = true
      return jsonResponse({})
    })

    const result = await publishToSmithery({
      ...BASE_OPTS,
      externalUrl: 'https://example.com/mcp',
      dryRun: true,
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.status).toBe('published')
    expect(result.value.warnings).toContain('Dry run -- no changes made')
    expect(fetchCalled).toBe(false)
  })

  test('dry run returns error when no URL or bundleDir provided', async () => {
    const result = await publishToSmithery({
      ...BASE_OPTS,
      dryRun: true,
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_VALIDATION_FAILED')
  })

  test('missing source returns E_MISSING_SOURCE when neither URL nor bundleDir', async () => {
    const result = await publishToSmithery({
      ...BASE_OPTS,
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_VALIDATION_FAILED')
  })
})

// ---------------------------------------------------------------------------
// publishToSmithery -- bundle mode
// ---------------------------------------------------------------------------

describe('publishToSmithery -- bundle', () => {
  let tmpDir: string

  afterEach(() => {
    if (tmpDir) cleanupDir(tmpDir)
  })

  test('reads manifest.json and sends multipart', async () => {
    tmpDir = makeTmpBundleDir({
      payload: { type: 'managed', runtime: 'node' },
    })

    let capturedFormData = false
    let capturedUrl = ''

    mockFetch(async (url, init) => {
      capturedUrl = String(url)
      // Verify it's FormData (not JSON)
      capturedFormData = init?.body instanceof FormData
      return jsonResponse({})
    })

    const result = await publishToSmithery({
      ...BASE_OPTS,
      bundleDir: tmpDir,
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.status).toBe('published')
    expect(result.value.registryUrl).toBe('https://smithery.ai/server/test-ns/test-server')
    expect(capturedFormData).toBe(true)
    expect(capturedUrl).toContain('/servers/test-ns%2Ftest-server/releases')
  })

  test('returns E_MISSING_MANIFEST when no manifest.json', async () => {
    tmpDir = makeTmpBundleDir() // no manifest written

    const result = await publishToSmithery({
      ...BASE_OPTS,
      bundleDir: tmpDir,
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_VALIDATION_FAILED')
  })

  test('returns E_INVALID_MANIFEST on bad JSON', async () => {
    tmpDir = join(tmpdir(), `smithery-publish-test-badjson-${Date.now()}`)
    mkdirSync(tmpDir, { recursive: true })
    writeFileSync(join(tmpDir, 'manifest.json'), '{ broken json!!!}')

    const result = await publishToSmithery({
      ...BASE_OPTS,
      bundleDir: tmpDir,
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_VALIDATION_FAILED')
  })
})

// ---------------------------------------------------------------------------
// pollDeployment
// ---------------------------------------------------------------------------

describe('pollDeployment', () => {
  test('returns published on SUCCESS status', async () => {
    mockFetch(async () =>
      jsonResponse({
        status: 'SUCCESS',
        mcpUrl: 'https://smithery.ai/server/ns/srv',
      })
    )

    const result = await pollDeployment('ns/srv', 'dep-1', 'sk-key', {
      baseUrl: BASE_URL,
      timeoutMs: 5_000,
      intervalMs: 50,
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.status).toBe('published')
    expect(result.value.releaseId).toBe('dep-1')
    expect(result.value.registryUrl).toBe('https://smithery.ai/server/ns/srv')
  })

  test('returns failed on FAILURE status', async () => {
    mockFetch(async () =>
      jsonResponse({
        status: 'FAILURE',
        logs: [{ stage: 'build', level: 'error', message: 'Build failed: missing entry point' }],
      })
    )

    const result = await pollDeployment('ns/srv', 'dep-2', 'sk-key', {
      baseUrl: BASE_URL,
      timeoutMs: 5_000,
      intervalMs: 50,
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.status).toBe('failed')
    expect(result.value.ok).toBe(false)
    expect(result.value.error).toContain('Build failed')
  })

  test('returns E_DEPLOY_TIMEOUT after timeout', async () => {
    mockFetch(async () => jsonResponse({ status: 'PENDING' }))

    const result = await pollDeployment('ns/srv', 'dep-3', 'sk-key', {
      baseUrl: BASE_URL,
      timeoutMs: 100,
      intervalMs: 30,
    })

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_PROVIDER_TIMEOUT')
  })

  test('continues polling on PENDING status then succeeds', async () => {
    let callCount = 0

    mockFetch(async () => {
      callCount++
      if (callCount < 3) {
        return jsonResponse({ status: 'PENDING' })
      }
      return jsonResponse({
        status: 'SUCCESS',
        mcpUrl: 'https://smithery.ai/server/ns/srv',
      })
    })

    const result = await pollDeployment('ns/srv', 'dep-4', 'sk-key', {
      baseUrl: BASE_URL,
      timeoutMs: 5_000,
      intervalMs: 30,
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.status).toBe('published')
    expect(callCount).toBeGreaterThanOrEqual(3)
  })

  test('handles network errors during poll gracefully', async () => {
    let callCount = 0

    mockFetch(async () => {
      callCount++
      if (callCount === 1) {
        throw new Error('Network timeout')
      }
      return jsonResponse({
        status: 'SUCCESS',
        mcpUrl: 'https://smithery.ai/server/ns/srv',
      })
    })

    const result = await pollDeployment('ns/srv', 'dep-5', 'sk-key', {
      baseUrl: BASE_URL,
      timeoutMs: 5_000,
      intervalMs: 30,
    })

    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.status).toBe('published')
    expect(callCount).toBeGreaterThanOrEqual(2)
  })
})
