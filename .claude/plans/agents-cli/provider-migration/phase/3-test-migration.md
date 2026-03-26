# Phase 3: Migrate Provider Tests to SDK

## Goal

Move provider test files from `packages/cli/test/component/` to `packages/sdk/test/providers/`, update their imports to reference SDK source paths, and translate error code assertions from CLI codes to SDK codes.

## Non-goals

- Do NOT delete CLI provider source files yet (that is Phase 4)
- Do NOT move tests that already import from SDK paths (see "Files that stay" below)
- Do NOT modify provider source code -- only test files change

## Prerequisites

- Phase 2 complete: CLI factory delegates to SDK's `createDefaultProviders()`
- SDK providers exist and use `SdkError` with SDK error codes
- The factory test's `toHaveLength(7)` is currently failing (expected -- SDK has 8 providers)

## Files

### Files to move (CLI -> SDK)

| Source (CLI) | Destination (SDK) |
|---|---|
| `packages/cli/test/component/provider-agent.test.ts` | `packages/sdk/test/providers/local/agent.test.ts` |
| `packages/cli/test/component/provider-command.test.ts` | `packages/sdk/test/providers/local/command.test.ts` |
| `packages/cli/test/component/provider-output-style.test.ts` | `packages/sdk/test/providers/local/output-style.test.ts` |
| `packages/cli/test/component/provider-plugin.test.ts` | `packages/sdk/test/providers/local/plugin.test.ts` |
| `packages/cli/test/component/provider-rule.test.ts` | `packages/sdk/test/providers/local/rule.test.ts` |
| `packages/cli/test/component/provider-local.test.ts` | `packages/sdk/test/providers/local/skill.test.ts` |
| `packages/cli/test/component/provider-smithery.test.ts` | `packages/sdk/test/providers/smithery.test.ts` |
| `packages/cli/test/component/smithery-auth.test.ts` | `packages/sdk/test/providers/smithery-auth.test.ts` |
| `packages/cli/test/component/smithery-publish.test.ts` | `packages/sdk/test/providers/smithery-publish.test.ts` |
| `packages/cli/test/component/client-config.test.ts` | `packages/sdk/test/providers/client-config.test.ts` |

### Files to modify (stay in CLI)

| Path | Change |
|---|---|
| `packages/cli/test/component/factory.test.ts` | Update provider count 7->8, add github test |

### Files that stay in CLI (do NOT move)

- `packages/cli/test/component/manager.test.ts` -- already imports from SDK
- `packages/cli/test/component/pagination.test.ts` -- already imports from SDK
- `packages/cli/test/component/types.test.ts` -- already imports from SDK
- `packages/cli/test/component/factory.test.ts` -- tests CLI-specific factory
- `packages/cli/test/component/skill-ops-impl.test.ts` -- tests CLI-specific adapter (Phase 1)
- `packages/cli/test/component/clients.test.ts` -- already imports from SDK

## Steps

### Task 3.1: Move non-skill local provider tests

- [ ] **3.1.1** Create target directories if needed: `mkdir -p packages/sdk/test/providers/local`
- [ ] **3.1.2** `git mv` provider-agent, provider-command, provider-output-style, provider-plugin, provider-rule tests to SDK
- [ ] **3.1.3** Update imports in each moved file (see Import Translation Table below)
- [ ] **3.1.4** Update error code assertions in each moved file (see Error Code Translation Table below)
- [ ] **3.1.5** Run `bun test --cwd packages/sdk` -- moved tests should pass

### Task 3.2: Move skill provider test

- [ ] **3.2.1** `git mv packages/cli/test/component/provider-local.test.ts packages/sdk/test/providers/local/skill.test.ts`
- [ ] **3.2.2** Rewrite test to use mock `SkillOperations` instead of real CLI skill modules
- [ ] **3.2.3** Update imports to SDK paths
- [ ] **3.2.4** Update error code assertions (see Error Code Translation Table below)
- [ ] **3.2.5** Run `bun test --cwd packages/sdk` -- skill test should pass

### Task 3.3: Update CLI factory test

- [ ] **3.3.1** Change `toHaveLength(7)` to `toHaveLength(8)` in both assertions
- [ ] **3.3.2** Add test: `has github provider for skill search`
- [ ] **3.3.3** Run `bun test --cwd packages/cli` -- factory test should pass

### Task 3.4: Move smithery tests

- [ ] **3.4.1** `git mv` provider-smithery, smithery-auth, smithery-publish tests to SDK
- [ ] **3.4.2** Update imports in each moved file
- [ ] **3.4.3** Update error code assertions
- [ ] **3.4.4** Run `bun test --cwd packages/sdk` -- smithery tests should pass

### Task 3.5: Move client-config test

- [ ] **3.5.1** `git mv packages/cli/test/component/client-config.test.ts packages/sdk/test/providers/client-config.test.ts`
- [ ] **3.5.2** Update imports
- [ ] **3.5.3** Run `bun test --cwd packages/sdk`

### Task 3.6: Final verification

