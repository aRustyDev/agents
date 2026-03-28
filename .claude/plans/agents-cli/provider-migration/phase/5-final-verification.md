# Phase 5: Final Verification

## Goal

Audit the entire migration to confirm no stale imports, no test regressions, and CLI commands work end-to-end.

## Non-goals

- Do NOT make code changes (this is verification only)
- Do NOT add new features or tests
- Do NOT optimize or refactor anything discovered during audit

## Prerequisites

- Phase 4 complete: all CLI provider files deleted, barrel updated
- All tests passing: CLI 1929+/11 fail (or fewer), SDK 132+/0, Core 10/0

## Files

No files are created, moved, or modified in this phase. This is purely an audit and verification phase.

## Steps

### Audit: No stale imports

- [ ] **5.1** Verify no CLI file imports from deleted paths:

```bash
grep -rn \
  'provider-local\|provider-agent\|provider-command\|provider-output-style\|provider-plugin\|provider-rule\|provider-smithery\|smithery-auth\|smithery-publish' \
  packages/cli/src/ packages/cli/test/
```

**Expected:** Zero results. If any results appear, record them and fix before continuing.

- [ ] **5.2** Verify no SDK test imports from CLI paths:

```bash
grep -rn 'packages/cli\|from.*@agents/cli' packages/sdk/test/
```

**Expected:** Zero results.

### Audit: Test suites

- [ ] **5.3** Run all three package test suites:

```bash
bun test --cwd packages/core
bun test --cwd packages/sdk
bun test --cwd packages/cli
```

**Expected results:**

| Package | Pass | Fail | Notes |
|---------|------|------|-------|
| Core | 10+ | 0 | Unchanged from baseline |
| SDK | 132+ | 0 | Plus migrated tests |
| CLI | 1929+ | 11 or fewer | Minus moved tests, no new failures |

- [ ] **5.4** Count SDK test increase to confirm all tests migrated:

```bash
bun test --cwd packages/sdk 2>&1 | tail -5
```

The pass count should be notably higher than the 132 baseline due to migrated provider tests.

### Audit: CLI commands work end-to-end

- [ ] **5.5** Verify CLI commands that use `createComponentManager()`:

```bash
bun run packages/cli/src/bin/agents.ts search skill test
bun run packages/cli/src/bin/agents.ts list skill
bun run packages/cli/src/bin/agents.ts doctor
```

Each command should execute without import errors or crashes. The results may vary (e.g., "no skills found" is fine if no skills are installed).

### Audit: File count

- [ ] **5.6** Verify CLI component directory final state:

```bash
ls -1 packages/cli/src/lib/component/
```

**Expected exactly 3 files:**

```
factory.ts
index.ts
skill-ops-impl.ts
```

- [ ] **5.7** Count SDK provider files:

```bash
find packages/sdk/src/providers/ -name '*.ts' | wc -l
```

**Expected:** approximately 20 files (existing providers + no change from migration, since we only moved tests, not source).

### Audit: Provider registration

- [ ] **5.8** Verify SDK factory registers 8 providers:

```bash
# Quick structural check
grep -c 'manager.register' packages/sdk/src/providers/factory.ts
```

**Expected:** 8 (or 7 if `LocalSkillProvider` is conditional -- the conditional registration counts as 1).

### Commit

- [ ] **5.9** If any fixes were needed (import corrections, missing re-exports), commit them:

```
chore: final fixups for CLI->SDK provider migration
```

- [ ] **5.10** Final commit (even if no changes -- tag the verification):

```
chore: verify CLI->SDK provider migration complete
```

## Acceptance Criteria

1. Zero grep hits for deleted provider file names in CLI source/test
2. Zero grep hits for CLI imports in SDK tests
3. Core: 10+ pass / 0 fail
4. SDK: 132+ pass / 0 fail (higher count expected from migrated tests)
5. CLI: baseline maintained (no new failures beyond pre-existing 11)
6. `agents.ts search skill test` runs without error
7. `agents.ts list skill` runs without error
8. `agents.ts doctor` runs without error
9. CLI `component/` has exactly 3 files
10. All changes committed to git

## Failure Criteria

- If any test suite has new failures not present in the pre-migration baseline, the migration introduced a regression. Identify the failing test and trace it back to the phase that caused it.
- If a CLI command crashes with a module-not-found error, a stale import path was missed. Fix it and re-run.
- If the provider count is wrong (not 8), a provider registration was lost during the factory rewrite. Fix in `packages/sdk/src/providers/factory.ts`.

## Fallback Logic

- If verification reveals a broken test: identify which phase introduced the break, revert to that phase's commit, and fix forward.
- If a CLI command fails at runtime: check `createComponentManager()` return value, verify all 8 providers are registered, check that the `SkillOperations` adapter resolves its dynamic imports correctly.
- If the import audit finds stale references: fix them in-place, run tests, commit as a fixup.

## Examples

### Successful verification output

```
$ bun test --cwd packages/core
  10 pass, 0 fail

$ bun test --cwd packages/sdk
  195 pass, 0 fail

$ bun test --cwd packages/cli
  1870 pass, 11 fail
  (59 tests moved to SDK, net total unchanged)

$ ls packages/cli/src/lib/component/
  factory.ts  index.ts  skill-ops-impl.ts

$ bun run packages/cli/src/bin/agents.ts list skill
  No skills installed.
```

### Failed verification -- stale import

```
$ grep -rn 'provider-smithery' packages/cli/src/
  packages/cli/src/commands/publish.ts:3:import { SmitheryProvider } from '../lib/component/provider-smithery'
```

**Fix:** Update `publish.ts` to import from SDK: `import { SmitheryProvider } from '@agents/sdk/providers/smithery'`

## Notes

- This phase is intentionally conservative -- it makes no code changes, only audits. Any fixes discovered should be minimal and targeted.
- The CLI test count will decrease because tests were moved to SDK. This is expected. The key metric is "no new failures" -- the failing 11 should be the same 11 that failed at baseline.
- If everything passes cleanly, this phase should take under 5 minutes.
