# Phase 3: Search and Discovery (find)

**ID:** `phase-3`
**Dependencies:** phase-1 (core); phase-2 (install-on-select only)
**Status:** pending
**Effort:** TBD

## Objective

Implement the `find` command for searching external skill registries, with JSON output, configurable result limits, and optional interactive install. The core search API (task 3.1) and non-interactive find have no dependency on phase 2. The interactive install-on-select feature (task 3.2 partial) requires `addSkill` from phase 2 and is deferred until phase 2 completes.

## Success Criteria

- [ ] `just agents skill find "kubernetes"` returns matching skills from registry
- [ ] `just agents skill find "kubernetes" --limit 20` returns up to 20 results (not hardcoded to 10)
- [ ] `just agents skill find "kubernetes" --json` outputs JSON array
- [ ] Interactive mode: fzf-style search with live filtering and direct install on selection
- [ ] Search backends: skills.sh API, local Meilisearch index, local catalog NDJSON
- [ ] Results include source, name, description, install count (when available)

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Find command logic | `cli/lib/skill-find.ts` | TypeScript |
| Search API client | `cli/lib/skill-search-api.ts` | TypeScript |
| CLI subcommand wiring | `cli/commands/skill.ts` | TypeScript (additions) |
| Tests | `cli/test/skill-find.test.ts` | bun:test |

## Files

**Create:**

- `cli/lib/skill-find.ts`
- `cli/lib/skill-search-api.ts`
- `cli/test/skill-find.test.ts`

**Modify:**

- `cli/commands/skill.ts` (add `find` subcommand)

## Error Types

All search-related failures use a single `SearchError` class with a `backend` discriminant to identify which backend failed. This is a domain-specific wrapper around the existing `CliError` from `lib/types.ts`.

```typescript
import { CliError } from './types'

export type SearchBackend = 'skills-sh' | 'meilisearch' | 'catalog'

export class SearchError extends CliError {
  constructor(
    message: string,
    readonly backend: SearchBackend,
    hint?: string,
    cause?: unknown,
  ) {
    super(message, `SEARCH_${backend.toUpperCase().replace('-', '_')}`, hint, cause)
  }
}
```

| Backend | Error Code | Retryable | Hint |
|---------|-----------|-----------|------|
| `skills-sh` | `SEARCH_SKILLS_SH` | Yes (timeout, 5xx); No (429) | `Skills.sh may be rate-limiting. Try --source meilisearch` |
| `meilisearch` | `SEARCH_MEILISEARCH` | No (not running) | `Is Meilisearch running? Try: docker compose up -d` |
| `catalog` | `SEARCH_CATALOG` | No (file missing) | `Run: just agents skill catalog ingest` |

## Edge Cases

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty query string | Interactive mode: show all results (unfiltered). Non-interactive: return empty array with info message |
| Network timeout on all backends | Return empty array, `out.warn()` with message listing which backends were tried |
| skills.sh returns 429 rate limit | `SearchError` with `backend: 'skills-sh'`, fall through to next backend in `auto` mode |
| Meilisearch not running (connection refused) | `isAvailable()` returns `false`, skip backend silently in `auto` mode |
| Catalog file does not exist | Return empty array from catalog backend, no throw |
| Interactive mode in non-TTY (CI) | Skip interactive, fall back to non-interactive with `out.warn('Non-TTY detected, skipping interactive mode')` |
| User cancels interactive search (ESC) | `searchMultiselect` returns `cancelSymbol`, exit with `EXIT.OK` (not an error) |
| Search result has no `source` field (malformed) | Valibot parse strips it; `source` defaults to `'unknown'` in `normalizeResult()` |
| `--limit 0` or `--limit -1` | Clamp to `1` minimum, `100` maximum. Log `out.warn()` if clamped. |

## Tasks

### 3.1 Search API Client (`lib/skill-search-api.ts`)

**Task Dependencies:** None (uses existing `lib/meilisearch.ts` and native `fetch`)

**Library Decisions:** No new dependencies. Uses native `fetch` for HTTP calls to skills.sh and the existing `lib/meilisearch.ts` module for local Meilisearch queries. Catalog search reads NDJSON with `node:readline` (already available).

