/**
 * Re-export shim — catalog-reconcile.ts moved to @agents/sdk/catalog/pipeline/reconcile in Phase 3.
 */

export type {
  ReconciliationAction,
  ReconciliationEntry,
  ReconciliationReport,
} from '@agents/sdk/catalog/pipeline/reconcile'

export {
  applyReconciliation,
  detectMoveRenames,
  reconcile,
} from '@agents/sdk/catalog/pipeline/reconcile'
