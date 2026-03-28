import type { ParsedComponent, ValidationResult } from '../component'
import type { ComponentTypeModule } from '../registry'
import { parsePlugin } from './parser'
import { pluginSchemaValidator } from './schema'
import type { PluginManifest } from './types'

export const pluginModule: ComponentTypeModule<PluginManifest> = {
  type: 'plugin',
  schema: pluginSchemaValidator,
  parse: parsePlugin,
  validate(component: ParsedComponent<PluginManifest>): ValidationResult {
    const errors = []
    const warnings = []
    if (!component.frontmatter.name) {
      errors.push({
        path: 'frontmatter.name',
        message: 'name is required',
        severity: 'error' as const,
      })
    }
    if (!component.frontmatter.description) {
      errors.push({
        path: 'frontmatter.description',
        message: 'description is required',
        severity: 'error' as const,
      })
    }
    if (!component.frontmatter.version) {
      errors.push({
        path: 'frontmatter.version',
        message: 'version is required',
        severity: 'error' as const,
      })
    }
    if (!component.frontmatter.keywords || component.frontmatter.keywords.length === 0) {
      warnings.push({
        path: 'frontmatter.keywords',
        message: 'keywords are recommended',
        severity: 'warning' as const,
      })
    }
    return { valid: errors.length === 0, errors, warnings }
  },
}

export { parsePlugin } from './parser'
export {
  detectUnknownPluginFields,
  KNOWN_PLUGIN_FIELDS,
  LspConfig,
  LspServerEntry,
  MarketplaceEntry,
  MarketplaceEntrySchema,
  MarketplaceManifest,
  MarketplaceManifestSchema,
  McpConfig,
  McpServerEntry,
  PluginAuthor,
  PluginAuthorSchema,
  PluginManifest,
  PluginManifestSchema,
  PluginSource,
  PluginSourceDefSchema,
  PluginSourceExtended,
  PluginSourceLegacy,
  PluginSourcePlanning,
  PluginSourcesManifest,
  PluginSourcesManifestSchema,
  pluginSchemaValidator,
} from './schema'
export type {
  BuildResult,
  PluginAuthor as PluginAuthorType,
  PluginManifest as PluginManifestType,
  PluginSourceDef,
} from './types'
