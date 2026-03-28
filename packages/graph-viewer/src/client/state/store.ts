/**
 * Centralized application state store.
 *
 * Provides a simple get/set/subscribe pattern. Subscribers are notified
 * whenever any property changes. The store is the single source of truth
 * for UI state that multiple modules need to read.
 */

// ---------------------------------------------------------------------------
// State interface
// ---------------------------------------------------------------------------

export interface AppState {
  /** ID of the currently loaded graph, or null if none loaded. */
  activeGraphId: string | null

  /** Set of currently selected node IDs. */
  selectedNodes: Set<string>

  /** Set of currently selected edge IDs. */
  selectedEdges: Set<string>

  /** ID of the node currently under the mouse cursor, or null. */
  hoveredNode: string | null

  /** Whether the graph has unsaved modifications. */
  isDirty: boolean

  /** Git working tree status of the graphs directory. */
  gitStatus: 'clean' | 'dirty' | 'unknown'

  /** Whether the WebSocket connection to the server is open. */
  wsConnected: boolean

  /** Whether a layout algorithm is currently running. */
  layoutRunning: boolean

  /** The currently active layout algorithm name. */
  activeLayout: string
}

// ---------------------------------------------------------------------------
// Subscriber type
// ---------------------------------------------------------------------------

type Subscriber = (state: Readonly<AppState>, changedKey: keyof AppState) => void

// ---------------------------------------------------------------------------
// Store class
// ---------------------------------------------------------------------------

export class Store {
  private state: AppState
  private readonly subscribers = new Set<Subscriber>()

  constructor() {
    this.state = {
      activeGraphId: null,
      selectedNodes: new Set(),
      selectedEdges: new Set(),
      hoveredNode: null,
      isDirty: false,
      gitStatus: 'unknown',
      wsConnected: false,
      layoutRunning: false,
      activeLayout: 'forceatlas2',
    }
  }

  /**
   * Get the current value of a state property.
   */
  get<K extends keyof AppState>(key: K): AppState[K] {
    return this.state[key]
  }

  /**
   * Get a readonly snapshot of the entire state.
   */
  getState(): Readonly<AppState> {
    return this.state
  }

  /**
   * Set a state property and notify all subscribers.
   */
  set<K extends keyof AppState>(key: K, value: AppState[K]): void {
    // Skip notification if the value has not actually changed
    // (except for Set types, which are mutable — always notify for those)
    if (!(value instanceof Set) && this.state[key] === value) {
      return
    }

    this.state[key] = value

    for (const subscriber of this.subscribers) {
      try {
        subscriber(this.state, key)
      } catch (err) {
        console.error('[Store] Error in subscriber:', err)
      }
    }
  }

  /**
   * Subscribe to state changes. Returns an unsubscribe function.
   */
  subscribe(fn: Subscriber): () => void {
    this.subscribers.add(fn)
    return () => {
      this.subscribers.delete(fn)
    }
  }
}

// ---------------------------------------------------------------------------
// Singleton instance
// ---------------------------------------------------------------------------

export const store = new Store()
