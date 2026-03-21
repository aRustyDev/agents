---
id: 149d764d-4f87-4786-b204-168aea26d19c
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 0: Scaffold & Foundation"
status: pending
related:
  depends-on: [bcb4f31b-e0a1-4bf5-af73-d36426442250]
---

# Phase 0: Scaffold & Foundation

**ID:** `phase-0`
**Dependencies:** None
**Status:** pending
**Effort:** Small

## Objective

Set up the TypeScript project alongside existing Python scripts. Establish the patterns (Result type, shared args, Citty routing) that all subsequent phases follow.

## Success Criteria

- [ ] `bun run .scripts/bin/ai-tools.ts --help` prints all four noun groups (plugin, skill, kg, registry)
- [ ] `bun run .scripts/bin/ai-tools.ts plugin --help` shows stub subcommands
- [ ] `bun test` runs successfully (even if test suite is empty)
- [ ] `just ai-tools --help` works as an alias
- [ ] `lib/types.ts` exports Result<T,E>, ok(), err(), CliError, unwrapOrExit(), tryAsync()
- [ ] `lib/uuid.ts` exports uuid4(), uuid5(), uuid7() — all passing tests

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Bun project config | `.scripts/package.json` | JSON |
| TypeScript config | `.scripts/tsconfig.json` | JSON |
| CLI entry point | `.scripts/bin/ai-tools.ts` | TypeScript |
| Result type module | `.scripts/lib/types.ts` | TypeScript |
| UUID module | `.scripts/lib/uuid.ts` | TypeScript |
| Shared CLI args | `.scripts/commands/shared-args.ts` | TypeScript |
| Command stubs | `.scripts/commands/{plugin,skill,kg,registry}.ts` | TypeScript |
| Unit tests | `.scripts/test/types.test.ts`, `.scripts/test/uuid.test.ts` | TypeScript |

## Files

**Create:**
- `.scripts/package.json`
- `.scripts/tsconfig.json`
- `.scripts/bin/ai-tools.ts`
- `.scripts/lib/types.ts`
- `.scripts/lib/uuid.ts`
- `.scripts/commands/shared-args.ts`
- `.scripts/commands/plugin.ts` (stub)
- `.scripts/commands/skill.ts` (stub)
- `.scripts/commands/kg.ts` (stub)
- `.scripts/commands/registry.ts` (stub)
- `.scripts/test/types.test.ts`
- `.scripts/test/uuid.test.ts`

**Modify:**
- `brewfile` — add `bun` under Core tools
- `justfile` — add `ai-tools` recipe alias, add `_init-bun` step to `init`

## Tasks

- [ ] Run `bun init` in `.scripts/`, configure `package.json` (private, type: module)
- [ ] Configure `tsconfig.json` (strict, moduleResolution: bundler, target: esnext)
- [ ] Add `bun` to `brewfile` under Core tools section
- [ ] Run `brew bundle` to install Bun (or verify already installed)
- [ ] Install core deps: `citty`, `valibot`, `ansis`, `console-table-printer`, `nanospinner`, `@opentf/cli-pbar`, `js-yaml`
- [ ] Install integration deps: `@octokit/core`, `@octokit/auth-oauth-device`
- [ ] Install data deps: `better-sqlite3`, `ollama`, `@carlrannaberg/cclint`
- [ ] Install dev deps: `@bomb.sh/tab`, `@types/better-sqlite3`, `@types/js-yaml`
- [ ] Write `lib/types.ts` — Result type, CliError class, shared enums
- [ ] Write `lib/uuid.ts` — uuid4 (crypto.randomUUID), uuid5 (crypto.subtle), uuid7 (timestamp-sortable)
- [ ] Write `commands/shared-args.ts` — globalArgs with envDefault utility
- [ ] Write stub command modules that export `defineCommand` with `--help` only
- [ ] Write `bin/ai-tools.ts` — Citty root with lazy-loaded subcommands
- [ ] Write unit tests for types.ts (Result, CliError, unwrapOrExit, tryAsync)
- [ ] Write unit tests for uuid.ts (format validation, v5 determinism, v7 ordering)
- [ ] Add `ai-tools` recipe to justfile
- [ ] Add `ai-tools-completions` recipe to generate shell completions via `@bomb.sh/tab`
- [ ] Verify `bun test` passes

## Notes

- `bun` must be added to brewfile so `just init` installs it — this is a prerequisite for the entire migration
- `js-yaml` is needed by Phase 1 (chunker frontmatter) and Phase 4b (sources.yaml parsing)
- All deps are installed upfront even though some aren't used until later phases — avoids re-running `bun add` in each phase
- Command stubs should return a helpful "not yet implemented" message, not silently succeed
- The `envDefault` utility is ~10 lines and handles boolean/string env var parsing
