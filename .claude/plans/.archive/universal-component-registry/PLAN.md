---
id: a7c2e4f1-8b3d-4e9a-b5c0-6d8f1a2e3c4b
project:
  id: 00000000-0000-0000-0000-000000000000
title: Universal Component Registry
status: active
tags: [component-model, registry, mcp, skills, architecture]
related:
  depends-on: [3f7a1c8e-9d4b-4e2f-a6c0-5b8d3e1f7a2c]
---

# Universal Component Registry — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a source-agnostic component management system where MCP servers, skills, agents, plugins, rules, commands, and hooks all flow through a unified search/add/list/remove/publish pipeline — with pluggable backends (Smithery, skills.sh, GitHub, local, self-hosted registry).

**Architecture:** A `ComponentProvider` interface abstracts over all entity types and backends. Each entity type (skill, mcp_server, agent, etc.) has a canonical internal representation (`Component`). Backends (Smithery API, skills.sh, local filesystem, self-hosted registry) implement the provider interface. CLI commands delegate to a `ComponentManager` that routes through providers by entity type and source.

**Tech Stack:** Bun, TypeScript, Citty (CLI), Valibot (schemas), existing `lib/types.ts` Result monad

---

## Objectives

| # | Objective | Measurable | Done When |
|---|-----------|------------|-----------|
| 1 | Unified `Component` type for all entity types | Yes | All 9 entity types representable as `Component` with passing schema validation |
| 2 | `ComponentProvider` interface with pluggable backends | Yes | Local + Smithery providers pass all interface tests |
| 3 | `ComponentManager` aggregates search across providers | Yes | Multi-provider search returns deduplicated, paginated results |
| 4 | Smithery MCP server search integrated | Yes | `agents mcp search "postgres"` returns results from Smithery API |
| 5 | AI client config I/O for 19+ clients | Yes | Can read/write MCP server entries in Claude Desktop, Cursor, VS Code config files |
| 6 | Page-based pagination on all search backends | Yes | `--page 2 --limit 20` works on skill and MCP search |

## Current State (post Phase 5)

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Entity types with unified interface | 7 (skill, mcp_server, agent, plugin, rule, command, output_style) | 9 | 2 deferred: hook (AD-2), claude_md |
| Search backends | 4 (skills.sh, meilisearch, catalog, Smithery) | 4+ | Done |
| AI client config support | 19 (file-based + command-based) | 19 | Done |
| Pagination support | Page-based on all backends | Page-based | Done |
| Source types | 6 (github, gitlab, git, local, well-known, smithery) | 6+ | Done |
| CLI commands for MCP | 6 (search/add/list/remove/info/publish) | 6 | Done |
| CLI commands for component | 2 (search/list cross-type) | 2 | Done |
| Publish capability | Smithery mcp_server publish | Smithery + self-hosted | Phase 4b deferred (AD-3) |

## Phases

| ID | Name | Status | Dependencies | Deliverables |
|----|------|--------|--------------|-------------|
| phase-1 | Universal interfaces + local provider | **complete** | None | `Component` type, `ComponentProvider`, `ComponentManager`, pagination, local FS provider |
| phase-2 | Smithery provider + client config I/O | **complete** | phase-1 | Smithery search, 19-client config writing, source parser extension |
| phase-3a | Agent provider | **complete** | phase-1 | Agent discovery, frontmatter parsing, nested dir support. 18 tests. |
| phase-3b | Plugin provider | **complete** | phase-1 | Plugin discovery via existing `readPluginManifest`, nested dirs. 18 tests. |
| phase-3c | Rule + command providers | **complete** | phase-1 | Path-derived names, optional frontmatter. 24 tests. |
| phase-3d | Output style provider | **complete** | phase-1 | Trivial discovery, description from content. 13 tests. |
| phase-4a | Publish to Smithery | **complete** | phase-2, phase-3a | publish() interface, smithery-auth, smithery-publish, SmitheryProvider publish. 58 tests. |
| phase-4b | Self-hosted registry | **deferred** | phase-4a | Separate plan per AD-3. Requires infrastructure decisions. |
| phase-5 | Migration + CLI wiring | **complete** | phase-3a-d, phase-4a | Manager factory, MCP commands, component commands, CLI wiring. 35 tests. |

## GAP Review Notes

Reviewed 2026-03-20 by code-reviewer subagent. Key findings addressed:
- `ComponentType` aligned to existing `EntityType` (uses `mcp_server` not `mcp`)
- Smithery has no skills API — provider is MCP-search only
- Types namespaced (`ComponentAddResult`/`ComponentAddOptions`) to avoid collision with existing `skill-add.ts`
- Cross-provider pagination fixed (fan-out page 1, aggregate in-memory)
- `outdated`/`update` added to `ProviderCapabilities`
- `Operation` type includes all 8 operations
- `comment-json` deferred — use strip-and-parse fallback for JSONC

## Status

All phases complete and merged to main (2026-03-20). Pushed to origin/main.

| Milestone | Commit | Tests |
|-----------|--------|-------|
| Phase 1-2 (foundation + Smithery) | ce5f601 | 281 |
| Phase 3 (entity providers) | 85372dd | +73 = 354 |
| Phase 4a (publish interface + auth) | d85697a | +58 = 316* |
| Phase 4a.4 + 5.1 (SmitheryProvider publish + factory) | ee1349c | +45 = 338* |
| Phase 5 (CLI wiring) | 3e3bd6f | +13 = 357 |

