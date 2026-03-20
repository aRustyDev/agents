/**
 * Property inspector sidebar with integrated filter panel.
 *
 * The sidebar has two sections:
 * 1. **Filter panel** (always visible) — node type / edge type checkboxes,
 *    label search, and a clear-all button.
 * 2. **Property inspector** (visible when a node is selected) — editable
 *    node properties and connected edges list.
 *
 * The sidebar opens by default to show the filter panel. When a node is
 * selected, the property inspector section appears below the filters.
 * When no node is selected, only the filter panel is shown.
 *
 * All mutations go through the CRUD module and push undo commands.
 */

import type Graph from 'graphology'
import { filterEngine } from '../filter/engine'
import { EDGE_TYPES, NODE_COLORS, NODE_TYPES, updateNodeAttribute } from '../interaction/crud'
import { type Command, undoManager } from '../interaction/undo'
import { bus } from '../state/events'
import { store } from '../state/store'

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

/** Currently displayed node ID, or null if inspector is hidden. */
let activeNodeId: string | null = null

/** Reference to the sidebar container element. */
let sidebarEl: HTMLElement | null = null

/** Reference to the graph instance. */
let graphRef: Graph | null = null

/** Reference to the filter panel container (persists across inspector open/close). */
let filterPanelEl: HTMLElement | null = null

/** Reference to the inspector container (re-rendered on selection). */
let inspectorEl: HTMLElement | null = null

/** Debounce timer for the search input. */
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------

/**
 * Mount the sidebar system. Call once during initialization.
 *
 * @param container - The `#gv-sidebar` DOM element.
 * @param graph - The Graphology graph instance.
 */
export function mountSidebar(container: HTMLElement, graph: Graph): void {
  sidebarEl = container
  graphRef = graph

  // Sidebar is open by default to show the filter panel
  sidebarEl.classList.add('gv-sidebar--open')

  // Build the static filter panel
  filterPanelEl = buildFilterPanel()
  sidebarEl.appendChild(filterPanelEl)

  // Create the inspector container (initially empty)
  inspectorEl = document.createElement('div')
  inspectorEl.className = 'gv-sidebar__inspector'
  sidebarEl.appendChild(inspectorEl)

  // Listen for node selection
  bus.on('graph:node-selected', ({ nodeId }) => {
    openInspector(nodeId)
  })

  // Listen for deselection
  bus.on('graph:node-deselected', () => {
    closeInspector()
  })

  bus.on('graph:all-deselected', () => {
    closeInspector()
  })

  // If a node gets removed while the inspector is open for it
  bus.on('graph:node-removed', ({ nodeId }) => {
    if (activeNodeId === nodeId) {
      closeInspector()
    }
  })

  // Refresh inspector when node attributes are updated externally (e.g., undo)
  bus.on('graph:node-updated', ({ nodeId }) => {
    if (activeNodeId === nodeId) {
      openInspector(nodeId)
    }
  })

  // Update filter panel badge when filter count changes
  bus.on('filter:changed', () => {
    updateFilterBadge()
    updateFilterCheckboxes()
    updateSearchInput()
  })
}

// ---------------------------------------------------------------------------
// Filter Panel
// ---------------------------------------------------------------------------

