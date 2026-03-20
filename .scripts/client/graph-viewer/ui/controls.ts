/**
 * Toolbar controls -- layout selector, action buttons, file picker, and save.
 *
 * Renders into #gv-toolbar. Provides:
 * - Graph file picker (fetches list from /api/graphs)
 * - Layout algorithm selector (ForceAtlas2 / Circular / Random)
 * - Start/Stop toggle for ForceAtlas2
 * - Zoom controls
 * - Save button (serialize graph and PUT to API)
 *
 * Communicates via the event bus and store rather than importing
 * other modules directly.
 */

import type Graph from 'graphology'
import type Sigma from 'sigma'
import { filterEngine } from '../filter/engine'
import { fetchGraph, fetchGraphList } from '../graph/loader'
import { serializeGraph } from '../graph/serializer'
import type { ViewManager } from '../graph/view'
import { removeEdge, removeNode } from '../interaction/crud'
import { toggleHelp } from '../interaction/shortcuts'
import { type Command, undoManager } from '../interaction/undo'
import type { LayoutManager } from '../layout/manager'
import { LAYOUT_LABELS, LAYOUT_NAMES, type LayoutName } from '../layout/presets'
import { bus } from '../state/events'
import { store } from '../state/store'
import { showToast } from './toast'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/**
 * Callback invoked when the user selects a new graph from the file picker.
 * The caller is responsible for re-wiring the Sigma renderer and layout
 * manager to the new graph instance.
 */
export type OnGraphSwitched = (graphId: string, graph: Graph) => void

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

/**
 * Mount toolbar controls into the #gv-toolbar element.
 *
 * @param container - The toolbar DOM element.
 * @param layoutManager - The layout manager instance.
 * @param renderer - The Sigma renderer instance.
 * @param graph - The Graphology graph instance bound to the renderer (viewGraph).
 * @param viewManager - The ViewManager that owns full/view graph lifecycle.
 * @param onGraphSwitched - Callback when a new graph is loaded from the picker.
 */
