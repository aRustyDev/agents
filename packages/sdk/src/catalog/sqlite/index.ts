import { err, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import type { CatalogStore } from '../interface'
import type {
  CatalogEntry,
  CatalogFilter,
  CatalogQuery,
  DiscoveryResult,
  ErrorRecord,
  StaleResult,
  SyncResult,
} from '../types'

const NOT_IMPLEMENTED = new SdkError('SQLite store not yet implemented', 'E_STORAGE_BACKEND')

export class SqliteStore implements CatalogStore {
  readonly backend = 'sqlite'

  async query(_params: CatalogQuery): Promise<Result<CatalogEntry[]>> {
    return err(NOT_IMPLEMENTED)
  }

  async get(_source: string, _name: string): Promise<Result<CatalogEntry | undefined>> {
    return err(NOT_IMPLEMENTED)
  }

  async count(_filter?: CatalogFilter): Promise<Result<number>> {
    return err(NOT_IMPLEMENTED)
  }

  async findStale(_upstream: Map<string, string>): Promise<Result<StaleResult[]>> {
    return err(NOT_IMPLEMENTED)
  }

  async upsert(_entries: CatalogEntry[]): Promise<Result<number>> {
    return err(NOT_IMPLEMENTED)
  }

  async remove(_source: string, _name: string): Promise<Result<boolean>> {
    return err(NOT_IMPLEMENTED)
  }

  async merge(_results: DiscoveryResult[]): Promise<Result<SyncResult>> {
    return err(NOT_IMPLEMENTED)
  }

  async appendErrors(_errors: ErrorRecord[]): Promise<Result<void>> {
    return err(NOT_IMPLEMENTED)
  }

  async close(): Promise<void> {
    // noop
  }
}
