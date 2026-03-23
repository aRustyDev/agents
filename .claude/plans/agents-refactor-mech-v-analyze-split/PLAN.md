---
id: 678131a9-6bd5-4cd0-9728-610fbc8044df
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
title: "Catalog Pipeline Refactor: Mechanical Discovery vs. LLM Analysis Split"
status: draft
tags: [catalog, pipeline, discovery, analysis, refactor]
related:
  supersedes: [d4e8f2a1-7c3b-4f5e-9a1d-8e6c4b2a0f3d]
---

# Catalog Pipeline Refactor: Mechanical Discovery vs. LLM Analysis Split

**Created:** 2026-03-23
**Updated:** 2026-03-23
**Owner:** aRustyDev
**Predecessor:** `.claude/plans/.archive/catalog-module-integration/PLAN.md`

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Shift from per-skill-name lookup to per-repo discovery | Yes | Discovery finds ALL skills in a repo, not just the one the catalog expects |
| 2 | Separate mechanical computation from LLM judgment | Yes | Phase 1 (discover) produces 100% deterministic output; Phase 2 (analyze) does zero I/O |
| 3 | Capture repo-level and component-level metadata | Yes | Every repo has a manifest; every skill has file sizes, line counts, section maps |
| 4 | Detect skill moves, renames, additions, and removals within repos | Yes | Catalog tracks `discoveredPath`, `lastSeenAt`, `status: removed_from_repo` |
| 5 | Eliminate orphaned error states and reclassify all legacy errors | Yes | 0 entries with `batch_failed`; all errors have structured types |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Fully complete entries | 7,049 (54.2%) | ~9,200 (all analyzable) | 2,151 |
| Partially analyzed (missing fields) | 2,165 | 0 | 2,165 |
| batch_failed (unclassified errors) | 458 | 0 | 458 |
| Repo-level metadata | 0 repos tracked | ~4,500 unique repos | 4,500 |
| Component-level file metadata | 0 | all analyzed entries | ~9,200 |
| Skill move/rename detection | none | automatic | - |
| Discovery model | per-skill-name | per-repo | architectural change |

## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-1 | Schema & Data Model Evolution | pending | - | Repo manifest type, enhanced entry fields, source_invalid rename, migration |
| phase-2 | Repo-level Mechanical Discovery | pending | phase-1 | Clone once per repo, discover all skills, capture all deterministic values |
| phase-3 | Catalog Reconciliation & State Management | pending | phase-2 | Match discovered vs. catalog, detect moves/renames/new/removed |
| phase-4 | Tier 1 Analysis Refactor | pending | phase-3 | Haiku receives pre-computed data, does judgment-only (0 I/O, 0 mechanical work) |
| phase-5 | Tier 2 Deep Analysis | pending | phase-4 | Sonnet agent for quality scoring on non-trivial, non-fork skills |

### Phase Details

1. [Phase 1: Schema & Data Model Evolution](./phase/1-schema-data-model.md)
2. [Phase 2: Repo-level Mechanical Discovery](./phase/2-repo-discovery.md)
3. [Phase 3: Catalog Reconciliation & State Management](./phase/3-catalog-reconciliation.md)
4. [Phase 4: Tier 1 Analysis Refactor](./phase/4-tier1-refactor.md)
5. [Phase 5: Tier 2 Deep Analysis](./phase/5-tier2-analysis.md)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Repo manifest bloats catalog file size | Medium | Low | Separate `.catalog-repos.ndjson` from `.catalog.ndjson` |
| Discovery finds thousands of new skills not in catalog | Medium | Medium | Gate auto-add behind `--auto-discover` flag; default reports only |
| Changing entry schema breaks existing consumers | Low | High | Additive-only changes; no field removals in this phase |
| Tier 2 Sonnet costs higher than expected | Medium | Medium | Gate behind `--tier2` flag; strict filtering (non-fork, non-trivial, >500 words) |
| Git history search (`git log --follow`) is slow on large repos | Medium | Low | Phase 2 initial implementation uses HEAD only; git history is a future extension |

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Planning complete | 2026-03-23 | 2026-03-23 |
| Phase 1 complete (schema) | | |
| Phase 2 complete (discovery) | | |
| Phase 3 complete (reconciliation) | | |
| Phase 4 complete (Tier 1 refactor) | | |
| Phase 5 complete (Tier 2) | | |