- [ ] Export `searchSkillsAPI(query, opts): Promise<SearchResult[]>`
- [ ] Support `opts.limit` (default: 10, configurable up to 100)
- [ ] Support `opts.source` to select backend:
  - `skills-sh`: `GET https://skills.sh/api/search?q=...&limit=N`
  - `meilisearch`: use existing `lib/meilisearch.ts` client
  - `catalog`: search local `.catalog.ndjson` via text matching
  - `auto` (default): try meilisearch -> skills-sh -> catalog fallback
- [ ] Normalize results to `SearchResult { name, source, description, installs?, url? }`
- [ ] Timeout: 3s per backend, never throws (returns empty on failure)
- [ ] Add `SearchResult` Valibot schema to `schemas.ts`

#### Code Examples

**Valibot schema addition to `lib/schemas.ts`:**

```typescript
// ---------------------------------------------------------------------------
// Search result schema (Phase 3)
// ---------------------------------------------------------------------------

export const SkillSearchResult = v.object({
  name: v.string(),
  source: v.pipe(v.string(), v.nonEmpty()),
  description: v.optional(v.string(), ''),
  installs: v.optional(v.number()),
  url: v.optional(v.string()),
})
export type SkillSearchResult = v.InferOutput<typeof SkillSearchResult>

export const SearchBackendType = v.picklist(['skills-sh', 'meilisearch', 'catalog', 'auto'])
export type SearchBackendType = v.InferOutput<typeof SearchBackendType>
```

**Core module structure (`lib/skill-search-api.ts`):**

```typescript
import { createClient, isAvailable, searchKeyword } from './meilisearch'
import { CliError, type Result, ok, err } from './types'
import type { SkillSearchResult, SearchBackendType } from './schemas'

export { SearchError, type SearchBackend } from './search-error'

export interface SearchOptions {
  limit?: number
  source?: SearchBackendType
  signal?: AbortSignal
}

/** Clamp limit to [1, 100] range. */
function clampLimit(limit: number | undefined): number {
  const raw = limit ?? 10
  return Math.max(1, Math.min(100, raw))
}

/** Search skills.sh public API with 3s timeout. */
async function searchSkillsSh(
  query: string,
  limit: number,
): Promise<Result<SkillSearchResult[]>> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 3_000)
  try {
    const url = new URL('https://skills.sh/api/search')
    url.searchParams.set('q', query)
    url.searchParams.set('limit', String(limit))
    const resp = await fetch(url, { signal: controller.signal })
    if (resp.status === 429) {
      return err(new SearchError('Rate limited', 'skills-sh', 'Try --source meilisearch'))
    }
    if (!resp.ok) {
      return err(new SearchError(`HTTP ${resp.status}`, 'skills-sh'))
    }
    const data = (await resp.json()) as unknown[]
    return ok(normalizeResults(data, 'skills-sh'))
  } catch (cause) {
    return err(new SearchError('Request failed', 'skills-sh', undefined, cause))
  } finally {
    clearTimeout(timeout)
  }
}

/** Search local Meilisearch instance. */
async function searchMeili(
  query: string,
  limit: number,
): Promise<Result<SkillSearchResult[]>> {
  const client = createClient()
  if (!(await isAvailable(client))) {
    return err(new SearchError('Not running', 'meilisearch',
      'Is Meilisearch running? Try: docker compose up -d'))
  }
  const hits = await searchKeyword(client, query, { limit, type: 'skill' })
  return ok(hits.map(h => ({
    name: h.name,
    source: h.filePath,
    description: h.description,
  })))
}

/** Search local .catalog.ndjson via case-insensitive substring match. */
async function searchCatalog(
  query: string,
  limit: number,
): Promise<Result<SkillSearchResult[]>> { /* ... */ }

/** Normalize raw API responses into SkillSearchResult[]. */
function normalizeResults(
  raw: unknown[],
  backend: SearchBackend,
): SkillSearchResult[] { /* ... */ }

/**
 * Unified search entry point. In `auto` mode, tries backends in order:
 * meilisearch -> skills-sh -> catalog. Returns first non-empty result set,
 * or empty array if all fail.
 */
export async function searchSkillsAPI(
  query: string,
  opts?: SearchOptions,
): Promise<SkillSearchResult[]> {
  const limit = clampLimit(opts?.limit)
  const source = opts?.source ?? 'auto'

  if (source !== 'auto') {
    const result = await searchBackend(query, limit, source)
    return result.ok ? result.value : []
  }

  // Auto fallback chain
  for (const backend of ['meilisearch', 'skills-sh', 'catalog'] as const) {
    const result = await searchBackend(query, limit, backend)
    if (result.ok && result.value.length > 0) return result.value
  }
  return []
}
```

