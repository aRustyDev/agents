---
id: bcb4f31b-e0a1-4bf5-af73-d36426442250
project:
  id: 00000000-0000-0000-0000-000000000000
title: Python to TypeScript Migration (cli/)
status: archived
tags: [migration, typescript, bun, cli]
---

# Python to TypeScript Migration (cli/)

**Created:** 2026-03-18
**Updated:** 2026-03-18
**Owner:** aRustyDev

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Consolidate to a single runtime (Bun) for all project scripting | Yes | `uv` and `pyproject.toml` removed from toolchain (or reduced to KG-only fallback) |
| 2 | Unified CLI tool (`ai-tools`) replacing individual Python scripts | Yes | All justfile recipes call `bun run cli/bin/ai-tools.ts` instead of `uv run python` |
| 3 | Add external skill tracking (passthrough/derived modes, drift detection, GH issues) | Yes | `ai-tools skill deps check/sync/issues/links/status` commands functional e2e |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Runtimes required | 2 (Python + Node/Bun) | 1 (Bun) | -1 runtime |
| CLI entry points | 8 separate Python scripts | 1 unified `ai-tools` binary | -7 entry points |
| External Python deps | 10+ (sqlite-vec, ollama, httpx, watchdog, etc.) | 0 (or sqlite-vec + ollama fallback) | -8+ deps |
| External TS deps | 0 | 13 (all lightweight) | +13 (net smaller footprint) |
| Skill dep management | None | Full (passthrough/derived, drift detection, GH issues) | New capability |

## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-0 | Scaffold & Foundation | **done** | - | `ai-tools --help` works, `bun test` runs |
| phase-1 | Core Library | **done** | phase-0 | hash, symlink, output, chunker pass tests; hash output matches Python |
| phase-2 | Schema & Manifest Layer | **done** | phase-1 | All real repo manifests/lockfiles parse; staleness matches Python |
| phase-3 | Plugin Commands | **done** | phase-1, phase-2 | All plugin recipes use TS; output matches Python |
| phase-4a | Skill Commands + GitHub | **done** | phase-1, phase-2 | Skill recipes (validate, hash, lint) use TS; GitHub auth works |
| phase-4b | External Skill Tracking | **done** | phase-4a | 5 deps subcommands work e2e; .external/ structure operational |
| phase-5 | Registry Crawler | **done** | phase-1 | Registry recipes use TS; crawl output matches Python |
| phase-6 | Knowledge Graph | **skipped** | phase-1 | Gate failed: better-sqlite3 unsupported in Bun, bun:sqlite lacks loadExtension. KG stays in Python. |
| phase-7 | Cleanup | **done** | phase-3, phase-4b, phase-5, phase-6 | Python removed (or minimized to KG-only) |

### Phase Details

1. [Phase 0: Scaffold & Foundation](./phase/0-scaffold.md)
2. [Phase 1: Core Library](./phase/1-core-library.md)
3. [Phase 2: Schema & Manifest Layer](./phase/2-schema-manifest.md)
4. [Phase 3: Plugin Commands](./phase/3-plugin-commands.md)
5. [Phase 4a: Skill Commands + GitHub](./phase/4a-skill-commands.md)
6. [Phase 4b: External Skill Tracking](./phase/4b-external-skill-tracking.md)
7. [Phase 5: Registry Crawler](./phase/5-registry-crawler.md)
8. [Phase 6: Knowledge Graph](./phase/6-knowledge-graph.md)
9. [Phase 7: Cleanup](./phase/7-cleanup.md)

## Architecture

### Directory Structure