function buildFilterPanel(): HTMLElement {
  const panel = document.createElement('div')
  panel.className = 'gv-filter'

  // --- Heading with badge ---
  const heading = document.createElement('div')
  heading.className = 'gv-filter__heading'

  const headingText = document.createElement('span')
  headingText.textContent = 'Filters'
  heading.appendChild(headingText)

  const badge = document.createElement('span')
  badge.className = 'gv-filter__badge'
  badge.id = 'gv-filter-badge'
  badge.textContent = ''
  badge.style.display = 'none'
  heading.appendChild(badge)

  panel.appendChild(heading)

  // --- Search input ---
  const searchInput = document.createElement('input')
  searchInput.className = 'gv-filter__search'
  searchInput.id = 'gv-filter-search'
  searchInput.type = 'text'
  searchInput.placeholder = 'Search labels...'
  searchInput.value = filterEngine.getState().searchQuery
  searchInput.addEventListener('input', () => {
    if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
    searchDebounceTimer = setTimeout(() => {
      filterEngine.setSearchQuery(searchInput.value)
    }, 200)
  })
  panel.appendChild(searchInput)

  // --- Node types group ---
  const nodeGroup = document.createElement('div')
  nodeGroup.className = 'gv-filter__group'

  const nodeGroupLabel = document.createElement('div')
  nodeGroupLabel.className = 'gv-filter__group-label'
  nodeGroupLabel.textContent = 'Node Types'
  nodeGroup.appendChild(nodeGroupLabel)

  const filterState = filterEngine.getState()

  for (const nodeType of NODE_TYPES) {
    const row = document.createElement('label')
    row.className = 'gv-filter__checkbox'

    const checkbox = document.createElement('input')
    checkbox.type = 'checkbox'
    checkbox.checked = filterState.enabledNodeTypes.has(nodeType)
    checkbox.dataset.filterNodeType = nodeType
    checkbox.addEventListener('change', () => {
      filterEngine.toggleNodeType(nodeType)
    })

    const colorDot = document.createElement('span')
    colorDot.className = 'gv-filter__color-dot'
    colorDot.style.background = NODE_COLORS[nodeType] ?? '#6366f1'

    const labelText = document.createElement('span')
    labelText.textContent = nodeType

    row.appendChild(checkbox)
    row.appendChild(colorDot)
    row.appendChild(labelText)
    nodeGroup.appendChild(row)
  }

  panel.appendChild(nodeGroup)

  // --- Edge types group ---
  const edgeGroup = document.createElement('div')
  edgeGroup.className = 'gv-filter__group'

  const edgeGroupLabel = document.createElement('div')
  edgeGroupLabel.className = 'gv-filter__group-label'
  edgeGroupLabel.textContent = 'Edge Types'
  edgeGroup.appendChild(edgeGroupLabel)

  for (const edgeType of EDGE_TYPES) {
    const row = document.createElement('label')
    row.className = 'gv-filter__checkbox'

    const checkbox = document.createElement('input')
    checkbox.type = 'checkbox'
    checkbox.checked = filterState.enabledEdgeTypes.has(edgeType)
    checkbox.dataset.filterEdgeType = edgeType
    checkbox.addEventListener('change', () => {
      filterEngine.toggleEdgeType(edgeType)
    })

    const labelText = document.createElement('span')
    labelText.textContent = edgeType

    row.appendChild(checkbox)
    row.appendChild(labelText)
    edgeGroup.appendChild(row)
  }

  panel.appendChild(edgeGroup)

  // --- Filter action buttons ---
  const btnRow = document.createElement('div')
  btnRow.style.display = 'flex'
  btnRow.style.gap = '6px'

  const clearBtn = document.createElement('button')
  clearBtn.className = 'gv-filter__clear'
  clearBtn.textContent = 'Clear'
  clearBtn.addEventListener('click', () => {
    filterEngine.clearAll()
  })
  btnRow.appendChild(clearBtn)

  const applyBtn = document.createElement('button')
  applyBtn.className = 'gv-filter__clear gv-filter__apply'
  applyBtn.textContent = 'Apply'
  applyBtn.title = 'Build a subgraph with only visible nodes. FA2 will run on the subgraph.'
  applyBtn.addEventListener('click', () => {
    bus.emit('filter:apply')
  })
  btnRow.appendChild(applyBtn)

  panel.appendChild(btnRow)

  return panel
}

/**
 * Update the badge next to "Filters" heading to show active filter count.
 */
function updateFilterBadge(): void {
  const badge = document.getElementById('gv-filter-badge')
  if (!badge) return

  const count = filterEngine.getActiveFilterCount()
  if (count > 0) {
    badge.textContent = String(count)
    badge.style.display = ''
  } else {
    badge.textContent = ''
    badge.style.display = 'none'
  }
}

/**
 * Sync checkbox states with the filter engine (e.g., after clearAll).
 */
function updateFilterCheckboxes(): void {
  if (!filterPanelEl) return

  const state = filterEngine.getState()

  const nodeCheckboxes = filterPanelEl.querySelectorAll<HTMLInputElement>(
    'input[data-filter-node-type]'
  )
  for (const cb of nodeCheckboxes) {
    cb.checked = state.enabledNodeTypes.has(cb.dataset.filterNodeType!)
  }

  const edgeCheckboxes = filterPanelEl.querySelectorAll<HTMLInputElement>(
    'input[data-filter-edge-type]'
  )
  for (const cb of edgeCheckboxes) {
    cb.checked = state.enabledEdgeTypes.has(cb.dataset.filterEdgeType!)
  }
}

/**
 * Sync search input with the filter engine (e.g., after clearAll).
 */
function updateSearchInput(): void {
  const searchInput = document.getElementById('gv-filter-search') as HTMLInputElement | null
  if (!searchInput) return

  const state = filterEngine.getState()
  if (searchInput.value !== state.searchQuery) {
    searchInput.value = state.searchQuery
  }
}

// ---------------------------------------------------------------------------
// Inspector Open / Close
// ---------------------------------------------------------------------------

