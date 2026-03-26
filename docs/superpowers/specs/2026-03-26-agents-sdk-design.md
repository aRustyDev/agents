# @agents/sdk Design Specification

> **Date:** 2026-03-26
> **Epic:** ai-gtc
> **Status:** Draft

## Overview

Extract a domain SDK (`@agents/sdk`) from the CLI codebase to enable multiple consumer tools (CLI, TUI, App, API, WebUI, search-matrix-viewer, linters, feedback tools, publishing tools) to share the component model, registry adapters, catalog storage, and UI rendering without coupling to the CLI.

## Package Architecture

```
@agents/core          Pure utilities — no domain knowledge
@agents/sdk           Domain framework — component model + workflows
@agents/cli           Thin CLI commands (consumer)
@agents/*-viewer      Other consumers
```

### Dependency Flow

```
core ← sdk/util ← sdk/context ← sdk/providers ← sdk/catalog
core ← sdk/ui ← sdk/context
core ← sdk ← cli
```

**Key rule:** `core` has zero knowledge of components, skills, or catalogs. `sdk` owns all domain concepts. Core never imports from SDK. SDK never imports from consumers.

### Import Pattern

Single package, deep imports per surface:

```typescript
import { parseComponent } from '@agents/sdk/context'
import { createProviderManager } from '@agents/sdk/providers'
import { createCatalog } from '@agents/sdk/catalog'
import { createRenderer } from '@agents/sdk/ui'
import { createLogger } from '@agents/sdk/util'
```

Each surface is independently importable. A read-only viewer need not import catalog or providers.

---

## Surface 1: `util/` — Cross-cutting Concerns

```
@agents/sdk/util
├── logger.ts        # Logger interface + default implementation
├── tracer.ts        # Tracer interface + noop default
├── metrics.ts       # Metrics interface + noop default
├── errors.ts        # SDK error codes + structured error types
└── index.ts
```

### Logger

```typescript
type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal'

interface LogEntry {
  level: LogLevel
  message: string
  context?: Record<string, unknown>
  timestamp?: string  // ISO, auto-filled if omitted
}

interface LogSink {
  write(entry: LogEntry): void
}

interface Logger {
  debug(message: string, context?: Record<string, unknown>): void
  info(message: string, context?: Record<string, unknown>): void
  warn(message: string, context?: Record<string, unknown>): void
  error(message: string, context?: Record<string, unknown>): void
  fatal(message: string, context?: Record<string, unknown>): void
}

function createLogger(opts?: { level?: LogLevel; sink?: LogSink }): Logger
```

Default sink: JSON to stderr. Pluggable for OTel, file, or silent sinks (future).

### Tracer & Metrics

Interface-only with noop defaults. Pluggable sinks for future OTel integration.

```typescript
interface Tracer {
  startSpan(name: string, attrs?: Record<string, unknown>): Span
}

interface Span {
  setAttribute(key: string, value: unknown): void
  end(): void
}

interface Metrics {
  counter(name: string, tags?: Record<string, string>): Counter
  histogram(name: string, tags?: Record<string, string>): Histogram
}

interface Counter { inc(value?: number): void }
interface Histogram { observe(value: number): void }
```

### Errors

```typescript
type SdkErrorCode =
  | 'E_PROVIDER_UNAVAILABLE'
  | 'E_COMPONENT_NOT_FOUND'
  | 'E_PARSE_FRONTMATTER'
  | 'E_CATALOG_SYNC_FAILED'
  | 'E_VALIDATION_FAILED'
  | 'E_STORAGE_BACKEND'
  | 'E_SCHEMA_INVALID'
  | 'E_PROVIDER_TIMEOUT'

class SdkError extends CliError {
  readonly code: SdkErrorCode
}
```

---

## Surface 2: `context/` — Component Domain Model

