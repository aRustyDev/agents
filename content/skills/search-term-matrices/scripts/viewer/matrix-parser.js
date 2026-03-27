/**
 * matrix-parser.js — Parse raw matrix markdown into structured data.
 * Used by overlay views in Pass 2 and for client-side data extraction.
 */
;(() => {
  window.MatrixViewer = window.MatrixViewer || {}
  const MV = window.MatrixViewer

  /**
   * Parse a single matrix markdown document into a ParsedMatrix object.
   * @param {string} raw - Raw markdown
   * @returns {object} ParsedMatrix
   */
  MV.parseMatrix = (raw) => {
    if (!raw) return emptyMatrix()

    var lines = raw.split('\n')
    var result = emptyMatrix()
    var currentSection = null
    var i = 0

    while (i < lines.length) {
      const line = lines[i]

      // Detect headings for section tracking
      const headingMatch = line.match(/^(#{1,6})\s+(.+)/)
      if (headingMatch) {
        const headingText = headingMatch[2]
        const section = MV.detectSection(headingText)
        if (section) currentSection = section

        // Extract context fields from list items after Context heading
        if (section === 'context') {
          i++
          result.context = parseContextBlock(lines, i)
          // Advance past the context block
          while (i < lines.length && lines[i].trim() !== '' && !lines[i].startsWith('#')) i++
          continue
        }

        // Extract runtime recovery items
        if (section === 'recovery') {
          i++
          result.runtimeRecovery = parseBulletList(lines, i)
          while (i < lines.length && lines[i].trim() !== '' && !lines[i].startsWith('#')) i++
          continue
        }

        // Extract grading summary
        if (section === 'grading') {
          i++
          const gradingLines = []
          while (i < lines.length && !lines[i].startsWith('#')) {
            gradingLines.push(lines[i])
            i++
          }
          result.gradingSummary = gradingLines.join('\n').trim()
          continue
        }

        i++
        continue
      }

      // Detect tables within tier sections
      if (
        currentSection?.startsWith('tier') &&
        line.includes('|') &&
        i + 1 < lines.length &&
        lines[i + 1].match(/^\|?[\s-:|]+\|?$/)
      ) {
        const tierLevel = parseInt(currentSection.replace('tier', ''), 10)
        const tier = parseTierTable(lines, i, tierLevel)
        // Find or create this tier
        const existing = result.tiers.find((t) => t.level === tierLevel)
        if (existing) {
          existing.rows = existing.rows.concat(tier.rows)
        } else {
          result.tiers.push(tier)
        }
        i = tier._endIndex
        continue
      }

      i++
    }

    return result
  }

  /**
   * Parse a document that may contain multiple matrices (decomposed output).
   * Returns an array of ParsedMatrix objects.
   * @param {string} raw - Raw markdown (possibly multi-matrix)
   * @returns {object[]} Array of ParsedMatrix
   */
  MV.parseAllMatrices = (raw) => {
    if (!raw) return []

    // Split on h2 headings that look like matrix headers
    var sections = raw.split(/(?=^## (?:Search Matrix|Matrix \d))/m)
    var matrices = []

    for (let s = 0; s < sections.length; s++) {
      const section = sections[s].trim()
      if (!section) continue
      // Only parse sections that have tier tables
      if (
        section.includes('Tier 1') ||
        section.includes('tier 1') ||
        section.includes('### Tier')
      ) {
        matrices.push(MV.parseMatrix(section))
      }
    }

    // If no splits found, try parsing the whole document as one matrix
    if (matrices.length === 0 && raw.includes('|')) {
      matrices.push(MV.parseMatrix(raw))
    }

    return matrices
  }

  /**
   * Detect section type from a heading string.
   * Exposed on MV namespace so other modules can reuse it.
   */
  MV.detectSection = (heading) => {
    var lower = heading.toLowerCase()
    if (lower.includes('context')) return 'context'
    if (lower.match(/tier\s*1/)) return 'tier1'
    if (lower.match(/tier\s*2/)) return 'tier2'
    if (lower.match(/tier\s*3/)) return 'tier3'
    if (lower.includes('runtime recovery') || lower.includes('recovery')) return 'recovery'
    if (lower.includes('grading')) return 'grading'
    if (lower.includes('decomposition')) return 'decomposition'
    return null
  }

  // --- Internal helpers ---

  function emptyMatrix() {
    return {
      context: null,
      tiers: [],
      runtimeRecovery: [],
      gradingSummary: '',
      decomposition: null,
    }
  }

  function parseContextBlock(lines, startIndex) {
    var ctx = { goal: '', type: '', domain: '' }
    var i = startIndex
    while (i < lines.length && !lines[i].startsWith('#')) {
      const line = lines[i].trim()
      const goalMatch = line.match(/\*?\*?Goal\*?\*?:\s*(.+)/i)
      const typeMatch = line.match(/\*?\*?Type\*?\*?:\s*(.+)/i)
      const domainMatch = line.match(/\*?\*?Domain\*?\*?:\s*(.+)/i)
      if (goalMatch) ctx.goal = goalMatch[1].trim()
      if (typeMatch) ctx.type = typeMatch[1].trim()
      if (domainMatch) ctx.domain = domainMatch[1].trim()
      i++
    }
    return ctx.goal || ctx.type || ctx.domain ? ctx : null
  }

  function parseBulletList(lines, startIndex) {
    var items = []
    var i = startIndex
    while (i < lines.length && !lines[i].startsWith('#')) {
      const match = lines[i].match(/^[\s]*[-*+]\s+(.+)/)
      if (match) items.push(match[1].trim())
      i++
    }
    return items
  }

  function parseTierTable(lines, startIndex, tierLevel) {
    var _headers = splitRow(lines[startIndex])
    var rows = []
    var i = startIndex + 2 // skip header + separator

    while (i < lines.length && lines[i].includes('|') && !lines[i].match(/^\|?[\s-:|]+\|?$/)) {
      const cells = splitRow(lines[i])
      const row = {
        num: parseInt(cells[0], 10) || rows.length + 1,
        engines: (cells[1] || '')
          .split(',')
          .map((e) => e.trim())
          .filter(Boolean),
        query: cells[2] || '',
        operators: cells[3] || '',
        expectedResults: cells[4] || '',
        acceptance: cells[5] || '',
        success: cells[6] || '',
      }
      rows.push(row)
      i++
    }

    var labels = {
      1: 'Primary (high-precision)',
      2: 'Broadened',
      3: 'Alternative sources',
    }
    return {
      level: tierLevel,
      label: labels[tierLevel] || `Tier ${tierLevel}`,
      rows: rows,
      _endIndex: i,
    }
  }

  function splitRow(line) {
    var trimmed = line.trim()
    if (trimmed.charAt(0) === '|') trimmed = trimmed.slice(1)
    if (trimmed.charAt(trimmed.length - 1) === '|') trimmed = trimmed.slice(0, -1)
    return trimmed.split('|').map((c) => c.trim())
  }
})()
