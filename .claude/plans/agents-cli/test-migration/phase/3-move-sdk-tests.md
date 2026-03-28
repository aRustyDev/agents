# Phase 3: Move SDK Tests (28 files)

## Status: PLANNED

## Goal

Move 28 test files from `packages/cli/test/` to `packages/sdk/test/` that test SDK
functionality (catalog operations, skill operations, manifests, lockfiles, schemas,
search, external skills, output rendering, component init, registry).

This is the largest phase and is split into 4 sub-phases to manage risk.

## Non-Goals

- Moving Core-bound tests (Phase 2) or KG-bound tests (Phase 4)
- Refactoring the SDK source code
- Changing test behavior -- only file locations and imports change

## Prerequisites

- Phase 1 complete (duplicates resolved -- especially `manager.test.ts`, `types.test.ts`,
  `registry.test.ts`, `pagination.test.ts`)
- SDK currently has ~21 test files (after Phase 1 deletions) with ~381 passing tests

## Sub-Phase 3a: Catalog Tests (10 files)

These are the cleanest to move -- no AgentResolver dependency, no `mock.module()`.

| Source (CLI) | Destination (SDK) |
|-------------|------------------|
| `test/catalog-availability.test.ts` | `test/catalog/availability.test.ts` |
| `test/catalog-backfill.test.ts` | `test/catalog/backfill.test.ts` |
| `test/catalog-discover.test.ts` | `test/catalog/discover.test.ts` |
| `test/catalog-download.test.ts` | `test/catalog/download.test.ts` |
| `test/catalog-integration.test.ts` | `test/catalog/integration.test.ts` |
| `test/catalog-manifest.test.ts` | `test/catalog/manifest.test.ts` |
| `test/catalog-reconcile.test.ts` | `test/catalog/reconcile.test.ts` |
| `test/catalog-schema.test.ts` | `test/catalog/schema.test.ts` |
| `test/catalog-stale.test.ts` | `test/catalog/stale.test.ts` |
| `test/catalog-tier1.test.ts` | `test/catalog/tier1.test.ts` |

**Import pattern**: These import from `@agents/sdk/catalog/...` already.

**Fixture note**: `catalog-reconcile.test.ts` references `content/skills/foo` in test
data construction (`makeDiscoveredSkill`), but this is synthetic data, not file reads.

### Procedure (3a)

```bash
mkdir -p packages/sdk/test/catalog/
for f in availability backfill discover download integration manifest reconcile schema stale tier1; do
  git mv packages/cli/test/catalog-${f}.test.ts packages/sdk/test/catalog/${f}.test.ts
done
# Update any relative imports, then:
bun test packages/sdk/test/catalog/
bun test packages/cli/
```

## Sub-Phase 3b: Skill Tests WITHOUT AgentResolver (6 files)

These skill tests do not import `createCliAgentResolver`.

| Source (CLI) | Destination (SDK) |
|-------------|------------------|
| `test/skill-commands.test.ts` | `test/skill/commands.test.ts` |
| `test/skill-discovery.test.ts` | `test/skill/discovery.test.ts` |
| `test/skill-find.test.ts` | `test/skill/find.test.ts` |
| `test/skill-find-cmd.test.ts` | `test/skill/find-cmd.test.ts` |
| `test/skill-init.test.ts` | `test/skill/init.test.ts` |
| `test/skill-outdated.test.ts` | `test/skill/outdated.test.ts` |

**mock.module note**: `skill-outdated.test.ts` uses `mock.module('@agents/core/git', ...)`.
This uses a package-absolute path and will work identically after moving to SDK.

**Fixture note**: `skill-commands.test.ts` and `skill-discovery.test.ts` use:

```ts
const WORKTREE = resolve(import.meta.dir, '../../..')
```

After moving to `packages/sdk/test/skill/`, the depth from project root is 4 levels:

```ts
const WORKTREE = resolve(import.meta.dir, '../../../..')
```

### Procedure (3b)

