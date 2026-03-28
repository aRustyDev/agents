/**
 * GitHub provider for the Component system.
 *
 * Provides search-only capability for discovering Claude Code skills
 * on GitHub. Uses the GitHub code search API to find repositories
 * containing SKILL.md files.
 *
 * Other operations (add, remove, list, info, publish) are not supported --
 * users discover skills via search, then install via the local provider.
 */

import type { Result } from '@agents/core/types'
import { err, ok } from '@agents/core/types'
import type {
  Component,
  ComponentAddOptions,
  ComponentAddResult,
  ComponentProvider,
  ComponentType,
  PaginatedResult,
  ProviderCapabilities,
  PublishResult,
  RemoveResult,
  SearchParams,
} from '../../context/types'
import { SdkError } from '../../util/errors'
import { clampLimit, clampPage, emptyPage, paginateArray } from '../pagination'
import { buildSkillSearchQuery } from './search'

const TIMEOUT_MS = 5_000

export class GitHubProvider implements ComponentProvider {
  readonly id = 'github'
  readonly displayName = 'GitHub'
  readonly capabilities: ProviderCapabilities = {
    search: ['skill'],
    add: [],
    list: [],
    remove: [],
    publish: [],
    info: [],
    outdated: [],
    update: [],
  }

  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    if (params.type && params.type !== 'skill') {
      return ok(emptyPage(clampPage(params.page), clampLimit(params.limit)))
    }

    const limit = clampLimit(params.limit)
    const page = clampPage(params.page)

    try {
      // Use GitHub code search API (public, no auth required for basic usage)
      const query = buildSkillSearchQuery(params.query)
      const url = new URL('https://api.github.com/search/code')
      url.searchParams.set('q', query)
      url.searchParams.set('per_page', String(limit))
      url.searchParams.set('page', String(page))

      const controller = new AbortController()
      const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)

      let response: Response
      try {
        const headers: Record<string, string> = {
          Accept: 'application/vnd.github.v3+json',
          'User-Agent': 'agents-sdk',
        }

        // Use GITHUB_TOKEN if available for higher rate limits
        const token = process.env.GITHUB_TOKEN
        if (token) {
          headers.Authorization = `Bearer ${token}`
        }

        response = await fetch(url.toString(), {
          headers,
          signal: controller.signal,
        })
      } finally {
        clearTimeout(timer)
      }

      if (response.status === 403 || response.status === 429) {
        // Rate limited
        return ok(emptyPage(page, limit))
      }

      if (!response.ok) {
        return ok(emptyPage(page, limit))
      }

      const body = (await response.json()) as {
        total_count?: number
        items?: Array<{
          name: string
          path: string
          repository: {
            full_name: string
            description: string
            html_url: string
            stargazers_count: number
            topics?: string[]
            owner?: { login: string }
          }
        }>
      }

      const items: Component[] = (body.items ?? []).map((item) => ({
        type: 'skill' as const,
        name: item.repository.full_name,
        source: `github://${item.repository.full_name}`,
        description: item.repository.description ?? '',
        url: item.repository.html_url,
        stars: item.repository.stargazers_count,
        tags: item.repository.topics,
        namespace: item.repository.owner?.login,
      }))

      // Deduplicate by repository (multiple SKILL.md files per repo)
      const seen = new Set<string>()
      const deduped: Component[] = []
      for (const item of items) {
        if (!seen.has(item.name)) {
          seen.add(item.name)
          deduped.push(item)
        }
      }

      return ok({
        items: deduped,
        page,
        pageSize: limit,
        hasMore: (body.total_count ?? 0) > page * limit,
        total: body.total_count,
      })
    } catch (cause) {
      if (cause instanceof DOMException && cause.name === 'AbortError') {
        return ok(emptyPage(page, limit))
      }
      return ok(emptyPage(page, limit))
    }
  }

  // -- Non-search operations: not supported ---

  async add(_source: string, _opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
    return err(new SdkError('GitHub provider does not support add', 'E_PROVIDER_UNAVAILABLE'))
  }

  async list(
    _type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<Component[]>> {
    return ok([])
  }

  async remove(
    _name: string,
    _type: ComponentType,
    _opts?: { cwd?: string; agent?: string }
  ): Promise<Result<RemoveResult>> {
    return err(new SdkError('GitHub provider does not support remove', 'E_PROVIDER_UNAVAILABLE'))
  }

  async info(
    _name: string,
    _type: ComponentType,
    _opts?: { cwd?: string }
  ): Promise<Result<Component>> {
    return err(new SdkError('GitHub provider does not support info', 'E_PROVIDER_UNAVAILABLE'))
  }

  async publish(): Promise<Result<PublishResult>> {
    return err(new SdkError('GitHub provider does not support publish', 'E_PROVIDER_UNAVAILABLE'))
  }
}
