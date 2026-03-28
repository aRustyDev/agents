/**
 * SilentRenderer — noop adapter for tests and headless environments.
 */

import type { ProgressHandle, Renderer } from './interface'

const noopProgress: ProgressHandle = {
  update() {},
  success() {},
  error() {},
}

export function createSilentRenderer(): Renderer {
  return {
    table() {},
    tree() {},
    success() {},
    error() {},
    warn() {},
    info() {},
    ndjson() {},
    progress() {
      return noopProgress
    },
    raw() {},
  }
}