function openInspector(nodeId: string): void {
  if (!sidebarEl || !graphRef || !inspectorEl) return
  if (!graphRef.hasNode(nodeId)) return

  activeNodeId = nodeId
  sidebarEl.classList.add('gv-sidebar--open')
  renderInspectorContent(nodeId)
}

function closeInspector(): void {
  if (!inspectorEl) return

  activeNodeId = null
  inspectorEl.innerHTML = ''
}

// ---------------------------------------------------------------------------
// Inspector Render
// ---------------------------------------------------------------------------

function renderInspectorContent(nodeId: string): void {
  if (!inspectorEl || !graphRef) return
  if (!graphRef.hasNode(nodeId)) return

  const graph = graphRef
  const attrs = graph.getNodeAttributes(nodeId)

  inspectorEl.innerHTML = ''

  // --- Title ---
  const title = document.createElement('div')
  title.className = 'gv-sidebar__title'
  title.textContent = 'Node Inspector'
  inspectorEl.appendChild(title)

  // --- Close button ---
  const closeBtn = document.createElement('button')
  closeBtn.className = 'gv-sidebar__close'
  closeBtn.textContent = '\u00d7'
  closeBtn.title = 'Close inspector'
  closeBtn.addEventListener('click', () => {
    // Deselect all to close inspector and clear selection state
    store.set('selectedNodes', new Set())
    bus.emit('graph:all-deselected', undefined)
  })
  title.appendChild(closeBtn)

  // --- ID (read-only) ---
  appendField(inspectorEl, 'ID', nodeId, true)

  // --- Label (editable) ---
  const labelInput = appendInputField(inspectorEl, 'Label', String(attrs.label ?? ''))
  labelInput.addEventListener('change', () => {
    const newLabel = labelInput.value.trim()
    if (!newLabel) {
      labelInput.value = String(attrs.label ?? '')
      return
    }
    const oldLabel = String(graph.getNodeAttribute(nodeId, 'label') ?? '')
    if (newLabel === oldLabel) return

    updateNodeAttribute(graph, nodeId, 'label', newLabel)
    store.set('isDirty', true)

    const cmd: Command = {
      description: `Rename node "${oldLabel}" to "${newLabel}"`,
      execute() {
        updateNodeAttribute(graph, nodeId, 'label', newLabel)
      },
      undo() {
        updateNodeAttribute(graph, nodeId, 'label', oldLabel)
      },
    }
    undoManager.push(cmd)
  })

  // --- Node Type (dropdown) ---
  const typeSelect = appendSelectField(
    inspectorEl,
    'Type',
    [...NODE_TYPES],
    String(attrs.nodeType ?? 'Concept')
  )
  typeSelect.addEventListener('change', () => {
    const newType = typeSelect.value
    const oldType = String(graph.getNodeAttribute(nodeId, 'nodeType') ?? 'Concept')
    const oldColor = String(graph.getNodeAttribute(nodeId, 'color') ?? NODE_COLORS.Concept)
    if (newType === oldType) return

    const newColor = NODE_COLORS[newType] ?? '#6366f1'
    updateNodeAttribute(graph, nodeId, 'nodeType', newType)
    updateNodeAttribute(graph, nodeId, 'color', newColor)
    store.set('isDirty', true)

    const cmd: Command = {
      description: `Change node type from "${oldType}" to "${newType}"`,
      execute() {
        updateNodeAttribute(graph, nodeId, 'nodeType', newType)
        updateNodeAttribute(graph, nodeId, 'color', newColor)
      },
      undo() {
        updateNodeAttribute(graph, nodeId, 'nodeType', oldType)
        updateNodeAttribute(graph, nodeId, 'color', oldColor)
      },
    }
    undoManager.push(cmd)
  })

  // --- Custom Properties Section ---
  const propsSection = document.createElement('div')
  propsSection.className = 'gv-sidebar__section'

  const propsTitle = document.createElement('div')
  propsTitle.className = 'gv-sidebar__section-title'
  propsTitle.textContent = 'Properties'
  propsSection.appendChild(propsTitle)

  const properties = (attrs.properties ?? {}) as Record<string, unknown>
  const propsList = document.createElement('div')
  propsList.className = 'gv-sidebar__props'

  for (const [key, value] of Object.entries(properties)) {
    const row = document.createElement('div')
    row.className = 'gv-sidebar__prop-row'

    const keySpan = document.createElement('span')
    keySpan.className = 'gv-sidebar__prop-key'
    keySpan.textContent = key

    const valInput = document.createElement('input')
    valInput.className = 'gv-sidebar__input gv-sidebar__prop-value'
    valInput.type = 'text'
    valInput.value = String(value ?? '')

    valInput.addEventListener('change', () => {
      const currentProps = {
        ...((graph.getNodeAttribute(nodeId, 'properties') as Record<string, unknown>) ?? {}),
      }
      const oldVal = currentProps[key]
      const newVal = valInput.value

      currentProps[key] = newVal
      updateNodeAttribute(graph, nodeId, 'properties', { ...currentProps })
      store.set('isDirty', true)

      const cmd: Command = {
        description: `Update property "${key}" on node "${nodeId}"`,
        execute() {
          const p = {
            ...((graph.getNodeAttribute(nodeId, 'properties') as Record<string, unknown>) ?? {}),
          }
          p[key] = newVal
          updateNodeAttribute(graph, nodeId, 'properties', { ...p })
        },
        undo() {
          const p = {
            ...((graph.getNodeAttribute(nodeId, 'properties') as Record<string, unknown>) ?? {}),
          }
          p[key] = oldVal
          updateNodeAttribute(graph, nodeId, 'properties', { ...p })
        },
      }
      undoManager.push(cmd)
    })

    row.appendChild(keySpan)
    row.appendChild(valInput)
    propsList.appendChild(row)
  }

  propsSection.appendChild(propsList)
  inspectorEl.appendChild(propsSection)

  // --- Connected Edges Section ---
  const edgesSection = document.createElement('div')
  edgesSection.className = 'gv-sidebar__section'

  const edgesTitle = document.createElement('div')
  edgesTitle.className = 'gv-sidebar__section-title'
  edgesTitle.textContent = 'Connected Edges'
  edgesSection.appendChild(edgesTitle)

  const edgesList = document.createElement('ul')
  edgesList.className = 'gv-sidebar__edges-list'

  graph.forEachEdge(nodeId, (edgeId, edgeAttrs, source, target) => {
    const li = document.createElement('li')
    li.className = 'gv-sidebar__edge-item'

    const edgeType = String(edgeAttrs.edgeType ?? 'relates_to')
    const otherNodeId = source === nodeId ? target : source
    const otherLabel = graph.hasNode(otherNodeId)
      ? String(graph.getNodeAttribute(otherNodeId, 'label') ?? otherNodeId)
      : otherNodeId

    const direction = source === nodeId ? '\u2192' : '\u2190'
    li.textContent = `${direction} ${otherLabel} (${edgeType})`
    li.title = `Edge: ${edgeId}\n${source} \u2192 ${target}`

    edgesList.appendChild(li)
  })

  if (edgesList.children.length === 0) {
    const li = document.createElement('li')
    li.className = 'gv-sidebar__edge-item gv-sidebar__edge-item--empty'
    li.textContent = 'No connected edges'
    edgesList.appendChild(li)
  }

  edgesSection.appendChild(edgesList)
  inspectorEl.appendChild(edgesSection)
}

