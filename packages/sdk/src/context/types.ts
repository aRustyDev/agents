/**
 * Universal Component type system.
 *
 * Source-agnostic abstractions for discovering, installing, and managing
 * Claude Code components (skills, MCP servers, agents, plugins, etc.)
 * across local, registry, and marketplace providers.
 */

import type { EntityType, Result } from '@agents/core/types'

// ---------------------------------------------------------------------------
// Component taxonomy
// ---------------------------------------------------------------------------

export const COMPONENT_TYPES = [
  'skill',
  'agent',
  'persona',
  'lsp',
  'mcp-server',
  'mcp-client',
  'mcp-tool',
  'rule',
  'hook',
  'plugin',
  'output-style',
  'command',
] as const

export type ComponentType = (typeof COMPONENT_TYPES)[number]

/** Type guard: returns true when `value` is a valid ComponentType string. */
export function isComponentType(value: string): value is ComponentType {
  return (COMPONENT_TYPES as readonly string[]).includes(value)
}

// ---------------------------------------------------------------------------
// Component type metadata
// ---------------------------------------------------------------------------

export interface ComponentTypeMetadata {
  readonly name: ComponentType
  readonly pluralName: string
  readonly discoveryPattern: string // glob for finding installed components
  readonly templateDir?: string // for init scaffold
  readonly schemaPath?: string // for lint validation
  readonly providers: string[] // provider IDs that handle this type
  readonly placeholder: boolean // true if not yet fully implemented
}

export const COMPONENT_TYPE_META: Record<ComponentType, ComponentTypeMetadata> = {
  skill: {
    name: 'skill',
    pluralName: 'skills',
    discoveryPattern: '**/skills/**/*.md',
    providers: ['local', 'smithery'],
    placeholder: false,
  },
  agent: {
    name: 'agent',
    pluralName: 'agents',
    discoveryPattern: '**/agents/**/*.md',
    providers: ['local-agent'],
    placeholder: false,
  },
  persona: {
    name: 'persona',
    pluralName: 'personas',
    discoveryPattern: '**/personas/**/*.md',
    templateDir: 'content/personas/_template',
    providers: [],
    placeholder: true,
  },
  lsp: {
    name: 'lsp',
    pluralName: 'lsp-configs',
    discoveryPattern: '**/lsp/**/*.json',
    providers: [],
    placeholder: true,
  },
  'mcp-server': {
    name: 'mcp-server',
    pluralName: 'mcp-servers',
    discoveryPattern: '**/mcp/servers/**/*.json',
    providers: ['smithery'],
    placeholder: false,
  },
  'mcp-client': {
    name: 'mcp-client',
    pluralName: 'mcp-clients',
    discoveryPattern: '**/mcp/clients/**/*.json',
    providers: [],
    placeholder: true,
  },
  'mcp-tool': {
    name: 'mcp-tool',
    pluralName: 'mcp-tools',
    discoveryPattern: '**/mcp/tools/**/*.json',
    providers: [],
    placeholder: true,
  },
  rule: {
    name: 'rule',
    pluralName: 'rules',
    discoveryPattern: '**/rules/**/*.md',
    providers: ['local-rule'],
    placeholder: false,
  },
  hook: {
    name: 'hook',
    pluralName: 'hooks',
    discoveryPattern: '**/hooks/**/*.{ts,js,sh}',
    templateDir: 'content/hooks/_template',
    providers: [],
    placeholder: true,
  },
  plugin: {
    name: 'plugin',
    pluralName: 'plugins',
    discoveryPattern: '**/plugins/**/*.json',
    providers: ['local-plugin'],
    placeholder: false,
  },
  'output-style': {
    name: 'output-style',
    pluralName: 'output-styles',
    discoveryPattern: '**/output-styles/**/*.md',
    providers: ['local-output-style'],
    placeholder: false,
  },
  command: {
    name: 'command',
    pluralName: 'commands',
    discoveryPattern: '**/commands/**/*.md',
    providers: ['local-command'],
    placeholder: false,
  },
}

/** Look up metadata for a component type. */
export function getComponentMeta(type: ComponentType): ComponentTypeMetadata {
  return COMPONENT_TYPE_META[type]
}

/** Get all non-placeholder component types. */
export function getActiveTypes(): ComponentType[] {
  return COMPONENT_TYPES.filter((t) => !COMPONENT_TYPE_META[t].placeholder)
}

