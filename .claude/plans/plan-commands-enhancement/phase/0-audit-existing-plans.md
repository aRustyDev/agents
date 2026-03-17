# Phase 0: Audit Existing Plans

**ID:** `phase-0`
**Dependencies:** None
**Status:** complete
**Effort:** 1 hour

## Objective

Survey existing plans in `.claude/plans/` to understand current state and identify migration guidance needed.

## Success Criteria

- [x] Inventory of all existing plans created
- [x] Current structure patterns documented
- [x] Migration complexity assessed per plan
- [x] Recommendations for legacy plan handling

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Plans inventory | `.claude/plans/plan-commands-enhancement/audit/inventory.md` | Markdown |
| Migration notes | `.claude/plans/plan-commands-enhancement/audit/migration-notes.md` | Markdown |

## Files

**Create:**

- `.claude/plans/plan-commands-enhancement/audit/inventory.md`
- `.claude/plans/plan-commands-enhancement/audit/migration-notes.md`

**Modify:**

- None

## Audit Checklist

For each plan in `.claude/plans/`:

| Check | Question |
|-------|----------|
| Structure | Uses `index.md` or `PLAN.md`? |
| Objectives | Has objectives table? Has Measurable column? |
| Current State | Has current state table? |
| Phases | Has phases table? Has Dependencies column? |
| Per-Phase | Do phases have Success Criteria, Deliverables, Files? |
| Risks | Has risks table? Has Mitigation column? |

## Migration Categories

| Category | Criteria | Action |
|----------|----------|--------|
| Compliant | Already matches schema | No action needed |
| Near-compliant | Missing 1-2 sections | Auto-fix with `--fix-schema` |
| Partial | Missing multiple sections | Manual review + auto-fix |
| Legacy | Completely different structure | Document only, don't migrate |
| Archived | In `.archive/` | Skip |

## Tasks

- [x] List all plans in `.claude/plans/`
- [x] Categorize each plan
- [x] Document common patterns
- [x] Identify which plans to use as test cases
- [x] Write migration recommendations

## Notes

- Focus on understanding, not fixing
- Archived plans (`.archive/`) should be skipped
- Active/in-progress plans need careful migration path