*Test counts reflect incremental additions per commit. Final total: **357 component tests, 0 failures.**

Deferred to future plans:
- **Phase 4b** (self-hosted registry) — per AD-3, requires separate infrastructure plan
- **hook** entity type — per AD-2, deferred until standalone hook pattern emerges
- **claude_md** entity type — no provider built yet

---

## File Structure

### New files (Phase 1: Foundation)

| File | Responsibility |
|------|---------------|
| `.scripts/lib/component/types.ts` | Universal `Component` type, `ComponentType` enum, `ComponentProvider` interface, `ProviderCapabilities`. Uses `mcp_server` (not `mcp`) to align with existing `EntityType` in `lib/types.ts`. |
| `.scripts/lib/component/schemas.ts` | Valibot schemas for `Component`, `ComponentType`, `PaginatedResult`, `SearchParams` — runtime validators matching the TS interfaces |
| `.scripts/lib/component/manager.ts` | `ComponentManager` — provider registry, routing, multi-provider search aggregation |
| `.scripts/lib/component/provider-local.ts` | Local filesystem provider (reads `context/` dirs) |
| `.scripts/lib/component/provider-smithery.ts` | Smithery API provider (search skills + MCP servers) |
| `.scripts/lib/component/provider-github.ts` | GitHub-based provider (owner/repo resolution, skills.sh passthrough) |
| `.scripts/lib/component/provider-registry.ts` | Self-hosted registry provider (configurable base URL, future) |
| `.scripts/lib/component/pagination.ts` | Shared pagination types and helpers |
| `.scripts/lib/component/client-config.ts` | AI client config file I/O (19 clients from Smithery's pattern) |
| `.scripts/lib/component/clients.ts` | Static registry of AI client definitions (paths per OS, format, transport) |
| `.scripts/test/component/types.test.ts` | Tests for type guards and schema validation |
| `.scripts/test/component/manager.test.ts` | Tests for provider routing and aggregation |
| `.scripts/test/component/provider-local.test.ts` | Tests for local filesystem provider |
| `.scripts/test/component/provider-smithery.test.ts` | Tests for Smithery API provider |
| `.scripts/test/component/client-config.test.ts` | Tests for client config I/O |
| `.scripts/test/component/pagination.test.ts` | Tests for pagination helpers |

### Modified files

| File | Change |
|------|--------|
| `.scripts/lib/schemas.ts` | Add `Component`, `ComponentType`, `PaginatedResult` schemas |
| `.scripts/lib/types.ts` | Extend `EntityType` with `'hook'` if missing |
| `.scripts/commands/skill.ts` | Refactor search/add to route through `ComponentManager` |
| `.scripts/lib/skill-search-api.ts` | Add `page` param to `SearchOptions`; import `clampLimit` from `component/pagination` |
| `.scripts/lib/source-parser.ts` | Add `smithery` source type for `smithery://namespace/slug` URIs |

---

## Phase Overview

| Phase | Name | Deps | Deliverables |
|-------|------|------|-------------|
| **1** | Universal interfaces + local provider | None | `Component` type, `ComponentProvider`, `ComponentManager`, local FS provider |
| **2** | Smithery provider + client config I/O | Phase 1 | Smithery search/resolve, 19-client config writing, `mcp` CLI commands |
| **3** | GitHub provider + remaining entity types | Phase 1 | GitHub source resolution, agent/plugin/rule/command/hook providers |
| **4** | Publish pipeline + self-hosted registry | Phase 2-3 | Build→package→upload pattern, configurable registry URL |
| **5** | Migration + integration | Phase 2-4 | Refactor existing `skill-*` modules to use `ComponentManager` |

---

## Phase 1: Universal Interfaces + Local Provider

### Task 1.1: Universal Component Type (`lib/component/types.ts`)

The core abstraction — every entity in the system is a `Component`.

**Files:**
- Create: `.scripts/lib/component/types.ts`
- Create: `.scripts/test/component/types.test.ts`

- [ ] **Step 1: Write failing tests for Component type guards**

```typescript
// .scripts/test/component/types.test.ts
import { describe, expect, test } from 'bun:test'
import {
  type Component,
  type ComponentType,
  COMPONENT_TYPES,
  isComponentType,
  type ComponentProvider,
  type ProviderCapabilities,
  type SearchParams,
  type PaginatedResult,
} from '../../lib/component/types'

describe('COMPONENT_TYPES', () => {
  test('contains all 9 entity types', () => {
    expect(COMPONENT_TYPES).toContain('skill')
    expect(COMPONENT_TYPES).toContain('mcp_server')
    expect(COMPONENT_TYPES).toContain('claude_md')
    expect(COMPONENT_TYPES).toContain('agent')
    expect(COMPONENT_TYPES).toContain('plugin')
    expect(COMPONENT_TYPES).toContain('rule')
    expect(COMPONENT_TYPES).toContain('command')
    expect(COMPONENT_TYPES).toContain('hook')
    expect(COMPONENT_TYPES).toContain('output_style')
    expect(COMPONENT_TYPES).toHaveLength(9)
  })
})

describe('isComponentType', () => {
  test('returns true for valid types', () => {
    expect(isComponentType('skill')).toBe(true)
    expect(isComponentType('mcp_server')).toBe(true)
  })

  test('returns false for invalid types', () => {
    expect(isComponentType('foo')).toBe(false)
    expect(isComponentType('')).toBe(false)
  })
})

describe('Component interface', () => {
  test('can construct a minimal component', () => {
    const c: Component = {
      type: 'skill',
      name: 'beads',
      source: 'steveyegge/beads',
      description: 'Issue tracker',
    }
    expect(c.type).toBe('skill')
    expect(c.name).toBe('beads')
  })

  test('can construct a component with all optional fields', () => {
    const c: Component = {
      type: 'mcp_server',
      name: 'postgres-mcp',
      source: 'smithery://myns/postgres-mcp',
      description: 'PostgreSQL MCP server',
      version: '1.2.0',
      author: 'author',
      url: 'https://smithery.ai/server/postgres-mcp',
      tags: ['database', 'postgres'],
      installs: 1500,
      stars: 200,
      verified: true,
      namespace: 'myns',
      transport: 'stdio',
      configSchema: { type: 'object' },
      installedAt: undefined,
      installedAgents: [],
      installMode: undefined,
      localPath: undefined,
    }
    expect(c.verified).toBe(true)
    expect(c.transport).toBe('stdio')
  })
})

describe('SearchParams', () => {
  test('has required and optional fields', () => {
    const params: SearchParams = {
      query: 'kubernetes',
      type: 'skill',
      limit: 20,
      page: 1,
    }
    expect(params.query).toBe('kubernetes')
  })

  test('allows omitting optional fields', () => {
    const params: SearchParams = { query: 'test' }
    expect(params.type).toBeUndefined()
  })
})

describe('PaginatedResult', () => {
  test('contains items and pagination metadata', () => {
    const result: PaginatedResult<Component> = {
      items: [],
      page: 1,
      pageSize: 10,
      hasMore: false,
      total: 0,
    }
    expect(result.items).toHaveLength(0)
    expect(result.hasMore).toBe(false)
  })
})

describe('ProviderCapabilities', () => {
  test('describes what a provider can do per entity type', () => {
    const caps: ProviderCapabilities = {
      search: ['skill', 'mcp_server'],
      add: ['skill'],
      list: ['skill', 'mcp_server'],
      remove: ['skill'],
      publish: [],
      info: ['skill'],
      outdated: ['skill'],
      update: ['skill'],
    }
    expect(caps.search).toContain('skill')
    expect(caps.publish).toHaveLength(0)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .scripts && bun test test/component/types.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Write the Component type system**

```typescript
// .scripts/lib/component/types.ts

/**
 * Universal component model for the AI Context Library.
 *
 * Every managed entity — skills, MCP servers, agents, plugins, rules,
 * commands, hooks, output styles — is represented as a Component.
 * Providers implement search/add/list/remove for their backend.
 */

import type { Result } from '../types'

// ---------------------------------------------------------------------------
// Component types
// ---------------------------------------------------------------------------

/**
 * All entity types managed by the component system.
 * Aligned with existing `EntityType` in `lib/types.ts` plus `hook`.
 */
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

export function isComponentType(value: string): value is ComponentType {
  return (COMPONENT_TYPES as readonly string[]).includes(value)
}

// ---------------------------------------------------------------------------
// Component — the universal entity
// ---------------------------------------------------------------------------

/**
 * A single component in the registry. This is the universal representation
 * that all backends normalize into.
 *
 * Required fields describe identity. Optional fields add metadata that
 * some backends provide and others don't.
 */
export interface Component {
  /** Entity type. */
  readonly type: ComponentType
  /** Machine-readable name (kebab-case). */
  readonly name: string
  /** Source identifier — format depends on backend (owner/repo, smithery://ns/slug, ./path). */
  readonly source: string
  /** Human-readable description. */
  readonly description: string

  // --- Optional metadata (not all backends provide these) ---

  /** Semver version string. */
  readonly version?: string
  /** Author name or handle. */
  readonly author?: string
  /** Canonical URL (registry page, GitHub repo, etc.). */
  readonly url?: string
  /** Categorization tags. */
  readonly tags?: string[]
  /** Install count (from registry). */
  readonly installs?: number
  /** GitHub stars or equivalent. */
  readonly stars?: number
  /** Whether the component is verified/official. */
  readonly verified?: boolean
  /** Namespace / organization scope. */
  readonly namespace?: string

  // --- MCP-specific fields ---

  /** MCP transport type: stdio, http, http-oauth, shttp. */
  readonly transport?: string
  /** JSON Schema for server configuration. */
  readonly configSchema?: Record<string, unknown>

  // --- Local installation state (populated by list/info, not search) ---

  /** When this component was installed locally. */
  readonly installedAt?: string
  /** Which agents have this component installed. */
  readonly installedAgents?: string[]
  /** How it was installed: copy or symlink. */
  readonly installMode?: 'copy' | 'symlink'
  /** Absolute path on disk (for installed components). */
  readonly localPath?: string
}

// ---------------------------------------------------------------------------
// Pagination
// ---------------------------------------------------------------------------

/** Standard pagination parameters for search operations. */
export interface SearchParams {
  /** Search query string. */
  readonly query: string
  /** Filter to a specific component type. */
  readonly type?: ComponentType
  /** Maximum results per page (default: 10, max: 100). */
  readonly limit?: number
  /** Page number (1-indexed, default: 1). */
  readonly page?: number
  /** Filter by agent compatibility. */
  readonly agent?: string
  /** Filter by component name. */
  readonly name?: string
  /** Filter by namespace. */
  readonly namespace?: string
  /** Filter by verified status. */
  readonly verified?: boolean
}

/** A page of results from a search or list operation. */
export interface PaginatedResult<T> {
  readonly items: T[]
  readonly page: number
  readonly pageSize: number
  readonly hasMore: boolean
  readonly total?: number
}

// ---------------------------------------------------------------------------
// Provider interface
// ---------------------------------------------------------------------------

/** Declares which operations a provider supports for which entity types. */
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

/**
 * Options for the add/install operation.
 * Named `ComponentAddOptions` to avoid collision with existing `AddOptions` in `skill-add.ts`.
 */
export interface ComponentAddOptions {
  /** Target agent(s) to install for. */
  readonly agents?: string[]
  /** Copy files instead of symlinking. */
  readonly copy?: boolean
  /** Skip interactive prompts. */
  readonly yes?: boolean
  /** Working directory override. */
  readonly cwd?: string
  /** Install globally (user-level) instead of project-local. */
  readonly global?: boolean
  /** MCP-specific: target client for config file writing. */
  readonly client?: string
  /** MCP-specific: server config values (JSON). */
  readonly config?: Record<string, unknown>
}

/**
 * Result of an add/install operation.
 * Named `ComponentAddResult` to avoid collision with existing `AddResult` in `skill-add.ts`.
 * Phase 5 migration will consolidate the two.
 */
export interface ComponentAddResult {
  readonly ok: boolean
  /** One add can install multiple components (e.g. a repo with multiple skills). */
  readonly components: Component[]
  readonly installedTo: string[]
  readonly warnings: string[]
  readonly error?: string
}

/** Result of a remove operation. */
export interface RemoveResult {
  readonly ok: boolean
  readonly component: string
  readonly removedFrom: string[]
  readonly error?: string
}

/**
 * A component provider — the core abstraction.
 *
 * Each backend (Smithery, GitHub, local filesystem, self-hosted registry)
 * implements this interface for the entity types it supports.
 *
 * Providers are registered with a ComponentManager, which routes
 * operations to the appropriate provider(s).
 */
export interface ComponentProvider {
  /** Unique identifier for this provider (e.g. 'smithery', 'local', 'github'). */
  readonly id: string

  /** Human-readable display name. */
  readonly displayName: string

  /** Which operations this provider supports for which types. */
  readonly capabilities: ProviderCapabilities

  /** Search for components across this provider's registry. */
  search(params: SearchParams): Promise<Result<PaginatedResult<Component>>>

  /** Install a component from this provider. */
  add(source: string, opts: ComponentAddOptions): Promise<Result<ComponentAddResult>>

  /** List installed components managed by this provider. */
  list(type: ComponentType, opts?: { cwd?: string; agent?: string }): Promise<Result<Component[]>>

  /** Remove an installed component. */
  remove(name: string, type: ComponentType, opts?: { cwd?: string; agent?: string }): Promise<Result<RemoveResult>>

  /** Get detailed info for a single component. */
  info(name: string, type: ComponentType, opts?: { cwd?: string }): Promise<Result<Component>>
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd .scripts && bun test test/component/types.test.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .scripts/lib/component/types.ts .scripts/test/component/types.test.ts
git commit -m "feat(component): add universal Component type and ComponentProvider interface"
```

---

### Task 1.2: Pagination Helpers (`lib/component/pagination.ts`)

Shared pagination logic used by all providers.

**Files:**
- Create: `.scripts/lib/component/pagination.ts`
- Create: `.scripts/test/component/pagination.test.ts`

- [ ] **Step 1: Write failing tests**

```typescript
// .scripts/test/component/pagination.test.ts
import { describe, expect, test } from 'bun:test'
import { clampPage, clampLimit, paginateArray, emptyPage } from '../../lib/component/pagination'

describe('clampLimit', () => {
  test('defaults to 10', () => expect(clampLimit(undefined)).toBe(10))
  test('clamps 0 to 1', () => expect(clampLimit(0)).toBe(1))
  test('clamps 500 to 100', () => expect(clampLimit(500)).toBe(100))
  test('passes through 25', () => expect(clampLimit(25)).toBe(25))
  test('handles NaN', () => expect(clampLimit(NaN)).toBe(10))
})

describe('clampPage', () => {
  test('defaults to 1', () => expect(clampPage(undefined)).toBe(1))
  test('clamps 0 to 1', () => expect(clampPage(0)).toBe(1))
  test('clamps -1 to 1', () => expect(clampPage(-1)).toBe(1))
  test('passes through 5', () => expect(clampPage(5)).toBe(5))
})

describe('paginateArray', () => {
  const items = ['a', 'b', 'c', 'd', 'e']

  test('returns first page', () => {
    const result = paginateArray(items, 1, 2)
    expect(result.items).toEqual(['a', 'b'])
    expect(result.page).toBe(1)
    expect(result.pageSize).toBe(2)
    expect(result.hasMore).toBe(true)
    expect(result.total).toBe(5)
  })

  test('returns last page', () => {
    const result = paginateArray(items, 3, 2)
    expect(result.items).toEqual(['e'])
    expect(result.hasMore).toBe(false)
  })

  test('returns empty for out-of-range page', () => {
    const result = paginateArray(items, 10, 2)
    expect(result.items).toEqual([])
    expect(result.hasMore).toBe(false)
  })
})

describe('emptyPage', () => {
  test('returns empty paginated result', () => {
    const result = emptyPage(3, 10)
    expect(result.items).toEqual([])
    expect(result.page).toBe(3)
    expect(result.hasMore).toBe(false)
    expect(result.total).toBe(0)
  })
})
```

- [ ] **Step 2: Run test, verify fails**
- [ ] **Step 3: Implement**

```typescript
// .scripts/lib/component/pagination.ts

import type { PaginatedResult } from './types'

/** Clamp limit to [1, 100], default 10. */
export function clampLimit(limit: number | undefined): number {
  const raw = limit ?? 10
  if (Number.isNaN(raw)) return 10
  return Math.max(1, Math.min(100, raw))
}

/** Clamp page to >= 1, default 1. Handles NaN. */
export function clampPage(page: number | undefined): number {
  const raw = page ?? 1
  if (Number.isNaN(raw)) return 1
  return Math.max(1, Math.floor(raw))
}

/** Paginate an in-memory array. */
export function paginateArray<T>(
  items: T[],
  page: number,
  pageSize: number,
): PaginatedResult<T> {
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const slice = items.slice(start, end)
  return {
    items: slice,
    page,
    pageSize,
    hasMore: end < items.length,
    total: items.length,
  }
}

/** Return an empty paginated result. */
export function emptyPage<T>(page: number, pageSize: number): PaginatedResult<T> {
  return { items: [], page, pageSize, hasMore: false, total: 0 }
}
```

- [ ] **Step 4: Run test, verify passes**
- [ ] **Step 5: Commit**

---

### Task 1.3: Component Manager (`lib/component/manager.ts`)

Routes operations to registered providers. Aggregates multi-provider search results.

**Files:**
- Create: `.scripts/lib/component/manager.ts`
- Create: `.scripts/test/component/manager.test.ts`

- [ ] **Step 1: Write failing tests**

```typescript
// .scripts/test/component/manager.test.ts
import { describe, expect, test } from 'bun:test'
import { ComponentManager } from '../../lib/component/manager'
import type { ComponentProvider, SearchParams, PaginatedResult, Component, ComponentAddOptions, ComponentAddResult, RemoveResult, ComponentType } from '../../lib/component/types'
import { ok, err, CliError } from '../../lib/types'

/** Minimal mock provider for testing. */
function mockProvider(id: string, searchResults: Component[] = []): ComponentProvider {
  return {
    id,
    displayName: `Mock ${id}`,
    capabilities: {
      search: ['skill', 'mcp_server'],
      add: ['skill'],
      list: ['skill'],
      remove: ['skill'],
      publish: [],
      info: ['skill'],
      outdated: ['skill'],
      update: ['skill'],
    },
    search: async (params) => ok({
      items: searchResults.filter(c =>
        !params.type || c.type === params.type
      ),
      page: params.page ?? 1,
      pageSize: params.limit ?? 10,
      hasMore: false,
      total: searchResults.length,
    }),
    add: async () => ok({ ok: true, components: searchResults.slice(0, 1), installedTo: [], warnings: [] }),
    list: async () => ok(searchResults),
    remove: async (name) => ok({ ok: true, component: name, removedFrom: [] }),
    info: async (name) => {
      const found = searchResults.find(c => c.name === name)
      return found ? ok(found) : err(new CliError('Not found', 'E_NOT_FOUND'))
    },
  }
}

const skillA: Component = { type: 'skill', name: 'beads', source: 'steveyegge/beads', description: 'Issue tracker' }
const skillB: Component = { type: 'skill', name: 'tdd', source: 'smithery://ns/tdd', description: 'TDD skill' }
const mcpA: Component = { type: 'mcp_server', name: 'postgres', source: 'smithery://ns/postgres', description: 'PG MCP' }

describe('ComponentManager', () => {
  test('registers and retrieves providers', () => {
    const mgr = new ComponentManager()
    const p = mockProvider('test')
    mgr.register(p)
    expect(mgr.getProvider('test')).toBe(p)
    expect(mgr.getProvider('nonexistent')).toBeUndefined()
  })

  test('lists registered providers', () => {
    const mgr = new ComponentManager()
    mgr.register(mockProvider('a'))
    mgr.register(mockProvider('b'))
    expect(mgr.providers()).toHaveLength(2)
  })

  test('search aggregates across providers', async () => {
    const mgr = new ComponentManager()
    mgr.register(mockProvider('local', [skillA]))
    mgr.register(mockProvider('smithery', [skillB, mcpA]))

    const result = await mgr.search({ query: 'test', type: 'skill' })
    expect(result.ok).toBe(true)
    if (result.ok) {
      // Should combine results from both providers
      expect(result.value.items.length).toBeGreaterThanOrEqual(2)
    }
  })

  test('search filters by type', async () => {
    const mgr = new ComponentManager()
    mgr.register(mockProvider('mixed', [skillA, mcpA]))

    const result = await mgr.search({ query: 'test', type: 'mcp_server' })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.items.every(c => c.type === 'mcp_server')).toBe(true)
    }
  })

  test('search skips providers that dont support the type', async () => {
    const mgr = new ComponentManager()
    const p = mockProvider('limited', [mcpA])
    // Override capabilities to only support mcp search
    ;(p as any).capabilities = { ...p.capabilities, search: ['mcp_server'] }
    mgr.register(p)

    const result = await mgr.search({ query: 'test', type: 'skill' })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.items).toHaveLength(0)
    }
  })

  test('search continues when one provider fails', async () => {
    const mgr = new ComponentManager()
    const failing: ComponentProvider = {
      ...mockProvider('failing'),
      search: async () => err(new CliError('Network error', 'E_NETWORK')),
    }
    mgr.register(failing)
    mgr.register(mockProvider('working', [skillA]))

    const result = await mgr.search({ query: 'test' })
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.items).toHaveLength(1)
    }
  })

  test('findProviders returns providers supporting a type+operation', () => {
    const mgr = new ComponentManager()
    mgr.register(mockProvider('a'))
    mgr.register(mockProvider('b'))
    const providers = mgr.findProviders('search', 'skill')
    expect(providers).toHaveLength(2)
  })
})
```

- [ ] **Step 2: Run test, verify fails**
- [ ] **Step 3: Implement**

```typescript
// .scripts/lib/component/manager.ts

