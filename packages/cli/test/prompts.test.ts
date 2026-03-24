import { describe, expect, test } from 'bun:test'
import { cancelSymbol } from '../src/lib/prompts/index'

describe('cancelSymbol', () => {
  test('is a unique symbol', () => {
    expect(typeof cancelSymbol).toBe('symbol')
    expect(cancelSymbol.toString()).toContain('cancel')
  })

  test('is not equal to any other symbol', () => {
    const other = Symbol('cancel')
    expect(cancelSymbol).not.toBe(other)
  })
})

describe('confirm (non-interactive)', () => {
  const getConfirm = async () => {
    const mod = await import('../src/lib/prompts/confirm')
    return mod.confirm
  }

  test('returns default when yes=true', async () => {
    const confirm = await getConfirm()
    const result = await confirm({ message: 'Continue?', yes: true })
    expect(result).toBe(false)
  })

  test('returns custom default when yes=true', async () => {
    const confirm = await getConfirm()
    const result = await confirm({ message: 'Continue?', default: true, yes: true })
    expect(result).toBe(true)
  })

  test('returns default in non-TTY environment', async () => {
    const confirm = await getConfirm()
    const result = await confirm({ message: 'Continue?', default: true })
    expect(result).toBe(true)
  })
})

describe('searchMultiselect (non-interactive)', () => {
  const getMultiselect = async () => {
    const mod = await import('../src/lib/prompts/search-multiselect')
    return mod.searchMultiselect
  }

  test('returns initial and locked items when yes=true', async () => {
    const searchMultiselect = await getMultiselect()
    const result = await searchMultiselect({
      message: 'Select items:',
      items: [
        { label: 'A', value: 'a', locked: true },
        { label: 'B', value: 'b' },
        { label: 'C', value: 'c' },
      ],
      initial: ['c'],
      yes: true,
    })
    expect(Array.isArray(result)).toBe(true)
    if (Array.isArray(result)) {
      expect(result).toContain('a')
      expect(result).toContain('c')
      expect(result).not.toContain('b')
    }
  })

  test('returns empty array when no items and yes=true', async () => {
    const searchMultiselect = await getMultiselect()
    const result = await searchMultiselect({
      message: 'Select:',
      items: [],
      yes: true,
    })
    expect(result).toEqual([])
  })

  test('returns all locked items when yes=true', async () => {
    const searchMultiselect = await getMultiselect()
    const result = await searchMultiselect({
      message: 'Select:',
      items: [
        { label: 'A', value: 'a', locked: true },
        { label: 'B', value: 'b', locked: true },
      ],
      yes: true,
    })
    expect(Array.isArray(result)).toBe(true)
    if (Array.isArray(result)) {
      expect(result).toContain('a')
      expect(result).toContain('b')
    }
  })

  test('returns only locked when no initial and yes=true', async () => {
    const searchMultiselect = await getMultiselect()
    const result = await searchMultiselect({
      message: 'Select:',
      items: [
        { label: 'A', value: 'a', locked: true },
        { label: 'B', value: 'b' },
      ],
      yes: true,
    })
    expect(Array.isArray(result)).toBe(true)
    if (Array.isArray(result)) {
      expect(result).toContain('a')
      expect(result).not.toContain('b')
    }
  })
})
