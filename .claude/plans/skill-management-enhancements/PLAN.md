---
id: 3f7a1c8e-9d4b-4e2f-a6c0-5b8d3e1f7a2c
project:
  id: 00000000-0000-0000-0000-000000000000
title: Skill Management Enhancements
status: draft
tags: [skills, cli, agents, installation]
related:
  depends-on: [8a2e4c17-f6d0-4b3a-9e51-3c7d8f1a2b05]
  references: [d4e8f2a1-7c3b-4f5e-9a1d-8e6c4b2a0f3d]
---

# Skill Management Enhancements

**Created:** 2026-03-20
**Updated:** 2026-03-20
**Owner:** aRustyDev

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Extract and internalize skill management logic from vercel-labs/skills | Yes | All 7 commands (find, add, outdated, update, init, list, remove) working via `just agents skill <verb>` |
| 2 | Support multi-agent skill installation with agent registry | Yes | Skills installable to any of 44 known agents with auto-detection (config dir presence) |
| 3 | Enable flexible source references with branch/tag/hash support | Yes | `owner/repo#ref:path@skill` parsed correctly in all commands |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| CLI skill subcommands | 11 (validate, hash, lint, check-all, deps/*, catalog/*) | 18+ (add find, add, outdated, update, init, list, remove) | 7 new commands |
| Source URL formats supported | `owner/repo@skill` only | Full URLs, refs, local paths, well-known URIs | No URL parser |
| Agent targets | Claude Code only (implicit) | 44 agents with auto-detect + `--agent` filter | No agent registry |
| Interactive prompts | None (all batch/non-interactive) | fzf-style search, multiselect, confirmation | No prompt library |

## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-1 | Foundation modules | pending | - | source-parser, agents, git, discovery, prompts libraries created with tests |
| phase-2 | Core commands (add, init, list, filters) | pending | phase-1 | Three commands + filter utilities working end-to-end |
| phase-3 | Search and discovery (find) | pending | phase-1; phase-2 for install-on-select | find command with JSON output, configurable limits |
| phase-4 | Update lifecycle (outdated, update) | pending | phase-1 (4.1); phase-2 (4.2) | outdated/update commands with arbitrary data input |
| phase-5 | Integration (remove, info, refactor, tests, docs) | pending | phase-2, phase-3, phase-4 | remove/info commands, refactored externals, integration tests |

### Phase Details

1. [Phase 1: Foundation Modules](./phase/1-foundation-modules.md)
2. [Phase 2: Core Commands + Filters](./phase/2-core-commands.md)
3. [Phase 3: Search and Discovery](./phase/3-search-discovery.md)
4. [Phase 4: Update Lifecycle](./phase/4-update-lifecycle.md)
5. [Phase 5: Integration](./phase/5-integration-filters.md)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Agent registry stale (new agents, changed paths) | High | Low | Data-driven registry from JSON, easy to update; track vercel-labs/skills as upstream |
| Breaking existing `skill deps` commands | Medium | High | All new code in new files; existing commands untouched until phase-5 integration |
| Source parser ambiguity (`@` means skill filter vs git ref) | Medium | Medium | Use `#` for ref (like npm), `@` for skill filter — different delimiter than vercel |
| Symlink permission failures on Windows | Low | Medium | Fall back to copy mode automatically (same as vercel-labs/skills) |
| Naming collision with existing `skill check-all` | Medium | Medium | New update-detection command named `outdated` (npm convention); existing `check-all` untouched |
| Over-serialized phases block parallel work | Medium | Medium | Relaxed dependency constraints: phase 3/4 can partially start after phase-1; phase 5.4 refactor starts after phase-1 |

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Planning complete | 2026-03-20 | |
| Phase 1 complete | | |
| Phase 2 complete | | |
| All phases complete | | |

## Rollback Strategy

All work in a git worktree. If any phase fails, the worktree can be discarded without affecting main. Each phase produces independent modules that don't modify existing code until phase 5.

## Notes

- This work extracts logic from vercel-labs/skills (MIT licensed) but reimplements it in our Bun/Citty/Valibot stack
- We use `#` for git ref (not `@`) to avoid conflict with the existing `owner/repo@skill` convention
- The agent registry is data we maintain, not a dependency on vercel-labs/skills
- All new modules must use the runtime-aware shims from `lib/runtime.ts` (ADR-016)
- Interactive prompts go in `lib/prompts/` even if initially only used by one command
- Two new dependencies adopted: `simple-git` (typed git CLI wrapper with AbortController, `raw()` for worktrees/sparse-checkout/archive) and `xdg-basedir` (correct XDG path resolution for agent global dirs)
- `skill add` is a parallel installation system — it writes to lock files only, does NOT modify `sources.yaml` (the external deps manifest)
- Agent detection uses config directory presence only (e.g., `~/.cursor` exists), not binary detection
- Coordinates with the skill-inspection pipeline plan — shares `.catalog.ndjson` and search infrastructure
- Naming: `outdated` (not `check`) avoids collision with existing `skill deps check` and `skill check-all`