import { ok, err, CliError, type Result } from '../types'
import type {
  Component,
  ComponentProvider,
  ComponentType,
  SearchParams,
  PaginatedResult,
  ComponentAddOptions,
  ComponentAddResult,
  RemoveResult,
} from './types'
import { clampLimit, clampPage, emptyPage, paginateArray } from './pagination'

type Operation = 'search' | 'add' | 'list' | 'remove' | 'publish' | 'info' | 'outdated' | 'update'

/**
 * Routes component operations to registered providers.
 *
 * For search: aggregates results from all providers that support the
 * requested entity type, deduplicating by name+source.
 *
 * For add/remove/info: uses the first provider whose id matches the
 * source prefix, or falls back to providers that support the type.
 */
export class ComponentManager {
  private readonly registry = new Map<string, ComponentProvider>()

  /** Register a provider. */
  register(provider: ComponentProvider): void {
    this.registry.set(provider.id, provider)
  }

  /** Get a provider by id. */
  getProvider(id: string): ComponentProvider | undefined {
    return this.registry.get(id)
  }

  /** List all registered providers. */
  providers(): ComponentProvider[] {
    return [...this.registry.values()]
  }

  /** Find providers that support a given operation + type. */
  findProviders(operation: Operation, type: ComponentType): ComponentProvider[] {
    return this.providers().filter((p) => {
      const supported = p.capabilities[operation]
      return (supported as readonly string[]).includes(type)
    })
  }

