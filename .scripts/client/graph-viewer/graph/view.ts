/**
 * View manager -- maintains the fullGraph / viewGraph subgraph model.
 *
 * `fullGraph` is the persistent document (source of truth for save).
 * `viewGraph` is a transient lens -- either the fullGraph itself (when
 * unfiltered) or a subgraph containing only visible nodes+edges (after
 * "Apply Filters").
 *
 * Sigma always binds to `viewGraph`. FA2 always runs on `viewGraph`.
 * CRUD edits hit `viewGraph` and are synced back to `fullGraph` when
 * the view is filtered.
 */

import Graph from 'graphology'
import { filterEngine } from '../filter/engine'

// ---------------------------------------------------------------------------
// ViewManager
// ---------------------------------------------------------------------------

export class ViewManager {
  private fullGraph: Graph
  private viewGraph: Graph
  private filtered = false

  constructor(fullGraph: Graph) {
    this.fullGraph = fullGraph
    // Unfiltered: viewGraph IS the fullGraph (same reference, no copy)
    this.viewGraph = fullGraph
  }

  /** The persistent document -- always serialized on save. */
  getFullGraph(): Graph {
    return this.fullGraph
  }

  /** The graph currently bound to Sigma and FA2. */
  getViewGraph(): Graph {
    return this.viewGraph
  }

  /** Whether a subgraph filter is currently applied. */
  isViewFiltered(): boolean {
    return this.filtered
  }

  // -------------------------------------------------------------------------
  // Filter lifecycle
  // -------------------------------------------------------------------------

  /**
   * Apply current filter state: build a subgraph from fullGraph containing
   * only the nodes that pass all active filters and edges whose both
   * endpoints are present and whose edge type is enabled.
   *
   * Positions from the current viewGraph are synced to fullGraph first so
   * that any FA2 / drag movements are preserved.
   *
   * @returns The new viewGraph (a fresh Graphology instance).
   */
  applyFilters(): Graph {
    // Preserve positions from the outgoing view
    this.syncPositionsToFull()

    const sub = new Graph()

    // Copy graph-level attributes (metadata)
    sub.replaceAttributes({ ...this.fullGraph.getAttributes() })

    // Add visible nodes
    this.fullGraph.forEachNode((nodeId, attrs) => {
      if (filterEngine.isNodeVisible(nodeId, attrs)) {
        sub.addNode(nodeId, { ...attrs })
      }
    })

    // Add edges where BOTH endpoints survived and edge type is enabled
    this.fullGraph.forEachEdge((edgeId, attrs, source, target) => {
      if (sub.hasNode(source) && sub.hasNode(target)) {
        const sourceVisible = true // already in subgraph
        const targetVisible = true
        if (filterEngine.isEdgeVisible(edgeId, attrs, sourceVisible, targetVisible)) {
          sub.addEdgeWithKey(edgeId, source, target, { ...attrs })
        }
      }
    })

    this.viewGraph = sub
    this.filtered = true
    return sub
  }

  /**
   * Clear the subgraph filter: merge positions from the current viewGraph
   * back into fullGraph, then point viewGraph at fullGraph again.
   *
   * @returns fullGraph (now also the viewGraph).
   */
  clearFilters(): Graph {
    this.syncPositionsToFull()
    this.viewGraph = this.fullGraph
    this.filtered = false
    return this.viewGraph
  }

  // -------------------------------------------------------------------------
  // Position sync
  // -------------------------------------------------------------------------

  /**
   * Write node positions from the current viewGraph back into fullGraph.
   *
   * This is a no-op when unfiltered (same reference). Call before:
   * - applying new filters (preserves drag / FA2 positions)
   * - clearing filters
   * - saving the document
   */
  syncPositionsToFull(): void {
    if (!this.filtered) return

    this.viewGraph.forEachNode((nodeId, attrs) => {
      if (this.fullGraph.hasNode(nodeId)) {
        if (attrs.x !== undefined) {
          this.fullGraph.setNodeAttribute(nodeId, 'x', attrs.x)
        }
        if (attrs.y !== undefined) {
          this.fullGraph.setNodeAttribute(nodeId, 'y', attrs.y)
        }
      }
    })
  }

  // -------------------------------------------------------------------------
  // CRUD sync  (viewGraph -> fullGraph)
  //
  // These are called by the wiring layer (main.ts) after a CRUD operation
  // mutates the viewGraph. When unfiltered, fullGraph IS viewGraph so the
  // sync methods are no-ops.
  // -------------------------------------------------------------------------

  syncAddNode(nodeId: string, attrs: Record<string, unknown>): void {
    if (!this.filtered) return
    if (!this.fullGraph.hasNode(nodeId)) {
      this.fullGraph.addNode(nodeId, { ...attrs })
    }
  }

  syncRemoveNode(nodeId: string): void {
    if (!this.filtered) return
    if (this.fullGraph.hasNode(nodeId)) {
      this.fullGraph.dropNode(nodeId) // cascades edges
    }
  }

  syncAddEdge(
    edgeId: string,
    source: string,
    target: string,
    attrs: Record<string, unknown>
  ): void {
    if (!this.filtered) return
    if (!this.fullGraph.hasEdge(edgeId)) {
      // Ensure both endpoints exist in fullGraph
      if (this.fullGraph.hasNode(source) && this.fullGraph.hasNode(target)) {
        this.fullGraph.addEdgeWithKey(edgeId, source, target, { ...attrs })
      }
    }
  }

  syncRemoveEdge(edgeId: string): void {
    if (!this.filtered) return
    if (this.fullGraph.hasEdge(edgeId)) {
      this.fullGraph.dropEdge(edgeId)
    }
  }

  syncUpdateNodeAttribute(nodeId: string, key: string, value: unknown): void {
    if (!this.filtered) return
    if (this.fullGraph.hasNode(nodeId)) {
      this.fullGraph.setNodeAttribute(nodeId, key, value)
    }
  }

  // -------------------------------------------------------------------------
  // Full-graph replacement (used when loading a new graph via file picker)
  // -------------------------------------------------------------------------

  /**
   * Replace the underlying fullGraph with a new instance and reset the
   * view to unfiltered.
   */
  replaceFullGraph(newFull: Graph): void {
    this.fullGraph = newFull
    this.viewGraph = newFull
    this.filtered = false
  }
}
