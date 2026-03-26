import * as v from 'valibot'
import { createSchemaValidator } from '../validator'

export const PluginAuthorSchema = v.object({
  name: v.string(),
  email: v.optional(v.string()),
  url: v.optional(v.string()),
})

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

export const PluginSourcesManifestSchema = v.object({
  $schema: v.optional(v.string()),
  sources: v.record(
    v.string(),
    v.union([
      v.string(),
      PluginSourceDefSchema,
      v.object({
        type: v.string(),
        base: v.optional(v.string()),
        notes: v.optional(v.string()),
      }),
    ])
  ),
})

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

export const MarketplaceManifestSchema = v.object({
  name: v.string(),
  owner: v.object({ name: v.string(), email: v.optional(v.string()) }),
  plugins: v.array(MarketplaceEntrySchema),
})

export const pluginSchemaValidator = createSchemaValidator(PluginManifestSchema)
