import type { Result } from '@agents/core/types'
import type {
  CatalogEntry,
  CatalogFilter,
  CatalogQuery,
  DiscoveryResult,
  ErrorRecord,
  StaleResult,
  SyncResult,
} from './types'

export interface CatalogReader {
  query(params: CatalogQuery): Promise<Result<CatalogEntry[]>>
  get(source: string, name: string): Promise<Result<CatalogEntry | undefined>>
  count(filter?: CatalogFilter): Promise<Result<number>>
  findStale(upstream: Map<string, string>): Promise<Result<StaleResult[]>>
}

export interface CatalogWriter {
  upsert(entries: CatalogEntry[]): Promise<Result<number>>
  remove(source: string, name: string): Promise<Result<boolean>>
  merge(results: DiscoveryResult[]): Promise<Result<SyncResult>>
  appendErrors(errors: ErrorRecord[]): Promise<Result<void>>
}

export interface CatalogStore extends CatalogReader, CatalogWriter {
  readonly backend: string
  close(): Promise<void>
}
