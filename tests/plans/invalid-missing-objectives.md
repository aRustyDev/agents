# Example: Invalid Plan - Missing Objectives

This plan is **invalid** because it lacks the required `## Objectives` section.

**Expected Error:** `Missing ## Objectives section`

---

**Created:** 2025-03-15
**Owner:** Example Team

A plan to demonstrate schema validation errors.

## Current State

| Metric | Current Value | Target Value | Gap |
|--------|---------------|--------------|-----|
| Coverage | 50% | 100% | 50% |

## Phases

| ID | Name | Status | Dependencies |
|----|------|--------|--------------|
| phase-1 | Setup | pending | - |
| phase-2 | Implementation | pending | phase-1 |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Timeline slip | Medium | Medium | Buffer time |

## Notes

This plan is missing the `## Objectives` section which is required by the schema.

To fix, add:

```markdown
## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | <objective> | Yes | <metric> |
```
