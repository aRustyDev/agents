# Phase 5: Tier 2 Deep Analysis

**ID:** `phase-5`
**Dependencies:** phase-4
**Status:** pending
**Effort:** Large

## Objective

Implement Sonnet-level deep analysis for non-trivial, non-fork skills. Produces quality grades, detailed reviews, and actionable feedback. Works from fresh clones (independent of Tier 1 judgments) to avoid bias.

## Success Criteria

- [ ] `catalog analyze-deep` command exists (or `catalog analyze --tier2`)
- [ ] Sonnet agent receives full skill content + repo context (not Haiku's judgments)
- [ ] Produces quality grade (A-F), detailed review, improvement suggestions
- [ ] Filters: only non-fork, non-trivial (>500 words), available, Tier 1 complete
- [ ] Results stored in `tier2` field on catalog entries
- [ ] Cost tracking: reports Sonnet token usage per batch

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Tier 2 agent prompt | `cli/commands/skill.ts` | String template |
| Tier 2 result type | `cli/lib/catalog.ts` | TypeScript interface |
| Filtering logic | `cli/lib/catalog.ts` | `filterForTier2()` function |
| CLI command | `cli/commands/skill.ts` | `catalog analyze-deep` subcommand |
| Tests | `cli/test/catalog-tier2.test.ts` | bun:test |

## Files

**Create:**
- `cli/test/catalog-tier2.test.ts`

**Modify:**
- `cli/lib/catalog.ts` — `Tier2Result` interface, `filterForTier2()`, merge function
- `cli/commands/skill.ts` — `catalog analyze-deep` subcommand

## Tasks

- [ ] Define `Tier2Result` interface: grade (A-F), qualityScore (1-100), review (markdown), improvements (string[]), strengths (string[]), weaknesses (string[])
- [ ] Define `filterForTier2(entries)`: available, Tier 1 complete, non-fork, >500 words, not already Tier 2 reviewed
- [ ] Design Sonnet agent prompt: receives full SKILL.md content + mechanical data, produces structured quality assessment
- [ ] Implement `catalog analyze-deep` with `--limit`, `--concurrency`, `--dry-run`
- [ ] Re-download skills for Tier 2 (independent of Tier 1 analysis to avoid bias)
- [ ] Merge Tier 2 results into catalog (additive, doesn't overwrite Tier 1)
- [ ] Cost tracking: log input/output tokens per skill, report batch totals
- [ ] Blue/green validation: run 50 skills, review Sonnet output quality manually

## Tier 2 Grading Rubric

| Grade | Score | Criteria |
|-------|-------|----------|
| A | 90-100 | Comprehensive, well-structured, actionable, good examples, follows best practices |
| B | 75-89 | Solid content, minor gaps in examples or structure |
| C | 60-74 | Adequate but missing depth, structure issues, thin examples |
| D | 40-59 | Minimal content, significant quality issues |
| F | 0-39 | Stub, placeholder, or broken content |

## Notes

- Tier 2 is expensive (~$0.01-0.03 per skill with Sonnet) — strict filtering is important
- Target population: ~4,000-5,000 skills (non-fork, non-trivial, available)
- Total estimated cost: $40-150 depending on skill sizes
- The Sonnet agent should NOT see Haiku's Tier 1 judgments — independent assessment avoids anchoring bias
- Grade distribution should roughly follow a normal curve — if >50% are A's, the rubric is too lenient
- This phase produces the data needed for Phase 6 of the skill-inspection plan (Grading & Stats)
