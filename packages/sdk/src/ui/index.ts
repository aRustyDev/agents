/**
 * ui/ barrel — factory + re-exports for all renderer adapters.
 */

import { createCliRenderer } from './cli'
import type { Renderer } from './interface'
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

// Backward compat alias
export { createCliRenderer, createOutput } from './cli'
export * from './interface'
export { createJsonRenderer } from './json'
export { createSilentRenderer } from './silent'
