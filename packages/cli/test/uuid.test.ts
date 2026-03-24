import { describe, expect, test } from 'bun:test'
import { UUID_NAMESPACE, uuid4, uuid5, uuid7 } from '../src/lib/uuid'

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/

describe('uuid4', () => {
  test('returns valid UUID format', () => {
    expect(uuid4()).toMatch(UUID_REGEX)
  })

  test('has version 4 marker', () => {
    const id = uuid4()
    expect(id[14]).toBe('4')
  })

  test('has RFC 4122 variant marker', () => {
    const id = uuid4()
    const variantChar = parseInt(id[19]!, 16)
    expect(variantChar & 0xc).toBe(0x8) // 10xx binary
  })

  test('generates unique values', () => {
    const ids = new Set(Array.from({ length: 100 }, () => uuid4()))
    expect(ids.size).toBe(100)
  })
})

describe('uuid5', () => {
  test('returns valid UUID format', async () => {
    const id = await uuid5(UUID_NAMESPACE.DNS, 'example.com')
    expect(id).toMatch(UUID_REGEX)
  })

  test('has version 5 marker', async () => {
    const id = await uuid5(UUID_NAMESPACE.DNS, 'test')
    expect(id[14]).toBe('5')
  })

  test('has RFC 4122 variant marker', async () => {
    const id = await uuid5(UUID_NAMESPACE.DNS, 'test')
    const variantChar = parseInt(id[19]!, 16)
    expect(variantChar & 0xc).toBe(0x8)
  })

  test('is deterministic (same input = same output)', async () => {
    const a = await uuid5(UUID_NAMESPACE.DNS, 'example.com')
    const b = await uuid5(UUID_NAMESPACE.DNS, 'example.com')
    expect(a).toBe(b)
  })

  test('different names produce different UUIDs', async () => {
    const a = await uuid5(UUID_NAMESPACE.DNS, 'foo.com')
    const b = await uuid5(UUID_NAMESPACE.DNS, 'bar.com')
    expect(a).not.toBe(b)
  })

  test('different namespaces produce different UUIDs', async () => {
    const a = await uuid5(UUID_NAMESPACE.DNS, 'test')
    const b = await uuid5(UUID_NAMESPACE.URL, 'test')
    expect(a).not.toBe(b)
  })
})

describe('uuid7', () => {
  test('returns valid UUID format', () => {
    expect(uuid7()).toMatch(UUID_REGEX)
  })

  test('has version 7 marker', () => {
    const id = uuid7()
    expect(id[14]).toBe('7')
  })

  test('has RFC 4122 variant marker', () => {
    const id = uuid7()
    const variantChar = parseInt(id[19]!, 16)
    expect(variantChar & 0xc).toBe(0x8)
  })

  test('sorts chronologically across distinct timestamps', async () => {
    const ids: string[] = []
    for (let i = 0; i < 5; i++) {
      ids.push(uuid7())
      await Bun.sleep(2) // Ensure distinct millisecond timestamps
    }
    const sorted = [...ids].sort()
    expect(ids).toEqual(sorted)
  })

  test('generates unique values', () => {
    const ids = new Set(Array.from({ length: 100 }, () => uuid7()))
    expect(ids.size).toBe(100)
  })

  test('embeds current timestamp', () => {
    const before = Date.now()
    const id = uuid7()
    const after = Date.now()

    // Extract timestamp from UUID (first 12 hex chars = 48 bits)
    const hex = id.replace(/-/g, '').slice(0, 12)
    const timestamp = parseInt(hex, 16)

    expect(timestamp).toBeGreaterThanOrEqual(before)
    expect(timestamp).toBeLessThanOrEqual(after)
  })
})
