/**
 * Unified skill search API with 3 backends and automatic fallback.
 *
 * Backends:
 *   1. skills-sh  -- skills.sh public HTTP API
 *   2. meilisearch -- local Meilisearch instance (via lib/meilisearch)
 *   3. catalog     -- offline substring search over .catalog.ndjson
 *
 * In `auto` mode the chain is: meilisearch -> skills-sh -> catalog.
 * The first backend that returns a non-empty result set wins.
 * Total failure returns an empty array -- this module never throws.
 */

import { join } from 'node:path'
import { clampLimit, clampPage } from '@agents/core/component/pagination'
import { readText } from '@agents/core/runtime'
import type { SearchBackendType, SkillSearchResult } from '@agents/core/schemas'
import { CliError, err, ok, type Result } from '@agents/core/types'
import { checkHealth, createClient, searchKeyword } from './meilisearch'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export type SearchBackend = 'skills-sh' | 'meilisearch' | 'catalog'

export class SearchError extends CliError {
  constructor(
    message: string,
    readonly backend: SearchBackend,
    hint?: string,
    cause?: unknown
  ) {
    super(message, `SEARCH_${backend.toUpperCase().replace('-', '_')}`, hint, cause)
  }
}

export interface SearchOptions {
  /** Maximum number of results to return (1..100, default 10). */
  limit?: number
  /** Page number for paginated results (>= 1, default 1). */
  page?: number
  /** Which backend to use (`auto` tries all in order). */
  source?: SearchBackendType
  /** Cancellation signal forwarded to network requests. */
  signal?: AbortSignal
  /**
   * Override path for the `.catalog.ndjson` file.
   * Defaults to `join(process.cwd(), '.catalog.ndjson')`.
   * Exposed for testing.
   */
  catalogPath?: string
}

// ---------------------------------------------------------------------------
// Backend: skills.sh
// ---------------------------------------------------------------------------

const SKILLS_SH_BASE = 'https://skills.sh/api/search'
const SKILLS_SH_TIMEOUT_MS = 3_000

async function searchSkillsSh(
  query: string,
  limit: number,
  page: number,
  signal?: AbortSignal
): Promise<Result<SkillSearchResult[]>> {
  try {
    const url = new URL(SKILLS_SH_BASE)
    url.searchParams.set('q', query)
    url.searchParams.set('limit', String(limit))
    if (page > 1) {
      url.searchParams.set('page', String(page))
    }

    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), SKILLS_SH_TIMEOUT_MS)

    // Combine caller's signal with our timeout
    if (signal) {
      signal.addEventListener('abort', () => controller.abort(), {
        once: true,
      })
    }

    let response: Response
    try {
      response = await fetch(url.toString(), { signal: controller.signal })
    } finally {
      clearTimeout(timer)
    }

    if (response.status === 429) {
      return ok([])
    }

    if (!response.ok) {
      return err(
        new SearchError(
          `skills.sh returned HTTP ${response.status}`,
          'skills-sh',
          'The skills.sh API may be temporarily unavailable.'
        )
      )
    }

    const body: unknown = await response.json()
    const items = Array.isArray(body) ? body : []

    const results: SkillSearchResult[] = items.map((item: Record<string, unknown>) => ({
      name: String(item.name ?? ''),
      source: String(item.source ?? item.repo ?? 'unknown') || 'unknown',
      description: item.description ? String(item.description) : '',
      installs: typeof item.installs === 'number' ? item.installs : undefined,
      url: item.url ? String(item.url) : undefined,
    }))

    return ok(results)
  } catch (cause) {
    // AbortError from timeout or caller cancellation
    if (cause instanceof DOMException && cause.name === 'AbortError') {
      return ok([])
    }
    return err(new SearchError('skills.sh request failed', 'skills-sh', undefined, cause))
  }
}

// ---------------------------------------------------------------------------
// Backend: Meilisearch
// ---------------------------------------------------------------------------

