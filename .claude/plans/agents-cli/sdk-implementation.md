# @agents/sdk Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract `@agents/sdk` as the domain framework layer between `@agents/core` (primitives) and consumer tools (CLI, viewers, linters, etc.)

**Architecture:** 5 SDK surfaces (util, context, providers, catalog, ui) built in dependency order. Each surface is independently importable via deep imports (`@agents/sdk/context`, etc.). After all surfaces land, CLI imports are migrated from core/lib to SDK.

**Tech Stack:** Bun workspaces, TypeScript, Valibot, smol-toml, simple-git, js-yaml

**Spec:** `docs/superpowers/specs/2026-03-26-agents-sdk-design.md`

---

## Objectives

| # | Objective | Done When |
|---|-----------|-----------|
| 1 | SDK package scaffolded with all 5 surfaces | `bun test --cwd packages/sdk` passes |
| 2 | Component model in SDK with per-type modules | `parseComponent('skill', path)` returns typed result |
| 3 | Providers moved to SDK | `createProviderManager({ providers })` works |
| 4 | Catalog storage abstracted | `NdjsonStore` passes all existing catalog tests |
| 5 | UI renderer interface | `createRenderer({ mode: 'cli' })` replaces `createOutput()` |
| 6 | CLI migrated to SDK imports | All CLI tests pass with SDK imports |
| 7 | Core slimmed | `core/component/` and `core/output.ts` removed |

### Test Strategy

- Baseline: `packages/cli` — 1929 pass / 11 fail / 0 errors (as of test fix commit; may vary ±5 due to flaky Bun tests)
- Each phase must maintain zero regressions in CLI
- Each SDK surface gets its own tests in `packages/sdk/test/`
- Run both: `bun test --cwd packages/sdk && bun test --cwd packages/cli`

---

## Phase 1: Scaffold + util/

### Task 1.1: Create packages/sdk/ scaffold

**Files:**

- Create: `packages/sdk/package.json`
- Create: `packages/sdk/tsconfig.json`
- Create: `packages/sdk/src/index.ts`

- [ ] **Step 1:** Create `packages/sdk/package.json`:

```json
{
  "name": "@agents/sdk",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "exports": {
    ".": "./src/index.ts",
    "./*": "./src/*.ts",
    "./util": "./src/util/index.ts",
    "./util/*": "./src/util/*.ts",
    "./context": "./src/context/index.ts",
    "./context/*": "./src/context/*.ts",
    "./providers": "./src/providers/index.ts",
    "./providers/*": "./src/providers/*.ts",
    "./catalog": "./src/catalog/index.ts",
    "./catalog/*": "./src/catalog/*.ts",
    "./ui": "./src/ui/index.ts",
    "./ui/*": "./src/ui/*.ts"
  },
  "dependencies": {
    "@agents/core": "workspace:*"
  }
}
```

- [ ] **Step 2:** Create `packages/sdk/tsconfig.json` (match core/cli pattern):

```json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "esnext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "outDir": "./dist",
    "rootDir": ".",
    "types": ["bun-types"]
  },
  "include": ["src/**/*.ts", "test/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

- [ ] **Step 3:** Create empty `packages/sdk/src/index.ts`:

```typescript
/**
 * @agents/sdk — Domain framework for AI Context Library tools.
 *
 * Surfaces: util, context, providers, catalog, ui
 * Import via deep paths: @agents/sdk/context, @agents/sdk/providers, etc.
 */
```

- [ ] **Step 4:** Add `"@agents/sdk": "workspace:*"` to `packages/cli/package.json` dependencies.

- [ ] **Step 5:** Verify root `package.json` workspace glob (`"workspaces": ["packages/*"]`) already matches `packages/sdk/`. Run `bun install` from repo root. Verify `bun.lock` now includes `@agents/sdk` workspace entry. Test: `bun run -e "import('@agents/sdk')"` should not throw.

- [ ] **Step 6:** Commit: `feat(sdk): scaffold @agents/sdk package`

### Task 1.2: Build util/ surface

**Files:**

- Create: `packages/sdk/src/util/logger.ts`
- Create: `packages/sdk/src/util/tracer.ts`
- Create: `packages/sdk/src/util/metrics.ts`
- Create: `packages/sdk/src/util/errors.ts`
- Create: `packages/sdk/src/util/index.ts`
- Create: `packages/sdk/test/util/logger.test.ts`
- Create: `packages/sdk/test/util/errors.test.ts`

- [ ] **Step 1:** Write test for Logger:

```typescript
// packages/sdk/test/util/logger.test.ts
import { describe, expect, test } from 'bun:test'
import { createLogger, type LogEntry, type LogSink } from '../../src/util/logger'

