/**
 * comments.js — Semantic comment system.
 * Add, edit, resolve, delete comments anchored to matrix cells.
 * Persists to localStorage, exports to JSON.
 */
;(() => {
  window.MatrixViewer = window.MatrixViewer || {}
  const MV = window.MatrixViewer

  var comments = []
  var storageKey = ''

  // --- Initialization ---

  MV.initComments = () => {
    var data = MV.getState().data
    storageKey = `matrixng-comments-${data.skillName}-${data.iteration}`
    loadFromStorage()
    updateCount()
  }

  // --- Cell Click Handlers ---

  MV.attachCellHandlers = () => {
    document.querySelectorAll('td[data-col]').forEach((td) => {
      // Operator token clicks
      td.querySelectorAll('.op-token').forEach((span, idx) => {
        span.addEventListener('click', (e) => {
          e.stopPropagation()
          showPopover(td, { token: span.textContent, tokenOffset: idx })
        })
      })

      td.addEventListener('click', (e) => {
        // Only trigger on the + icon (pseudo-element area) or direct click
        var rect = td.getBoundingClientRect()
        var isIconArea = e.clientX > rect.right - 24 && e.clientY < rect.top + 24
        if (isIconArea || e.detail === 2) {
          // Capture text selection as token anchor if present
          let tokenInfo = null
          const sel = window.getSelection()
          if (sel?.toString().trim()) {
            const selText = sel.toString().trim()
            const cellText = td.textContent || ''
            tokenInfo = { token: selText, tokenOffset: cellText.indexOf(selText) }
          }
          showPopover(td, tokenInfo)
        }
      })

      // Mark cells that have comments
      var anchor = anchorFromCell(td)
      if (anchor && hasComment(anchor)) {
        td.classList.add('has-comment')
      }
    })
  }

  // --- Popover ---

  function showPopover(td, tokenInfo) {
    var popover = document.getElementById('comment-popover')
    var textarea = document.getElementById('popover-textarea')
    var label = document.getElementById('popover-anchor-label')
    var anchor = anchorFromCell(td)

    if (anchor && tokenInfo) {
      anchor.token = tokenInfo.token
      anchor.tokenOffset = tokenInfo.tokenOffset
    }

    if (!anchor) return

    label.textContent = buildAnchorLabel(anchor)
    textarea.value = ''

    // Position near the cell
    var rect = td.getBoundingClientRect()
    popover.style.top = `${rect.bottom + 4}px`
    popover.style.left = `${Math.min(rect.left, window.innerWidth - 340)}px`
    popover.classList.remove('hidden')
    textarea.focus()

    // Wire save/cancel
    var saveBtn = document.getElementById('popover-save')
    var cancelBtn = document.getElementById('popover-cancel')

    var onSave = () => {
      var text = textarea.value.trim()
      if (text) {
        MV.saveComment(anchor, text)
        td.classList.add('has-comment')
      }
      popover.classList.add('hidden')
      cleanup()
    }

    var onCancel = () => {
      popover.classList.add('hidden')
      cleanup()
    }

    function cleanup() {
      saveBtn.removeEventListener('click', onSave)
      cancelBtn.removeEventListener('click', onCancel)
    }

    saveBtn.addEventListener('click', onSave)
    cancelBtn.addEventListener('click', onCancel)
  }

  // --- CRUD ---

  MV.saveComment = (anchor, text) => {
    var comment = {
      id: generateId(),
      anchor: anchor,
      anchorLabel: buildAnchorLabel(anchor),
      text: text,
      timestamp: new Date().toISOString(),
      resolved: false,
    }
    comments.push(comment)
    saveToStorage()
    updateCount()
    MV.renderSidebar(anchor.evalId)
  }

  MV.resolveComment = (id) => {
    var comment = comments.find((c) => c.id === id)
    if (comment) {
      comment.resolved = !comment.resolved
      saveToStorage()
      MV.renderSidebar(comment.anchor.evalId)
    }
  }

  MV.deleteComment = (id) => {
    var idx = comments.findIndex((c) => c.id === id)
    if (idx >= 0) {
      const evalId = comments[idx].anchor.evalId
      comments.splice(idx, 1)
      saveToStorage()
      updateCount()
      MV.renderSidebar(evalId)
    }
  }

  // --- Sidebar Rendering ---

  MV.renderSidebar = (evalId) => {
    var list = document.getElementById('comment-list')
    var filtered = comments.filter((c) => c.anchor.evalId === evalId)

    // Sort by document position
    filtered.sort((a, b) => {
      var sectionOrder = ['context', 'tier1', 'tier2', 'tier3', 'recovery', 'grading']
      var ai = sectionOrder.indexOf(a.anchor.section)
      var bi = sectionOrder.indexOf(b.anchor.section)
      if (ai !== bi) return ai - bi
      return (a.anchor.row || 0) - (b.anchor.row || 0)
    })

    list.innerHTML = filtered
      .map((c) => {
        var cls = `comment-entry${c.resolved ? ' resolved' : ''}`
        return (
          '<div class="' +
          cls +
          '" data-comment-id="' +
          c.id +
          '">' +
          '<div class="comment-anchor-label">' +
          escapeHtml(c.anchorLabel) +
          '</div>' +
          '<div class="comment-text">' +
          escapeHtml(c.text) +
          '</div>' +
          '<div class="comment-actions">' +
          '<button onclick="MatrixViewer.resolveComment(\'' +
          c.id +
          '\')">' +
          (c.resolved ? 'Reopen' : 'Resolve') +
          '</button>' +
          '<button onclick="MatrixViewer.deleteComment(\'' +
          c.id +
          '\')">Delete</button>' +
          '</div>' +
          '</div>'
        )
      })
      .join('')

    // Click to scroll to anchored cell
    list.querySelectorAll('.comment-entry').forEach((entry) => {
      entry.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON') return
        var id = entry.dataset.commentId
        var comment = comments.find((c) => c.id === id)
        if (comment) scrollToAnchor(comment.anchor)
      })
    })
  }

  // --- Export ---

  MV.exportComments = () => {
    var data = MV.getState().data
    var exportData = {
      metadata: {
        skillName: data.skillName,
        iteration: data.iteration,
        exportedAt: new Date().toISOString(),
      },
      comments: comments,
    }
    var blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    })
    var url = URL.createObjectURL(blob)
    var a = document.createElement('a')
    a.href = url
    a.download = `comments-${data.skillName}-iter${data.iteration}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // --- Helpers ---

  function anchorFromCell(td) {
    var evalId = parseInt(td.dataset.eval, 10)
    var config = td.dataset.config
    var section = td.dataset.section
    var row = td.dataset.row ? parseInt(td.dataset.row, 10) : undefined
    var column = td.dataset.col || undefined
    if (!evalId || !section) return null
    return {
      evalId: evalId,
      configuration: config || 'with_skill',
      section: section,
      row: row,
      column: column,
    }
  }

  function buildAnchorLabel(anchor) {
    var parts = [`Eval ${anchor.evalId}`]
    var sectionLabels = {
      context: 'Context',
      tier1: 'Tier 1',
      tier2: 'Tier 2',
      tier3: 'Tier 3',
      recovery: 'Runtime Recovery',
      grading: 'Grading Summary',
      decomposition: 'Decomposition',
    }
    parts.push(sectionLabels[anchor.section] || anchor.section)
    if (anchor.row) parts[parts.length - 1] += `, Row ${anchor.row}`
    if (anchor.column) {
      const colLabels = {
        engines: 'Engines',
        query: 'Query',
        operators: 'Operators',
        expected: 'Expected',
        acceptance: 'Acceptance',
        success: 'Success',
      }
      parts.push(colLabels[anchor.column] || anchor.column)
    }
    var result = parts.join(' \u2192 ')
    if (anchor.token) {
      result += ` \u2192 "${anchor.token}"`
    }
    return result
  }

  function hasComment(anchor) {
    return comments.some(
      (c) =>
        c.anchor.evalId === anchor.evalId &&
        c.anchor.section === anchor.section &&
        c.anchor.row === anchor.row &&
        c.anchor.column === anchor.column
    )
  }

  function scrollToAnchor(anchor) {
    var selector = `td[data-eval="${anchor.evalId}"][data-section="${anchor.section}"]`
    if (anchor.row) selector += `[data-row="${anchor.row}"]`
    if (anchor.column) selector += `[data-col="${anchor.column}"]`
    var el = document.querySelector(selector)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      el.style.outline = '2px solid var(--primary)'
      setTimeout(() => {
        el.style.outline = ''
      }, 2000)

      // Highlight the specific token within the cell
      if (anchor.token) {
        highlightToken(el, anchor.token)
      }
    }
  }

  function highlightToken(cell, token) {
    var walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT)
    var node = walker.nextNode()
    var idx, range, mark
    while (node) {
      idx = node.textContent.indexOf(token)
      if (idx !== -1) {
        range = document.createRange()
        range.setStart(node, idx)
        range.setEnd(node, idx + token.length)
        mark = document.createElement('mark')
        mark.style.background = 'var(--primary)'
        mark.style.color = '#fff'
        range.surroundContents(mark)
        setTimeout(() => {
          var parent = mark.parentNode
          parent.replaceChild(document.createTextNode(mark.textContent), mark)
          parent.normalize()
        }, 2000)
        return
      }
      node = walker.nextNode()
    }
  }

  function loadFromStorage() {
    try {
      const stored = localStorage.getItem(storageKey)
      if (stored) comments = JSON.parse(stored)
    } catch (_e) {
      comments = []
    }
  }

  function saveToStorage() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(comments))
    } catch (_e) {
      // localStorage full or unavailable — silent fail
    }
  }

  function updateCount() {
    var el = document.getElementById('comment-count')
    if (el) el.textContent = comments.filter((c) => !c.resolved).length
  }

  function generateId() {
    return Math.random().toString(36).substring(2, 9)
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
  }
})()
