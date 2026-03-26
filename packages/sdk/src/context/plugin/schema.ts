import * as v from 'valibot'
import { createSchemaValidator } from '../validator'

// ---------------------------------------------------------------------------
// Plugin author
// ---------------------------------------------------------------------------

export const PluginAuthorSchema = v.object({
  name: v.string(),
  email: v.optional(v.string()),
  url: v.optional(v.string()),
})

/** Alias for backward compat with consumers using the un-suffixed name. */
export const PluginAuthor = PluginAuthorSchema
export type PluginAuthor = v.InferOutput<typeof PluginAuthorSchema>

// ---------------------------------------------------------------------------
// Plugin manifest
// ---------------------------------------------------------------------------

export const PluginManifestSchema = v.object({
  name: v.string(),
  version: v.pipe(
    v.string(),
    v.regex(
      /^\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?$/,
      'Must be a valid semver version (e.g. 1.0.0, 0.1.0-beta.1)'
    )
  ),
  description: v.string(),
  author: v.optional(PluginAuthorSchema),
  homepage: v.optional(v.string()),
  repository: v.optional(v.string()),
  license: v.optional(v.string()),
  keywords: v.optional(v.array(v.string())),
  commands: v.optional(v.array(v.string())),
  agents: v.optional(v.array(v.string())),
  skills: v.optional(v.array(v.string())),
  outputStyles: v.optional(v.array(v.string())),
})

/** Alias for backward compat with consumers using the un-suffixed name. */
export const PluginManifest = PluginManifestSchema
export type PluginManifest = v.InferOutput<typeof PluginManifestSchema>

// ---------------------------------------------------------------------------
// Plugin source formats (3 formats)
// ---------------------------------------------------------------------------

/**
 * Legacy source format -- a bare string path.
 *
 * Example: `"content/commands/foo.md"`
 */
export const PluginSourceLegacy = v.string()
export type PluginSourceLegacy = v.InferOutput<typeof PluginSourceLegacy>

/**
 * Extended source format -- object with source path, hash, and optional fork info.
 */
export const PluginSourceDefSchema = v.object({
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

/** Alias for backward compat with consumers using the un-suffixed name. */
export const PluginSourceExtended = PluginSourceDefSchema
export type PluginSourceExtended = v.InferOutput<typeof PluginSourceDefSchema>

/**
 * Planning source format -- describes intent to extend/create from an external base.
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
  PluginSourceDefSchema,
  PluginSourcePlanning,
])
export type PluginSource = v.InferOutput<typeof PluginSource>

// ---------------------------------------------------------------------------
// Plugin sources manifest (plugin.sources.json)
// ---------------------------------------------------------------------------

export const PluginSourcesManifestSchema = v.object({
  $schema: v.optional(v.string()),
  sources: v.record(v.string(), PluginSource),
})

/** Alias for backward compat with consumers using the un-suffixed name. */
export const PluginSourcesManifest = PluginSourcesManifestSchema
export type PluginSourcesManifest = v.InferOutput<typeof PluginSourcesManifestSchema>

// ---------------------------------------------------------------------------
// Marketplace schema (marketplace.json)
// ---------------------------------------------------------------------------

export const MarketplaceEntrySchema = v.object({
  name: v.string(),
  source: v.string(),
  description: v.string(),
  version: v.pipe(
    v.string(),
    v.regex(/^\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?$/, 'Must be valid semver')
  ),
  author: PluginAuthorSchema,
  keywords: v.array(v.string()),
  license: v.string(),
  homepage: v.string(),
  repository: v.string(),
})

/** Alias for backward compat with consumers using the un-suffixed name. */
export const MarketplaceEntry = MarketplaceEntrySchema
export type MarketplaceEntry = v.InferOutput<typeof MarketplaceEntrySchema>

export const MarketplaceManifestSchema = v.object({
  name: v.string(),
  owner: v.object({ name: v.string(), email: v.optional(v.string()) }),
  plugins: v.array(MarketplaceEntrySchema),
})

/** Alias for backward compat with consumers using the un-suffixed name. */
export const MarketplaceManifest = MarketplaceManifestSchema
export type MarketplaceManifest = v.InferOutput<typeof MarketplaceManifestSchema>

// ---------------------------------------------------------------------------
// Unknown field detection
// ---------------------------------------------------------------------------

/**
 * Known valid fields in plugin.json.
 *
 * Used for unknown-field detection -- any key not in this set is flagged
 * as a warning during validation.
 */
export const KNOWN_PLUGIN_FIELDS = new Set([
  'name',
  'version',
  'description',
  'author',
  'homepage',
  'repository',
  'license',
  'keywords',
  'commands',
  'agents',
  'skills',
  'outputStyles',
])

/**
 * Detect unknown fields in a parsed plugin manifest.
 *
 * @returns Array of field names not in KNOWN_PLUGIN_FIELDS
 */
export function detectUnknownPluginFields(data: Record<string, unknown>): string[] {
  return Object.keys(data).filter((k) => !KNOWN_PLUGIN_FIELDS.has(k))
}

// ---------------------------------------------------------------------------
// LSP server config schema (.lsp.json)
// ---------------------------------------------------------------------------

/**
 * A single LSP server entry in .lsp.json.
 * Claude Code requires command + extensionToLanguage.
 */
export const LspServerEntry = v.object({
  command: v.string(),
  args: v.optional(v.array(v.string())),
  extensionToLanguage: v.record(v.string(), v.string()),
})
export type LspServerEntry = v.InferOutput<typeof LspServerEntry>

/**
 * The .lsp.json file format.
 */
export const LspConfig = v.object({
  lspServers: v.record(v.string(), LspServerEntry),
})
export type LspConfig = v.InferOutput<typeof LspConfig>

// ---------------------------------------------------------------------------
// MCP server config schema (.mcp.json)
// ---------------------------------------------------------------------------

/**
 * A single MCP server entry.
 */
export const McpServerEntry = v.object({
  command: v.string(),
  args: v.optional(v.array(v.string())),
  env: v.optional(v.record(v.string(), v.string())),
})
export type McpServerEntry = v.InferOutput<typeof McpServerEntry>

/**
 * The .mcp.json file format.
 * Supports both `mcpServers` (flat) and `mcp.servers` (nested) formats.
 */
export const McpConfig = v.union([
  v.object({ mcpServers: v.record(v.string(), McpServerEntry) }),
  v.object({ mcp: v.object({ servers: v.record(v.string(), McpServerEntry) }) }),
])
export type McpConfig = v.InferOutput<typeof McpConfig>

// ---------------------------------------------------------------------------
// Validator
// ---------------------------------------------------------------------------

export const pluginSchemaValidator = createSchemaValidator(PluginManifestSchema)
