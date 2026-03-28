# Phase 4: Move KG Tests (2 files)

## Status: PLANNED

## Goal

Move 2 test files from `packages/cli/test/` to `packages/kg/test/` that test Knowledge
Graph functionality (degradation handling and KG command wiring).

## Non-Goals

- Moving Core or SDK tests (Phases 2-3)
- Restructuring KG source code
- Adding new KG functionality

## Prerequisites

- Phase 1 complete (duplicates resolved)
- KG currently has 3 test files (`chunker.test.ts`, `graph.test.ts`, `meilisearch.test.ts`)
  with 127 passing tests

## File Moves

| Source (CLI) | Destination (KG) | Complications |
|-------------|-----------------|---------------|
| `test/degradation.test.ts` | `test/degradation.test.ts` | Tests embedder/meilisearch availability -- may need KG-internal imports |
| `test/kg-commands.test.ts` | `test/commands.test.ts` | Uses `PROJECT_ROOT` from module import; references `content/` fixtures in string assertions |

## Import Rewrite Rules

### `degradation.test.ts`

Audit current imports. Expected pattern:

```ts
// If importing from @agents/kg/... -- no change needed
import { checkEmbedder } from '@agents/kg/embedder'

// If importing from @agents/cli/... -- rewrite to @agents/kg/...
// (unlikely, but check)
```

### `kg-commands.test.ts`

This file imports `PROJECT_ROOT` from the KG commands module:

```ts
import { PROJECT_ROOT, ... } from '@agents/kg/commands'
// or from a CLI-relative path
```

After moving to `packages/kg/test/`, the import source needs to be a KG-internal path:

```ts
// If currently: import { PROJECT_ROOT } from '../../cli/src/commands/kg'
// Change to:    import { PROJECT_ROOT } from '../src/commands'
// Or if already: import { PROJECT_ROOT } from '@agents/kg/commands'
// No change needed
```

## mock.module Path Updates

Neither file uses `mock.module()`.

## Fixture Path Updates

### `kg-commands.test.ts`

This file references content fixtures in assertions:

```ts
expect(entityIdFromPath('content/skills/beads/SKILL.md')).toBe('content_skills_beads_SKILL')
expect(entityIdFromPath('content/plugins/foo/.claude-plugin/plugin.json')).toBe(...)
```

These are string arguments to `entityIdFromPath()`, not file system reads. The function
parses the path string, not the file. **No change needed.**

However, if the test also uses `PROJECT_ROOT` to resolve absolute paths for file reads:

```ts
expect(f.absPath).toBe(resolve(PROJECT_ROOT, f.relPath))
```

Verify that `PROJECT_ROOT` still resolves correctly after the move. If `PROJECT_ROOT`
is imported from the KG module (not computed in the test file), it will continue to
work because the module's own resolution doesn't change.

## Procedure

```bash
# 1. Move degradation test
git mv packages/cli/test/degradation.test.ts packages/kg/test/degradation.test.ts

# 2. Move kg-commands test (rename to just commands.test.ts)
git mv packages/cli/test/kg-commands.test.ts packages/kg/test/commands.test.ts

# 3. Update imports in both files
#    - Replace any ../src/ relative imports with @agents/kg/ package imports
#    - Replace any @agents/cli/ imports with @agents/kg/ equivalents

# 4. Verify
bun test packages/kg/
bun test packages/cli/
```

## Acceptance Criteria

1. KG test suite: 5 test files, ~135+ passing tests
2. CLI test suite: Pass count decreases by exactly the tests moved
3. Total pass count unchanged (>= 2075)
4. No `@agents/cli` imports in any KG test file
5. `bun test packages/kg/` runs independently

## Verification Commands

```bash
# After moves
bun test packages/kg/ 2>&1 | tail -5    # Should show ~135+ pass
bun test packages/cli/ 2>&1 | tail -5   # Decreased by moved tests

# Verify no CLI imports in KG tests
grep -r '@agents/cli' packages/kg/test/ && echo "FAIL" || echo "OK"

# Count KG test files
ls packages/kg/test/*.test.ts | wc -l   # Should be 5
```

## Failure Criteria and Fallback

- **If `degradation.test.ts` depends on CLI-specific service checks**: It may test
  embedder availability through CLI's service layer. If so, the CLI dependency needs
  to be extracted to KG first, or the test stays in CLI.
- **If `kg-commands.test.ts` imports CLI command wiring**: Some tests may test how KG
  commands are registered in CLI's command tree. Those tests should stay in CLI.
  Split the file if needed: pure KG logic tests move, CLI wiring tests stay.