```
cli/
├── package.json                 # Bun project, private, type: "module"
├── tsconfig.json
├── bun.lock
├── bin/
│   └── ai-tools.ts             # Single CLI entry point (Citty router)
├── lib/
│   ├── types.ts                 # Result<T,E>, CliError, shared enums/constants
│   ├── uuid.ts                  # v4 (native), v5 (crypto.subtle), v7 (timestamp-sortable)
│   ├── hash.ts                  # Content-addressed hashing (file, dir, verify)
│   ├── symlink.ts               # Symlink health checks, creation, resolution
│   ├── schemas.ts               # Valibot schemas for all JSON structures
│   ├── lockfile.ts              # Schema-driven lockfile parse/update/staleness
│   ├── manifest.ts              # Plugin/skill manifest I/O, format detection
│   ├── github.ts                # Octokit wrapper (Device Flow, issue CRUD)
│   ├── output.ts                # Unified output formatter (human/JSON dual mode)
│   ├── chunker.ts               # Markdown parsing, frontmatter, hierarchical chunking
│   ├── embedder.ts              # Ollama client, Float32Array embeddings
│   ├── db.ts                    # better-sqlite3 + sqlite-vec setup
│   └── registry.ts              # Registry crawling, rate limiting, transforms
├── commands/
│   ├── shared-args.ts           # Global args (--verbose, --json) with env fallback
│   ├── plugin.ts                # plugin build|check|hash|update|lint
│   ├── skill.ts                 # skill validate|hash|deps|sync|lint
│   ├── kg.ts                    # kg ingest|search|similar|stats|dump
│   └── registry.ts              # registry crawl|validate|stats
└── test/
    ├── hash.test.ts
    ├── lockfile.test.ts
    ├── symlink.test.ts
    ├── output.test.ts
    └── ...
```

### Dependency Inventory

| Dependency | Size | Purpose | Category |
|------------|------|---------|----------|
| `citty` | 2.9 KB | CLI framework | CLI |
| `@bomb.sh/tab` | small | Shell completions (Citty adapter) | CLI |
| `valibot` | ~1.4 KB used | Schema validation & type inference | Core |
| `@octokit/core` | ~6 KB | GitHub API client | Integration |
| `@octokit/auth-oauth-device` | ~4 KB | Device Flow OAuth | Integration |
| `better-sqlite3` | native | SQLite + sqlite-vec extension | Data |
| `ollama` | small | Embedding generation | Data |
| `@carlrannaberg/cclint` | ~30 KB | Claude Code project linting | Lint |
| `js-yaml` | ~3 KB | YAML parsing (sources.yaml manifest, frontmatter) | Core |
| `console-table-printer` | ~52 KB | Pretty terminal tables | Output |
| `ansis` | ~6 KB | Terminal colors (Bun-native) | Output |
| `nanospinner` | ~20 KB | Spinners for long operations | Output |
| `@opentf/cli-pbar` | small | Progress bars (Bun-native) | Output |
| Custom (owned) | 0 | Result type, UUID, output formatter, tree renderer | Core |

### CLI Surface

```
ai-tools plugin build <name> [--force] [--check-only] [--update-hashes]
ai-tools plugin check <name> [--json]
ai-tools plugin hash <path>
ai-tools plugin lint [<name>]
ai-tools plugin check-all [--json]
ai-tools plugin build-all [--force] [--update-hashes]

ai-tools skill validate <name>
ai-tools skill hash <name>
ai-tools skill deps check [--json]
ai-tools skill deps sync [--force] [--json]
ai-tools skill deps issues [--dry-run] [--json]
ai-tools skill deps links
ai-tools skill deps status [--json]
ai-tools skill lint [<name>]
ai-tools skill check-all

ai-tools kg init [--force]
ai-tools kg ingest [--all] [--type <type>] [--file <path>] [--model <model>]
ai-tools kg search <query> [--limit <n>]
ai-tools kg similar <slug> [--k <n>]
ai-tools kg stats
ai-tools kg dump
ai-tools kg load
ai-tools kg watch [--model <model>]

ai-tools registry crawl [--tier api|scrape|awesome|all] [--resume] [--dry-run]
ai-tools registry validate
ai-tools registry stats
```

