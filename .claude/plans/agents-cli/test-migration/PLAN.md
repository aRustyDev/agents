# Test Migration Plan: Move CLI Tests to Proper Packages

## Status: PLANNED

## Problem

The CLI package contains 63 test files (1557 pass, 10 fail, 3 skip) but only ~23 of
those files actually test CLI-specific behavior. The remaining 40 files test SDK, Core,
or KG functionality and were never moved when those packages were extracted. This creates:

- **False ownership**: Tests live in CLI but test SDK/Core/KG code
- **Import indirection**: Tests import via `@agents/sdk/...` from a sibling package
- **Skewed metrics**: CLI appears heavily tested; SDK/Core/KG appear under-tested
- **Maintenance burden**: Failures in CLI tests may actually be SDK regressions

## Current State (baseline)

| Package | Test files | Pass | Fail | Skip |
|---------|-----------|------|------|------|
| Core    | 1         | 10   | 0    | 0    |
| SDK     | 23        | 381  | 0    | 1    |
| KG      | 3         | 127  | 0    | 0    |
| CLI     | 63        | 1557 | 10   | 3    |
| **Total** | **90**  | **2075** | **10** | **4** |

## Target State (after migration)

| Package | Test files | Estimated pass |
|---------|-----------|----------------|
| Core    | 10        | ~19+           |
| SDK     | 51+       | ~1500+         |
| KG      | 5         | ~135+          |
| CLI     | 23        | ~400           |
| **Total** | **89+** | **2075+**      |

Note: One file deleted (`graph-spike.test.ts`), so 90 - 1 = 89, plus any new
test-utils files created in SDK.

## Classification Summary

| Destination | Count | Files |
|------------|-------|-------|
| Move to SDK | 28 (+3 duplicates resolved toward SDK) | catalog-*, skill-*, external-skills-*, manifest, lockfile, schemas, search, output, init-component, registry |
| Move to Core | 9 | git, github, github-token, hash, uuid, symlink, source-parser, types, file-io |
| Move to KG | 2 | degradation, kg-commands |
| Keep in CLI | 23 | agents, prompts, commands/*, component/factory, component/skill-ops-impl, lib/config, mcp, plugin-*, skill-cli-wiring, skill-integration |
| Delete | 1 | graph-spike.test.ts (exploratory spike, no maintained code) |

## Duplicate Resolution Strategy

Five test files exist in BOTH CLI and SDK. These must be resolved before any moves:

| Test | CLI (lines) | SDK (lines) | Resolution |
|------|------------|------------|------------|
| `manager.test.ts` | 535 | 278 | Keep CLI version (more comprehensive), delete SDK `providers/manager.test.ts` |
| `pagination.test.ts` | 74 | 110 | Keep SDK version (better coverage), delete CLI `component/pagination.test.ts` |
| `types.test.ts` | 829 | 108 | Keep CLI version (massive), merge unique SDK tests, delete SDK `context/types.test.ts` |
| `registry.test.ts` | 693 | 72 | Keep CLI version (much larger), delete SDK `context/registry.test.ts` |
| `github.test.ts` | 149 | 111 | Different scope -- CLI tests `@agents/core/git`, SDK tests GitHub provider. Keep both, move CLI version to Core |

## Complication Handling

### 1. `mock.module()` paths (3 files)

Files using `mock.module()`:

- `skill-outdated.test.ts` -- mocks `@agents/core/git`
- `skill-update.test.ts` -- mocks `@agents/sdk/providers/local/skill/outdated` and `@agents/sdk/providers/local/skill/add`
- `external-skills-refactor.test.ts` -- mocks `@agents/core/git`

These already use package-absolute paths (`@agents/core/...`, `@agents/sdk/...`),
so they will work identically after moving to SDK. No path changes needed in the
mock.module calls themselves.

### 2. `createCliAgentResolver` dependency (6 files)

Files importing `createCliAgentResolver` from `../src/lib/agents`:

- `skill-filters.test.ts`
- `skill-info.test.ts`
- `skill-integration.test.ts` (stays in CLI)
- `skill-remove.test.ts`
- `skill-add.test.ts`
- `skill-list.test.ts`

**Strategy**: Create a `packages/sdk/test/_utils/mock-resolver.ts` that provides a
test-only AgentResolver implementation. This breaks the cross-package test dependency.
The mock resolver returns the same default agent paths that `createCliAgentResolver()`
returns but without importing from CLI.

### 3. `content/` fixture paths (7+ files)

Files that read real `content/skills/`, `content/plugins/` fixtures:

- `manifest.test.ts` -- uses `WORKTREE = resolve(import.meta.dir, '../../..')`
- `schemas.test.ts` -- uses `REPO_ROOT = resolve(import.meta.dir, '../../..')`
- `lockfile.test.ts` -- uses `REPO_ROOT = resolve(import.meta.dir, '../../..')`
- `skill-commands.test.ts` -- uses `WORKTREE = resolve(import.meta.dir, '../../..')`
- `skill-discovery.test.ts` -- uses `WORKTREE = resolve(import.meta.dir, '../../..')`
- `kg-commands.test.ts` -- imports `PROJECT_ROOT` from module

**Strategy**: After moving from `packages/cli/test/` to `packages/sdk/test/` (or
`packages/core/test/`), the depth changes from `../../..` (3 up) to `../../../..`
(4 up). Update each file's root resolution.

**Better**: Create a shared `packages/sdk/test/_utils/paths.ts` helper:

```ts
import { resolve } from 'path'
export const PROJECT_ROOT = resolve(import.meta.dir, '../../../..')
export const CONTENT_DIR = resolve(PROJECT_ROOT, 'content')
```

### 4. `WORKTREE`/`PROJECT_ROOT` constants

Several tests compute project root via `resolve(import.meta.dir, '../../..')`.
After moving one package level deeper, the depth changes. Each file must be audited.

## Phase Summary

| Phase | Description | Files | Dependencies |
|-------|------------|-------|-------------|
| 1 | Resolve duplicates | 5 pairs | None |
| 2 | Move Core tests | 9 files | Phase 1 |
| 3 | Move SDK tests | 28 files | Phase 1 |
| 4 | Move KG tests | 2 files | Phase 1 |
| 5 | Cleanup and verify | 1 delete + full suite | Phases 2-4 |

Phases 2, 3, and 4 are independent of each other (can be done in any order after
Phase 1). Phase 5 must be last.

## Global Acceptance Criteria

1. **Zero test regressions**: Total pass count >= 2075 (current total)
2. **No cross-package test imports**: No test in SDK imports from `@agents/cli/*`
3. **All 4 suites pass independently**: `bun test packages/<pkg>` works for each
4. **File counts match target**: CLI has ~23 test files, SDK has ~51+, Core has ~10, KG has ~5
5. **No orphaned imports**: Every test file's imports resolve correctly
6. **Duplicates eliminated**: No test file exists in two packages simultaneously

## Risk Mitigation

- **Run tests after every file move** -- catch import failures immediately
- **Move in small batches** -- 3-5 files per sub-phase, verify green before continuing
- **Keep git history** -- use `git mv` so blame/log survives
- **Fallback**: If a file fails after move, temporarily revert that single file and continue with others
