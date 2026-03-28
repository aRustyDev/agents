/**
 * ui/ barrel — factory + re-exports for all renderer adapters.
 */

import { createCliRenderer } from './cli'
import type { ProgressHandle, Renderer } from './interface'
import { createJsonRenderer } from './json'
import { createSilentRenderer } from './silent'

export function createRenderer(opts?: {
  mode?: 'cli' | 'json' | 'silent'
  quiet?: boolean
}): Renderer {
  const mode = opts?.mode ?? 'cli'
  if (mode === 'json') return createJsonRenderer()
  if (mode === 'silent') return createSilentRenderer()
  return createCliRenderer({ json: false, quiet: opts?.quiet ?? false })
}

// Backward compat aliases
export { createCliRenderer, createOutput } from './cli'
export * from './interface'
export { createJsonRenderer } from './json'
export { createSilentRenderer } from './silent'

// Legacy type aliases for CLI backward compatibility
/** @deprecated Use `Renderer` instead. */
export type OutputFormatter = Renderer & { spinner(message: string): ProgressHandle }
/** @deprecated Use `ProgressHandle` instead. */
export type SpinnerHandle = ProgressHandle
