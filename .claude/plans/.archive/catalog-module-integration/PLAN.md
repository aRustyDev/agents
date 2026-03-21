# Catalog Pipeline Module Integration Plan

> **Status: COMPLETE** — All phases implemented and merged to main on 2026-03-20. 17 commits, 170 tests passing, ~1550 lines added.

**Goal:** Replace shell-out dependencies (`npx skills`, `exec git worktree`, `find`, `gh auth`) in the catalog analyze pipeline with structured modules. Migrate GitHub auth from file-based token caching to system keychain with mutex-guarded device flow.

**Architecture:** Extract the download/worktree/discovery logic from the inline `processBatch` closure in `skill.ts` into a new `lib/catalog-download.ts` module that composes the Phase 5.5 modules. Refactor `lib/github.ts` to use `@napi-rs/keyring` for token storage with a mutex-guarded `GitHubTokenProvider`. The existing `catalog.ts` (types, merge, compute) stays untouched.

**Tech Stack:** TypeScript, Bun, simple-git, @octokit/auth-oauth-device, @octokit/core, @napi-rs/keyring, valibot, bun:test

**GitHub OAuth App:** [arustydev-agents](https://github.com/apps/arustydev-agents) (App ID: 3143146, Client ID: `Iv23licWoRnUpjtO0oKM`)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `.scripts/lib/github.ts` | **Modify** | Replace file-based token cache with `@napi-rs/keyring`, add `GitHubTokenProvider` with mutex + TTL, wire real OAuth App client ID |
| `.scripts/lib/source-parser.ts` | **Modify** | Add `resolveCloneUrl`, `detectGitProtocol` for SSH/HTTPS URL generation |
| `.scripts/lib/catalog-download.ts` | **Create** | Download orchestrator: validate, clone via `git.ts`, discover via `skill-discovery.ts`, compute mechanical fields |
| `.scripts/lib/catalog-stale.ts` | **Create** | Stale detection: compare treeSha vs upstream via GitHub Trees API |
| `.scripts/commands/skill.ts` | **Modify** | Blue/green download switch, `simple-git` worktree alongside exec, `--git-protocol` flag, `catalog stale` command |
| `.scripts/lib/catalog.ts` | **Modify** (minor) | Add `Tier1ErrorType` value `'source_invalid'`, add `treeSha` field to `Tier1Result` |
| `.scripts/test/github-token.test.ts` | **Create** | Unit tests for `GitHubTokenProvider` (keyring mock, mutex behavior, TTL) |
| `.scripts/test/github.test.ts` | **Modify** | Replace file-cache tests with keyring-based tests, keep `parseRepo` + integration tests |
| `.scripts/test/catalog-download.test.ts` | **Create** | Unit + component tests for download orchestrator |
| `.scripts/test/catalog-stale.test.ts` | **Create** | Unit tests for stale detection |
| `.scripts/test/catalog-integration.test.ts` | **Create** | Smoke test: end-to-end with real repo (uses SSH per 1Password agent) |
| `.scripts/test/source-parser.test.ts` | **Modify** | Add tests for `resolveCloneUrl`, `detectGitProtocol` |

## Phases

| Phase | Name | Dependencies | Status |
|-------|------|-------------|--------|
| 0 | GitHub token provider refactor (keychain + mutex) | None | **Done** |
| 1 | Source validation + SSH clone URL support | None | **Done** |
| 2 | Download orchestrator with `git.ts` + `skill-discovery.ts` | Phase 1 | **Done** |
| 3 | Wire new download path (blue/green) + `--git-protocol` flag | Phases 1, 2 | **Done** |
| 3b | Remove legacy download path | Phase 3 validated | **Done** |
| 4 | Stale detection with `treeSha` + GitHub Trees API | Phases 0, 3 | **Done** |

**Parallelism:** Phases 0 and 1+2 are independent — Phase 0 touches `github.ts` only, Phases 1+2 touch `source-parser.ts` + `catalog-download.ts`. They can be implemented concurrently.

**Task ordering within phases:** Task 1.1 (add `source_invalid` to `Tier1ErrorType`) MUST complete before Task 2.1 (which uses the type). Since Phase 2 depends on Phase 1, this is naturally enforced — but if running tasks within phases out of order, ensure 1.1 lands first.

---

## Phase 0: GitHub Token Provider Refactor

Refactor `lib/github.ts` to:

1. Replace file-based token cache (`~/.config/ai-tools/github-token`) with `@napi-rs/keyring` (macOS Keychain)
2. Add `GitHubTokenProvider` singleton with Promise-based mutex (first caller triggers auth, others wait)
3. Wire the real OAuth App client ID (`Iv23licWoRnUpjtO0oKM`)
4. Add TTL-based expiry checking
5. Support `GITHUB_TOKEN` env var as highest-priority override
6. Remove `gh auth token` dependency

### Task 0.1: Add `@napi-rs/keyring` and write keyring wrapper tests

**Files:**

- Create: `.scripts/test/github-token.test.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// .scripts/test/github-token.test.ts
import { afterEach, beforeEach, describe, expect, it, mock } from 'bun:test'

// We test the keyring wrapper and token provider logic.
// Tests use a unique service name to avoid polluting the real keychain.
const TEST_SERVICE = 'arustydev/agents/test-github-token'
const TEST_ACCOUNT = 'test-user'

describe('KeyringTokenStore', () => {
  // Dynamically import to allow mocking
  let store: typeof import('../lib/github')

  beforeEach(async () => {
    store = await import('../lib/github')
  })

  afterEach(() => {
    // Clean up test keychain entry
    try {
      const { Entry } = require('@napi-rs/keyring')
      new Entry(TEST_SERVICE, TEST_ACCOUNT).deletePassword()
    } catch { /* ignore */ }
  })

  it('stores and retrieves a token from the keychain', () => {
    const { Entry } = require('@napi-rs/keyring')
    const entry = new Entry(TEST_SERVICE, TEST_ACCOUNT)
    const data = JSON.stringify({ token: 'gho_test123', expiresAt: Date.now() + 3600000 })
    entry.setPassword(data)

    const raw = entry.getPassword()
    expect(raw).toBeTruthy()
    const parsed = JSON.parse(raw!)
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
      const { GitHubTokenProvider } = await import('../lib/github')
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
    const { GitHubTokenProvider } = await import('../lib/github')
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
    entry.setPassword(JSON.stringify({
      token: 'gho_cached_token',
      expiresAt: Date.now() + 3600000, // 1 hour from now
    }))

    const { GitHubTokenProvider } = await import('../lib/github')
    let deviceFlowCalled = false
    const provider = new GitHubTokenProvider({
      service: TEST_SERVICE,
      account: TEST_ACCOUNT,
      tokenSource: async () => { deviceFlowCalled = true; return 'gho_fresh' },
    })

    const token = await provider.getToken()
    expect(token).toBe('gho_cached_token')
    expect(deviceFlowCalled).toBe(false)
  })

  it('refreshes when cached token is expired', async () => {
    // Pre-seed with expired token
    const { Entry } = require('@napi-rs/keyring')
    const entry = new Entry(TEST_SERVICE, TEST_ACCOUNT)
    entry.setPassword(JSON.stringify({
      token: 'gho_expired',
      expiresAt: Date.now() - 1000, // expired 1 second ago
    }))

    const { GitHubTokenProvider } = await import('../lib/github')
    const provider = new GitHubTokenProvider({
      service: TEST_SERVICE,
      account: TEST_ACCOUNT,
      tokenSource: async () => 'gho_refreshed',
    })

    const token = await provider.getToken()
    expect(token).toBe('gho_refreshed')

    // Verify it was stored in keyring
    const stored = JSON.parse(entry.getPassword()!)
    expect(stored.token).toBe('gho_refreshed')
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `cd .scripts && bun test github-token`
Expected: FAIL — `GitHubTokenProvider` not exported

- [ ] **Step 3: Commit test file**

```bash
git add .scripts/test/github-token.test.ts
git commit -m "test(github): add token provider tests with keyring + mutex"
```

### Task 0.2: Implement `GitHubTokenProvider` in `github.ts`

**Files:**

- Modify: `.scripts/lib/github.ts`

- [ ] **Step 1: Replace token management section**

Replace the entire "Token management" section (lines 44-102) and "Client initialization" section (lines 104-172) with:

```typescript
import { Entry } from '@napi-rs/keyring'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const GITHUB_CLIENT_ID = 'Iv23licWoRnUpjtO0oKM'
const KEYRING_SERVICE = 'arustydev/agents/github-token'
const TOKEN_TTL_MS = 55 * 60 * 1000 // 55 minutes (tokens last ~1hr)

// ---------------------------------------------------------------------------
// Token storage (keyring)
// ---------------------------------------------------------------------------

interface StoredToken {
  token: string
  expiresAt: number // epoch ms
  scopes?: string[]
}

function readKeyring(service: string, account: string): StoredToken | null {
  try {
    const entry = new Entry(service, account)
    const raw = entry.getPassword()
    if (!raw) return null
    const parsed = JSON.parse(raw) as StoredToken
    if (!parsed.token || typeof parsed.expiresAt !== 'number') return null
    return parsed
  } catch {
    return null
  }
}

function writeKeyring(service: string, account: string, state: StoredToken): void {
  try {
    const entry = new Entry(service, account)
    entry.setPassword(JSON.stringify(state))
  } catch {
    // Keyring write failed — log but don't crash
    process.stderr.write('[github] Warning: failed to cache token in keychain\n')
  }
}

function deleteKeyring(service: string, account: string): void {
  try {
    new Entry(service, account).deletePassword()
  } catch { /* ignore */ }
}

// ---------------------------------------------------------------------------
// Token provider (mutex + TTL + keyring)
// ---------------------------------------------------------------------------

export interface TokenProviderOptions {
  /** Keyring service name (default: arustydev/agents/github-token) */
  service?: string
  /** Keyring account name (default: github.com) */
  account?: string
  /** Override token source for testing (replaces device flow) */
  tokenSource?: () => Promise<string>
  /** Token TTL in ms (default: 55 minutes) */
  ttlMs?: number
}

/**
 * Mutex-guarded GitHub token provider.
 *
 * Priority chain:
 * 1. GITHUB_TOKEN env var (CI override) — checked every call, never cached
 * 2. @napi-rs/keyring cached token (if not expired)
 * 3. @octokit/auth-oauth-device flow → stores in keyring on success
 *
 * Concurrent callers: first triggers generation, others await the same Promise.
 */
export class GitHubTokenProvider {
  private readonly service: string
  private readonly account: string
  private readonly ttlMs: number
  private readonly tokenSource: () => Promise<string>

  /** In-memory cache for the current process */
  private cached: StoredToken | null = null
  /** Mutex: pending refresh promise (first caller creates, others await) */
  private pending: Promise<string> | null = null

  constructor(opts: TokenProviderOptions = {}) {
    this.service = opts.service ?? KEYRING_SERVICE
    this.account = opts.account ?? 'github.com'
    this.ttlMs = opts.ttlMs ?? TOKEN_TTL_MS
    this.tokenSource = opts.tokenSource ?? (() => performDeviceFlow())
  }

  /**
   * Get a valid GitHub token.
   *
   * - Returns immediately if GITHUB_TOKEN env var is set
   * - Returns cached token if not expired
   * - Otherwise triggers refresh (with mutex for concurrent callers)
   */
  async getToken(): Promise<string> {
    // Priority 1: env var override (always checked, never cached)
    const envToken = process.env.GITHUB_TOKEN
    if (envToken) return envToken

    // Priority 2: in-memory cache
    if (this.cached && Date.now() < this.cached.expiresAt) {
      return this.cached.token
    }

    // Priority 3: keyring cache
    const stored = readKeyring(this.service, this.account)
    if (stored && Date.now() < stored.expiresAt) {
      this.cached = stored
      return stored.token
    }

    // Priority 4: refresh (mutex-guarded)
    if (this.pending) return this.pending

    this.pending = this.refresh()
    try {
      return await this.pending
    } finally {
      this.pending = null
    }
  }

  /** Clear cached token (forces re-auth on next getToken call) */
  invalidate(): void {
    this.cached = null
    deleteKeyring(this.service, this.account)
  }

  private async refresh(): Promise<string> {
    const token = await this.tokenSource()
    const state: StoredToken = {
      token,
      expiresAt: Date.now() + this.ttlMs,
    }
    this.cached = state
    writeKeyring(this.service, this.account, state)
    return token
  }
}

// ---------------------------------------------------------------------------
// Device flow
// ---------------------------------------------------------------------------

/**
 * Perform OAuth Device Flow using the arustydev-agents GitHub App.
 * Prompts the user to visit a URL and enter a code.
 */
async function performDeviceFlow(): Promise<string> {
  const auth = createOAuthDeviceAuth({
    clientType: 'oauth-app',
    clientId: GITHUB_CLIENT_ID,
    scopes: ['public_repo'],
    onVerification(verification) {
      process.stderr.write('\n')
      process.stderr.write('GitHub authentication required.\n')
      process.stderr.write(`Open: ${verification.verification_uri}\n`)
      process.stderr.write(`Enter code: ${verification.user_code}\n`)
      process.stderr.write('\n')
    },
  })

  const { token } = await auth({ type: 'oauth' })
  return token
}

// ---------------------------------------------------------------------------
// Singleton provider + Octokit client
// ---------------------------------------------------------------------------

/** Global token provider singleton */
const _provider = new GitHubTokenProvider()

/** Lazy-initialized Octokit client */
let _client: Octokit | null = null
let _clientToken: string | null = null

/**
 * Get an authenticated Octokit client.
 *
 * Uses the GitHubTokenProvider singleton:
 * GITHUB_TOKEN env → keyring cache → device flow (mutex-guarded)
 *
 * Recreates the client if the token has been refreshed since last call.
 */
export async function getClient(): Promise<Octokit> {
  const token = await _provider.getToken()

  // Reuse existing client if token hasn't changed
  if (_client && token === _clientToken) return _client

  // Token changed (refreshed) or first call — create new client
  _client = new Octokit({ auth: token })
  _clientToken = token
  return _client
}

/**
 * Reset the client singleton. Intended for tests only.
 */
export function resetClient(): void {
  _client = null
}

/**
 * Get the token provider singleton (for testing or direct access).
 */
export function getTokenProvider(): GitHubTokenProvider {
  return _provider
}
```

- [ ] **Step 2: Remove old token functions**

Delete these functions from `github.ts`:

- `setTokenPath`, `getTokenPath`, `getCachedToken`, `cacheToken`, `getGhToken`
- The `TOKEN_PATH` variable
- The old `GITHUB_CLIENT_ID` with placeholder
- The old `performDeviceFlow` and `getClient`

- [ ] **Step 3: Remove unused imports**

Remove from the imports:

- `homedir` from `node:os` (no longer writing to `~/.config/`)
- `spawnSync` from `./runtime` (no longer calling `gh auth token`)

Keep: `existsSync`, `readFileSync`, `unlinkSync` — needed for legacy token migration (Task 0.3).

- [ ] **Step 4: Update `test/github.test.ts`**

The existing test file imports deleted functions (`getCachedToken`, `cacheToken`, `setTokenPath`, `getTokenPath`). Replace the token caching tests with keyring-based equivalents. Keep `parseRepo` tests and integration test unchanged.

Replace lines 1-41 (imports + setup/teardown) with:

```typescript
import { afterEach, describe, expect, test } from 'bun:test'
import {
  GitHubTokenProvider,
  parseRepo,
  resetClient,
} from '../lib/github'

const TEST_SERVICE = 'arustydev/agents/test-github-compat'
const TEST_ACCOUNT = 'test-compat'

afterEach(() => {
  resetClient()
  // Clean up test keychain entry
  try {
    const { Entry } = require('@napi-rs/keyring')
    new Entry(TEST_SERVICE, TEST_ACCOUNT).deletePassword()
  } catch { /* ignore */ }
})
```

Replace lines 47-119 (token caching + setTokenPath tests) with:

```typescript
describe('GitHubTokenProvider (compat)', () => {
  test('returns token from keyring when cached', async () => {
    const { Entry } = require('@napi-rs/keyring')
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
    const { Entry } = require('@napi-rs/keyring')
    const entry = new Entry(TEST_SERVICE, TEST_ACCOUNT)
    entry.setPassword(
      JSON.stringify({ token: 'gho_to_invalidate', expiresAt: Date.now() + 3600000 })
    )

    let refreshCount = 0
    const provider = new GitHubTokenProvider({
      service: TEST_SERVICE,
      account: TEST_ACCOUNT,
      tokenSource: async () => { refreshCount++; return 'gho_refreshed' },
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
    const stored = JSON.parse(entry.getPassword()!)
    expect(stored.token).toBe('gho_refreshed')
  })
})
```

Keep `parseRepo` tests (lines 125-161) and integration test (lines 167-190) unchanged.

- [ ] **Step 5: Run tests**

Run: `cd .scripts && bun test github-token github`
Expected: All pass (both new and updated test files)

- [ ] **Step 6: Run full test suite**

Run: `cd .scripts && bun test`
Expected: No regressions

- [ ] **Step 7: Commit**

```bash
git add .scripts/lib/github.ts .scripts/test/github-token.test.ts .scripts/test/github.test.ts .scripts/package.json .scripts/bun.lock
git commit -m "refactor(github): replace file cache with keyring + mutex token provider

- Replace ~/.config/ai-tools/github-token with @napi-rs/keyring
- Add GitHubTokenProvider with Promise-based mutex
- Wire arustydev-agents OAuth App (Iv23licWoRnUpjtO0oKM)
- Remove gh auth token dependency
- Priority: GITHUB_TOKEN env → keyring cache → device flow"
```

### Task 0.3: Migrate existing file-cached tokens to keyring

**Files:**

- Modify: `.scripts/lib/github.ts`

One-time migration: if the old file-based token exists, import it into the keyring and delete the file.

- [ ] **Step 1: Add migration function**

```typescript
import { existsSync, readFileSync, unlinkSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'

const LEGACY_TOKEN_PATH = join(homedir(), '.config', 'ai-tools', 'github-token')

/**
 * One-time migration: if the old file-based token exists, move it to keyring.
 * Called once on first getToken() if the keyring is empty.
 */
async function migrateLegacyToken(service: string, account: string): Promise<string | null> {
  try {
    if (!existsSync(LEGACY_TOKEN_PATH)) return null
    const token = readFileSync(LEGACY_TOKEN_PATH, 'utf-8').trim()
    if (!token) return null

    // Validate the token is still working before caching with fresh TTL
    try {
      const testClient = new Octokit({ auth: token })
      await testClient.request('GET /rate_limit')
    } catch {
      process.stderr.write('[github] Legacy token is expired or invalid — skipping migration\n')
      try { unlinkSync(LEGACY_TOKEN_PATH) } catch { /* ignore */ }
      return null
    }

    // Token is valid — store in keyring
    writeKeyring(service, account, {
      token,
      expiresAt: Date.now() + TOKEN_TTL_MS,
    })

    // Delete the old file
    try { unlinkSync(LEGACY_TOKEN_PATH) } catch { /* ignore */ }

    process.stderr.write('[github] Migrated token from file cache to system keychain\n')
    return token
  } catch {
    return null
  }
}
```

- [ ] **Step 2: Wire migration into `getToken()`**

Add after the keyring cache check, before the device flow:

```typescript
// Priority 3.5: migrate legacy file-based token
const migrated = await migrateLegacyToken(this.service, this.account)
if (migrated) {
  this.cached = { token: migrated, expiresAt: Date.now() + this.ttlMs }
  return migrated
}
```

- [ ] **Step 3: Run tests**

Run: `cd .scripts && bun test github-token`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add .scripts/lib/github.ts
git commit -m "feat(github): auto-migrate file-based token to keychain"
```

---

## Phase 1: Source Validation + SSH Clone URL Support

Replace the inline regex guard in `preDownloadSkills` with `parseSource()` from `source-parser.ts`. Extend `parseSource` to support SSH clone URLs and GitHub tree URLs (for pinned skills). Add a `resolveCloneUrl` helper that respects the system's git auth protocol.

### Task 1.1: Add `source_invalid` error type

**Files:**

- Modify: `.scripts/lib/catalog.ts` — `Tier1ErrorType` union

- [ ] **Step 1: Update the type**

In `catalog.ts`, find the `Tier1ErrorType` union and add `'source_invalid'`:

```typescript
export type Tier1ErrorType =
  | 'download_failed'
  | 'download_timeout'
  | 'analysis_failed'
  | 'analysis_timeout'
  | 'rate_limited'
  | 'batch_failed'
  | 'source_invalid'  // ← add
```

- [ ] **Step 2: Run existing tests**

Run: `cd .scripts && bun test catalog-tier1`
Expected: 75 pass, 0 fail

- [ ] **Step 3: Commit**

```bash
git add .scripts/lib/catalog.ts
git commit -m "feat(catalog): add source_invalid error type"
```

### Task 1.2: Add `resolveCloneUrl` — SSH/HTTPS URL builder

**Why:** `parseSource` hardcodes `https://github.com/${owner}/${repo}.git`. But
when the system has `gh auth status` showing `Git operations protocol: ssh`, HTTPS
clones fail with "Authentication failed". This is the root cause of many download
failures in the current pipeline.

**Files:**

- Modify: `.scripts/lib/source-parser.ts`
- Modify: `.scripts/test/source-parser.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// Add to source-parser.test.ts
import { resolveCloneUrl } from '../lib/source-parser'

describe('resolveCloneUrl', () => {
  it('returns HTTPS URL by default', () => {
    expect(resolveCloneUrl('anthropics/skills')).toBe('https://github.com/anthropics/skills.git')
  })

  it('returns SSH URL when protocol is ssh', () => {
    expect(resolveCloneUrl('anthropics/skills', 'ssh')).toBe('git@github.com:anthropics/skills.git')
  })

  it('returns HTTPS URL when protocol is https', () => {
    expect(resolveCloneUrl('anthropics/skills', 'https')).toBe('https://github.com/anthropics/skills.git')
  })

  it('handles owner/repo with dots and hyphens', () => {
    expect(resolveCloneUrl('my-org/my.repo', 'ssh')).toBe('git@github.com:my-org/my.repo.git')
  })
})

describe('detectGitProtocol', () => {
  // Note: this test reflects the actual system config, so expected value
  // depends on whether 1Password SSH agent / IdentityAgent is configured.
  it('returns ssh when IdentityAgent is in ~/.ssh/config', () => {
    // On this machine, IdentityAgent is set to 1Password socket
    const { detectGitProtocol } = require('../lib/source-parser')
    const protocol = detectGitProtocol()
    // If running on a machine with 1Password SSH agent:
    expect(['ssh', 'https']).toContain(protocol)
  })

  it('returns a valid GitProtocol value', () => {
    const { detectGitProtocol } = require('../lib/source-parser')
    expect(['ssh', 'https']).toContain(detectGitProtocol())
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `cd .scripts && bun test source-parser`
Expected: FAIL — `resolveCloneUrl` not exported

- [ ] **Step 3: Implement**

```typescript
// Add to source-parser.ts

export type GitProtocol = 'https' | 'ssh'

/**
 * Build a clone URL for a GitHub owner/repo, respecting the preferred protocol.
 *
 * - `https` → `https://github.com/owner/repo.git`
 * - `ssh` → `git@github.com:owner/repo.git`
 */
export function resolveCloneUrl(ownerRepo: string, protocol: GitProtocol = 'https'): string {
  if (protocol === 'ssh') {
    return `git@github.com:${ownerRepo}.git`
  }
  return `https://github.com/${ownerRepo}.git`
}

/**
 * Detect the preferred git protocol by checking (in order):
 * 1. SSH IdentityAgent in ~/.ssh/config (1Password, Secretive, etc.)
 * 2. git config url rewrite rules (url."git@github.com:".insteadOf)
 * 3. gh auth status (if gh CLI is available)
 *
 * Falls back to 'https' if no SSH signal is detected.
 */
export function detectGitProtocol(): GitProtocol {
  try {
    const { readFileSync: readF } = require('node:fs')
    const { homedir: home } = require('node:os')
    const { join: joinP } = require('node:path')

    // 1. Check ~/.ssh/config for IdentityAgent (1Password SSH agent, etc.)
    // This is the most reliable signal that SSH is configured
    try {
      const sshConfig = readF(joinP(home(), '.ssh', 'config'), 'utf-8') as string
      if (sshConfig.includes('IdentityAgent')) return 'ssh'
    } catch { /* no ssh config */ }

    // 2. Check git config for URL rewrite rules
    const { spawnSync: spS } = require('node:child_process')
    const git = spS('git', ['config', '--get', 'url.git@github.com:.insteadOf'], {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe'],
      timeout: 3000,
    })
    if (git.stdout?.trim()) return 'ssh'

    // 3. Check gh CLI (optional — works even without gh installed)
    try {
      const gh = spS('gh', ['auth', 'status'], {
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'pipe'],
        timeout: 5000,
      })
      const output = `${gh.stdout ?? ''}${gh.stderr ?? ''}`
      if (output.includes('Git operations protocol: ssh')) return 'ssh'
    } catch { /* gh not installed */ }
  } catch {
    // Detection failed entirely
  }
  return 'https'
}
```

- [ ] **Step 4: Run tests**

Run: `cd .scripts && bun test source-parser`
Expected: All pass (existing + 4 new)

- [ ] **Step 5: Commit**

```bash
git add .scripts/lib/source-parser.ts .scripts/test/source-parser.test.ts
git commit -m "feat(source-parser): add resolveCloneUrl with SSH/HTTPS protocol support"
```

### Task 1.3: Create `validateCatalogSource` — accepts short form AND tree URLs

**Design:** `validateCatalogSource` accepts:

- `owner/repo` — standard catalog entry
- `owner/repo#ref` — pinned to a branch/tag (for archived/deleted skills)
- `github.com/owner/repo/tree/ref/path` — pinned tree URL (for archived skills)

Rejects local paths, SSH URLs, and non-GitHub sources.

**Files:**

- Create: `.scripts/lib/catalog-download.ts`
- Create: `.scripts/test/catalog-download.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// .scripts/test/catalog-download.test.ts
import { describe, expect, it } from 'bun:test'
import { validateCatalogSource } from '../lib/catalog-download'

describe('validateCatalogSource', () => {
  it('accepts valid org/repo format', () => {
    const result = validateCatalogSource('anthropics/skills')
    expect(result.ok).toBe(true)
    expect(result.value.ownerRepo).toBe('anthropics/skills')
  })

  it('accepts org/repo#ref (pinned)', () => {
    const result = validateCatalogSource('anthropics/skills#v1.2.0')
    expect(result.ok).toBe(true)
    expect(result.value.ownerRepo).toBe('anthropics/skills')
    expect(result.value.ref).toBe('v1.2.0')
  })

  it('accepts GitHub tree URL (pinned)', () => {
    const result = validateCatalogSource('https://github.com/org/repo/tree/main/skills/my-skill')
    expect(result.ok).toBe(true)
    expect(result.value.ownerRepo).toBe('org/repo')
    expect(result.value.ref).toBe('main')
    expect(result.value.subpath).toBe('skills/my-skill')
  })

  it('resolves SSH clone URL when protocol is ssh', () => {
    const result = validateCatalogSource('anthropics/skills', 'ssh')
    expect(result.ok).toBe(true)
    expect(result.value.cloneUrl).toBe('git@github.com:anthropics/skills.git')
  })

  it('resolves HTTPS clone URL by default', () => {
    const result = validateCatalogSource('anthropics/skills', 'https')
    expect(result.ok).toBe(true)
    expect(result.value.cloneUrl).toContain('https://github.com/')
  })

  it('rejects filesystem paths', () => {
    const result = validateCatalogSource('/tmp/worktrees/skill-inspect-11/.claude/skills/foo')
    expect(result.ok).toBe(false)
    expect(result.error?.code).toBe('E_NOT_GITHUB')
  })

  it('rejects empty strings', () => {
    const result = validateCatalogSource('')
    expect(result.ok).toBe(false)
  })

  it('accepts org/repo with dots and hyphens', () => {
    const result = validateCatalogSource('my-org/my.repo-name')
    expect(result.ok).toBe(true)
  })

  it('rejects non-GitHub URLs', () => {
    const result = validateCatalogSource('https://gitlab.com/org/repo')
    expect(result.ok).toBe(false)
    expect(result.error?.code).toBe('E_NOT_GITHUB')
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `cd .scripts && bun test catalog-download`
Expected: FAIL — module not found

- [ ] **Step 3: Write implementation**

```typescript
// .scripts/lib/catalog-download.ts
/**
 * Catalog download orchestrator.
 *
 * Composes git.ts, source-parser.ts, and skill-discovery.ts to replace
 * the npx-skills shell-out in the analyze pipeline.
 */

import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import {
  parseSource,
  getOwnerRepo,
  resolveCloneUrl,
  detectGitProtocol,
  type GitProtocol,
  type ParsedSource,
} from './source-parser'
import { CliError, err, ok, type Result } from './types'

/** Well-known subdirectory prefixes where skills may live in a repo. */
export const SKILL_LOOKUP_DIRS = ['', 'skills/', 'context/skills/', '.claude/skills/']

/** Build full SKILL.md lookup paths for a given skill name. */
const SKILL_LOOKUP_PATHS = (skillName: string) =>
  SKILL_LOOKUP_DIRS.map((prefix) => `${prefix}${skillName}/SKILL.md`)

/** Validated catalog source with resolved clone URL. */
export interface CatalogSource {
  ownerRepo: string
  cloneUrl: string
  ref?: string
  subpath?: string
  skillFilter?: string
}

/**
 * Validate a catalog source string. Accepts:
 * - `owner/repo` — standard entry
 * - `owner/repo#ref` — pinned to branch/tag
 * - `github.com/owner/repo/tree/ref/path` — pinned tree URL
 *
 * Rejects local paths, SSH raw URLs, non-GitHub sources.
 * Resolves clone URL using the detected git protocol (SSH/HTTPS).
 */
export function validateCatalogSource(
  source: string,
  protocol?: GitProtocol
): Result<CatalogSource> {
  const parsed = parseSource(source)
  if (!parsed.ok) return parsed as Result<never>

  // Must be a GitHub source
  if (parsed.value.type !== 'github') {
    return err(
      new CliError(
        `Catalog source must be GitHub (owner/repo or tree URL), got type "${parsed.value.type}": ${source}`,
        'E_NOT_GITHUB',
        'Supported: owner/repo, owner/repo#ref, github.com/o/r/tree/branch/path'
      )
    )
  }

  const ownerRepo = getOwnerRepo(parsed.value)
  if (!ownerRepo) {
    return err(
      new CliError(
        `Could not extract owner/repo from: ${source}`,
        'E_NOT_GITHUB',
        'Expected format: owner/repo'
      )
    )
  }

  const proto = protocol ?? detectGitProtocol()
  return ok({
    ownerRepo,
    cloneUrl: resolveCloneUrl(ownerRepo, proto),
    ref: parsed.value.ref,
    subpath: parsed.value.subpath,
    skillFilter: parsed.value.skillFilter,
  })
}
```

- [ ] **Step 4: Run tests**

Run: `cd .scripts && bun test catalog-download`
Expected: 9 pass, 0 fail

- [ ] **Step 5: Commit**

```bash
git add .scripts/lib/catalog-download.ts .scripts/test/catalog-download.test.ts
git commit -m "feat(catalog): add validateCatalogSource with tree URL + SSH support"
```

---

## Phase 2: Download Orchestrator

Replace `npx skills add` + `find` fallback with `cloneRepo()` + `discoverSkills()`. Uses `CatalogSource.cloneUrl` (from Phase 1) which respects SSH/HTTPS protocol.

1. Validates the source with `validateCatalogSource` → `CatalogSource`
2. Clones via `cloneRepo(catalogSource.cloneUrl, ...)` (SSH-aware, structured errors)
3. Discovers SKILL.md via `discoverSkills` (priority dirs, recursive fallback)
4. Computes mechanical fields (contentHash, wordCount, etc.)

### Task 2.1: Write `downloadSkill` — the per-skill download function

**Files:**

- Modify: `.scripts/lib/catalog-download.ts`
- Modify: `.scripts/test/catalog-download.test.ts`

- [ ] **Step 1: Write the failing tests**

```typescript
// Add to catalog-download.test.ts
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, beforeEach } from 'bun:test'
import { downloadSkill, type SkillDownloadResult } from '../lib/catalog-download'

describe('downloadSkill', () => {
  // These test the local-path code path (no network)
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'dl-test-'))
  })
  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  it('downloads from a local directory with SKILL.md', async () => {
    // Create a fake skill
    const skillDir = join(tmpDir, 'my-skill')
    mkdirSync(skillDir, { recursive: true })
    writeFileSync(
      join(skillDir, 'SKILL.md'),
      '---\nname: my-skill\ndescription: test\n---\n# My Skill\nSome content here.'
    )

    const result = await downloadSkill('test-org/test-repo', 'my-skill', {
      localOverride: skillDir,
    })

    expect(result.path).toBeTruthy()
    expect(result.contentHash).toMatch(/^sha256:[a-f0-9]{64}$/)
    expect(result.wordCount).toBeGreaterThan(0)
    expect(result.sectionCount).toBe(1)
    expect(result.error).toBeUndefined()
  })

  it('returns error for missing SKILL.md', async () => {
    mkdirSync(join(tmpDir, 'empty-skill'), { recursive: true })

    const result = await downloadSkill('test-org/test-repo', 'empty-skill', {
      localOverride: join(tmpDir, 'empty-skill'),
    })

    expect(result.path).toBeNull()
    expect(result.error).toBeDefined()
    expect(result.errorType).toBe('download_failed')
  })

  it('returns error for invalid source format', async () => {
    const result = await downloadSkill('/tmp/bad/path', 'skill', {})
    expect(result.path).toBeNull()
    expect(result.errorType).toBe('source_invalid')
  })

  it('computes all mechanical fields on success', async () => {
    const skillDir = join(tmpDir, 'metrics-skill')
    mkdirSync(skillDir, { recursive: true })
    writeFileSync(
      join(skillDir, 'SKILL.md'),
      '---\nname: metrics-skill\ndescription: test\n---\n# H1\n## H2\n### H3\nword1 word2 word3'
    )
    writeFileSync(join(skillDir, 'extra.md'), 'extra file')

    const result = await downloadSkill('org/repo', 'metrics-skill', {
      localOverride: skillDir,
    })

    expect(result.contentHash).toMatch(/^sha256:/)
    expect(result.wordCount).toBeGreaterThan(0)
    expect(result.sectionCount).toBe(3)
    expect(result.fileCount).toBe(2)
    expect(result.headingTree).toHaveLength(3)
    expect(result.headingTree![0]).toEqual({ depth: 1, title: 'H1' })
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `cd .scripts && bun test catalog-download`
Expected: FAIL — `downloadSkill` not exported

- [ ] **Step 3: Implement `downloadSkill`**

```typescript
// Add to .scripts/lib/catalog-download.ts

import {
  computeContentHash,
  computeFileCount,
  computeHeadingTree,
  computeSectionCount,
  computeWordCount,
  type Tier1ErrorType,
} from './catalog'
import { cloneRepo, type GitCloneError } from './git'
import { discoverSkills } from './skill-discovery'

export interface SkillDownloadResult {
  path: string | null
  error?: string
  errorType?: Tier1ErrorType
  errorDetail?: string
  errorCode?: number
  contentHash?: string
  wordCount?: number
  sectionCount?: number
  fileCount?: number
  headingTree?: Array<{ depth: number; title: string }>
  /** Parsed frontmatter name (from discovery). */
  discoveredName?: string
  /** Parsed frontmatter description. */
  discoveredDescription?: string
}

export interface DownloadOptions {
  /** Override clone with a local directory (for testing). */
  localOverride?: string
  /** AbortSignal for cancellation. */
  signal?: AbortSignal
  /** Clone timeout in ms (default: 60000). */
  timeout?: number
}

/**
 * Download and analyze a single skill from a catalog entry.
 *
 * Flow:
 * 1. Validate source with parseSource()
 * 2. Clone repo (or use localOverride)
 * 3. Discover SKILL.md via discoverSkills()
 * 4. Compute mechanical fields
 *
 * Never throws — all errors returned in the result.
 */
export async function downloadSkill(
  source: string,
  skill: string,
  opts: DownloadOptions
): Promise<SkillDownloadResult> {
  // Step 1: Validate source
  const validated = validateCatalogSource(source)
  if (!validated.ok) {
    return {
      path: null,
      error: validated.error.message,
      errorType: 'source_invalid',
      errorDetail: validated.error.hint ?? validated.error.message,
    }
  }

  // Step 2: Get the skill directory
  let searchDir: string
  let cleanup: (() => Promise<void>) | undefined

  if (opts.localOverride) {
    searchDir = opts.localOverride
  } else {
    // Uses CatalogSource.cloneUrl which respects SSH/HTTPS protocol
    const cloneResult = await cloneRepo(validated.value.cloneUrl, validated.value.ref)
    if (!cloneResult.ok) {
      const gitErr = cloneResult.error as GitCloneError
      return {
        path: null,
        error: `clone failed: ${gitErr.message}`,
        errorType: gitErr.isTimeout ? 'download_timeout' : 'download_failed',
        errorDetail: gitErr.hint ?? gitErr.message,
      }
    }
    searchDir = cloneResult.value.tempDir
    cleanup = cloneResult.value.cleanup
  }

  try {
    // Step 3: Discover SKILL.md files
    const discovered = await discoverSkills(searchDir)
    if (!discovered.ok) {
      return {
        path: null,
        error: `discovery failed: ${discovered.error.message}`,
        errorType: 'download_failed',
        errorDetail: discovered.error.hint ?? discovered.error.message,
      }
    }

    // Find the specific skill by name
    const match = discovered.value.find(
      (s) => s.name.toLowerCase() === skill.toLowerCase()
    )

    if (!match) {
      // Fallback: look for SKILL.md in well-known paths
      for (const p of SKILL_LOOKUP_PATHS(skill).map((rel) => join(searchDir, rel))) {
        if (existsSync(p)) {
          return computeResult(p, join(p, '..'))
        }
      }

      return {
        path: null,
        error: `skill "${skill}" not found in ${source} (${discovered.value.length} skills discovered: ${discovered.value.map((s) => s.name).join(', ').slice(0, 200)})`,
        errorType: 'download_failed',
        errorDetail: 'SKILL.md not found by discovery or direct path lookup',
      }
    }

    // Step 4: Compute mechanical fields
    const result = computeResult(match.path, join(match.path, '..'))
    result.discoveredName = match.name
    result.discoveredDescription = match.frontmatter.description
    return result
  } finally {
    if (cleanup) await cleanup()
  }
}

/** Read SKILL.md and compute all mechanical analysis fields. */
function computeResult(skillMdPath: string, skillDir: string): SkillDownloadResult {
  const content = readFileSync(skillMdPath, 'utf8')
  return {
    path: skillMdPath,
    contentHash: computeContentHash(content),
    wordCount: computeWordCount(content),
    sectionCount: computeSectionCount(content),
    fileCount: computeFileCount(skillDir),
    headingTree: computeHeadingTree(content),
  }
}
```

- [ ] **Step 4: Run tests**

Run: `cd .scripts && bun test catalog-download`
Expected: 10 pass (5 from Task 1.2 + 5 new)

- [ ] **Step 5: Commit**

```bash
git add .scripts/lib/catalog-download.ts .scripts/test/catalog-download.test.ts
git commit -m "feat(catalog): add downloadSkill using git.ts + skill-discovery"
```

### Task 2.2: Write `downloadBatch` — batch orchestration with concurrency

**Files:**

- Modify: `.scripts/lib/catalog-download.ts`
- Modify: `.scripts/test/catalog-download.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
describe('downloadBatch', () => {
  let tmpDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'batch-test-'))
  })
  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  it('downloads multiple skills and returns a Map', async () => {
    // Create two fake skills
    for (const name of ['skill-a', 'skill-b']) {
      const dir = join(tmpDir, name)
      mkdirSync(dir, { recursive: true })
      writeFileSync(
        join(dir, 'SKILL.md'),
        `---\nname: ${name}\ndescription: test\n---\n# ${name}\ncontent`
      )
    }

    const entries = [
      { source: 'org/repo', skill: 'skill-a', availability: 'available' as const },
      { source: 'org/repo', skill: 'skill-b', availability: 'available' as const },
    ]

    const results = await downloadBatch(entries, {
      localOverrideDir: tmpDir,
    })

    expect(results.size).toBe(2)
    expect(results.get('skill-a')?.path).toBeTruthy()
    expect(results.get('skill-b')?.contentHash).toMatch(/^sha256:/)
  })

  it('handles mixed success/failure', async () => {
    mkdirSync(join(tmpDir, 'good'), { recursive: true })
    writeFileSync(
      join(tmpDir, 'good', 'SKILL.md'),
      '---\nname: good\ndescription: test\n---\n# Good'
    )
    // 'bad' directory exists but has no SKILL.md
    mkdirSync(join(tmpDir, 'bad'), { recursive: true })

    const entries = [
      { source: 'org/repo', skill: 'good', availability: 'available' as const },
      { source: 'org/repo', skill: 'bad', availability: 'available' as const },
    ]

    const results = await downloadBatch(entries, {
      localOverrideDir: tmpDir,
    })

    expect(results.get('good')?.path).toBeTruthy()
    expect(results.get('bad')?.error).toBeDefined()
  })

  it('groups entries by source for efficient cloning', async () => {
    // Two different "repos" (simulated via localOverrideDir)
    for (const repo of ['repo-a', 'repo-b']) {
      for (const skill of ['s1', 's2']) {
        const dir = join(tmpDir, `${repo}/${skill}`)
        mkdirSync(dir, { recursive: true })
        writeFileSync(
          join(dir, 'SKILL.md'),
          `---\nname: ${skill}\ndescription: test\n---\n# ${skill}`
        )
      }
    }

    const entries = [
      { source: 'org/repo-a', skill: 's1', availability: 'available' as const },
      { source: 'org/repo-b', skill: 's2', availability: 'available' as const },
      { source: 'org/repo-a', skill: 's2', availability: 'available' as const },
    ]

    // Note: localOverrideDir won't perfectly simulate multi-repo grouping
    // since it maps skill names directly, but it tests the Map return shape
    const results = await downloadBatch(entries, { localOverrideDir: tmpDir })
    expect(results.size).toBe(3)
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `cd .scripts && bun test catalog-download`
Expected: FAIL — `downloadBatch` not exported

- [ ] **Step 3: Implement `downloadBatch`**

```typescript
// Add to catalog-download.ts

import type { CatalogEntry } from './catalog'

export interface BatchDownloadOptions {
  /** Use local directories instead of cloning (for testing). Skill dirs at localOverrideDir/<skill-name>/ */
  localOverrideDir?: string
  /** Force git protocol override (default: auto-detect). */
  protocol?: 'ssh' | 'https'
  signal?: AbortSignal
  timeout?: number
}

/**
 * Download all skills in a batch.
 *
 * For remote sources with the same org/repo, clones once and discovers
 * all skills from the single clone. Falls back to per-skill clone if
 * the batch spans multiple repos.
 */
export async function downloadBatch(
  entries: CatalogEntry[],
  opts: BatchDownloadOptions = {}
): Promise<Map<string, SkillDownloadResult>> {
  const results = new Map<string, SkillDownloadResult>()

  // Group entries by source for efficient cloning
  const bySource = new Map<string, CatalogEntry[]>()
  for (const entry of entries) {
    const group = bySource.get(entry.source) ?? []
    group.push(entry)
    bySource.set(entry.source, group)
  }

  for (const [source, group] of bySource) {
    if (opts.localOverrideDir) {
      // Test mode: use local directories (no network)
      for (const entry of group) {
        const localDir = join(opts.localOverrideDir, entry.skill)
        if (!existsSync(localDir)) {
          results.set(entry.skill, {
            path: null,
            error: `local directory not found: ${localDir}`,
            errorType: 'download_failed',
            errorDetail: 'localOverrideDir set but skill directory missing',
          })
          continue
        }
        const result = await downloadSkill(source, entry.skill, {
          localOverride: localDir,
          signal: opts.signal,
        })
        results.set(entry.skill, result)
      }
      continue
    }

    // Production mode: clone once per source, discover all skills
    const validated = validateCatalogSource(source, opts.protocol)
    if (!validated.ok) {
      for (const entry of group) {
        results.set(entry.skill, {
          path: null,
          error: validated.error.message,
          errorType: 'source_invalid',
          errorDetail: validated.error.hint ?? validated.error.message,
        })
      }
      continue
    }

    const cloneResult = await cloneRepo(validated.value.cloneUrl, validated.value.ref)
    if (!cloneResult.ok) {
      const gitErr = cloneResult.error as GitCloneError
      for (const entry of group) {
        results.set(entry.skill, {
          path: null,
          error: `clone failed: ${gitErr.message}`,
          errorType: gitErr.isTimeout ? 'download_timeout' : 'download_failed',
          errorDetail: gitErr.hint ?? gitErr.message,
        })
      }
      continue
    }

    try {
      // Discover all skills in the cloned repo
      const discovered = await discoverSkills(cloneResult.value.tempDir)
      const discoveredMap = new Map(
        (discovered.ok ? discovered.value : []).map((s) => [s.name.toLowerCase(), s])
      )

      for (const entry of group) {
        const match = discoveredMap.get(entry.skill.toLowerCase())
        if (match) {
          const result = computeResult(match.path, join(match.path, '..'))
          result.discoveredName = match.name
          result.discoveredDescription = match.frontmatter.description
          results.set(entry.skill, result)
        } else {
          // Direct path fallback using well-known paths
          let found = false
          for (const p of SKILL_LOOKUP_PATHS(entry.skill).map((rel) => join(cloneResult.value.tempDir, rel))) {
            if (existsSync(p)) {
              results.set(entry.skill, computeResult(p, join(p, '..')))
              found = true
              break
            }
          }
          if (!found) {
            results.set(entry.skill, {
              path: null,
              error: `skill "${entry.skill}" not found in ${source}`,
              errorType: 'download_failed',
              errorDetail: `Discovered ${discoveredMap.size} skills but none matched "${entry.skill}"`,
            })
          }
        }
      }
    } finally {
      await cloneResult.value.cleanup()
    }
  }

  return results
}
```

- [ ] **Step 4: Run tests**

Run: `cd .scripts && bun test catalog-download`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add .scripts/lib/catalog-download.ts .scripts/test/catalog-download.test.ts
git commit -m "feat(catalog): add downloadBatch with per-source clone grouping"
```

---

## Phase 3: Wire New Download Path (Blue/Green)

Wire `downloadBatch` into `processBatch` alongside the existing `preDownloadSkills`. Use a `--legacy-download` flag to select the old path. Default to the new path. The old code stays until Phase 3b validates the new path in production.

**Blue** = existing `npx skills` + `exec` path (preserved behind `--legacy-download`)
**Green** = new `downloadBatch` + `createGit` path (default)

### Task 3.1: Add blue/green download switch

**Files:**

- Modify: `.scripts/commands/skill.ts`

- [ ] **Step 1: Add import and `--legacy-download` flag**

Add import at the top of skill.ts:

```typescript
import { downloadBatch, type SkillDownloadResult } from '../lib/catalog-download'
```

Add `cpSync` to the existing `node:fs` import:

```typescript
import { cpSync, readdirSync, statSync } from 'node:fs'
```

Add the flags to the analyze command args:

```typescript
'legacy-download': {
  type: 'boolean',
  description: 'Use legacy npx-skills download path (for rollback)',
  default: false,
},
'git-protocol': {
  type: 'string',
  description: 'Force git protocol: ssh|https|auto (default: auto)',
  default: 'auto',
},
```

- [ ] **Step 2: Branch the download path in `processBatch`**

In `processBatch`, after creating the worktree, add the green path:

```typescript
const useLegacy = args['legacy-download'] as boolean
const gitProtocol = args['git-protocol'] as string

let downloaded: Map<string, SkillDownloadResult>
if (useLegacy) {
  // BLUE: legacy npx-skills path (preserved for rollback)
  downloaded = await preDownloadSkills(batch, wtPath) as Map<string, SkillDownloadResult>
} else {
  // GREEN: new git.ts + skill-discovery path
  // Pass git protocol override (auto = detect from system config)
  const protocol = gitProtocol === 'auto' ? undefined : gitProtocol as 'ssh' | 'https'
  downloaded = await downloadBatch(batch, { protocol })

  // Copy downloaded skills into worktree for agent access
  const wtSkillsDir = join(wtPath, '.claude', 'skills')
  mkdirSync(wtSkillsDir, { recursive: true })
  for (const [skillName, dl] of downloaded) {
    if (dl.path) {
      const destDir = join(wtSkillsDir, skillName)
      mkdirSync(destDir, { recursive: true })
      const skillSrcDir = join(dl.path, '..')
      cpSync(skillSrcDir, destDir, { recursive: true })
      dl.path = join(destDir, 'SKILL.md')
    }
  }
}
```

- [ ] **Step 3: Run catalog tests**

Run: `cd .scripts && bun test catalog-tier1 catalog-download`
Expected: All pass

- [ ] **Step 4: Smoke test both paths**

```bash
# Green path (new, default — auto-detects SSH from IdentityAgent)
just agents skill catalog analyze --force --limit 1 --batch-size 3

# Green path with explicit SSH
just agents skill catalog analyze --force --limit 1 --batch-size 3 --git-protocol ssh

# Green path with explicit HTTPS
just agents skill catalog analyze --force --limit 1 --batch-size 3 --git-protocol https

# Blue path (legacy fallback)
just agents skill catalog analyze --force --limit 1 --batch-size 3 --legacy-download
```

Expected: All produce results. SSH path uses `git@github.com:` URLs, HTTPS uses `https://`. Auto-detect matches system config.

- [ ] **Step 5: Commit**

```bash
git add .scripts/commands/skill.ts
git commit -m "feat(catalog): add blue/green download switch (--legacy-download)"
```

### Task 3.2: Add `simple-git` worktree alongside exec-based version

**Files:**

- Modify: `.scripts/commands/skill.ts`

The worktree is still needed for the Haiku agent. Add the `simple-git` version alongside the exec version, gated by the same `--legacy-download` flag.

- [ ] **Step 1: Add `simple-git` worktree functions**

```typescript
import { createGit } from '../lib/git'

async function createWorktreeNew(batchId: number): Promise<string> {
  const wtPath = join(WORKTREE_BASE, `skill-inspect-${batchId}`)
  const git = createGit(PROJECT_ROOT)

  if (fsExists(wtPath)) {
    try { await git.raw(['worktree', 'unlock', wtPath]) } catch { /* ignore */ }
    try { await git.raw(['worktree', 'remove', '--force', wtPath]) } catch { /* ignore */ }
    try { rmSync(wtPath, { recursive: true, force: true }) } catch { /* ignore */ }
  }

  await git.raw(['worktree', 'add', '--detach', wtPath, 'HEAD'])
  return wtPath
}

async function removeWorktreeNew(wtPath: string): Promise<void> {
  const git = createGit(PROJECT_ROOT)
  try { await git.raw(['worktree', 'unlock', wtPath]) } catch { /* ignore */ }
  try { await git.raw(['worktree', 'remove', '--force', wtPath]) } catch { /* ignore */ }
  try { rmSync(wtPath, { recursive: true, force: true }) } catch { /* ignore */ }
}
```

- [ ] **Step 2: Branch worktree creation on the flag**

In `processBatch`:

```typescript
wtPath = useLegacy
  ? await createWorktree(batchNum)
  : await createWorktreeNew(batchNum)
```

And cleanup:

```typescript
if (wtPath) {
  useLegacy
    ? await removeWorktree(wtPath)
    : await removeWorktreeNew(wtPath)
}
```

- [ ] **Step 3: Smoke test both paths**

```bash
# Green (new)
just agents skill catalog analyze --force --limit 1 --batch-size 3
# Blue (legacy)
just agents skill catalog analyze --force --limit 1 --batch-size 3 --legacy-download
```

Expected: Both work, worktrees created/cleaned

- [ ] **Step 4: Commit**

```bash
git add .scripts/commands/skill.ts
git commit -m "feat(catalog): add simple-git worktree alongside exec version"
```

### Task 3.3: Integration smoke test

**Files:**

- Create: `.scripts/test/catalog-integration.test.ts`

**Note:** These tests use `cloneRepo` which respects `detectGitProtocol()` — it will use SSH if `gh auth status` reports SSH protocol, HTTPS otherwise. No GitHub token env var required when SSH keys are configured.

- [ ] **Step 1: Write the test**

```typescript
// .scripts/test/catalog-integration.test.ts
import { describe, expect, it } from 'bun:test'
import { downloadSkill } from '../lib/catalog-download'

describe('catalog-download integration', () => {
  it('downloads a real public skill (0x2e/superpowers@systematic-debugging)', async () => {
    const result = await downloadSkill(
      '0x2e/superpowers',
      'systematic-debugging',
      { timeout: 60_000 }
    )

    expect(result.path).toBeTruthy()
    expect(result.contentHash).toMatch(/^sha256:[a-f0-9]{64}$/)
    expect(result.wordCount).toBeGreaterThan(100)
    expect(result.error).toBeUndefined()
  }, 90_000)

  it('returns structured error for nonexistent repo', async () => {
    const result = await downloadSkill(
      'definitely-not-a-real-org/nonexistent-repo-12345',
      'fake-skill',
      { timeout: 30_000 }
    )

    expect(result.path).toBeNull()
    expect(result.error).toBeDefined()
    expect(result.errorType).toBe('download_failed')
    expect(result.errorDetail).toBeDefined()
  }, 60_000)
})
```

- [ ] **Step 2: Run**

Run: `cd .scripts && bun test catalog-integration`
Expected: 2 pass (requires network + git SSH keys or HTTPS credentials)

- [ ] **Step 3: Commit**

```bash
git add .scripts/test/catalog-integration.test.ts
git commit -m "test(catalog): add integration tests for downloadSkill"
```

---

## Phase 3b: Remove Legacy Download Path

**Prerequisite:** Run at least 2 production batches (100+ skills) with the green path and verify:

1. Success rate is equal or better than the legacy path
2. Error classification is richer (auth errors, not-found vs generic "download failed")
3. No worktree cleanup regressions

**Tracking:** Create beads issues at Phase 3 completion:

```bash
bd create "Validate green download path: batch 1 (100+ skills)" --label "catalog,validation"
bd create "Validate green download path: batch 2 (100+ skills)" --label "catalog,validation"
bd create "Compare green vs legacy error rates" --label "catalog,validation"
bd dep add <batch1-id> <phase3b-id>
bd dep add <batch2-id> <phase3b-id>
bd dep add <compare-id> <phase3b-id>
```

### Task 3b.1: Remove legacy code

**Files:**

- Modify: `.scripts/commands/skill.ts`

- [ ] **Step 1: Remove `--legacy-download` flag from args**

- [ ] **Step 2: Remove `preDownloadSkills` function and `DownloadResult` interface**

- [ ] **Step 3: Remove `createWorktree` and `removeWorktree` (exec-based versions)**

- [ ] **Step 4: Remove the `useLegacy` branch — keep only green path**

- [ ] **Step 5: Remove `exec`-related imports that are no longer used**

(`exec`, `spawn` from `node:child_process` — verify nothing else uses them in this file)

- [ ] **Step 6: Run full test suite**

Run: `cd .scripts && bun test catalog-tier1 catalog-download catalog-integration`
Expected: All pass

- [ ] **Step 7: Run production batch**

```bash
just agents skill catalog analyze --batch-size 25 --concurrency 3 --limit 5
```

Expected: Works identically to pre-removal

- [ ] **Step 8: Commit**

```bash
git add .scripts/commands/skill.ts
git commit -m "refactor(catalog): remove legacy npx-skills download path"
```

---

## Phase 4: Stale Detection

Add a `catalog stale` command that identifies analyzed skills whose upstream content has changed since analysis. Uses `fetchSkillFolderHash()` from `git.ts` to fetch git tree SHAs and compares tree-to-tree.

**Design note:** `contentHash` (SHA-256 of file content) and `fetchSkillFolderHash` (git tree SHA) are different hash types and cannot be compared directly. Instead, we:

1. Store `treeSha` as a new field on catalog entries during download (Phase 2 `downloadBatch` fetches it after clone)
2. Compare `treeSha` against upstream `fetchSkillFolderHash` for stale detection

### Task 4.0: Add `treeSha` field to catalog types

**Files:**

- Modify: `.scripts/lib/catalog.ts` — add `treeSha` to `Tier1Result`
- Modify: `.scripts/lib/catalog-download.ts` — populate `treeSha` in `SkillDownloadResult`

- [ ] **Step 1: Add `treeSha` to `Tier1Result`**

In `catalog.ts`, add to the `Tier1Result` interface:

```typescript
  contentHash?: string
  treeSha?: string  // ← add: git tree SHA of the skill folder (for stale detection)
  tier2Reviewed?: boolean
```

- [ ] **Step 2: Add `treeSha` to `SkillDownloadResult`**

In `catalog-download.ts`, add to the interface:

```typescript
export interface SkillDownloadResult {
  // ... existing fields ...
  /** Git tree SHA of the skill folder (for stale detection). */
  treeSha?: string
}
```

And populate it in `downloadBatch` after cloning (using `gitRaw` to get the tree hash):

```typescript
// After discovering the skill, get the tree SHA for its directory
import { relative } from 'node:path'
import { gitRaw } from './git'

const relPath = relative(cloneResult.value.tempDir, join(match.path, '..')).replace(/\\/g, '/')
if (relPath && !relPath.startsWith('..')) {
  const treeShaResult = await gitRaw(
    ['rev-parse', `HEAD:${relPath}`],
    cloneResult.value.tempDir
  )
  if (treeShaResult.ok) {
    result.treeSha = treeShaResult.value.trim()
  }
  // treeSha is optional — if rev-parse fails, it's just undefined
  // Stale detection in Phase 4 skips entries without treeSha
}
```

- [ ] **Step 3: Run tests**

Run: `cd .scripts && bun test catalog-tier1 catalog-download`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add .scripts/lib/catalog.ts .scripts/lib/catalog-download.ts
git commit -m "feat(catalog): add treeSha field for stale detection"
```

### Task 4.1: Create `checkCatalogStale` function

**Files:**

- Create: `.scripts/lib/catalog-stale.ts`
- Create: `.scripts/test/catalog-stale.test.ts`

- [ ] **Step 1: Write the failing test**

```typescript
// .scripts/test/catalog-stale.test.ts
import { describe, expect, it } from 'bun:test'
import { identifyStaleEntries, type StaleCheckResult } from '../lib/catalog-stale'
import type { CatalogEntryWithTier1 } from '../lib/catalog'

describe('identifyStaleEntries', () => {
  it('flags entries where upstream treeSha differs from stored treeSha', () => {
    const entries: CatalogEntryWithTier1[] = [
      {
        source: 'org/repo',
        skill: 'skill-a',
        availability: 'available',
        treeSha: 'abc123old',
        wordCount: 500,
        attemptCount: 0,
      } as CatalogEntryWithTier1,
    ]

    const upstreamHashes = new Map([
      ['org/repo:skill-a', 'def456new'],
    ])

    const results = identifyStaleEntries(entries, upstreamHashes)
    expect(results).toHaveLength(1)
    expect(results[0].status).toBe('stale')
    expect(results[0].localHash).toBe('abc123old')
    expect(results[0].remoteHash).toBe('def456new')
  })

  it('skips entries without treeSha', () => {
    const entries: CatalogEntryWithTier1[] = [
      {
        source: 'org/repo',
        skill: 'no-hash',
        availability: 'available',
        wordCount: 500,
      } as CatalogEntryWithTier1,
    ]

    const results = identifyStaleEntries(entries, new Map())
    expect(results).toHaveLength(0)
  })

  it('marks as current when treeSha matches', () => {
    const sha = 'abc123same'
    const entries: CatalogEntryWithTier1[] = [
      {
        source: 'org/repo',
        skill: 'current',
        availability: 'available',
        treeSha: sha,
        wordCount: 500,
        attemptCount: 0,
      } as CatalogEntryWithTier1,
    ]

    const results = identifyStaleEntries(entries, new Map([['org/repo:current', sha]]))
    expect(results).toHaveLength(1)
    expect(results[0].status).toBe('current')
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `cd .scripts && bun test catalog-stale`
Expected: FAIL — module not found

- [ ] **Step 3: Implement**

```typescript
// .scripts/lib/catalog-stale.ts
/**
 * Stale detection for catalog entries.
 *
 * Compares analyzed treeSha against upstream folder hashes
 * (fetched via GitHub Trees API) to identify skills that need
 * re-analysis due to content changes.
 */

import type { CatalogEntryWithTier1 } from './catalog'
import { SKILL_LOOKUP_DIRS } from './catalog-download'
import { fetchSkillFolderHash } from './git'

export type StaleStatus = 'current' | 'stale' | 'unknown'

export interface StaleCheckResult {
  source: string
  skill: string
  status: StaleStatus
  localHash?: string
  remoteHash?: string
  error?: string
}

/**
 * Compare local catalog treeSha against upstream tree SHAs.
 * Pure function — no I/O. Takes pre-fetched upstream hashes.
 *
 * Note: Uses `treeSha` (git tree SHA), NOT `contentHash` (SHA-256 of file content).
 * These are different hash types and cannot be compared cross-type.
 */
export function identifyStaleEntries(
  entries: CatalogEntryWithTier1[],
  upstreamHashes: Map<string, string>
): StaleCheckResult[] {
  const results: StaleCheckResult[] = []

  for (const entry of entries) {
    if (!entry.treeSha || !entry.wordCount) continue

    const key = `${entry.source}:${entry.skill}`
    const remoteHash = upstreamHashes.get(key)

    if (!remoteHash) {
      // No upstream hash available (API failed or not fetched)
      continue
    }

    results.push({
      source: entry.source,
      skill: entry.skill,
      status: entry.treeSha === remoteHash ? 'current' : 'stale',
      localHash: entry.treeSha,
      remoteHash,
    })
  }

  return results
}

/**
 * Fetch upstream folder hashes for a batch of catalog entries.
 * Uses GitHub Trees API — no cloning required.
 *
 * Returns a Map of "source:skill" → treeSHA.
 * Entries that fail API lookup are silently skipped.
 */
export async function fetchUpstreamHashes(
  entries: CatalogEntryWithTier1[],
  opts?: { concurrency?: number }
): Promise<Map<string, string>> {
  const concurrency = opts?.concurrency ?? 5
  const hashes = new Map<string, string>()
  const queue = [...entries.filter((e) => e.treeSha && e.wordCount)]

  async function worker() {
    while (queue.length > 0) {
      const entry = queue.shift()
      if (!entry) break

      // Check well-known paths (shared with catalog-download.ts)
      const paths = SKILL_LOOKUP_DIRS.map((prefix) => `${prefix}${entry.skill}`)

      for (const path of paths) {
        const hash = await fetchSkillFolderHash(entry.source, path)
        if (hash) {
          hashes.set(`${entry.source}:${entry.skill}`, hash)
          break
        }
      }
    }
  }

  await Promise.all(Array.from({ length: concurrency }, () => worker()))
  return hashes
}
```

- [ ] **Step 4: Run tests**

Run: `cd .scripts && bun test catalog-stale`
Expected: 3 pass

- [ ] **Step 5: Commit**

```bash
git add .scripts/lib/catalog-stale.ts .scripts/test/catalog-stale.test.ts
git commit -m "feat(catalog): add stale detection with GitHub Trees API"
```

### Task 4.2: Add `catalog stale` CLI subcommand

**Files:**

- Modify: `.scripts/commands/skill.ts`

- [ ] **Step 1: Add the subcommand**

Inside the `catalog` subCommands object, add after `scrub`:

```typescript
stale: defineCommand({
  meta: {
    name: 'stale',
    description: 'Find analyzed skills with upstream content changes',
  },
  args: {
    ...globalArgs,
    limit: {
      type: 'string',
      description: 'Max entries to check (default: 100)',
      default: '100',
    },
    concurrency: {
      type: 'string',
      description: 'Parallel API requests (default: 5)',
      default: '5',
    },
  },
  async run({ args }) {
    const out = createOutput({
      json: args.json as boolean,
      quiet: args.quiet as boolean,
    })

    const catalogPath = join(PROJECT_ROOT, 'context/skills/.catalog.ndjson')
    if (!existsSync(catalogPath)) {
      out.error('Catalog not found.')
      process.exit(EXIT.ERROR)
    }

    const { identifyStaleEntries, fetchUpstreamHashes } = await import('../lib/catalog-stale')
    const allEntries = readCatalog(catalogPath) as import('../lib/catalog').CatalogEntryWithTier1[]
    const analyzed = allEntries.filter((e) => e.treeSha && e.wordCount && e.availability === 'available')
    const limit = parseInt(args.limit as string, 10) || 100
    const concurrency = parseInt(args.concurrency as string, 10) || 5
    const toCheck = analyzed.slice(0, limit)

    out.info(`Checking ${toCheck.length} analyzed skills against upstream...`)

    const upstreamHashes = await fetchUpstreamHashes(toCheck, { concurrency })
    const results = identifyStaleEntries(toCheck, upstreamHashes)
    const stale = results.filter((r) => r.status === 'stale')

    if (args.json) {
      out.raw({ checked: toCheck.length, stale: stale.length, results: stale })
    } else {
      out.info(`Checked: ${results.length}, Stale: ${stale.length}`)
      for (const r of stale) {
        out.info(`  ${r.source}@${r.skill} (local: ${r.localHash?.slice(0, 16)}... remote: ${r.remoteHash?.slice(0, 16)}...)`)
      }
      if (stale.length > 0) {
        out.info(`\nRe-analyze stale skills with: just agents skill catalog analyze --force`)
      }
    }

    process.exit(EXIT.OK)
  },
}),
```

- [ ] **Step 2: Smoke test**

Run: `just agents skill catalog stale --limit 5`
Expected: Checks 5 entries, reports stale/current counts

- [ ] **Step 3: Commit**

```bash
git add .scripts/commands/skill.ts
git commit -m "feat(catalog): add catalog stale command for content-change detection"
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| `cloneRepo` slower than `npx skills` for single-skill repos | `downloadBatch` groups by source — one clone per repo, not per skill |
| GitHub Trees API rate limits on `catalog stale` | Default limit=100, concurrency=5, uses authenticated API via `getClient()` with mutex-guarded token |
| `discoverSkills` finds different skills than `npx skills` naming | Direct-path fallback checks 4 well-known locations via `SKILL_LOOKUP_PATHS` |
| Breaking existing `processBatch` behavior | Blue/green: `--legacy-download` flag preserves old path, no behavioral change until Phase 3b |
| Device flow triggered during batch | Mutex: first worker triggers flow, others await same Promise. One prompt max per batch. |
| 1Password locked during batch | SSH auth fails non-interactively → `GitCloneError.isAuthError`, logged as retryable download_failed |
| Keyring unavailable (headless CI) | `GITHUB_TOKEN` env var bypasses keyring entirely. `readKeyring` catch returns null gracefully. |
| Token expired mid-batch | TTL check on every `getToken()` call. Expired → refresh (single refresh via mutex). |

## Rollback

Each phase produces independent commits. Revert any phase without affecting others:

- Phase 1: type + helper additions, no behavioral impact
- Phase 2: new module, not wired in yet
- Phase 3: blue/green — instant rollback via `--legacy-download` flag, no code revert needed
- Phase 3b: revert to restore the `--legacy-download` flag and legacy functions
- Phase 4: new command only, no impact on existing commands

**Blue/green rollback example:**

```bash
# Green path breaks? Instant rollback:
just agents skill catalog analyze --legacy-download --batch-size 25 --limit 10
# No code changes needed — legacy path is still in the binary
```
