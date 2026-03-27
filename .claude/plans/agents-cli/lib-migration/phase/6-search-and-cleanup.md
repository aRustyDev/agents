# Phase 6: Search, External Skills & Cleanup

## Goal

Move the 3 remaining modules (`search.ts`, `external-skills.ts`, `plugin-ops.ts`) to SDK, then verify CLI lib/ contains exactly 4 files and all tests pass.

## Non-Goals

- Adding new search backends.
- Changing external skill sync behavior.
- Changing plugin build or validation logic.
- Restructuring CLI commands.
- Publishing packages or changing version numbers.

## Prerequisites

- **All previous phases complete (1-5).** This is the final cleanup phase.
- Specifically:
  - Phase 1: KG package exists (meilisearch is in `@agents/kg`).
  - Phase 2: Manifest/lockfile in SDK.
  - Phase 3: Catalog pipeline in SDK.
  - Phase 4: AgentResolver in SDK.
  - Phase 5: Skill operations in SDK.

## Files

### Move

| Source (cli/src/lib/) | Destination (sdk/src/) | Lines | Notes |
|-----------------------|------------------------|-------|-------|
| `search.ts` (287) | `catalog/search.ts` | 287 | Pure RRF merge logic, zero external deps |
| `external-skills.ts` (706) | `providers/local/external.ts` | 706 | Drift detection, sync, issue filing |
| `plugin-ops.ts` (746) | `context/plugin/ops.ts` | 746 | Plugin class, validate, build, bundle |

### Modify

| File | Change |
|------|--------|
| `sdk/src/catalog/index.ts` | Re-export search module |
| `sdk/src/providers/local/index.ts` | Re-export external module |
| `sdk/src/context/plugin/index.ts` | Re-export ops module |
| `sdk/package.json` | Add exports for new paths |
| `cli/src/commands/search.ts` | Update import from `'../lib/search'` to `'@agents/sdk/catalog/search'` |
| `cli/src/commands/plugin.ts` | Update import from `'../lib/plugin-ops'` to `'@agents/sdk/context/plugin/ops'` |
| `cli/src/commands/component.ts` | Update any external-skills imports |
| `cli/src/lib/component/skill-ops-impl.ts` | Final cleanup -- all imports from SDK |

### Delete

| File | Lines |
|------|-------|
| `packages/cli/src/lib/search.ts` | 287 |
| `packages/cli/src/lib/external-skills.ts` | 706 |
| `packages/cli/src/lib/plugin-ops.ts` | 746 |

### Verify Remaining (should NOT be deleted)

| File | Reason to keep |
|------|----------------|
| `cli/src/lib/agents.ts` (391) | CLI-specific concrete agent registry with filesystem detection |
| `cli/src/lib/component/factory.ts` (23) | CLI DI wiring |
| `cli/src/lib/component/index.ts` (6) | Barrel re-exports |
| `cli/src/lib/component/skill-ops-impl.ts` (27) | DI adapter |

Also remaining but non-TypeScript (not counted):
| `cli/src/lib/chunker.py` | Python KG chunker |
| `cli/src/lib/embedder.py` | Python KG embedder |
| `cli/src/lib/__init__.py` | Python package marker |
| `cli/src/lib/prompts/` | Prompt template directory |

## Steps

### Stage A: Move search.ts

- [ ] **6.1** Copy `search.ts` to `sdk/src/catalog/search.ts`.
- [ ] **6.2** Verify: `search.ts` has ZERO external dependencies -- it is pure TypeScript with no imports at all (no `node:`, no `@agents/core`, nothing). This is the cleanest possible move.
- [ ] **6.3** Update `sdk/src/catalog/index.ts`:

  ```typescript
  export * from './search'
  ```

- [ ] **6.4** Update `cli/src/commands/search.ts`:

  ```typescript
  // Before
  import { hybridSearch, rrfMerge, type HybridSearchOpts } from '../lib/search'
  // After
  import { hybridSearch, rrfMerge, type HybridSearchOpts } from '@agents/sdk/catalog/search'
  ```