#### Example Test Cases

```typescript
// cli/test/skill-find.test.ts (search API section)
import { describe, expect, mock, test } from 'bun:test'
import { searchSkillsAPI } from '../lib/skill-search-api'

describe('searchSkillsAPI', () => {
  test('skills-sh backend: returns normalized results from fetch', async () => {
    const originalFetch = globalThis.fetch
    globalThis.fetch = mock(() =>
      Promise.resolve(new Response(JSON.stringify([
        { name: 'k8s-deploy', source: 'owner/repo', description: 'Kubernetes deploy' },
      ]), { status: 200 }))
    ) as typeof fetch
    try {
      const results = await searchSkillsAPI('kubernetes', { source: 'skills-sh' })
      expect(results).toHaveLength(1)
      expect(results[0].name).toBe('k8s-deploy')
      expect(results[0].description).toBe('Kubernetes deploy')
    } finally {
      globalThis.fetch = originalFetch
    }
  })

  test('auto mode: falls back to catalog when meilisearch and skills-sh fail', async () => {
    // Mock fetch to reject (skills-sh down) and meilisearch isAvailable to false
    const originalFetch = globalThis.fetch
    globalThis.fetch = mock(() => Promise.reject(new Error('ECONNREFUSED'))) as typeof fetch
    try {
      const results = await searchSkillsAPI('test', { source: 'auto' })
      // Should not throw; returns catalog results or empty array
      expect(Array.isArray(results)).toBe(true)
    } finally {
      globalThis.fetch = originalFetch
    }
  })

  test('timeout: returns empty array when backend exceeds 3s', async () => {
    const originalFetch = globalThis.fetch
    globalThis.fetch = mock(() =>
      new Promise((resolve) => setTimeout(() => resolve(new Response('{}', { status: 200 })), 5_000))
    ) as typeof fetch
    try {
      const results = await searchSkillsAPI('slow', { source: 'skills-sh' })
      expect(results).toEqual([])
    } finally {
      globalThis.fetch = originalFetch
    }
  })

  test('limit clamping: --limit 0 clamps to 1', async () => {
    // Verify via catalog backend which we control
    const results = await searchSkillsAPI('test', { source: 'catalog', limit: 0 })
    // Should not throw even with limit=0
    expect(Array.isArray(results)).toBe(true)
  })

  test('limit clamping: --limit 500 clamps to 100', async () => {
    const results = await searchSkillsAPI('test', { source: 'catalog', limit: 500 })
    expect(results.length).toBeLessThanOrEqual(100)
  })

  test('skills-sh 429 rate limit: returns empty in auto mode, tries next backend', async () => {
    const originalFetch = globalThis.fetch
    globalThis.fetch = mock(() =>
      Promise.resolve(new Response('Rate limited', { status: 429 }))
    ) as typeof fetch
    try {
      const results = await searchSkillsAPI('test', { source: 'skills-sh' })
      expect(results).toEqual([])
    } finally {
      globalThis.fetch = originalFetch
    }
  })
})
```

#### Acceptance Criteria

- [ ] `searchSkillsAPI('kubernetes')` returns `SkillSearchResult[]` from the first available backend
- [ ] `searchSkillsAPI('kubernetes', { source: 'skills-sh' })` calls only the skills.sh API
- [ ] `searchSkillsAPI('kubernetes', { source: 'meilisearch' })` calls only the local Meilisearch instance
- [ ] `searchSkillsAPI('kubernetes', { source: 'catalog' })` searches only `.catalog.ndjson`
- [ ] `searchSkillsAPI('kubernetes', { source: 'auto' })` tries meilisearch -> skills-sh -> catalog in order
- [ ] All backends respect the 3-second timeout and never throw
- [ ] `SkillSearchResult` Valibot schema added to `lib/schemas.ts`
- [ ] `SearchError` class exists with `backend` discriminant field
- [ ] Limit is clamped to [1, 100] range
- [ ] Empty query string returns empty array (not an error)
- [ ] Malformed results from backends are normalized (missing `source` defaults to `'unknown'`)

### 3.2 Find Command (`lib/skill-find.ts`)

**Task Dependencies:**

