/**
 * Batch update orchestrator for outdated skills.
 *
 * Combines `checkOutdated()` and `addSkill()` into a single workflow:
 *
 * 1. Run checkOutdated() to discover which locked skills have changed upstream.
 * 2. Optionally filter to a user-supplied subset of skill names.
 * 3. Re-install each outdated skill via addSkill(source, { yes: true }).
 * 4. Collect and return structured per-skill results.
 *
 * Partial failures are tolerated -- if one skill fails, the remaining skills
 * are still processed.  The function never throws.
 */

import { CliError } from '@agents/core/types'
import { addSkill } from './skill-add'
import { checkOutdated, type OutdatedOptions, type OutdatedResult } from './skill-outdated'

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

export class UpdateError extends CliError {
  constructor(
    readonly skill: string,
    message: string,
    code: string,
    hint?: string,
    cause?: unknown
  ) {
    super(message, code, hint, cause)
  }
}

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export type UpdateStatus = 'updated' | 'current' | 'failed' | 'skipped'

export interface UpdateResult {
  skill: string
  source: string
  status: UpdateStatus
  error?: string
}

export interface UpdateOptions {
  /** Specific skills to update (empty = all outdated). */
  skills?: string[]
  /** Pass through to checkOutdated. */
  stdin?: boolean
  fromFile?: string
  fromUrl?: string
  /** Pass through to addSkill. */
  copy?: boolean
  yes?: boolean
  json?: boolean
  quiet?: boolean
  cwd?: string
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Map an OutdatedResult that will NOT be updated into an UpdateResult.
 * - `current` stays `current`
 * - everything else (`unavailable`, `unknown`) becomes `skipped`
 */
function toPassthrough(r: OutdatedResult): UpdateResult {
  return {
    skill: r.skill,
    source: r.source,
    status: r.status === 'current' ? 'current' : 'skipped',
  }
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

/**
 * Update outdated skills by re-installing from their upstream source.
 *
 * Never throws -- all errors are captured per-skill in the returned array.
 */
export async function updateSkills(opts: UpdateOptions = {}): Promise<UpdateResult[]> {
  const outdatedOpts: OutdatedOptions = {
    stdin: opts.stdin,
    fromFile: opts.fromFile,
    fromUrl: opts.fromUrl,
    cwd: opts.cwd,
  }

  // Step 1: Discover what is outdated
  const outdatedResults = await checkOutdated(outdatedOpts)

  // Step 2: Filter to outdated entries only
  let toUpdate = outdatedResults.filter((r) => r.status === 'outdated')

  // Step 3: Narrow to requested skill names (if supplied)
  if (opts.skills?.length) {
    const requested = new Set(opts.skills.map((s) => s.toLowerCase()))
    toUpdate = toUpdate.filter((r) => requested.has(r.skill.toLowerCase()))
  }

  // Nothing to update -- return passthrough results for every entry
  if (toUpdate.length === 0) {
    return outdatedResults.map(toPassthrough)
  }

  // Build a set for O(1) membership checks
  const updateSet = new Set(toUpdate.map((r) => r.skill))

  // Step 4: Re-install each outdated skill sequentially
  const results: UpdateResult[] = []

  for (const entry of toUpdate) {
    try {
      const addResult = await addSkill(entry.source, {
        cwd: opts.cwd,
        copy: opts.copy,
        yes: true, // Always non-interactive during batch update
        json: opts.json,
        quiet: true, // Suppress per-skill output during batch
      })

      if (addResult.ok) {
        results.push({
          skill: entry.skill,
          source: entry.source,
          status: 'updated',
        })
      } else {
        results.push({
          skill: entry.skill,
          source: entry.source,
          status: 'failed',
          error: addResult.error?.message ?? 'Unknown error',
        })
      }
    } catch (e) {
      results.push({
        skill: entry.skill,
        source: entry.source,
        status: 'failed',
        error: e instanceof Error ? e.message : String(e),
      })
    }
  }

  // Append passthrough entries for skills that were not targeted for update
  for (const entry of outdatedResults) {
    if (!updateSet.has(entry.skill)) {
      results.push(toPassthrough(entry))
    }
  }

  return results
}
