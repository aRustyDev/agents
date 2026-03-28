/**
 * Smithery Registry provider for the Component system.
 *
 * Smithery is an MCP server registry. It only supports search for the
 * `mcp-server` component type. Add, remove, list, and info operations
 * are not supported -- installation is handled by other providers once
 * the user has discovered a server via search.
 */

import { CliError, err, ok, type Result } from '../types'
import { clampLimit, clampPage, emptyPage } from './pagination'
import type {
  Component,
  ComponentAddOptions,
  ComponentAddResult,
  ComponentProvider,
  ComponentType,
  PaginatedResult,
  ProviderCapabilities,
  PublishOptions,
  PublishResult,
  RemoveResult,
  SearchParams,
} from './types'

const SMITHERY_API_BASE = 'https://registry.smithery.ai/api/v1'
const TIMEOUT_MS = 3_000

export class SmitheryProvider implements ComponentProvider {
  readonly id = 'smithery'
  readonly displayName = 'Smithery Registry'
  readonly capabilities: ProviderCapabilities = {
    search: ['mcp-server'],
    add: [],
    list: [],
    remove: [],
    publish: ['mcp-server'],
    info: [],
    outdated: [],
    update: [],
  }

  private readonly baseUrl: string

  constructor(opts?: { baseUrl?: string }) {
    this.baseUrl = opts?.baseUrl ?? SMITHERY_API_BASE
  }

  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    if (params.type && params.type !== 'mcp-server') {
      return ok(emptyPage(clampPage(params.page), clampLimit(params.limit)))
    }

    const limit = clampLimit(params.limit)
    const page = clampPage(params.page)

    try {
      const url = new URL(`${this.baseUrl}/servers`)
      if (params.query) url.searchParams.set('q', params.query)
      url.searchParams.set('pageSize', String(limit))
      url.searchParams.set('page', String(page))
      if (params.verified) url.searchParams.set('verified', 'true')
      if (params.namespace) url.searchParams.set('namespace', params.namespace)

      const controller = new AbortController()
      const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)

      let response: Response
      try {
        response = await fetch(url.toString(), { signal: controller.signal })
      } finally {
        clearTimeout(timer)
      }

      if (response.status === 429) {
        return ok(emptyPage(page, limit))
      }

      if (!response.ok) {
        return ok(emptyPage(page, limit))
      }

      const body = (await response.json()) as { servers?: unknown[] }
      const servers = Array.isArray(body.servers)
        ? body.servers
        : Array.isArray(body)
          ? (body as unknown[])
          : []

      const items: Component[] = servers.map((s: Record<string, unknown>) => ({
        type: 'mcp-server' as const,
        name: String(s.qualifiedName ?? s.name ?? ''),
        source: `smithery://${String(s.qualifiedName ?? s.name ?? '')}`,
        description: String(s.description ?? s.displayName ?? ''),
        url: s.qualifiedName ? `https://smithery.ai/server/${String(s.qualifiedName)}` : undefined,
        installs: typeof s.useCount === 'number' ? s.useCount : undefined,
        verified: typeof s.verified === 'boolean' ? s.verified : undefined,
        namespace: typeof s.qualifiedName === 'string' ? s.qualifiedName.split('/')[0] : undefined,
      }))

      return ok({
        items,
        page,
        pageSize: limit,
        hasMore: items.length >= limit,
        total: undefined,
      })
    } catch (cause) {
      if (cause instanceof DOMException && cause.name === 'AbortError') {
        return ok(emptyPage(page, limit))
      }
      return ok(emptyPage(page, limit))
    }
  }

  // -- Non-search operations: not supported by Smithery ---

  async add(_source: string, _opts: ComponentAddOptions): Promise<Result<ComponentAddResult>> {
    return err(new CliError('Smithery provider does not support add', 'E_UNSUPPORTED'))
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
    return err(new CliError('Smithery provider does not support remove', 'E_UNSUPPORTED'))
  }

  async info(
    _name: string,
    _type: ComponentType,
    _opts?: { cwd?: string }
  ): Promise<Result<Component>> {
    return err(new CliError('Smithery provider does not support info', 'E_UNSUPPORTED'))
  }

  async publish(type: ComponentType, opts: PublishOptions): Promise<Result<PublishResult>> {
    if (type !== 'mcp-server') {
      return err(
        new CliError(`Smithery only supports publishing mcp-server, not ${type}`, 'E_UNSUPPORTED')
      )
    }

    // Resolve auth
    const { resolveSmitheryAuth } = await import('./smithery-auth')
    const authResult = resolveSmitheryAuth({ apiKey: opts.apiKey })
    if (!authResult.ok) return err(authResult.error)

    // Resolve qualified name
    const qualifiedName = opts.name ?? (opts.namespace ? `${opts.namespace}/unknown` : undefined)
    if (!qualifiedName) {
      return err(
        new CliError('Qualified name required (--name namespace/server)', 'E_MISSING_NAME')
      )
    }

    // Delegate to publish module
    const { publishToSmithery } = await import('./smithery-publish')
    const result = await publishToSmithery({
      qualifiedName,
      apiKey: authResult.value.apiKey,
      externalUrl: opts.externalUrl,
      configSchema: opts.configSchema,
      bundleDir: opts.bundleDir,
      dryRun: opts.dryRun,
      baseUrl: this.baseUrl,
    })

    if (!result.ok) return err(result.error)

    return ok({
      ok: result.value.ok,
      registryUrl: result.value.registryUrl,
      releaseId: result.value.releaseId,
      status: result.value.status,
      error: result.value.error,
      warnings: result.value.warnings,
    })
  }
}
