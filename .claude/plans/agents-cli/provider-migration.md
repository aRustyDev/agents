# CLI→SDK Provider Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace CLI's 11 provider files + factory with SDK providers, completing the CLI→SDK migration so all future consumers share one provider implementation.

**Architecture:** CLI's `createComponentManager()` (factory.ts) switches from importing local provider classes to using SDK's `createDefaultProviders()` with dependency injection. CLI provides `SkillOperations` implementation that wraps the existing skill-*.ts modules. Provider tests migrate to SDK.

**Tech Stack:** Bun workspaces, TypeScript, @agents/sdk

---

## Current State

```text
CLI (packages/cli/src/lib/component/)       SDK (packages/sdk/src/providers/)
├── factory.ts (40 lines)                   ├── factory.ts (46 lines)
├── provider-local.ts (216 lines)           ├── local/index.ts (216 lines) ← DI
├── provider-agent.ts (243 lines)           ├── local/agent.ts (254 lines)
├── provider-command.ts (173 lines)         ├── local/command.ts (177 lines)
├── provider-output-style.ts (208 lines)    ├── local/output-style.ts (212 lines)
├── provider-plugin.ts (190 lines)          ├── local/plugin.ts (208 lines)
├── provider-rule.ts (168 lines)            ├── local/rule.ts (172 lines)
├── provider-smithery.ts (188 lines)        ├── smithery/index.ts (193 lines)
├── smithery-auth.ts (91 lines)             ├── smithery/auth.ts (97 lines)
├── smithery-publish.ts (359 lines)         └── smithery/publish.ts (376 lines)
└── index.ts (5 lines)
```

**Key difference:** SDK's `LocalSkillProvider` uses `SkillOperations` DI interface instead of dynamic imports to `skill-list.ts`, `skill-add.ts`, etc.

## Target State

```text
CLI (packages/cli/src/lib/component/)       SDK (unchanged)
├── skill-ops-impl.ts (NEW — wires CLI skill modules to SkillOperations)
├── factory.ts (REWRITTEN — calls SDK's createDefaultProviders)
└── index.ts (updated barrel)
```

All provider-*.ts and smithery-*.ts files deleted from CLI. Tests migrated to SDK.

## Acceptance Criteria

1. `createComponentManager()` in CLI returns a ProviderManager from SDK
2. All 7 CLI commands that call `createComponentManager()` work unchanged
3. All provider tests pass (migrated to SDK test directory)
4. `bun test --cwd packages/cli` — zero regressions from baseline (1929/11)
5. `bun test --cwd packages/sdk` — migrated tests pass
6. No CLI file imports from `lib/component/provider-*` or `lib/component/smithery-*`

---

## Phase 1: Wire SkillOperations implementation

### Task 1.1: Create CLI SkillOperations adapter

**Files:**

- Create: `packages/cli/src/lib/component/skill-ops-impl.ts`
- Test: `packages/cli/test/component/skill-ops-impl.test.ts`

This file adapts CLI's skill-*.ts modules to the SDK's `SkillOperations` interface.

- [ ] **Step 1:** Write the adapter:

```typescript
// packages/cli/src/lib/component/skill-ops-impl.ts
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

- [ ] **Step 2:** Write structural test:

```typescript
// packages/cli/test/component/skill-ops-impl.test.ts
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
})
```

- [ ] **Step 3:** Run tests: `bun test --cwd packages/cli`
- [ ] **Step 4:** Commit: `feat(cli): add SkillOperations adapter for SDK provider DI`

---

## Phase 2: Replace CLI factory

### Task 2.1: Rewrite factory.ts to use SDK providers

**Files:**

- Modify: `packages/cli/src/lib/component/factory.ts`

- [ ] **Step 1:** Rewrite factory:

```typescript
// packages/cli/src/lib/component/factory.ts
import { createDefaultProviders } from '@agents/sdk/providers/factory'
import type { ProviderManager } from '@agents/sdk/providers/manager'
import { createSkillOps } from './skill-ops-impl'

/**
 * Create a fully-configured ProviderManager with all providers registered.
 *
 * Uses SDK's createDefaultProviders with CLI-specific SkillOperations
 * wired via dependency injection.
 */
