# Phase 4: Delete CLI Provider Files

## Goal

Remove all CLI provider source files (`provider-*.ts`, `smithery-*.ts`) that are now replaced by SDK providers, and update the CLI barrel export to re-export from SDK.

## Non-goals

- Do NOT delete skill modules (`skill-list.ts`, `skill-add.ts`, etc.) -- those are still used by the `SkillOperations` adapter
- Do NOT modify SDK provider source files
- Do NOT move any additional test files
- Do NOT change CLI command files -- they import from `factory.ts` or `index.ts`, not from provider files directly

## Prerequisites

- Phase 3 complete: all provider tests migrated to SDK and passing
- CLI factory already rewired to use SDK's `createDefaultProviders()` (Phase 2)
- No file in CLI (other than the old factory, which is already rewritten) imports from provider files

## Files

| Action | Path |
|--------|------|
| Delete | `packages/cli/src/lib/component/provider-local.ts` |
| Delete | `packages/cli/src/lib/component/provider-agent.ts` |
| Delete | `packages/cli/src/lib/component/provider-command.ts` |
| Delete | `packages/cli/src/lib/component/provider-output-style.ts` |
| Delete | `packages/cli/src/lib/component/provider-plugin.ts` |
| Delete | `packages/cli/src/lib/component/provider-rule.ts` |
| Delete | `packages/cli/src/lib/component/provider-smithery.ts` |
| Delete | `packages/cli/src/lib/component/smithery-auth.ts` |
| Delete | `packages/cli/src/lib/component/smithery-publish.ts` |
| Modify | `packages/cli/src/lib/component/index.ts` |

## Steps

- [ ] **4.1** Verify no CLI file imports from the files to be deleted:

```bash
# Run from repo root. Should return ZERO results.
grep -rn \
  'from.*provider-local\|from.*provider-agent\|from.*provider-command\|from.*provider-output-style\|from.*provider-plugin\|from.*provider-rule\|from.*provider-smithery\|from.*smithery-auth\|from.*smithery-publish' \
  packages/cli/src/ packages/cli/test/
```

If any results appear other than `index.ts` barrel re-exports, STOP and fix those imports first.

- [ ] **4.2** Delete all 9 provider files:

```bash
git rm packages/cli/src/lib/component/provider-local.ts
git rm packages/cli/src/lib/component/provider-agent.ts
git rm packages/cli/src/lib/component/provider-command.ts
git rm packages/cli/src/lib/component/provider-output-style.ts
git rm packages/cli/src/lib/component/provider-plugin.ts
git rm packages/cli/src/lib/component/provider-rule.ts
git rm packages/cli/src/lib/component/provider-smithery.ts
git rm packages/cli/src/lib/component/smithery-auth.ts
git rm packages/cli/src/lib/component/smithery-publish.ts
```

- [ ] **4.3** Update `packages/cli/src/lib/component/index.ts` barrel:

```typescript
// Re-export from SDK for any CLI code that imports from this barrel
export { ProviderManager as ComponentManager } from '@agents/sdk/providers/manager'
export * from '@agents/sdk/context/types'
export * from '@agents/sdk/providers/pagination'
```

- [ ] **4.4** Verify the barrel still satisfies all existing consumers:

```bash
# Find all imports from the component barrel
grep -rn "from.*lib/component['\"]" packages/cli/src/ packages/cli/test/
# Each import should resolve to something re-exported above
```

- [ ] **4.5** Run all tests:

```bash
bun test --cwd packages/sdk
bun test --cwd packages/cli
```

- [ ] **4.6** Verify CLI component directory contains exactly 3 files:

```bash
ls packages/cli/src/lib/component/
# Expected: factory.ts  index.ts  skill-ops-impl.ts
```

- [ ] **4.7** Commit: `refactor(cli): remove CLI provider files -- now using SDK providers`

## Acceptance Criteria

1. All 9 provider files deleted from `packages/cli/src/lib/component/`
2. `packages/cli/src/lib/component/` contains exactly: `factory.ts`, `index.ts`, `skill-ops-impl.ts`
3. `packages/cli/src/lib/component/index.ts` re-exports `ComponentManager`, types, and pagination from SDK
4. `bun test --cwd packages/cli` -- zero regressions from post-Phase-3 baseline
5. `bun test --cwd packages/sdk` -- all tests pass (132+ pass / 0 fail)
6. Zero grep hits for deleted file names in CLI source or test directories

## Failure Criteria

- If `bun test --cwd packages/cli` has new failures after deletion, STOP -- a file still imports from a deleted path. Restore with `git checkout` and fix the import first.
- If the barrel `index.ts` update breaks type resolution, STOP -- a consumer depends on a type that was not re-exported. Add the missing re-export.
- If `git rm` fails because a file is already deleted, the file was removed in a previous step -- safe to ignore.

## Fallback Logic

- If a CLI file is discovered importing from a deleted provider (missed in Step 4.1), restore the file with `git checkout HEAD -- <path>`, update the import to use SDK, then re-delete.
- If the barrel `index.ts` needs additional re-exports not covered by the 3 lines above, add them. Common candidates:
  - `export { createComponentManager } from './factory'` (if consumers import from the barrel instead of factory directly)
  - `export type { ComponentProvider } from '@agents/sdk/context/types'` (if consumers need the provider interface)
- If a consumer imports a CLI-specific type that does not exist in SDK (e.g., a CLI-only error code), create a thin re-export shim or update the consumer to use the SDK equivalent.

## Examples

### index.ts -- Before

```typescript
// packages/cli/src/lib/component/index.ts (CURRENT)
// Re-export SDK component model

export * from '@agents/sdk/context/types'
export { ComponentManager } from '@agents/sdk/providers/manager'
export * from '@agents/sdk/providers/pagination'
```

### index.ts -- After

```typescript
// packages/cli/src/lib/component/index.ts (UPDATED)
// Re-export from SDK for any CLI code that imports from this barrel
export { ProviderManager as ComponentManager } from '@agents/sdk/providers/manager'
export * from '@agents/sdk/context/types'
export * from '@agents/sdk/providers/pagination'
```

Note: The barrel is already close to the target state. The key change is confirming it does NOT re-export anything from deleted `provider-*.ts` files. If the current `index.ts` only re-exports from SDK (which it does), no change may be needed -- verify before modifying.

### Directory listing -- Before

```
packages/cli/src/lib/component/
+-- factory.ts
+-- index.ts
+-- provider-agent.ts
+-- provider-command.ts
+-- provider-local.ts
+-- provider-output-style.ts
+-- provider-plugin.ts
+-- provider-rule.ts
+-- provider-smithery.ts
+-- skill-ops-impl.ts        (added in Phase 1)
+-- smithery-auth.ts
+-- smithery-publish.ts
```

### Directory listing -- After

```
packages/cli/src/lib/component/
+-- factory.ts
+-- index.ts
+-- skill-ops-impl.ts
```

## Error Code Mapping

This phase does not introduce new error code changes. All error codes were already translated in Phase 3 when tests were migrated. However, if any remaining CLI test references a deleted provider's error code, update using the mapping in [PLAN.md](../PLAN.md#error-code-translation-cli---sdk).

## Notes

- The deletion is safe because:
  1. The factory (Phase 2) no longer imports from these files
  2. The barrel `index.ts` already re-exports from SDK, not from local providers
  3. All tests that imported from these files were moved to SDK in Phase 3
- Use `git rm` (not `rm`) to track deletions in git history.
- After this phase, the CLI's component directory goes from 11 files to 3 files -- a 73% reduction.
