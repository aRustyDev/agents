/**
 * Status bar — displays connection info, graph stats, and git status.
 *
 * Renders into #gv-status-bar. Updates reactively via store subscriptions
 * and event bus listeners.
 */

import type Graph from 'graphology'
import { bus } from '../state/events'
import { store } from '../state/store'

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

/**
 * Mount the status bar into the #gv-status-bar element.
 *
 * @param container - The status bar DOM element.
 * @param graph - The Graphology graph instance (for node/edge counts).
 */
export function mountStatusBar(container: HTMLElement, graph: Graph): void {
  container.innerHTML = ''
  container.classList.add('gv-status-bar')

  // --- WebSocket indicator ---
  const wsIndicator = document.createElement('span')
  wsIndicator.className = 'gv-status-bar__item gv-status-bar__ws'
  updateWsIndicator(wsIndicator, store.get('wsConnected'))
  container.appendChild(wsIndicator)

  // --- Git status indicator ---
  const gitIndicator = document.createElement('span')
  gitIndicator.className = 'gv-status-bar__item gv-status-bar__git'
  updateGitIndicator(gitIndicator, store.get('gitStatus'))
  container.appendChild(gitIndicator)

  // --- Node/Edge count ---
  const statsEl = document.createElement('span')
  statsEl.className = 'gv-status-bar__item gv-status-bar__stats'
  updateStats(statsEl, graph)
  container.appendChild(statsEl)

  // --- Layout indicator ---
  const layoutEl = document.createElement('span')
  layoutEl.className = 'gv-status-bar__item gv-status-bar__layout'
  updateLayoutIndicator(layoutEl, store.get('activeLayout'), store.get('layoutRunning'))
  container.appendChild(layoutEl)

  // --- Selection count ---
  const selectionEl = document.createElement('span')
  selectionEl.className = 'gv-status-bar__item gv-status-bar__selection'
  updateSelectionCount(selectionEl, store.get('selectedNodes').size)
  container.appendChild(selectionEl)

  // --- Reactive updates via store subscription ---
  store.subscribe((_state, key) => {
    switch (key) {
      case 'wsConnected':
        updateWsIndicator(wsIndicator, store.get('wsConnected'))
        break
      case 'gitStatus':
        updateGitIndicator(gitIndicator, store.get('gitStatus'))
        break
      case 'selectedNodes':
        updateSelectionCount(selectionEl, store.get('selectedNodes').size)
        break
      case 'layoutRunning':
      case 'activeLayout':
        updateLayoutIndicator(layoutEl, store.get('activeLayout'), store.get('layoutRunning'))
        break
    }
  })

  // --- Update stats on graph changes ---
  bus.on('graph:loaded', () => {
    updateStats(statsEl, graph)
  })
}

// ---------------------------------------------------------------------------
// Update helpers
// ---------------------------------------------------------------------------

function updateWsIndicator(el: HTMLElement, connected: boolean): void {
  const dot = connected ? 'gv-dot--green' : 'gv-dot--red'
  const label = connected ? 'WS Connected' : 'WS Disconnected'
  el.innerHTML = `<span class="gv-dot ${dot}"></span> ${label}`
}

function updateGitIndicator(el: HTMLElement, status: 'clean' | 'dirty' | 'unknown'): void {
  const dotClass =
    status === 'clean' ? 'gv-dot--green' : status === 'dirty' ? 'gv-dot--yellow' : 'gv-dot--gray'
  const label =
    status === 'clean' ? 'Git: clean' : status === 'dirty' ? 'Git: dirty' : 'Git: unknown'
  el.innerHTML = `<span class="gv-dot ${dotClass}"></span> ${label}`
}

function updateStats(el: HTMLElement, graph: Graph): void {
  const nodes = graph.order
  const edges = graph.size
  el.textContent = `Nodes: ${nodes} | Edges: ${edges}`
}

function updateLayoutIndicator(el: HTMLElement, layout: string, running: boolean): void {
  const runLabel = running ? ' (running)' : ''
  el.textContent = `Layout: ${layout}${runLabel}`
}

function updateSelectionCount(el: HTMLElement, count: number): void {
  el.textContent = count > 0 ? `Selected: ${count}` : ''
}
