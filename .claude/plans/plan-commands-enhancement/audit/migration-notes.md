# Migration Notes

**Audit Date:** 2025-03-16

## Key Findings

### 1. Only One Plan Uses New Schema

`plan-commands-enhancement` is the only plan following the new PLAN.md schema. This is expected since we just created it.

### 2. Most Structured Plan: merge-convert-skills

This plan has the richest structure and would benefit most from schema enforcement:

- Already has `index.md` with clear sections
- Has `phase/*.md` files with varying completeness
- Missing: Objectives table, Current State table, Risks, per-phase Files sections

### 3. Different Patterns Serve Different Purposes

| Pattern | Purpose | Migrate? |
|---------|---------|----------|
| PLAN.md + phase/ | Multi-phase implementation plans | Yes (target) |
| brainstorm → research → roadmap | Plugin planning workflow | No (different use case) |
| Numbered task files | Step-by-step guides | Optional |
| Single notes file | Research/exploration | No |

### 4. Schema Validation Should Be Optional

Many existing "plans" are really:

- Research notes (convert-skill-mcp)
- Early drafts (ai-arusty-dev)
- Plugin workflows (plugins/*)

These should not fail schema validation. Recommendation: **default to `--validate-schema=warn`**

## Migration Recommendations

### Migrate: merge-convert-skills

**Effort:** ~30 minutes

**Steps:**

1. Rename `index.md` → `PLAN.md`
2. Add Objectives table (convert Goals prose)
3. Add Current State table (already has similar)
4. Add Risks table
5. Update phase files with Files sections

**Or:** Use as test case for `--fix-schema` auto-migration

### Document Only: sqlite-vec

**Reason:** Task-list structure serves its purpose well

**Action:** Document as alternative "task-list plan" pattern

### Skip: ai-arusty-dev, convert-skill-mcp

**Reason:** Not actually plans - just notes/drafts

**Action:** Consider moving to `.archive/` or `notes/`

### Skip: plugins/*

**Reason:** Uses plugin planning workflow (brainstorm → research → roadmap)

**Action:** Document as separate workflow pattern

### Skip: features/*

**Reason:** Container directory, sub-plans need individual review

**Action:** Review each sub-plan separately if/when they become active

## Validation Mode Recommendations

| Plan Type | Validation Mode | Rationale |
|-----------|-----------------|-----------|
| New plans via `/context:plan:create` | `strict` | Ensure compliance from start |
| Existing implementation plans | `warn` | Show gaps without blocking |
| Research notes | `off` | Not applicable |
| Plugin workflows | `off` | Different pattern |

## Test Cases Selected

For Phase 5 integration testing:

1. **TC2: Legacy Compatibility**
   - Use `merge-convert-skills` as near-compliant plan
   - Test `--validate-schema=off` and `--validate-schema=warn`

2. **TC4: Edge Cases**
   - Use `ai-arusty-dev` as minimal plan
   - Use `convert-skill-mcp` as single-file plan

## Schema Design Implications

Based on this audit, the schema should:

1. **Be lenient by default** - Many valid plans don't match the schema
2. **Support index.md OR PLAN.md** - Both conventions exist
3. **Handle missing sections gracefully** - Report, don't fail
4. **Support `--validate-schema=off`** - For non-plan content in plans directory
