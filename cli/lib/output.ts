/**
 * Unified dual-mode output formatter.
 *
 * Factory `createOutput()` returns a formatter that emits either structured
 * JSON (for machine consumption) or human-readable colored text depending
 * on the `json` flag.
 */

import ansis from 'ansis'
import { printTable } from 'console-table-printer'
import { createSpinner } from 'nanospinner'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface TreeNode {
  label: string
  children?: TreeNode[]
}

export interface SpinnerHandle {
  success(opts?: { text?: string }): void
  error(opts?: { text?: string }): void
  update(opts: { text: string }): void
}

export interface OutputFormatter {
  table(data: Record<string, unknown>[], columns?: string[]): void
  success(message: string, data?: unknown): void
  error(message: string, data?: unknown): void
  warn(message: string, data?: unknown): void
  info(message: string, data?: unknown): void
  tree(label: string, children: TreeNode[]): void
  ndjson(data: Record<string, unknown>): void
  raw(data: unknown): void
  spinner(message: string): SpinnerHandle
}

// ---------------------------------------------------------------------------
// No-op spinner (used in JSON mode and quiet mode)
// ---------------------------------------------------------------------------

const noopSpinner: SpinnerHandle = {
  success() {},
  error() {},
  update() {},
}

// ---------------------------------------------------------------------------
// Tree rendering helpers (human mode)
// ---------------------------------------------------------------------------

function renderTree(nodes: TreeNode[], prefix: string): string[] {
  const lines: string[] = []
  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i]!
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
// JSON formatter
// ---------------------------------------------------------------------------

function createJsonFormatter(): OutputFormatter {
  return {
    table(data, columns) {
      const output = columns ? filterColumns(data, columns) : data
      console.log(JSON.stringify(output, null, 2))
    },

    success(message, data) {
      console.log(
        JSON.stringify({
          status: 'success',
          message,
          ...(data !== undefined && { data }),
        })
      )
    },

    error(message, data) {
      console.error(
        JSON.stringify({
          status: 'error',
          message,
          ...(data !== undefined && { data }),
        })
      )
    },

    warn(message, data) {
      console.error(
        JSON.stringify({
          status: 'warning',
          message,
          ...(data !== undefined && { data }),
        })
      )
    },

    info(message, data) {
      console.log(
        JSON.stringify({
          status: 'info',
          message,
          ...(data !== undefined && { data }),
        })
      )
    },

    tree(label, children) {
      console.log(JSON.stringify({ label, children }, null, 2))
    },

    ndjson(data) {
      console.log(JSON.stringify(data))
    },

    raw(data) {
      console.log(JSON.stringify(data, null, 2))
    },

    spinner() {
      return noopSpinner
    },
  }
}

// ---------------------------------------------------------------------------
// Human formatter
// ---------------------------------------------------------------------------

function createHumanFormatter(quiet: boolean): OutputFormatter {
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

    spinner(message) {
      if (quiet) return noopSpinner

      const s = createSpinner(message).start()
      return {
        success(opts) {
          s.success(opts)
        },
        error(opts) {
          s.error(opts)
        },
        update(opts) {
          s.update(opts)
        },
      }
    },
  }
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------

export function createOutput(opts: { json: boolean; quiet: boolean }): OutputFormatter {
  return opts.json ? createJsonFormatter() : createHumanFormatter(opts.quiet)
}
