/**
 * Lock file handling for graph view state.
 *
 * Lock files (`.graph.lock.json`) store rendering concerns — node positions,
 * camera state, layout configuration — separate from graph data. This keeps
 * the graph JSON clean for agent consumption while preserving the developer's
 * visual arrangement across sessions.
 */

import { readFile, writeFile } from 'node:fs/promises'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Camera state for the graph viewport. */
export interface CameraState {
  readonly x: number
  readonly y: number
  readonly ratio: number
  readonly angle: number
}

/** Layout algorithm configuration stored in the lock file. */
export interface LayoutConfig {
  readonly algorithm: string
  readonly params?: Record<string, unknown>
}

/** Node position in 2D space. */
export interface NodePosition {
  readonly x: number
  readonly y: number
}

/**
 * The full lock file structure.
 *
 * Separated from graph data so that AI agents never need to care about
 * rendering concerns like positions and camera state.
 */
export interface LockFile {
  readonly version: 1
  readonly graphId: string
  readonly layout: LayoutConfig
  readonly positions: Record<string, NodePosition>
  readonly view: {
    readonly camera: CameraState
  }
  readonly filters: Record<string, unknown>
}

/** Report returned by {@link reconcileLock} describing what changed. */
export interface ReconcileReport {
  /** Node IDs that were in the lock file but not in the graph (removed). */
  readonly orphansRemoved: string[]
  /** Node IDs that are in the graph but had no position in the lock file. */
  readonly missingNodes: string[]
}

// ---------------------------------------------------------------------------
// Read / Write
// ---------------------------------------------------------------------------

/**
 * Read and parse a lock file from disk.
 *
 * Returns `null` if the file does not exist or cannot be parsed.
 * This is intentionally lenient — a missing or corrupt lock file should
 * never prevent the graph from loading.
 */
export async function readLock(path: string): Promise<LockFile | null> {
  try {
    const raw = await readFile(path, 'utf-8')
    const parsed: unknown = JSON.parse(raw)

    // Basic structural check — not full validation, just enough to prevent
    // runtime crashes from completely wrong data.
    if (
      typeof parsed === 'object' &&
      parsed !== null &&
      'version' in parsed &&
      (parsed as Record<string, unknown>).version === 1 &&
      'graphId' in parsed &&
      'positions' in parsed
    ) {
      return parsed as LockFile
    }
    return null
  } catch {
    return null
  }
}

/**
 * Write a lock file to disk.
 *
 * Uses 2-space indentation with a trailing newline to match the project's
 * JSON formatting conventions.
 */
export async function writeLock(path: string, lock: LockFile): Promise<void> {
  const json = `${JSON.stringify(lock, null, 2)}\n`
  await writeFile(path, json, 'utf-8')
}

// ---------------------------------------------------------------------------
// Reconciliation
// ---------------------------------------------------------------------------

/**
 * Reconcile a lock file against the current set of graph node IDs.
 *
 * Applies two rules:
 * 1. **Orphan removal** — positions for node IDs not in the graph are dropped.
 * 2. **Missing detection** — node IDs without positions are reported so the
 *    caller can assign positions via the configured layout algorithm.
 *
 * Returns a new lock file (immutable) and a report of what changed.
 *
 * @param lock - The existing lock file to reconcile.
 * @param nodeIds - The current set of node IDs in the graph.
 * @returns A tuple of `[reconciledLock, report]`.
 */
export function reconcileLock(lock: LockFile, nodeIds: string[]): [LockFile, ReconcileReport] {
  const nodeIdSet = new Set(nodeIds)

  // Find orphans: positions in lock for nodes not in the graph
  const orphansRemoved: string[] = []
  const reconciledPositions: Record<string, NodePosition> = {}

  for (const [id, position] of Object.entries(lock.positions)) {
    if (nodeIdSet.has(id)) {
      reconciledPositions[id] = position
    } else {
      orphansRemoved.push(id)
    }
  }

  // Find missing: nodes in the graph without positions in the lock
  const missingNodes: string[] = []
  for (const id of nodeIds) {
    if (!(id in lock.positions)) {
      missingNodes.push(id)
    }
  }

  const reconciledLock: LockFile = {
    ...lock,
    positions: reconciledPositions,
  }

  const report: ReconcileReport = {
    orphansRemoved,
    missingNodes,
  }

  return [reconciledLock, report]
}
