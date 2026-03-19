---
id: a1b2c3d4-6666-4aaa-bbbb-666666666666
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 6: Grading & Stats"
status: pending
related:
  depends-on: [a1b2c3d4-4444-4aaa-bbbb-444444444444, a1b2c3d4-5555-4aaa-bbbb-555555555555]
---

# Phase 6: Grading & Stats

**ID:** `phase-6`
**Dependencies:** phase-4, phase-5
**Status:** pending
**Effort:** Small

## Objective

Compute final weighted grades for all catalog entries, generate summary statistics, and produce the `.catalog-stats.json` report.

## Success Criteria

- [ ] All 13,644 entries in `.catalog.ndjson` have a `grade` (A-F) and numeric `score` (0-10)
- [ ] Tier 2 reviewed skills use full 5-dimension grading; Tier 1 only skills use 4-dimension grading capped at C
- [ ] `.catalog-stats.json` generated with category, grade, and availability distributions
- [ ] `ai-tools skill catalog grade` and `ai-tools skill catalog stats` commands work
- [ ] `ai-tools skill catalog search` queries the catalog via jq-style filters

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Grading logic | `.scripts/lib/catalog.ts` (additions) | TypeScript |
| Stats output | `context/skills/.catalog-stats.json` | JSON |
| CLI commands | `.scripts/commands/skill.ts` (additions) | TypeScript |
| Tests | `.scripts/test/catalog-grading.test.ts` | TypeScript |

## Files

**Create:**
- `.scripts/test/catalog-grading.test.ts`
- `context/skills/.catalog-stats.json` — generated output (committed)

**Modify:**
- `.scripts/lib/catalog.ts` — add grading formula, stats aggregation
- `.scripts/commands/skill.ts` — implement `catalog grade`, `catalog stats`, `catalog search`

## Tasks

### Grading Formula
- [ ] Implement two grading modes:

**Tier 2 Reviewed (full grade):**
```
score = (bestPractices/5 * 10 * 0.30)
      + (contentQuality/5 * 10 * 0.25)
      + (security/5 * 10 * 0.20)
      + (min(10, pdTechniques.length * 2.5) * 0.15)
      + (metadataCompleteness * 10 * 0.10)
```

**Tier 1 Only (provisional, capped at C/6.0):**
```
score = min(6.0,
        (bestPracticesMechanical/3.5 * 10 * 0.35)
      + (securityMechanical/4 * 10 * 0.30)
      + (min(10, pdTechniques.length * 2.5) * 0.20)
      + (metadataCompleteness * 10 * 0.15)
)
```

- [ ] Map score to grade: A=9-10, B=7-8, C=5-6, D=3-4, F=0-2
- [ ] Compute `metadataCompleteness`: count of present frontmatter fields / expected fields

### Unavailable / Error Entries
- [ ] Skills with `availability != "available"`: auto-grade F with score 0, note "source unavailable"
- [ ] Skills with `possibleForkOf != null` and `tier2Reviewed: false`: keep Tier 1 provisional grade

### Stats Aggregation
- [ ] Read all `.catalog.ndjson` entries, compute:
  - `totalEntries`, `uniqueSkills`, `uniqueRepos`
  - `categoryDistribution`: count per category
  - `gradeDistribution`: count per grade (A-F)
  - `availabilityDistribution`: count per availability status
  - `forkClusters`: count of unique content hashes that appear in >1 entry
  - `avgScore`: mean score across all entries
  - `tier2ReviewedCount` vs `tier1OnlyCount`
  - `generatedAt`: ISO timestamp
- [ ] Write to `context/skills/.catalog-stats.json`

### CLI Implementation
- [ ] `ai-tools skill catalog grade [--json]` — compute and write grades
- [ ] `ai-tools skill catalog stats [--json]` — show summary table (or JSON)
- [ ] `ai-tools skill catalog search <query> [--category <cat>] [--min-grade <grade>] [--json]`
  - Search `keywords[]` for query match
  - Filter by category and minimum grade
  - Output: table of matching skills with source, category, grade, score
- [ ] `ai-tools skill catalog run` — full pipeline: taxonomy → availability → analyze (t1+t2) → grade

### Justfile Integration
- [ ] Implement `catalog:grade`, `catalog:stats`, `catalog:search` recipes (delegates to ai-tools)
- [ ] Implement `catalog:run` as the full pipeline orchestrator

## Notes

- This phase is fast (seconds) — it's pure computation over existing data
- `.catalog-stats.json` is committed to git for visibility
- The search command is basic jq-style filtering — semantic search is deferred to the knowledge graph
- The `catalog:run` recipe is the entry point for running the entire pipeline end-to-end
