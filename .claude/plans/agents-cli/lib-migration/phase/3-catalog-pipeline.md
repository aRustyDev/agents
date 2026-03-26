# Phase 3: Catalog Pipeline to SDK

## Goal

Move the 7 catalog-related modules into `sdk/src/catalog/pipeline/`, dissolving the monolithic `catalog.ts` (1520 lines) into the SDK's existing catalog type system rather than copying it wholesale.

## Non-Goals

- Changing catalog data formats (NDJSON, .TODO.yaml).
- Adding new pipeline stages.
- Changing the registry crawl logic behavior.
- Moving the `commands/catalog.ts` CLI command file (it stays as a thin CLI layer).

## Prerequisites

- **Phase 2 complete:** `manifest.ts` and `lockfile.ts` are in SDK. The catalog-download module imports `readSkillFrontmatter` from manifest -- it must resolve via `@agents/sdk/context/manifest`.
- **Phase 1 complete (soft):** `chunker.ts` is in `@agents/kg`. If catalog modules need frontmatter parsing they should use `@agents/sdk/context/frontmatter`.

## Files

### Move/Dissolve

| Source (cli/src/lib/) | Destination (sdk/src/) | Lines | Strategy |
|----------------------|------------------------|-------|----------|
| `catalog.ts` (1520) | Dissolve into multiple SDK files | 1520 | Split -- see below |
| `catalog-discover.ts` (370) | `catalog/pipeline/discover.ts` | 370 | Move |
| `catalog-download.ts` (640) | `catalog/pipeline/download.ts` | 640 | Move |
| `catalog-manifest.ts` (182) | `catalog/pipeline/manifest.ts` | 182 | Move |
| `catalog-reconcile.ts` (410) | `catalog/pipeline/reconcile.ts` | 410 | Move |
| `catalog-stale.ts` (98) | `catalog/pipeline/stale.ts` | 98 | Move |
| `registry.ts` (1152) | `catalog/pipeline/crawl.ts` | 1152 | Move |

### Dissolving catalog.ts (1520 lines)

The monolithic `catalog.ts` contains several distinct concerns that map to existing or new SDK locations:

| Concern | Lines (approx) | Target |
|---------|----------------|--------|
| Types (`CatalogEntry`, `AvailabilityStatus`, etc.) | ~120 | Already in `sdk/src/catalog/types.ts` -- merge/reconcile |
| Repo manifest types (`SectionMapEntry`, `RepoManifest`) | ~80 | `sdk/src/catalog/pipeline/types.ts` (new) |
| Tier1 error types and extensions | ~60 | `sdk/src/catalog/pipeline/types.ts` (new) |
| NDJSON I/O helpers (`readCatalogNdjson`, `writeCatalogNdjson`) | ~120 | Already in `sdk/src/catalog/ndjson/io.ts` -- verify overlap |
| Availability check functions (`checkRepoAvailability`, `checkBatch`) | ~250 | `sdk/src/catalog/availability.ts` (new) |
| Progress/logging helpers | ~80 | `sdk/src/catalog/pipeline/progress.ts` (new) or inline |
| Computation functions (`computeTier1`, stats helpers) | ~200 | `sdk/src/catalog/pipeline/compute.ts` (new) |
| CLI entry point / orchestrator (`main()`) | ~300 | Stays in `packages/cli/src/commands/catalog.ts` |
| Config constants (concurrency, delay, paths) | ~50 | `sdk/src/catalog/pipeline/config.ts` (new) |
| Resume/checkpoint logic | ~120 | `sdk/src/catalog/pipeline/checkpoint.ts` (new) |
| Write stream helpers | ~140 | Merge into `sdk/src/catalog/ndjson/io.ts` |

### Create (new SDK files)

