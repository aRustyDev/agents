/**
 * @agents/sdk — Domain framework layer between @agents/core and consumer tools.
 *
 * Surfaces:
 *   - util/      — Logger, tracer, metrics, error types
 *   - context/   — Component model (parse, validate, frontmatter)
 *   - providers/ — Provider manager and adapters
 *   - catalog/   — Storage-agnostic catalog operations
 *   - ui/        — Renderer interface for CLI/TUI output
 */

export * from './catalog'
export * from './context'
export * from './providers'
export * from './ui'
export * from './util'
