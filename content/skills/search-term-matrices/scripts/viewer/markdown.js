/**
 * Markdown -> HTML renderer.
 * Supports: tables (with data-* annotations), headings, bold, italic,
 * code blocks, inline code, lists, blockquotes, paragraphs.
 *
 * Tables get special treatment: each cell is annotated with data-anchor
 * attributes for the comment system.
 */
;(() => {
  window.MatrixViewer = window.MatrixViewer || {}
  const MV = window.MatrixViewer

  /**
   * Render markdown string to HTML.
   * @param {string} md - Raw markdown
   * @param {object} [anchorContext] - { evalId, configuration } for table annotation
   * @returns {string} HTML
   */
  MV.renderMarkdown = (md, anchorContext) => {
    if (!md) return ''
    const lines = md.split('\n')
    const result = []
    let i = 0
    let currentSection = null
    let currentTierLevel = 0

    while (i < lines.length) {
      const line = lines[i]

      // Headings
      const headingMatch = line.match(/^(#{1,6})\s+(.+)/)
      if (headingMatch) {
        const level = headingMatch[1].length
        const text = processInline(headingMatch[2])
        const sectionId = detectSection(headingMatch[2])
        if (sectionId) currentSection = sectionId
        if (sectionId && sectionId.startsWith('tier')) {
          currentTierLevel = parseInt(sectionId.replace('tier', ''))
        }
        const attrs = sectionId ? ` data-section="${sectionId}"` : ''
        result.push(`<h${level}${attrs}>${text}</h${level}>`)
        i++
        continue
      }

      // Code blocks
      if (line.startsWith('```')) {
        const lang = line.slice(3).trim()
        const codeLines = []
        i++
        while (i < lines.length && !lines[i].startsWith('```')) {
          codeLines.push(escapeHtml(lines[i]))
          i++
        }
        i++ // skip closing ```
        result.push(
          `<pre><code class="language-${lang || 'text'}">${codeLines.join('\n')}</code></pre>`
        )
        continue
      }

      // Tables
      if (line.includes('|') && i + 1 < lines.length && lines[i + 1].match(/^\|?[\s-:|]+\|?$/)) {
        const tableHtml = renderTable(lines, i, anchorContext, currentSection, currentTierLevel)
        result.push(tableHtml.html)
        i = tableHtml.endIndex
        continue
      }

      // Blockquotes
      if (line.startsWith('>')) {
        const quoteLines = []
        while (i < lines.length && lines[i].startsWith('>')) {
          quoteLines.push(processInline(lines[i].replace(/^>\s?/, '')))
          i++
        }
        result.push(`<blockquote>${quoteLines.join('<br>')}</blockquote>`)
        continue
      }

      // Lists
      if (line.match(/^[\s]*[-*+]\s/) || line.match(/^[\s]*\d+\.\s/)) {
        const listResult = renderList(lines, i)
        result.push(listResult.html)
        i = listResult.endIndex
        continue
      }

      // Blank line
      if (line.trim() === '') {
        i++
        continue
      }

      // Paragraph
      const paraLines = []
      while (
        i < lines.length &&
        lines[i].trim() !== '' &&
        !lines[i].startsWith('#') &&
        !lines[i].startsWith('```') &&
        !lines[i].startsWith('>') &&
        !lines[i].includes('|')
      ) {
        paraLines.push(processInline(lines[i]))
        i++
      }
      if (paraLines.length > 0) {
        result.push(`<p>${paraLines.join(' ')}</p>`)
      }
    }

    return result.join('\n')
  }

  // --- Table rendering with data-anchor attributes ---

  function renderTable(lines, startIndex, ctx, section, tierLevel) {
    const headerLine = lines[startIndex]
    const headers = splitRow(headerLine)

    // Map header names to column keys for anchoring
    const colKeys = headers.map((h) => {
      const lower = h.toLowerCase().replace(/[^a-z]/g, '')
      if (lower === 'engines' || lower === 'engine' || lower === 'engines') return 'engines'
      if (lower === 'query') return 'query'
      if (lower === 'operators') return 'operators'
      if (lower === 'expectedresults') return 'expected'
      if (lower === 'acceptance' || lower === 'acceptancecriteria') return 'acceptance'
      if (lower === 'success' || lower === 'successcriteria') return 'success'
      return lower
    })

    let i = startIndex + 2 // skip header + separator
    const rows = []
    let rowNum = 0

    while (i < lines.length && lines[i].includes('|') && !lines[i].match(/^\|?[\s-:|]+\|?$/)) {
      rowNum++
      const cells = splitRow(lines[i])
      rows.push({ num: rowNum, cells: cells })
      i++
    }

    // Build HTML
    let html = '<table>'
    html += '<thead><tr>'
    for (const h of headers) {
      html += `<th>${processInline(h)}</th>`
    }
    html += '</tr></thead>'
    html += '<tbody>'

    for (const row of rows) {
      html += '<tr>'
      for (let c = 0; c < headers.length; c++) {
        const cellText = row.cells[c] || ''
        let attrs = ''
        if (ctx && section) {
          attrs = ` data-eval="${ctx.evalId}" data-config="${ctx.configuration}" data-section="${section}" data-row="${row.num}" data-col="${colKeys[c] || ''}"`
        }
        html += `<td${attrs}>${processInline(cellText)}</td>`
      }
      html += '</tr>'
    }

    html += '</tbody></table>'
    return { html: html, endIndex: i }
  }

  function renderList(lines, startIndex) {
    const isOrdered = !!lines[startIndex].match(/^[\s]*\d+\.\s/)
    const tag = isOrdered ? 'ol' : 'ul'
    const items = []
    let i = startIndex

    while (i < lines.length) {
      const match = lines[i].match(isOrdered ? /^[\s]*\d+\.\s(.+)/ : /^[\s]*[-*+]\s(.+)/)
      if (!match) break
      items.push(`<li>${processInline(match[1])}</li>`)
      i++
    }

    return { html: `<${tag}>${items.join('')}</${tag}>`, endIndex: i }
  }

  function detectSection(heading) {
    const lower = heading.toLowerCase()
    if (lower.includes('context')) return 'context'
    if (lower.includes('tier 1') || lower.includes('tier1')) return 'tier1'
    if (lower.includes('tier 2') || lower.includes('tier2')) return 'tier2'
    if (lower.includes('tier 3') || lower.includes('tier3')) return 'tier3'
    if (lower.includes('runtime recovery') || lower.includes('recovery')) return 'recovery'
    if (lower.includes('grading')) return 'grading'
    if (lower.includes('decomposition')) return 'decomposition'
    return null
  }

  function splitRow(line) {
    var trimmed = line.trim()
    if (trimmed.charAt(0) === '|') trimmed = trimmed.slice(1)
    if (trimmed.charAt(trimmed.length - 1) === '|') trimmed = trimmed.slice(0, -1)
    return trimmed.split('|').map((c) => c.trim())
  }

  function processInline(text) {
    if (!text) return ''
    text = escapeHtml(text)
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>')
    text = text.replace(/`(.+?)`/g, '<code>$1</code>')
    text = text.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>')
    return text
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
  }
})()
