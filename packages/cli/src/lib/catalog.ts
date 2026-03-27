/**
 * Re-export shim — catalog.ts moved to @agents/sdk/catalog/pipeline in Phase 3.
 *
 * This file preserves backward compatibility for CLI consumers.
 * All implementations now live in the SDK package.
 */

// Availability checks
export {
  checkAllRepos,
  checkRepoAvailability,
} from '@agents/sdk/catalog/availability'
// Compute functions
export {
  computeContentHash,
  computeFileCount,
  computeFileTree,
  computeHeadingTree,
  computeLineCount,
  computeSectionCount,
  computeSectionMap,
  computeSkillSizeBytes,
  computeWordCount,
  extractKeywords,
  isSimpleSkill,
} from '@agents/sdk/catalog/pipeline/compute'
// I/O functions
export {
  appendError,
  appendErrors,
  createBatches,
  detectForks,
  filterAvailable,
  filterForProcessing,
  formatBatchPrompt,
  getErrorsForSkill,
  loadProcessedRepos,
  mergeBackfillResults,
  mergeRepoManifest,
  mergeTier1Results,
  migrateCatalogSchema,
  parseTier1Output,
  parseTodoYaml,
  readCatalog,
  readErrorLog,
  readRepoManifest,
  uniqueRepos,
  validateBatchResults,
  writeCatalogEntries,
  writeRepoManifest,
} from '@agents/sdk/catalog/pipeline/io'
// Types
export type {
  BackfillResult,
  CatalogEntry,
  CatalogEntryWithTier1,
  ComponentMetadata,
  ErrorRecord,
  FilterProcessingOpts,
  RepoManifest,
  SectionMapEntry,
  Tier1ErrorType,
  Tier1Result,
  Tier1ResultWithTransient,
  TransientErrorFields,
  ValidationReport,
} from '@agents/sdk/catalog/pipeline/types'
export type { AvailabilityStatus } from '@agents/sdk/catalog/types'
