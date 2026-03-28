# Phase 1: Resolve Duplicate Test Files

## Status: PLANNED

## Goal

Eliminate the 5 test files that exist in both CLI and SDK packages. After this phase,
each test file exists in exactly one package, ready for Phase 2-4 moves.

## Non-Goals

- Moving any files to new packages (that is Phases 2-4)
- Changing any import paths
- Creating new test utilities

## Prerequisites

- Worktree on `plan/test-migration` branch
- `bun install` completed
- Baseline test counts recorded (see PLAN.md)

## Duplicate Pairs

### 1. `manager.test.ts` -- CLI wins

| | Location | Lines | Tests |
|-|----------|-------|-------|
| CLI | `packages/cli/test/component/manager.test.ts` | 535 | More comprehensive |
| SDK | `packages/sdk/test/providers/manager.test.ts` | 278 | Subset of CLI |

**Action**:

1. Diff the two files to identify any unique tests in SDK version
2. If SDK has unique test cases, port them into CLI version
3. Delete `packages/sdk/test/providers/manager.test.ts`
4. Run `bun test packages/sdk/` -- verify pass count drops by SDK-only tests moved
5. Run `bun test packages/cli/` -- verify pass count stable or increased

### 2. `pagination.test.ts` -- SDK wins

| | Location | Lines | Tests |
|-|----------|-------|-------|
| CLI | `packages/cli/test/component/pagination.test.ts` | 74 | Basic |
| SDK | `packages/sdk/test/providers/pagination.test.ts` | 110 | Better coverage |

**Action**:

1. Diff the two files to identify any unique tests in CLI version
2. If CLI has unique test cases, port them into SDK version
3. Delete `packages/cli/test/component/pagination.test.ts`
4. Run `bun test packages/cli/` -- verify pass count drops by CLI-only tests removed
5. Run `bun test packages/sdk/` -- verify pass count stable or increased

### 3. `types.test.ts` -- CLI wins (massive)

| | Location | Lines | Tests |
|-|----------|-------|-------|
| CLI | `packages/cli/test/component/types.test.ts` | 829 | Comprehensive |
| SDK | `packages/sdk/test/context/types.test.ts` | 108 | Small subset |

**Action**:

1. Diff to find unique SDK test cases
2. Merge any unique tests from SDK into CLI version
3. Delete `packages/sdk/test/context/types.test.ts`
4. Verify both suites

### 4. `registry.test.ts` -- CLI wins (much larger)

| | Location | Lines | Tests |
|-|----------|-------|-------|
| CLI | `packages/cli/test/registry.test.ts` | 693 | Comprehensive |
| SDK | `packages/sdk/test/context/registry.test.ts` | 72 | Minimal |

**Action**:

1. Diff to find unique SDK test cases
2. Merge any unique tests from SDK into CLI version
3. Delete `packages/sdk/test/context/registry.test.ts`
4. Verify both suites

### 5. `github.test.ts` -- Keep both (different scope)

| | Location | Lines | Tests |
|-|----------|-------|-------|
| CLI | `packages/cli/test/github.test.ts` | 149 | Tests `@agents/core` git/github utilities |
| SDK | `packages/sdk/test/providers/github.test.ts` | 111 | Tests GitHub provider (API client) |

**Action**: No changes needed. These test different modules:

- CLI's `github.test.ts` will move to Core in Phase 2
- SDK's `github.test.ts` stays in SDK (tests provider layer)

## Import Rewrite Rules

None required in this phase. We are only deleting weaker versions and optionally
merging unique tests into the surviving version.

## mock.module Path Updates

None in this phase.

## Fixture Path Updates

None in this phase.

## Acceptance Criteria

1. No test file name exists in more than one package (except `github.test.ts` which
   tests different code)
2. Total pass count across all packages >= 2075 (no regressions)
3. Any unique tests from deleted files have been ported to the surviving version
4. `bun test packages/sdk/` passes with <= 23 test files (was 23, may drop to 20-21)
5. `bun test packages/cli/` passes with <= 63 test files (was 63, may drop to 62)

## Verification Commands

```bash
# After each deletion
bun test packages/sdk/ 2>&1 | tail -5
bun test packages/cli/ 2>&1 | tail -5

# Final check -- no duplicates
comm -12 \
  <(ls packages/cli/test/**/*.test.ts | xargs -I{} basename {} | sort) \
  <(ls packages/sdk/test/**/*.test.ts | xargs -I{} basename {} | sort)
# Expected: only github.test.ts
```

## Failure Criteria and Fallback

- **If merging unique tests breaks the surviving file**: Revert the merge, keep both
  files temporarily, and flag for manual review in Phase 5
- **If a deleted file turns out to be the only test for some code path**: Restore it
  from git and reassign to the correct package immediately
