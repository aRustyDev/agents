---
paths:
  - .claude/plans/**
---

# Plans → Issues Lifecycle

## Principle

All plans must become GitHub issues. Plans are drafts; issues are the system of record.

## Lifecycle

```
Draft Plan (.claude/plans/<name>/index.md)
  ↓ Decompose into phases
Phase Plans (.claude/plans/<name>/phase/01-*.md)
  ↓ GAP review (Gaps, Areas for refinement, Potential extensions)
Refined Phase Plans
  ↓ Convert to issues
Parent Issue (from index.md)
  ├── Child Issue (from phase/01-*.md)
  ├── Child Issue (from phase/02-*.md)
  └── Child Issue (from phase/03-*.md)
  ↓ Link to milestones and projects
Tracked Work
  ↓ Implementation on feature branches
Done
```

## Converting Plans to Issues

1. **Parent issue** from `index.md`:
   - Title: Plan name
   - Body: Overview, architecture, links to child issues
   - Labels: `needs plan` → `enhancement`
   - Milestone: version target

2. **Child issues** from each `phase/*.md`:
   - Title: Phase name
   - Body: Scope, deliverables, acceptance criteria
   - Link: `Parent: #<parent-issue>`
   - Dependencies: `Blocked by: #<prior-phase>`

3. **Update plan files** with issue numbers once created

## GAP Review (Required Before Issues)

Before any plan becomes an issue, review for:

- **G**aps: Missing pieces, uncovered scenarios
- **A**reas for refinement: Vague requirements, unclear acceptance criteria
- **P**otential extensions: Future considerations, optional enhancements

Document findings in the plan's `index.md` under "GAP Review Notes".

## Issue Updates

- Update issue body as work progresses
- Check off acceptance criteria in issue body
- Close child issues when phase completes
- Close parent issue when all children are closed

## ROADMAP.md

Every plan must include a `ROADMAP.md` that:
- Links to issues, milestones, and projects
- Describes expected version bumps (major/minor/patch)
- Tracks MVP timeline
