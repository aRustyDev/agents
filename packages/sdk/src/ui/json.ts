/**
 * JsonRenderer — machine-readable JSON output for programmatic consumption.
 */

import type { ProgressHandle, Renderer, TreeNode } from './interface'

const noopProgress: ProgressHandle = {
  update() {},
  success() {},
  error() {},
}

export function createJsonRenderer(): Renderer {
  return {
    table(data) {
      console.log(JSON.stringify(data))
    },

    tree(_label: string, children: TreeNode[]) {
      console.log(JSON.stringify(children))
    },

    success(_msg: string, data?: unknown) {
      if (data !== undefined) console.log(JSON.stringify(data))
    },

    error(msg: string, data?: unknown) {
      console.error(
        JSON.stringify({
          error: msg,
          ...(data && typeof data === 'object' ? (data as object) : {}),
        })
      )
    },

    warn(_msg: string, data?: unknown) {
      if (data !== undefined) console.log(JSON.stringify(data))
    },

    info(_msg: string, data?: unknown) {
      if (data !== undefined) console.log(JSON.stringify(data))
    },

    ndjson(data) {
      console.log(JSON.stringify(data))
    },

    progress() {
      return noopProgress
    },

    raw(data) {
      console.log(JSON.stringify(data))
    },
  }
}
