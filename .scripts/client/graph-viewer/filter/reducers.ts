/**
 * Sigma node/edge reducers that apply filter visibility.
 *
 * These are passed to Sigma's `settings.nodeReducer` and
 * `settings.edgeReducer`. They run on EVERY frame for EVERY node/edge,
 * so they must be kept as fast as possible.
 *
 * The reducers delegate to FilterEngine for the actual predicate logic,
 * and set `hidden: true` on items that should not be rendered.
 */

import type Graph from 'graphology'
import type { EdgeDisplayData, NodeDisplayData } from 'sigma/types'
import { filterEngine } from './engine'

// ---------------------------------------------------------------------------
// Node reducer
// ---------------------------------------------------------------------------

/**
 * Create a nodeReducer function that hides nodes excluded by active
 * filters, and highlights nodes matching the current search query.
 */
export function createNodeReducer(
  _graph: Graph
): (node: string, data: Record<string, unknown>) => Partial<NodeDisplayData> {
  return (node: string, data: Record<string, unknown>): Partial<NodeDisplayData> => {
    if (!filterEngine.isNodeVisible(node, data)) {
      return { ...data, hidden: true } as Partial<NodeDisplayData>
    }

    // If a search query is active and this node matches, highlight it
    const query = filterEngine.getState().searchQuery
    if (query) {
      const label = String(data.label ?? '')
      if (label.toLowerCase().includes(query.toLowerCase())) {
        return { ...data, highlighted: true } as Partial<NodeDisplayData>
      }
    }

    return data as Partial<NodeDisplayData>
  }
}

// ---------------------------------------------------------------------------
// Edge reducer
// ---------------------------------------------------------------------------

/**
 * Create an edgeReducer function that hides edges whose type is
 * disabled or whose source/target nodes are hidden.
 */
export function createEdgeReducer(
  graph: Graph
): (edge: string, data: Record<string, unknown>) => Partial<EdgeDisplayData> {
  return (edge: string, data: Record<string, unknown>): Partial<EdgeDisplayData> => {
    const source = graph.source(edge)
    const target = graph.target(edge)
    const sourceAttrs = graph.getNodeAttributes(source)
    const targetAttrs = graph.getNodeAttributes(target)
    const sourceVisible = filterEngine.isNodeVisible(source, sourceAttrs)
    const targetVisible = filterEngine.isNodeVisible(target, targetAttrs)

    if (!filterEngine.isEdgeVisible(edge, data, sourceVisible, targetVisible)) {
      return { ...data, hidden: true } as Partial<EdgeDisplayData>
    }

    return data as Partial<EdgeDisplayData>
  }
}
