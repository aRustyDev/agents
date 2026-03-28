import { describe, expect, it } from 'bun:test'
import { clampLimit, clampPage, emptyPage, paginateArray } from '../../src/providers/pagination'

describe('clampLimit', () => {
  it('defaults to 10 when undefined', () => {
    expect(clampLimit(undefined)).toBe(10)
  })

  it('defaults to 10 when NaN', () => {
    expect(clampLimit(NaN)).toBe(10)
  })

  it('clamps to 1 when below minimum', () => {
    expect(clampLimit(0)).toBe(1)
    expect(clampLimit(-5)).toBe(1)
  })

  it('clamps to 100 when above maximum', () => {
    expect(clampLimit(200)).toBe(100)
    expect(clampLimit(101)).toBe(100)
  })

  it('passes through valid values', () => {
    expect(clampLimit(1)).toBe(1)
    expect(clampLimit(50)).toBe(50)
    expect(clampLimit(100)).toBe(100)
  })
})

describe('clampPage', () => {
  it('defaults to 1 when undefined', () => {
    expect(clampPage(undefined)).toBe(1)
  })

  it('defaults to 1 when NaN', () => {
    expect(clampPage(NaN)).toBe(1)
  })

  it('clamps to 1 when below minimum', () => {
    expect(clampPage(0)).toBe(1)
    expect(clampPage(-3)).toBe(1)
  })

  it('floors fractional pages', () => {
    expect(clampPage(2.7)).toBe(2)
    expect(clampPage(1.1)).toBe(1)
  })

  it('passes through valid integers', () => {
    expect(clampPage(1)).toBe(1)
    expect(clampPage(5)).toBe(5)
    expect(clampPage(999)).toBe(999)
  })
})

describe('paginateArray', () => {
  const items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

  it('returns first page correctly', () => {
    const result = paginateArray(items, 1, 3)
    expect(result.items).toEqual([1, 2, 3])
    expect(result.page).toBe(1)
    expect(result.pageSize).toBe(3)
    expect(result.hasMore).toBe(true)
    expect(result.total).toBe(10)
  })

  it('returns middle page correctly', () => {
    const result = paginateArray(items, 2, 3)
    expect(result.items).toEqual([4, 5, 6])
    expect(result.hasMore).toBe(true)
  })

  it('returns last page correctly', () => {
    const result = paginateArray(items, 4, 3)
    expect(result.items).toEqual([10])
    expect(result.hasMore).toBe(false)
  })

  it('returns empty for out-of-range page', () => {
    const result = paginateArray(items, 100, 3)
    expect(result.items).toEqual([])
    expect(result.hasMore).toBe(false)
    expect(result.total).toBe(10)
  })

  it('paginates with page size larger than array', () => {
    const result = paginateArray(items, 1, 50)
    expect(result.items).toEqual(items)
    expect(result.hasMore).toBe(false)
  })

  it('handles empty array', () => {
    const result = paginateArray([], 1, 10)
    expect(result.items).toEqual([])
    expect(result.hasMore).toBe(false)
    expect(result.total).toBe(0)
  })
})

describe('emptyPage', () => {
  it('returns a properly shaped empty result', () => {
    const result = emptyPage(3, 25)
    expect(result.items).toEqual([])
    expect(result.page).toBe(3)
    expect(result.pageSize).toBe(25)
    expect(result.hasMore).toBe(false)
    expect(result.total).toBe(0)
  })
})
