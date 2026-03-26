import { afterEach, beforeEach, describe, expect, it } from 'bun:test'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import {
  parseNdjson,
  readNdjsonFile,
  serializeNdjson,
  writeNdjsonFile,
} from '../../src/catalog/ndjson/io'

describe('parseNdjson', () => {
  it('parses valid NDJSON', () => {
    const input = '{"a":1}\n{"a":2}\n'
    const result = parseNdjson<{ a: number }>(input)
    expect(result).toEqual([{ a: 1 }, { a: 2 }])
  })

  it('handles empty lines', () => {
    const input = '{"a":1}\n\n{"a":2}\n\n'
    const result = parseNdjson<{ a: number }>(input)
    expect(result).toEqual([{ a: 1 }, { a: 2 }])
  })

  it('handles empty string', () => {
    const result = parseNdjson<unknown>('')
    expect(result).toEqual([])
  })

  it('handles whitespace-only lines', () => {
    const input = '{"x":"y"}\n   \n{"x":"z"}\n'
    const result = parseNdjson<{ x: string }>(input)
    expect(result).toEqual([{ x: 'y' }, { x: 'z' }])
  })
})

describe('serializeNdjson', () => {
  it('produces valid NDJSON', () => {
    const entries = [{ a: 1 }, { a: 2 }]
    const output = serializeNdjson(entries)
    expect(output).toBe('{"a":1}\n{"a":2}\n')
  })

  it('handles single entry', () => {
    const output = serializeNdjson([{ key: 'value' }])
    expect(output).toBe('{"key":"value"}\n')
  })

  it('handles empty array', () => {
    const output = serializeNdjson([])
    expect(output).toBe('\n')
  })
})

describe('readNdjsonFile / writeNdjsonFile', () => {
  let dir: string

  beforeEach(() => {
    dir = mkdtempSync(join(tmpdir(), 'ndjson-io-'))
  })

  afterEach(() => {
    rmSync(dir, { recursive: true, force: true })
  })

  it('returns empty array for missing file', async () => {
    const result = await readNdjsonFile(join(dir, 'does-not-exist.ndjson'))
    expect(result.ok).toBe(true)
    if (result.ok) expect(result.value).toEqual([])
  })

  it('round-trips data through write then read', async () => {
    const filePath = join(dir, 'test.ndjson')
    const data = [
      { name: 'alpha', count: 1 },
      { name: 'beta', count: 2 },
    ]

    const writeResult = await writeNdjsonFile(filePath, data)
    expect(writeResult.ok).toBe(true)

    const readResult = await readNdjsonFile<{ name: string; count: number }>(filePath)
    expect(readResult.ok).toBe(true)
    if (readResult.ok) expect(readResult.value).toEqual(data)
  })

  it('overwrites previous content atomically', async () => {
    const filePath = join(dir, 'overwrite.ndjson')
    await writeNdjsonFile(filePath, [{ v: 1 }])
    await writeNdjsonFile(filePath, [{ v: 2 }, { v: 3 }])

    const readResult = await readNdjsonFile<{ v: number }>(filePath)
    expect(readResult.ok).toBe(true)
    if (readResult.ok) {
      expect(readResult.value).toEqual([{ v: 2 }, { v: 3 }])
    }
  })
})
