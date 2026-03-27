// Re-export shim — moved to @agents/sdk/providers/local/external
export {
  type CheckResult,
  checkDrift,
  createDriftIssues,
  type DriftStatus,
  getStatus,
  gitLsRemote,
  readLock,
  readManifest,
  refreshLinks,
  type StatusResult,
  syncAll,
  syncSkill,
  writeLock,
} from '@agents/sdk/providers/local/external'
