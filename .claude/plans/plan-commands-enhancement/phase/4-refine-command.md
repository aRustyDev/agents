# Phase 4: Refine Command Enhancement

**ID:** `phase-4`
**Dependencies:** phase-2, phase-3
**Status:** complete
**Effort:** 2 hours

## Objective

Update `/context:plan:refine` to auto-fix schema violations and apply review findings.

## Success Criteria

- [ ] `--fix-schema` adds missing required sections
- [ ] `--apply-review` parses and applies review report findings
- [ ] Validation step confirms fixes were applied
- [ ] Report shows before/after status

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Enhanced refine.md | `context/commands/context/plan/refine.md` | Slash command |

## Files

**Create:**

- None

**Modify:**

- `context/commands/context/plan/refine.md`

## Key Changes

### 1. Add --fix-schema Flag

Auto-fix missing required elements:

| Missing Element | Auto-Fix |
|-----------------|----------|
| Objectives table | Add template with placeholder rows |
| Current State table | Add template with TBD values |
| Phases Dependencies column | Add column, default to previous phase |
| Phase Files section | Add Create/Modify with placeholders |
| Deliverables Location | Add column with TBD values |
| Risks Mitigation | Add column with TBD values |

### 2. Enhance --apply-review

Parse review report and apply fixes:

| Review Category | Action |
|-----------------|--------|
| Schema Violations | Apply schema fixes |
| Critical Logic Gaps | Create TODO items in phase |
| Important Gaps | Add to Risks table |
| Consistency Issues | Fix cross-references |
| Clarity Improvements | Apply text changes |

### 3. Add Validation Step

After applying changes:

1. Re-run schema validation
2. Check internal links resolve
3. Verify phase numbering sequential
4. Report remaining issues

### 4. Enhanced Report

```markdown
## Plan Refined

| Field | Value |
|-------|-------|
| Plan | <name> |
| Changes Applied | N |
| Schema Valid | ✓ / ✗ (remaining) |

### Changes Made

**Schema Fixes:**

- Added Objectives table
- Added Files section to Phase 2, 3

**From Review:**

- Fixed: "improve performance" → "reduce p99 by 30%"

### Remaining Issues

| Issue | Location | Action Needed |
|-------|----------|---------------|
| TBD value | Deliverables.Location | Manual fix |
```

### 5. Combined Flags

Support running both:

```bash
/context:plan:refine <path> --fix-schema --apply-review
```

Order: fix schema first, then apply review findings.

## Tasks

- [ ] Implement --fix-schema auto-fix logic
- [ ] Implement review report parsing
- [ ] Add validation step after changes
- [ ] Update report template
- [ ] Support combined flags
- [ ] Handle edge cases (no review file, already valid)

## Notes

- Auto-fixes use placeholder values (TBD, placeholder rows)
- User must fill in actual values after auto-fix
- Review file located at `<plan-dir>/REVIEW.md` or most recent `review-*.md`
