import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { resolveSmitheryAuth, validateSmitheryApiKey } from '../../src/providers/smithery/auth'

describe('resolveSmitheryAuth', () => {
  const originalEnv = process.env.SMITHERY_API_KEY

  afterEach(() => {
    if (originalEnv !== undefined) {
      process.env.SMITHERY_API_KEY = originalEnv
    } else {
      delete process.env.SMITHERY_API_KEY
    }
  })

  test('resolves from explicit apiKey option', () => {
    const result = resolveSmitheryAuth({ apiKey: 'explicit-key' })
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value.apiKey).toBe('explicit-key')
  })

  test('resolves from SMITHERY_API_KEY env var', () => {
    process.env.SMITHERY_API_KEY = 'env-key'
    const result = resolveSmitheryAuth()
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value.apiKey).toBe('env-key')
  })

  test('explicit option takes precedence over env var', () => {
    process.env.SMITHERY_API_KEY = 'env-key'
    const result = resolveSmitheryAuth({ apiKey: 'explicit-key' })
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value.apiKey).toBe('explicit-key')
  })

  test('returns E_AUTH_REQUIRED when no key available', () => {
    delete process.env.SMITHERY_API_KEY
    const result = resolveSmitheryAuth()
    expect(result.ok).toBe(false)
    if (!result.ok) {
      expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
      expect(result.error.detail).toContain('SMITHERY_API_KEY')
    }
  })

  test('returns E_AUTH_REQUIRED with empty opts', () => {
    delete process.env.SMITHERY_API_KEY
    const result = resolveSmitheryAuth({})
    expect(result.ok).toBe(false)
  })
})

describe('validateSmitheryApiKey', () => {
  let originalFetch: typeof globalThis.fetch

  beforeEach(() => {
    originalFetch = globalThis.fetch
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  test('returns true for 200 response', async () => {
    globalThis.fetch = (async () => new Response('{}', { status: 200 })) as typeof fetch
    const result = await validateSmitheryApiKey('valid-key')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toBe(true)
  })

  test('returns false for 401 response', async () => {
    globalThis.fetch = (async () => new Response('', { status: 401 })) as typeof fetch
    const result = await validateSmitheryApiKey('bad-key')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toBe(false)
  })

  test('returns false for 403 response', async () => {
    globalThis.fetch = (async () => new Response('', { status: 403 })) as typeof fetch
    const result = await validateSmitheryApiKey('forbidden-key')
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toBe(false)
  })

  test('returns E_API_ERROR for 500 response', async () => {
    globalThis.fetch = (async () => new Response('', { status: 500 })) as typeof fetch
    const result = await validateSmitheryApiKey('key')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })

  test('returns E_NETWORK on network error', async () => {
    globalThis.fetch = (async () => {
      throw new Error('ECONNREFUSED')
    }) as typeof fetch
    const result = await validateSmitheryApiKey('key')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
  })

  test('returns E_TIMEOUT on timeout', async () => {
    globalThis.fetch = (async () => {
      throw new DOMException('Aborted', 'AbortError')
    }) as typeof fetch
    const result = await validateSmitheryApiKey('key')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_PROVIDER_TIMEOUT')
  })

  test('sends Authorization header', async () => {
    let capturedHeaders: Headers | undefined
    globalThis.fetch = (async (_url: string | URL | Request, init?: RequestInit) => {
      capturedHeaders = new Headers(init?.headers)
      return new Response('{}', { status: 200 })
    }) as typeof fetch
    await validateSmitheryApiKey('my-key')
    expect(capturedHeaders?.get('Authorization')).toBe('Bearer my-key')
  })

  test('uses custom base URL', async () => {
    let capturedUrl = ''
    globalThis.fetch = (async (url: string | URL | Request) => {
      capturedUrl = String(url)
      return new Response('{}', { status: 200 })
    }) as typeof fetch
    await validateSmitheryApiKey('key', 'https://custom.api.com')
    expect(capturedUrl).toContain('custom.api.com')
  })
})
