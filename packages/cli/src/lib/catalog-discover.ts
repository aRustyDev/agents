/**
 * Re-export shim — catalog-discover.ts moved to @agents/sdk/catalog/pipeline/discover in Phase 3.
 */

export type {
  DiscoveredSkillResult,
  DiscoverOptions,
  DiscoverySummary,
  RepoDiscoveryResult,
} from '@agents/sdk/catalog/pipeline/discover'

export {
  collectRepoMetadata,
  computeAllMechanicalFields,
  discoverAllRepos,
  discoverRepo,
  fetchRemoteHeadSha,
} from '@agents/sdk/catalog/pipeline/discover'