```
@agents/sdk/context
├── component.ts       # Abstract Component interface + base utilities
├── registry.ts        # Type registry (maps type string → module)
├── parser.ts          # Generic parse(type, path) dispatcher
├── validator.ts       # Generic validate(component) dispatcher
├── skill/
│   ├── types.ts       # SkillFrontmatter, SkillComponent
│   ├── schema.ts      # Valibot schema for skill frontmatter
│   └── parser.ts      # SKILL.md → ParsedSkill
├── plugin/
│   ├── types.ts       # PluginManifest, SourceDef, BuildResult
│   ├── schema.ts      # plugin.json + plugin.sources.json + marketplace.json schemas
│   └── parser.ts      # Plugin parsing (composes skill, rule, mcp, output-style, command)
├── mcp/
│   ├── types.ts       # McpServerConfig, McpClientConfig, McpToolConfig
│   ├── schema.ts      # MCP JSON schemas
│   └── parser.ts
├── rule/
│   ├── types.ts
│   ├── schema.ts
│   └── parser.ts
├── agent/
│   ├── types.ts
│   ├── schema.ts
│   └── parser.ts
├── hook/
│   ├── types.ts
│   ├── schema.ts
│   └── parser.ts
├── output-style/
│   ├── types.ts
│   ├── schema.ts
│   └── parser.ts
├── command/
│   ├── types.ts
│   ├── schema.ts
│   └── parser.ts
├── persona/           # placeholder
│   └── types.ts
├── lsp/               # placeholder
│   └── types.ts
└── index.ts
```

### Abstract Component Interface

```typescript
interface Component<T extends Record<string, unknown> = Record<string, unknown>> {
  readonly type: ComponentType
  readonly name: string
  readonly content: string
  readonly frontmatter: T
  readonly metadata: ComponentMetadata
}

interface ComponentMetadata {
  discoveredPath?: string
  lastSeenAt?: string
  lastSeenHeadSha?: string
  wordCount?: number
  sectionCount?: number
  headingTree?: Array<{ depth: number; title: string }>
  fileTree?: string[]
  fileCount?: number
  contentHash?: string
  skillSizeBytes?: number
  lineCount?: number
  isSimple?: boolean
}
```

### Component Type Module Pattern

Each type directory exports a module implementing:

```typescript
interface ComponentTypeModule<T extends Record<string, unknown>> {
  readonly type: ComponentType
  readonly schema: BaseSchema
  parse(path: string): Promise<Result<Component<T>>>
  validate(component: Component<T>): ValidationResult
}
```

### Type Registry

```typescript
// Moved from core — ComponentType, COMPONENT_TYPES, etc.
type ComponentType = 'skill' | 'agent' | 'persona' | 'lsp' | 'mcp-server' |
  'mcp-client' | 'mcp-tool' | 'rule' | 'hook' | 'plugin' | 'output-style' | 'command'

const CONTEXT_MODULES = new Map<ComponentType, ComponentTypeModule<any>>()

function registerComponentType<T>(module: ComponentTypeModule<T>): void
function getComponentModule(type: ComponentType): ComponentTypeModule<unknown> | undefined
function parseComponentType(input: string): ComponentType | undefined
function getActiveTypes(): ComponentType[]
```

### Composite Types

```
context/rule/         ← leaf
context/hook/         ← leaf
context/output-style/ ← leaf
context/command/      ← leaf
context/mcp/          ← leaf
context/agent/        ← leaf
context/skill/        ← composite (imports rule, hook, mcp)
context/plugin/       ← composite (imports skill, rule, mcp, output-style, command)
```

Composites import leaves. Never the reverse.

### Schema Distribution

| Schema | Location | Reason |
|--------|----------|--------|
| SkillFrontmatter | `context/skill/schema.ts` | Component definition |
| PluginManifest | `context/plugin/schema.ts` | Component definition |
| PluginSourcesManifest | `context/plugin/schema.ts` | Plugin structure |
| MarketplaceManifest | `context/plugin/schema.ts` | Plugin marketplace |
| LspConfig, McpConfig | `context/mcp/schema.ts` | Component definition |
| LockfileV1 | `providers/local/schemas.ts` | Installation state |
| ExternalSourcesManifest | `providers/local/schemas.ts` | External skill tracking |

No central `schemas.ts`. Each schema lives next to the code that uses it.