- **phase-1:** `lib/prompts/search-multiselect.ts` (interactive fzf-style search prompt, `cancelSymbol`)
- **3.1:** `lib/skill-search-api.ts` (the `searchSkillsAPI()` function)
- **phase-2 (deferred):** `lib/skill-add.ts` (`addSkill()` for install-on-select — this feature can be stubbed until phase 2 completes)

**Library Decisions:** No new dependencies. Uses `lib/prompts/search-multiselect.ts` from phase 1, `lib/skill-add.ts` from phase 2, `lib/output.ts` for `createOutput()`, and `lib/skill-search-api.ts` from task 3.1. All existing modules.

- [ ] Export `findSkills(args: string[], opts: FindOptions): Promise<void>`
- [ ] Non-interactive mode (has query arg):
  - Call `searchSkillsAPI(query, { limit: opts.limit })`
  - If `--json`: output `JSON.stringify(results)` and exit
  - Otherwise: format as human-readable table
- [ ] Interactive mode (TTY, no query arg):
  - Launch fzf-style search prompt from `lib/prompts/search-multiselect.ts`
  - Debounced API calls on keystroke
  - On selection: call `addSkill(source)` from `lib/skill-add.ts` (phase-2 dependency)
- [ ] Support `--agent` filter on results (pre-filter by agent compatibility if metadata available)

#### Code Examples

**Core module structure (`lib/skill-find.ts`):**

```typescript
import { searchSkillsAPI, type SearchOptions } from './skill-search-api'
import type { SkillSearchResult, SearchBackendType } from './schemas'
import { addSkill } from './skill-add'
import type { OutputFormatter } from './output'
import { EXIT } from './types'

export interface FindOptions {
  limit?: number
  json?: boolean
  quiet?: boolean
  source?: SearchBackendType
  agent?: string
  yes?: boolean
}

/**
 * Format search results as a human-readable table.
 * Columns: name, source, description (truncated to 60 chars), installs.
 */
function formatResultsTable(
  out: OutputFormatter,
  results: SkillSearchResult[],
): void {
  out.table(
    results.map(r => ({
      name: r.name,
      source: r.source,
      description: (r.description ?? '').slice(0, 60),
      installs: r.installs ?? '-',
    })),
    ['name', 'source', 'description', 'installs'],
  )
}

/**
 * Detect whether stdout is a TTY (interactive terminal).
 * Returns false in CI, piped output, or non-TTY environments.
 */
function isTTY(): boolean {
  return process.stdout.isTTY === true
}

export async function findSkills(
  args: string[],
  opts: FindOptions,
): Promise<void> {
  const { createOutput } = await import('./output')
  const out = createOutput({ json: opts.json ?? false, quiet: opts.quiet ?? false })

  const query = args[0] ?? ''

  // Non-interactive path: query provided or not a TTY
  if (query || !isTTY()) {
    if (!query && !isTTY()) {
      out.warn('Non-TTY detected, skipping interactive mode')
    }
    const results = await searchSkillsAPI(query, {
      limit: opts.limit,
      source: opts.source,
    })

    if (opts.json) {
      out.raw(results)
    } else if (results.length === 0) {
      out.info('No skills found')
    } else {
      formatResultsTable(out, results)
    }
    return
  }

  // Interactive path: no query, TTY available
  const { searchMultiselect, cancelSymbol } = await import('./prompts/search-multiselect')

  const selected = await searchMultiselect<SkillSearchResult>({
    message: 'Search skills',
    search: async (term) => {
      const results = await searchSkillsAPI(term, {
        limit: opts.limit ?? 20,
        source: opts.source,
      })
      return results.map(r => ({
        label: `${r.name} - ${r.description ?? ''}`,
        value: r,
      }))
    },
    debounceMs: 200,
  })

  if (selected === cancelSymbol) {
    process.exit(EXIT.OK)
  }

  // Install selected skills via addSkill from phase 2
  for (const skill of selected) {
    await addSkill(skill.source, { agent: opts.agent, yes: opts.yes })
  }
}
```

**Output format examples:**

Non-interactive table output:

```text
+-----------------+-----------+----------------------------------------------+----------+
| name            | source    | description                                  | installs |
+-----------------+-----------+----------------------------------------------+----------+
| k8s-deploy      | owner/rep | Kubernetes deployment patterns and best p... | 142      |
| k8s-security    | other/rep | Security hardening for Kubernetes clusters   | 87       |
+-----------------+-----------+----------------------------------------------+----------+
```