- [ ] **6.5** Write SDK tests for `search.ts` (RRF merge, hybrid search with mocks).
- [ ] **6.6** Run tests, confirm pass.

### Stage B: Move external-skills.ts

- [ ] **6.7** Copy `external-skills.ts` to `sdk/src/providers/local/external.ts`.
- [ ] **6.8** Update imports in the SDK copy:

  ```typescript
  // Before
  import { CliError, err, ok, type Result } from '@agents/core/types'
  import {
    type ExternalLockEntry,
    type ExternalSkillEntry,
    ExternalSourcesManifest,
  } from '@agents/sdk/providers/local/schemas'
  // After
  import { err, ok, type Result } from '@agents/core/types'
  import { SdkError } from '../../util/errors'
  import {
    type ExternalLockEntry,
    type ExternalSkillEntry,
    ExternalSourcesManifest,
  } from './schemas'
  ```

  Other `@agents/core` imports (`git`, `github`, `hash`, `runtime`, `symlink`) remain unchanged -- they are cross-package core dependencies.
- [ ] **6.9** Replace all `CliError` with `SdkError` in the copy.
- [ ] **6.10** Update `sdk/src/providers/local/index.ts`:

  ```typescript
  export * from './external'
  ```

- [ ] **6.11** Update CLI consumers. Find all files importing from `'../lib/external-skills'`:
  - `cli/src/commands/component.ts` or `cli/src/commands/skill.ts` (if they reference external skill check/sync)
  - Update to `import { ... } from '@agents/sdk/providers/local/external'`
- [ ] **6.12** Write SDK tests for external-skills (mock git operations, test drift detection logic).
- [ ] **6.13** Run tests, confirm pass.

### Stage C: Move plugin-ops.ts

- [ ] **6.14** Copy `plugin-ops.ts` to `sdk/src/context/plugin/ops.ts`.
- [ ] **6.15** Update imports in the SDK copy:

  ```typescript
  // Before
  import { CliError } from '@agents/core/types'
  import { SkillFrontmatter } from '@agents/sdk/context/skill/schema'
  import type { OutputFormatter } from '@agents/sdk/ui'
  // After
  import { SdkError } from '../../util/errors'
  import { SkillFrontmatter } from '../skill/schema'
  import type { OutputFormatter } from '../../ui'
  ```

  Convert all `@agents/sdk/*` imports to relative SDK-internal paths. Keep `@agents/core/*` imports as-is.
- [ ] **6.16** Replace all `CliError` with `SdkError`.
- [ ] **6.17** Update `sdk/src/context/plugin/index.ts`:

  ```typescript
  export * from './ops'
  ```

- [ ] **6.18** Update CLI consumers:
  - `cli/src/commands/plugin.ts`: Update import to `'@agents/sdk/context/plugin/ops'`
  - `cli/src/commands/lint.ts`: Update if it imports plugin validation
- [ ] **6.19** Write SDK tests for plugin-ops (mock filesystem, test validate and build).
- [ ] **6.20** Run tests, confirm pass.

### Stage D: Final Cleanup and Verification

- [ ] **6.21** Delete the 3 source files from `cli/src/lib/`.
- [ ] **6.22** Run `bun test --cwd packages/core` -- 10 pass / 0 fail.
- [ ] **6.23** Run `bun test --cwd packages/kg` -- all KG tests pass.
- [ ] **6.24** Run `bun test --cwd packages/sdk` -- 382+ pass / 0 fail (likely 450+ with all new tests).
- [ ] **6.25** Run `bun test --cwd packages/cli` -- 1684 pass / 10 fail (unchanged).
- [ ] **6.26** Verify final file inventory in `cli/src/lib/`:

  ```bash
  ls -la packages/cli/src/lib/
  # Expected TypeScript files:
  #   agents.ts
  #   component/factory.ts
  #   component/index.ts
  #   component/skill-ops-impl.ts
  # Expected non-TypeScript (not counted):
  #   __init__.py
  #   chunker.py
  #   embedder.py
  #   prompts/
  ```

