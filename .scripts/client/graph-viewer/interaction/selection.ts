/**
 * Node selection handler for Sigma.js.
 *
 * Click a node to select it. Click the stage (background) to deselect all.
 * Selected nodes get a highlighted color and increased size.
 *
 * Communicates selection state through the event bus and store.
 */

import type Graph from 'graphology'
import type Sigma from 'sigma'
import { SELECTED_SIZE_MULTIPLIER } from '../graph/loader'
import { bus } from '../state/events'
import { store } from '../state/store'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Color applied to selected nodes. */
const SELECTED_COLOR = '#fbbf24' // amber-400

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

/**
 * Attach selection interaction handlers to a Sigma renderer.
 *
 * @param renderer - The Sigma renderer instance.
 * @param graph - The Graphology graph instance.
 */
export function setupSelectionHandlers(renderer: Sigma, graph: Graph): void {
  // Store original colors/sizes so we can restore them on deselect
  const originalAttributes = new Map<string, { color: string; size: number }>()

  // --- clickNode: select node ---
  renderer.on('clickNode', (event) => {
    const nodeId = event.node
    const selectedNodes = store.get('selectedNodes')

    // If already selected, deselect it
    if (selectedNodes.has(nodeId)) {
      deselectNode(nodeId, graph)
      bus.emit('graph:node-deselected', { nodeId })
      return
    }

    // Select the node
    selectNode(nodeId, graph)

    const attrs = graph.getNodeAttributes(nodeId)
    bus.emit('graph:node-selected', {
      nodeId,
      attributes: { ...attrs },
    })
  })

  // --- clickStage: deselect all ---
  renderer.on('clickStage', () => {
    deselectAll(graph)
    bus.emit('graph:all-deselected', undefined)
  })

  // --- enterNode / leaveNode: hover state ---
  renderer.on('enterNode', (event) => {
    store.set('hoveredNode', event.node)
    bus.emit('graph:node-hovered', { nodeId: event.node })
    renderer.getContainer().style.cursor = 'pointer'
  })

  renderer.on('leaveNode', (event) => {
    store.set('hoveredNode', null)
    bus.emit('graph:node-unhovered', { nodeId: event.node })
    renderer.getContainer().style.cursor = 'default'
  })

  // --- Helper functions ---

  function selectNode(nodeId: string, g: Graph): void {
    if (!g.hasNode(nodeId)) return

    // Store original attributes for restoration
    if (!originalAttributes.has(nodeId)) {
      originalAttributes.set(nodeId, {
        color: g.getNodeAttribute(nodeId, 'color') as string,
        size: g.getNodeAttribute(nodeId, 'size') as number,
      })
    }

    // Apply selection visual
    g.setNodeAttribute(nodeId, 'color', SELECTED_COLOR)
    const currentSize = g.getNodeAttribute(nodeId, 'size') as number
    g.setNodeAttribute(nodeId, 'size', currentSize * SELECTED_SIZE_MULTIPLIER)

    // Update store
    const selected = new Set(store.get('selectedNodes'))
    selected.add(nodeId)
    store.set('selectedNodes', selected)
  }

  function deselectNode(nodeId: string, g: Graph): void {
    if (!g.hasNode(nodeId)) return

    // Restore original attributes
    const original = originalAttributes.get(nodeId)
    if (original) {
      g.setNodeAttribute(nodeId, 'color', original.color)
      g.setNodeAttribute(nodeId, 'size', original.size)
      originalAttributes.delete(nodeId)
    }

    // Update store
    const selected = new Set(store.get('selectedNodes'))
    selected.delete(nodeId)
    store.set('selectedNodes', selected)
  }

  function deselectAll(g: Graph): void {
    const selected = store.get('selectedNodes')
    for (const nodeId of selected) {
      if (!g.hasNode(nodeId)) continue
      const original = originalAttributes.get(nodeId)
      if (original) {
        g.setNodeAttribute(nodeId, 'color', original.color)
        g.setNodeAttribute(nodeId, 'size', original.size)
        originalAttributes.delete(nodeId)
      }
    }

    store.set('selectedNodes', new Set())
  }
}