---

## Surface 3: `providers/` — Registry Adapters

```
@agents/sdk/providers
├── interface.ts       # ComponentProvider interface
├── manager.ts         # ProviderManager (fan-out, dedup, pagination)
├── pagination.ts      # clampLimit, clampPage, paginateArray
├── clients/
│   ├── registry.ts    # AI client registry (19 clients)
│   └── config.ts      # Client config I/O (JSON/JSONC/YAML per client)
├── local/
│   ├── index.ts       # LocalProvider
│   ├── skill.ts       # Skill-specific local ops
│   ├── plugin.ts      # Plugin-specific local ops
│   ├── agent.ts       # Agent discovery
│   ├── rule.ts        # Rule discovery
│   ├── command.ts     # Command discovery
│   ├── output-style.ts
│   ├── hook.ts
│   └── schemas.ts     # LockfileV1, ExternalSourcesManifest
├── smithery/
│   ├── index.ts       # SmitheryProvider
│   ├── auth.ts        # OAuth device flow + keyring
│   └── publish.ts     # Publish workflow
├── github/
│   ├── index.ts       # GitHubProvider
│   └── search.ts      # GitHub search queries
└── index.ts
```

### Provider Interface

```typescript
interface ComponentProvider {
  readonly id: string
  readonly displayName: string
  readonly capabilities: ProviderCapabilities
  search(params: SearchParams): Promise<Result<PaginatedResult<Component>>>
  add(source: string, opts: ComponentAddOptions): Promise<Result<ComponentAddResult>>
  list(type: ComponentType, opts?): Promise<Result<Component[]>>
  remove(name: string, type: ComponentType, opts?): Promise<Result<RemoveResult>>
  info(name: string, type: ComponentType, opts?): Promise<Result<Component>>
  publish(type: ComponentType, opts: PublishOptions): Promise<Result<PublishResult>>
}

interface ProviderCapabilities {
  readonly search: readonly ComponentType[]
  readonly add: readonly ComponentType[]
  readonly list: readonly ComponentType[]
  readonly remove: readonly ComponentType[]
  readonly publish: readonly ComponentType[]
  readonly info: readonly ComponentType[]
  readonly outdated: readonly ComponentType[]
  readonly update: readonly ComponentType[]
}
```

### ProviderManager

```typescript
function createProviderManager(opts: {
  providers: ComponentProvider[]
  logger?: Logger
}): ProviderManager

interface ProviderManager {
  register(provider: ComponentProvider): void
  search(params: SearchParams): Promise<Result<PaginatedResult<Component>>>
  add(source: string, type: ComponentType, opts: ComponentAddOptions): Promise<Result<ComponentAddResult>>
  list(type: ComponentType, opts?): Promise<Result<Component[]>>
  remove(name: string, type: ComponentType, opts?): Promise<Result<RemoveResult>>
  info(name: string, type: ComponentType, opts?): Promise<Result<Component>>
  publish(type: ComponentType, opts: PublishOptions): Promise<Result<PublishResult>>
  findProviders(operation: string, type: ComponentType): ComponentProvider[]
}
```

---

## Surface 4: `catalog/` — Storage & Indexing

```
@agents/sdk/catalog
├── interface.ts       # CatalogReader, CatalogWriter, CatalogStore
├── types.ts           # CatalogEntry, CatalogQuery, SyncResult
├── manager.ts         # CatalogManager (orchestrates sync, query, staleness)
├── schemas.ts         # MarketplaceManifest (moved from context note: actually in plugin)
├── ndjson/
│   ├── index.ts       # NdjsonStore implements CatalogStore
│   └── io.ts          # Atomic read/write/append
├── sqlite/
│   ├── index.ts       # SqliteStore implements CatalogStore
│   ├── schema.sql
│   └── migrations.ts
└── index.ts
```

### Split Interfaces