export function mountControls(
  container: HTMLElement,
  layoutManager: LayoutManager,
  renderer: Sigma,
  graph: Graph,
  viewManager?: ViewManager,
  onGraphSwitched?: OnGraphSwitched
): void {
  container.innerHTML = ''
  container.classList.add('gv-toolbar')

  // --- Graph file picker group ---
  const graphGroup = document.createElement('div')
  graphGroup.className = 'gv-toolbar__group'

  const graphLabel = document.createElement('span')
  graphLabel.className = 'gv-toolbar__label'
  graphLabel.textContent = 'Graph:'
  graphGroup.appendChild(graphLabel)

  const graphSelect = document.createElement('select')
  graphSelect.className = 'gv-toolbar__select'
  graphSelect.title = 'Select a graph to load'

  // Populate asynchronously
  populateGraphPicker(graphSelect)

  graphSelect.addEventListener('change', async () => {
    const selectedId = graphSelect.value
    if (!selectedId || selectedId === store.get('activeGraphId')) return

    graphSelect.disabled = true
    try {
      const loaded = await fetchGraph(selectedId)

      // Clear the current graph and copy from the loaded one
      graph.clear()
      graph.replaceAttributes(loaded.graph.getAttributes())

      loaded.graph.forEachNode((nodeId, attrs) => {
        graph.addNode(nodeId, { ...attrs })
      })
      loaded.graph.forEachEdge((edgeId, attrs, source, target) => {
        graph.addEdgeWithKey(edgeId, source, target, { ...attrs })
      })

      store.set('activeGraphId', selectedId)
      store.set('isDirty', false)

      // Re-apply layout
      layoutManager.apply(layoutManager.getCurrent())

      bus.emit('graph:loaded', {
        graphId: selectedId,
        nodeCount: graph.order,
        edgeCount: graph.size,
      })

      showToast(`Loaded "${selectedId}" (${graph.order} nodes, ${graph.size} edges)`, 'info', 3000)

      if (onGraphSwitched) {
        onGraphSwitched(selectedId, graph)
      }
    } catch (err) {
      showToast(`Failed to load graph "${selectedId}": ${String(err)}`, 'error', 5000)
      // Restore the picker to the current active graph
      const currentId = store.get('activeGraphId')
      if (currentId) {
        graphSelect.value = currentId
      }
    } finally {
      graphSelect.disabled = false
    }
  })

  graphGroup.appendChild(graphSelect)
  container.appendChild(graphGroup)

  // --- Layout selector group ---
  const layoutGroup = document.createElement('div')
  layoutGroup.className = 'gv-toolbar__group'

  const layoutLabel = document.createElement('span')
  layoutLabel.className = 'gv-toolbar__label'
  layoutLabel.textContent = 'Layout:'
  layoutGroup.appendChild(layoutLabel)

  for (const name of LAYOUT_NAMES) {
    const btn = document.createElement('button')
    btn.className = 'gv-toolbar__btn'
    btn.textContent = LAYOUT_LABELS[name]
    btn.dataset.layout = name

    if (name === store.get('activeLayout')) {
      btn.classList.add('gv-toolbar__btn--active')
    }

    btn.addEventListener('click', () => {
      layoutManager.apply(name)
      updateActiveButton(container, name)
    })

    layoutGroup.appendChild(btn)
  }

  container.appendChild(layoutGroup)

  // --- FA2 toggle button ---
  const fa2Group = document.createElement('div')
  fa2Group.className = 'gv-toolbar__group'

  const toggleBtn = document.createElement('button')
  toggleBtn.className = 'gv-toolbar__btn gv-toolbar__btn--toggle'
  toggleBtn.textContent = layoutManager.isRunning() ? 'Stop FA2' : 'Start FA2'
  toggleBtn.title = 'Toggle ForceAtlas2 layout simulation'

  toggleBtn.addEventListener('click', () => {
    layoutManager.toggleFA2()
    toggleBtn.textContent = layoutManager.isRunning() ? 'Stop FA2' : 'Start FA2'
    toggleBtn.classList.toggle('gv-toolbar__btn--running', layoutManager.isRunning())
    updateActiveButton(container, 'forceatlas2')
  })

  fa2Group.appendChild(toggleBtn)
  container.appendChild(fa2Group)

  // --- Zoom controls ---
  const zoomGroup = document.createElement('div')
  zoomGroup.className = 'gv-toolbar__group'

  const zoomIn = document.createElement('button')
  zoomIn.className = 'gv-toolbar__btn'
  zoomIn.textContent = '+'
  zoomIn.title = 'Zoom in'
  zoomIn.addEventListener('click', () => {
    const camera = renderer.getCamera()
    camera.animatedZoom({ duration: 200 })
  })

  const zoomOut = document.createElement('button')
  zoomOut.className = 'gv-toolbar__btn'
  zoomOut.textContent = '-'
  zoomOut.title = 'Zoom out'
  zoomOut.addEventListener('click', () => {
    const camera = renderer.getCamera()
    camera.animatedUnzoom({ duration: 200 })
  })

  const zoomReset = document.createElement('button')
  zoomReset.className = 'gv-toolbar__btn'
  zoomReset.textContent = 'Fit'
  zoomReset.title = 'Reset zoom to fit all nodes'
  zoomReset.addEventListener('click', () => {
    const camera = renderer.getCamera()
    camera.animatedReset({ duration: 300 })
  })

  zoomGroup.appendChild(zoomIn)
  zoomGroup.appendChild(zoomOut)
  zoomGroup.appendChild(zoomReset)
  container.appendChild(zoomGroup)

  // --- Save button ---
  const saveGroup = document.createElement('div')
  saveGroup.className = 'gv-toolbar__group'

  const saveBtn = document.createElement('button')
  saveBtn.className = 'gv-toolbar__btn gv-toolbar__btn--save'
  saveBtn.textContent = 'Save'
  saveBtn.title = 'Save graph changes to the server'

  saveBtn.addEventListener('click', () => {
    handleSave(graph, saveBtn, viewManager)
  })

  saveGroup.appendChild(saveBtn)
  container.appendChild(saveGroup)

  // --- Edit actions group (Delete, Undo, Redo) ---
  const editGroup = document.createElement('div')
  editGroup.className = 'gv-toolbar__group'

  const deleteBtn = document.createElement('button')
  deleteBtn.className = 'gv-toolbar__btn gv-toolbar__btn--danger'
  deleteBtn.textContent = 'Delete'
  deleteBtn.title = 'Delete selected nodes and edges (Del)'
  deleteBtn.addEventListener('click', () => {
    handleDelete(graph)
  })

  const undoBtn = document.createElement('button')
  undoBtn.className = 'gv-toolbar__btn'
  undoBtn.textContent = 'Undo'
  undoBtn.title = 'Undo last action (Ctrl+Z)'
  undoBtn.disabled = !undoManager.canUndo()
  undoBtn.addEventListener('click', () => {
    if (undoManager.undo()) {
      showToast('Undo', 'info', 1500)
    }
    updateUndoRedoButtons(undoBtn, redoBtn)
  })

  const redoBtn = document.createElement('button')
  redoBtn.className = 'gv-toolbar__btn'
  redoBtn.textContent = 'Redo'
  redoBtn.title = 'Redo last undone action (Ctrl+Shift+Z)'
  redoBtn.disabled = !undoManager.canRedo()
  redoBtn.addEventListener('click', () => {
    if (undoManager.redo()) {
      showToast('Redo', 'info', 1500)
    }
    updateUndoRedoButtons(undoBtn, redoBtn)
  })

  const resetViewBtn = document.createElement('button')
  resetViewBtn.className = 'gv-toolbar__btn'
  resetViewBtn.textContent = 'Reset'
  resetViewBtn.title = 'Return to the full graph (undo Apply Filters)'
  resetViewBtn.addEventListener('click', () => {
    bus.emit('filter:clear-view')
  })

  editGroup.appendChild(deleteBtn)
  editGroup.appendChild(undoBtn)
  editGroup.appendChild(redoBtn)
  editGroup.appendChild(resetViewBtn)
  container.appendChild(editGroup)

  // --- Filter toggle group ---
  const filterGroup = document.createElement('div')
  filterGroup.className = 'gv-toolbar__group'

  const filterBtn = document.createElement('button')
  filterBtn.className = 'gv-toolbar__btn gv-toolbar__btn--filter'
  filterBtn.title = 'Toggle filter sidebar'

  const filterBtnLabel = document.createElement('span')
  filterBtnLabel.textContent = 'Filters'

  const filterBtnBadge = document.createElement('span')
  filterBtnBadge.className = 'gv-toolbar__filter-badge'
  filterBtnBadge.id = 'gv-toolbar-filter-badge'
  const initialCount = filterEngine.getActiveFilterCount()
  if (initialCount > 0) {
    filterBtnBadge.textContent = String(initialCount)
    filterBtnBadge.style.display = ''
  } else {
    filterBtnBadge.textContent = ''
    filterBtnBadge.style.display = 'none'
  }

  filterBtn.appendChild(filterBtnLabel)
  filterBtn.appendChild(filterBtnBadge)

  filterBtn.addEventListener('click', () => {
    const sidebar = document.getElementById('gv-sidebar')
    if (sidebar) {
      sidebar.classList.toggle('gv-sidebar--open')
    }
  })

  filterGroup.appendChild(filterBtn)
  container.appendChild(filterGroup)

  // --- Help button ---
  const helpGroup = document.createElement('div')
  helpGroup.className = 'gv-toolbar__group'

  const helpBtn = document.createElement('button')
  helpBtn.className = 'gv-toolbar__btn gv-toolbar__btn--help'
  helpBtn.textContent = '?'
  helpBtn.title = 'Keyboard shortcuts (?)'
  helpBtn.addEventListener('click', () => {
    toggleHelp()
  })

  helpGroup.appendChild(helpBtn)
  container.appendChild(helpGroup)

  // Update toolbar filter badge when filters change
  bus.on('filter:changed', ({ activeCount }) => {
    if (activeCount > 0) {
      filterBtnBadge.textContent = String(activeCount)
      filterBtnBadge.style.display = ''
      filterBtn.classList.add('gv-toolbar__btn--filter-active')
    } else {
      filterBtnBadge.textContent = ''
      filterBtnBadge.style.display = 'none'
      filterBtn.classList.remove('gv-toolbar__btn--filter-active')
    }
  })

  // Update undo/redo buttons when graph state changes
  const updateUndoRedoOnChange = () => {
    updateUndoRedoButtons(undoBtn, redoBtn)
  }
  bus.on('graph:node-added', updateUndoRedoOnChange)
  bus.on('graph:node-removed', updateUndoRedoOnChange)
  bus.on('graph:edge-added', updateUndoRedoOnChange)
  bus.on('graph:edge-removed', updateUndoRedoOnChange)
  bus.on('graph:node-updated', updateUndoRedoOnChange)

  // --- Update save button styling when dirty state changes ---
  store.subscribe((_state, key) => {
    if (key === 'isDirty') {
      const dirty = store.get('isDirty')
      saveBtn.classList.toggle('gv-toolbar__btn--dirty', dirty)
      saveBtn.textContent = dirty ? 'Save *' : 'Save'
    }
  })

  // --- Listen for layout events to update toggle button ---
  bus.on('layout:started', () => {
    toggleBtn.textContent = 'Stop FA2'
    toggleBtn.classList.add('gv-toolbar__btn--running')
  })

  bus.on('layout:stopped', () => {
    toggleBtn.textContent = 'Start FA2'
    toggleBtn.classList.remove('gv-toolbar__btn--running')
  })

  bus.on('layout:changed', ({ algorithm }) => {
    updateActiveButton(container, algorithm as LayoutName)
    // If switching away from FA2, update toggle button
    if (algorithm !== 'forceatlas2') {
      toggleBtn.textContent = 'Start FA2'
      toggleBtn.classList.remove('gv-toolbar__btn--running')
    }
  })
}