  /**
   * Search across all providers that support the requested type.
   * Results are aggregated and deduplicated by name+source.
   */
  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    const limit = clampLimit(params.limit)
    const page = clampPage(params.page)
    const type = params.type

    const providers = type
      ? this.findProviders('search', type)
      : this.providers().filter((p) => p.capabilities.search.length > 0)

    if (providers.length === 0) {
      return ok(emptyPage(page, limit))
    }

    // Fan out to all matching providers.
    // Request page 1 with a generous limit from each — we paginate the
    // aggregate result in-memory. This avoids the double-pagination bug
    // where per-provider page offsets produce incorrect combined results.
    const fanOutLimit = limit * providers.length * 2 // over-fetch to fill the page
    const settled = await Promise.allSettled(
      providers.map((p) => p.search({ ...params, limit: fanOutLimit, page: 1 })),
    )

    // Collect successful results
    const allItems: Component[] = []
    for (const result of settled) {
      if (result.status === 'fulfilled' && result.value.ok) {
        allItems.push(...result.value.value.items)
      }
    }

    // Deduplicate by name+source
    const seen = new Set<string>()
    const deduped: Component[] = []
    for (const item of allItems) {
      const key = `${item.type}:${item.name}:${item.source}`
      if (!seen.has(key)) {
        seen.add(key)
        deduped.push(item)
      }
    }