```typescript
interface CatalogReader {
  query(params: CatalogQuery): Promise<Result<CatalogEntry[]>>
  get(source: string, name: string): Promise<Result<CatalogEntry | undefined>>
  count(filter?: CatalogFilter): Promise<Result<number>>
  findStale(upstream: Map<string, string>): Promise<Result<StaleResult[]>>
}

interface CatalogWriter {
  upsert(entries: CatalogEntry[]): Promise<Result<number>>
  remove(source: string, name: string): Promise<Result<boolean>>
  merge(results: DiscoveryResult[]): Promise<Result<SyncResult>>
  appendErrors(errors: ErrorRecord[]): Promise<Result<void>>
}

interface CatalogStore extends CatalogReader, CatalogWriter {
  readonly backend: string
  close(): Promise<void>
}
```

### CatalogManager

```typescript
function createCatalog(opts: {
  store: CatalogStore
  providers?: ComponentProvider[]
  logger?: Logger
}): CatalogManager

interface CatalogManager {
  query(params: CatalogQuery): Promise<Result<CatalogEntry[]>>
  get(source: string, name: string): Promise<Result<CatalogEntry | undefined>>
  stats(): Promise<Result<CatalogStats>>
  sync(opts?: SyncOptions): Promise<Result<SyncResult>>
  findStale(opts?: StaleOptions): Promise<Result<StaleResult[]>>
  readonly store: CatalogStore
}
```

### CatalogEntry

```typescript
interface CatalogEntry {
  source: string
  name: string
  type: ComponentType
  availability: AvailabilityStatus
  mechanical?: MechanicalFields
  analysis?: AnalysisFields
  discoveredAt?: string
  analyzedAt?: string
  contentHash?: string
  errorCount?: number
}

type AvailabilityStatus = 'available' | 'archived' | 'not_found' | 'private' | 'error' | 'removed_from_repo'
```

### Backend Priority

1. NDJSON (port current implementation)
2. SQLite (next)
3. DuckDB → Meilisearch + Qdrant → Cloudflare (future, interface only)

---

## Surface 5: `ui/` — Renderer Interface & Adapters

```
@agents/sdk/ui
├── interface.ts       # Renderer, ProgressHandle, TreeNode
├── cli.ts             # CliRenderer (colored terminal — from core/output.ts)
├── json.ts            # JsonRenderer (structured JSON stdout)
├── silent.ts          # SilentRenderer (noop for tests/headless)
└── index.ts
```

### Renderer Interface

```typescript
interface Renderer {
  table(data: Record<string, unknown>[], columns?: string[]): void
  tree(label: string, children: TreeNode[]): void
  success(message: string, data?: unknown): void
  error(message: string, data?: unknown): void
  warn(message: string, data?: unknown): void
  info(message: string, data?: unknown): void
  progress(message: string): ProgressHandle
  raw(data: unknown): void
}

interface ProgressHandle {
  update(opts: { text: string }): void
  success(opts?: { text?: string }): void
  error(opts?: { text?: string }): void
}

interface TreeNode {
  label: string
  children?: TreeNode[]
}

function createRenderer(opts?: {
  mode?: 'cli' | 'json' | 'silent'
  quiet?: boolean
}): Renderer
```

Future extensions: WebRenderer (emits events), TuiRenderer, interactive headless components.

---

## What Moves Where

### From `@agents/core` → `@agents/sdk`

| Source | Destination |
|--------|-------------|
| `core/component/types.ts` | `sdk/context/component.ts` + `sdk/context/registry.ts` |
| `core/component/manager.ts` | `sdk/providers/manager.ts` |
| `core/component/pagination.ts` | `sdk/providers/pagination.ts` |
| `core/component/clients.ts` | `sdk/providers/clients/registry.ts` |
| `core/component/client-config.ts` | `sdk/providers/clients/config.ts` |
| `core/component/index.ts` | `sdk/context/index.ts` + `sdk/providers/index.ts` |
| `core/output.ts` | `sdk/ui/cli.ts` |
| `core/schemas.ts` | Dissolved into per-type schemas |

### From `@agents/cli` → `@agents/sdk`

