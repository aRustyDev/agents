/**
 * GitHub API integration via Octokit with Device Flow auth.
 *
 * Auth strategy (in priority order):
 * 1. Cached token at ~/.config/ai-tools/github-token
 * 2. Piggyback on `gh auth token` (GitHub CLI)
 * 3. Device Flow OAuth (prompts user to open browser)
 */

import { Octokit } from '@octokit/core'
import { createOAuthDeviceAuth } from '@octokit/auth-oauth-device'
import { homedir } from 'node:os'
import { join } from 'node:path'
import { mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs'
import { ok, err, CliError, tryAsync, type Result } from './types'

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
// Token management
// ---------------------------------------------------------------------------

/** Default token path. Overridable for testing via `setTokenPath`. */
let TOKEN_PATH = join(homedir(), '.config', 'ai-tools', 'github-token')

/**
 * Override the token cache path. Intended for tests only.
 */
export function setTokenPath(path: string): void {
  TOKEN_PATH = path
  // Reset the cached client when token path changes
  _client = null
}

/**
 * Get the current token path. Useful for tests to verify configuration.
 */
export function getTokenPath(): string {
  return TOKEN_PATH
}

/**
 * Read a cached GitHub token from disk, if one exists.
 */
export function getCachedToken(): string | null {
  try {
    if (!existsSync(TOKEN_PATH)) return null
    const token = readFileSync(TOKEN_PATH, 'utf-8').trim()
    return token.length > 0 ? token : null
  } catch {
    return null
  }
}

/**
 * Persist a GitHub token to disk for reuse across sessions.
 */
export function cacheToken(token: string): void {
  const dir = join(TOKEN_PATH, '..')
  mkdirSync(dir, { recursive: true })
  writeFileSync(TOKEN_PATH, token, { mode: 0o600 })
}

/**
 * Try to get a token from the GitHub CLI (`gh auth token`).
 * Returns null if `gh` is not installed or not authenticated.
 */
export async function getGhToken(): Promise<string | null> {
  try {
    const proc = Bun.spawnSync(['gh', 'auth', 'token'], {
      stdout: 'pipe',
      stderr: 'pipe',
    })
    if (proc.exitCode !== 0) return null
    const token = proc.stdout.toString().trim()
    return token.length > 0 ? token : null
  } catch {
    return null
  }
}

// ---------------------------------------------------------------------------
// Client initialization
// ---------------------------------------------------------------------------

const GITHUB_CLIENT_ID = process.env.AI_TOOLS_GITHUB_CLIENT_ID ?? 'Iv1.placeholder'

/** Lazy-initialized singleton client. */
let _client: Octokit | null = null

/**
 * Get an authenticated Octokit client.
 *
 * Tries auth sources in order:
 * 1. Cached token file
 * 2. GitHub CLI (`gh auth token`)
 * 3. Device Flow OAuth (interactive)
 *
 * The obtained token is cached for future use.
 */
export async function getClient(): Promise<Octokit> {
  if (_client) return _client

  // 1. Try cached token
  let token = getCachedToken()

  // 2. Try gh CLI
  if (!token) {
    token = await getGhToken()
    if (token) {
      cacheToken(token)
    }
  }

  // 3. Fall back to Device Flow
  if (!token) {
    token = await performDeviceFlow()
    cacheToken(token)
  }

  _client = new Octokit({ auth: token })
  return _client
}

/**
 * Perform OAuth Device Flow authentication.
 * Prompts the user to visit a URL and enter a code.
 */
async function performDeviceFlow(): Promise<string> {
  const auth = createOAuthDeviceAuth({
    clientType: 'oauth-app',
    clientId: GITHUB_CLIENT_ID,
    scopes: ['repo'],
    onVerification(verification) {
      console.log('\nGitHub authentication required.')
      console.log(`Open: ${verification.verification_uri}`)
      console.log(`Enter code: ${verification.user_code}\n`)
    },
  })

  const { token } = await auth({ type: 'oauth' })
  return token
}

/**
 * Reset the client singleton. Intended for tests only.
 */
export function resetClient(): void {
  _client = null
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
export async function createIssue(
  repo: string,
  opts: CreateIssueOpts,
): Promise<Result<Issue>> {
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
        e,
      ),
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
  opts: UpdateIssueOpts,
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
        e,
      ),
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
  body: string,
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
        e,
      ),
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
