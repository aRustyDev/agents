# CLI lib/ Migration Plan

## Goal

Move the 32 remaining TypeScript files from `packages/cli/src/lib/` into their proper packages (`@agents/sdk`, `@agents/kg`) or explicitly mark them as CLI-only. When complete, `cli/src/lib/` retains at most 5 files that are genuinely CLI-specific.

## Current State

| Location | Files | Description |
|----------|-------|-------------|
| `packages/cli/src/lib/` | 32 `.ts` files | Mixed concerns: KG, catalog, skill ops, agents, search, plugins |
| `packages/cli/src/lib/component/` | 3 files | DI wiring: `factory.ts`, `index.ts`, `skill-ops-impl.ts` |
| `packages/sdk/src/` | ~76 files | SDK context, catalog, providers, UI layers |
| `packages/core/src/` | 11 files | Low-level primitives: hash, git, runtime, types |

**Total lines to migrate:** ~11,588 (lib/*.ts) plus updates to ~12 command files that import from lib/.

## Target State

After all 6 phases:

```text
packages/cli/src/lib/
  agents.ts                    # CLI-specific agent config (implements SDK AgentResolver)
  component/
    factory.ts                 # Wires SDK providers with CLI config
    index.ts                   # Barrel re-exports
    skill-ops-impl.ts          # DI adapter (imports from SDK, trivial)
```

Everything else lives in `@agents/sdk` or `@agents/kg`.

## Test Baselines

| Package | Pass | Fail | Notes |
|---------|------|------|-------|
| `@agents/core` | 10 | 0 | Stable foundation |
| `@agents/sdk` | 382 | 0 | Growing as modules move in |
| `@agents/cli` | 1684 | 10 | 10 known failures (pre-existing) |
| `@agents/kg` | 0 | 0 | New package -- tests created in Phase 1 |

**Rule:** No phase may increase the fail count in any package. New code must ship with tests.

## Dependency Graph

```text
Phase 1: KG Extraction ─────────────────────────────────┐
                                                         │
Phase 2: Content Parsing → SDK ──────────────────────────┤
                              │                          │
                              ├── Phase 3: Catalog ──────┤
                              │                          │
Phase 4: Agent Abstraction ───┤                          │
                              │                          │
                              ├── Phase 5: Skill Ops ────┤
                                                         │
                              Phase 6: Cleanup ──────────┘
```

- **Phase 1** is independent -- no blockers, no downstream until Phase 6.
- **Phase 2** is independent -- unlocks Phases 3 and 5.
- **Phase 3** depends on Phase 2 (manifest.ts and lockfile.ts must be in SDK).
- **Phase 4** is independent -- but must complete before Phase 5.
- **Phase 5** depends on Phases 2 + 4 (content parsing + agent abstraction).
- **Phase 6** depends on all previous phases.

**Parallelism:** Phases 1, 2, and 4 can run concurrently.

## Phase Summary

| Phase | Name | Files Moved | Target Package | Lines |
|-------|------|-------------|----------------|-------|
| 1 | KG Extraction | 6 | `@agents/kg` (new) | ~1,369 |
| 2 | Content Parsing | 4 | `@agents/sdk` | ~1,507 |
| 3 | Catalog Pipeline | 7 | `@agents/sdk` | ~3,719 |
| 4 | Agent Abstraction | 0 (create interface) | `@agents/sdk` | ~50 new |
| 5 | Skill Operations | 11 | `@agents/sdk` | ~2,924 |
| 6 | Search & Cleanup | 3 + verify | `@agents/sdk` | ~1,781 |

**Total:** 31 files moved/dissolved + 1 file stays (`agents.ts`). Component directory (3 files) stays.

## Global Acceptance Criteria

1. All existing tests pass (core 10/0, SDK 382+/0, CLI 1684/10).
2. New code has at least one test per exported function.
3. No circular dependencies between packages.
4. `bun run packages/cli/src/bin/agents.ts --help` works.
5. CLI commands that exercised moved modules still pass their integration tests.
6. `cli/src/lib/` contains exactly 4 files (agents.ts + 3 component/ files).
7. `packages/kg/` exists with package.json, exports, and passing tests.
8. No `import ... from '../lib/...'` in any SDK or KG package.

## Error Code Mapping

Modules use `CliError` codes. After migration, SDK modules should use `SdkError` (from `@agents/sdk/util/errors`) instead. Map:

| CLI Code | SDK Code | Module |
|----------|----------|--------|
| `E_UNKNOWN_AGENT` | `E_AGENT_UNKNOWN` | agents.ts (stays CLI) |
| `E_LOCKFILE_PARSE` | `E_STORAGE_BACKEND` | lockfile.ts |
| `E_MANIFEST_PARSE` | `E_PARSE_FAILED` | manifest.ts |
| `E_CATALOG_IO` | `E_STORAGE_BACKEND` | catalog*.ts |
| `E_KG_*` | `E_KG_*` (new) | graph*.ts, embedder.ts |
| `E_SEARCH_*` | `E_SEARCH_*` | search.ts, meilisearch.ts |

## Test Migration Policy

For each module moved from CLI to SDK/KG:
1. If a corresponding test exists in `packages/cli/test/`, move it to the destination package's test directory.
2. Update test imports to use the new package path.
3. If the test has CLI-specific fixtures or setup, keep it in CLI and update imports to point to the new package.

**Test files per phase:**
- **Phase 1:** `chunker.test.ts`, `graph.test.ts` --> `packages/kg/test/`
- **Phase 2:** `manifest.test.ts`, `lockfile.test.ts` --> `packages/sdk/test/`
- **Phase 3:** `catalog-*.test.ts` (7 files) --> `packages/sdk/test/catalog/`
- **Phase 5:** `skill-*.test.ts` (7 files) --> `packages/sdk/test/providers/local/`
- **Phase 6:** `external-skills*.test.ts` --> `packages/sdk/test/`

## Non-Goals

- **No behavioral changes.** This is a pure structural refactor. Functions keep the same signatures and semantics.
- **No new features.** Each phase produces identical output as before.
- **No Python changes.** The `chunker.py` and `embedder.py` files stay in cli/src/lib/ (they are Python, not TypeScript).
- **No command restructuring.** CLI commands keep their current file layout; only their imports change.
- **No package publishing.** All packages remain `private: true` workspace packages.
- **No dependency version bumps.** Dependencies move between package.json files at their current versions.

## Phase Details

See individual phase files:

- [Phase 1: KG Extraction](./phase/1-kg-extraction.md)
- [Phase 2: Content Parsing](./phase/2-content-parsing.md)
- [Phase 3: Catalog Pipeline](./phase/3-catalog-pipeline.md)
- [Phase 4: Agent Abstraction](./phase/4-agent-abstraction.md)
- [Phase 5: Skill Operations](./phase/5-skill-operations.md)
- [Phase 6: Search & Cleanup](./phase/6-search-and-cleanup.md)

## Migration Strategy per File

For each file:

1. **Copy** to target location (do not delete source yet).
2. **Update imports** in the copy to use package-relative paths.
3. **Replace error classes** (`CliError` -> `SdkError` for SDK modules).
4. **Re-export from source** -- change the original file to `export * from '@agents/<pkg>/...'`.
5. **Run tests** -- all existing tests must pass via the re-export shim.
6. **Update consumers** -- change command files to import from the new package.
7. **Delete shim** -- remove the re-export file from cli/src/lib/.
8. **Run tests again** -- confirm nothing breaks.

This two-step approach (shim then delete) prevents big-bang breakage. If step 6 causes failures, the shim still works as a fallback.
