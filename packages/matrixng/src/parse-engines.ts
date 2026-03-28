import { readdir, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import type { TableRow } from './parse-markdown-table'
import { findAllTables } from './parse-markdown-table'
import type { EngineOperator } from './types'

interface Section {
  name: string
  startLine: number
}

interface ColumnMap {
  operator: string
  syntax: string
  example?: string
  description?: string
}

/** Extract ## headings as engine sections, stripping parenthetical suffixes. */
function parseSections(lines: string[]): Section[] {
  const sections: Section[] = []
  for (let i = 0; i < lines.length; i++) {
    const match = lines[i].match(/^## (.+)/)
    if (!match) continue
    const raw = match[1].trim()
    if (raw.toLowerCase() === 'table of contents') continue
    const name = raw.replace(/\s*\(.*\)\s*$/, '').trim()
    sections.push({ name, startLine: i })
  }
  return sections
}

/** Find which engine section a line belongs to. */
function engineForLine(sections: Section[], lineIdx: number): string | null {
  for (let s = sections.length - 1; s >= 0; s--) {
    if (lineIdx >= sections[s].startLine) return sections[s].name
  }
  return null
}

/** Find the line index where a table starts by matching its first data cell. */
function findTableLine(lines: string[], firstCellValue: string, searchFrom: number): number {
  for (let i = searchFrom; i < lines.length; i++) {
    if (lines[i].includes(firstCellValue) && lines[i].includes('|')) {
      return Math.max(0, i - 2)
    }
  }
  return -1
}

/** Detect Operator/Syntax columns in a table, returning a ColumnMap or null. */
function detectColumns(headers: string[]): ColumnMap | null {
  const operatorCol = headers.find((h) => h.toLowerCase() === 'operator')
  const syntaxCol = headers.find((h) => h.toLowerCase() === 'syntax')
  if (!operatorCol || !syntaxCol) return null
  const exampleCol = headers.find((h) => h.toLowerCase() === 'example')
  const descCol = headers.find((h) => h !== operatorCol && h !== syntaxCol && h !== exampleCol)
  return { operator: operatorCol, syntax: syntaxCol, example: exampleCol, description: descCol }
}

/** Convert a parsed table row into an EngineOperator. */
function rowToOperator(row: TableRow, engine: string, cols: ColumnMap): EngineOperator {
  return {
    engine,
    operator: row[cols.operator] ?? '',
    syntax: row[cols.syntax] ?? '',
    example: cols.example ? (row[cols.example] ?? '') : '',
    description: cols.description ? (row[cols.description] ?? '') : '',
  }
}

/** Extract operators from a single markdown file. */
function extractFromFile(content: string): Record<string, EngineOperator[]> {
  const lines = content.split('\n')
  const sections = parseSections(lines)
  const tables = findAllTables(content)
  const result: Record<string, EngineOperator[]> = {}

  let searchFrom = 0
  for (const table of tables) {
    if (table.length === 0) continue
    const cols = detectColumns(Object.keys(table[0]))
    if (!cols) continue

    const tableLine = findTableLine(lines, table[0][cols.operator], searchFrom)
    if (tableLine >= 0) searchFrom = tableLine + 3

    const engine = tableLine >= 0 ? engineForLine(sections, tableLine) : null
    if (!engine) continue

    if (!result[engine]) result[engine] = []
    for (const row of table) {
      result[engine].push(rowToOperator(row, engine, cols))
    }
  }

  return result
}

/**
 * Parse engine reference markdown files into operator lookup.
 * Reads references/engines/*.md, finds tables with Operator/Syntax columns,
 * and returns Record<string, EngineOperator[]> keyed by engine name.
 */
export async function parseEngineReferences(
  skillPath: string
): Promise<Record<string, EngineOperator[]>> {
  const enginesDir = join(skillPath, 'references', 'engines')
  const files = await readdir(enginesDir)
  const mdFiles = files.filter((f) => f.endsWith('.md'))

  const result: Record<string, EngineOperator[]> = {}

  for (const file of mdFiles) {
    const content = await readFile(join(enginesDir, file), 'utf-8')
    const fileResult = extractFromFile(content)
    for (const [engine, ops] of Object.entries(fileResult)) {
      if (!result[engine]) result[engine] = []
      result[engine].push(...ops)
    }
  }

  return result
}
