import type { PaginatedResult } from './types'

/** Clamp limit to [1, 100], default 10. Handles NaN. */
export function clampLimit(limit: number | undefined): number {
  const raw = limit ?? 10
  if (Number.isNaN(raw)) return 10
  return Math.max(1, Math.min(100, raw))
}

/** Clamp page to >= 1, default 1. Handles NaN. */
export function clampPage(page: number | undefined): number {
  const raw = page ?? 1
  if (Number.isNaN(raw)) return 1
  return Math.max(1, Math.floor(raw))
}

/** Paginate an in-memory array. */
export function paginateArray<T>(items: T[], page: number, pageSize: number): PaginatedResult<T> {
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const slice = items.slice(start, end)
  return {
    items: slice,
    page,
    pageSize,
    hasMore: end < items.length,
    total: items.length,
  }
}

/** Return an empty paginated result. */
export function emptyPage<T>(page: number, pageSize: number): PaginatedResult<T> {
  return { items: [], page, pageSize, hasMore: false, total: 0 }
}
