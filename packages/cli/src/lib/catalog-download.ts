/**
 * Re-export shim — catalog-download.ts moved to @agents/sdk/catalog/pipeline/download in Phase 3.
 */

export type {
  BackfillOptions,
  BatchDownloadOptions,
  CatalogSource,
  DownloadOptions,
  SkillDownloadResult,
} from '@agents/sdk/catalog/pipeline/download'

export {
  backfillEntries,
  downloadBatch,
  downloadSkill,
  SKILL_LOOKUP_DIRS,
  validateCatalogSource,
} from '@agents/sdk/catalog/pipeline/download'
