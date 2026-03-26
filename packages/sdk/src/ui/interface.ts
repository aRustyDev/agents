/**
 * Renderer interface — the contract every output adapter must satisfy.
 *
 * Adapters: CliRenderer (human-friendly), JsonRenderer (machine), SilentRenderer (noop).
 */

export interface TreeNode {
  label: string
  children?: TreeNode[]
}

export interface ProgressHandle {
  update(opts: { text: string }): void
  success(opts?: { text?: string }): void
  error(opts?: { text?: string }): void
}

export interface Renderer {
  table(data: Record<string, unknown>[], columns?: string[]): void
  tree(label: string, children: TreeNode[]): void
  success(message: string, data?: unknown): void
  error(message: string, data?: unknown): void
  warn(message: string, data?: unknown): void
  info(message: string, data?: unknown): void
  ndjson(data: Record<string, unknown>): void
  progress(message: string): ProgressHandle
  raw(data: unknown): void
}
