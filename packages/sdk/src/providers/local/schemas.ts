/**
 * Lockfile and external sources schemas for local providers.
 *
 * Canonical location for lockfile, external skill, and search-related
 * schemas used across the CLI and SDK.
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

/**
 * A single entry in the external skills manifest (`sources.yaml`).
 *
 * Declares how an external skill is used: either as a passthrough symlink
 * or as the basis for one or more derived local skills.
 *
 * Cross-field constraint: `passthrough` and `derived_by` are mutually
 * exclusive -- a skill cannot be both a live symlink and a drift-tracked
 * derivation source.
 *
 * Example:
 * ```yaml
 * beads:
 *   source: steveyegge/beads
 *   skill: beads
 *   passthrough: true
 * ```
 */
export const ExternalSkillEntry = v.pipe(
  v.object({
    source: v.string(),
    skill: v.string(),
    passthrough: v.boolean(),
    ref: v.optional(v.string()),
    derived_by: v.optional(v.array(v.string())),
  }),
  v.check(
    (entry) => !(entry.passthrough && entry.derived_by?.length),
    'passthrough and derived_by are mutually exclusive'
  )
)
export type ExternalSkillEntry = v.InferOutput<typeof ExternalSkillEntry>

/**
 * The full `sources.yaml` manifest for external skills.
 *
 * Example:
 * ```yaml
 * skills:
 *   beads:
 *     source: steveyegge/beads
 *     skill: beads
 *     passthrough: true
 * ```
 */
export const ExternalSourcesManifest = v.object({
  skills: v.record(v.string(), ExternalSkillEntry),
})
export type ExternalSourcesManifest = v.InferOutput<typeof ExternalSourcesManifest>

/**
 * A single entry in the external skills lock file (`sources.lock.json`).
 *
 * Keyed by a content-hash of `source/skill` so that manifest renames
 * do not lose tracking history.
 *
 * Example:
 * ```json
 * {
 *   "upstream_commit": "5045496bbe4b42d1...",
 *   "snapshot_hash": "sha256:16b0efc72b43...",
 *   "last_synced": "2026-03-18T12:00:00Z"
 * }
 * ```
 */
export const ExternalLockEntry = v.object({
  upstream_commit: v.string(),
  snapshot_hash: v.string(),
  last_synced: v.string(),
  last_reviewed_commit: v.optional(v.string()),
  drift_issue: v.optional(v.number()),
})
export type ExternalLockEntry = v.InferOutput<typeof ExternalLockEntry>

/**
 * The full external skills lock file (`sources.lock.json`).
 *
 * A flat record keyed by the first 12 hex chars of
 * `sha256(source + "/" + skill)`.
 */
export const ExternalLockfile = v.record(v.string(), ExternalLockEntry)
export type ExternalLockfile = v.InferOutput<typeof ExternalLockfile>

// ---------------------------------------------------------------------------
// Component registry schema
// ---------------------------------------------------------------------------

/**
 * A record in the component registry (knowledge graph / search index).
 */
export const ComponentRecord = v.object({
  id: v.string(),
  name: v.string(),
  type: v.string(),
  description: v.string(),
  author: v.optional(v.string()),
  canonical_url: v.optional(v.string()),
  github_url: v.optional(v.string()),
  star_count: v.optional(v.number()),
  source_type: v.string(),
  source_name: v.string(),
  tags: v.optional(v.array(v.string())),
  discovered_at: v.optional(v.string()),
})
export type ComponentRecord = v.InferOutput<typeof ComponentRecord>

// ---------------------------------------------------------------------------
// Output / status message schema
// ---------------------------------------------------------------------------

/**
 * Structured status message emitted by CLI commands in JSON mode.
 */
export const StatusMessage = v.object({
  status: v.picklist(['success', 'error', 'warning', 'info']),
  message: v.string(),
  data: v.optional(v.unknown()),
})
export type StatusMessage = v.InferOutput<typeof StatusMessage>

// ---------------------------------------------------------------------------
// Search result schema
// ---------------------------------------------------------------------------

/**
 * A single result from the unified skill search API.
 *
 * Backends normalize their responses into this shape so that callers get a
 * consistent interface regardless of the underlying search engine.
 */
export const SkillSearchResult = v.object({
  name: v.string(),
  source: v.pipe(v.string(), v.nonEmpty()),
  description: v.optional(v.string(), ''),
  installs: v.optional(v.number()),
  url: v.optional(v.string()),
})
export type SkillSearchResult = v.InferOutput<typeof SkillSearchResult>

/**
 * Supported search backends.
 *
 * - `skills-sh`   -- skills.sh public API
 * - `meilisearch`  -- local Meilisearch instance
 * - `catalog`      -- offline .catalog.ndjson file
 * - `auto`         -- try meilisearch -> skills-sh -> catalog
 */
export const SearchBackendType = v.picklist(['skills-sh', 'meilisearch', 'catalog', 'auto'])
export type SearchBackendType = v.InferOutput<typeof SearchBackendType>
