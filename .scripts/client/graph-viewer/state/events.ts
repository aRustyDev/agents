/**
 * Typed event bus for cross-module communication.
 *
 * All modules communicate through this event bus rather than importing
 * each other directly. Event names follow the `domain:action` convention.
 */

// ---------------------------------------------------------------------------
// Event type map — every event and its payload
// ---------------------------------------------------------------------------

export interface EventMap {
  // Graph lifecycle
  'graph:loaded': { graphId: string; nodeCount: number; edgeCount: number }
  'graph:saved': { graphId: string }
  'graph:save-failed': { graphId: string; error: string }
  'graph:node-selected': {
    nodeId: string
    attributes: Record<string, unknown>
  }
  'graph:node-deselected': { nodeId: string }
  'graph:all-deselected': undefined
  'graph:node-hovered': { nodeId: string }
  'graph:node-unhovered': { nodeId: string }

  // CRUD mutations
  'graph:node-added': { nodeId: string }
  'graph:node-removed': { nodeId: string }
  'graph:edge-added': { edgeId: string }
  'graph:edge-removed': { edgeId: string }
  'graph:node-updated': {
    nodeId: string
    key: string
    oldValue: unknown
    newValue: unknown
  }

  // Layout
  'layout:started': { algorithm: string }
  'layout:stopped': { algorithm: string }
  'layout:changed': { algorithm: string }
  // WebSocket
  'ws:connected': undefined
  'ws:disconnected': undefined
  'ws:file-changed': { type: string; file: string; graphId?: string }

  // Filters
  'filter:changed': { activeCount: number }
  'filter:apply': undefined
  'filter:clear-view': undefined

  // UI
  'ui:toast': {
    message: string
    type: 'info' | 'warn' | 'error'
    duration?: number
  }
}

// ---------------------------------------------------------------------------
// EventBus class
// ---------------------------------------------------------------------------

type Handler<T> = (data: T) => void

export class EventBus {
  private readonly listeners = new Map<string, Set<Handler<unknown>>>()

  /**
   * Subscribe to an event. Returns an unsubscribe function.
   */
  on<K extends keyof EventMap>(event: K, handler: Handler<EventMap[K]>): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    const set = this.listeners.get(event)!
    set.add(handler as Handler<unknown>)
    return () => {
      set.delete(handler as Handler<unknown>)
    }
  }

  /**
   * Unsubscribe a specific handler from an event.
   */
  off<K extends keyof EventMap>(event: K, handler: Handler<EventMap[K]>): void {
    const set = this.listeners.get(event)
    if (set) {
      set.delete(handler as Handler<unknown>)
    }
  }

  /**
   * Emit an event to all registered handlers.
   */
  emit<K extends keyof EventMap>(
    event: K,
    ...args: EventMap[K] extends undefined ? [] : [EventMap[K]]
  ): void {
    const set = this.listeners.get(event)
    if (!set) return
    const data = args[0] as EventMap[K]
    for (const handler of set) {
      try {
        handler(data)
      } catch (err) {
        console.error(`[EventBus] Error in handler for "${event}":`, err)
      }
    }
  }

  /**
   * Remove all listeners for a specific event, or all events if none specified.
   */
  clear(event?: keyof EventMap): void {
    if (event) {
      this.listeners.delete(event)
    } else {
      this.listeners.clear()
    }
  }
}

// ---------------------------------------------------------------------------
// Singleton instance
// ---------------------------------------------------------------------------

export const bus = new EventBus()
