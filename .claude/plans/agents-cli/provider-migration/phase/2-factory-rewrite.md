# Phase 2: Rewrite CLI Factory

## Goal

Rewrite `packages/cli/src/lib/component/factory.ts` to delegate to SDK's `createDefaultProviders()` instead of directly constructing CLI provider classes.

## Non-goals

- Do NOT delete any CLI provider files yet (that is Phase 4)
- Do NOT move any test files yet (that is Phase 3)
- Do NOT change the public signature of `createComponentManager()` beyond what is needed

## Prerequisites

- Phase 1 complete: `skill-ops-impl.ts` exists and its test passes
- SDK's `createDefaultProviders()` exists at `packages/sdk/src/providers/factory.ts`
- The `SmitheryProvider` constructor accepts an optional `{ baseUrl }` config

## Files

| Action | Path |
|--------|------|
| Modify | `packages/cli/src/lib/component/factory.ts` |
| Modify | `packages/sdk/src/providers/factory.ts` |

## Steps

- [ ] **2.1** **REQUIRED CODE CHANGE:** Update `packages/sdk/src/providers/factory.ts` to accept `smitheryBaseUrl` in its options and forward it to `SmitheryProvider`. The SDK factory currently does NOT have a `smitheryBaseUrl` parameter -- this must be added (see Examples below for before/after).
- [ ] **2.2** Rewrite `packages/cli/src/lib/component/factory.ts` to call `createDefaultProviders()` with `skillOps` and `smitheryBaseUrl`
- [ ] **2.3** Add a test in `packages/cli/test/component/factory.test.ts` that verifies `createComponentManager({ smitheryBaseUrl: 'https://custom.url' })` passes the URL to the SmitheryProvider. Verify by checking the provider's internal state or by mocking the SmitheryProvider constructor.
- [ ] **2.4** Run `bun test --cwd packages/cli` -- expect the factory test's `toHaveLength(7)` assertions to fail (SDK registers 8 providers). All other tests should pass.
- [ ] **2.5** Commit: `refactor(cli): rewrite factory to use SDK providers`

## Acceptance Criteria

1. `createComponentManager()` calls `createDefaultProviders()` from SDK
2. `createComponentManager({ smitheryBaseUrl: '...' })` forwards the URL to SDK factory
3. `createComponentManager({ cwd: '/tmp' })` forwards `cwd` to SDK factory
4. `createSkillOps()` is passed as `skillOps` to SDK factory
5. CLI factory file no longer imports from `./provider-*` or `./smithery-*`
6. `bun test --cwd packages/sdk` still passes (132/0)
7. `bun test --cwd packages/cli` has no NEW failures except the expected provider count assertions (7 -> 8)

## Failure Criteria

- If any CLI command that uses `createComponentManager()` breaks at runtime, STOP -- the return type or method signatures have changed
- If SDK tests regress after modifying `factory.ts`, STOP -- the `smitheryBaseUrl` change broke existing behavior
- If more than 2-3 tests fail (the count assertions), investigate -- something beyond the expected count change is wrong

## Fallback Logic

- If `createComponentManager` callers need an async factory (e.g., for dynamic imports), consider making `createComponentManager` async and updating all call sites. But this should NOT be needed -- `createDefaultProviders` is synchronous.
- If the `smitheryBaseUrl` approach of modifying the SDK factory is rejected, alternative: make `createComponentManager` register a replacement `SmitheryProvider` after calling `createDefaultProviders`. Since `ProviderManager.register()` uses `Map.set()` keyed by `provider.id`, a second `SmitheryProvider` with the same ID (`'smithery'`) replaces the first.

## Examples

### SDK factory.ts -- Before

```typescript
// packages/sdk/src/providers/factory.ts (CURRENT)
export function createDefaultProviders(opts?: {
  cwd?: string
  logger?: Logger
  skillOps?: SkillOperations
}): ProviderManager {
  const manager = new ProviderManager()
  manager.register(new SmitheryProvider())
  // ...
}
```

### SDK factory.ts -- After

```typescript
// packages/sdk/src/providers/factory.ts (MODIFIED)
export function createDefaultProviders(opts?: {
  cwd?: string
  logger?: Logger
  skillOps?: SkillOperations
  smitheryBaseUrl?: string          // <-- ADD
}): ProviderManager {
  const manager = new ProviderManager()
  manager.register(new SmitheryProvider(
    opts?.smitheryBaseUrl ? { baseUrl: opts.smitheryBaseUrl } : undefined
  ))
  // ... rest unchanged
}
```

### CLI factory.ts -- Before

```typescript
// packages/cli/src/lib/component/factory.ts (CURRENT)
import { ComponentManager } from '@agents/sdk/providers/manager'
import { LocalAgentProvider } from './provider-agent'
import { LocalCommandProvider } from './provider-command'
import { LocalProvider } from './provider-local'
import { LocalOutputStyleProvider } from './provider-output-style'
import { LocalPluginProvider } from './provider-plugin'
import { LocalRuleProvider } from './provider-rule'
import { SmitheryProvider } from './provider-smithery'

export function createComponentManager(opts?: {
  cwd?: string
  smitheryBaseUrl?: string
}): ComponentManager {
  const cwd = opts?.cwd
  const manager = new ComponentManager()
  manager.register(new LocalProvider(cwd))
  manager.register(new LocalAgentProvider(cwd))
  manager.register(new LocalPluginProvider(cwd))
  manager.register(new LocalRuleProvider(cwd))
  manager.register(new LocalCommandProvider(cwd))
  manager.register(new LocalOutputStyleProvider(cwd))
  manager.register(
    new SmitheryProvider(opts?.smitheryBaseUrl ? { baseUrl: opts.smitheryBaseUrl } : undefined)
  )
  return manager
}
```

### CLI factory.ts -- After

```typescript
// packages/cli/src/lib/component/factory.ts (REWRITTEN)
import { createDefaultProviders } from '@agents/sdk/providers/factory'
import type { ProviderManager } from '@agents/sdk/providers/manager'
import { createSkillOps } from './skill-ops-impl'

/**
 * Create a fully-configured ProviderManager with all providers registered.
 *
 * Delegates to SDK's createDefaultProviders with CLI-specific SkillOperations
 * wired via dependency injection.
 */
export function createComponentManager(opts?: {
  cwd?: string
  smitheryBaseUrl?: string
}): ProviderManager {
  return createDefaultProviders({
    cwd: opts?.cwd,
    skillOps: createSkillOps(),
    smitheryBaseUrl: opts?.smitheryBaseUrl,
  })
}
```

## Notes

- The rewritten factory drops from 40 lines with 7 imports to ~15 lines with 3 imports.
- `ComponentManager` was already a re-export of `ProviderManager` from SDK. The return type is compatible.
- The factory test will fail its `toHaveLength(7)` check because SDK registers 8 providers (adds `GitHubProvider`). This is expected and fixed in Phase 3 (Task 3.3).
- Do NOT fix the factory test count in this phase. Leave it failing so Phase 3 has a clear signal of what to update.