describe('createLogger', () => {
  test('logs at info level by default', () => {
    const entries: LogEntry[] = []
    const sink: LogSink = { write: (e) => entries.push(e) }
    const log = createLogger({ sink })
    log.info('hello', { key: 'value' })
    expect(entries).toHaveLength(1)
    expect(entries[0]!.level).toBe('info')
    expect(entries[0]!.message).toBe('hello')
    expect(entries[0]!.context?.key).toBe('value')
  })

  test('respects log level filter', () => {
    const entries: LogEntry[] = []
    const sink: LogSink = { write: (e) => entries.push(e) }
    const log = createLogger({ level: 'warn', sink })
    log.debug('ignored')
    log.info('ignored')
    log.warn('kept')
    log.error('kept')
    log.fatal('kept')
    expect(entries).toHaveLength(3)
  })

  test('auto-fills timestamp', () => {
    const entries: LogEntry[] = []
    const sink: LogSink = { write: (e) => entries.push(e) }
    const log = createLogger({ sink })
    log.info('test')
    expect(entries[0]!.timestamp).toBeDefined()
  })
})
```

- [ ] **Step 2:** Run test, verify it fails: `bun test --cwd packages/sdk`

- [ ] **Step 3:** Implement `packages/sdk/src/util/logger.ts`:

```typescript
export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'fatal'

export interface LogEntry {
  level: LogLevel
  message: string
  context?: Record<string, unknown>
  timestamp?: string
}

export interface LogSink {
  write(entry: LogEntry): void
}

export interface Logger {
  debug(message: string, context?: Record<string, unknown>): void
  info(message: string, context?: Record<string, unknown>): void
  warn(message: string, context?: Record<string, unknown>): void
  error(message: string, context?: Record<string, unknown>): void
  fatal(message: string, context?: Record<string, unknown>): void
}

const LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 0, info: 1, warn: 2, error: 3, fatal: 4,
}

const defaultSink: LogSink = {
  write(entry) {
    console.error(JSON.stringify(entry))
  },
}

export function createLogger(opts?: { level?: LogLevel; sink?: LogSink }): Logger {
  const minLevel = LEVEL_ORDER[opts?.level ?? 'info']
  const sink = opts?.sink ?? defaultSink

  function log(level: LogLevel, message: string, context?: Record<string, unknown>) {
    if (LEVEL_ORDER[level] < minLevel) return
    sink.write({ level, message, context, timestamp: new Date().toISOString() })
  }

  return {
    debug: (m, c) => log('debug', m, c),
    info: (m, c) => log('info', m, c),
    warn: (m, c) => log('warn', m, c),
    error: (m, c) => log('error', m, c),
    fatal: (m, c) => log('fatal', m, c),
  }
}
```

- [ ] **Step 4:** Run test, verify it passes.

- [ ] **Step 5:** Implement `packages/sdk/src/util/tracer.ts` (noop defaults):

```typescript
export interface Span {
  setAttribute(key: string, value: unknown): void
  end(): void
}

export interface Tracer {
  startSpan(name: string, attrs?: Record<string, unknown>): Span
}

const noopSpan: Span = { setAttribute() {}, end() {} }

export function createNoopTracer(): Tracer {
  return { startSpan: () => noopSpan }
}
```

- [ ] **Step 6:** Implement `packages/sdk/src/util/metrics.ts` (noop defaults):

```typescript
export interface Counter { inc(value?: number): void }
export interface Histogram { observe(value: number): void }

export interface Metrics {
  counter(name: string, tags?: Record<string, string>): Counter
  histogram(name: string, tags?: Record<string, string>): Histogram
}

const noopCounter: Counter = { inc() {} }
const noopHistogram: Histogram = { observe() {} }

export function createNoopMetrics(): Metrics {
  return {
    counter: () => noopCounter,
    histogram: () => noopHistogram,
  }
}
```

- [ ] **Step 7:** Implement `packages/sdk/src/util/errors.ts`:

```typescript
export type SdkErrorCode =
  | 'E_PROVIDER_UNAVAILABLE'
  | 'E_COMPONENT_NOT_FOUND'
  | 'E_PARSE_FRONTMATTER'
  | 'E_CATALOG_SYNC_FAILED'
  | 'E_VALIDATION_FAILED'
  | 'E_STORAGE_BACKEND'
  | 'E_SCHEMA_INVALID'
  | 'E_PROVIDER_TIMEOUT'

export class SdkError extends Error {
  readonly code: SdkErrorCode
  readonly detail?: string

  constructor(message: string, code: SdkErrorCode, detail?: string) {
    super(message)
    this.name = 'SdkError'
    this.code = code
    this.detail = detail
  }

  display(): string {
    return this.detail ? `${this.message}: ${this.detail}` : this.message
  }
}
```

- [ ] **Step 8:** Write error test, verify passes:

```typescript
// packages/sdk/test/util/errors.test.ts
import { describe, expect, test } from 'bun:test'
import { SdkError } from '../../src/util/errors'

