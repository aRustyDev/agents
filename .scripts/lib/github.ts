/**
 * GitHub API integration via Octokit with Device Flow auth.
 *
 * Auth strategy (in priority order):
 * 1. GITHUB_TOKEN env var (CI override)
 * 2. @napi-rs/keyring cached token (if not expired)
 * 3. @octokit/auth-oauth-device flow (interactive)
 */

import { Entry } from '@napi-rs/keyring'
import { createOAuthDeviceAuth } from '@octokit/auth-oauth-device'
import { Octokit } from '@octokit/core'
import { CliError, type Result, tryAsync } from './types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Issue {
  number: number
  title: string
  state: string
  body?: string
  labels: { name: string }[]
  html_url: string
}

export interface CreateIssueOpts {
  title: string
  body: string
  labels?: string[]
}

export interface UpdateIssueOpts {
  title?: string
  body?: string
  state?: 'open' | 'closed'
  labels?: string[]
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

// cspell:disable-next-line -- OAuth App Client ID
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
    // Keyring write failed -- log but don't crash
    process.stderr.write('[github] Warning: failed to cache token in keychain\n')
  }
}

function deleteKeyring(service: string, account: string): void {
  try {
    new Entry(service, account).deletePassword()
  } catch {
    /* ignore */
  }
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
 * 1. GITHUB_TOKEN env var (CI override) -- checked every call, never cached
 * 2. @napi-rs/keyring cached token (if not expired)
 * 3. @octokit/auth-oauth-device flow -> stores in keyring on success
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
 * GITHUB_TOKEN env -> keyring cache -> device flow (mutex-guarded)
 *
 * Recreates the client if the token has been refreshed since last call.
 */
export async function getClient(): Promise<Octokit> {
  const token = await _provider.getToken()

  // Reuse existing client if token hasn't changed
  if (_client && token === _clientToken) return _client

  // Token changed (refreshed) or first call -- create new client
  _client = new Octokit({ auth: token })
  _clientToken = token
  return _client
}

/**
 * Reset the client singleton. Intended for tests only.
 */
export function resetClient(): void {
  _client = null
  _clientToken = null
}

/**
 * Get the token provider singleton (for testing or direct access).
 */
export function getTokenProvider(): GitHubTokenProvider {
  return _provider
}

// ---------------------------------------------------------------------------
// Repo string parsing
// ---------------------------------------------------------------------------

/**
 * Parse an "owner/repo" string into its components.
 */
export function parseRepo(repo: string): { owner: string; repo: string } {
  const parts = repo.split('/')
  if (parts.length !== 2 || !parts[0] || !parts[1]) {
    throw new Error(`Invalid repo format: "${repo}". Expected "owner/repo".`)
  }
  return { owner: parts[0], repo: parts[1] }
}

// ---------------------------------------------------------------------------
// Issue operations
// ---------------------------------------------------------------------------

/**
 * Search for issues in a repository.
 *
 * @param repo - Repository in "owner/repo" format
 * @param query - GitHub search query string
 * @returns Array of matching issues
 */
export async function searchIssues(repo: string, query: string): Promise<Issue[]> {
  const client = await getClient()
  const { owner, repo: repoName } = parseRepo(repo)

  const fullQuery = `repo:${owner}/${repoName} ${query}`
  const response = await client.request('GET /search/issues', {
    q: fullQuery,
  })

  return response.data.items.map(mapIssue)
}

/**
 * Read a single issue by number.
 *
 * @param repo - Repository in "owner/repo" format
 * @param number - Issue number
 * @returns The issue
 */
export async function readIssue(repo: string, number: number): Promise<Issue> {
  const client = await getClient()
  const { owner, repo: repoName } = parseRepo(repo)

  const response = await client.request('GET /repos/{owner}/{repo}/issues/{issue_number}', {
    owner,
    repo: repoName,
    issue_number: number,
  })

  return mapIssue(response.data)
}

/**
 * Create a new issue in a repository.
 *
 * @param repo - Repository in "owner/repo" format
 * @param opts - Issue creation options
 * @returns Result containing the created issue
 */
export async function createIssue(repo: string, opts: CreateIssueOpts): Promise<Result<Issue>> {
  return tryAsync(
    async () => {
      const client = await getClient()
      const { owner, repo: repoName } = parseRepo(repo)

      const response = await client.request('POST /repos/{owner}/{repo}/issues', {
        owner,
        repo: repoName,
        title: opts.title,
        body: opts.body,
        labels: opts.labels,
      })

      return mapIssue(response.data)
    },
    (e) =>
      new CliError(
        `Failed to create issue in ${repo}`,
        'E_GITHUB_CREATE',
        e instanceof Error ? e.message : String(e),
        e
      )
  )
}

/**
 * Update an existing issue.
 *
 * @param repo - Repository in "owner/repo" format
 * @param number - Issue number to update
 * @param opts - Fields to update
 * @returns Result indicating success or failure
 */
export async function updateIssue(
  repo: string,
  number: number,
  opts: UpdateIssueOpts
): Promise<Result<void>> {
  return tryAsync(
    async () => {
      const client = await getClient()
      const { owner, repo: repoName } = parseRepo(repo)

      await client.request('PATCH /repos/{owner}/{repo}/issues/{issue_number}', {
        owner,
        repo: repoName,
        issue_number: number,
        title: opts.title,
        body: opts.body,
        state: opts.state,
        labels: opts.labels,
      })
    },
    (e) =>
      new CliError(
        `Failed to update issue #${number} in ${repo}`,
        'E_GITHUB_UPDATE',
        e instanceof Error ? e.message : String(e),
        e
      )
  )
}

/**
 * Add a comment to an issue.
 *
 * @param repo - Repository in "owner/repo" format
 * @param number - Issue number
 * @param body - Comment body (markdown)
 * @returns Result indicating success or failure
 */
export async function addComment(
  repo: string,
  number: number,
  body: string
): Promise<Result<void>> {
  return tryAsync(
    async () => {
      const client = await getClient()
      const { owner, repo: repoName } = parseRepo(repo)

      await client.request('POST /repos/{owner}/{repo}/issues/{issue_number}/comments', {
        owner,
        repo: repoName,
        issue_number: number,
        body,
      })
    },
    (e) =>
      new CliError(
        `Failed to add comment to issue #${number} in ${repo}`,
        'E_GITHUB_COMMENT',
        e instanceof Error ? e.message : String(e),
        e
      )
  )
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Map a raw GitHub API issue response to our Issue type.
 */
function mapIssue(raw: Record<string, unknown>): Issue {
  const labels = Array.isArray(raw.labels)
    ? raw.labels.map((label: unknown) => {
        if (typeof label === 'string') return { name: label }
        if (typeof label === 'object' && label !== null && 'name' in label) {
          return { name: String((label as Record<string, unknown>).name) }
        }
        return { name: '' }
      })
    : []

  return {
    number: raw.number as number,
    title: raw.title as string,
    state: raw.state as string,
    body: (raw.body as string) ?? undefined,
    labels,
    html_url: raw.html_url as string,
  }
}
