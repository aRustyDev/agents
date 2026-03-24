---
id: e3f4a5b6-7c8d-9e0f-1a2b-3c4d5e6f7a8b
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
title: Monorepo + CLI Decomposition Roadmap
status: draft
---

# Monorepo + CLI Decomposition — Roadmap

## Milestones

| Milestone | Phase | Target | Actual | Version Bump |
|-----------|-------|--------|--------|-------------|
| Fix broken components/ recipes | phase-0 | TBD | | patch |
| Cleanup dead directories | phase-1 | TBD | | patch |
| CLI to packages/cli with src/test | phase-2 | TBD | | minor |
| Rename context/ → content/ | phase-3 | TBD | | minor |
| Root workspace configuration | phase-4 | TBD | | minor |
| Part A verification | phase-5 | TBD | | — |
| Shared library modules | phase-6 | TBD | | minor |
| Verb-first decomposition | phase-7 | TBD | | **major** |
| Config system + placeholders | phase-8 | TBD | | minor |
| Doctor + Serve MVP | phase-9 | TBD | | minor |

## Issues

Issues to be created via `/beads:string` after plan approval.

## Cross-Plan Dependencies

| This Plan | Other Plan | Constraint |
|-----------|-----------|------------|
| phase-7 (decomposition) | agents-refactor phase-4 | **Done.** Refactor plan's processBatch refactored. skill.ts ready for decomposition. |
| phase-5 (Part A done) | All other plans | All plans referencing `cli/` or `context/` paths break until Part A updates them |

## Version Strategy

- Part A (phases 0-5): Non-breaking moves and renames. Minor version bumps.
- Part B phase-7: **Breaking change** — command grammar changes from noun-first to verb-first. Major version bump. Backward-compat aliases provided during transition.
- Part B phases 8-9: New features. Minor version bumps.

## Links

- Plan: `.claude/plans/agents-cli/PLAN.md`
- CLI Grammar: `.claude/plans/agents-cli/reference/product/commands.md`
- Module Architecture: `.claude/plans/agents-cli/reference/product/requirements.md`
- Registry Providers: `.claude/plans/agents-cli/reference/providers.yaml`
- Library Research: `.claude/plans/agents-cli/reference/libraries.md`
- Predecessor (archived): `.claude/plans/.archive/monorepo-workspace/`
