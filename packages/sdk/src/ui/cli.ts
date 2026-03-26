/**
 * CliRenderer — human-friendly terminal output with colors, tables, and spinners.
 *
 * Ported from `@agents/core` output.ts. Implements the Renderer interface.
 * The `spinner()` method is kept as a deprecated alias for `progress()`.
 */

import ansis from 'ansis'
import { printTable } from 'console-table-printer'
import { createSpinner } from 'nanospinner'

import type { ProgressHandle, Renderer, TreeNode } from './interface'

// ---------------------------------------------------------------------------
// No-op progress handle (used in quiet mode)
// ---------------------------------------------------------------------------

const noopProgress: ProgressHandle = {
  update() {},
  success() {},
  error() {},
}

// ---------------------------------------------------------------------------
// Tree rendering helpers
// ---------------------------------------------------------------------------

function renderTree(nodes: TreeNode[], prefix: string): string[] {
  const lines: string[] = []
  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i] as TreeNode
    const isLast = i === nodes.length - 1
    const connector = isLast ? '\u2514\u2500\u2500 ' : '\u251c\u2500\u2500 '
    const childPrefix = isLast ? '    ' : '\u2502   '

    lines.push(`${prefix}${connector}${node.label}`)
    if (node.children && node.children.length > 0) {
      lines.push(...renderTree(node.children, `${prefix}${childPrefix}`))
    }
  }
  return lines
}

// ---------------------------------------------------------------------------
// Column filtering helper
// ---------------------------------------------------------------------------

function filterColumns(
  data: Record<string, unknown>[],
  columns: string[]
): Record<string, unknown>[] {
  return data.map((row) => {
    const filtered: Record<string, unknown> = {}
    for (const col of columns) {
      if (col in row) {
        filtered[col] = row[col]
      }
    }
    return filtered
  })
}

// ---------------------------------------------------------------------------
// CliRenderer (human-friendly)
// ---------------------------------------------------------------------------

export interface CliRendererOptions {
  json?: boolean
  quiet?: boolean
}

/**
 * Create a human-friendly CLI renderer.
 *
 * When `json` is true the renderer delegates to the JSON formatter from core
 * for backward compatibility; prefer `createJsonRenderer()` for new code.
 */
export function createCliRenderer(opts?: CliRendererOptions): Renderer {
  const quiet = opts?.quiet ?? false

  return {
    table(data, columns) {
      const output = columns ? filterColumns(data, columns) : data
      printTable(output)
    },

    success(message) {
      if (!quiet) {
        console.log(ansis.green(`[ok] ${message}`))
      }
    },

    error(message) {
      console.error(ansis.red(`[error] ${message}`))
    },

    warn(message) {
      console.error(ansis.yellow(`[warn] ${message}`))
    },

    info(message) {
      if (!quiet) {
        console.log(ansis.cyan(`[info] ${message}`))
      }
    },

    tree(label, children) {
      console.log(ansis.bold(label))
      const lines = renderTree(children, '')
      for (const line of lines) {
        console.log(line)
      }
    },

    ndjson() {
      // No-op in human mode
    },

    raw(data) {
      console.log(data)
    },

    progress(message) {
      if (quiet) return noopProgress

      const s = createSpinner(message).start()
      return {
        update(o) {
          s.update(o)
        },
        success(o) {
          s.success(o)
        },
        error(o) {
          s.error(o)
        },
      }
    },
  }
}

/**
 * @deprecated Use `createCliRenderer` and its `progress()` method instead.
 *
 * Backward-compatible alias — returns a renderer whose `progress()` method
 * is also available as `spinner()`.
 */
export function createOutput(opts: {
  json: boolean
  quiet: boolean
}): Renderer & { spinner(message: string): ProgressHandle } {
  const renderer = createCliRenderer({ quiet: opts.quiet })
  return {
    ...renderer,
    /** @deprecated Use `progress()` instead. */
    spinner(message: string): ProgressHandle {
      return renderer.progress(message)
    },
  }
}
