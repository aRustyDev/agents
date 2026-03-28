# CLI-to-SDK Provider Migration — Plan Index

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan phase-by-phase.

## Overview

**Goal:** Replace CLI's 11 provider files + factory with SDK providers, so all future consumers share one provider implementation.

**Architecture:** CLI's `createComponentManager()` switches from importing local provider classes to calling SDK's `createDefaultProviders()` with dependency injection. CLI provides a `SkillOperations` adapter that wraps existing `skill-*.ts` modules. Provider tests migrate to SDK.

**Tech Stack:** Bun workspaces, TypeScript, `@agents/sdk`

## Current State

```text
CLI (packages/cli/src/lib/component/)       SDK (packages/sdk/src/providers/)
+-- factory.ts (40 lines)                   +-- factory.ts (46 lines)
+-- provider-local.ts (216 lines)           +-- local/index.ts (216 lines) <-- DI
+-- provider-agent.ts (243 lines)           +-- local/agent.ts (254 lines)
+-- provider-command.ts (173 lines)         +-- local/command.ts (177 lines)
+-- provider-output-style.ts (208 lines)    +-- local/output-style.ts (212 lines)
+-- provider-plugin.ts (190 lines)          +-- local/plugin.ts (208 lines)
+-- provider-rule.ts (168 lines)            +-- local/rule.ts (172 lines)
+-- provider-smithery.ts (188 lines)        +-- smithery/index.ts (193 lines)
+-- smithery-auth.ts (91 lines)             +-- smithery/auth.ts (97 lines)
+-- smithery-publish.ts (359 lines)         +-- smithery/publish.ts (376 lines)
+-- index.ts (5 lines)                      +-- github/index.ts (NEW)
(11 CLI files total)
```

**Key difference:** SDK's `LocalSkillProvider` uses a `SkillOperations` DI interface instead of dynamic imports to `skill-list.ts`, `skill-add.ts`, etc.

## Target State

```text
CLI (packages/cli/src/lib/component/)       SDK (unchanged)
+-- skill-ops-impl.ts (NEW)
+-- factory.ts (REWRITTEN)
+-- index.ts (updated barrel)
```

All `provider-*.ts` and `smithery-*.ts` files deleted from CLI. Tests migrated to SDK.

## Phase Summary

| Phase | Title | Depends On | Files Changed | Key Risk |
|-------|-------|-----------|---------------|----------|
| [1](phase/1-skill-ops-adapter.md) | Wire SkillOperations adapter | -- | +2 create | Adapter signature mismatch |
| [2](phase/2-factory-rewrite.md) | Rewrite CLI factory | Phase 1 | ~2 modify | smitheryBaseUrl forwarding |
| [3](phase/3-test-migration.md) | Migrate provider tests to SDK | Phase 2 | ~10 move, ~2 modify | Error code translations |
| [4](phase/4-delete-cli-providers.md) | Delete CLI provider files | Phase 3 | -9 delete, ~1 modify | Stale imports break build |
| [5](phase/5-final-verification.md) | Final verification | Phase 4 | 0 (audit only) | Missed regression |

## Test Baselines

| Package | Pass | Fail |
|---------|------|------|
| CLI | 1929 | 11 |
| SDK | 132 | 0 |
| Core | 10 | 0 |

## Provider Count Change

CLI currently registers **7** providers. SDK factory creates **8** (adds `GitHubProvider`). Tests that assert provider count must update `7 -> 8`.

## Error Code Translation (CLI -> SDK)

Used in Phases 3 and 4 when updating test assertions:

| CLI Code (`CliError`) | SDK Code (`SdkError`) |
|---|---|
| `E_UNSUPPORTED` | `E_PROVIDER_UNAVAILABLE` |
| `E_UNSUPPORTED_OP` | `E_PROVIDER_UNAVAILABLE` |
| `E_UNSUPPORTED_TYPE` | `E_PROVIDER_UNAVAILABLE` |
| `E_UNSUPPORTED_OPERATION` | `E_PROVIDER_UNAVAILABLE` |
| `E_NO_PROVIDER` | `E_PROVIDER_UNAVAILABLE` |
| `E_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` |
| `E_COMMAND_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` |
| `E_SKILL_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` |
| `E_RULE_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` |
| `E_AGENT_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` |
| `E_OUTPUT_STYLE_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` |
| `E_PLUGIN_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` |
| `E_SERVER_NOT_FOUND` | `E_COMPONENT_NOT_FOUND` |
| `E_ADD_FAILED` | `E_PROVIDER_UNAVAILABLE` |
| `E_REMOVE_FAILED` | `E_COMPONENT_NOT_FOUND` |
| `E_AUTH_FAILED` | `E_PROVIDER_UNAVAILABLE` |
| `E_AUTH_REQUIRED` | `E_PROVIDER_UNAVAILABLE` |
| `E_RATE_LIMITED` | `E_PROVIDER_UNAVAILABLE` |
| `E_TIMEOUT` | `E_PROVIDER_TIMEOUT` |
| `E_MISSING_SOURCE` | `E_VALIDATION_FAILED` |
| `E_MISSING_NAME` | `E_VALIDATION_FAILED` |
| `E_MISSING_MANIFEST` | `E_VALIDATION_FAILED` |
| `E_INVALID_NAME` | `E_VALIDATION_FAILED` |
| `E_INVALID_MANIFEST` | `E_VALIDATION_FAILED` |
| `E_POLL_FAILED` | `E_PROVIDER_UNAVAILABLE` |
| `E_DEPLOY_TIMEOUT` | `E_PROVIDER_TIMEOUT` |
| `E_API_ERROR` | `E_PROVIDER_UNAVAILABLE` |
| `E_NETWORK` | `E_PROVIDER_UNAVAILABLE` |

## Global Acceptance Criteria

1. `createComponentManager()` in CLI returns a `ProviderManager` backed by SDK providers
2. All 7 CLI commands that call `createComponentManager()` work unchanged
3. All provider tests pass in their new locations (SDK test directory)
4. `bun test --cwd packages/cli` -- zero regressions from baseline (1929 pass / 11 fail)
5. `bun test --cwd packages/sdk` -- migrated tests pass (132+ pass / 0 fail)
6. No CLI file imports from `lib/component/provider-*` or `lib/component/smithery-*`
7. CLI `component/` directory contains exactly 3 files: `factory.ts`, `index.ts`, `skill-ops-impl.ts`

## Cross-Phase Consistency Notes

- **Import paths:** All moved tests must use `@agents/sdk/...` package imports, never relative `../../` paths back into CLI source.
- **Error types:** Moved tests must import `SdkError` from `@agents/sdk/util/errors`, not `CliError`.
- **Provider IDs:** SDK uses the same provider IDs as CLI (`local`, `local-agent`, `smithery`, etc.) plus `github`. No ID mapping needed.
- **Return types:** `ProviderManager` (SDK) is the same class CLI already re-exports as `ComponentManager`. The alias is preserved in `index.ts`.
- **SkillOperations stays lazy:** The adapter uses dynamic `import()` so skill modules are only loaded when skill operations are actually called, preserving CLI startup performance.

## File Inventory

| Phase | Created | Moved | Deleted | Modified |
|-------|---------|-------|---------|----------|
| 1 | 2 | 0 | 0 | 0 |
| 2 | 0 | 0 | 0 | 2 |
| 3 | 0 | 10 | 0 | 2 |
| 4 | 0 | 0 | 9 | 1 |
| 5 | 0 | 0 | 0 | 0 |
| **Total** | **2** | **10** | **9** | **5** |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Mock SkillOperations doesn't match real behavior | Medium | Medium | Test factory integration in CLI, not just unit tests |
| Provider test imports break after move | Medium | Low | grep before move, fix in same commit |
| `createComponentManager()` callers break | Low | High | Return type is same ProviderManager, method signatures unchanged |
| CLI barrel re-exports miss something | Medium | Medium | grep for all `from.*lib/component` imports after cleanup |
| Error code mapping incomplete | Medium | Medium | Full mapping table above; grep for all `error.code` assertions |
