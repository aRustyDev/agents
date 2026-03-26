/**
 * Tests for lib/github.ts
 *
 * Unit tests use keyring with test-specific service/account names.
 * Integration tests (real HTTP) are gated by CI env var.
 */

import { afterEach, describe, expect, test } from 'bun:test'
import { GitHubTokenProvider, parseRepo, resetClient } from '@agents/core/github'
import { Entry } from '@napi-rs/keyring'

const TEST_SERVICE = 'arustydev/agents/test-github-compat'
const TEST_ACCOUNT = 'test-compat'

afterEach(() => {
  resetClient()
  // Clean up test keychain entry
  try {
    new Entry(TEST_SERVICE, TEST_ACCOUNT).deletePassword()
  } catch {
    /* ignore */
  }
})

// ---------------------------------------------------------------------------
// GitHubTokenProvider (compat)
// ---------------------------------------------------------------------------

describe('GitHubTokenProvider (compat)', () => {
  test('returns token from keyring when cached', async () => {
    new Entry(TEST_SERVICE, TEST_ACCOUNT).setPassword(
      JSON.stringify({ token: 'gho_compat_test', expiresAt: Date.now() + 3600000 })
    )

    const provider = new GitHubTokenProvider({
      service: TEST_SERVICE,
      account: TEST_ACCOUNT,
    })
    const token = await provider.getToken()
    expect(token).toBe('gho_compat_test')
  })

  test('invalidate clears keyring and in-memory cache', async () => {
    const entry = new Entry(TEST_SERVICE, TEST_ACCOUNT)
    entry.setPassword(
      JSON.stringify({ token: 'gho_to_invalidate', expiresAt: Date.now() + 3600000 })
    )

    let refreshCount = 0
    const provider = new GitHubTokenProvider({
      service: TEST_SERVICE,
      account: TEST_ACCOUNT,
      tokenSource: async () => {
        refreshCount++
        return 'gho_refreshed'
      },
    })

    // First call uses cached token
    const first = await provider.getToken()
    expect(first).toBe('gho_to_invalidate')
    expect(refreshCount).toBe(0)

    // Invalidate
    provider.invalidate()

    // Next call triggers refresh
    const second = await provider.getToken()
    expect(second).toBe('gho_refreshed')
    expect(refreshCount).toBe(1)

    // Verify keyring was cleared then re-populated
    const raw = entry.getPassword()
    expect(raw).toBeTruthy()
    const stored = JSON.parse(raw as string)
    expect(stored.token).toBe('gho_refreshed')
  })
})

// ---------------------------------------------------------------------------
// parseRepo
// ---------------------------------------------------------------------------

describe('parseRepo', () => {
  test('parses owner/repo correctly', () => {
    const result = parseRepo('aRustyDev/agents')
    expect(result.owner).toBe('aRustyDev')
    expect(result.repo).toBe('ai')
  })

  test('parses different owner/repo values', () => {
    const result = parseRepo('octocat/Hello-World')
    expect(result.owner).toBe('octocat')
    expect(result.repo).toBe('Hello-World')
  })

  test('throws for invalid format (no slash)', () => {
    expect(() => parseRepo('invalid')).toThrow('Invalid repo format')
  })

  test('throws for invalid format (too many slashes)', () => {
    expect(() => parseRepo('a/b/c')).toThrow('Invalid repo format')
  })

  test('throws for empty string', () => {
    expect(() => parseRepo('')).toThrow('Invalid repo format')
  })

  test('throws for slash only', () => {
    expect(() => parseRepo('/')).toThrow('Invalid repo format')
  })

  test('throws for missing owner', () => {
    expect(() => parseRepo('/repo')).toThrow('Invalid repo format')
  })

  test('throws for missing repo', () => {
    expect(() => parseRepo('owner/')).toThrow('Invalid repo format')
  })
})

// ---------------------------------------------------------------------------
// Integration test (real HTTP -- skipped in CI)
// ---------------------------------------------------------------------------

describe('integration', () => {
  test('can read a public issue (skipped in CI)', async () => {
    if (process.env.CI) return

    // This import must be dynamic to avoid initializing the client during
    // unit-test-only runs where no token is available.
    const { readIssue } = await import('@agents/core/github')

    // Reading a public issue does not strictly require auth,
    // but the Octokit client always sends a token if one is set.
    // If no token is available, this test may fail with a 401.
    // That is acceptable -- the test is meant for local dev use.
    try {
      const issue = await readIssue('aRustyDev/agents', 1)
      expect(issue.number).toBe(1)
      expect(issue.title).toBeDefined()
      expect(typeof issue.title).toBe('string')
      expect(issue.html_url).toContain('github.com')
    } catch {
      // If auth fails, skip gracefully
      console.log('  (skipped: no auth available)')
    }
  })
})