| Source | Destination |
|--------|-------------|
| `cli/lib/component/provider-local.ts` | `sdk/providers/local/index.ts` |
| `cli/lib/component/provider-agent.ts` | `sdk/providers/local/agent.ts` |
| `cli/lib/component/provider-command.ts` | `sdk/providers/local/command.ts` |
| `cli/lib/component/provider-plugin.ts` | `sdk/providers/local/plugin.ts` |
| `cli/lib/component/provider-rule.ts` | `sdk/providers/local/rule.ts` |
| `cli/lib/component/provider-output-style.ts` | `sdk/providers/local/output-style.ts` |
| `cli/lib/component/provider-smithery.ts` | `sdk/providers/smithery/index.ts` |
| `cli/lib/component/smithery-auth.ts` | `sdk/providers/smithery/auth.ts` |
| `cli/lib/component/smithery-publish.ts` | `sdk/providers/smithery/publish.ts` |
| `cli/lib/component/factory.ts` | `sdk/providers/factory.ts` |
| `cli/lib/chunker.ts` | `sdk/context/parser.ts` (frontmatter parsing) |
| `cli/lib/manifest.ts` | `sdk/context/skill/parser.ts` + `sdk/context/plugin/parser.ts` |
| `cli/lib/lockfile.ts` | `sdk/providers/local/schemas.ts` (lockfile schemas) |
| `cli/lib/catalog.ts` | Split: mechanical fns → `sdk/context/`, I/O → `sdk/catalog/ndjson/`, filters → `sdk/catalog/manager.ts` |
| `cli/lib/catalog-reconcile.ts` | `sdk/catalog/manager.ts` |
| `cli/lib/catalog-stale.ts` | `sdk/catalog/manager.ts` |

### Stays in `@agents/cli`

| File | Reason |
|------|--------|
| `skill-add.ts` through `skill-update.ts` | CLI install/update workflows |
| `catalog-discover.ts` | Pipeline orchestration (calls SDK primitives) |
| `catalog-download.ts` | Pipeline orchestration |
| `catalog-manifest.ts` | LLM agent prompt building |
| `external-skills.ts` | External skill drift detection |
| `registry.ts` | Catalog crawling (awesome-lists) |
| `taxonomy.ts` | Skill category classification |
| `search.ts`, `meilisearch.ts` | Multi-backend search orchestration |
| `embedder.ts`, `graph*.ts` | Knowledge graph (separate concern) |
| `agents.ts` | Agent directory management |
| `prompts/*` | Interactive CLI prompts |

### `@agents/core` After Extraction

```
core/
├── types.ts         # Result, CliError, EntityType, EXIT
├── file-io.ts       # Result-wrapped file I/O
├── symlink.ts       # Symlink operations
├── config.ts        # TOML config + validation
├── hash.ts          # SHA-256 hashing
├── uuid.ts          # UUID7 generation
├── runtime.ts       # currentDir, async helpers
├── git.ts           # Git operations
├── github.ts        # GitHub API client
├── source-parser.ts # URL/source parsing
└── index.ts         # barrel
```

Removed from core: `output.ts`, `schemas.ts`, `component/*`

---

## Migration Order

1. **util/** — interfaces + default implementations (no moves, all new code)
2. **context/** — move component types from core, chunker/manifest from CLI, build per-type modules
3. **providers/** — move providers from CLI, manager from core, build factory
4. **catalog/** — split catalog.ts, build NDJSON store, build manager
5. **ui/** — move output.ts from core, build interface + adapters
6. **CLI migration** — update CLI imports to use SDK, remove moved code

Each surface is independently deployable. CLI migration happens incrementally as each surface stabilizes.

---

## Anti-Patterns

- **Core importing from SDK** — core is primitives only, never domain-aware
- **Circular deps within context/** — composites (plugin, skill) import leaves, never reverse
- **Central schema files** — each schema lives next to its consumer
- **SDK importing from CLI** — dependency flows one direction: core ← sdk ← consumers
- **Concrete types in interfaces** — `CatalogStore`, `ComponentProvider`, `Renderer` are abstract; implementations are in subdirectories
- **Moving CLI workflows to SDK** — install/update/discover pipelines stay in CLI; SDK provides the building blocks they compose