async function searchMeili(query: string, limit: number): Promise<Result<SkillSearchResult[]>> {
  try {
    const client = createClient()
    const health = await checkHealth(client)
    if (!health.ok) {
      return err(
        new SearchError(
          'Meilisearch is not available',
          'meilisearch',
          health.error.hint,
          health.error
        )
      )
    }

    const hits = await searchKeyword(client, query, { limit })

    const results: SkillSearchResult[] = hits.map((hit) => ({
      name: hit.name,
      source: hit.filePath || 'meilisearch',
      description: hit.description ?? hit.snippet ?? '',
      url: undefined,
      installs: undefined,
    }))

    return ok(results)
  } catch (cause) {
    return err(new SearchError('Meilisearch search failed', 'meilisearch', undefined, cause))
  }
}

// ---------------------------------------------------------------------------
// Backend: catalog (offline NDJSON)
// ---------------------------------------------------------------------------

async function searchCatalog(
  query: string,
  limit: number,
  page: number,
  catalogPath?: string
): Promise<Result<SkillSearchResult[]>> {
  const path = catalogPath ?? join(process.cwd(), '.catalog.ndjson')
  try {
    let content: string
    try {
      content = await readText(path)
    } catch {
      return ok([])
    }

    const lowerQuery = query.toLowerCase()
    const skip = (page - 1) * limit
    const results: SkillSearchResult[] = []
    let matched = 0

    for (const line of content.split('\n')) {
      const trimmed = line.trim()
      if (!trimmed) continue

      let entry: Record<string, unknown>
      try {
        entry = JSON.parse(trimmed) as Record<string, unknown>
      } catch {
        continue
      }

      const name = String(entry.name ?? entry.skill ?? '')
      const description = String(entry.description ?? '')
      const source = String(entry.source ?? 'unknown') || 'unknown'

      if (
        name.toLowerCase().includes(lowerQuery) ||
        description.toLowerCase().includes(lowerQuery)
      ) {
        matched++
        if (matched <= skip) continue
        results.push({
          name,
          source,
          description,
          installs: typeof entry.installs === 'number' ? entry.installs : undefined,
          url: entry.url ? String(entry.url) : undefined,
        })
        if (results.length >= limit) break
      }
    }

    return ok(results)
  } catch (cause) {
    return err(new SearchError('Catalog search failed', 'catalog', undefined, cause))
  }
}

// ---------------------------------------------------------------------------
// Internal dispatcher
// ---------------------------------------------------------------------------

async function searchBackend(
  query: string,
  limit: number,
  page: number,
  backend: SearchBackend,
  opts?: SearchOptions
): Promise<Result<SkillSearchResult[]>> {
  switch (backend) {
    case 'skills-sh':
      return searchSkillsSh(query, limit, page, opts?.signal)
    case 'meilisearch':
      return searchMeili(query, limit)
    case 'catalog':
      return searchCatalog(query, limit, page, opts?.catalogPath)
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/** Auto-mode fallback order: meilisearch -> skills-sh -> catalog. */
const AUTO_CHAIN: readonly SearchBackend[] = ['meilisearch', 'skills-sh', 'catalog'] as const

/**
 * Search for skills across one or more backends.
 *
 * In `auto` mode (the default) backends are tried in order and the first
 * non-empty result set is returned. If every backend fails or returns no
 * results, an empty array is returned -- this function never throws.
 */
export async function searchSkillsAPI(
  query: string,
  opts?: SearchOptions
): Promise<SkillSearchResult[]> {
  if (!query.trim()) return []

  const limit = clampLimit(opts?.limit)
  const page = clampPage(opts?.page)
  const source: SearchBackendType = opts?.source ?? 'auto'

  if (source !== 'auto') {
    const result = await searchBackend(query, limit, page, source, opts)
    return result.ok ? result.value : []
  }

  // Auto mode: try each backend in sequence
  for (const backend of AUTO_CHAIN) {
    const result = await searchBackend(query, limit, page, backend, opts)
    if (result.ok && result.value.length > 0) {
      return result.value
    }
  }

  return []
}