    // Apply type filter if searching across all types
    const filtered = type ? deduped.filter((c) => c.type === type) : deduped

    // Paginate the aggregate in-memory
    return ok(paginateArray(filtered, page, limit))
  }

  /**
   * Add/install a component. Routes to the first provider that
   * recognizes the source format.
   */
  async add(
    source: string,
    type: ComponentType,
    opts: ComponentAddOptions,
  ): Promise<Result<ComponentAddResult>> {
    const providers = this.findProviders('add', type)
    if (providers.length === 0) {
      return err(new CliError(
        `No provider supports adding ${type} components`,
        'E_NO_PROVIDER',
      ))
    }
    // Use the first capable provider (future: route by source prefix)
    return providers[0]!.add(source, opts)
  }

  /** List installed components of a given type. */
  async list(
    type: ComponentType,
    opts?: { cwd?: string; agent?: string },
  ): Promise<Result<Component[]>> {
    const providers = this.findProviders('list', type)
    const allItems: Component[] = []
    for (const p of providers) {
      const result = await p.list(type, opts)
      if (result.ok) allItems.push(...result.value)
    }
    return ok(allItems)
  }

  /** Get detailed info for a component. */
  async info(
    name: string,
    type: ComponentType,
    opts?: { cwd?: string },
  ): Promise<Result<Component>> {
    const providers = this.findProviders('info', type)
    for (const p of providers) {
      const result = await p.info(name, type, opts)
      if (result.ok) return result
    }
    return err(new CliError(
      `Component "${name}" (${type}) not found in any provider`,
      'E_NOT_FOUND',
    ))
  }

  /** Remove an installed component. */
  async remove(
    name: string,
    type: ComponentType,
    opts?: { cwd?: string; agent?: string },
  ): Promise<Result<RemoveResult>> {
    const providers = this.findProviders('remove', type)
    if (providers.length === 0) {
      return err(new CliError(
        `No provider supports removing ${type} components`,
        'E_NO_PROVIDER',
      ))
    }
    return providers[0]!.remove(name, type, opts)
  }
}
```

- [ ] **Step 4: Run test, verify passes**
- [ ] **Step 5: Commit**

---

### Task 1.4: Local Filesystem Provider (`lib/component/provider-local.ts`)

Reads installed components from `context/` directories.

**Files:**
- Create: `.scripts/lib/component/provider-local.ts`
- Create: `.scripts/test/component/provider-local.test.ts`

- [ ] **Step 1: Write failing tests**

Tests should create temp directories with SKILL.md fixtures and verify the local provider discovers them. Test cases:
- Discovers skills in `context/skills/`
- Returns empty for nonexistent directories
- Populates `localPath`, `installMode`, and `installedAgents`
- Search filters by query (substring match on name+description)
- Info returns full detail for a single component
- List supports `--agent` filter

- [ ] **Step 2: Run test, verify fails**
- [ ] **Step 3: Implement**

The local provider wraps existing `discoverSkills()`, `listSkills()`, `skillInfo()`, `removeSkills()`, and `addSkill()` from Phase 1's skill modules, converting their results into `Component` objects. For non-skill types, it scans the corresponding `context/` subdirectory (e.g., `context/rules/`, `context/commands/`).

- [ ] **Step 4: Run test, verify passes**
- [ ] **Step 5: Commit**

---

### Task 1.5: Barrel Export + Index (`lib/component/index.ts`)

**Files:**
- Create: `.scripts/lib/component/index.ts`

```typescript
// .scripts/lib/component/index.ts
export * from './types'
export * from './pagination'
export { ComponentManager } from './manager'
// Providers are imported directly, not re-exported — keeps the barrel lightweight
// import { LocalProvider } from './component/provider-local'
// import { SmitheryProvider } from './component/provider-smithery'
```

- [ ] **Step 1: Create barrel export**
- [ ] **Step 2: Commit**

---

## Phase 2: Smithery Provider + Client Config I/O

### Task 2.1: Smithery API Provider (`lib/component/provider-smithery.ts`)

Wraps the Smithery public API for searching skills and MCP servers.

**Files:**
- Create: `.scripts/lib/component/provider-smithery.ts`
- Create: `.scripts/test/component/provider-smithery.test.ts`

Key logic:
- `search(params)`: calls `GET https://registry.smithery.ai/api/v1/servers?q=...&pageSize=N&page=N` for MCP servers
- **Smithery does NOT have a skills API** — only MCP server search is supported. Skill search uses skills.sh / meilisearch / catalog (existing backends)
- Normalizes Smithery responses into `Component` objects with `type: 'mcp_server'`
- 3-second timeout per request, never throws
- Supports `--verified`, `--namespace` filters
- Capabilities: `search: ['mcp_server']`, everything else empty (remote search only)

