/**
 * core.js — Main application controller.
 * Initializes the viewer, manages tab/subtab state, renders content, handles keyboard nav.
 */
;(() => {
  window.MatrixViewer = window.MatrixViewer || {}
  const MV = window.MatrixViewer

  var state = {
    data: null,
    currentTab: 'outputs',
    currentEvalIndex: 0,
    editMode: false,
  }

  // --- Initialization ---

  MV.init = () => {
    state.data = window.__VIEWER_DATA__
    if (!state.data) {
      document.getElementById('matrix-content').innerHTML = '<p>No viewer data found.</p>'
      return
    }

    // Populate header
    document.getElementById('skill-name').textContent = state.data.skillName
    document.getElementById('meta-info').textContent =
      'Iteration ' +
      state.data.iteration +
      ' \u2022 ' +
      new Date(state.data.generatedAt).toLocaleDateString()

    // Build subtabs for evals
    buildSubtabs()

    // Wire up tab bar
    document.querySelectorAll('.tab').forEach((tab) => {
      tab.addEventListener('click', () => {
        MV.switchTab(tab.dataset.tab)
      })
    })

    // Wire up benchmark subtabs
    document.querySelectorAll('.bench-subtab').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.bench-subtab').forEach((b) => {
          b.classList.remove('active')
        })
        btn.classList.add('active')
        document.querySelectorAll('.bench-panel').forEach((p) => {
          p.classList.remove('active')
        })
        document.getElementById(`${btn.dataset.subtab}-panel`).classList.add('active')
      })
    })

    // Wire up mode toggle
    document.getElementById('mode-rendered').addEventListener('click', () => {
      state.editMode = false
      updateModeButtons()
      renderCurrentEval()
    })
    document.getElementById('mode-edit').addEventListener('click', () => {
      state.editMode = true
      updateModeButtons()
      renderCurrentEval()
    })

    // Wire up nav buttons
    document.getElementById('prev-subtab').addEventListener('click', () => {
      MV.navSubtab(-1)
    })
    document.getElementById('next-subtab').addEventListener('click', () => {
      MV.navSubtab(1)
    })

    // Wire up sidebar toggle
    document.getElementById('sidebar-toggle').addEventListener('click', () => {
      document.getElementById('comment-sidebar').classList.toggle('collapsed')
    })

    // Wire up export button
    document.getElementById('export-comments').addEventListener('click', () => {
      if (MV.exportComments) MV.exportComments()
    })

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      // Skip if inside an input or textarea
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return

      switch (e.key) {
        case 'ArrowLeft':
          e.preventDefault()
          MV.navSubtab(-1)
          break
        case 'ArrowRight':
          e.preventDefault()
          MV.navSubtab(1)
          break
        case '1':
          MV.switchTab('outputs')
          break
        case '2':
          MV.switchTab('benchmark')
          break
        case 'e':
          state.editMode = !state.editMode
          updateModeButtons()
          renderCurrentEval()
          break
        case 'c':
          document.getElementById('comment-sidebar').classList.remove('collapsed')
          break
        case 'Escape': {
          const popover = document.getElementById('comment-popover')
          if (popover) popover.classList.add('hidden')
          break
        }
      }
    })

    // Initialize comments system
    if (MV.initComments) MV.initComments()

    // Render first eval
    renderCurrentEval()

    // Render benchmark
    if (MV.renderBenchmark) MV.renderBenchmark()
    if (MV.initRibbon) MV.initRibbon()
  }

  // --- Tab Management ---

  MV.switchTab = (tabName) => {
    state.currentTab = tabName
    document.querySelectorAll('.tab').forEach((t) => {
      t.classList.toggle('active', t.dataset.tab === tabName)
    })
    document.querySelectorAll('.tab-panel').forEach((p) => {
      p.classList.toggle('active', p.id === `${tabName}-tab`)
    })
  }

  MV.switchSubtab = (index) => {
    if (index < 0 || index >= state.data.evals.length) return
    state.currentEvalIndex = index
    document.querySelectorAll('.subtab').forEach((s, i) => {
      s.classList.toggle('active', i === index)
    })
    renderCurrentEval()
    if (MV.renderSidebar) MV.renderSidebar(state.data.evals[index].evalId)
  }

  MV.navSubtab = (delta) => {
    var next = state.currentEvalIndex + delta
    if (next >= 0 && next < state.data.evals.length) {
      MV.switchSubtab(next)
    }
  }

  // --- Rendering ---

  function renderCurrentEval() {
    var evalCase = state.data.evals[state.currentEvalIndex]
    if (!evalCase) return

    var container = document.getElementById('matrix-content')
    var raw = evalCase.configurations.with_skill.raw

    if (state.editMode) {
      container.innerHTML = renderEditMode(raw)
    } else {
      const anchorCtx = { evalId: evalCase.evalId, configuration: 'with_skill' }
      let html = MV.renderMarkdown(raw, anchorCtx)

      // Add baseline section
      const baselineRaw = evalCase.configurations.without_skill.raw
      if (baselineRaw) {
        html += renderBaselineSection(baselineRaw, evalCase.evalId)
      }

      container.innerHTML = html

      // Re-attach comment click handlers
      if (MV.attachCellHandlers) MV.attachCellHandlers()
    }
  }

  function renderEditMode(raw) {
    var lines = raw.split('\n')
    var lineHtml = lines.map((line) => `<span class="line">${escapeHtml(line)}</span>`).join('\n')
    return `<pre class="edit-mode">${lineHtml}</pre>`
  }

  function renderBaselineSection(raw, evalId) {
    var html = '<div class="baseline-section">'
    html +=
      '<button class="baseline-toggle" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">Baseline (without skill)</button>'
    html += '<div class="baseline-content">'
    html += MV.renderMarkdown(raw, {
      evalId: evalId,
      configuration: 'without_skill',
    })
    html += '</div></div>'
    return html
  }

  function buildSubtabs() {
    var bar = document.getElementById('subtab-bar')
    bar.innerHTML = ''
    state.data.evals.forEach((ev, i) => {
      var btn = document.createElement('button')
      btn.className = `subtab${i === 0 ? ' active' : ''}`
      btn.textContent = formatEvalName(ev.evalName)
      btn.addEventListener('click', () => {
        MV.switchSubtab(i)
      })
      bar.appendChild(btn)
    })
  }

  function formatEvalName(name) {
    // "offline-sync-frameworks" → "Offline Sync Frameworks"
    return name.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
  }

  function updateModeButtons() {
    document.getElementById('mode-rendered').classList.toggle('active', !state.editMode)
    document.getElementById('mode-edit').classList.toggle('active', state.editMode)
  }

  function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }

  // --- Expose state for other modules ---
  MV.getState = () => state

  // --- Boot ---
  document.addEventListener('DOMContentLoaded', MV.init)
})()
