/**
 * Universal Component type system.
 *
 * Source-agnostic abstractions for discovering, installing, and managing
 * Claude Code components (skills, MCP servers, agents, plugins, etc.)
 * across local, registry, and marketplace providers.
 */

import type { Result } from '../types'

// ---------------------------------------------------------------------------
// Component taxonomy
// ---------------------------------------------------------------------------

export const COMPONENT_TYPES = [
  'skill',
  'mcp_server',
  'agent',
  'plugin',
  'rule',
  'command',
  'hook',
  'output_style',
  'claude_md',
] as const

export type ComponentType = (typeof COMPONENT_TYPES)[number]

/** Type guard: returns true when `value` is a valid ComponentType string. */
export function isComponentType(value: string): value is ComponentType {
  return (COMPONENT_TYPES as readonly string[]).includes(value)
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
