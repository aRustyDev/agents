/**
 * Skill discovery command module.
 *
 * Searches for skills across registries (skills.sh, Meilisearch, offline
 * catalog) and formats the results as a table or JSON.
 */

import { createOutput, type OutputFormatter } from '../../../ui'
import type { SearchBackendType, SkillSearchResult } from '../schemas'
import { searchSkillsAPI } from './search-api'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface FindOptions {
  /** Maximum results (1..100, default 10). */
  limit?: number
  /** Emit machine-readable JSON instead of a table. */
  json?: boolean
  /** Suppress informational output. */
  quiet?: boolean
  /** Restrict search to a single backend. */
  source?: SearchBackendType
  /** Target agent (reserved for future interactive install). */
  agent?: string
  /** Skip confirmation prompts (reserved for future install flow). */
  yes?: boolean
  /** Working directory override. */
  cwd?: string
  /** Override catalog path (exposed for testing). */
  catalogPath?: string
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Search for skills across registries and display the results.
 *
 * Non-interactive path (query provided or non-TTY):
 *   - Calls `searchSkillsAPI`, formats as table or JSON.
 *
 * Interactive path (TTY, no query):
 *   - Prints a usage hint (full interactive deferred).
 */
export async function findSkills(args: string[], opts: FindOptions): Promise<void> {
  const out = createOutput({
    json: opts.json ?? false,
    quiet: opts.quiet ?? false,
  })
  const query = args[0] ?? ''

  // ------------------------------------------------------------------
  // Non-interactive: query was provided, or stdout is not a TTY
  // ------------------------------------------------------------------
  if (query || !process.stdout.isTTY) {
    if (!query && !process.stdout.isTTY) {
      out.warn('Non-TTY detected, skipping interactive mode')
    }

    const results = await searchSkillsAPI(query, {
      limit: opts.limit,
      source: opts.source,
      catalogPath: opts.catalogPath,
    })

    if (opts.json) {
      out.raw(results)
      return
    }

    if (results.length === 0) {
      out.info('No skills found')
      return
    }

    formatResultsTable(out, results)
    return
  }

  // ------------------------------------------------------------------
  // Interactive: no query, TTY -- show usage hints
  // ------------------------------------------------------------------
  out.info('Usage: just agents skill find "search query"')
  out.info('  --json     JSON output')
  out.info('  --limit N  Max results (default: 10)')
  out.info('  --source   Backend: auto, skills-sh, meilisearch, catalog')
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Render a list of search results as a formatted table.
 *
 * Truncates descriptions to 60 characters to keep the table readable
 * in standard terminal widths.
 */
function formatResultsTable(out: OutputFormatter, results: SkillSearchResult[]): void {
  out.table(
    results.map((r) => ({
      name: r.name,
      source: r.source,
      description: (r.description ?? '').slice(0, 60),
      installs: r.installs ?? '-',
    })),
    ['name', 'source', 'description', 'installs']
  )
}
