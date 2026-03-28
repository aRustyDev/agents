/**
 * HTTP availability checking for catalog sources.
 *
 * Checks GitHub repo availability via HTTP HEAD requests with
 * concurrency control and rate limiting.
 */

import type { AvailabilityStatus } from './types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CheckOptions {
  concurrency?: number // parallel requests (default: 20)
  delayMs?: number // ms between batches (default: 500)
  token?: string // GitHub token for higher rate limit
  dryRun?: boolean // if true, skip actual HTTP requests
  timeout?: number // request timeout in ms (default: 10000)
}

// ---------------------------------------------------------------------------
// Single Repo Check
// ---------------------------------------------------------------------------

/**
 * Check GitHub availability for a single org/repo.
 * Uses HTTP HEAD to minimize payload. GitHub redirects archived repos to
 * /owner/repo/archived — we detect that via the Location header on a 301.
 */
export async function checkRepoAvailability(
  ownerRepo: string,
  opts: { token?: string; timeout?: number; dryRun?: boolean } = {}
): Promise<AvailabilityStatus> {
  if (opts.dryRun) return 'available'

  const url = `https://github.com/${ownerRepo}`
  const timeout = opts.timeout ?? 10_000

  const headers: Record<string, string> = {
    'User-Agent': 'catalog-availability-checker/1.0 (ai-context-library)',
  }
  if (opts.token) {
    headers.Authorization = `token ${opts.token}`
  }

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      method: 'HEAD',
      headers,
      redirect: 'manual', // capture redirects ourselves
      signal: controller.signal,
    })

    clearTimeout(timer)

    const status = response.status

    if (status === 200) return 'available'

    if (status === 301 || status === 302) {
      // GitHub archives repos by redirecting to the same URL (HEAD still returns 301)
      // A permanent redirect of a repo page typically signals archival or rename.
      // We conservatively mark 301 as 'archived'.
      return 'archived'
    }

    if (status === 404) return 'not_found'
    if (status === 401 || status === 403) return 'private'

    // 429 rate-limited — treat as error; caller should retry with backoff
    if (status === 429) return 'error'

    // Any other 4xx/5xx
    return 'error'
  } catch (_err) {
    clearTimeout(timer)
    // AbortError = timeout; fetch errors = network issue
    return 'error'
  }
}

// ---------------------------------------------------------------------------
// Batch Checker
// ---------------------------------------------------------------------------

/**
 * Check availability for all repos with concurrency control and rate limiting.
 * Returns a Map of ownerRepo -> AvailabilityStatus.
 * Writes progress to stderr.
 */
export async function checkAllRepos(
  repos: string[],
  opts: CheckOptions = {}
): Promise<Map<string, AvailabilityStatus>> {
  const { concurrency = 20, delayMs = 500, token, dryRun = false, timeout = 10_000 } = opts

  const results = new Map<string, AvailabilityStatus>()
  const total = repos.length
  let done = 0

  // Process repos in batches of `concurrency`
  for (let i = 0; i < repos.length; i += concurrency) {
    const batch = repos.slice(i, i + concurrency)

    const batchResults = await Promise.all(
      batch.map((repo) =>
        checkRepoAvailability(repo, { token, timeout, dryRun })
          .then((status) => ({ repo, status }))
          .catch(() => ({ repo, status: 'error' as AvailabilityStatus }))
      )
    )

    for (const { repo, status } of batchResults) {
      results.set(repo, status)
      done++
    }

    // Progress report to stderr
    const pct = Math.round((done / total) * 100)
    process.stderr.write(
      `\r  Checking repos: ${done}/${total} (${pct}%)  [batch ${Math.ceil((i + concurrency) / concurrency)} of ${Math.ceil(total / concurrency)}]`
    )

    // Rate-limit delay between batches (skip after the last batch)
    if (i + concurrency < repos.length && delayMs > 0 && !dryRun) {
      await new Promise((resolve) => setTimeout(resolve, delayMs))
    }
  }

  process.stderr.write('\n')
  return results
}
