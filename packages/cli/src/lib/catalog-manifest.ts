/**
 * Re-export shim — catalog-manifest.ts moved to @agents/sdk/catalog/pipeline/manifest in Phase 3.
 */

export type {
  SkillManifest,
  Tier1Judgment,
} from '@agents/sdk/catalog/pipeline/manifest'

export {
  buildManifest,
  buildManifestFromEntry,
  buildTier1AgentPrompt,
  formatManifestBatch,
} from '@agents/sdk/catalog/pipeline/manifest'