## Rollback Strategy

- Phase 1: Schema changes are additive — old entries still valid, new fields optional
- Phase 2: Discovery produces a separate output; existing catalog untouched until Phase 3
- Phase 3: Reconciliation uses `mergeBackfillResults`-style partial merge; existing data preserved
- Phase 4: Blue/green pattern (ADR-026) — `--legacy-analyze` flag if needed
- Phase 5: New command, no impact on existing pipeline

## Cross-Plan Dependencies

| This Plan Phase | Skill-Inspection Phase | Constraint |
|---|---|---|
| phase-4 (Tier 1 Refactor) | phase-4 (Tier 1 Analysis) | This plan's phase-4 must complete before skill-inspection phase-4 starts — both modify `processBatch` in `skill.ts` |
| phase-5 (Tier 2) | phase-5 (Tier 2 Analysis) | This plan's phase-5 must complete before skill-inspection phase-5 starts |

**Execution order:** This plan's phases 1-3 can run independently. Phase 4+ blocks skill-inspection phases 4+.

## Design Decisions

### CLI Contract

`catalog discover` and `catalog analyze` are separate commands. `catalog analyze` auto-invokes discovery when results are stale (>24h) or missing, unless `--skip-discovery` is passed. `--skip-discovery` errors if `.catalog-repos.ndjson` does not exist; warns if last discovery was >24h ago.

### File Persistence

- `.catalog-repos.ndjson` is **gitignored** (changes on every discovery run, like `.catalog.ndjson`)
- `.catalog-repos.ndjson.sql` dump is version-controlled if a SQL export is needed

### Grading of `removed_from_repo` Entries

Entries with `status: removed_from_repo` retain their last-known analysis data and grade. They are excluded from active search results but preserved for historical reference. The skill-inspection Phase 6 grading pipeline treats them as "last known grade, flagged as removed."

### `isSimple` Usage

`isSimple` is included in `SkillManifest` (Phase 4) and used in the Tier 2 gate filter (Phase 5) as an additional signal alongside the >500 words threshold. Simple skills (SKILL.md only) with >500 words still qualify for Tier 2 but are deprioritized in batch ordering.

## Architecture Notes

### Current Model (per-skill-name)

```text
catalog entry (source@skill) → clone repo → search for skill by name → analyze
```

Problems: misses moved skills, misses new skills, clones redundantly, mixes mechanical + judgment work.

### Proposed Model (per-repo discovery)

```text
Phase 1: unique repos from catalog → clone each once → discover ALL skills → compute ALL deterministic fields
Phase 2: discovered skills → Haiku agent (judgment-only, receives pre-computed manifest)
Phase 3: analyzed skills → Sonnet agent (quality scoring, non-trivial only)
```

### Key Data Model Changes

**Repo Manifest** (`.catalog-repos.ndjson`):

```json
{
  "repo": "owner/repo",
  "clonedAt": "2026-03-23T...",
  "headSha": "abc123",
  "totalFiles": 342,
  "repoSizeBytes": 15728640,
  "archived": false,
  "lastCommitAt": "2026-03-20T...",
  "commitCount": 156,
  "contributorCount": 3,
  "skillCount": 12,
  "skills": ["skill-a", "skill-b", ...]
}
```

**Enhanced Catalog Entry** (additions to existing fields):

```json
{
  "source": "owner/repo",
  "skill": "skill-name",
  "discoveredPath": "context/skills/skill-name",
  "lastSeenAt": "2026-03-23T...",
  "lastSeenHeadSha": "abc123",
  "movedFrom": "skills/old-name",
  "skillSizeBytes": 4096,
  "lineCount": 245,
  "sectionMap": [{"heading": "Configuration", "line": 42}, ...],
  "fileTree": ["SKILL.md", "resources/guide.md", "examples/basic.ts"],
  "isSimple": true
}
```

**Error Type Rename**: `source_invalid` → `invalid_source_entry` with structured detail:

```json
{
  "lastErrorType": "invalid_source_entry",
  "errorDetail": "source contains filesystem path: /tmp/worktrees/..."
}
```