- [ ] **3.6.1** Run `bun test --cwd packages/sdk` -- all tests pass (132+ pass / 0 fail)
- [ ] **3.6.2** Run `bun test --cwd packages/cli` -- no regressions from baseline
- [ ] **3.6.3** Commit: `refactor: migrate provider tests from CLI to SDK`

## Import Translation Table

When moving tests from CLI to SDK, update import paths as follows:

| Old Import (CLI relative) | New Import (SDK package) |
|---|---|
| `from '../../src/lib/component/provider-agent'` | `from '../../src/providers/local/agent'` |
| `from '../../src/lib/component/provider-command'` | `from '../../src/providers/local/command'` |
| `from '../../src/lib/component/provider-output-style'` | `from '../../src/providers/local/output-style'` |
| `from '../../src/lib/component/provider-plugin'` | `from '../../src/providers/local/plugin'` |
| `from '../../src/lib/component/provider-rule'` | `from '../../src/providers/local/rule'` |
| `from '../../src/lib/component/provider-local'` | `from '../../src/providers/local/index'` |
| `from '../../src/lib/component/provider-smithery'` | `from '../../src/providers/smithery/index'` |
| `from '../../src/lib/component/smithery-auth'` | `from '../../src/providers/smithery/auth'` |
| `from '../../src/lib/component/smithery-publish'` | `from '../../src/providers/smithery/publish'` |
| `from '@agents/sdk/context/types'` | `from '../../src/context/types'` (or keep package import) |
| `from '@agents/sdk/providers/pagination'` | `from '../../src/providers/pagination'` (or keep package import) |

**Note:** Prefer relative imports within the SDK package for consistency with existing SDK tests. Check `packages/sdk/test/providers/github.test.ts` for the import style used by existing SDK tests.

## Error Code Translation Table

All error code assertions in moved tests must be updated. The CLI providers used `CliError` codes; the SDK providers use `SdkError` codes.

### Local provider tests (agent, command, output-style, plugin, rule)

| Test File | Old Code | New Code | Context |
|---|---|---|---|
| `provider-agent.test.ts` | `E_AGENT_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` | info for missing agent |
| `provider-agent.test.ts` | `E_UNSUPPORTED_TYPE` | `E_PROVIDER_UNAVAILABLE` | search for wrong type |
| `provider-agent.test.ts` | `E_UNSUPPORTED_OP` | `E_PROVIDER_UNAVAILABLE` | add/remove not supported |
| `provider-command.test.ts` | `E_COMMAND_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` | info for missing command |
| `provider-command.test.ts` | `E_UNSUPPORTED_TYPE` | `E_PROVIDER_UNAVAILABLE` | search for wrong type |
| `provider-output-style.test.ts` | `E_OUTPUT_STYLE_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` | info for missing style |
| `provider-output-style.test.ts` | `E_UNSUPPORTED_TYPE` | `E_PROVIDER_UNAVAILABLE` | search for wrong type |
| `provider-plugin.test.ts` | `E_PLUGIN_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` | info for missing plugin |
| `provider-plugin.test.ts` | `E_UNSUPPORTED_TYPE` | `E_PROVIDER_UNAVAILABLE` | search for wrong type |
| `provider-plugin.test.ts` | `E_UNSUPPORTED_OPERATION` | `E_PROVIDER_UNAVAILABLE` | add/remove not supported |
| `provider-rule.test.ts` | `E_RULE_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` | info for missing rule |
| `provider-rule.test.ts` | `E_UNSUPPORTED_TYPE` | `E_PROVIDER_UNAVAILABLE` | search for wrong type |

### Skill provider test (provider-local -> skill)

| Old Code | New Code | Context |
|---|---|---|
| `E_SKILL_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` | info for missing skill |
| `E_UNSUPPORTED_TYPE` | `E_PROVIDER_UNAVAILABLE` | search/info for wrong type |

### Smithery tests

