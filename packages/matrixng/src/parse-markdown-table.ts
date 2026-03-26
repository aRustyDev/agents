export type TableRow = Record<string, string>

/**
 * Parse a markdown table string into an array of row objects.
 * Keys are the header column names. Values are trimmed cell text.
 * Returns [] if the input doesn't contain a valid markdown table.
 */
export function parseMarkdownTable(markdown: string): TableRow[] {
  const lines = markdown.split('\n').filter((l) => l.trim().length > 0)

  // Need at least header + separator + one data row
  if (lines.length < 3) return []

  const headerLine = lines[0]
  const separatorLine = lines[1]

  // Validate: header must have pipes, separator must have dashes
  if (!headerLine.includes('|') || !separatorLine.match(/^\|?[\s-:|]+\|?$/)) return []

  const headers = splitTableRow(headerLine)
  if (headers.length === 0) return []

  const rows: TableRow[] = []
  for (let i = 2; i < lines.length; i++) {
    const cells = splitTableRow(lines[i])
    if (cells.length === 0) continue
    const row: TableRow = {}
    for (let j = 0; j < headers.length; j++) {
      row[headers[j]] = cells[j] ?? ''
    }
    rows.push(row)
  }

  return rows
}

/**
 * Split a markdown table row into trimmed cell values.
 * Handles leading/trailing pipes.
 */
function splitTableRow(line: string): string[] {
  let trimmed = line.trim()
  if (trimmed.startsWith('|')) trimmed = trimmed.slice(1)
  if (trimmed.endsWith('|')) trimmed = trimmed.slice(0, -1)
  return trimmed.split('|').map((cell) => cell.trim())
}

/**
 * Find all markdown tables in a document and parse each.
 * Returns an array of table arrays — one per table found.
 */
export function findAllTables(markdown: string): TableRow[][] {
  const tables: TableRow[][] = []
  const lines = markdown.split('\n')
  let i = 0

  while (i < lines.length) {
    // Look for a line that looks like a table header (has pipes)
    if (lines[i].includes('|') && i + 1 < lines.length && lines[i + 1].match(/^\|?[\s-:|]+\|?$/)) {
      // Collect contiguous table lines
      const tableLines: string[] = []
      let j = i
      while (j < lines.length && lines[j].includes('|')) {
        tableLines.push(lines[j])
        j++
      }
      const parsed = parseMarkdownTable(tableLines.join('\n'))
      if (parsed.length > 0) tables.push(parsed)
      i = j
    } else {
      i++
    }
  }

  return tables
}
