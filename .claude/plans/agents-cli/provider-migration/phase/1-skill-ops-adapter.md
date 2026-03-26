# Phase 1: Wire SkillOperations Adapter

## Goal

Create a CLI adapter that implements the SDK's `SkillOperations` interface by delegating to the existing CLI skill modules (`skill-list.ts`, `skill-add.ts`, `skill-remove.ts`, `skill-info.ts`).

## Non-goals

- Do NOT modify the CLI factory yet (that is Phase 2)
- Do NOT move or delete any existing provider files
- Do NOT change any existing test files
- Do NOT modify the SDK's `SkillOperations` interface

## Prerequisites

- SDK's `SkillOperations` interface exists at `packages/sdk/src/providers/local/skill-ops.ts`
- CLI skill modules exist and export their functions: `listSkills`, `addSkill`, `removeSkills`, `skillInfo`
- All tests pass at baseline: CLI 1929/11, SDK 132/0

## Files

| Action | Path |
|--------|------|
| Create | `packages/cli/src/lib/component/skill-ops-impl.ts` |
| Create | `packages/cli/test/component/skill-ops-impl.test.ts` |

## Steps

- [ ] **1.1** Create `packages/cli/src/lib/component/skill-ops-impl.ts` with the `createSkillOps()` factory function
- [ ] **1.2** Create `packages/cli/test/component/skill-ops-impl.test.ts` with structural assertions
- [ ] **1.3** Run `bun test --cwd packages/cli` -- verify zero regressions (1929 pass / 11 fail)
- [ ] **1.4** Commit: `feat(cli): add SkillOperations adapter for SDK provider DI`

## Acceptance Criteria

1. `createSkillOps()` returns an object satisfying `SkillOperations` (has `list`, `add`, `remove`, `info` methods)
2. Each method is a function (typeof check)
3. Dynamic imports use correct relative paths to CLI skill modules
4. New test passes: `bun test packages/cli/test/component/skill-ops-impl.test.ts`
5. Existing tests unaffected -- CLI baseline unchanged

## Failure Criteria

- If any existing CLI test that previously passed now fails, STOP -- the adapter file is somehow affecting module resolution
- If `bun test` cannot find the skill modules at the dynamic import paths, the relative paths are wrong

## Fallback Logic

- If dynamic `import()` paths are wrong, check the actual locations of `skill-list.ts` etc. with `find packages/cli/src -name 'skill-*.ts'` and adjust paths
- If TypeScript complains about the `SkillOperations` type import, verify the SDK package exports it: check `packages/sdk/package.json` exports map

## Examples

### Before (no adapter exists)

CLI factory directly imports provider classes:

```typescript
// packages/cli/src/lib/component/factory.ts (CURRENT)
import { LocalProvider } from './provider-local'
// LocalProvider internally does: await import('../skill-list')
```

### After (adapter created)

```typescript
// packages/cli/src/lib/component/skill-ops-impl.ts (NEW)
import type { SkillOperations } from '@agents/sdk/providers/local/skill-ops'

/**
 * CLI implementation of SkillOperations.
 * Bridges SDK's DI interface to CLI's skill-*.ts modules via dynamic imports.
 */
export function createSkillOps(): SkillOperations {
  return {
    async list(opts) {
      const { listSkills } = await import('../skill-list')
      return listSkills(opts)
    },
    async add(source, opts) {
      const { addSkill } = await import('../skill-add')
      return addSkill(source, opts)
    },
    async remove(names, opts) {
      const { removeSkills } = await import('../skill-remove')
      return removeSkills(names, opts)
    },
    async info(name, opts) {
      const { skillInfo } = await import('../skill-info')
      return skillInfo(name, opts)
    },
  }
}
```

### Test file

```typescript
// packages/cli/test/component/skill-ops-impl.test.ts (NEW)
import { describe, expect, test } from 'bun:test'
import { createSkillOps } from '../../src/lib/component/skill-ops-impl'

describe('createSkillOps', () => {
  test('returns object with list, add, remove, info methods', () => {
    const ops = createSkillOps()
    expect(typeof ops.list).toBe('function')
    expect(typeof ops.add).toBe('function')
    expect(typeof ops.remove).toBe('function')
    expect(typeof ops.info).toBe('function')
  })

  test('returns exactly 4 methods', () => {
    const ops = createSkillOps()
    const keys = Object.keys(ops).sort()
    expect(keys).toEqual(['add', 'info', 'list', 'remove'])
  })
})
```

## Notes

- The adapter uses dynamic `import()` (not static `import`) so that skill modules are only loaded when actually invoked. This preserves CLI startup performance -- commands that do not touch skills never load the skill modules.
- This file stays in CLI permanently. It is CLI-specific glue code, not portable SDK logic.
- The test file `skill-ops-impl.test.ts` also stays in CLI permanently (listed in the "do NOT move" set).