- [ ] **6.27** Verify no broken imports across the codebase:

  ```bash
  # Check for any remaining ../lib/ imports that reference deleted files
  grep -r "from '\.\./lib/" packages/cli/src/commands/ | grep -v agents | grep -v component
  # Should return empty
  ```

- [ ] **6.28** Run the full CLI end-to-end smoke test:

  ```bash
  bun run packages/cli/src/bin/agents.ts --help
  bun run packages/cli/src/bin/agents.ts list --type skill --help
  bun run packages/cli/src/bin/agents.ts search --help
  bun run packages/cli/src/bin/agents.ts lint --help
  ```

- [ ] **6.29** Verify no circular dependencies:

  ```bash
  # Core should not import from SDK or KG
  grep -r "@agents/sdk\|@agents/kg" packages/core/src/ || echo "OK: core is clean"
  # SDK should not import from CLI
  grep -r "@arustydev/agents\|packages/cli" packages/sdk/src/ || echo "OK: sdk is clean"
  # KG should not import from CLI or SDK
  grep -r "@arustydev/agents\|@agents/sdk" packages/kg/src/ || echo "OK: kg is clean"
  # SDK should not have a static dependency on KG
  grep -r "@agents/kg" packages/sdk/src/ || echo "OK: sdk has no kg dependency"
  ```

- [ ] **6.30** Update `cli/package.json` -- remove dependencies that were only used by moved modules. Audit:
  - `graphology`, `graphology-layout`, `graphology-layout-forceatlas2` -> moved to `@agents/kg`
  - `ajv`, `ajv-formats` -> moved to `@agents/kg`
  - `ollama` -> moved to `@agents/kg`
  - `meilisearch` -> moved to `@agents/kg`
  - Keep: `@agents/kg` dependency (replaces the individual deps)
  Note: Some deps may still be needed for the graph-viewer server. Audit carefully.
- [ ] **6.31** Run `bun install` after dependency cleanup.
- [ ] **6.32** Final full test run across all packages.

## Acceptance Criteria

1. `cli/src/lib/` contains exactly 4 TypeScript files: `agents.ts`, `component/factory.ts`, `component/index.ts`, `component/skill-ops-impl.ts`.
2. `sdk/src/catalog/search.ts` exists with RRF merge functions.
3. `sdk/src/providers/local/external.ts` exists with external skill management.
4. `sdk/src/context/plugin/ops.ts` exists with plugin operations.
5. No `CliError` usage in any file under `packages/sdk/src/` or `packages/kg/src/`.
6. No circular dependencies between core, sdk, kg, cli packages.
7. Test results:
   - Core: 10 pass / 0 fail
   - KG: 6+ pass / 0 fail
   - SDK: 400+ pass / 0 fail
   - CLI: 1684 pass / 10 fail
8. All CLI commands work end-to-end.
9. `cli/package.json` no longer directly depends on graphology, ajv, ollama, or meilisearch (these are in `@agents/kg`).
10. No `import ... from '../lib/...'` in CLI commands that references deleted files.

## Failure Criteria

- **Stop if:** `external-skills.ts` depends on modules not yet moved. It imports from `@agents/core` and `@agents/sdk/providers/local/schemas` -- both should be fine. If it imports from other `cli/src/lib/` files, those must be resolved first.
- **Stop if:** `plugin-ops.ts` depends on `agents.ts` for agent resolution. Check: it imports `SkillFrontmatter` from SDK schema (fine) and `OutputFormatter` from SDK UI (fine). It should NOT import from agents.ts.
- **Stop if:** Removing graphology/ajv/ollama/meilisearch from CLI package.json breaks the graph-viewer server. The server should import these through `@agents/kg`.

## Fallback Logic