/** Parse a CLI input string to ComponentType (handles spaces and hyphens). */
export function parseComponentType(input: string): ComponentType | undefined {
  const normalized = input.toLowerCase().replace(/\s+/g, '-').replace(/_/g, '-')
  if (isComponentType(normalized)) return normalized
  return undefined
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/** Unified representation of any installable component. */
export interface Component {
  readonly type: ComponentType
  readonly name: string
  readonly source: string
  readonly description: string
  readonly version?: string
  readonly author?: string
  readonly url?: string
  readonly tags?: string[]
  readonly installs?: number
  readonly stars?: number
  readonly verified?: boolean
  readonly namespace?: string
  readonly transport?: string
  readonly configSchema?: Record<string, unknown>
  readonly installedAt?: string
  readonly installedAgents?: string[]
  readonly installMode?: 'copy' | 'symlink'
  readonly localPath?: string
}

// ---------------------------------------------------------------------------
// Component metadata (for parsed components)
// ---------------------------------------------------------------------------

export interface ComponentMetadata {
  readonly wordCount: number
  readonly sectionCount: number
  readonly headingTree: Array<{ depth: number; title: string }>
  readonly lineCount: number
}

// ---------------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------------

export interface SearchParams {
  readonly query: string
  readonly type?: ComponentType
  readonly limit?: number
  readonly page?: number
  readonly agent?: string
  readonly name?: string
  readonly namespace?: string
  readonly verified?: boolean
}

export interface PaginatedResult<T> {
  readonly items: T[]
  readonly page: number
  readonly pageSize: number
  readonly hasMore: boolean
  readonly total?: number
}

// ---------------------------------------------------------------------------
// Provider capabilities
// ---------------------------------------------------------------------------

export interface ProviderCapabilities {
  readonly search: readonly ComponentType[]
  readonly add: readonly ComponentType[]
  readonly list: readonly ComponentType[]
  readonly remove: readonly ComponentType[]
  readonly publish: readonly ComponentType[]
  readonly info: readonly ComponentType[]
  readonly outdated: readonly ComponentType[]
  readonly update: readonly ComponentType[]
}

// ---------------------------------------------------------------------------
// Add / Remove results
// ---------------------------------------------------------------------------

export interface ComponentAddOptions {
  readonly agents?: string[]
  readonly copy?: boolean
  readonly yes?: boolean
  readonly cwd?: string
  readonly global?: boolean
  readonly client?: string
  readonly config?: Record<string, unknown>
}

export interface ComponentAddResult {
  readonly ok: boolean
  readonly components: Component[]
  readonly installedTo: string[]
  readonly warnings: string[]
  readonly error?: string
}

export interface RemoveResult {
  readonly ok: boolean
  readonly component: string
  readonly removedFrom: string[]
  readonly error?: string
}

// ---------------------------------------------------------------------------
// Publish
// ---------------------------------------------------------------------------

/** Options for publishing a component to a registry. */
export interface PublishOptions {
  /** Qualified name (e.g. namespace/server for Smithery). */
  readonly name?: string
  /** Namespace to publish under. */
  readonly namespace?: string
  /** API key for authentication. */
  readonly apiKey?: string
  /** URL of an external MCP server (no build needed). */
  readonly externalUrl?: string
  /** JSON Schema for server configuration. */
  readonly configSchema?: Record<string, unknown>
  /** Pre-built bundle directory path. */
  readonly bundleDir?: string
  /** Dry run — validate without uploading. */
  readonly dryRun?: boolean
  /** Working directory. */
  readonly cwd?: string
}

/** Result of a publish operation. */
export interface PublishResult {
  readonly ok: boolean
  /** Registry URL where the component is now available. */
  readonly registryUrl?: string
  /** Deployment/release identifier. */
  readonly releaseId?: string
  /** Status: 'published', 'pending', 'failed'. */
  readonly status: 'published' | 'pending' | 'failed'
  readonly error?: string
  readonly warnings: string[]
}

// ---------------------------------------------------------------------------
// Provider interface
// ---------------------------------------------------------------------------

export interface ComponentProvider {
  readonly id: string
  readonly displayName: string
  readonly capabilities: ProviderCapabilities

  search(params: SearchParams): Promise<Result<PaginatedResult<Component>>>
  add(source: string, opts: ComponentAddOptions): Promise<Result<ComponentAddResult>>
  list(type: ComponentType, opts?: { cwd?: string; agent?: string }): Promise<Result<Component[]>>
  remove(
    name: string,
    type: ComponentType,
    opts?: { cwd?: string; agent?: string }
  ): Promise<Result<RemoveResult>>
  info(name: string, type: ComponentType, opts?: { cwd?: string }): Promise<Result<Component>>
  /** Publish a component to a registry. */
  publish(type: ComponentType, opts: PublishOptions): Promise<Result<PublishResult>>
}

// ---------------------------------------------------------------------------
// EntityType <-> ComponentType bridge
// ---------------------------------------------------------------------------

/** Map between ComponentType (CLI, kebab-case) and EntityType (KG, snake_case). */
const COMPONENT_TO_ENTITY: Partial<Record<ComponentType, EntityType>> = {
  skill: 'skill',
  agent: 'agent',
  plugin: 'plugin',
  rule: 'rule',
  command: 'command',
  'mcp-server': 'mcp_server',
  'output-style': 'output_style',
}

const ENTITY_TO_COMPONENT: Partial<Record<EntityType, ComponentType>> = {
  skill: 'skill',
  agent: 'agent',
  plugin: 'plugin',
  rule: 'rule',
  command: 'command',
  mcp_server: 'mcp-server',
  output_style: 'output-style',
  // claude_md has no ComponentType equivalent
}

/** Convert ComponentType to EntityType for KG queries. Returns undefined for types with no KG mapping. */
export function toEntityType(ct: ComponentType): EntityType | undefined {
  return COMPONENT_TO_ENTITY[ct]
}

/** Convert EntityType to ComponentType for CLI display. Returns undefined for KG-only types (e.g., claude_md). */
export function toComponentType(et: EntityType): ComponentType | undefined {
  return ENTITY_TO_COMPONENT[et]
}
