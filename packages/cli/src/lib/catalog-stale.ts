/**
 * Re-export shim — catalog-stale.ts moved to @agents/sdk/catalog/pipeline/stale in Phase 3.
 */

export type {
  StaleCheckResult,
  StaleStatus,
} from '@agents/sdk/catalog/pipeline/stale'

export {
  fetchUpstreamHashes,
  identifyStaleEntries,
} from '@agents/sdk/catalog/pipeline/stale'