All commands support `--verbose`, `--json`, `--quiet` globally via the Citty spread pattern.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| CLI framework | Citty | 2.9 KB, zero-dep, Bun-native, async-first, TypeScript-native |
| Schema validation | Valibot | Smallest (1.4 KB used), zero-dep, tree-shakeable, infers TS types |
| Error handling | Custom Result<T, CliError> | ~25 LOC, zero-dep, user-friendly terminal output |
| GitHub API | @octokit/core + auth-oauth-device | Device Flow OAuth, ~10 KB total, Bun-compatible |
| Terminal colors | ansis | Smallest, fastest, explicit Bun support, truecolor |
| Tables | console-table-printer | Native TypeScript, minimal deps, rich features |
| UUID | Native crypto | v4/v5/v7 all implementable with zero deps |
| Global CLI options | Spread pattern (Nuxi approach) | Proven, type-safe, no Citty plugin hacks |
| Env var support | process.env in arg defaults | Simple, transparent, ~10 LOC utility |
| Shell completions | @bomb.sh/tab | Native Citty adapter, recommended by Citty maintainers |
| Output formatting | Custom dual-mode formatter | ~80 LOC, switches human/JSON based on --json flag |
| Lockfile schemas | Extensible registry pattern | Add new lockfile formats without changing core logic |

### Parity Validation Pattern

Used throughout the migration to confirm TS output matches Python:

```bash
# Python output
uv run python cli/<script>.py <args> --json > /tmp/py.json

# TypeScript output
bun run cli/bin/ai-tools.ts <noun> <verb> <args> --json > /tmp/ts.json

# Diff
diff /tmp/py.json /tmp/ts.json
```

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| sqlite-vec doesn't work with better-sqlite3 under Bun | Medium | High | Phase 6 runs last; fallback is keeping KG in Python |
| Citty pre-1.0 API breaks | Low | Medium | Pin version in bun.lock; Citty is backed by UnJS/Nuxt org |
| Embedding output differs between Python/TS Ollama clients | Low | Medium | Same model + input = same output; validate in Phase 6 |
| console-table-printer output format differs from Python rich | Low | Low | JSON mode is the machine-readable contract; human output can differ |

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Planning complete | 2026-03-18 | 2026-03-18 |
| Phase 0 complete (scaffold) | | |
| Phase 2 complete (schema layer) | | |
| Phases 3-5 complete (commands) | | |
| Phase 6 complete (KG) | | |
| Phase 7 complete (cleanup) | | |

## Rollback Strategy

Both Python and TypeScript coexist during the entire migration. Each phase cuts over justfile recipes one group at a time. To rollback any phase:

1. Revert the justfile recipe changes (point back to `uv run python`)
2. The Python scripts remain in place until Phase 7 cleanup
3. Phase 7 (cleanup) is the only irreversible step — do not execute until all phases are validated

## GAP Review Notes

**Reviewed:** 2026-03-18

### Gaps (addressed)
- `bun` missing from brewfile — added to Phase 0
- `js-yaml` missing from Phase 0 dep install — added
- No ROADMAP.md — created
- No frontmatter on plan docs — added

### Areas for Refinement
- Phase 4 was too large — split into 4a (existing commands) and 4b (external skill tracking)
- Exit codes not specified for Phases 3, 5, 6 — to be added
- Shell completions setup task missing — to be added to Phase 0 or 3

### Potential Extensions
- CI integration: `just external:check` as periodic GitHub Action
- `ai-tools` as a standalone installable binary (future, post-migration)
- Plugin dependency tracking (same pattern as skill deps, different manifest)

## Notes

- The IR code conversion system (`.claude/plans/merge-convert-skills/tools/`) is out of scope — it stays in Python
- The `sentence-transformers` fallback is dropped — Ollama is the sole embedding backend
- If sqlite-vec under Bun fails, the KG system stays in Python and `pyproject.toml` is kept with minimal deps