```bash
mkdir -p packages/sdk/test/skill/
for f in commands discovery find find-cmd init outdated; do
  git mv packages/cli/test/skill-${f}.test.ts packages/sdk/test/skill/${f}.test.ts
done
# Update WORKTREE depth: ../../.. -> ../../../..
# Update any relative ../src/ imports to @agents/sdk/...
bun test packages/sdk/test/skill/
bun test packages/cli/
```

## Sub-Phase 3c: Skill Tests WITH AgentResolver (6 files)

These files import `createCliAgentResolver` from `../src/lib/agents`. Moving them
requires creating a mock resolver in SDK test utilities first.

| Source (CLI) | Destination (SDK) |
|-------------|------------------|
| `test/skill-add.test.ts` | `test/skill/add.test.ts` |
| `test/skill-filters.test.ts` | `test/skill/filters.test.ts` |
| `test/skill-info.test.ts` | `test/skill/info.test.ts` |
| `test/skill-list.test.ts` | `test/skill/list.test.ts` |
| `test/skill-remove.test.ts` | `test/skill/remove.test.ts` |
| `test/skill-update.test.ts` | `test/skill/update.test.ts` |

**mock.module note**: `skill-update.test.ts` uses `mock.module('@agents/sdk/...')` -- this
already uses package-absolute paths and works after the move.

### AgentResolver Mock Creation

**Before moving any Phase 3c files**, create:

```text
packages/sdk/test/_utils/mock-resolver.ts
```

This file provides a test-only `AgentResolver` that returns the same default paths
as `createCliAgentResolver()` but without depending on CLI:

```ts
import type { AgentResolver } from '@agents/sdk'
import { resolve } from 'path'

const PROJECT_ROOT = resolve(import.meta.dir, '../../../..')

export function createTestAgentResolver(): AgentResolver {
  return {
    // Match the same defaults as CLI's createCliAgentResolver()
    resolve(name: string) {
      return resolve(PROJECT_ROOT, 'content', 'agents', name)
    },
    projectRoot: PROJECT_ROOT,
  }
}
```

The exact interface depends on what `AgentResolver` looks like -- inspect
`packages/sdk/src/index.ts` and `packages/cli/src/lib/agents.ts` to determine the
correct shape.

### Import Rewrite Rules (3c)

```ts
// Before (in CLI)
import { createCliAgentResolver } from '../src/lib/agents'
const resolver = createCliAgentResolver()

// After (in SDK)
import { createTestAgentResolver } from '../_utils/mock-resolver'
const resolver = createTestAgentResolver()
```

### Procedure (3c)

```bash
# 1. Create mock resolver
# (write packages/sdk/test/_utils/mock-resolver.ts)

# 2. Move files
for f in add filters info list remove update; do
  git mv packages/cli/test/skill-${f}.test.ts packages/sdk/test/skill/${f}.test.ts
done

# 3. Rewrite createCliAgentResolver -> createTestAgentResolver in each file
# 4. Update WORKTREE/PROJECT_ROOT depth where needed
# 5. Verify
bun test packages/sdk/test/skill/
bun test packages/cli/
```

## Sub-Phase 3d: Remaining SDK Tests (6 files)

| Source (CLI) | Destination (SDK) |
|-------------|------------------|
| `test/external-skills.test.ts` | `test/providers/local/external-skills.test.ts` |
| `test/external-skills-refactor.test.ts` | `test/providers/local/external-skills-refactor.test.ts` |
| `test/manifest.test.ts` | `test/context/manifest.test.ts` |
| `test/lockfile.test.ts` | `test/context/lockfile.test.ts` |
| `test/schemas.test.ts` | `test/context/schemas.test.ts` |
| `test/search.test.ts` | `test/providers/search.test.ts` |

**Plus these files from Phase 1 duplicate resolution** (already in CLI, move now):

