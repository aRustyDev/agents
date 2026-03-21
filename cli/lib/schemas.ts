/**
 * Valibot schema definitions for all JSON structures in the project.
 *
 * Every schema is exported both as a runtime validator (PascalCase value) and
 * as an inferred TypeScript type (PascalCase type).  This ensures a single
 * source of truth -- the schema IS the type.
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
// Plugin source schemas (3 formats)
// ---------------------------------------------------------------------------

/**
 * Legacy source format -- a bare string path.
 *
 * Example: `"context/commands/foo.md"`
 */
export const PluginSourceLegacy = v.string()
export type PluginSourceLegacy = v.InferOutput<typeof PluginSourceLegacy>

/**
 * Extended source format -- object with source path, hash, and optional fork info.
 *
 * Example:
 * ```json
 * {
 *   "source": "context/skills/lang-swift-dev/SKILL.md",
 *   "hash": "sha256:964e09bc408c52c70ffbc99884131a0c6065a2455aefef0294a30b74bc104d1b",
 *   "forked": false
 * }
 * ```
 */
export const PluginSourceExtended = v.object({
  source: v.string(),
  hash: v.optional(
    v.pipe(
      v.string(),
      v.regex(/^sha256:[a-f0-9]{64}$/, 'Must be a sha256-prefixed 64-char hex digest')
    )
  ),
  forked: v.optional(v.boolean()),
  forked_at: v.optional(v.string()),
})
export type PluginSourceExtended = v.InferOutput<typeof PluginSourceExtended>

/**
 * Planning source format -- describes intent to extend/create from an external base.
 *
 * Example:
 * ```json
 * {
 *   "type": "extend",
 *   "base": "https://github.com/example/repo",
 *   "notes": "Adapt for specific use case"
 * }
 * ```
 */
export const PluginSourcePlanning = v.object({
  type: v.string(),
  base: v.optional(v.string()),
  notes: v.optional(v.string()),
})
export type PluginSourcePlanning = v.InferOutput<typeof PluginSourcePlanning>

/**
 * Union of all three plugin source formats.
 */
export const PluginSource = v.union([
  PluginSourceLegacy,
  PluginSourceExtended,
  PluginSourcePlanning,
])
export type PluginSource = v.InferOutput<typeof PluginSource>

// ---------------------------------------------------------------------------
// Plugin sources manifest (plugin.sources.json)
// ---------------------------------------------------------------------------

/**
 * The full `plugin.sources.json` file.
 *
 * Has an optional `$schema` field and a `sources` record mapping local paths
 * to source definitions.
 */
export const PluginSourcesManifest = v.object({
  $schema: v.optional(v.string()),
  sources: v.record(v.string(), PluginSource),
})
export type PluginSourcesManifest = v.InferOutput<typeof PluginSourcesManifest>

// ---------------------------------------------------------------------------
// Plugin manifest schemas (plugin.json)
// ---------------------------------------------------------------------------

/**
 * Plugin author information.
 */
export const PluginAuthor = v.object({
  name: v.string(),
  email: v.optional(v.string()),
  url: v.optional(v.string()),
})
export type PluginAuthor = v.InferOutput<typeof PluginAuthor>

/**
 * Platform skill detection entry within a plugin manifest.
 */
export const PlatformSkill = v.object({
  name: v.string(),
  path: v.string(),
  detection: v.optional(v.array(v.string())),
})
export type PlatformSkill = v.InferOutput<typeof PlatformSkill>

/**
 * The full `plugin.json` manifest.
 *
 * Semver regex allows typical semver versions like 0.1.0, 1.0.0-beta.1, etc.
 */
export const PluginManifest = v.object({
  name: v.string(),
  version: v.pipe(
    v.string(),
    v.regex(
      /^\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?$/,
      'Must be a valid semver version (e.g. 1.0.0, 0.1.0-beta.1)'
    )
  ),
  description: v.string(),
  author: PluginAuthor,
  homepage: v.optional(v.string()),
  repository: v.optional(v.string()),
  license: v.optional(v.string()),
  keywords: v.optional(v.array(v.string())),
  commands: v.optional(v.array(v.string())),
  agents: v.optional(v.array(v.string())),
  skills: v.optional(v.array(v.string())),
  platformSkills: v.optional(v.array(PlatformSkill)),
  mcpServers: v.optional(v.string()),
  outputStyles: v.optional(v.array(v.string())),
  lspServers: v.optional(v.string()),
})
export type PluginManifest = v.InferOutput<typeof PluginManifest>

// ---------------------------------------------------------------------------
// Skill frontmatter schema
// ---------------------------------------------------------------------------

/**
 * YAML frontmatter found at the top of SKILL.md files.
 *
 * The only strictly required fields are `name` and `description`.
 * Everything else is optional metadata.
 */
export const SkillFrontmatter = v.object({
  name: v.string(),
  description: v.string(),
  version: v.optional(v.string()),
  author: v.optional(v.string()),
  license: v.optional(v.string()),
  tags: v.optional(v.array(v.string())),
  source: v.optional(v.string()),
  created: v.optional(v.string()),
  updated: v.optional(v.string()),
  globs: v.optional(v.array(v.string())),
  'allowed-tools': v.optional(v.string()),
})
export type SkillFrontmatter = v.InferOutput<typeof SkillFrontmatter>

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
// External skill schemas
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
// Search result schema (Phase 3)
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