describe('SdkError', () => {
  test('extends Error', () => {
    const e = new SdkError('fail', 'E_COMPONENT_NOT_FOUND')
    expect(e).toBeInstanceOf(Error)
    expect(e.code).toBe('E_COMPONENT_NOT_FOUND')
  })

  test('display includes detail', () => {
    const e = new SdkError('fail', 'E_STORAGE_BACKEND', 'disk full')
    expect(e.display()).toBe('fail: disk full')
  })
})
```

- [ ] **Step 9:** Create `packages/sdk/src/util/index.ts` barrel:

```typescript
export * from './logger'
export * from './tracer'
export * from './metrics'
export * from './errors'
```

- [ ] **Step 10:** Run all tests: `bun test --cwd packages/sdk && bun test --cwd packages/cli`

- [ ] **Step 11:** Commit: `feat(sdk): add util/ surface — logger, tracer, metrics, errors`

---

## Phase 2: context/ surface

### Task 2.1: Move component types + build registry

**Files:**

- Move: `packages/core/src/component/types.ts` → `packages/sdk/src/context/types.ts`
- Create: `packages/sdk/src/context/component.ts`
- Create: `packages/sdk/src/context/registry.ts`
- Create: `packages/sdk/src/context/validator.ts`
- Create: `packages/sdk/test/context/types.test.ts`

- [ ] **Step 1:** `git mv packages/core/src/component/types.ts packages/sdk/src/context/types.ts`

- [ ] **Step 2:** Update import in moved file: `from '@agents/core/types'` stays correct (core still has types.ts).

- [ ] **Step 3:** Create `packages/sdk/src/context/component.ts` — the abstract ParsedComponent interface:

```typescript
import type { Result } from '@agents/core/types'
import type { ComponentType, ComponentMetadata } from './types'

/** A fully parsed component with raw content, typed frontmatter, and metadata. */
export interface ParsedComponent<T extends Record<string, unknown> = Record<string, unknown>> {
  readonly type: ComponentType
  readonly name: string
  readonly content: string
  readonly frontmatter: T
  readonly metadata: ComponentMetadata
}

/** Validation result from schema checking. */
export interface ValidationResult {
  valid: boolean
  errors: ValidationIssue[]
  warnings: ValidationIssue[]
}

export interface ValidationIssue {
  path: string
  message: string
  severity: 'error' | 'warning'
}

/** Opaque schema validator — wraps validation lib internally. */
export interface SchemaValidator<T> {
  validate(data: unknown): Result<T>
}
```

- [ ] **Step 4:** Create `packages/sdk/src/context/registry.ts` — the type module registry:

```typescript
import type { Result } from '@agents/core/types'
import type { ParsedComponent, SchemaValidator, ValidationResult } from './component'
import type { ComponentType } from './types'

/** Interface every component type module implements. */
export interface ComponentTypeModule<T extends Record<string, unknown> = Record<string, unknown>> {
  readonly type: ComponentType
  readonly schema: SchemaValidator<T>
  parse(path: string): Promise<Result<ParsedComponent<T>>>
  validate(component: ParsedComponent<T>): ValidationResult
}

const modules = new Map<ComponentType, ComponentTypeModule>()

export function registerComponentType<T extends Record<string, unknown>>(
  module: ComponentTypeModule<T>
): void {
  modules.set(module.type, module as ComponentTypeModule)
}

export function getComponentModule(
  type: ComponentType
): ComponentTypeModule | undefined {
  return modules.get(type)
}

export function getActiveTypes(): ComponentType[] {
  return [...modules.keys()]
}
```

- [ ] **Step 5:** Create `packages/sdk/src/context/validator.ts`:

```typescript
import * as v from 'valibot'
import { err, ok, type Result } from '@agents/core/types'
import type { SchemaValidator } from './component'

/** Create a SchemaValidator from a Valibot schema. */
export function createSchemaValidator<T>(schema: v.BaseSchema<unknown, T, v.BaseIssue<unknown>>): SchemaValidator<T> {
  return {
    validate(data: unknown): Result<T> {
      const result = v.safeParse(schema, data)
      if (result.success) return ok(result.output)
      const message = result.issues.map(i => i.message).join('; ')
      return err(new Error(message) as any)
    },
  }
}
```

- [ ] **Step 6:** Write tests and verify:

```typescript
// packages/sdk/test/context/types.test.ts
import { describe, expect, test } from 'bun:test'
import { COMPONENT_TYPES, parseComponentType, getActiveTypes } from '../../src/context/types'