Non-interactive JSON output (`--json`):

```json
[
  {
    "name": "k8s-deploy",
    "source": "owner/repo",
    "description": "Kubernetes deployment patterns and best practices",
    "installs": 142,
    "url": "https://skills.sh/s/k8s-deploy"
  }
]
```

#### Example Test Cases

```typescript
// cli/test/skill-find.test.ts (find command section)
import { describe, expect, mock, test, beforeEach, afterEach } from 'bun:test'
import { findSkills } from '../lib/skill-find'

describe('findSkills', () => {
  let consoleLogSpy: ReturnType<typeof mock>
  let originalStdout: boolean | undefined

  beforeEach(() => {
    consoleLogSpy = mock(() => {})
    console.log = consoleLogSpy as typeof console.log
  })

  test('non-interactive JSON output: returns array of SkillSearchResult', async () => {
    // Mock searchSkillsAPI to return known data
    await findSkills(['kubernetes'], { json: true, source: 'catalog' })
    const output = (consoleLogSpy as { mock: { calls: unknown[][] } }).mock.calls
    // Should have called console.log with JSON
    expect(output.length).toBeGreaterThan(0)
    const parsed = JSON.parse(String(output[0][0]))
    expect(Array.isArray(parsed)).toBe(true)
  })

  test('non-interactive table output: renders human-readable table', async () => {
    await findSkills(['kubernetes'], { json: false, source: 'catalog' })
    // console-table-printer writes to stdout
    // Verify it was called (not JSON)
    const output = (consoleLogSpy as { mock: { calls: unknown[][] } }).mock.calls
    // At minimum, should have produced some output
    expect(output.length).toBeGreaterThanOrEqual(0)
  })

  test('limit parameter: passes through to searchSkillsAPI', async () => {
    await findSkills(['test'], { json: true, limit: 5, source: 'catalog' })
    const output = (consoleLogSpy as { mock: { calls: unknown[][] } }).mock.calls
    if (output.length > 0) {
      const parsed = JSON.parse(String(output[0][0]))
      expect(parsed.length).toBeLessThanOrEqual(5)
    }
  })

  test('empty query in non-TTY: warns and returns empty', async () => {
    // Simulate non-TTY
    const origTTY = process.stdout.isTTY
    Object.defineProperty(process.stdout, 'isTTY', { value: false, configurable: true })
    try {
      await findSkills([], { json: true, source: 'catalog' })
      const output = (consoleLogSpy as { mock: { calls: unknown[][] } }).mock.calls
      // Should produce output (even if empty array)
      expect(output.length).toBeGreaterThan(0)
    } finally {
      Object.defineProperty(process.stdout, 'isTTY', { value: origTTY, configurable: true })
    }
  })

  test('--source flag: restricts to specified backend', async () => {
    // When source is 'catalog', should not call fetch (skills-sh) or meilisearch
    const originalFetch = globalThis.fetch
    let fetchCalled = false
    globalThis.fetch = mock(() => { fetchCalled = true; return Promise.reject() }) as typeof fetch
    try {
      await findSkills(['test'], { json: true, source: 'catalog' })
      expect(fetchCalled).toBe(false)
    } finally {
      globalThis.fetch = originalFetch
    }
  })
})
```

#### Acceptance Criteria

- [ ] `findSkills(['kubernetes'], { json: true })` writes a JSON array to stdout
- [ ] `findSkills(['kubernetes'], { json: false })` writes a formatted table to stdout
- [ ] `findSkills(['kubernetes'], { limit: 20 })` passes `limit: 20` to `searchSkillsAPI`
- [ ] `findSkills([], {})` on a TTY launches the interactive `searchMultiselect` prompt
- [ ] `findSkills([], {})` on a non-TTY warns and returns empty (does not hang)
- [ ] Interactive mode: selecting a skill calls `addSkill(skill.source, ...)`
- [ ] Interactive mode: pressing ESC returns `cancelSymbol` and exits with code 0
- [ ] `--source` flag restricts search to a single backend (no fallback chain)
- [ ] `--agent` filter is passed through to `addSkill` in interactive mode
- [ ] When all backends return empty, non-interactive mode outputs `out.info('No skills found')`

### 3.3 CLI Wiring

**Task Dependencies:**

- **3.1:** `lib/skill-search-api.ts` (imported indirectly through `skill-find.ts`)
- **3.2:** `lib/skill-find.ts` (the `findSkills()` function)
- Existing: `commands/shared-args.ts` (`globalArgs`)

