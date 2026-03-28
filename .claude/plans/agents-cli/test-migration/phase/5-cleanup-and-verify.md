# Phase 5: Cleanup and Final Verification

## Status: PLANNED

## Goal

Delete exploratory test files, verify final file counts and test counts across all
4 packages, and confirm no regressions.

## Non-Goals

- Moving any more files (all moves complete in Phases 2-4)
- Refactoring test code
- Adding new tests

## Prerequisites

- Phases 1-4 complete
- All 4 package test suites pass independently

## Cleanup Tasks

### 1. Delete `graph-spike.test.ts`

```bash
git rm packages/cli/test/graph-spike.test.ts
```

This is an exploratory spike test that does not test any maintained code. It was used
during initial graph/KG prototyping and is no longer relevant.

### 2. Remove empty `component/` subdirectory in CLI (if empty)

After moving `manager.test.ts`, `pagination.test.ts` (deleted), `types.test.ts`, and
`skill-ops-impl.test.ts` stays:

```bash
# Check what remains
ls packages/cli/test/component/
# Expected: factory.test.ts, skill-ops-impl.test.ts (these stay in CLI)
```

If the directory still has files, leave it. If empty, remove it.

### 3. Remove empty `lib/` subdirectory in CLI (if empty)

After moving `file-io.test.ts` (to Core) and `init-component.test.ts` (to SDK):

```bash
ls packages/cli/test/lib/
# Expected: config.test.ts (stays in CLI)
```

If `config.test.ts` remains, the directory stays.

### 4. Verify no stale imports

Run a project-wide check for imports that reference moved files:

```bash
# Check for broken relative imports
grep -rn "from '\.\." packages/*/test/**/*.test.ts | grep -v node_modules | grep 'cli/src'
# Should only appear in packages/cli/test/ files

# Check for any test importing from wrong package
grep -rn "@agents/cli" packages/sdk/test/ packages/core/test/ packages/kg/test/
# Should return nothing
```

## Final Verification

### File Count Verification

```bash
echo "=== Test File Counts ==="
echo "Core: $(find packages/core/test -name '*.test.ts' | wc -l) files"
echo "SDK:  $(find packages/sdk/test -name '*.test.ts' | wc -l) files"
echo "KG:   $(find packages/kg/test -name '*.test.ts' | wc -l) files"
echo "CLI:  $(find packages/cli/test -name '*.test.ts' | wc -l) files"
```

**Expected counts**:

| Package | Files | Notes |
|---------|-------|-------|
| Core | 10 | 1 existing + 9 moved |
| SDK | 51+ | ~21 existing (after Phase 1) + ~28 moved + ~3 duplicate winners moved |
| KG | 5 | 3 existing + 2 moved |
| CLI | 22 | 63 original - 40 moved - 1 deleted |

### Test Count Verification

```bash
echo "=== Running All Test Suites ==="
echo "--- Core ---"
bun test packages/core/ 2>&1 | tail -3
echo "--- SDK ---"
bun test packages/sdk/ 2>&1 | tail -3
echo "--- KG ---"
bun test packages/kg/ 2>&1 | tail -3
echo "--- CLI ---"
bun test packages/cli/ 2>&1 | tail -3
```

**Expected ranges**:

| Package | Pass (min) | Pass (max) | Fail (max) |
|---------|-----------|-----------|-----------|
| Core | 19 | 30 | 0 (github integration may skip) |
| SDK | 1400 | 1600 | 0 |
| KG | 130 | 145 | 0 |
| CLI | 350 | 450 | 10 (pre-existing failures) |
| **Total** | **2065** | **2075+** | **10** |

### Cross-Package Import Verification

```bash
# No SDK test should import from CLI
grep -r '@agents/cli' packages/sdk/test/ && echo "FAIL" || echo "PASS: SDK clean"

# No Core test should import from CLI
grep -r '@agents/cli' packages/core/test/ && echo "FAIL" || echo "PASS: Core clean"

# No KG test should import from CLI
grep -r '@agents/cli' packages/kg/test/ && echo "FAIL" || echo "PASS: KG clean"

# No test should have dangling relative imports to moved files
grep -rn "from '\.\./\.\./\.\." packages/*/test/ | grep -v import.meta | grep -v node_modules
# Review any hits -- they may be legitimate (WORKTREE resolution) or broken imports
```

### Duplicate Verification

```bash
# List all test file basenames, find any appearing in multiple packages
for pkg in core sdk kg cli; do
  find packages/$pkg/test -name '*.test.ts' -exec basename {} \;
done | sort | uniq -d
# Expected: github.test.ts only (different scope in Core vs SDK)
```

## Acceptance Criteria

1. **Total pass count >= 2065**: May be slightly lower than 2075 if `graph-spike.test.ts`
   had passing tests, but the delta should equal exactly the tests in that deleted file
2. **File distribution matches target**: Core ~10, SDK ~51, KG ~5, CLI ~22
3. **No cross-package test dependencies**: Zero `@agents/cli` imports in non-CLI tests
4. **No duplicate test files**: Only `github.test.ts` appears in multiple packages
   (Core tests git utilities, SDK tests GitHub provider)
5. **All 4 suites run independently**: Each `bun test packages/<pkg>/` succeeds on its own
6. **Clean git status**: All changes committed, no untracked test files

## Post-Migration Recommendations

1. **Add CI check**: Lint rule preventing `@agents/cli` imports in SDK/Core/KG test files
2. **Update CLAUDE.md**: Document the test distribution convention
3. **Convert to beads**: If follow-up work is needed (e.g., further test refactoring),
   create beads issues for tracking

## Failure Criteria and Fallback

- **If total pass count is significantly lower** (> 20 tests missing): Some tests were
  lost in moves. Use `git log --diff-filter=D -- '*.test.ts'` to find deleted files
  and restore them.
- **If a suite fails entirely**: Likely a misconfigured `bun test` path or missing
  package.json test configuration. Check each package's `package.json` for test scripts
  and Bun configuration for test setup.
- **If duplicates remain**: Re-run Phase 1 resolution for the remaining duplicates.