export function createComponentManager(opts?: {
  cwd?: string
  smitheryBaseUrl?: string
}): ProviderManager {
  const manager = createDefaultProviders({
    cwd: opts?.cwd,
    skillOps: createSkillOps(),
  })
  // If custom smithery URL provided, replace default SmitheryProvider
  if (opts?.smitheryBaseUrl) {
    const { SmitheryProvider } = require('@agents/sdk/providers/smithery')
    // Unregister default, register with custom URL
    // ProviderManager doesn't have unregister, so we construct fresh
    const { createDefaultProviders: create } = require('@agents/sdk/providers/factory')
    const m = create({ cwd: opts.cwd, skillOps: createSkillOps() })
    // Actually — simpler: just register the custom one. Last-registered wins for same id.
    manager.register(new SmitheryProvider({ baseUrl: opts.smitheryBaseUrl }))
  }
  return manager
}
```

**Note:** The `smitheryBaseUrl` option is preserved for backward compat. The SDK's `createDefaultProviders` registers a default SmitheryProvider; if a custom URL is needed, we register a replacement with the same `id`, which overwrites the default in the provider map.

Actually, `ProviderManager.register()` uses `Map.set()` keyed by `provider.id`, so registering a second `SmitheryProvider` with the same `id` (`'smithery'`) replaces the first. The simpler implementation:

```typescript
export function createComponentManager(opts?: {
  cwd?: string
  smitheryBaseUrl?: string
}): ProviderManager {
  const manager = createDefaultProviders({
    cwd: opts?.cwd,
    skillOps: createSkillOps(),
  })
  if (opts?.smitheryBaseUrl) {
    const { SmitheryProvider } = await import('@agents/sdk/providers/smithery')
    manager.register(new SmitheryProvider({ baseUrl: opts.smitheryBaseUrl }))
  }
  return manager
}
```

Wait — `createComponentManager` is sync. Use a dynamic import workaround or make the factory async. Since all callers already `await` the manager's methods (not construction), the cleanest fix is to add `smitheryBaseUrl` to the SDK's `createDefaultProviders` signature. The implementer should update `packages/sdk/src/providers/factory.ts` to accept and forward `smitheryBaseUrl`.

- [ ] **Step 1b:** Update `packages/sdk/src/providers/factory.ts` to accept `smitheryBaseUrl`:

```typescript
export function createDefaultProviders(opts?: {
  cwd?: string
  logger?: Logger
  skillOps?: SkillOperations
  smitheryBaseUrl?: string  // ADD THIS
}): ProviderManager {
  // ...
  manager.register(new SmitheryProvider(
    opts?.smitheryBaseUrl ? { baseUrl: opts.smitheryBaseUrl } : undefined
  ))
  // ...
}
```

- [ ] **Step 2:** Run all CLI tests: `bun test --cwd packages/cli`

**Expected:** The factory test's provider count assertion (`toHaveLength(7)`) will fail — the SDK factory registers 8 providers (7 local + 1 github that CLI didn't have). This is fixed in Task 3.3. All other tests should pass.

- [ ] **Step 3:** Commit: `refactor(cli): rewrite factory to use SDK providers`

---

## Phase 3: Migrate provider tests to SDK

### Task 3.1: Migrate non-skill provider tests

**Files:**

- Move: `packages/cli/test/component/provider-agent.test.ts` → `packages/sdk/test/providers/local/agent.test.ts`
- Move: `packages/cli/test/component/provider-command.test.ts` → `packages/sdk/test/providers/local/command.test.ts`
- Move: `packages/cli/test/component/provider-output-style.test.ts` → `packages/sdk/test/providers/local/output-style.test.ts`
- Move: `packages/cli/test/component/provider-plugin.test.ts` → `packages/sdk/test/providers/local/plugin.test.ts`
- Move: `packages/cli/test/component/provider-rule.test.ts` → `packages/sdk/test/providers/local/rule.test.ts`
- Move: `packages/cli/test/component/provider-smithery.test.ts` → `packages/sdk/test/providers/smithery.test.ts`
- Move: `packages/cli/test/component/smithery-auth.test.ts` → `packages/sdk/test/providers/smithery-auth.test.ts`
- Move: `packages/cli/test/component/smithery-publish.test.ts` → `packages/sdk/test/providers/smithery-publish.test.ts`

- [ ] **Step 1:** For each test file, `git mv` to SDK test directory.

- [ ] **Step 2:** Update imports in each moved test:

```text
from '../../src/lib/component/provider-agent'     → from '@agents/sdk/providers/local/agent'
from '../../src/lib/component/provider-smithery'   → from '@agents/sdk/providers/smithery'
from '../../src/lib/component/smithery-auth'       → from '@agents/sdk/providers/smithery/auth'
from '../../src/lib/component/smithery-publish'    → from '@agents/sdk/providers/smithery/publish'
from '@agents/sdk/context/types'                   → (unchanged, already correct)
from '@agents/sdk/providers/pagination'            → (unchanged)
```

- [ ] **Step 2b:** Update error code assertions in moved tests. SDK providers use `SdkError` codes, not `CliError` codes:

```text
In provider-smithery.test.ts:
  'E_UNSUPPORTED' → 'E_PROVIDER_UNAVAILABLE'  (add, remove, info unsupported ops)

