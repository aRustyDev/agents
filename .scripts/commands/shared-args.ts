/**
 * Global CLI arguments shared across all commands via the Citty spread pattern.
 * Env var fallback follows the convention AI_TOOLS_<FLAG_NAME>.
 */
import type { ArgDef } from 'citty'

function envDefault<T>(envVar: string, fallback: T): T {
  const val = process.env[envVar]
  if (val === undefined) return fallback
  if (typeof fallback === 'boolean') return (val === 'true' || val === '1') as T
  return val as T
}

export const globalArgs = {
  verbose: {
    type: 'boolean',
    alias: 'v',
    description: 'Verbose output (env: AI_TOOLS_VERBOSE)',
    default: envDefault('AI_TOOLS_VERBOSE', false),
  },
  json: {
    type: 'boolean',
    description: 'JSON output (env: AI_TOOLS_JSON)',
    default: envDefault('AI_TOOLS_JSON', false),
  },
  quiet: {
    type: 'boolean',
    alias: 'q',
    description: 'Suppress non-essential output',
    default: false,
  },
} as const satisfies Record<string, ArgDef>
