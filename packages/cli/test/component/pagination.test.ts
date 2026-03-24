import { describe, expect, test } from 'bun:test'
import { clampLimit, clampPage, emptyPage, paginateArray } from '../../src/lib/component/pagination'

describe('clampLimit', () => {
  test('defaults to 10', () => expect(clampLimit(undefined)).toBe(10))
  test('clamps 0 to 1', () => expect(clampLimit(0)).toBe(1))
  test('clamps 500 to 100', () => expect(clampLimit(500)).toBe(100))
  test('passes through 25', () => expect(clampLimit(25)).toBe(25))
  test('handles NaN', () => expect(clampLimit(NaN)).toBe(10))
})

describe('clampPage', () => {
  test('defaults to 1', () => expect(clampPage(undefined)).toBe(1))
  test('clamps 0 to 1', () => expect(clampPage(0)).toBe(1))
  test('clamps -1 to 1', () => expect(clampPage(-1)).toBe(1))
  test('passes through 5', () => expect(clampPage(5)).toBe(5))
  test('handles NaN', () => expect(clampPage(NaN)).toBe(1))
})

describe('paginateArray', () => {
  const items = ['a', 'b', 'c', 'd', 'e']

  test('returns first page', () => {
    const result = paginateArray(items, 1, 2)
    expect(result.items).toEqual(['a', 'b'])
    expect(result.page).toBe(1)
    expect(result.pageSize).toBe(2)
    expect(result.hasMore).toBe(true)
    expect(result.total).toBe(5)
  })

  test('returns middle page', () => {
    const result = paginateArray(items, 2, 2)
    expect(result.items).toEqual(['c', 'd'])
    expect(result.hasMore).toBe(true)
  })

  test('returns last page', () => {
    const result = paginateArray(items, 3, 2)
    expect(result.items).toEqual(['e'])
    expect(result.hasMore).toBe(false)
  })

  test('returns empty for out-of-range page', () => {
    const result = paginateArray(items, 10, 2)
    expect(result.items).toEqual([])
    expect(result.hasMore).toBe(false)
  })

  test('handles empty array', () => {
    const result = paginateArray([], 1, 10)
    expect(result.items).toEqual([])
    expect(result.hasMore).toBe(false)
    expect(result.total).toBe(0)
  })

  test('single page fits all items', () => {
    const result = paginateArray(items, 1, 100)
    expect(result.items).toEqual(items)
    expect(result.hasMore).toBe(false)
    expect(result.total).toBe(5)
  })
})

describe('emptyPage', () => {
  test('returns empty paginated result', () => {
    const result = emptyPage(3, 10)
    expect(result.items).toEqual([])
    expect(result.page).toBe(3)
    expect(result.pageSize).toBe(10)
    expect(result.hasMore).toBe(false)
    expect(result.total).toBe(0)
  })
})
