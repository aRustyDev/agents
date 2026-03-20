/**
 * Graph Viewer -- Client entry point.
 *
 * Wires together all modules: state, graph loading, Sigma rendering,
 * interaction handlers, layout manager, WebSocket, and UI components.
 *
 * Architecture:
 *   fullGraph (Graphology)  <- source of truth, always in memory
 *       | filter + "Apply"
 *   viewGraph (Graphology)  <- subgraph bound to Sigma + FA2
 *
 * When no filter is applied, viewGraph IS fullGraph (same reference).
 * Save always serializes fullGraph. CRUD edits viewGraph and syncs to
 * fullGraph via ViewManager.
 *
 * This runs in the browser. It cannot import from `../../lib/` (Bun APIs).
 */

import './styles.css'

import type Graph from 'graphology'
import Sigma from 'sigma'
import { filterEngine } from './filter/engine'
import { createEdgeReducer, createNodeReducer } from './filter/reducers'
import { fetchGraph, fetchGraphList } from './graph/loader'
import { buildLockFile } from './graph/serializer'
import { ViewManager } from './graph/view'
import {
  addEdge,
  addNode,
  EDGE_COLORS,
  EDGE_SIZES,
  EDGE_TYPES,
  NODE_COLORS,
  NODE_TYPES,
  removeNode,
} from './interaction/crud'
import { setupDragHandlers } from './interaction/drag'
import { setupSelectionHandlers } from './interaction/selection'
import { hideHelp, isHelpVisible, toggleHelp } from './interaction/shortcuts'
import { type Command, undoManager } from './interaction/undo'
import { LayoutManager } from './layout/manager'
import { bus } from './state/events'
import { store } from './state/store'
import { mountControls } from './ui/controls'
import { mountSidebar } from './ui/sidebar'
import { mountStatusBar } from './ui/status'
import { initToastSystem, showToast } from './ui/toast'

// ---------------------------------------------------------------------------
// WebSocket with exponential backoff
// ---------------------------------------------------------------------------

