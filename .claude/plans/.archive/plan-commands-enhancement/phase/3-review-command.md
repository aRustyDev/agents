# Phase 3: Review Command Enhancement

**ID:** `phase-3`
**Dependencies:** phase-1, phase-2
**Status:** complete
**Effort:** 3 hours

## Objective

Update `/context:plan:review` to validate schema, identify logic gaps, and check consistency.

## Success Criteria

- [ ] Schema validation reports missing/malformed sections
- [ ] Logic gap analysis identifies causal and completeness gaps
- [ ] Internal consistency checks cross-reference alignment
- [ ] External consistency checks project standards (--depth thorough)
- [ ] Review report includes all five dimensions:
  1. Schema Compliance
  2. Logic Soundness
  3. Internal Consistency
  4. External Consistency
  5. Clarity

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Enhanced review.md | `context/commands/context/plan/review.md` | Slash command |

## Files

**Create:**

- None

**Modify:**

- `context/commands/context/plan/review.md`

## Key Changes

### 1. Add Schema Validation Dimension

New Step 3: Schema Validation

```markdown
### Step 3: Schema Validation

If `--validate-schema` (default on):

1. Parse PLAN.md structure
2. Check each required element per SCHEMA.md
3. Record violations as Critical gaps

| Element | Required | Check |
|---------|----------|-------|
| Objectives table | Yes | Has Measurable column |
| Current State table | Yes | Has Current/Target/Gap columns |
| Phases table | Yes | Has ID, Dependencies columns |
| Phase Success Criteria | Yes | Checklist format |
| Phase Deliverables | Yes | Has Location column |
| Phase Files | Yes | Create/Modify sections |
```

### 2. Add Logic Gap Analysis

New Step 4: Logic Gap Analysis

**Causal Gaps:**

- Steps that don't logically follow predecessors
- Missing intermediate steps
- Unstated assumptions that could fail

**Completeness Gaps:**

- Edge cases not handled
- Error scenarios not addressed
- Rollback procedures missing

**Dependency Gaps:**

- Circular dependencies
- Missing prerequisites
- Unordered parallel work

### 3. Enhance Consistency Checks

**Internal Consistency:**

| Check | Description |
|-------|-------------|
| Objectives ↔ Success | Phase success criteria roll up to objectives? |
| Deliverables ↔ Files | All deliverables in Files section? |
| Dependencies ↔ Order | Phase order matches dependency graph? |
| Current ↔ Target | Gap column accurate? |

**External Consistency (--depth thorough):**

| Check | Source |
|-------|--------|
| Naming conventions | CLAUDE.md, project patterns |
| Directory structure | Project conventions |
| Tool choices | Project stack |
| Related plans | `.claude/plans/` conflicts |

### 4. Update Report Template

Add new sections:

- `## Schema Violations` table
- `## Logic Gaps` (Critical/Important)
- `## Consistency Issues` (Internal/External)
- Updated `## Overall Assessment` with 5 dimensions

### 5. Add Flag

`--validate-schema=on|off|strict`

- `on` (default): Warn on violations
- `strict`: Fail on violations
- `off`: Skip schema validation

## Tasks

- [ ] Add schema validation step
- [ ] Add logic gap analysis step
- [ ] Enhance consistency checks (internal + external)
- [ ] Update report template with new sections
- [ ] Add `--validate-schema` flag
- [ ] Update Overall Assessment to 5 dimensions

## Notes

- Schema violations → Critical gaps
- Logic gaps → Critical or Important based on impact
- External consistency only runs with `--depth thorough`
