---
description: Refine a plan based on review feedback or new information
argument-hint: <plan-path> [--fix-schema] [--apply-review] [--interactive]
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion
---

# Refine Plan

Update and improve a plan document based on review feedback, schema violations, or new information.

**Schema Reference:** See `docs/src/content/plan/schema.md` for plan structure requirements.

## Arguments

- `$1` - Path to plan (directory or PLAN.md/index.md)
- `--fix-schema` - Auto-fix missing required sections with placeholders
- `--apply-review` - Apply suggestions from most recent review report
- `--interactive` - Prompt for each change (default if no flags provided)

## Workflow

### Step 1: Load Plan

1. Locate main plan document (`PLAN.md` or `index.md`)
2. Read all phase documents from `phase/*.md`
3. Check for review report:
   - `<plan-dir>/REVIEW.md`
   - Most recent `<plan-dir>/review-*.md`
4. Parse plan structure into working model

### Step 2: Determine Refinement Mode

| Flags | Mode | Behavior |
|-------|------|----------|
| `--fix-schema` | Schema Fix | Auto-add missing required elements |
| `--apply-review` | Review Apply | Parse and apply review findings |
| `--fix-schema --apply-review` | Combined | Fix schema first, then apply review |
| None or `--interactive` | Interactive | Prompt user for changes |

### Step 3: Schema Fixes (if --fix-schema)

Check for and auto-fix missing required elements:

#### PLAN.md Fixes

| Missing Element | Auto-Fix Template |
|-----------------|-------------------|
| `## Objectives` table | Add table with placeholder row, Measurable column |
| `## Current State` table | Add table with TBD values for Current/Target/Gap |
| `## Phases` table | Add table from existing phase files, add Dependencies column |
| `## Risks` table | Add table with "None identified" row and Mitigation column |
| Metadata header | Add Created/Updated/Owner with TBD values |

**Objectives Template:**

```markdown
## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | TBD | Yes | TBD |
```

**Current State Template:**

```markdown
## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| TBD | TBD | TBD | TBD |
```

**Risks Template:**

```markdown
## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| None identified | - | - | - |
```

#### Phase File Fixes

| Missing Element | Auto-Fix Template |
|-----------------|-------------------|
| Metadata block | Add ID, Dependencies, Status, Effort placeholders |
| `## Success Criteria` | Add checklist with 2 placeholder items |
| `## Deliverables` table | Add table with Location column |
| `## Files` section | Add Create/Modify subsections with "None" |

**Success Criteria Template:**

```markdown
## Success Criteria

- [ ] TBD - Define measurable criterion 1
- [ ] TBD - Define measurable criterion 2
```

**Deliverables Template:**

```markdown
## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| TBD | TBD | TBD |
```

**Files Template:**

```markdown
## Files

**Create:**

- None (TBD)

**Modify:**

- None (TBD)
```

### Step 4: Apply Review (if --apply-review)

Locate and parse review report, then apply fixes by category:

#### Review Categories → Actions

| Review Section | Action |
|----------------|--------|
| **Schema Violations** | Apply schema fixes (same as --fix-schema) |
| **Critical Logic Gaps** | Add as TODO items in relevant phase's Tasks section |
| **Important Logic Gaps** | Add to Risks table with mitigation "TBD" |
| **Internal Consistency Issues** | Fix cross-references, update misaligned sections |
| **External Consistency Issues** | Log as notes (require manual intervention) |
| **Clarity Improvements** | Apply text changes where unambiguous |

#### Parsing Review Report

Look for these patterns in review:

```markdown
## Schema Violations

| ... | Element | ... | Fix |
→ Apply fix from "Fix" column

## Logic Gaps

### Critical

| Gap | Location | ... | Fix |
→ Add to phase Tasks: "- [ ] TODO: <Fix>"

## Consistency Issues

### Internal

| Issue | Elements | Fix |
→ Apply fix from "Fix" column
```

### Step 5: Interactive Refinement (if --interactive or no flags)

Use AskUserQuestion to prompt for changes:

#### Question 1: Refinement Focus

- Scope (add/remove phases)
- Detail (flesh out tasks/deliverables)
- Clarity (improve descriptions)
- Schema (fix missing sections)
- Dependencies (update prerequisites)

#### Question 2: Specific Changes

Based on focus area, prompt for details.

### Step 6: Apply Changes

For each change identified:

1. **Structural changes** (add section, add table column):
   - Edit PLAN.md or phase file
   - Preserve surrounding content

2. **Content changes** (fix wording, add values):
   - Edit specific section
   - Use Edit tool for precision

3. **Cross-reference updates**:
   - Update phases table in PLAN.md if phase added/removed
   - Update phase file metadata if dependencies change
   - Fix internal links

### Step 7: Validate Result

After all changes applied:

| Check | Action if Failed |
|-------|------------------|
| Schema validation | Log remaining violations |
| Internal links resolve | Log broken links |
| Phase numbering sequential | Log gaps |
| No orphaned references | Log orphans |
| Dependencies acyclic | Log cycles |

### Step 8: Report

```markdown
## Plan Refined

| Field | Value |
|-------|-------|
| Plan | <plan-name> |
| Mode | <fix-schema / apply-review / interactive> |
| Changes Applied | N |
| Schema Valid | ✓ / ✗ (N remaining issues) |

### Changes Made

**Schema Fixes:**

- Added `## Objectives` table to PLAN.md
- Added `## Files` section to phase/2-implementation.md
- Added `## Files` section to phase/3-testing.md

**From Review:**

- Added risk: "Timeline slip" with mitigation TBD
- Added TODO to phase-2: "Handle edge case X"
- Fixed: "improve performance" → "reduce p99 latency by 30%"

**Interactive:**

- Updated phase-1 dependencies
- Added phase-4: Deployment

### Remaining Issues

| Issue | Location | Action Needed |
|-------|----------|---------------|
| TBD value | Objectives row 1 | Fill in objective text |
| TBD value | Current State | Fill in metrics |
| Placeholder | phase-2 Deliverables | Specify actual deliverables |

### Next Steps

1. Fill in TBD/placeholder values
2. Run `/context:plan:review` to verify improvements
3. Convert to issues with `/beads:string` when ready
```

## Examples

```bash
# Auto-fix schema violations
/context:plan:refine .claude/plans/api-migration/ --fix-schema

# Apply review findings automatically
/context:plan:refine .claude/plans/api-migration/ --apply-review

# Fix schema AND apply review (schema first, then review)
/context:plan:refine .claude/plans/api-migration/ --fix-schema --apply-review

# Interactive refinement (default)
/context:plan:refine .claude/plans/api-migration/

# Explicit interactive mode
/context:plan:refine .claude/plans/api-migration/ --interactive
```

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No review file found | Log warning, skip --apply-review |
| Plan already valid | Report "No schema fixes needed" |
| Review has no actionable items | Report "No review items to apply" |
| Conflicting flags | --fix-schema runs first, then --apply-review |
| Can't parse review format | Log warning, skip unparseable sections |

## Placeholder Values

Auto-fixes use these placeholder values that must be filled in manually:

| Placeholder | Meaning |
|-------------|---------|
| `TBD` | To Be Determined - requires user input |
| `None` | Explicitly no items (valid if intentional) |
| `None identified` | No risks identified yet |
| `- [ ] TBD - Define...` | Placeholder task needing definition |

## Related Commands

- `/context:plan:review` - Review plan for gaps (generates review report)
- `/context:plan:create` - Create new schema-compliant plan
- `docs/src/content/plan/schema.md` - Full schema specification
