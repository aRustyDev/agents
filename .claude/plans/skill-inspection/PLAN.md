---
id: d4e8f2a1-7c3b-4f5e-9a1d-8e6c4b2a0f3d
project:
  id: 00000000-0000-0000-0000-000000000000
title: Skill Catalog Inspection Pipeline
status: draft
tags: [skills, catalog, taxonomy, analysis, pipeline]
---

# Skill Catalog Inspection Pipeline

**Created:** 2026-03-18
**Updated:** 2026-03-18
**Owner:** aRustyDev
**Spec:** `docs/superpowers/specs/2026-03-18-skill-catalog-pipeline-design.md`

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Categorize all 9,429 unique skill names into a 19-category taxonomy | Yes | <2% classified as `misc` |
| 2 | Determine availability of all 13,644 skill entries | Yes | 100% entries have `available\|archived\|not_found\|private\|error` status |
| 3 | Analyze content quality of available, non-fork skills via tiered agents | Yes | All available non-fork skills have Tier 1 results; all non-trivial have Tier 2 |
| 4 | Grade and index the full catalog for searchability | Yes | `.catalog.ndjson` queryable via `jq`, `.catalog-stats.json` generated |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Categorized skills | 0 | 9,429 | 9,429 |
| Availability checked | 0 | 13,644 | 13,644 |
| Content analyzed (Tier 1) | 0 | ~11,000 (available) | ~11,000 |
| Content analyzed (Tier 2) | 0 | ~4,500 (non-fork, non-trivial) | ~4,500 |
| Graded entries | 0 | 13,644 | 13,644 |

## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-1 | Taxonomy Engine | pending | - | `.taxonomy.yaml` generated, <2% misc |
| phase-2 | Availability Check | pending | - | All entries have availability status |
| phase-3 | Agent Definitions & Tooling | pending | - | Both agent .md files created, `ai-tools skill catalog` commands scaffolded |
| phase-4 | Tier 1 Analysis | pending | phase-2, phase-3 | All available skills have mechanical analysis results |
| phase-5 | Tier 2 Analysis | pending | phase-4 | Non-fork, non-trivial skills have qualitative scores |
| phase-6 | Grading & Stats | pending | phase-4, phase-5 | Final grades computed, `.catalog-stats.json` generated |

### Phase Details

1. [Phase 1: Taxonomy Engine](./phase/1-taxonomy-engine.md)
2. [Phase 2: Availability Check](./phase/2-availability-check.md)
3. [Phase 3: Agent Definitions & Tooling](./phase/3-agent-tooling.md)
4. [Phase 4: Tier 1 Analysis](./phase/4-tier1-analysis.md)
5. [Phase 5: Tier 2 Analysis](./phase/5-tier2-analysis.md)
6. [Phase 6: Grading & Stats](./phase/6-grading-stats.md)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GitHub rate limiting during availability check (13K requests) | High | Medium | Authenticate with GITHUB_TOKEN (5K/hr), batch with delays, resume from checkpoint |
| `npx skills add` failures for individual skills in Tier 1 | Medium | Low | Agent logs failure per-skill, continues batch, marks entry as `error` |
| LLM batch classification inconsistency in Phase 1 | Low | Medium | Validate output schema, retry failed batches, preserve incremental results in `.taxonomy.yaml` |
| Worktree cleanup failure leaves orphan directories | Low | Low | `just catalog:cleanup` recipe to sweep `/tmp/worktrees/` |
| Cost overrun on Tier 2 Sonnet dispatches | Low | Medium | Gate Tier 2 strictly — only non-fork, non-trivial, available skills (~4-5K of 13K) |

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Planning complete | 2026-03-18 | 2026-03-18 |
| Phase 1 complete (taxonomy) | | |
| Phase 2 complete (availability) | | |
| Phase 3 complete (tooling) | | |
| Phase 4 complete (Tier 1) | | |
| Phase 5 complete (Tier 2) | | |
| Phase 6 complete (grading) | | |

## Rollback Strategy

Each phase produces independent artifacts. To rollback:
- Phase 1: delete `.taxonomy.yaml`
- Phase 2: delete availability entries from `.catalog.ndjson`
- Phases 4-5: delete analysis entries from `.catalog.ndjson`
- Phase 6: delete `.catalog-stats.json`, revert grade fields

The `.TODO.yaml` source is never modified. All generated files can be regenerated from it.

## Notes

- Phases 1 and 2 have no dependencies on each other — they can run in parallel
- Phase 3 (agent definitions + CLI scaffolding) can also run in parallel with 1 and 2
- This plan maps to Phase 4c in the TypeScript migration plan (depends on Phase 4b External Skill Tracking for `.external/` infrastructure)
- `mdq` (yshavit/mdq) must be added to brewfile before Phase 4 execution
- `@anthropic-ai/sdk` must be added to `cli/package.json` before Phase 1 execution
- `.catalog.ndjson` is gitignored (generated artifact); `.taxonomy.yaml` and `.catalog-stats.json` are committed