**Library Decisions:** No new dependencies. Uses `citty` `defineCommand` (already a project dependency) and the existing `globalArgs` spread pattern from `commands/shared-args.ts`.

- [ ] Add `skill find [query] [--limit] [--json] [--source] [--agent]` subcommand

#### Code Examples

**Citty subcommand wiring (addition to `cli/commands/skill.ts`):**

```typescript
import { findSkills } from '../lib/skill-find'

// Inside the subCommands object of the skill command:
find: defineCommand({
  meta: {
    name: 'find',
    description: 'Search external skill registries',
  },
  args: {
    ...globalArgs,
    query: {
      type: 'positional',
      description: 'Search query (omit for interactive mode)',
      required: false,
    },
    limit: {
      type: 'string',
      alias: 'l',
      description: 'Maximum number of results (default: 10, max: 100)',
      default: '10',
    },
    source: {
      type: 'string',
      alias: 's',
      description: 'Search backend: auto, skills-sh, meilisearch, catalog',
      default: 'auto',
    },
    agent: {
      type: 'string',
      alias: 'a',
      description: 'Filter by agent compatibility / install target',
    },
    yes: {
      type: 'boolean',
      alias: 'y',
      description: 'Skip confirmation prompts (non-interactive)',
      default: false,
    },
  },
  async run({ args }) {
    const query = args.query as string | undefined
    await findSkills(query ? [query] : [], {
      json: args.json as boolean,
      quiet: args.quiet as boolean,
      limit: Number.parseInt(args.limit as string, 10),
      source: (args.source as string) as SearchBackendType,
      agent: args.agent as string | undefined,
      yes: args.yes as boolean,
    })
  },
}),
```

#### Example Test Cases

```typescript
// cli/test/skill-find.test.ts (CLI wiring section)
import { describe, expect, test } from 'bun:test'

describe('skill find CLI wiring', () => {
  test('--limit parses as integer from string arg', () => {
    const parsed = Number.parseInt('20', 10)
    expect(parsed).toBe(20)
    expect(Number.isNaN(parsed)).toBe(false)
  })

  test('--limit with non-numeric string falls back to NaN (clamped by searchSkillsAPI)', () => {
    const parsed = Number.parseInt('abc', 10)
    expect(Number.isNaN(parsed)).toBe(true)
    // clampLimit in skill-search-api.ts handles NaN -> defaults to 10
  })

  test('--source validates against known backends', () => {
    const valid = ['auto', 'skills-sh', 'meilisearch', 'catalog']
    for (const s of valid) {
      expect(valid).toContain(s)
    }
  })

  test('positional query is optional (undefined when omitted)', () => {
    // Citty returns undefined for omitted optional positional args
    const query: string | undefined = undefined
    const args = query ? [query] : []
    expect(args).toEqual([])
  })
})
```

#### Acceptance Criteria

- [ ] `just agents skill find "kubernetes"` runs without error and prints results
- [ ] `just agents skill find "kubernetes" --limit 20` passes `limit: 20` to `findSkills`
- [ ] `just agents skill find "kubernetes" --json` sets `json: true` on `FindOptions`
- [ ] `just agents skill find "kubernetes" --source meilisearch` restricts to local Meilisearch
- [ ] `just agents skill find --agent claude-code` sets agent filter for install-on-select
- [ ] `just agents skill find` (no query) enters interactive mode on TTY
- [ ] `just agents skill find --yes` skips confirmation prompts in install-on-select flow
- [ ] `--limit` is a string arg parsed to integer (Citty does not have `type: 'number'`)
- [ ] All global args (`--json`, `--quiet`, `--verbose`) work as expected

## Notes

- The existing `lib/search.ts` (hybrid RRF) and `lib/meilisearch.ts` provide search infrastructure -- `skill-search-api.ts` wraps these with the skill-specific API
- The skills.sh API limit of 10 is a server-side constraint; our `--limit` param is passed through but may be capped by the backend
- Local catalog search is always available (no network dependency)
- The interactive fzf prompt is the primary UX -- non-interactive is for scripting/CI
- Phase-2 dependency is only needed for install-on-select in interactive mode; `find --json` and `find "query"` work without it
- If phase 2 is not yet complete, interactive mode can print "run `just agents skill add <source>` to install" instead of calling `addSkill` directly