| File | Description |
|------|-------------|
| `sdk/src/catalog/pipeline/index.ts` | Barrel for pipeline modules |
| `sdk/src/catalog/pipeline/types.ts` | Tier1 types, repo manifest types, section map |
| `sdk/src/catalog/pipeline/discover.ts` | Skill discovery in repos |
| `sdk/src/catalog/pipeline/download.ts` | Skill download + extraction |
| `sdk/src/catalog/pipeline/manifest.ts` | Per-repo manifest generation |
| `sdk/src/catalog/pipeline/reconcile.ts` | Catalog reconciliation logic |
| `sdk/src/catalog/pipeline/stale.ts` | Staleness detection |
| `sdk/src/catalog/pipeline/crawl.ts` | Registry crawl (from registry.ts) |
| `sdk/src/catalog/pipeline/compute.ts` | Tier1 computation functions |
| `sdk/src/catalog/pipeline/checkpoint.ts` | Resume/checkpoint logic |
| `sdk/src/catalog/availability.ts` | HTTP availability checks |

### Modify

| File | Change |
|------|--------|
| `sdk/src/catalog/types.ts` | Merge CLI's `CatalogEntry` fields that don't exist yet |
| `sdk/src/catalog/ndjson/io.ts` | Add write-stream helpers from catalog.ts if not already present |
| `sdk/src/catalog/index.ts` | Re-export pipeline submodule |
| `sdk/package.json` | May need to add exports for `./catalog/pipeline/*`, `./catalog/availability` |
| `cli/src/commands/catalog.ts` | Update all imports from `'../lib/catalog*'` to `'@agents/sdk/catalog/pipeline/*'` |
| `cli/src/commands/registry.ts` | Update import from `'../lib/registry'` to `'@agents/sdk/catalog/pipeline/crawl'` |

### Delete

| File | Lines |
|------|-------|
| `packages/cli/src/lib/catalog.ts` | 1520 |
| `packages/cli/src/lib/catalog-discover.ts` | 370 |
| `packages/cli/src/lib/catalog-download.ts` | 640 |
| `packages/cli/src/lib/catalog-manifest.ts` | 182 |
| `packages/cli/src/lib/catalog-reconcile.ts` | 410 |
| `packages/cli/src/lib/catalog-stale.ts` | 98 |
| `packages/cli/src/lib/registry.ts` | 1152 |

## Steps

### Stage A: Type Reconciliation

- [ ] **3.1** Audit type overlap between `cli/src/lib/catalog.ts` types and `sdk/src/catalog/types.ts`. Document which types exist in both, which are CLI-only, and which are SDK-only.
- [ ] **3.2** Create `sdk/src/catalog/pipeline/types.ts` for pipeline-specific types that don't belong in the general catalog type file:
  - `CatalogEntryWithTier1` (extends CatalogEntry with tier1 fields)
  - `Tier1ErrorType`, `Tier1Result`
  - `SectionMapEntry`, `RepoManifest`
  - `DiscoveredSkillResult`, `RepoDiscoveryResult`
- [ ] **3.3** Merge any missing fields from CLI's `CatalogEntry` into SDK's `CatalogEntry`. The SDK version already has `source`, `name`, `type`, `availability`, `mechanical`, `analysis`. The CLI version has `source`, `skill`, `availability`. Reconcile: the CLI's `skill` field maps to SDK's `name` field.

### Stage B: I/O and Computation

- [ ] **3.4** Audit `sdk/src/catalog/ndjson/io.ts` vs the NDJSON helpers in `catalog.ts`. The SDK already has `parseNdjson`, `serializeNdjson`, `readNdjsonFile`, `writeNdjsonFile`. The CLI has streaming write (`createWriteStream` + line-by-line append). Add stream-write capability to the SDK if not present.
- [ ] **3.5** Create `sdk/src/catalog/availability.ts` with the HTTP availability check functions extracted from `catalog.ts`:
  - `checkRepoAvailability(source: string): Promise<AvailabilityStatus>`
  - `checkBatchAvailability(sources: string[], opts: BatchOpts): Promise<Map<string, AvailabilityStatus>>`