Test with mocked `globalThis.fetch`.

- [ ] **Steps: test → fail → implement → pass → commit**

---

### Task 2.2: Add Smithery as Search Backend (`lib/skill-search-api.ts`)

Extend the existing search API to include Smithery as a 4th backend and add `page` parameter.

**Files:**
- Modify: `.scripts/lib/skill-search-api.ts`
- Modify: `.scripts/lib/schemas.ts` (add `'smithery'` to `SearchBackendType`)
- Modify: `.scripts/test/skill-find.test.ts`

Changes:
- Add `page` field to `SearchOptions` (page-based pagination for all backends)
- Pass `page` through to backends that support it (skills.sh, catalog)
- **Do NOT add Smithery as a skill search backend** — Smithery has no skills API. Smithery MCP search is handled by the `SmitheryProvider` in the component system, not the skill-specific search API.
- Keep `AUTO_CHAIN` as `['meilisearch', 'skills-sh', 'catalog']` (unchanged)

- [ ] **Steps: test → fail → implement → pass → commit**

---

### Task 2.3: AI Client Config Registry (`lib/component/clients.ts`)

Static registry of 19+ AI client definitions — their config file paths per OS, file format, transport capabilities, and field mappings.

**Files:**
- Create: `.scripts/lib/component/clients.ts`
- Create: `.scripts/test/component/clients.test.ts`