describe('context types (moved from core)', () => {
  test('COMPONENT_TYPES has 12 entries', () => {
    expect(COMPONENT_TYPES).toHaveLength(12)
  })
  test('parseComponentType normalizes input', () => {
    expect(parseComponentType('mcp_server')).toBe('mcp-server')
    expect(parseComponentType('MCP-Server')).toBe('mcp-server')
  })
})
```

- [ ] **Step 7:** Update `packages/core/src/component/index.ts` to re-export from SDK for backward compat:

```typescript
// Temporarily re-export from SDK during migration
export * from '@agents/sdk/context/types'
```

Note: This requires adding `"@agents/sdk": "workspace:*"` to core's package.json. This creates a temporary circular workspace dep (core → sdk → core) that Bun handles for re-exports. Alternatively, keep types.ts in core and have SDK re-export from core. **Decision: keep the re-export direction as SDK being canonical, core re-exporting for backward compat.**

Actually — this circular dep is problematic. Better approach: **SDK re-exports core types during transition, not the reverse.** Keep `core/component/types.ts` as a re-export shim pointing to SDK. Wait — that's the same circular dep.

**Correct approach for Task 2.1:** Copy the file (don't move yet). SDK has the canonical version. Core keeps its copy unchanged. In Phase 6 (migration), core's copy gets replaced with a re-export or removed entirely. This avoids circular deps during the build-up phase.

- [ ] **Step 7 (revised):** Copy `packages/core/src/component/types.ts` to `packages/sdk/src/context/types.ts`. Both copies exist temporarily. SDK version becomes canonical; core version is frozen and will be removed in Phase 6.

- [ ] **Step 8:** Create `packages/sdk/src/context/index.ts` barrel:

```typescript
export * from './component'
export * from './types'
export * from './registry'
export * from './validator'
```

- [ ] **Step 9:** Run all tests. Commit: `feat(sdk): add context/ types, registry, and validator`

### Task 2.2: Build per-type modules (skill, rule, hook, etc.)

**Files:**

- Create: `packages/sdk/src/context/skill/types.ts`
- Create: `packages/sdk/src/context/skill/schema.ts`
- Create: `packages/sdk/src/context/skill/parser.ts`
- Create: `packages/sdk/src/context/skill/index.ts`
- Repeat for: rule, hook, command, output-style, agent, mcp, plugin
- Create: `packages/sdk/src/context/parser.ts` (generic dispatcher)
- Create: `packages/sdk/test/context/skill.test.ts`

- [ ] **Step 1:** Create skill type module — `packages/sdk/src/context/skill/types.ts`:

```typescript
/** Skill-specific frontmatter shape. */
export interface SkillFrontmatter {
  name: string
  description?: string
  version?: string
  tags?: string[]
  [key: string]: unknown
}
```

- [ ] **Step 2:** Create skill schema — `packages/sdk/src/context/skill/schema.ts`:

```typescript
import * as v from 'valibot'
import { createSchemaValidator } from '../validator'

export const SkillFrontmatterSchema = v.object({
  name: v.string(),
  description: v.optional(v.string()),
  version: v.optional(v.string()),
  tags: v.optional(v.array(v.string())),
})

export const skillSchemaValidator = createSchemaValidator(SkillFrontmatterSchema)
```

- [ ] **Step 3:** Create skill parser — `packages/sdk/src/context/skill/parser.ts`:

```typescript
import { load as yamlLoad } from 'js-yaml'
import { readTextFile } from '@agents/core/file-io'
import { err, ok, type Result } from '@agents/core/types'
import type { ParsedComponent, ValidationResult, ValidationIssue } from '../component'
import type { ComponentMetadata } from '../types'
import { SdkError } from '../../util/errors'
import type { SkillFrontmatter } from './types'
import { skillSchemaValidator } from './schema'

/** Parse YAML frontmatter from markdown content. */
function parseFrontmatter(content: string): { attrs: Record<string, unknown>; body: string } {
  const match = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/)
  if (!match) return { attrs: {}, body: content }
  try {
    return { attrs: (yamlLoad(match[1]) as Record<string, unknown>) ?? {}, body: match[2] ?? '' }
  } catch {
    return { attrs: {}, body: content }
  }
}