- [ ] **3.6** Create `sdk/src/catalog/pipeline/compute.ts` with tier1 computation:
  - `computeTier1(entry: CatalogEntry, skillDir: string): Promise<Tier1Result>`
- [ ] **3.7** Create `sdk/src/catalog/pipeline/checkpoint.ts` with resume logic:
  - `loadCheckpoint(path: string): Set<string>`
  - `saveCheckpoint(path: string, processed: Set<string>): void`

### Stage C: Pipeline Modules

- [ ] **3.8** Copy `catalog-discover.ts` to `sdk/src/catalog/pipeline/discover.ts`. Update imports:
  - `@agents/core/git` stays.
  - `@agents/core/source-parser` stays.
  - Types from `./catalog` become relative to pipeline/types.
- [ ] **3.9** Copy `catalog-download.ts` to `sdk/src/catalog/pipeline/download.ts`. Update imports:
  - `readSkillFrontmatter` from `../context/manifest` (moved in Phase 2).
  - Types from `./types`.
- [ ] **3.10** Copy `catalog-manifest.ts` to `sdk/src/catalog/pipeline/manifest.ts`. Update type imports.
- [ ] **3.11** Copy `catalog-reconcile.ts` to `sdk/src/catalog/pipeline/reconcile.ts`. Update type imports.
- [ ] **3.12** Copy `catalog-stale.ts` to `sdk/src/catalog/pipeline/stale.ts`. Update imports.
- [ ] **3.13** Copy `registry.ts` to `sdk/src/catalog/pipeline/crawl.ts`. Update imports:
  - `CliError` -> `SdkError`.
  - `@agents/core/runtime` stays (spawnSync).

### Stage D: Wiring

- [ ] **3.14** Create `sdk/src/catalog/pipeline/index.ts` barrel with re-exports.
- [ ] **3.15** Update `sdk/src/catalog/index.ts` to re-export pipeline.
- [ ] **3.16** Update `sdk/package.json` exports map for new paths.
- [ ] **3.17** Update `cli/src/commands/catalog.ts`:

  ```typescript
  // Before
  import { type CatalogEntry, readCatalogNdjson, ... } from '../lib/catalog'
  import { discoverSkills } from '../lib/catalog-discover'
  // After
  import { type CatalogEntry } from '@agents/sdk/catalog/types'
  import { readCatalogNdjson } from '@agents/sdk/catalog/ndjson/io'
  import { discoverSkills } from '@agents/sdk/catalog/pipeline/discover'
  ```

- [ ] **3.18** Update `cli/src/commands/registry.ts`:

  ```typescript
  // Before
  import { crawlRegistry } from '../lib/registry'
  // After
  import { crawlRegistry } from '@agents/sdk/catalog/pipeline/crawl'
  ```

- [ ] **3.19** Check for any other CLI files importing from the 7 moved modules. Update them.

### Stage E: Verify and Clean

- [ ] **3.20** Run `bun test --cwd packages/sdk` -- all tests pass.
- [ ] **3.21** Run `bun test --cwd packages/cli` -- 1684/10 maintained.
- [ ] **3.22** Delete the 7 source files from `cli/src/lib/`.
- [ ] **3.23** Run test suite again after deletion.
- [ ] **3.24** Verify `bun run packages/cli/src/bin/agents.ts catalog --help` works.

## Acceptance Criteria

1. `sdk/src/catalog/pipeline/` exists with at least 8 files (types, discover, download, manifest, reconcile, stale, crawl, index).
2. `sdk/src/catalog/availability.ts` exists with HTTP check functions.
3. CLI's `catalog.ts` (1520-line monolith) no longer exists -- its contents are distributed.
4. No duplicate type definitions between CLI and SDK for catalog types.
5. SDK tests: 382+ pass / 0 fail.
6. CLI tests: 1684 pass / 10 fail.
7. `cli/src/lib/` no longer contains any `catalog*.ts` or `registry.ts` files.
8. `bun run packages/cli/src/bin/agents.ts catalog discover` still works end-to-end.

