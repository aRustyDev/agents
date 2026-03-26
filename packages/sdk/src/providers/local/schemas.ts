/**
 * Lockfile and external sources schemas for local providers.
 *
 * Copied from @agents/core/schemas -- only the lockfile-related schemas
 * needed by the SDK providers surface.
 */

import * as v from 'valibot'

// ---------------------------------------------------------------------------
// Lockfile schemas
// ---------------------------------------------------------------------------

/**
 * A single entry in the skills lockfile.
 *
 * Example:
 * ```json
 * {
 *   "source": "steveyegge/beads",
 *   "sourceType": "github",
 *   "computedHash": "16b0efc72b43177e1ad05e3f2e04132d266033e220834fd692369c65a15f8f39"
 * }
 * ```
 */
export const SkillLockEntry = v.object({
  source: v.string(),
  sourceType: v.string(),
  computedHash: v.pipe(
    v.string(),
    v.regex(/^[a-f0-9]{64}$/, 'Must be a 64-character lowercase hex SHA256 digest')
  ),
})
export type SkillLockEntry = v.InferOutput<typeof SkillLockEntry>

/**
 * Lockfile v1 -- the top-level structure of `skills-lock.json`.
 *
 * Example:
 * ```json
 * {
 *   "version": 1,
 *   "skills": {
 *     "beads": { "source": "...", "sourceType": "...", "computedHash": "..." }
 *   }
 * }
 * ```
 */
export const LockfileV1 = v.object({
  version: v.literal(1),
  skills: v.record(v.string(), SkillLockEntry),
})
export type LockfileV1 = v.InferOutput<typeof LockfileV1>

// ---------------------------------------------------------------------------
// External sources manifest
// ---------------------------------------------------------------------------

/** A single external skill entry in `sources.yaml`. */
export const ExternalSkillEntry = v.object({
  repo: v.string(),
  path: v.optional(v.string()),
  ref: v.optional(v.string()),
})
export type ExternalSkillEntry = v.InferOutput<typeof ExternalSkillEntry>

/**
 * External sources manifest (`sources.yaml`).
 *
 * Maps skill names to their remote source definitions.
 */
export const ExternalSourcesManifest = v.object({
  skills: v.record(v.string(), ExternalSkillEntry),
})
export type ExternalSourcesManifest = v.InferOutput<typeof ExternalSourcesManifest>
