// Re-export shim — moved to @agents/sdk/providers/local/lockfile in Phase 2

export type {
  LockfileSchema,
  StalenessEntry,
  StalenessReport,
} from '@agents/sdk/providers/local/lockfile'
export {
  checkStaleness,
  getSchema,
  readLockfile,
  registerSchema,
  writeLockfile,
} from '@agents/sdk/providers/local/lockfile'
