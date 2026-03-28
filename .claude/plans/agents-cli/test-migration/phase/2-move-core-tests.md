# Phase 2: Move Core Tests (9 files)

## Status: PLANNED

## Goal

Move 9 test files from `packages/cli/test/` to `packages/core/test/` that test Core
package functionality (git, hashing, uuid, symlinks, types, file-io, source-parser,
github utilities).

## Non-Goals

- Moving SDK-bound or KG-bound tests (Phases 3-4)
- Restructuring Core's `src/` directory
- Adding new Core functionality

## Prerequisites

- Phase 1 complete (duplicates resolved)
- Core currently has 1 test file (`imports.test.ts`) with 10 passing tests

## File Moves

| Source (CLI) | Destination (Core) | Complications |
|-------------|-------------------|---------------|
| `test/git.test.ts` | `test/git.test.ts` | None -- tests pure `@agents/core/git` functions |
| `test/github.test.ts` | `test/github.test.ts` | Has integration test needing GitHub auth -- may timeout in CI |
| `test/github-token.test.ts` | `test/github-token.test.ts` | None -- tests `@agents/core` token resolution |
| `test/hash.test.ts` | `test/hash.test.ts` | None -- tests pure hash functions |
| `test/uuid.test.ts` | `test/uuid.test.ts` | None -- tests pure uuid generation |
| `test/symlink.test.ts` | `test/symlink.test.ts` | None -- tests symlink utilities |
| `test/source-parser.test.ts` | `test/source-parser.test.ts` | References `content/skills` in URL parsing strings (string literals, not file reads) |
| `test/types.test.ts` | `test/types.test.ts` | Large file (829 lines) -- the one in `test/` root, NOT `component/types.test.ts` |
| `test/lib/file-io.test.ts` | `test/file-io.test.ts` | Flatten out of `lib/` subdirectory |

## Import Rewrite Rules

Most of these files import from `@agents/core/...` already (since they test Core
code). The main change is the relative import path for any local test helpers.

### Pattern 1: Direct `@agents/core` imports (no change needed)

```ts
// These already use package imports -- work identically after move
import { gitLog } from '@agents/core/git'
import { hashContent } from '@agents/core/hash'
```

### Pattern 2: Relative imports from `../src/...`

Some files may import directly from CLI's `src/` via relative paths. These need to
change to `@agents/core/...` package imports.

```ts
// Before (in CLI)
import { parseSource } from '../src/lib/source-parser'

// After (in Core)
import { parseSource } from '@agents/core/source-parser'
```

Audit each file for relative imports and convert to package imports.

### Pattern 3: `WORKTREE`/`REPO_ROOT` resolution depth

Files currently compute project root as:

```ts
// In packages/cli/test/ (3 levels up)
const PROJECT_ROOT = resolve(import.meta.dir, '../../..')
```

After moving to `packages/core/test/`:

```ts
// In packages/core/test/ (3 levels up -- same depth!)
const PROJECT_ROOT = resolve(import.meta.dir, '../../..')
```

Both `packages/cli/test/` and `packages/core/test/` are at the same depth relative to
project root, so **no depth change needed** for these files.

## mock.module Path Updates

None of the 9 Core-bound files use `mock.module()`.

## Fixture Path Updates

- `source-parser.test.ts`: Contains string literals like `'content/skills'` in URL
  tests. These are test data strings, not file system reads. No change needed.
- `types.test.ts`: Verify it does not read from `content/`. If it does, update paths.

## Procedure

For each file:

```bash
# 1. Move the file
git mv packages/cli/test/<file>.test.ts packages/core/test/<file>.test.ts

# 2. Update imports (if any relative imports exist)
# Change ../src/lib/<module> -> @agents/core/<module>

# 3. Run Core tests
bun test packages/core/

# 4. Run CLI tests (verify no broken references)
bun test packages/cli/
```

### Recommended batch order

1. **Batch A (pure functions, zero risk)**: `hash.test.ts`, `uuid.test.ts`, `symlink.test.ts`
2. **Batch B (git utilities)**: `git.test.ts`, `github.test.ts`, `github-token.test.ts`
3. **Batch C (parsers and types)**: `source-parser.test.ts`, `types.test.ts`, `file-io.test.ts`

## Acceptance Criteria

1. Core test suite: 10 (existing) + N (moved) tests pass, where N is the number of
   tests in the 9 moved files
2. CLI test suite: Pass count decreases by exactly the number of tests moved
3. Total pass count across all packages unchanged (>= 2075)
4. No relative imports pointing to `@agents/cli` in any Core test file
5. `bun test packages/core/` runs independently with no CLI dependency

## Verification Commands

```bash
# After all moves
bun test packages/core/ 2>&1 | tail -5   # Should show ~19+ pass
bun test packages/cli/ 2>&1 | tail -5    # Should show ~1557 minus moved tests

# Verify no CLI imports in Core tests
grep -r '@agents/cli' packages/core/test/ && echo "FAIL: CLI imports found" || echo "OK"

# Verify no relative imports escaping package
grep -r '\.\./\.\./\.\.' packages/core/test/*.test.ts | grep -v 'import.meta.dir' && echo "WARN: deep relative imports" || echo "OK"
```

## Failure Criteria and Fallback

- **If a file imports CLI-specific utilities** (not available in Core): Leave it in CLI,
  document as "needs CLI adapter extracted to Core first"
- **If `github.test.ts` integration tests fail** due to auth: Mark them as `test.skip`
  in Core, document the auth requirement
- **If `types.test.ts` has SDK dependencies**: Move it to SDK instead of Core (reclassify)
