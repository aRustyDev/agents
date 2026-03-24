/**
 * Node drag handler for Sigma.js.
 *
 * Implements the standard Sigma drag pattern:
 * 1. `downNode` — begin tracking the dragged node, disable camera
 * 2. `mousemovebody` — update node position in Graphology
 * 3. `mouseup` — release, re-enable camera
 *
 * Communicates through the event bus rather than directly importing
 * other modules.
 */

import type Graph from 'graphology'
import type Sigma from 'sigma'
import { store } from '../state/store'

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

interface DragState {
  /** ID of the node being dragged, or null. */
  draggedNode: string | null
  /** Whether the mouse is currently down on a node. */
  isDragging: boolean
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

/**
 * Attach drag interaction handlers to a Sigma renderer.
 *
 * @param renderer - The Sigma renderer instance.
 * @param graph - The Graphology graph instance.
 */
export function setupDragHandlers(renderer: Sigma, graph: Graph): void {
  const state: DragState = {
    draggedNode: null,
    isDragging: false,
  }

  // Track mouse position for coordinate conversion
  const mouseCaptor = renderer.getMouseCaptor()
  const camera = renderer.getCamera()

  // --- downNode: start drag ---
  renderer.on('downNode', (event) => {
    state.draggedNode = event.node
    state.isDragging = true

    // Disable camera movement while dragging
    camera.disable()

    // Mark the graph as dirty since positions are changing
    store.set('isDirty', true)
  })

  // --- mousemovebody: update position during drag ---
  mouseCaptor.on('mousemovebody', (event) => {
    if (!state.isDragging || !state.draggedNode) return

    // Convert viewport coordinates to graph coordinates
    const pos = renderer.viewportToGraph(event)

    graph.setNodeAttribute(state.draggedNode, 'x', pos.x)
    graph.setNodeAttribute(state.draggedNode, 'y', pos.y)

    // Prevent sigma from handling the event for camera panning
    event.preventSigmaDefault()
    event.original.preventDefault()
    event.original.stopPropagation()
  })

  // --- mouseup: end drag ---
  mouseCaptor.on('mouseup', () => {
    if (state.isDragging && state.draggedNode) {
      // Fix the node position so ForceAtlas2 does not move it
      if (graph.hasNode(state.draggedNode)) {
        graph.setNodeAttribute(state.draggedNode, 'fixed', true)
      }
    }

    state.draggedNode = null
    state.isDragging = false

    // Re-enable camera
    camera.enable()
  })

  // --- mousedown (on stage, not on a node): nothing to do, let camera handle it ---
}