/** Compute basic metadata from content. */
function computeMetadata(content: string, body: string): ComponentMetadata {
  const lines = content.split('\n')
  const headings = lines
    .filter(l => l.startsWith('#'))
    .map(l => {
      const match = l.match(/^(#{1,6})\s+(.*)/)
      return match ? { depth: match[1]!.length, title: match[2]!.trim() } : null
    })
    .filter(Boolean) as Array<{ depth: number; title: string }>

  return {
    wordCount: body.split(/\s+/).filter(Boolean).length,
    sectionCount: headings.length,
    headingTree: headings,
    lineCount: lines.length,
  }
}

export async function parseSkill(path: string): Promise<Result<ParsedComponent<SkillFrontmatter>>> {
  const content = await readTextFile(path)
  if (!content.ok) {
    return err(new SdkError(`Failed to read skill at ${path}`, 'E_COMPONENT_NOT_FOUND', content.error.message))
  }

  const { attrs, body } = parseFrontmatter(content.value)
  const validated = skillSchemaValidator.validate(attrs)
  if (!validated.ok) {
    return err(new SdkError(`Invalid skill frontmatter in ${path}`, 'E_PARSE_FRONTMATTER', String(validated.error)))
  }

  const metadata = computeMetadata(content.value, body)

  return ok({
    type: 'skill',
    name: validated.value.name,
    content: content.value,
    frontmatter: validated.value,
    metadata,
  })
}
```

- [ ] **Step 4:** Create `packages/sdk/src/context/skill/index.ts`:

```typescript
import type { ComponentTypeModule } from '../registry'
import type { SkillFrontmatter } from './types'
import { skillSchemaValidator } from './schema'
import { parseSkill } from './parser'

export const skillModule: ComponentTypeModule<SkillFrontmatter> = {
  type: 'skill',
  schema: skillSchemaValidator,
  parse: parseSkill,
  validate(component) {
    const result = skillSchemaValidator.validate(component.frontmatter)
    return {
      valid: result.ok,
      errors: result.ok ? [] : [{ path: 'frontmatter', message: String(result.error), severity: 'error' as const }],
      warnings: [],
    }
  },
}

export * from './types'
export * from './schema'
export * from './parser'
```

- [ ] **Step 5:** Write skill parser test:

```typescript
// packages/sdk/test/context/skill.test.ts
import { describe, expect, test } from 'bun:test'
import { parseSkill } from '../../src/context/skill/parser'
import { skillModule } from '../../src/context/skill'
import { mkdtemp, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

describe('parseSkill', () => {
  test('parses valid SKILL.md', async () => {
    const dir = await mkdtemp(join(tmpdir(), 'sdk-test-'))
    const path = join(dir, 'SKILL.md')
    await writeFile(path, '---\nname: test-skill\ndescription: A test\ntags:\n  - testing\n---\n\n# Test Skill\n\nContent here.\n')
    const result = await parseSkill(path)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.value.name).toBe('test-skill')
      expect(result.value.type).toBe('skill')
      expect(result.value.frontmatter.description).toBe('A test')
      expect(result.value.metadata.wordCount).toBeGreaterThan(0)
    }
  })

  test('returns error for missing file', async () => {
    const result = await parseSkill('/nonexistent/SKILL.md')
    expect(result.ok).toBe(false)
  })

  test('module has correct type', () => {
    expect(skillModule.type).toBe('skill')
  })
})
```

- [ ] **Step 6:** Run tests, verify passes.

- [ ] **Step 7:** Create leaf type modules (rule, hook, command, output-style, agent) — each follows the same pattern as skill but with appropriate schemas. These are simpler (frontmatter-only markdown files). Create one file per module with types.ts + schema.ts + parser.ts + index.ts.

- [ ] **Step 8:** Create MCP type module — `packages/sdk/src/context/mcp/` — handles mcp-server, mcp-client, mcp-tool (JSON configs, not markdown).

- [ ] **Step 9:** Create plugin type module — `packages/sdk/src/context/plugin/` — composite, imports from skill, rule, mcp, output-style, command. Include PluginManifest, PluginSourcesManifest, MarketplaceManifest schemas (moved from `core/schemas.ts`).

- [ ] **Step 9b:** Create placeholder type modules — `packages/sdk/src/context/persona/types.ts` and `packages/sdk/src/context/lsp/types.ts`. Minimal exports (type definition only, no schema/parser — these are not yet implemented).

- [ ] **Step 10:** Create generic dispatcher — `packages/sdk/src/context/parser.ts`:

```typescript
import { err, type Result } from '@agents/core/types'
import type { ParsedComponent } from './component'
import type { ComponentType } from './types'
import { getComponentModule } from './registry'
import { SdkError } from '../util/errors'

export async function parseComponent(
  type: ComponentType,
  path: string
): Promise<Result<ParsedComponent>> {
  const mod = getComponentModule(type)
  if (!mod) return err(new SdkError(`No parser for type '${type}'`, 'E_COMPONENT_NOT_FOUND'))
  return mod.parse(path)
}
```

- [ ] **Step 11:** Register all modules in `packages/sdk/src/context/index.ts`:

```typescript
import { registerComponentType } from './registry'
import { skillModule } from './skill'
import { ruleModule } from './rule'
// ... other modules

// Auto-register all built-in types
registerComponentType(skillModule)
registerComponentType(ruleModule)
// ...

export * from './component'
export * from './types'
export * from './registry'
export * from './validator'
export * from './parser'
```

- [ ] **Step 12:** Run all tests. Commit: `feat(sdk): add context/ surface with per-type modules`

---

## Phase 3: providers/ surface

### Task 3.1: Move provider interface + manager

**Files:**

- Copy: `packages/core/src/component/manager.ts` → `packages/sdk/src/providers/manager.ts`
- Copy: `packages/core/src/component/pagination.ts` → `packages/sdk/src/providers/pagination.ts`
- Create: `packages/sdk/src/providers/interface.ts`
- Create: `packages/sdk/src/providers/factory.ts`
- Create: `packages/sdk/src/providers/index.ts`
- Create: `packages/sdk/test/providers/manager.test.ts`

- [ ] **Step 1:** Create `packages/sdk/src/providers/interface.ts` — re-export the ComponentProvider types from context/types (they're already defined there: ComponentProvider, ProviderCapabilities, SearchParams, etc.)

```typescript
// Re-export provider-related types from context
export type {
  ComponentProvider,
  ProviderCapabilities,
  SearchParams,
  PaginatedResult,
  ComponentAddOptions,
  ComponentAddResult,
  RemoveResult,
  PublishOptions,
  PublishResult,
  Component,
} from '../context/types'
```

- [ ] **Step 2:** Copy `packages/core/src/component/manager.ts` to `packages/sdk/src/providers/manager.ts`. Update imports: reference `../context/types` for component types, and replace `CliError` with `SdkError` from `../util/errors` in all error paths.

- [ ] **Step 3:** Copy `packages/core/src/component/pagination.ts` to `packages/sdk/src/providers/pagination.ts`.

- [ ] **Step 4:** Write manager test (port from `packages/cli/test/component/manager.test.ts` — adapt imports).

- [ ] **Step 5:** Run tests, verify passes.

- [ ] **Step 6:** Commit: `feat(sdk): add providers/ manager and pagination`

### Task 3.2: Move concrete providers

**Files:**

- Copy: `packages/cli/src/lib/component/provider-local.ts` → `packages/sdk/src/providers/local/skill.ts` (and split others)
- Copy: `packages/cli/src/lib/component/provider-smithery.ts` → `packages/sdk/src/providers/smithery/index.ts`
- Copy: AI client files
- Create: `packages/sdk/src/providers/factory.ts`

- [ ] **Step 1:** Copy local providers from CLI to SDK. The `provider-local.ts` (skill provider) uses dynamic imports to `skill-list`, `skill-add`, `skill-remove`, `skill-info`. **Resolution: refactor to dependency injection.** The SDK's `LocalSkillProvider` accepts a `SkillOperations` interface in its constructor:

```typescript
// packages/sdk/src/providers/local/skill-ops.ts
export interface SkillOperations {
  list(opts: { cwd?: string; agent?: string }): Promise<any>
  add(source: string, opts: any): Promise<any>
  remove(names: string[], opts: any): Promise<any[]>
  info(name: string, opts: any): Promise<any>
}
```

The SDK provider calls `this.ops.list()` instead of `await import('../skill-list')`. The CLI wires the real implementations when constructing the provider:

```typescript
// In CLI's factory.ts
import { listSkills } from '../lib/skill-list'
import { addSkill } from '../lib/skill-add'
const provider = new LocalSkillProvider({ list: listSkills, add: addSkill, ... })
```

This cleanly breaks the circular dependency: SDK defines the interface, CLI provides the implementation. Same pattern applies to other providers that import from `chunker.ts` or `manifest.ts` — inject the parsing functions rather than importing them.

For `provider-agent.ts`, `provider-command.ts`, `provider-rule.ts`, `provider-output-style.ts`: these import `parseFrontmatter` from `chunker.ts`. Since the SDK's `context/parser.ts` already provides frontmatter parsing, these providers can import from `@agents/sdk/context` instead — no injection needed, the dependency flows correctly (providers → context).

For `provider-plugin.ts`: it imports `readPluginManifest` from `manifest.ts`. Inject via a `PluginOperations` interface, same pattern as skill.

- [ ] **Step 2:** Copy Smithery provider + auth + publish.

- [ ] **Step 3:** Copy client registry + client config from `packages/core/src/component/`.

- [ ] **Step 4:** Create factory:

```typescript
// packages/sdk/src/providers/factory.ts
import type { Logger } from '../util/logger'
import { ProviderManager } from './manager'

export function createDefaultProviders(opts?: {
  cwd?: string
  smitheryBaseUrl?: string
  logger?: Logger
}): ProviderManager {
  const manager = new ProviderManager()
  // Register providers lazily to avoid import weight
  // Implementations loaded on first use
  return manager
}
```

- [ ] **Step 5:** Create GitHub provider skeleton — `packages/sdk/src/providers/github/index.ts` and `packages/sdk/src/providers/github/search.ts`. This is a new provider (no CLI source to copy). Implement `GitHubProvider` that searches GitHub repos/topics for components using the `@agents/core/github` module. For the initial SDK, implement `search` capability only (list, add, remove, info, publish return unsupported errors). Use GitHub code search for `SKILL.md` files and topic search for `claude-code-skill`.

- [ ] **Step 6:** Create barrel, run tests. Commit: `feat(sdk): add providers/ with local, smithery, github, and client registry`

---

## Phase 4: catalog/ surface

### Task 4.1: Define catalog interfaces and types

**Files:**

- Create: `packages/sdk/src/catalog/interface.ts`
- Create: `packages/sdk/src/catalog/types.ts`
- Create: `packages/sdk/test/catalog/types.test.ts`

- [ ] **Step 1:** Create types (CatalogEntry, CatalogQuery, CatalogFilter, SyncResult, StaleResult, ErrorRecord, DiscoveryResult) as defined in the spec.

- [ ] **Step 2:** Create split interfaces (CatalogReader, CatalogWriter, CatalogStore) as defined in the spec.

- [ ] **Step 3:** Write interface type tests (structural).

- [ ] **Step 4:** Commit: `feat(sdk): add catalog/ interfaces and types`

### Task 4.2: Build NDJSON store

**Files:**

- Create: `packages/sdk/src/catalog/ndjson/index.ts`
- Create: `packages/sdk/src/catalog/ndjson/io.ts`
- Create: `packages/sdk/src/catalog/manager.ts`
- Create: `packages/sdk/test/catalog/ndjson.test.ts`

- [ ] **Step 1:** Port atomic NDJSON I/O from `packages/cli/src/lib/catalog.ts` (readCatalog, atomic write pattern) into `packages/sdk/src/catalog/ndjson/io.ts`.

- [ ] **Step 2:** Implement NdjsonStore implementing CatalogStore.

- [ ] **Step 3:** Implement CatalogManager wrapping a CatalogStore.

- [ ] **Step 4:** Write tests for NDJSON round-trip, query, upsert, remove.

- [ ] **Step 5:** Commit: `feat(sdk): add catalog/ NDJSON store and manager`

### Task 4.3: Build SQLite store (stub)

**Files:**

- Create: `packages/sdk/src/catalog/sqlite/index.ts`
- Create: `packages/sdk/src/catalog/sqlite/schema.sql`

- [ ] **Step 1:** Create SqliteStore skeleton implementing CatalogStore. All methods return `err(new SdkError('Not implemented', 'E_STORAGE_BACKEND'))` for now.

- [ ] **Step 2:** Define schema.sql with table definitions matching CatalogEntry.

- [ ] **Step 3:** Commit: `feat(sdk): add catalog/ SQLite store skeleton`

---

## Phase 5: ui/ surface

### Task 5.1: Build Renderer interface and adapters

**Files:**

- Create: `packages/sdk/src/ui/interface.ts`
- Create: `packages/sdk/src/ui/cli.ts`
- Create: `packages/sdk/src/ui/json.ts`
- Create: `packages/sdk/src/ui/silent.ts`
- Create: `packages/sdk/src/ui/index.ts`
- Create: `packages/sdk/test/ui/renderer.test.ts`

- [ ] **Step 1:** Create `packages/sdk/src/ui/interface.ts` with Renderer, ProgressHandle, TreeNode.

- [ ] **Step 2:** Port `packages/core/src/output.ts` to `packages/sdk/src/ui/cli.ts` as CliRenderer implementing Renderer. Rename `createOutput` → `createCliRenderer` (export both for backward compat). Also rename `spinner()` → `progress()` and `SpinnerHandle` → `ProgressHandle` to match the `Renderer` interface. Keep `spinner` as a deprecated alias on CliRenderer for backward compat during CLI migration.

- [ ] **Step 3:** Create JsonRenderer (JSON to stdout, matching current JSON output mode).

- [ ] **Step 4:** Create SilentRenderer (noop — for tests and headless consumers).

- [ ] **Step 5:** Create `createRenderer({ mode, quiet })` factory in `packages/sdk/src/ui/index.ts`.

- [ ] **Step 6:** Write tests:

```typescript
// packages/sdk/test/ui/renderer.test.ts
import { describe, expect, test } from 'bun:test'
import { createRenderer } from '../../src/ui'

describe('createRenderer', () => {
  test('silent mode produces no output', () => {
    const r = createRenderer({ mode: 'silent' })
    // Should not throw
    r.info('test')
    r.success('test')
    r.table([{ a: 1 }])
  })

  test('json mode is available', () => {
    const r = createRenderer({ mode: 'json' })
    expect(r).toBeDefined()
  })
})
```

- [ ] **Step 7:** Run all tests. Commit: `feat(sdk): add ui/ surface with Renderer interface and 3 adapters`

---

## Phase 6: CLI migration

### Task 6.1: Migrate CLI imports from core/component to sdk/context

**Files:**

- Modify: All `packages/cli/src/commands/*.ts` that import from `@agents/core/component/*`
- Modify: All `packages/cli/src/lib/component/*.ts` (providers)
- Modify: All `packages/cli/test/component/*.ts`

- [ ] **Step 1:** Bulk replace in CLI source:
  - `from '@agents/core/component/types'` → `from '@agents/sdk/context/types'`
  - `from '@agents/core/component/manager'` → `from '@agents/sdk/providers/manager'`
  - `from '@agents/core/component/pagination'` → `from '@agents/sdk/providers/pagination'`
  - `from '@agents/core/component'` → `from '@agents/sdk/context'`

- [ ] **Step 2:** Run tests, fix any broken imports.

- [ ] **Step 3:** Commit: `refactor(cli): migrate component imports to @agents/sdk`

### Task 6.2: Migrate CLI imports from core/output to sdk/ui

**Files:**

- Modify: All `packages/cli/src/commands/*.ts` that import `createOutput`

- [ ] **Step 1:** Replace `from '@agents/core/output'` → `from '@agents/sdk/ui'` and rename `createOutput` to `createRenderer` (or keep both exported for backward compat).

- [ ] **Step 2:** Run tests, fix any broken imports.

- [ ] **Step 3:** Commit: `refactor(cli): migrate output imports to @agents/sdk/ui`

### Task 6.3: Remove moved code from core

**Files:**

- Remove: `packages/core/src/component/` (entire directory)
- Remove: `packages/core/src/output.ts`
- Modify: `packages/core/src/schemas.ts` (remove component schemas, keep infrastructure ones or remove entirely if all dissolved)
- Modify: `packages/core/src/index.ts` (remove re-exports)

- [ ] **Step 1:** Delete `packages/core/src/component/` directory.
- [ ] **Step 2:** Delete `packages/core/src/output.ts`.
- [ ] **Step 3:** Update `packages/core/src/index.ts` to remove component and output exports.
- [ ] **Step 4:** Dissolve `packages/core/src/schemas.ts` — move remaining infrastructure schemas to appropriate locations (lockfile schemas → `sdk/providers/local/schemas.ts`, etc.) or keep in core if still needed by core modules.
- [ ] **Step 5:** Run all tests across all three packages.
- [ ] **Step 6:** Commit: `refactor(core): remove component model and output — now in @agents/sdk`

### Task 6.4: Rename core CliError to BaseError

**Files:**

- Modify: `packages/core/src/types.ts`
- Modify: All files importing CliError from core

- [ ] **Step 1:** In `packages/core/src/types.ts`, rename `CliError` → `BaseError`. Keep `CliError` as a type alias for backward compat. Also update the `Result` type alias default: `Result<T, E = BaseError>`:

```typescript
export class BaseError extends Error { ... }
/** @deprecated Use BaseError */
export { BaseError as CliError }
export type Result<T, E = BaseError> = ...
```

- [ ] **Step 2:** Update all core-internal references from `CliError` to `BaseError` (file-io.ts, config.ts, git.ts, github.ts).
- [ ] **Step 3:** Run tests, verify passes.
- [ ] **Step 3:** Commit: `refactor(core): rename CliError to BaseError`

### Task 6.5: Final verification

- [ ] **Step 1:** `bun test --cwd packages/core` — all pass
- [ ] **Step 2:** `bun test --cwd packages/sdk` — all pass
- [ ] **Step 3:** `bun test --cwd packages/cli` — zero regressions
- [ ] **Step 4:** Verify deep imports work: create a scratch file that imports from `@agents/sdk/context`, `@agents/sdk/providers`, `@agents/sdk/catalog`, `@agents/sdk/ui`, `@agents/sdk/util`.
- [ ] **Step 5:** Commit: `chore: verify @agents/sdk integration complete`

---

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Circular workspace deps (core↔sdk) | Medium | High | Copy files during build-up, delete originals in Phase 6 only |
| Dynamic imports break after path changes | Medium | Medium | Test each provider after move |
| schemas.ts dissolution leaves orphans | Low | Medium | Grep for all schema imports before removing |
| CLI test regressions from import changes | Medium | High | Run full CLI suite after every task |
| js-yaml not in SDK deps | Certain | Low | Add to SDK package.json |

### Dependencies to add to SDK package.json (during implementation)

```json
{
  "dependencies": {
    "@agents/core": "workspace:*",
    "valibot": "^1.0.0",
    "js-yaml": "^4.1.0"
  }
}
```

Additional deps added per phase:

- Phase 3: `@napi-rs/keyring`, `@octokit/auth-oauth-device`, `@octokit/core` (for smithery auth + GitHub provider)
- Phase 5: `ansis`, `console-table-printer`, `nanospinner` (for CLI renderer)
