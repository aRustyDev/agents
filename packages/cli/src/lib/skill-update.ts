// Re-export shim — logic moved to @agents/sdk/providers/local/skill/update
// This shim preserves CLI test compatibility by importing checkOutdated and
// addSkill from the CLI-level shims (which tests can mock.module on).

import { CliError } from '@agents/core/types'
import { createCliAgentResolver } from './agents'

// Re-export types from SDK
export {
  UpdateError,
  type UpdateOptions,
  type UpdateResult,
  type UpdateStatus,
} from '@agents/sdk/providers/local/skill/update'

import type { UpdateOptions, UpdateResult } from '@agents/sdk/providers/local/skill/update'
import type { OutdatedOptions, OutdatedResult } from './skill-outdated'

/**
 * Map an OutdatedResult that will NOT be updated into an UpdateResult.
 */
function toPassthrough(r: OutdatedResult): UpdateResult {
  return {
    skill: r.skill,
    source: r.source,
    status: r.status === 'current' ? 'current' : 'skipped',
  }
}

/**
 * CLI-specific updateSkills that uses CLI-level shim imports.
 * This allows tests to mock ../skill-outdated and ../skill-add individually.
 */
export async function updateSkills(opts: UpdateOptions = {}): Promise<UpdateResult[]> {
  const { checkOutdated } = await import('./skill-outdated')
  const { addSkill } = await import('./skill-add')

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
        yes: true,
        json: opts.json,
        quiet: true,
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
