// Catalog surface — pluggable storage for component indexes

// Pipeline modules
export { checkAllRepos, checkRepoAvailability } from './availability'
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
export * as pipeline from './pipeline/index'
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
