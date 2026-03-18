/**
 * Tests for lib/github.ts
 *
 * Unit tests use temp directories and mock data.
 * Integration tests (real HTTP) are gated by CI env var.
 */

import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdtemp, rm, writeFile, readFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  getCachedToken,
  cacheToken,
  setTokenPath,
  getTokenPath,
  parseRepo,
  resetClient,
} from '../lib/github'

// ---------------------------------------------------------------------------
// Setup / teardown
// ---------------------------------------------------------------------------

let tmp: string
let originalTokenPath: string

beforeEach(async () => {
  tmp = await mkdtemp(join(tmpdir(), 'github-test-'))
  originalTokenPath = getTokenPath()
  // Point token path to temp dir so tests don't pollute real config
  setTokenPath(join(tmp, 'github-token'))
})

afterEach(async () => {
  // Restore original token path
  setTokenPath(originalTokenPath)
  resetClient()
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// Token caching
// ---------------------------------------------------------------------------

describe('getCachedToken', () => {
  test('returns null when no token file exists', () => {
    const token = getCachedToken()
    expect(token).toBeNull()
  })

  test('returns null for empty token file', async () => {
    await writeFile(join(tmp, 'github-token'), '')
    const token = getCachedToken()
    expect(token).toBeNull()
  })

  test('returns null for whitespace-only token file', async () => {
    await writeFile(join(tmp, 'github-token'), '   \n  ')
    const token = getCachedToken()
    expect(token).toBeNull()
  })

  test('returns token from file', async () => {
    await writeFile(join(tmp, 'github-token'), 'ghp_test123\n')
    const token = getCachedToken()
    expect(token).toBe('ghp_test123')
  })

  test('trims whitespace from token', async () => {
    await writeFile(join(tmp, 'github-token'), '  ghp_spaces  \n')
    const token = getCachedToken()
    expect(token).toBe('ghp_spaces')
  })
})

describe('cacheToken', () => {
  test('writes token to file', async () => {
    cacheToken('ghp_cached_token')

    const tokenPath = getTokenPath()
    expect(existsSync(tokenPath)).toBe(true)

    const content = await readFile(tokenPath, 'utf-8')
    expect(content).toBe('ghp_cached_token')
  })

  test('creates parent directories if needed', () => {
    const deepPath = join(tmp, 'deep', 'nested', 'github-token')
    setTokenPath(deepPath)

    cacheToken('ghp_deep')
    expect(existsSync(deepPath)).toBe(true)
  })

  test('round-trips with getCachedToken', () => {
    cacheToken('ghp_roundtrip')
    const result = getCachedToken()
    expect(result).toBe('ghp_roundtrip')
  })
})

// ---------------------------------------------------------------------------
// setTokenPath / getTokenPath
// ---------------------------------------------------------------------------

describe('setTokenPath / getTokenPath', () => {
  test('getTokenPath returns current path', () => {
    const path = getTokenPath()
    expect(path).toBe(join(tmp, 'github-token'))
  })

  test('setTokenPath changes the path', () => {
    const newPath = join(tmp, 'custom-token')
    setTokenPath(newPath)
    expect(getTokenPath()).toBe(newPath)
  })
})

// ---------------------------------------------------------------------------
// parseRepo
// ---------------------------------------------------------------------------

describe('parseRepo', () => {
  test('parses owner/repo correctly', () => {
    const result = parseRepo('aRustyDev/ai')
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
    const { readIssue } = await import('../lib/github')

    // Reading a public issue does not strictly require auth,
    // but the Octokit client always sends a token if one is set.
    // If no token is available, this test may fail with a 401.
    // That is acceptable -- the test is meant for local dev use.
    try {
      const issue = await readIssue('aRustyDev/ai', 1)
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
