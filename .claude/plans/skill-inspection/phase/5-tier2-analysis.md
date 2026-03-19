---
id: a1b2c3d4-5555-4aaa-bbbb-555555555555
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 5: Tier 2 Analysis"
status: pending
related:
  depends-on: [a1b2c3d4-4444-4aaa-bbbb-444444444444]
---

# Phase 5: Tier 2 Analysis

**ID:** `phase-5`
**Dependencies:** phase-4
**Status:** pending
**Effort:** Large

## Objective

Dispatch Tier 2 (Sonnet) agents for qualitative analysis of non-fork, non-trivial, available skills: content quality assessment, actionable trigger detection, and prompt injection review.

## Success Criteria

- [ ] All skills passing the Tier 2 gate have `contentQuality`, judgment-based `bestPractices`, and injection `security` scores
- [ ] Tier 2 results merge cleanly into existing Tier 1 entries in `.catalog.ndjson`
- [ ] Skills NOT sent to Tier 2 have `tier2Reviewed: false` and default scores
- [ ] Agent dispatch is parallelized (3-5 concurrent worktrees)
- [ ] Incremental: re-running skips already Tier-2-reviewed entries

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Tier 2 orchestrator | `.scripts/lib/catalog.ts` (additions) | TypeScript |
| Updated catalog | `context/skills/.catalog.ndjson` | NDJSON |
| Tests | `.scripts/test/catalog-tier2.test.ts` | TypeScript |

## Files

**Create:**
- `.scripts/test/catalog-tier2.test.ts`

**Modify:**
- `.scripts/lib/catalog.ts` — add Tier 2 orchestrator, gating logic, result merging
- `.scripts/commands/skill.ts` — extend `catalog analyze` to support `--tier 1|2|all`

## Tasks

### Gating Filter
- [ ] Read Tier 1 results from `.catalog.ndjson`
- [ ] Filter to entries matching ALL of:
  - `availability == "available"`
  - `possibleForkOf == null`
  - `complexity != "simple" || wordCount >= 200`
  - `tier2Reviewed != true` (skip already reviewed)
- [ ] Log gate stats: total entries → after each filter → final Tier 2 candidate count

### Orchestrator
- [ ] For each batch of 10-15 gated skills:
  - Create git worktree
  - Provide the agent with NDJSON entries from Tier 1 (so it has metadata context)
  - Agent re-downloads skill (or reuses if worktree has it) and performs qualitative review
  - Capture NDJSON merge entries from agent
  - Merge into existing `.catalog.ndjson` entries (update fields, don't replace)
  - Set `tier2Reviewed: true` on merged entries
  - Clean up worktree
- [ ] Concurrency: up to `--concurrency` (default: 3) agents in parallel
- [ ] Lower concurrency than Tier 1 because Sonnet is slower and more expensive

### Default Scores for Non-Tier-2 Skills
- [ ] After Tier 2 completes, sweep `.catalog.ndjson` for entries with `tier2Reviewed: false`
- [ ] Set default values:
  - `contentQuality: { score: 0, notes: "not reviewed (filtered)" }`
  - `bestPractices.score` = Tier 1 mechanical score only (0-3.5 range)
  - `security.score` = Tier 1 regex score only (0-4 range)

### CLI Extension
- [ ] Extend `ai-tools skill catalog analyze` with `--tier 1|2|all` flag
  - `--tier 1` — run only Tier 1 (Haiku mechanical)
  - `--tier 2` — run only Tier 2 (Sonnet qualitative, requires Tier 1 data)
  - `--tier all` (default for `catalog run`) — run Tier 1 then Tier 2
- [ ] Progress: show Tier 2 gate stats before dispatching

## Notes

- Estimated dispatches: ~300-500 (filtered from ~11K available to ~4-5K non-fork non-trivial)
- Estimated cost: ~$15-25 (Sonnet)
- Tier 2 agents need SKILL.md content to make qualitative judgments — they must download or have access to the skill files
- The merge semantics are additive: Tier 2 fields are added/updated on existing Tier 1 entries, not replacing them
- If a Tier 2 agent fails on a batch, those skills keep their Tier 1 scores with `tier2Reviewed: false`