function connectWebSocket(): void {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws`

  let reconnectDelay = 1000
  const MAX_DELAY = 30000

  function connect(): void {
    const ws = new WebSocket(wsUrl)

    ws.addEventListener('open', () => {
      store.set('wsConnected', true)
      bus.emit('ws:connected')
      reconnectDelay = 1000 // Reset backoff on successful connection
    })

    ws.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(String(event.data))

        // File change event from the server watcher
        if (data.type && typeof data.file === 'string') {
          bus.emit('ws:file-changed', {
            type: data.type,
            file: data.file,
            graphId: data.graphId,
          })
        }
      } catch {
        // Non-JSON messages (e.g., "hello" from spike server) -- ignore
      }
    })

    ws.addEventListener('close', () => {
      store.set('wsConnected', false)
      bus.emit('ws:disconnected')

      // Reconnect with exponential backoff
      setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, MAX_DELAY)
        connect()
      }, reconnectDelay)
    })

    ws.addEventListener('error', () => {
      // The close event will fire after this, triggering reconnect
      ws.close()
    })
  }

  connect()
}

// ---------------------------------------------------------------------------
// Git status polling
// ---------------------------------------------------------------------------

async function pollGitStatus(): Promise<void> {
  try {
    const res = await fetch('/api/git/status')
    if (res.ok) {
      const data = await res.json()
      store.set('gitStatus', data.dirty ? 'dirty' : 'clean')
    } else {
      store.set('gitStatus', 'unknown')
    }
  } catch {
    store.set('gitStatus', 'unknown')
  }
}

// ---------------------------------------------------------------------------
// Sigma renderer factory
// ---------------------------------------------------------------------------

/** Sigma settings shared by every renderer instance. */
const SIGMA_SETTINGS = {
  renderEdgeLabels: false,
  enableEdgeEvents: false,
  defaultNodeColor: '#6366f1',
  defaultEdgeColor: '#475569',
  labelColor: { color: '#e2e4eb' },
  labelFont: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  labelSize: 12,
  labelWeight: '400' as const,
  labelRenderedSizeThreshold: 4,
  zIndex: true,
  allowInvalidContainer: true,
} as const

/**
 * Create a new Sigma renderer bound to the given graph and container.
 * Attaches drag, selection, and filter-reducer handlers.
 *
 * Returns the renderer. Callers are responsible for calling
 * `renderer.kill()` before creating a replacement.
 */
function createRenderer(graph: Graph, container: HTMLElement): Sigma {
  const renderer = new Sigma(graph, container, { ...SIGMA_SETTINGS })

  // Wire filter reducers (preview: dims/hides nodes before "Apply")
  renderer.setSetting('nodeReducer', createNodeReducer(graph))
  renderer.setSetting('edgeReducer', createEdgeReducer(graph))

  // Interaction handlers
  setupDragHandlers(renderer, graph)
  setupSelectionHandlers(renderer, graph)

  return renderer
}

// ---------------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  // 1. Initialize toast system (connects to event bus)
  initToastSystem()

  // 2. Determine which graph to load
  let graphId: string

  try {
    const graphs = await fetchGraphList()
    if (graphs.length === 0) {
      showToast('No graphs available. Add graph files to .data/graphs/', 'warn', 0)
      return
    }
    graphId = graphs[0].id
  } catch (err) {
    showToast(`Failed to fetch graph list: ${String(err)}`, 'error', 0)
    return
  }

  // 3. Fetch graph data
  let loaded: Awaited<ReturnType<typeof fetchGraph>> | undefined
  try {
    loaded = await fetchGraph(graphId)
  } catch (err) {
    showToast(`Failed to load graph "${graphId}": ${String(err)}`, 'error', 0)
    return
  }

  const { graph: fullGraph } = loaded
  store.set('activeGraphId', graphId)

  // 4. Create ViewManager -- fullGraph is the document, viewGraph starts
  //    as fullGraph (same reference, no filter applied yet).
  const viewManager = new ViewManager(fullGraph)

  // 5. Create Sigma renderer -- wait for container to have real dimensions
  const container = document.getElementById('gv-graph-container')
  if (!container) {
    showToast('Missing #gv-graph-container element', 'error', 0)
    return
  }

  // Sigma needs pixel dimensions. Wait two animation frames for CSS Grid.
  await new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))

  console.log('[GraphViewer] Container size:', container.clientWidth, 'x', container.clientHeight)

  // Mutable references that get swapped when the view changes.
  let renderer: Sigma
  let layoutManager: LayoutManager

  try {
    renderer = createRenderer(viewManager.getViewGraph(), container)
    console.log('[GraphViewer] Sigma renderer created successfully')
  } catch (err) {
    console.error('[GraphViewer] Sigma constructor failed:', err)
    showToast(`Sigma failed to initialize: ${String(err)}`, 'error', 0)
    return
  }

  // 5b. Filter preview: when checkboxes change, refresh Sigma to dim/hide
  filterEngine.onFilterChange(() => {
    renderer.refresh()
  })

  // 6. Set up layout manager (default: ForceAtlas2)
  layoutManager = new LayoutManager(viewManager.getViewGraph())
  layoutManager.apply('forceatlas2')

  // -----------------------------------------------------------------------
  // Helper: rebuild renderer + layout for a new viewGraph
  // -----------------------------------------------------------------------

  function rebindView(newGraph: Graph): void {
    // Deselect everything -- old node references are invalid in the new graph
    store.set('selectedNodes', new Set())
    store.set('selectedEdges', new Set())
    bus.emit('graph:all-deselected', undefined)

    // Tear down the old renderer and layout
    layoutManager.destroy()
    renderer.kill()

    // Stand up new renderer and layout on the new graph
    renderer = createRenderer(newGraph, container!)
    layoutManager = new LayoutManager(newGraph)
    layoutManager.apply('forceatlas2')

    // Re-wire the lock-file save (camera listener is on the new renderer)
    renderer.getCamera().on('updated', saveLockDebounced)

    // Fit the camera to the (potentially tighter) subgraph
    requestAnimationFrame(() => {
      renderer.getCamera().animatedReset({ duration: 300 })
    })

    console.log(
      `[GraphViewer] Rebound Sigma to graph (${newGraph.order} nodes, ${newGraph.size} edges)`
    )
  }

  // -----------------------------------------------------------------------
  // Filter apply / clear
  // -----------------------------------------------------------------------

  bus.on('filter:apply', () => {
    const newView = viewManager.applyFilters()
    rebindView(newView)
    showToast(`Applied filters: ${newView.order} nodes, ${newView.size} edges`, 'info', 3000)
  })

  bus.on('filter:clear-view', () => {
    filterEngine.clearAll()
    const full = viewManager.clearFilters()
    rebindView(full)
    showToast('Filters cleared -- showing full graph', 'info', 3000)
  })

  // -----------------------------------------------------------------------
  // CRUD + sync-back wiring
  // -----------------------------------------------------------------------

  // 7a. Double-click stage to add a node
  renderer.on('doubleClickStage', (event) => {
    const coords = renderer.viewportToGraph(event.event)

    const label = window.prompt('New node label:')
    if (!label || !label.trim()) return

    const nodeType = window.prompt(`Node type (${NODE_TYPES.join(', ')}):`, 'Concept')
    if (!nodeType || !NODE_TYPES.includes(nodeType as (typeof NODE_TYPES)[number])) {
      showToast(`Invalid node type. Valid types: ${NODE_TYPES.join(', ')}`, 'warn', 3000)
      return
    }

    const viewGraph = viewManager.getViewGraph()
    const nodeId = addNode(viewGraph, coords.x, coords.y, label.trim(), nodeType)
    viewManager.syncAddNode(nodeId, viewGraph.getNodeAttributes(nodeId))
    store.set('isDirty', true)

    const cmd: Command = {
      description: `Add node "${label.trim()}"`,
      execute() {
        const g = viewManager.getViewGraph()
        if (!g.hasNode(nodeId)) {
          g.addNode(nodeId, {
            label: label.trim(),
            nodeType,
            x: coords.x,
            y: coords.y,
            size: 8,
            color: NODE_COLORS[nodeType] ?? '#6366f1',
            properties: {},
          })
          viewManager.syncAddNode(nodeId, g.getNodeAttributes(nodeId))
          bus.emit('graph:node-added', { nodeId })
        }
      },
      undo() {
        const g = viewManager.getViewGraph()
        if (g.hasNode(nodeId)) {
          removeNode(g, nodeId)
          viewManager.syncRemoveNode(nodeId)
        }
      },
    }
    undoManager.push(cmd)

    showToast(`Added node "${label.trim()}"`, 'info', 2000)
  })

  // 7b. Shift+click to create edge between selected node and clicked node
  renderer.on('clickNode', (event) => {
    if (!event.event.original.shiftKey) return

    const selectedNodes = store.get('selectedNodes')
    if (selectedNodes.size !== 1) return

    const sourceId = selectedNodes.values().next().value as string
    const targetId = event.node

    const viewGraph = viewManager.getViewGraph()
    if (sourceId === targetId) return
    if (viewGraph.hasEdge(sourceId, targetId)) {
      showToast('Edge already exists between these nodes', 'warn', 2000)
      return
    }

    const edgeType = window.prompt(`Edge type (${EDGE_TYPES.join(', ')}):`, 'relates_to')
    if (!edgeType || !EDGE_TYPES.includes(edgeType as (typeof EDGE_TYPES)[number])) {
      showToast(`Invalid edge type. Valid types: ${EDGE_TYPES.join(', ')}`, 'warn', 3000)
      return
    }

    const edgeId = addEdge(viewGraph, sourceId, targetId, edgeType)
    viewManager.syncAddEdge(edgeId, sourceId, targetId, viewGraph.getEdgeAttributes(edgeId))
    store.set('isDirty', true)

    const cmd: Command = {
      description: `Add edge ${sourceId} -> ${targetId}`,
      execute() {
        const g = viewManager.getViewGraph()
        if (!g.hasEdge(edgeId) && g.hasNode(sourceId) && g.hasNode(targetId)) {
          g.addEdgeWithKey(edgeId, sourceId, targetId, {
            edgeType,
            label: edgeType,
            color: EDGE_COLORS[edgeType] ?? '#64748b',
            size: EDGE_SIZES[edgeType] ?? 1.5,
            properties: {},
          })
          viewManager.syncAddEdge(edgeId, sourceId, targetId, g.getEdgeAttributes(edgeId))
          bus.emit('graph:edge-added', { edgeId })
        }
      },
      undo() {
        const g = viewManager.getViewGraph()
        if (g.hasEdge(edgeId)) {
          g.dropEdge(edgeId)
          viewManager.syncRemoveEdge(edgeId)
          bus.emit('graph:edge-removed', { edgeId })
        }
      },
    }
    undoManager.push(cmd)

    showToast(`Added edge: ${edgeType}`, 'info', 2000)
  })

  // 7c. Keyboard shortcuts
  document.addEventListener('keydown', (event) => {
    const tag = (event.target as HTMLElement).tagName
    const isInputFocused = tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA'

    // --- Escape: always available (close help, deselect, close sidebar) ---
    if (event.key === 'Escape') {
      event.preventDefault()
      if (isHelpVisible()) {
        hideHelp()
        return
      }
      // Deselect all nodes/edges
      store.set('selectedNodes', new Set())
      store.set('selectedEdges', new Set())
      bus.emit('graph:all-deselected', undefined)
      // Close sidebar inspector
      const sidebar = document.getElementById('gv-sidebar')
      if (sidebar) sidebar.classList.remove('gv-sidebar--open')
      return
    }

    // --- Ctrl+S / Cmd+S: save (works even in inputs) ---
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
      event.preventDefault()
      const saveBtn = document.querySelector<HTMLButtonElement>('.gv-toolbar__btn--save')
      if (saveBtn) saveBtn.click()
      return
    }

    // Remaining shortcuts are ignored when an input/select is focused
    if (isInputFocused) return

    // --- Delete key: delete selected items ---
    if (event.key === 'Delete' || event.key === 'Backspace') {
      const selectedNodes = store.get('selectedNodes')
      const selectedEdges = store.get('selectedEdges')
      if (selectedNodes.size > 0 || selectedEdges.size > 0) {
        event.preventDefault()
        const deleteBtn = document.querySelector<HTMLButtonElement>('.gv-toolbar__btn--danger')
        if (deleteBtn) deleteBtn.click()
      }
    }

    // --- Ctrl+Z / Cmd+Z: Undo ---
    if ((event.ctrlKey || event.metaKey) && event.key === 'z' && !event.shiftKey) {
      event.preventDefault()
      if (undoManager.undo()) {
        showToast('Undo', 'info', 1500)
      }
    }

    // --- Ctrl+Shift+Z / Cmd+Shift+Z: Redo ---
    if ((event.ctrlKey || event.metaKey) && event.key === 'z' && event.shiftKey) {
      event.preventDefault()
      if (undoManager.redo()) {
        showToast('Redo', 'info', 1500)
      }
    }

    // --- Ctrl+Y / Cmd+Y: Redo (alternative) ---
    if ((event.ctrlKey || event.metaKey) && event.key === 'y') {
      event.preventDefault()
      if (undoManager.redo()) {
        showToast('Redo', 'info', 1500)
      }
    }

    // --- F: fit graph to viewport ---
    if (event.key === 'f' || event.key === 'F') {
      if (!event.ctrlKey && !event.metaKey && !event.altKey) {
        event.preventDefault()
        renderer.getCamera().animatedReset({ duration: 300 })
      }
    }

    // --- /: focus the search input ---
    if (event.key === '/') {
      event.preventDefault()
      const searchInput = document.querySelector<HTMLInputElement>('.gv-filter__search')
      if (searchInput) {
        // Open the sidebar if it is closed so the search input is visible
        const sidebar = document.getElementById('gv-sidebar')
        if (sidebar && !sidebar.classList.contains('gv-sidebar--open')) {
          sidebar.classList.add('gv-sidebar--open')
        }
        searchInput.focus()
      }
    }

    // --- ?: toggle help overlay ---
    if (event.key === '?') {
      event.preventDefault()
      toggleHelp()
    }
  })

  // -----------------------------------------------------------------------
  // 7. Mount UI
  // -----------------------------------------------------------------------

  const toolbar = document.getElementById('gv-toolbar')
  if (toolbar) {
    mountControls(toolbar, layoutManager, renderer, viewManager.getViewGraph(), viewManager)
  }

  const statusBar = document.getElementById('gv-status-bar')
  if (statusBar) {
    mountStatusBar(statusBar, viewManager.getViewGraph())
  }

  const sidebar = document.getElementById('gv-sidebar')
  if (sidebar) {
    mountSidebar(sidebar, viewManager.getViewGraph())
  }

  // -----------------------------------------------------------------------
  // 8. Track dirty state on graph mutations (viewGraph)
  // -----------------------------------------------------------------------

  const viewGraph = viewManager.getViewGraph()
  viewGraph.on('nodeAdded', () => store.set('isDirty', true))
  viewGraph.on('edgeAdded', () => store.set('isDirty', true))
  viewGraph.on('nodeDropped', () => store.set('isDirty', true))
  viewGraph.on('edgeDropped', () => store.set('isDirty', true))
  viewGraph.on('nodeAttributesUpdated', () => store.set('isDirty', true))

  // -----------------------------------------------------------------------
  // 9. Auto-save lock file (debounced, best-effort)
  //
  // Always uses fullGraph (after syncing positions) so that the lock file
  // contains positions for ALL nodes, not just the filtered subset.
  // -----------------------------------------------------------------------

  let lockSaveTimer: ReturnType<typeof setTimeout> | null = null

  function saveLockDebounced(): void {
    if (lockSaveTimer) clearTimeout(lockSaveTimer)
    lockSaveTimer = setTimeout(async () => {
      const activeId = store.get('activeGraphId')
      if (!activeId) return

      // Sync positions from the viewGraph back to fullGraph
      viewManager.syncPositionsToFull()

      const camera = renderer.getCamera().getState()
      const lockData = buildLockFile(
        viewManager.getFullGraph(),
        activeId,
        camera,
        layoutManager.getCurrent()
      )

      try {
        await fetch(`/api/graphs/${encodeURIComponent(activeId)}/lock`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(lockData),
        })
      } catch {
        // Silent -- lock saves are best-effort
      }
    }, 2000)
  }

  bus.on('layout:stopped', saveLockDebounced)
  bus.on('layout:changed', saveLockDebounced)
  renderer.getCamera().on('updated', saveLockDebounced)

  // -----------------------------------------------------------------------
  // 10. Clear undo history on graph load/switch, then emit loaded event
  // -----------------------------------------------------------------------

  undoManager.clear()

  bus.on('graph:loaded', () => {
    undoManager.clear()
  })

  bus.emit('graph:loaded', {
    graphId,
    nodeCount: fullGraph.order,
    edgeCount: fullGraph.size,
  })

  showToast(`Loaded "${graphId}" (${fullGraph.order} nodes, ${fullGraph.size} edges)`, 'info', 3000)

  // -----------------------------------------------------------------------
  // 10b. Show empty graph state if no nodes
  // -----------------------------------------------------------------------

  function updateEmptyState(): void {
    const existing = container?.querySelector('.gv-empty-state')
    if (viewManager.getViewGraph().order === 0) {
      if (!existing) {
        const emptyMsg = document.createElement('div')
        emptyMsg.className = 'gv-empty-state'
        emptyMsg.textContent = 'Double-click to create a node'
        container?.appendChild(emptyMsg)
      }
    } else if (existing) {
      existing.remove()
    }
  }

  updateEmptyState()
  bus.on('graph:node-added', updateEmptyState)
  bus.on('graph:node-removed', updateEmptyState)
  bus.on('graph:loaded', updateEmptyState)

  // -----------------------------------------------------------------------
  // 11. Connect WebSocket for live reload
  // -----------------------------------------------------------------------

  connectWebSocket()

  bus.on('ws:file-changed', ({ file, graphId: changedGraphId }) => {
    const activeId = store.get('activeGraphId')
    if (changedGraphId === activeId || !changedGraphId) {
      if (store.get('isDirty')) {
        showToast(
          'Graph modified externally while you have unsaved changes. Save to keep your changes, or reload to get the external version.',
          'warn',
          0
        )
      } else {
        showToast(`Graph file changed: ${file}. Click to reload.`, 'warn', 8000)
      }
    }
  })

  // -----------------------------------------------------------------------
  // 12. Poll git status
  // -----------------------------------------------------------------------

  pollGitStatus()
  setInterval(pollGitStatus, 15000)
}

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

main().catch((err) => {
  console.error('[GraphViewer] Fatal error during initialization:', err)
})
