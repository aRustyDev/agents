// cli/test/github-token.test.ts
import { afterEach, beforeEach, describe, expect, it } from 'bun:test'

// We test the keyring wrapper and token provider logic.
// Tests use a unique service name to avoid polluting the real keychain.
const TEST_SERVICE = 'arustydev/agents/test-github-token'
const TEST_ACCOUNT = 'test-user'

describe('KeyringTokenStore', () => {
  // Dynamically import to allow mocking
  let _store: typeof import('@agents/core/github')

  beforeEach(async () => {
    _store = await import('@agents/core/github')
  })

  afterEach(() => {
    // Clean up test keychain entry
    try {
      const { Entry } = require('@napi-rs/keyring')
      new Entry(TEST_SERVICE, TEST_ACCOUNT).deletePassword()
    } catch {
      /* ignore */
    }
  })

  it('stores and retrieves a token from the keychain', () => {
    const { Entry } = require('@napi-rs/keyring')
    const entry = new Entry(TEST_SERVICE, TEST_ACCOUNT)
    const data = JSON.stringify({ token: 'gho_test123', expiresAt: Date.now() + 3600000 })
    entry.setPassword(data)

    const raw = entry.getPassword()
    expect(raw).toBeTruthy()
    const parsed = JSON.parse(raw as string)
    expect(parsed.token).toBe('gho_test123')
    expect(parsed.expiresAt).toBeGreaterThan(Date.now())
  })

  it('returns null or throws for nonexistent keychain entry', () => {
    const { Entry } = require('@napi-rs/keyring')
    const entry = new Entry(TEST_SERVICE, 'nonexistent-account')
    try {
      const pw = entry.getPassword()
      // Some platforms return null for missing entries
      expect(pw).toBeNull()
    } catch {
      // Other platforms throw — this is also acceptable
      expect(true).toBe(true)
    }
  })

  it('overwrites existing entry', () => {
    const { Entry } = require('@napi-rs/keyring')
    const entry = new Entry(TEST_SERVICE, TEST_ACCOUNT)
    entry.setPassword('first')
    entry.setPassword('second')
    expect(entry.getPassword()).toBe('second')
  })
})

describe('GitHubTokenProvider', () => {
  it('returns GITHUB_TOKEN env var when set (highest priority)', async () => {
    const originalToken = process.env.GITHUB_TOKEN
    try {
      process.env.GITHUB_TOKEN = 'gho_env_override_test'
      // Re-import to pick up env change
      const { GitHubTokenProvider } = await import('@agents/core/github')
      const provider = new GitHubTokenProvider({
        service: TEST_SERVICE,
        account: TEST_ACCOUNT,
      })
      const token = await provider.getToken()
      expect(token).toBe('gho_env_override_test')
    } finally {
      if (originalToken) {
        process.env.GITHUB_TOKEN = originalToken
      } else {
        delete process.env.GITHUB_TOKEN
      }
    }
  })

  it('mutex: concurrent calls return the same token', async () => {
    const { GitHubTokenProvider } = await import('@agents/core/github')
    const provider = new GitHubTokenProvider({
      service: TEST_SERVICE,
      account: TEST_ACCOUNT,
      // Provide a mock token source to avoid triggering real device flow
      tokenSource: async () => 'gho_mutex_test_token',
    })

    // Fire 5 concurrent requests
    const results = await Promise.all([
      provider.getToken(),
      provider.getToken(),
      provider.getToken(),
      provider.getToken(),
      provider.getToken(),
    ])

    // All should return the same token
    expect(new Set(results).size).toBe(1)
    expect(results[0]).toBe('gho_mutex_test_token')
  })

  it('uses cached keyring token when not expired', async () => {
    // Pre-seed the keyring
    const { Entry } = require('@napi-rs/keyring')
    const entry = new Entry(TEST_SERVICE, TEST_ACCOUNT)
    entry.setPassword(
      JSON.stringify({
        token: 'gho_cached_token',
        expiresAt: Date.now() + 3600000, // 1 hour from now
      })
    )

    const { GitHubTokenProvider } = await import('@agents/core/github')
    let deviceFlowCalled = false
    const provider = new GitHubTokenProvider({
      service: TEST_SERVICE,
      account: TEST_ACCOUNT,
      tokenSource: async () => {
        deviceFlowCalled = true
        return 'gho_fresh'
      },
    })

    const token = await provider.getToken()
    expect(token).toBe('gho_cached_token')
    expect(deviceFlowCalled).toBe(false)
  })

  it('refreshes when cached token is expired', async () => {
    // Pre-seed with expired token
    const { Entry } = require('@napi-rs/keyring')
    const entry = new Entry(TEST_SERVICE, TEST_ACCOUNT)
    entry.setPassword(
      JSON.stringify({
        token: 'gho_expired',
        expiresAt: Date.now() - 1000, // expired 1 second ago
      })
    )

    const { GitHubTokenProvider } = await import('@agents/core/github')
    const provider = new GitHubTokenProvider({
      service: TEST_SERVICE,
      account: TEST_ACCOUNT,
      tokenSource: async () => 'gho_refreshed',
    })

    const token = await provider.getToken()
    expect(token).toBe('gho_refreshed')

    // Verify it was stored in keyring
    const stored = JSON.parse(entry.getPassword() as string)
    expect(stored.token).toBe('gho_refreshed')
  })
})