// ---------------------------------------------------------------------------
// Field helpers
// ---------------------------------------------------------------------------

function appendField(
  container: HTMLElement,
  labelText: string,
  value: string,
  readOnly: boolean
): void {
  const field = document.createElement('div')
  field.className = 'gv-sidebar__field'

  const label = document.createElement('label')
  label.className = 'gv-sidebar__label'
  label.textContent = labelText

  const span = document.createElement('span')
  span.className = 'gv-sidebar__value'
  span.textContent = value
  if (readOnly) {
    span.classList.add('gv-sidebar__value--readonly')
  }

  field.appendChild(label)
  field.appendChild(span)
  container.appendChild(field)
}

function appendInputField(
  container: HTMLElement,
  labelText: string,
  value: string
): HTMLInputElement {
  const field = document.createElement('div')
  field.className = 'gv-sidebar__field'

  const label = document.createElement('label')
  label.className = 'gv-sidebar__label'
  label.textContent = labelText

  const input = document.createElement('input')
  input.className = 'gv-sidebar__input'
  input.type = 'text'
  input.value = value

  field.appendChild(label)
  field.appendChild(input)
  container.appendChild(field)

  return input
}

function appendSelectField(
  container: HTMLElement,
  labelText: string,
  options: string[],
  selectedValue: string
): HTMLSelectElement {
  const field = document.createElement('div')
  field.className = 'gv-sidebar__field'

  const label = document.createElement('label')
  label.className = 'gv-sidebar__label'
  label.textContent = labelText

  const select = document.createElement('select')
  select.className = 'gv-sidebar__select'

  for (const opt of options) {
    const option = document.createElement('option')
    option.value = opt
    option.textContent = opt
    if (opt === selectedValue) {
      option.selected = true
    }
    select.appendChild(option)
  }

  field.appendChild(label)
  field.appendChild(select)
  container.appendChild(field)

  return select
}
