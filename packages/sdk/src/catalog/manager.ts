import { ok, type Result } from '@agents/core/types'
import type { Logger } from '../util/logger'
import type { CatalogStore } from './interface'
import type {
  CatalogEntry,
  CatalogQuery,
  CatalogStats,
  DiscoveryResult,
  StaleResult,
  SyncResult,
} from './types'

export interface CatalogManagerOpts {
  store: CatalogStore
  logger?: Logger
}

export function createCatalog(opts: CatalogManagerOpts): CatalogManager {
  return new CatalogManager(opts)
}

export class CatalogManager {
  readonly store: CatalogStore
  private readonly logger?: Logger

  constructor(opts: CatalogManagerOpts) {
    this.store = opts.store
    this.logger = opts.logger
  }

  async query(params: CatalogQuery): Promise<Result<CatalogEntry[]>> {
    this.logger?.debug('catalog.query', { params })
    const result = await this.store.query(params)
    if (result.ok) {
      this.logger?.debug('catalog.query.result', { count: result.value.length })
    }
    return result
  }

  async get(source: string, name: string): Promise<Result<CatalogEntry | undefined>> {
    this.logger?.debug('catalog.get', { source, name })
    return this.store.get(source, name)
  }

  async stats(): Promise<Result<CatalogStats>> {
    this.logger?.debug('catalog.stats')
    const all = await this.store.query({})
    if (!all.ok) return all as Result<never>

    const entries = all.value
    const byType: Record<string, number> = {}
    const byAvailability: Record<string, number> = {}
    let analyzed = 0
    let withErrors = 0

    for (const entry of entries) {
      byType[entry.type] = (byType[entry.type] ?? 0) + 1
      byAvailability[entry.availability] = (byAvailability[entry.availability] ?? 0) + 1
      if (entry.analysis) analyzed++
      if (entry.errorCount && entry.errorCount > 0) withErrors++
    }

    return ok({
      total: entries.length,
      byType,
      byAvailability,
      analyzed,
      withErrors,
    })
  }

  async findStale(upstream: Map<string, string>): Promise<Result<StaleResult[]>> {
    this.logger?.debug('catalog.findStale', { upstreamCount: upstream.size })
    return this.store.findStale(upstream)
  }

  async sync(results: DiscoveryResult[]): Promise<Result<SyncResult>> {
    this.logger?.debug('catalog.sync', { count: results.length })
    const syncResult = await this.store.merge(results)
    if (syncResult.ok) {
      this.logger?.info('catalog.sync.complete', { ...syncResult.value })
    }
    return syncResult
  }
}
