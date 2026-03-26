import { describe, expect, test } from 'bun:test'
import { findAllTables, parseMarkdownTable, type TableRow } from '../src/parse-markdown-table'

const SIMPLE_TABLE = `
| # | Engine(s) | Query | Operators |
|---|-----------|-------|-----------|
| 1 | Google | CRDT typescript | site:dev.to |
| 2 | GitHub, npm | offline sync | stars:>50 |
`.trim()

describe('parseMarkdownTable', () => {
  test('parses a simple table into row objects', () => {
    const rows = parseMarkdownTable(SIMPLE_TABLE)
    expect(rows).toHaveLength(2)
    expect(rows[0]).toEqual({
      '#': '1',
      'Engine(s)': 'Google',
      Query: 'CRDT typescript',
      Operators: 'site:dev.to',
    })
    expect(rows[1]['Engine(s)']).toBe('GitHub, npm')
  })

  test('returns empty array for non-table input', () => {
    expect(parseMarkdownTable('just some text')).toEqual([])
    expect(parseMarkdownTable('')).toEqual([])
  })

  test('handles single-row table', () => {
    const table = '| A | B |\n|---|---|\n| 1 | 2 |'
    const rows = parseMarkdownTable(table)
    expect(rows).toHaveLength(1)
    expect(rows[0]).toEqual({ A: '1', B: '2' })
  })

  test('trims whitespace from headers and cells', () => {
    const table = '|  Name  |  Value  |\n|---|---|\n|  foo  |  bar  |'
    const rows = parseMarkdownTable(table)
    expect(rows[0]).toEqual({ Name: 'foo', Value: 'bar' })
  })
})

describe('findAllTables', () => {
  test('finds multiple tables in a document', () => {
    const doc = `# Heading

| A | B |
|---|---|
| 1 | 2 |

Some text between tables.

| X | Y |
|---|---|
| 3 | 4 |
| 5 | 6 |`
    const tables = findAllTables(doc)
    expect(tables).toHaveLength(2)
    expect(tables[0]).toHaveLength(1)
    expect(tables[1]).toHaveLength(2)
    expect(tables[0][0]).toEqual({ A: '1', B: '2' })
    expect(tables[1][1]).toEqual({ X: '5', Y: '6' })
  })

  test('returns empty array for document with no tables', () => {
    expect(findAllTables('just text\nmore text')).toEqual([])
  })
})
