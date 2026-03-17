# Example: Invalid Plan - Missing Phases

This plan is **invalid** because it lacks the required `## Phases` section.

**Expected Error:** `Missing ## Phases section`

---

**Created:** 2025-03-15
**Owner:** Example Team

A plan to demonstrate schema validation errors.

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Complete the work | Yes | All tasks done |

## Current State

| Metric | Current Value | Target Value | Gap |
|--------|---------------|--------------|-----|
| Progress | 0% | 100% | 100% |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Unknown scope | High | High | Discovery phase |

## Notes

This plan is missing the `## Phases` section which is required by the schema.

A plan without phases has no structure for tracking progress or dependencies.

To fix, add:

```markdown
## Phases

| ID | Name | Status | Dependencies |
|----|------|--------|--------------|
| phase-1 | <name> | pending | - |
```