// ---------------------------------------------------------------------------
// Graph picker
// ---------------------------------------------------------------------------

/**
 * Fetch the graph list from the API and populate the select element.
 */
async function populateGraphPicker(select: HTMLSelectElement): Promise<void> {
  try {
    const graphs = await fetchGraphList()
    const activeId = store.get('activeGraphId')

    // Clear existing options
    select.innerHTML = ''

    for (const item of graphs) {
      const option = document.createElement('option')
      option.value = item.id
      option.textContent = item.label || item.id
      option.title = item.description || ''

      if (item.id === activeId) {
        option.selected = true
      }

      select.appendChild(option)
    }
  } catch (err) {
    console.error('[Controls] Failed to populate graph picker:', err)
    const fallback = document.createElement('option')
    fallback.value = ''
    fallback.textContent = '(failed to load)'
    fallback.disabled = true
    select.appendChild(fallback)
  }
}

// ---------------------------------------------------------------------------
// Save handler
// ---------------------------------------------------------------------------

/**
 * Serialize the current graph and PUT it to the API.
 *
 * When a ViewManager is provided, positions are synced from the viewGraph
 * back to the fullGraph before serializing the fullGraph (source of truth).
 */
async function handleSave(
  graph: Graph,
  saveBtn: HTMLButtonElement,
  viewManager?: ViewManager
): Promise<void> {
  const activeId = store.get('activeGraphId')
  if (!activeId) {
    showToast('No active graph to save', 'warn', 3000)
    return
  }

  saveBtn.disabled = true
  saveBtn.textContent = 'Saving...'

  try {
    // Always save the fullGraph (source of truth)
    const saveTarget = viewManager ? viewManager.getFullGraph() : graph
    if (viewManager) {
      viewManager.syncPositionsToFull()
    }
    const data = serializeGraph(saveTarget)

    const res = await fetch(`/api/graphs/${encodeURIComponent(activeId)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (res.ok) {
      store.set('isDirty', false)
      bus.emit('graph:saved', { graphId: activeId })
      showToast(`Saved "${activeId}" successfully`, 'info', 3000)
    } else if (res.status === 400) {
      // Validation error -- show details from the response body
      const body = await res.json().catch(() => ({ errors: ['Unknown validation error'] }))
      const messages = Array.isArray(body.errors)
        ? body.errors.join('; ')
        : String(body.message || body.error || 'Validation failed')
      bus.emit('graph:save-failed', { graphId: activeId, error: messages })
      showToast(`Validation error: ${messages}`, 'error', 6000)
    } else {
      const text = await res.text()
      bus.emit('graph:save-failed', { graphId: activeId, error: text })
      showToast(`Save failed (${res.status}): ${text}`, 'error', 5000)
    }
  } catch (err) {
    bus.emit('graph:save-failed', { graphId: activeId, error: String(err) })
    showToast(`Save failed: ${String(err)}`, 'error', 5000)
  } finally {
    saveBtn.disabled = false
    // Restore label based on current dirty state
    saveBtn.textContent = store.get('isDirty') ? 'Save *' : 'Save'
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function updateActiveButton(container: HTMLElement, active: LayoutName): void {
  const buttons = container.querySelectorAll<HTMLButtonElement>('.gv-toolbar__btn[data-layout]')
  for (const btn of buttons) {
    btn.classList.toggle('gv-toolbar__btn--active', btn.dataset.layout === active)
  }
}

// ---------------------------------------------------------------------------
// Delete handler
// ---------------------------------------------------------------------------

/**
 * Delete all selected nodes (with cascade) and selected edges.
 * Prompts for confirmation if more than 3 items would be deleted.
 */
function handleDelete(graph: Graph): void {
  const selectedNodes = store.get('selectedNodes')
  const selectedEdges = store.get('selectedEdges')
  const totalItems = selectedNodes.size + selectedEdges.size

  if (totalItems === 0) {
    showToast('Nothing selected to delete', 'warn', 2000)
    return
  }

  // Confirm if deleting many items
  if (totalItems > 3) {
    const confirmed = window.confirm(
      `Delete ${selectedNodes.size} node(s) and ${selectedEdges.size} edge(s)? This will also remove connected edges.`
    )
    if (!confirmed) return
  }

  // Collect undo data for all removals
  const undoOps: Array<
    | {
        type: 'node'
        nodeId: string
        attrs: Record<string, unknown>
        edges: Array<{
          id: string
          source: string
          target: string
          attrs: Record<string, unknown>
        }>
      }
    | {
        type: 'edge'
        edgeId: string
        source: string
        target: string
        attrs: Record<string, unknown>
      }
  > = []

  // Remove edges first (nodes will cascade their edges too)
  for (const edgeId of selectedEdges) {
    if (!graph.hasEdge(edgeId)) continue
    const data = removeEdge(graph, edgeId)
    undoOps.push({ type: 'edge', edgeId, ...data })
  }

  // Remove nodes (cascades connected edges)
  for (const nodeId of selectedNodes) {
    if (!graph.hasNode(nodeId)) continue
    const data = removeNode(graph, nodeId)
    undoOps.push({ type: 'node', nodeId, attrs: data.node, edges: data.edges })
  }

  store.set('selectedNodes', new Set())
  store.set('selectedEdges', new Set())
  store.set('isDirty', true)
  bus.emit('graph:all-deselected', undefined)

  const cmd: Command = {
    description: `Delete ${totalItems} item(s)`,
    execute() {
      // Re-delete: not safe to re-run since IDs may conflict, so this is a no-op.
      // The redo after undo restores then re-removes. We handle this by replaying removals.
      // However for simplicity, redo is handled by re-deleting the same IDs.
      // Since undo restores them, this is safe.
      for (const op of undoOps) {
        if (op.type === 'edge' && graph.hasEdge(op.edgeId)) {
          removeEdge(graph, op.edgeId)
        } else if (op.type === 'node' && graph.hasNode(op.nodeId)) {
          removeNode(graph, op.nodeId)
        }
      }
    },
    undo() {
      // Restore in reverse order: nodes first, then edges
      for (let i = undoOps.length - 1; i >= 0; i--) {
        const op = undoOps[i]
        if (op.type === 'node') {
          graph.addNode(op.nodeId, { ...op.attrs })
          // Restore edges that were cascade-deleted with this node
          for (const edge of op.edges) {
            if (
              !graph.hasEdge(edge.id) &&
              graph.hasNode(edge.source) &&
              graph.hasNode(edge.target)
            ) {
              graph.addEdgeWithKey(edge.id, edge.source, edge.target, {
                ...edge.attrs,
              })
            }
          }
        } else if (op.type === 'edge') {
          if (!graph.hasEdge(op.edgeId) && graph.hasNode(op.source) && graph.hasNode(op.target)) {
            graph.addEdgeWithKey(op.edgeId, op.source, op.target, {
              ...op.attrs,
            })
          }
        }
      }
    },
  }
  undoManager.push(cmd)

  showToast(`Deleted ${totalItems} item(s)`, 'info', 2000)
}

// ---------------------------------------------------------------------------
// Undo/Redo button state
// ---------------------------------------------------------------------------

function updateUndoRedoButtons(undoBtn: HTMLButtonElement, redoBtn: HTMLButtonElement): void {
  undoBtn.disabled = !undoManager.canUndo()
  redoBtn.disabled = !undoManager.canRedo()
}
