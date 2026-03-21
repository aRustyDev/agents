# Phase 5: Integration Test

**ID:** `phase-5`
**Dependencies:** phase-2, phase-3, phase-4
**Status:** complete
**Effort:** 2 hours

## Objective

Verify the full create → review → refine cycle works end-to-end.

## Success Criteria

- [x] Create generates valid plan
- [x] Review identifies intentional gaps in test plan
- [x] Refine fixes gaps and passes re-review
- [x] Edge cases handled gracefully
- [x] Commands work with existing (legacy) plans

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Test plan | `.claude/plans/plan-commands-enhancement/test/` | Plan directory |
| Test results | `.claude/plans/plan-commands-enhancement/test/RESULTS.md` | Markdown |

## Files

**Create:**

- `.claude/plans/plan-commands-enhancement/test/PLAN.md`
- `.claude/plans/plan-commands-enhancement/test/RESULTS.md`

**Modify:**

- None (test artifacts)

## Test Cases

### TC1a: Happy Path - New Plan

1. Run `/context:plan:create test-integration --phases 2`
2. Verify PLAN.md has all required sections
3. Run `/context:plan:review test/`
4. Verify review passes with no critical schema gaps
5. Verify review report includes all 5 dimensions

### TC1b: Failure + Recovery

1. Delete one required section from test plan
2. Run `/context:plan:review test/`
3. Verify review catches missing section as Critical gap
4. Run `/context:plan:refine test/ --fix-schema`
5. Verify section restored with placeholder values
6. Run `/context:plan:review test/` again
7. Verify schema now passes (may have warnings for TBD values)

### TC2: Legacy Plan Compatibility

1. Use existing plan without new schema sections
2. Run `/context:plan:review <legacy> --validate-schema=off`
3. Verify review completes without schema errors
4. Run `/context:plan:review <legacy> --validate-schema=warn`
5. Verify warnings logged but doesn't fail

### TC3: Apply Review

1. Create plan with intentional gaps
2. Run `/context:plan:review` → save report
3. Run `/context:plan:refine --apply-review`
4. Verify changes match review suggestions
5. Re-run review, verify gaps resolved

### TC4: Edge Cases

| Case | Input | Expected |
|------|-------|----------|
| Empty plan | `PLAN.md` with only title | Schema violations reported |
| No phases | Plan without phase/ dir | Handled gracefully |
| Circular deps | Phase depends on itself | Detected as logic gap |
| Missing review | `--apply-review` without review file | Clear error message |

## Tasks

- [x] Create test plan with known gaps
- [x] Run TC1: Full cycle
- [x] Run TC2: Legacy compatibility
- [x] Run TC3: Apply review
- [x] Run TC4: Edge cases
- [x] Document results

## Results Template

```markdown
# Integration Test Results

**Date:** YYYY-MM-DD
**Commands Tested:** create, review, refine

## Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC1: Full Cycle | PASS/FAIL | |
| TC2: Legacy | PASS/FAIL | |
| TC3: Apply Review | PASS/FAIL | |
| TC4: Edge Cases | PASS/FAIL | |

## Issues Found

| Issue | Severity | Resolution |
|-------|----------|------------|
| | | |

## Conclusion

<Ready for use / Needs fixes>
```

## Notes

- Test artifacts can be deleted after validation
- Or keep as example/reference plans
