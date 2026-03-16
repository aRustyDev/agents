---
description: Refine a plan based on review feedback or new information
argument-hint: <plan-path> [--apply-review]
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion
---

# Refine Plan

Update and improve a plan document based on review feedback or new information.

## Arguments

- `$1` - Path to plan (directory or index.md)
- `--apply-review` - Automatically apply suggestions from most recent review

## Workflow

### Step 1: Load Plan

1. Read plan index.md
2. Read all phase documents
3. Check for existing review report in same directory

### Step 2: Identify Changes Needed

If `--apply-review` and review exists:

- Parse review report for Critical and Warning items
- Create change list from suggestions

Otherwise, use AskUserQuestion:

1. What aspects need refinement?
   - Scope (add/remove phases)
   - Detail (flesh out tasks)
   - Clarity (improve descriptions)
   - Dependencies (update prerequisites)

### Step 3: Apply Refinements

For each change:

1. Edit the relevant file
2. Update cross-references if needed
3. Update index.md status table

### Step 4: Validate

1. Check all links still work
2. Verify phase numbering is sequential
3. Confirm no orphaned references

### Step 5: Report

```text
## Plan Refined

| Field | Value |
|-------|-------|
| Plan | <name> |
| Changes | N |

**Modifications:**
- <change 1>
- <change 2>

**Next steps:**
1. Run `/context:plan:review` to verify improvements
```

## Examples

```bash
# Interactive refinement
/context:plan:refine .claude/plans/api-migration/

# Apply review suggestions automatically
/context:plan:refine .claude/plans/api-migration/ --apply-review
```

## Related Commands

- `/context:plan:review` - Review plan for gaps
- `/context:plan:create` - Create new plan
