---
id: a1b2c3d4-4444-4aaa-bbbb-444444444444
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 4: Tier 1 Analysis"
status: pending
related:
  depends-on: [a1b2c3d4-2222-4aaa-bbbb-222222222222, a1b2c3d4-3333-4aaa-bbbb-333333333333]
---

# Phase 4: Tier 1 Analysis

**ID:** `phase-4`
**Dependencies:** phase-2, phase-3
**Status:** pending
**Effort:** Large

## Objective

Dispatch Tier 1 (Haiku) agents in isolated worktrees to perform mechanical analysis on all available skills: metadata extraction, keyword indexing, complexity scoring, progressive disclosure detection, regex-based security checks, and fork detection via content hashing.

## Success Criteria

- [ ] All entries with `availability == "available"` have Tier 1 analysis results in `.catalog.ndjson`
- [ ] Fork detection identifies duplicate SKILL.md content across repos (by content hash)
- [ ] Agent dispatch is parallelized (5-10 concurrent worktrees)
- [ ] Failed skill downloads are logged as `error` entries, not blocking the batch
- [ ] `ai-tools skill catalog analyze` command orchestrates dispatches and merges results
- [ ] Incremental: re-running skips already-analyzed entries (by content hash)

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Orchestrator logic | `cli/lib/catalog.ts` (additions) | TypeScript |
| Analyze CLI | `cli/commands/skill.ts` (additions) | TypeScript |
| Updated catalog | `context/skills/.catalog.ndjson` | NDJSON |
| Tests | `cli/test/catalog-analyze.test.ts` | TypeScript |

## Files

**Create:**
- `cli/test/catalog-analyze.test.ts`

**Modify:**
- `cli/lib/catalog.ts` — add orchestrator: batch creation, agent dispatch, result merging
- `cli/commands/skill.ts` — implement `catalog analyze` (replace stub)

## Tasks

### Pre-filter
- [ ] Read `.catalog.ndjson` from Phase 2
- [ ] Filter to `availability == "available"` entries
- [ ] Group by `source` (owner/repo) to avoid downloading the same repo multiple times in a batch
- [ ] Split into batches of 15-20 skills

### Orchestrator
- [ ] For each batch:
  - Create git worktree in `/tmp/worktrees/skill-inspect-<batch-id>/`
  - Dispatch `skill-inspector-t1` agent with the batch list
  - Capture NDJSON stdout from agent
  - Validate each line against `CatalogEntry` schema
  - Merge valid entries into `.catalog.ndjson`
  - Clean up worktree
- [ ] Concurrency: dispatch up to `--concurrency` (default: 5) agents in parallel
- [ ] Failure handling: if agent fails entirely, log batch as failed, continue with next batch
- [ ] Per-skill failure: agent emits error entries for skills that fail to download — orchestrator merges these

### Fork Detection (post-analysis pass)
- [ ] After all Tier 1 results are in: group entries by skill name
- [ ] For entries sharing the same skill name, compare `contentHash`
- [ ] Identical hashes → mark later entries with `possibleForkOf: "<first-seen source>"`
- [ ] Update `.catalog.ndjson` with fork annotations

### CLI Implementation
- [ ] `ai-tools skill catalog analyze [--batch-size 15] [--concurrency 5] [--only-available] [--json]`
- [ ] `--only-available` (default: true) — skip unavailable entries
- [ ] Progress output: batch N/total, skills processed, errors
- [ ] `--json` outputs final summary as JSON

### Incremental Support
- [ ] Before dispatching a batch, check if entries already exist in `.catalog.ndjson` with matching `contentHash`
- [ ] Skip already-analyzed entries unless `--force` is passed
- [ ] New entries from an updated `.TODO.yaml` are analyzed; existing entries are preserved

## Notes

- This is the most compute-intensive phase: ~800 agent dispatches, each downloading 15-20 skills
- Estimated time: 3-5 hours with concurrency=5
- Estimated cost: ~$2-4 (Haiku)
- Worktree isolation prevents `npx skills add` collisions between parallel agents
- The orchestrator is library code in `catalog.ts` — the CLI command is a thin wrapper
- `mdq -o json` provides section trees + link extraction in one call per SKILL.md
