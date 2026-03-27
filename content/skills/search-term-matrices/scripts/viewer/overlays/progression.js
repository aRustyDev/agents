;(() => {
  const MV = window.MatrixViewer
  MV.overlays = MV.overlays || {}

  let panel = null

  function activate() {
    const state = MV.getState()
    const evalCase = state.data.evals[state.currentEvalIndex]
    if (!evalCase) return

    const raw = evalCase.configurations.with_skill.raw
    const matrices = MV.parseAllMatrices ? MV.parseAllMatrices(raw) : [MV.parseMatrix(raw)]
    const matrix = matrices[0]
    if (!matrix || matrix.tiers.length === 0) return

    // Collect all engines across tiers for "new engine" detection
    const enginesByTier = {}
    const seenEngines = new Set()

    matrix.tiers.forEach((tier) => {
      const tierEngines = new Set()
      tier.rows.forEach((row) => {
        row.engines.forEach((e) => tierEngines.add(e))
      })
      enginesByTier[tier.level] = { engines: tierEngines, newEngines: new Set() }
    })

    // Mark new engines (not seen in previous tiers)
    matrix.tiers.forEach((tier) => {
      const info = enginesByTier[tier.level]
      info.engines.forEach((e) => {
        if (!seenEngines.has(e)) {
          if (tier.level > 1) info.newEngines.add(e)
        }
      })
      info.engines.forEach((e) => seenEngines.add(e))
    })

    // Build the panel
    panel = document.createElement('div')
    panel.className = 'progression-panel'

    matrix.tiers.forEach((tier) => {
      const col = document.createElement('div')
      col.className = 'progression-tier'

      const header = document.createElement('div')
      header.className = 'progression-tier-header'
      header.textContent = `Tier ${tier.level}: ${tier.label} (${tier.rows.length} rows)`
      col.appendChild(header)

      const info = enginesByTier[tier.level]

      tier.rows.forEach((row) => {
        const rowEl = document.createElement('div')
        rowEl.className = 'progression-row'

        // Engine chips
        const chips = row.engines
          .map((e) => {
            const isNew = info.newEngines.has(e)
            return `<span class="engine-chip${isNew ? ' new' : ''}">${escapeHtml(e)}</span>`
          })
          .join(' ')

        // Precision tag
        const precision = getPrecision(row.operators)
        const precisionHtml = `<span class="precision-tag precision-${precision}">${precision}</span>`

        rowEl.innerHTML = `${precisionHtml} ${chips}<br><small>${escapeHtml(row.query)}</small>`
        col.appendChild(rowEl)
      })

      panel.appendChild(col)
    })

    const content = document.getElementById('matrix-content')
    if (content) content.appendChild(panel)
  }

  function deactivate() {
    if (panel) {
      panel.remove()
      panel = null
    }
  }

  function getPrecision(operators) {
    if (!operators) return 'broad'
    const lower = operators.toLowerCase()
    if (
      lower.includes('site:') ||
      lower.includes('"') ||
      lower.includes('language:') ||
      lower.includes('cat:')
    )
      return 'high'
    if (lower.includes(':') || lower.includes('after:') || lower.includes('stars:')) return 'medium'
    return 'broad'
  }

  function escapeHtml(text) {
    return (text || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }

  MV.overlays.progression = { activate, deactivate }
})()