| Source (CLI) | Destination (SDK) |
|-------------|------------------|
| `test/component/manager.test.ts` | `test/providers/manager.test.ts` (replaces deleted SDK version) |
| `test/component/types.test.ts` | `test/context/types.test.ts` (replaces deleted SDK version) |
| `test/registry.test.ts` | `test/context/registry.test.ts` (replaces deleted SDK version) |
| `test/output.test.ts` | `test/ui/output.test.ts` |
| `test/lib/init-component.test.ts` | `test/context/init-component.test.ts` |

**mock.module note**: `external-skills-refactor.test.ts` uses
`mock.module('@agents/core/git', ...)` -- package-absolute, works after move.

**Fixture notes**:

- `manifest.test.ts`: Uses `WORKTREE = resolve(import.meta.dir, '../../..')` and reads
  real `content/plugins/` and `content/skills/` files. After move to
  `packages/sdk/test/context/`, depth becomes `../../../..`.
- `schemas.test.ts`: Same pattern -- `REPO_ROOT = resolve(import.meta.dir, '../../..')`.
  After move to `packages/sdk/test/context/`, depth becomes `../../../..`.
- `lockfile.test.ts`: Same pattern. Reads `skills-lock.json` and
  `content/plugins/blog-workflow/...`. Update depth.
- `init-component.test.ts`: Uses `PROJECT_ROOT = resolve(import.meta.dir, '../../../..')`.
  After move from `packages/cli/test/lib/` to `packages/sdk/test/context/`,
  depth changes from `../../../..` to `../../../..` (same -- 4 levels).

### Procedure (3d)

```bash
# Move external-skills
mkdir -p packages/sdk/test/providers/local/
git mv packages/cli/test/external-skills.test.ts packages/sdk/test/providers/local/
git mv packages/cli/test/external-skills-refactor.test.ts packages/sdk/test/providers/local/

# Move manifest/lockfile/schemas
mkdir -p packages/sdk/test/context/
git mv packages/cli/test/manifest.test.ts packages/sdk/test/context/
git mv packages/cli/test/lockfile.test.ts packages/sdk/test/context/
git mv packages/cli/test/schemas.test.ts packages/sdk/test/context/

# Move search
git mv packages/cli/test/search.test.ts packages/sdk/test/providers/

# Move duplicate-resolved files
git mv packages/cli/test/component/manager.test.ts packages/sdk/test/providers/manager.test.ts
git mv packages/cli/test/component/types.test.ts packages/sdk/test/context/types.test.ts
git mv packages/cli/test/registry.test.ts packages/sdk/test/context/registry.test.ts
git mv packages/cli/test/output.test.ts packages/sdk/test/ui/output.test.ts
git mv packages/cli/test/lib/init-component.test.ts packages/sdk/test/context/init-component.test.ts

# Update WORKTREE/REPO_ROOT depth in each file
# Update any relative imports
bun test packages/sdk/
bun test packages/cli/
```

## Acceptance Criteria (Full Phase 3)

1. SDK test suite: ~51+ test files, ~1500+ passing tests
2. CLI test suite: ~23 test files, ~400 passing tests
3. Total pass count unchanged (>= 2075)
4. No test in `packages/sdk/test/` imports from `@agents/cli/*` or uses relative
   paths like `../../cli/`
5. `createCliAgentResolver` appears in zero SDK test files
6. `mock.module()` calls continue to work (they use package-absolute paths)
7. All `content/` fixture reads resolve correctly

## Failure Criteria and Fallback

- **If catalog tests fail after move**: Check for missing SDK catalog pipeline exports.
  The imports use deep paths like `@agents/sdk/catalog/pipeline/io` -- verify
  these are exported from SDK's `package.json` exports map.
- **If AgentResolver mock doesn't match interface**: Inspect the real interface from
  `packages/sdk/src/types.ts` or wherever `AgentResolver` is defined, and update
  the mock accordingly.
- **If `content/` fixture reads fail**: The project root resolution is wrong. Debug
  by logging `import.meta.dir` and the computed root, then adjust depth.
- **If a test has hidden CLI dependencies**: Leave it in CLI temporarily, create an
  issue for extracting the dependency to SDK/Core.