| Test File | Old Code | New Code | Context |
|---|---|---|---|
| `provider-smithery.test.ts` | `E_UNSUPPORTED` | `E_PROVIDER_UNAVAILABLE` | add/remove/info not supported |
| `provider-smithery.test.ts` | `E_AUTH_REQUIRED` | `E_PROVIDER_UNAVAILABLE` | publish without auth |
| `provider-smithery.test.ts` | `E_MISSING_NAME` | `E_VALIDATION_FAILED` | publish without name |
| `smithery-auth.test.ts` | `E_AUTH_REQUIRED` | `E_PROVIDER_UNAVAILABLE` | no token |
| `smithery-auth.test.ts` | `E_API_ERROR` | `E_PROVIDER_UNAVAILABLE` | HTTP error |
| `smithery-auth.test.ts` | `E_NETWORK` | `E_PROVIDER_UNAVAILABLE` | network failure |
| `smithery-auth.test.ts` | `E_TIMEOUT` | `E_PROVIDER_TIMEOUT` | request timeout |
| `smithery-publish.test.ts` | `E_SERVER_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` | 404 on server |
| `smithery-publish.test.ts` | `E_AUTH_FAILED` | `E_PROVIDER_UNAVAILABLE` | 401 response |
| `smithery-publish.test.ts` | `E_RATE_LIMITED` | `E_PROVIDER_UNAVAILABLE` | 429 response |
| `smithery-publish.test.ts` | `E_API_ERROR` | `E_PROVIDER_UNAVAILABLE` | other HTTP error |
| `smithery-publish.test.ts` | `E_INVALID_NAME` | `E_VALIDATION_FAILED` | bad qualified name |
| `smithery-publish.test.ts` | `E_MISSING_SOURCE` | `E_VALIDATION_FAILED` | no URL or bundleDir |
| `smithery-publish.test.ts` | `E_MISSING_MANIFEST` | `E_VALIDATION_FAILED` | no manifest.json |
| `smithery-publish.test.ts` | `E_INVALID_MANIFEST` | `E_VALIDATION_FAILED` | bad manifest JSON |
| `smithery-publish.test.ts` | `E_DEPLOY_TIMEOUT` | `E_PROVIDER_TIMEOUT` | deploy polling timeout |

### Client-config test

| Old Code | New Code | Context |
|---|---|---|
| `E_STORAGE_BACKEND` | `E_STORAGE_BACKEND` | No change -- already uses SDK code |

## Acceptance Criteria

1. All 10 test files successfully moved via `git mv` (tracked by git as renames)
2. All moved tests pass when run from SDK: `bun test --cwd packages/sdk`
3. CLI factory test passes with updated count (8 providers)
4. CLI test baseline maintained: 1929 pass / 11 fail (minus moved tests, plus any new tests)
5. No moved test file imports anything from `packages/cli/src/`
6. Every error code assertion in moved tests uses an `SdkErrorCode` value

## Failure Criteria

- If a moved test fails because it cannot resolve a module, STOP -- check the import path translation
- If a moved test fails on an error code assertion, check the Error Code Translation Table above
- If the CLI baseline changes by more than the number of tests moved, STOP -- something else broke
- If `git mv` reports a conflict, the file has uncommitted changes -- resolve before proceeding

## Fallback Logic

- If a test file imports helpers or fixtures from CLI test directories, copy (not move) the helpers to SDK test directory first
- If the skill provider test cannot be cleanly rewritten with mock `SkillOperations`, keep it in CLI test directory as an integration test and create a new unit test in SDK with mocks
- If `client-config.test.ts` already uses SDK codes (it does for `E_STORAGE_BACKEND`), no error code changes are needed for that file

## Examples

### Skill provider test -- Before (CLI)

```typescript
// packages/cli/test/component/provider-local.test.ts
import { LocalProvider } from '../../src/lib/component/provider-local'

describe('LocalProvider', () => {
  const provider = new LocalProvider('/tmp')

  test('info returns error for missing skill', async () => {
    const result = await provider.info('nonexistent', 'skill')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_SKILL_NOT_FOUND')
  })
})
```

### Skill provider test -- After (SDK)

```typescript
// packages/sdk/test/providers/local/skill.test.ts
import { LocalSkillProvider } from '../../src/providers/local/index'
import type { SkillOperations } from '../../src/providers/local/skill-ops'

function createMockOps(overrides?: Partial<SkillOperations>): SkillOperations {
  return {
    list: async () => ({ ok: true, skills: [] }),
    add: async () => ({ ok: true, installed: [], warnings: [] }),
    remove: async () => [],
    info: async () => ({ ok: false, error: { message: 'not found' } }),
    ...overrides,
  }
}

describe('LocalSkillProvider', () => {
  const provider = new LocalSkillProvider(createMockOps(), '/tmp')

  test('info returns error for missing skill', async () => {
    const result = await provider.info('nonexistent', 'skill')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.error.code).toBe('E_COMPONENT_NOT_FOUND')
  })
})
```

### Factory test -- Before

```typescript
test('has 7 providers registered', () => {
  const manager = createComponentManager()
  expect(manager.providers()).toHaveLength(7)
})
```

### Factory test -- After

```typescript
test('has 8 providers registered', () => {
  const manager = createComponentManager()
  expect(manager.providers()).toHaveLength(8)
})

test('has github provider for skill search', () => {
  const manager = createComponentManager()
  expect(manager.getProvider('github')).toBeDefined()
  const providers = manager.findProviders('search', 'skill')
  expect(providers.some((p) => p.id === 'github')).toBe(true)
})
```

## Notes

- Use `git mv` (not copy+delete) to preserve git history for the moved files.
- The `clients.test.ts` file already imports from `@agents/sdk` paths, so it does NOT need to be moved. It stays in CLI.
- The `manager.test.ts` file already imports from SDK and tests the SDK `ProviderManager` class directly. It stays in CLI.
- The skill provider test (Task 3.2) requires the most work because it must be rewritten to use mock `SkillOperations` instead of real file system operations. All other tests are straightforward move-and-update-imports.
