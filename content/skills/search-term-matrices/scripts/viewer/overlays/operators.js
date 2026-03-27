;(() => {
  const MV = window.MatrixViewer
  MV.overlays = MV.overlays || {}

  let tooltip = null
  const originalContents = new Map()

  function activate() {
    // Create tooltip element if needed
    if (!tooltip) {
      tooltip = document.createElement('div')
      tooltip.className = 'op-tooltip'
      tooltip.innerHTML =
        '<div class="op-tooltip-engine"></div><div class="op-tooltip-syntax"></div><div class="op-tooltip-example"></div>'
      document.body.appendChild(tooltip)
    }

    const operators = MV.getState().data.engineOperators || {}
    // Build a flat lookup: prefix -> EngineOperator
    const lookup = buildLookup(operators)

    document.querySelectorAll('td[data-col="operators"]').forEach((td) => {
      // Save original HTML for restoration
      originalContents.set(td, td.innerHTML)

      const text = td.textContent || ''
      // Tokenize: split on spaces and commas, keep non-empty
      const tokens = text.split(/[\s,]+/).filter(Boolean)
      let html = td.innerHTML

      tokens.forEach((token) => {
        // Match by prefix: "site:reddit.com" matches operator "site:"
        const match = findOperatorMatch(token, lookup)
        if (match) {
          const escaped = escapeRegex(token)
          const re = new RegExp(`(?<![\\w-])${escaped}(?![\\w])`, 'g')
          html = html.replace(
            re,
            `<span class="op-token" data-op="${encodeURIComponent(match.operator)}">${token}</span>`
          )
        }
      })

      td.innerHTML = html
    })

    // Add hover listeners
    document.addEventListener('mouseover', handleHover)
    document.addEventListener('mouseout', handleOut)
  }

  function deactivate() {
    // Restore original cell contents
    originalContents.forEach((html, td) => {
      td.innerHTML = html
    })
    originalContents.clear()

    // Remove tooltip
    if (tooltip) {
      tooltip.classList.remove('visible')
    }

    document.removeEventListener('mouseover', handleHover)
    document.removeEventListener('mouseout', handleOut)
  }

  function handleHover(e) {
    const target = e.target.closest('.op-token')
    if (!target || !tooltip) return

    const opKey = decodeURIComponent(target.dataset.op)
    const operators = MV.getState().data.engineOperators || {}
    const lookup = buildLookup(operators)
    const match = lookup.get(opKey)

    if (!match) return

    tooltip.querySelector('.op-tooltip-engine').textContent = match.engine
    tooltip.querySelector('.op-tooltip-syntax').textContent = match.syntax
    tooltip.querySelector('.op-tooltip-example').textContent = match.example || ''

    const rect = target.getBoundingClientRect()
    tooltip.style.top = `${rect.bottom + 4}px`
    tooltip.style.left = `${Math.min(rect.left, window.innerWidth - 340)}px`
    tooltip.classList.add('visible')
  }

  function handleOut(e) {
    if (!e.target.closest('.op-token') && tooltip) {
      tooltip.classList.remove('visible')
    }
  }

  function buildLookup(operators) {
    const map = new Map()
    for (const [_engine, ops] of Object.entries(operators)) {
      for (const op of ops) {
        // Key by the operator prefix (e.g., "site:", "language:")
        map.set(op.operator, op)
      }
    }
    return map
  }

  function findOperatorMatch(token, lookup) {
    // Direct match
    if (lookup.has(token)) return lookup.get(token)
    // Prefix match: "site:reddit.com" starts with "site:"
    for (const [key, op] of lookup) {
      if (token.startsWith(key)) return op
    }
    return null
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  }

  MV.overlays.operators = { activate, deactivate }
})()
