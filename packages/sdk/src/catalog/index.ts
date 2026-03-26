// Catalog surface — pluggable storage for component indexes

export type { CatalogReader, CatalogStore, CatalogWriter } from './interface'
export { CatalogManager, type CatalogManagerOpts, createCatalog } from './manager'

export { NdjsonStore, type NdjsonStoreOptions } from './ndjson/index'
export {
  appendNdjsonFile,
  parseNdjson,
  readNdjsonFile,
  serializeNdjson,
  writeNdjsonFile,
} from './ndjson/io'

export { SqliteStore } from './sqlite/index'
export type {
  AnalysisFields,
  AvailabilityStatus,
  CatalogEntry,
  CatalogFilter,
  CatalogQuery,
  CatalogStats,
  DiscoveryResult,
  ErrorRecord,
  MechanicalFields,
  StaleResult,
  SyncResult,
} from './types'
