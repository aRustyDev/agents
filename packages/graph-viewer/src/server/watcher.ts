/**
 * File system watcher for graph data changes.
 *
 * Watches the `.data/graphs/` directory for file changes and emits typed
 * events. Events are debounced (200ms) to collapse rapid successive writes
 * (common with editors that do write-rename cycles).
 *
 * The watcher is designed to be robust against transient filesystem errors --
 * individual watch errors are logged but never crash the server.
 */

import { existsSync, type FSWatcher, watch } from 'node:fs'
import { basename, resolve } from 'node:path'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Event types emitted by the file watcher. */
export type FileChangeType = 'file:changed' | 'file:created' | 'file:deleted'

/** Payload broadcast to WebSocket clients on file change. */
export interface FileChangeEvent {
  readonly type: FileChangeType
  /** Path relative to the graphs directory. */
  readonly file: string
  /** The graph ID this file belongs to, if determinable. */
  readonly graphId?: string
}

/** Callback signature for file change listeners. */
export type FileChangeCallback = (event: FileChangeEvent) => void

/** Handle returned by createWatcher. */
export interface GraphWatcher {
  /** Start watching the directory. Idempotent. */
  start: () => void
  /** Stop watching. Safe to call even if not started. */
  stop: () => void
  /** Register a callback for file change events. Returns an unsubscribe function. */
  onFileChange: (cb: FileChangeCallback) => () => void
}

// ---------------------------------------------------------------------------
// Implementation
// ---------------------------------------------------------------------------

/** Debounce interval in milliseconds. */
const DEBOUNCE_MS = 200

/**
 * Attempt to extract a graph ID from a filename.
 *
 * Graph files follow the pattern `<id>.json` or `<id>.graph.lock.json`.
 * Returns undefined for non-graph files (manifest.json, schemas, etc.).
 */
function extractGraphId(filename: string): string | undefined {
  // Skip manifest and schema files
  if (filename === 'manifest.json') return undefined
  if (filename.startsWith('schemas/') || filename.startsWith('schemas\\')) return undefined

  // Lock file: <id>.graph.lock.json
  const lockMatch = filename.match(/^([a-zA-Z0-9_-]+)\.graph\.lock\.json$/)
  if (lockMatch) return lockMatch[1]

  // Graph file: <id>.json
  const graphMatch = filename.match(/^([a-zA-Z0-9_-]+)\.json$/)
  if (graphMatch) return graphMatch[1]

  return undefined
}

/**
 * Determine the change type by checking whether the file exists after the
 * event fires. This is a best-effort heuristic -- between the event and the
 * stat call, additional changes may have occurred.
 */
function inferChangeType(absolutePath: string): FileChangeType {
  try {
    if (existsSync(absolutePath)) {
      // We cannot distinguish create from modify reliably with fs.watch,
      // but for the UI's purposes "changed" covers both.
      return 'file:changed'
    }
    return 'file:deleted'
  } catch {
    return 'file:changed'
  }
}

/**
 * Create a file watcher for the graphs data directory.
 *
 * @param graphsDir - Absolute path to the graphs directory.
 * @returns A {@link GraphWatcher} handle.
 */
export function createWatcher(graphsDir: string): GraphWatcher {
  const listeners = new Set<FileChangeCallback>()
  let watcher: FSWatcher | null = null

  // Debounce map: relative path -> timer handle
  const debounceTimers = new Map<string, ReturnType<typeof setTimeout>>()

  function emitEvent(event: FileChangeEvent): void {
    for (const cb of listeners) {
      try {
        cb(event)
      } catch (err) {
        console.error('[watcher] Listener error:', err)
      }
    }
  }

  function handleFsEvent(_eventType: string, filename: string | null): void {
    if (!filename) return

    // Normalize to forward slashes
    const normalizedFile = filename.replace(/\\/g, '/')

    // Debounce: clear any pending timer for this file
    const existing = debounceTimers.get(normalizedFile)
    if (existing) clearTimeout(existing)

    debounceTimers.set(
      normalizedFile,
      setTimeout(() => {
        debounceTimers.delete(normalizedFile)

        const absolutePath = resolve(graphsDir, normalizedFile)
        const changeType = inferChangeType(absolutePath)
        const graphId = extractGraphId(basename(normalizedFile))

        const event: FileChangeEvent = {
          type: changeType,
          file: normalizedFile,
          ...(graphId !== undefined ? { graphId } : {}),
        }

        emitEvent(event)
      }, DEBOUNCE_MS)
    )
  }

  function start(): void {
    if (watcher) return // Already watching

    try {
      watcher = watch(graphsDir, { recursive: true }, (eventType, filename) => {
        try {
          handleFsEvent(eventType, filename)
        } catch (err) {
          console.error('[watcher] Error handling fs event:', err)
        }
      })

      watcher.on('error', (err) => {
        console.error('[watcher] FSWatcher error:', err)
        // Do not crash; the watcher may recover on the next event
      })

      console.log(`[watcher] Watching ${graphsDir}`)
    } catch (err) {
      console.error('[watcher] Failed to start:', err)
    }
  }

  function stop(): void {
    if (watcher) {
      watcher.close()
      watcher = null
    }

    // Clear any pending debounce timers
    for (const timer of debounceTimers.values()) {
      clearTimeout(timer)
    }
    debounceTimers.clear()

    console.log('[watcher] Stopped')
  }

  function onFileChange(cb: FileChangeCallback): () => void {
    listeners.add(cb)
    return () => {
      listeners.delete(cb)
    }
  }

  return { start, stop, onFileChange }
}
