---
id: a1b2c3d4-1111-4aaa-bbbb-111111111111
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 1: Taxonomy Engine"
status: pending
---

# Phase 1: Taxonomy Engine

**ID:** `phase-1`
**Dependencies:** None
**Status:** pending
**Effort:** Medium

## Objective

Build a hybrid classification engine that categorizes 9,429 unique skill names into 19 categories using keyword rules (~60%) and LLM batch classification (~40%).

## Success Criteria

- [ ] `.taxonomy.yaml` contains all 9,429 unique skill names with category + subcategory
- [ ] Less than 2% of entries classified as `misc`
- [ ] Rule engine covers at least 55% of entries deterministically
- [ ] LLM batches process remaining entries with validated output schema
- [ ] Classification is idempotent — re-running preserves existing entries, only classifies new ones
- [ ] `ai-tools skill catalog taxonomy` command works with `--json` output

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Taxonomy rule engine | `.scripts/lib/taxonomy.ts` | TypeScript |
| Taxonomy output | `context/skills/.taxonomy.yaml` | YAML |
| Valibot schemas | `.scripts/lib/schemas.ts` (additions) | TypeScript |
| CLI subcommand | `.scripts/commands/skill.ts` (additions) | TypeScript |
| Tests | `.scripts/test/taxonomy.test.ts` | TypeScript |

## Files

**Create:**
- `.scripts/lib/taxonomy.ts` — rule engine + LLM batch classification
- `.scripts/test/taxonomy.test.ts` — unit tests for rule matching
- `context/skills/.taxonomy.yaml` — generated output

**Modify:**
- `.scripts/lib/schemas.ts` — add `TaxonomyEntry`, `TaxonomyManifest` schemas
- `.scripts/commands/skill.ts` — add `catalog taxonomy` subcommand
- `.scripts/package.json` — add `@anthropic-ai/sdk` dependency

## Tasks

### Dependencies
- [ ] Add `@anthropic-ai/sdk` to `.scripts/package.json` via `bun add @anthropic-ai/sdk`

### Rule Engine
- [ ] Define the 19 categories with subcategory lists in `taxonomy.ts`
- [ ] Write ~100 regex rules mapping skill name prefixes to category/subcategory
- [ ] Extract unique skill names from `.TODO.yaml` (deduplicate by `@<skill>` suffix)
- [ ] Apply rules, collect unmatched names for LLM classification
- [ ] Test rule engine against known skill names — verify >55% coverage

### LLM Batch Classification
- [ ] Build prompt template: taxonomy definition + batch of 200 names → structured JSON output
- [ ] Implement batch dispatch: split unmatched names into batches of 200
- [ ] Model: `claude-haiku-4-5-20251001` — validate JSON output against Valibot schema per batch
- [ ] Handle failures: log failed batches, retry once, mark remaining as `misc`
- [ ] Incremental: check `.taxonomy.yaml` for existing entries before classifying

### Output
- [ ] Merge rule engine + LLM results into `.taxonomy.yaml`
- [ ] Validate: count `misc` entries, assert <2%
- [ ] Write CLI subcommand `ai-tools skill catalog taxonomy [--force] [--json]`
- [ ] `--force` reclassifies all entries; default only classifies new ones
- [ ] `--json` outputs classification results as JSON array

## Notes

- The rule engine and LLM classification are independent steps — rules run first, LLM fills gaps
- Cost estimate: ~19 batches × ~1K tokens ≈ <$0.50 total (Haiku pricing)
- `.taxonomy.yaml` is committed to git for auditability and incremental updates
- The 19 categories match those defined in the design spec