## Failure Criteria

- **Stop if:** `catalog-discover.ts` or `catalog-download.ts` depend on `skill-discovery.ts` (Phase 5 module) at import time (not just type imports). Check if it is a runtime dependency. If so, use dynamic import (`await import(...)`) to defer the dependency. The type can be imported from the CLI shim until Phase 5 completes.
- **Stop if:** Dissolving `catalog.ts` breaks more than 20 tests. In that case, move it as a whole file first (`sdk/src/catalog/legacy.ts`) and split in a follow-up.

## Fallback Logic

1. **Monolith move fallback:** If dissolving `catalog.ts` proves too error-prone, copy the entire 1520-line file to `sdk/src/catalog/pipeline/catalog-legacy.ts` and re-export everything. Schedule splitting as a separate task after the full migration.
2. **Circular dependency:** If discover/download create import cycles with SDK modules, break the cycle by extracting shared types into `sdk/src/catalog/pipeline/types.ts` and having both sides import from there.
3. **Registry complexity:** `registry.ts` (1152 lines) is large. If it resists clean extraction, leave it in CLI and mark as "CLI-only orchestration" -- the core crawl logic can be extracted later.

## Examples

### Before (cli/src/lib/catalog.ts, partial)

```typescript
import { createWriteStream, existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { currentDir } from '@agents/core/runtime'

export type AvailabilityStatus = 'available' | 'archived' | 'not_found' | ...
export interface CatalogEntry { source: string; skill: string; availability: AvailabilityStatus }
export interface SectionMapEntry { heading: string; line: number; depth: number }

export async function checkRepoAvailability(source: string): Promise<AvailabilityStatus> { ... }
export function readCatalogNdjson(path: string): CatalogEntry[] { ... }
```

### After (dissolved into SDK)

```typescript
// sdk/src/catalog/types.ts (existing, extended)
export type AvailabilityStatus = 'available' | 'archived' | 'not_found' | ...
export interface CatalogEntry { source: string; name: string; type: ComponentType; ... }

// sdk/src/catalog/pipeline/types.ts (new)
export interface SectionMapEntry { heading: string; line: number; depth: number }
export interface CatalogEntryWithTier1 extends CatalogEntry { ... }

// sdk/src/catalog/availability.ts (new)
export async function checkRepoAvailability(source: string): Promise<AvailabilityStatus> { ... }

// sdk/src/catalog/ndjson/io.ts (existing, extended)
export function readNdjsonFile<T>(path: string): Promise<Result<T[]>> { ... }  // already present
```

### Before (cli/src/commands/catalog.ts)

```typescript
import { type CatalogEntry, checkRepoAvailability } from '../lib/catalog'
import { discoverSkills } from '../lib/catalog-discover'
```

### After (cli/src/commands/catalog.ts)

```typescript
import type { CatalogEntry } from '@agents/sdk/catalog/types'
import { checkRepoAvailability } from '@agents/sdk/catalog/availability'
import { discoverSkills } from '@agents/sdk/catalog/pipeline/discover'
```

## Dependency Notes

- **catalog-discover -> skill-discovery:** `catalog-discover.ts` may import types or functions from `skill-discovery.ts`. Since skill-discovery moves in Phase 5, use a type-only import or dynamic import for now.
- **catalog-download -> manifest:** Already resolved by Phase 2 moving manifest to SDK.
- **catalog-stale -> catalog-download:** `SKILL_LOOKUP_DIRS` constant is imported from catalog-download. Both move to SDK in this phase, so the relative import just needs updating.
- **catalog-reconcile -> catalog + catalog-discover:** Pure type imports from sibling modules. After moving, these become pipeline-relative.
- **registry.ts** is largely self-contained (imports from `@agents/core` only) -- clean extraction.
