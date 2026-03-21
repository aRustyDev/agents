/**
 * Filter engine — manages active filter predicates for the graph viewer.
 *
 * Filters are applied via Sigma's nodeReducer and edgeReducer, which run
 * on every render frame. The engine maintains state for:
 * - Which node types are visible (all enabled by default)
 * - Which edge types are visible (all enabled by default)
 * - A label substring search (case-insensitive)
 *
 * All filters are combined with AND logic: a node must pass all active
 * filters to remain visible.
 */

import { EDGE_TYPES, NODE_TYPES } from '../interaction/crud'
import { bus } from '../state/events'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface FilterState {
  /** Which node types are visible (all enabled by default). */
  enabledNodeTypes: Set<string>

  /** Which edge types are visible (all enabled by default). */
  enabledEdgeTypes: Set<string>

  /** Label substring search (case-insensitive). */
  searchQuery: string
}

// ---------------------------------------------------------------------------
// FilterEngine class
// ---------------------------------------------------------------------------

export class FilterEngine {
  private state: FilterState
  private onChange: (() => void) | null = null

  constructor() {
    this.state = {
      enabledNodeTypes: new Set<string>(NODE_TYPES),
      enabledEdgeTypes: new Set<string>(EDGE_TYPES),
      searchQuery: '',
    }
  }

  /**
   * Register a callback invoked whenever any filter changes.
   * Used to trigger Sigma refresh.
   */
  onFilterChange(cb: () => void): void {
    this.onChange = cb
  }

  /** Toggle visibility of a node type. */
  toggleNodeType(nodeType: string): void {
    if (this.state.enabledNodeTypes.has(nodeType)) {
      this.state.enabledNodeTypes.delete(nodeType)
    } else {
      this.state.enabledNodeTypes.add(nodeType)
    }
    this.fireChange()
  }

  /** Toggle visibility of an edge type. */
  toggleEdgeType(edgeType: string): void {
    if (this.state.enabledEdgeTypes.has(edgeType)) {
      this.state.enabledEdgeTypes.delete(edgeType)
    } else {
      this.state.enabledEdgeTypes.add(edgeType)
    }
    this.fireChange()
  }

  /** Update the label search query. */
  setSearchQuery(query: string): void {
    this.state.searchQuery = query
    this.fireChange()
  }

  /** Re-enable all types and clear the search query. */
  clearAll(): void {
    this.state.enabledNodeTypes = new Set<string>(NODE_TYPES)
    this.state.enabledEdgeTypes = new Set<string>(EDGE_TYPES)
    this.state.searchQuery = ''
    this.fireChange()
  }

  /**
   * Check if a node passes all active filters (AND logic).
   *
   * NOTE: This runs on every frame for every node. Keep it fast.
   */
  isNodeVisible(_nodeId: string, attrs: Record<string, unknown>): boolean {
    // 1. Check nodeType is enabled
    const nodeType = String(attrs.nodeType ?? 'Concept')
    if (!this.state.enabledNodeTypes.has(nodeType)) {
      return false
    }

    // 2. Check label matches search query (if query is non-empty)
    const query = this.state.searchQuery
    if (query) {
      const label = String(attrs.label ?? '')
      if (!label.toLowerCase().includes(query.toLowerCase())) {
        return false
      }
    }

    return true
  }

  /**
   * Check if an edge passes all active filters.
   *
   * An edge is visible only if its edgeType is enabled AND both the
   * source and target nodes are visible.
   *
   * NOTE: This runs on every frame for every edge. Keep it fast.
   */
  isEdgeVisible(
    _edgeId: string,
    attrs: Record<string, unknown>,
    sourceVisible: boolean,
    targetVisible: boolean
  ): boolean {
    // Edge hidden if either endpoint is hidden
    if (!sourceVisible || !targetVisible) {
      return false
    }

    // Check edgeType is enabled
    const edgeType = String(attrs.edgeType ?? 'relates_to')
    if (!this.state.enabledEdgeTypes.has(edgeType)) {
      return false
    }

    return true
  }

  /** Get a readonly snapshot of the current filter state. */
  getState(): Readonly<FilterState> {
    return this.state
  }

  /**
   * Count the number of active filters (filters that deviate from
   * the default "everything visible, no search" state).
   */
  getActiveFilterCount(): number {
    let count = 0

    // Count disabled node types
    const disabledNodeTypes = NODE_TYPES.length - this.state.enabledNodeTypes.size
    count += disabledNodeTypes

    // Count disabled edge types
    const disabledEdgeTypes = EDGE_TYPES.length - this.state.enabledEdgeTypes.size
    count += disabledEdgeTypes

    // Count non-empty search query as 1 active filter
    if (this.state.searchQuery.trim().length > 0) {
      count += 1
    }

    return count
  }

  // -------------------------------------------------------------------------
  // Internal
  // -------------------------------------------------------------------------

  private fireChange(): void {
    bus.emit('filter:changed', { activeCount: this.getActiveFilterCount() })
    if (this.onChange) {
      this.onChange()
    }
  }
}

// ---------------------------------------------------------------------------
// Singleton instance
// ---------------------------------------------------------------------------

export const filterEngine = new FilterEngine()