In all local provider tests (agent, command, rule, output-style, plugin):
  'E_UNSUPPORTED_TYPE' → 'E_PROVIDER_UNAVAILABLE'  (unsupported type errors)
```

- [ ] **Step 3:** Run: `bun test --cwd packages/sdk`
- [ ] **Step 4:** Commit: `refactor: migrate non-skill provider tests to SDK`

### Task 3.2: Migrate skill provider test

**Files:**

- Move: `packages/cli/test/component/provider-local.test.ts` → `packages/sdk/test/providers/local/skill.test.ts`

The skill provider test is special — it tested `LocalProvider` which used dynamic imports. Now it needs to test `LocalSkillProvider` which uses `SkillOperations` DI. The test must provide mock skill ops.

- [ ] **Step 1:** `git mv` the test file.

- [ ] **Step 2:** Rewrite test to use mock SkillOperations:

```typescript
import { LocalSkillProvider } from '@agents/sdk/providers/local'
import type { SkillOperations } from '@agents/sdk/providers/local/skill-ops'

function createMockOps(overrides?: Partial<SkillOperations>): SkillOperations {
  return {
    list: async () => ({ ok: true, skills: [{ name: 'test-skill', description: 'A test', source: 'local', agents: [] }] }),
    add: async () => ({ ok: true, installed: [{ name: 'test', source: 'local', canonicalPath: '/tmp/test', agentLinks: [] }], warnings: [] }),
    remove: async () => [{ skill: 'test', removedFrom: ['/tmp/agent'], error: undefined }],
    info: async () => ({ ok: true, value: { name: 'test', path: '/tmp/test', source: 'local', sourceType: 'local', installedAgents: [], symlinkStatus: 'copy' } }),
    ...overrides,
  }
}