```typescript
// Key types
export type ClientTransport = 'stdio' | 'http' | 'http-oauth'
export type ClientFormat = 'json' | 'jsonc' | 'yaml'
export type InstallMethod = 'file' | 'command'

export interface ClientConfig {
  readonly id: string
  readonly displayName: string
  readonly installMethod: InstallMethod
  readonly format?: ClientFormat
  readonly configPaths: {
    readonly darwin?: string
    readonly win32?: string
    readonly linux?: string
  }
  readonly command?: string  // for command-based clients
  readonly supportedTransports: readonly ClientTransport[]
  readonly fieldOverrides?: Record<string, string>  // remap JSON keys
}

export const CLIENT_REGISTRY: ReadonlyMap<string, ClientConfig>
export const CLIENT_IDS: readonly string[]
export function getClientConfig(id: string): ClientConfig | undefined
export function getConfigPath(client: ClientConfig): string | undefined
```

Clients to include (from Smithery's `clients.ts`):
claude-desktop, claude-code, cursor, windsurf, vscode, vscode-insiders, cline, roo-code, continue, zed, goose, opencode, witsy, enconvo, coterm, librechat, mcp-cli, superinterface, amazon-bedrock

- [ ] **Steps: test → fail → implement → pass → commit**

---

### Task 2.4: Client Config I/O (`lib/component/client-config.ts`)

Read and write MCP server entries in client config files.

**Files:**
- Create: `.scripts/lib/component/client-config.ts`
- Create: `.scripts/test/component/client-config.test.ts`

```typescript
// Key exports
export function readClientConfig(clientId: string): Promise<Result<Record<string, unknown>>>
export function writeServerToClient(
  clientId: string,
  serverName: string,
  serverConfig: McpServerEntry,
): Promise<Result<void>>
export function removeServerFromClient(
  clientId: string,
  serverName: string,
): Promise<Result<void>>
export function listServersInClient(
  clientId: string,
): Promise<Result<McpServerEntry[]>>

export interface McpServerEntry {
  readonly name: string
  readonly transport: ClientTransport
  readonly url?: string        // for http/http-oauth
  readonly command?: string    // for stdio
  readonly args?: string[]     // for stdio
  readonly env?: Record<string, string>
}
```

Supports JSON (most clients), JSONC (opencode), YAML (goose, librechat). Uses `comment-json` for JSONC if needed, or falls back to strip-comments-then-parse.

Test with temp files for each format.

- [ ] **Steps: test → fail → implement → pass → commit**

---

### Task 2.5: Source Parser Extension (`lib/source-parser.ts`)

Add `smithery` source type for `smithery://namespace/slug` URIs.

**Files:**
- Modify: `.scripts/lib/source-parser.ts`
- Modify: `.scripts/test/source-parser.test.ts`

New test cases:
| Input | type | namespace | name |
|-------|------|-----------|------|
| `smithery://myns/postgres-mcp` | smithery | myns | postgres-mcp |
| `smithery://org/my-skill` | smithery | org | my-skill |

- [ ] **Steps: test → fail → implement → pass → commit**

---

## Phase 3: Remaining Entity Types (future plan)

Each entity type gets a provider implementation that maps its on-disk format to `Component`:

| Type | Discovery Pattern | Frontmatter/Config |
|------|-------------------|-------------------|
| `agent` | `context/agents/*/` with agent definition YAML | Agent frontmatter |
| `plugin` | `context/plugins/*/.claude-plugin/plugin.json` | Plugin manifest |
| `rule` | `context/rules/**/*.md` | Markdown with optional frontmatter |
| `command` | `context/commands/**/*.md` or plugin commands | Command frontmatter (YAML) |
| `hook` | `.claude/settings.json` hooks section | JSON config |
| `output_style` | `context/output-styles/**/*.md` | Markdown |

---

## Phase 4: Publish Pipeline (future plan)

Abstract pattern from Smithery's `mcp publish`:
1. **Package**: collect files → ZIP/tarball
2. **Validate**: schema check, manifest present, name valid
3. **Upload**: multipart POST to registry URL
4. **Poll**: GET status endpoint until terminal state
5. **Report**: print URL / error

The registry URL is configurable (`REGISTRY_URL` env var or settings file). The manifest format is our own (not Smithery's workerd-specific format).

---

## Phase 5: Migration (future plan)

Refactor existing `skill-*` modules to delegate through `ComponentManager`:
- `skill search` → `manager.search({ type: 'skill', query })`
- `skill add` → `manager.add(source, 'skill', opts)`
- `skill list` → `manager.list('skill', opts)`
- `skill remove` → `manager.remove(name, 'skill', opts)`

Add new top-level CLI commands:
- `agents mcp search/add/list/remove/info`
- `agents component search` (cross-type search)

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Smithery API changes without notice | Medium | Medium | Pin to known endpoints; abstract behind provider |
| Component type inflation (too many types) | Low | Medium | `COMPONENT_TYPES` is a closed set; new types require explicit addition |
| Provider interface too generic for MCP specifics | Medium | High | MCP-specific fields on `Component` (transport, configSchema); providers cast as needed |
| Client config file format changes | Medium | Medium | Each client's config is versioned; detect format on read |
| Self-hosted registry doesn't exist yet | Certain | Low | Provider-registry is a stub until the registry is built |

---

## Notes

- The `Component` interface is intentionally flat (no deep nesting) for JSON serialization
- MCP-specific fields (`transport`, `configSchema`) live on the base `Component` — this is a pragmatic choice over a discriminated union, since most consumers just want to display/filter
- The `ComponentManager.search()` aggregation is concurrent (`Promise.allSettled`) and fault-tolerant (one provider failing doesn't block others)
- Client config I/O from Smithery supports 19 clients; we start with the same set and can add more
- Pagination is page-based (not cursor-based) for simplicity; cursor support can be added to `PaginatedResult` later if needed
- The `smithery://` URI scheme is our convention, not Smithery's — their API uses `namespace/slug` paths
