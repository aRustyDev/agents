/**
 * Core types, Result monad, and error handling for ai-tools.
 */

// ---------------------------------------------------------------------------
// Result<T, E>
// ---------------------------------------------------------------------------

export type Result<T, E = CliError> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E }

export const ok = <T>(value: T): Result<T, never> => ({ ok: true, value })
export const err = <E>(error: E): Result<never, E> => ({ ok: false, error })

/**
 * Unwrap a Result or exit the process with a user-friendly message.
 * Use in CLI command handlers where failure means "stop".
 */
export function unwrapOrExit<T>(result: Result<T>): T {
  if (result.ok) return result.value
  console.error(result.error.display())
  process.exit(2)
}

/**
 * Wrap an async function that might throw into a Result.
 */
export async function tryAsync<T>(
  fn: () => Promise<T>,
  mapError: (e: unknown) => CliError
): Promise<Result<T>> {
  try {
    return ok(await fn())
  } catch (e) {
    return err(mapError(e))
  }
}

// ---------------------------------------------------------------------------
// CliError
// ---------------------------------------------------------------------------

export class CliError {
  constructor(
    readonly message: string,
    readonly code: string,
    readonly hint?: string,
    readonly cause?: unknown
  ) {}

  display(): string {
    let output = `error[${this.code}]: ${this.message}`
    if (this.hint) output += `\n  hint: ${this.hint}`
    return output
  }
}

// ---------------------------------------------------------------------------
// Shared enums / constants
// ---------------------------------------------------------------------------

export type EntityType =
  | 'skill'
  | 'plugin'
  | 'command'
  | 'agent'
  | 'rule'
  | 'output-style'
  | 'claude_md'
  | 'mcp-server'

export type SourceFormat = 'legacy' | 'extended' | 'planning'

export type StalenessStatus = 'fresh' | 'stale' | 'missing' | 'forked' | 'no-hash'

// Exit codes used across all commands
export const EXIT = {
  OK: 0,
  FAILURES: 1,
  ERROR: 2,
} as const
