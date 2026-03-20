/**
 * Help overlay — displays a modal listing all keyboard shortcuts.
 *
 * Toggled by the `?` key or the toolbar help button. Escape closes it.
 * The overlay is lazily created on first show and reused thereafter.
 */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let overlayEl: HTMLElement | null = null
let visible = false

// ---------------------------------------------------------------------------
// Shortcut data
// ---------------------------------------------------------------------------

interface ShortcutEntry {
  readonly keys: string[]
  readonly action: string
}

const SHORTCUTS: readonly ShortcutEntry[] = [
  { keys: ['Delete', 'Backspace'], action: 'Delete selected nodes/edges' },
  { keys: ['Ctrl+Z'], action: 'Undo' },
  { keys: ['Ctrl+Shift+Z', 'Ctrl+Y'], action: 'Redo' },
  { keys: ['Ctrl+S'], action: 'Save graph' },
  { keys: ['Escape'], action: 'Deselect / Close panels' },
  { keys: ['F'], action: 'Fit graph to viewport' },
  { keys: ['/'], action: 'Focus search input' },
  { keys: ['?'], action: 'Toggle this help' },
  { keys: ['Double-click'], action: 'Create node' },
  { keys: ['Shift+Click'], action: 'Create edge from selected node' },
]

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Create and return the help overlay element. Lazily constructed once,
 * then reused on subsequent calls.
 */
export function createHelpOverlay(): HTMLElement {
  if (overlayEl) return overlayEl

  const overlay = document.createElement('div')
  overlay.className = 'gv-help-overlay'
  overlay.style.display = 'none'

  // Clicking the backdrop closes the overlay
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      hideHelp()
    }
  })

  const content = document.createElement('div')
  content.className = 'gv-help-overlay__content'

  // Title row
  const titleRow = document.createElement('div')
  titleRow.className = 'gv-help-overlay__title-row'

  const title = document.createElement('h2')
  title.className = 'gv-help-overlay__title'
  title.textContent = 'Keyboard Shortcuts'
  titleRow.appendChild(title)

  const closeBtn = document.createElement('button')
  closeBtn.className = 'gv-help-overlay__close'
  closeBtn.textContent = '\u00d7'
  closeBtn.title = 'Close (Escape)'
  closeBtn.addEventListener('click', () => hideHelp())
  titleRow.appendChild(closeBtn)

  content.appendChild(titleRow)

  // Shortcut table
  const table = document.createElement('table')
  table.className = 'gv-help-overlay__table'

  const thead = document.createElement('thead')
  const headerRow = document.createElement('tr')
  const thKey = document.createElement('th')
  thKey.textContent = 'Key'
  const thAction = document.createElement('th')
  thAction.textContent = 'Action'
  headerRow.appendChild(thKey)
  headerRow.appendChild(thAction)
  thead.appendChild(headerRow)
  table.appendChild(thead)

  const tbody = document.createElement('tbody')
  for (const shortcut of SHORTCUTS) {
    const tr = document.createElement('tr')

    const tdKey = document.createElement('td')
    for (let i = 0; i < shortcut.keys.length; i++) {
      if (i > 0) {
        const sep = document.createTextNode(' / ')
        tdKey.appendChild(sep)
      }
      const kbd = document.createElement('kbd')
      kbd.className = 'gv-help-overlay__key'
      kbd.textContent = shortcut.keys[i]
      tdKey.appendChild(kbd)
    }

    const tdAction = document.createElement('td')
    tdAction.textContent = shortcut.action

    tr.appendChild(tdKey)
    tr.appendChild(tdAction)
    tbody.appendChild(tr)
  }

  table.appendChild(tbody)
  content.appendChild(table)
  overlay.appendChild(content)

  document.body.appendChild(overlay)
  overlayEl = overlay
  return overlay
}

/**
 * Toggle the help overlay visibility. If it does not exist yet, it is
 * created and appended to `document.body`.
 */
export function toggleHelp(): void {
  if (visible) {
    hideHelp()
  } else {
    showHelp()
  }
}

/**
 * Show the help overlay.
 */
export function showHelp(): void {
  const overlay = createHelpOverlay()
  overlay.style.display = ''
  visible = true
}

/**
 * Hide the help overlay.
 */
export function hideHelp(): void {
  if (overlayEl) {
    overlayEl.style.display = 'none'
  }
  visible = false
}

/**
 * Whether the help overlay is currently visible.
 */
export function isHelpVisible(): boolean {
  return visible
}