1. If `external-skills.ts` has hidden dependencies on skill-list or skill-info (already in SDK after Phase 5), those resolve naturally. If they depend on something still in CLI, leave external-skills in CLI and reduce the target from 4 files to 5.
2. If `plugin-ops.ts` is too tightly coupled to CLI formatting helpers, extract the pure logic (validate, build) to SDK and leave the CLI-specific formatting in a thin adapter.
3. If dependency cleanup in step 6.30 causes runtime errors, add back the specific dependency that is needed and investigate whether the graph-viewer server needs its own package.json.
4. If final file count is 5 instead of 4 (e.g., `init-component.ts` decided to stay in Phase 2), that is acceptable. Update PLAN.md with the revised target.

## Examples

### search.ts (simplest move -- zero deps)

```typescript
// sdk/src/catalog/search.ts -- identical to cli/src/lib/search.ts
// No imports to change. No error classes to change. Pure TypeScript logic.
export interface RankedResult { ... }
export function rrfMerge(...): MergedResult[] { ... }
export async function hybridSearch(...): Promise<HybridSearchResult> { ... }
```

### external-skills.ts import changes

```typescript
// Before (cli/src/lib/external-skills.ts)
import { CliError, err, ok, type Result } from '@agents/core/types'
import { ExternalSourcesManifest } from '@agents/sdk/providers/local/schemas'

// After (sdk/src/providers/local/external.ts)
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import { ExternalSourcesManifest } from './schemas'
```

### plugin-ops.ts import changes

```typescript
// Before (cli/src/lib/plugin-ops.ts)
import { computeHash, formatHash, parseHash } from '@agents/core/hash'
import { CliError } from '@agents/core/types'
import { SkillFrontmatter } from '@agents/sdk/context/skill/schema'
import type { OutputFormatter } from '@agents/sdk/ui'

// After (sdk/src/context/plugin/ops.ts)
import { computeHash, formatHash, parseHash } from '@agents/core/hash'
import { SdkError } from '../../util/errors'
import { SkillFrontmatter } from '../skill/schema'
import type { OutputFormatter } from '../../ui'
```

### Final directory structure

```text
packages/cli/src/lib/
  __init__.py          # Python
  agents.ts            # CLI-specific agent registry (implements AgentResolver)
  chunker.py           # Python KG chunker
  embedder.py          # Python KG embedder
  prompts/             # Prompt templates
  component/
    factory.ts         # DI wiring
    index.ts           # Barrel
    skill-ops-impl.ts  # SkillOperations adapter
```

**TypeScript files: 4** (agents.ts + 3 in component/).

## Test Files

Move corresponding test files from `packages/cli/test/` to `packages/sdk/test/`:
- `external-skills.test.ts` --> `packages/sdk/test/providers/local/external.test.ts`
- `search.test.ts` --> `packages/sdk/test/catalog/search.test.ts`
- `plugin-ops.test.ts` --> `packages/sdk/test/context/plugin/ops.test.ts`

Update imports in moved tests to use SDK package paths. If tests have CLI-specific fixtures, keep them in CLI and update imports to point to the new SDK package paths.

## Dependency Notes

- `search.ts` has zero dependencies -- safest possible move. Do this first.
- `external-skills.ts` depends heavily on `@agents/core` (git, github, hash, runtime, symlink, types). These are all stable cross-package dependencies. It also depends on `@agents/sdk/providers/local/schemas` for type definitions -- these become relative imports after the move.
- `plugin-ops.ts` depends on `@agents/core/hash`, `@agents/core/runtime`, `@agents/core/types`, `@agents/sdk/context/skill/schema`, and `@agents/sdk/ui`. All become relative imports within SDK.
- After this phase, CLI depends on: `@agents/core`, `@agents/sdk`, `@agents/kg` plus its own direct deps (citty, vite, ws, etc.).
- The dependency DAG is clean: `core` <- `sdk` <- `cli`, `core` <- `kg` <- `cli`. SDK and KG do not depend on each other — unless `skill-search-api.ts` (moved in Phase 5) uses a static import of `@agents/kg/meilisearch`. Per Phase 5's guidance, dynamic import is preferred to avoid this cross-dependency. Verify with: `grep -r "@agents/kg" packages/sdk/src/ || echo "OK: sdk has no kg dependency"`. If a static import exists, convert it to a dynamic import to preserve the DAG.