// Then use: new LocalSkillProvider(createMockOps(), '/tmp')
```

- [ ] **Step 2b:** Update error code assertions — SDK uses different codes than CLI:

```text
'E_UNSUPPORTED_TYPE' → 'E_PROVIDER_UNAVAILABLE'  (unsupported type checks)
'E_SKILL_NOT_FOUND'  → 'E_COMPONENT_NOT_FOUND'   (info for missing skill)
'E_REMOVE_FAILED'    → 'E_COMPONENT_NOT_FOUND'    (remove errors)
```

- [ ] **Step 3:** Run: `bun test --cwd packages/sdk`
- [ ] **Step 4:** Commit: `refactor: migrate skill provider test to SDK with mock DI`

### Task 3.3: Migrate factory test

**Files:**

- Modify: `packages/cli/test/component/factory.test.ts`

The factory test verifies `createComponentManager()` returns a manager with the right providers registered. Since the factory now delegates to SDK, update the test to verify SDK provider IDs.

- [ ] **Step 1:** Update factory test assertions:
  - Change provider count from 7 → 8 (SDK adds GitHubProvider)
  - Update the `accepts cwd option` test count similarly
  - Add new test: `has github provider for skill search` verifying `findProviders('search', 'skill')` includes a provider with `id === 'github'`
  - Verify `findProviders('search', 'mcp-server')` still routes to smithery
  - Update expected provider IDs: local, local-agent, local-command, local-rule, local-output-style, local-plugin, smithery, github

- [ ] **Step 2:** Run: `bun test --cwd packages/cli`
- [ ] **Step 3:** Commit: `test(cli): update factory test for SDK providers (8 providers, github added)`

### Task 3.4: Migrate remaining component tests (optional cleanup)

**Note:** These files already import from SDK paths (`@agents/sdk/providers/clients/*`), so they will NOT break when CLI provider files are deleted in Phase 4. This move is for organizational consistency only.

**Files that stay in CLI test/component/ (already import from SDK):**

- `manager.test.ts` — imports from `@agents/sdk/providers/manager`
- `pagination.test.ts` — imports from `@agents/sdk/providers/pagination`
- `types.test.ts` — imports from `@agents/sdk/context/types`
- `factory.test.ts` — tests CLI-specific factory function

**Files to optionally move for tidiness:**

- Move: `packages/cli/test/component/client-config.test.ts` → `packages/sdk/test/providers/client-config.test.ts`
- Move: `packages/cli/test/component/clients.test.ts` → `packages/sdk/test/providers/clients.test.ts`

These test SDK code that happens to live in CLI's test directory.

- [ ] **Step 1:** `git mv` both files, update imports.
- [ ] **Step 2:** Run: `bun test --cwd packages/sdk`
- [ ] **Step 3:** Commit: `refactor: migrate client config tests to SDK`

---

## Phase 4: Delete CLI provider files

### Task 4.1: Remove CLI provider source files

**Files:**

- Delete: `packages/cli/src/lib/component/provider-local.ts`
- Delete: `packages/cli/src/lib/component/provider-agent.ts`
- Delete: `packages/cli/src/lib/component/provider-command.ts`
- Delete: `packages/cli/src/lib/component/provider-output-style.ts`
- Delete: `packages/cli/src/lib/component/provider-plugin.ts`
- Delete: `packages/cli/src/lib/component/provider-rule.ts`
- Delete: `packages/cli/src/lib/component/provider-smithery.ts`
- Delete: `packages/cli/src/lib/component/smithery-auth.ts`
- Delete: `packages/cli/src/lib/component/smithery-publish.ts`
- Modify: `packages/cli/src/lib/component/index.ts`

- [ ] **Step 1:** Before deleting, verify NO file in CLI imports from these:

```bash
grep -rn "from.*provider-local\|from.*provider-agent\|from.*provider-command\|from.*provider-output-style\|from.*provider-plugin\|from.*provider-rule\|from.*provider-smithery\|from.*smithery-auth\|from.*smithery-publish" packages/cli/src/ packages/cli/test/
```

Should return ONLY `factory.ts` (which we already rewrote) and `index.ts`.

- [ ] **Step 2:** Delete all 9 provider files.

- [ ] **Step 3:** Update `packages/cli/src/lib/component/index.ts` barrel:

```typescript
// Re-export from SDK for any CLI code that imports from this barrel
export { ProviderManager as ComponentManager } from '@agents/sdk/providers/manager'
export * from '@agents/sdk/context/types'
export * from '@agents/sdk/providers/pagination'
```

- [ ] **Step 4:** Run all tests:

```bash
bun test --cwd packages/sdk
bun test --cwd packages/cli
```

- [ ] **Step 5:** Commit: `refactor(cli): remove CLI provider files — now using SDK providers`

---

## Phase 5: Final verification

### Task 5.1: Audit and verify

- [ ] **Step 1:** Verify no CLI file imports from deleted paths:

```bash
grep -rn "provider-local\|provider-agent\|provider-command\|provider-output-style\|provider-plugin\|provider-rule\|provider-smithery\|smithery-auth\|smithery-publish" packages/cli/src/ packages/cli/test/
```

Expected: zero results.

- [ ] **Step 2:** Run full test suites:

```bash
bun test --cwd packages/core
bun test --cwd packages/sdk
bun test --cwd packages/cli
```

- [ ] **Step 3:** Verify CLI commands work end-to-end:

```bash
bun run packages/cli/src/bin/agents.ts search skill test
bun run packages/cli/src/bin/agents.ts list skill
bun run packages/cli/src/bin/agents.ts doctor
```

- [ ] **Step 4:** Count final state:

```bash
# CLI component/ should have exactly:
ls packages/cli/src/lib/component/
# Expected: factory.ts, index.ts, skill-ops-impl.ts (3 files)

# SDK providers/ should have:
find packages/sdk/src/providers/ -name '*.ts' | wc -l
# Expected: ~20 files
```

- [ ] **Step 5:** Commit: `chore: verify CLI→SDK provider migration complete`

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Mock SkillOperations doesn't match real behavior | Medium | Medium | Test factory integration in CLI, not just unit tests |
| Provider test imports break after move | Medium | Low | grep before move, fix in same commit |
| `createComponentManager()` callers break | Low | High | Return type is same ProviderManager, method signatures unchanged |
| CLI barrel re-exports miss something | Medium | Medium | grep for all `from.*lib/component` imports after cleanup |

## File Inventory

| Phase | Files Created | Files Moved | Files Deleted | Files Modified |
|-------|--------------|-------------|---------------|----------------|
| 1 | 2 (adapter + test) | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 1 (factory.ts) |
| 3 | 0 | 10 (tests) | 0 | 2 (factory test, moved tests) |
| 4 | 0 | 0 | 9 (providers) | 1 (index.ts) |
| 5 | 0 | 0 | 0 | 0 (verification only) |
| **Total** | **2** | **10** | **9** | **4** |
