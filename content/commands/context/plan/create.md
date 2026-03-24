---
description: Create a new plan document with proper structure for multi-phase work
argument-hint: <plan-name> [--phases N] [--location .claude|.plans] [--minimal]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(ls:*), AskUserQuestion
---

# Create Plan

Create a structured plan document for multi-phase work with proper organization. Generated plans comply with the schema defined in `docs/src/content/plan/schema.md`.

## Arguments

- `$1` - Plan name (lowercase, hyphenated). Example: `api-migration`
- `--phases` - Number of phases to scaffold (default: 3)
- `--location` - Where to create the plan:
  - `.claude` (default): `.claude/plans/<plan-name>/`
  - `.plans`: `.plans/<plan-name>/`
- `--minimal` - Skip interactive questions, use placeholder values

## Output

```text
<location>/<plan-name>/
├── PLAN.md            # Unified plan (schema-compliant)
└── phase/
    ├── 1-<name>.md    # Phase documents
    ├── 2-<name>.md
    └── ...
```

## Workflow

### Step 1: Parse and Validate

1. Extract plan name from `$1`
2. Validate format: `^[a-z][a-z0-9-]{0,46}[a-z0-9]$`
3. Parse `--phases` (default: 3)
4. Parse `--location` (default: `.claude`)
5. Parse `--minimal` flag (default: false)
6. Determine target path
7. Check if plan exists — ask to overwrite or rename

### Step 2: Gather Plan Information

Skip this step if `--minimal` flag is set (use placeholders instead).

Use AskUserQuestion to collect:

1. **Plan Title**: Human-readable title
2. **Objectives**: What does this plan accomplish? (Ask for 2-3 measurable objectives)
   - Prompt: "List 2-3 objectives. For each, include how you will measure success. Example: 'Reduce API latency to <100ms (measured via p95 metrics)'"
3. **Current State Metrics**: What is the current state?
   - Prompt: "List 1-3 metrics with current values and target values. Example: 'API latency: Current=350ms, Target=100ms'"
4. **Phase Names**: Name for each phase (or use defaults like "Setup", "Implementation", "Validation")
5. **Key Risks**: What could go wrong?
   - Prompt: "List 1-2 potential risks and how you would mitigate them."

### Step 3: Create Directory Structure

```bash
mkdir -p "<location>/<plan-name>/phase"
```

### Step 4: Generate PLAN.md

Write `PLAN.md`:

```markdown
# <Plan Title>

**Created:** <YYYY-MM-DD>
**Updated:** <YYYY-MM-DD>
**Owner:** <user or team>

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | <objective 1> | Yes | <how to measure> |
| 2 | <objective 2> | Yes | <how to measure> |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| <metric 1> | <current value> | <target value> | <delta> |
| <metric 2> | <current value> | <target value> | <delta> |

## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-1 | <phase-1-name> | pending | - | <summary> |
| phase-2 | <phase-2-name> | pending | phase-1 | <summary> |
| phase-3 | <phase-3-name> | pending | phase-2 | <summary> |

### Phase Details

1. [Phase 1: <Phase 1 Name>](./phase/1-<slug>.md)
2. [Phase 2: <Phase 2 Name>](./phase/2-<slug>.md)
3. [Phase 3: <Phase 3 Name>](./phase/3-<slug>.md)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| <risk 1> | Medium | Medium | <mitigation strategy> |
| <risk 2> | Low | High | <mitigation strategy> |

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Planning complete | | |
| Phase 1 complete | | |
| All phases complete | | |

## Rollback Strategy

<describe how to revert changes if needed>

## Notes

<any additional context>
```

### Step 5: Generate Phase Documents

For each phase, write `phase/N-<slug>.md`:

```markdown
# Phase N: <Phase Name>

**ID:** `phase-N`
**Dependencies:** <phase-ids or None>
**Status:** pending
**Effort:** <estimate or TBD>

## Objective

<What this phase accomplishes - 1-2 sentences>

## Success Criteria

- [ ] <measurable criterion 1>
- [ ] <measurable criterion 2>
- [ ] <measurable criterion 3>

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| <deliverable 1> | `<file path>` | <type> |
| <deliverable 2> | `<file path>` | <type> |

## Files

**Create:**
- `<path/to/new/file>` (or "None" if no files to create)

**Modify:**
- `<path/to/existing/file>` (or "None" if no files to modify)

## Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Notes

<phase-specific notes>
```

### Step 6: Validate Output

Before reporting, validate the generated plan against the schema:

1. **PLAN.md Validation:**
   - [ ] Has `## Objectives` section with table containing `Measurable` column
   - [ ] Has `## Current State` section with `Current`, `Target`, `Gap` columns
   - [ ] Has `## Phases` section with `ID`, `Dependencies`, `Status` columns
   - [ ] Has `## Risks` section with `Mitigation` column
   - [ ] At least 1 objective, 1 metric, 1 phase, 1 risk

2. **Phase Document Validation (for each phase):**
   - [ ] Has metadata block with `**ID:**`, `**Dependencies:**`, `**Status:**`
   - [ ] Has `## Objective` section (non-empty)
   - [ ] Has `## Success Criteria` as checklist with 2+ items
   - [ ] Has `## Deliverables` table with `Location` column
   - [ ] Has `## Files` section with `**Create:**` and/or `**Modify:**` subsections

3. **Record validation result:**
   - `PASS` - All required elements present
   - `WARN` - Optional elements missing (still valid)
   - `FAIL` - Required elements missing (should not happen with this command)

### Step 7: Report

```text
## Plan Created

| Field | Value |
|-------|-------|
| Plan | <plan-name> |
| Location | <path> |
| Phases | N |
| Schema | PASS |

**Files created:**
- <path>/PLAN.md
- <path>/phase/1-<name>.md
- <path>/phase/2-<name>.md
...

**Schema validation:**
- PLAN.md: PASS (all required sections present)
- Phase 1: PASS
- Phase 2: PASS
...

**Next steps:**
1. Review and refine phase details
2. Run `/context:plan:review <path>` to check for gaps
3. Convert to beads issues with `/string-beads <path>`
```

## Examples

```bash
# Create a 3-phase plan in .claude/plans/
/context:plan:create api-migration

# Create a 5-phase plan
/context:plan:create database-refactor --phases 5

# Create in .plans/ directory
/context:plan:create feature-rollout --location .plans

# Quick scaffolding without interactive questions
/context:plan:create quick-fix --minimal
```

## Plan Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in-progress` | Currently being worked |
| `blocked` | Waiting on dependency |
| `complete` | Finished and verified |
| `skipped` | Intentionally skipped |

## Placeholder Values (for --minimal mode)

When `--minimal` is used, populate with these placeholders:

| Field | Placeholder |
|-------|-------------|
| Objectives | "Define objective (make measurable)" |
| Current State Metric | "Metric TBD" |
| Current/Target Values | "TBD" |
| Gap | "-" |
| Risk | "None identified" |
| Mitigation | "N/A" |
| Phase Names | "Setup", "Implementation", "Validation" |
| Deliverables | "TBD" |
| Files Create/Modify | "None" |

## Related Commands

- `/context:plan:review` - Review plan for gaps and schema compliance
- `/context:plan:refine` - Refine plan with AI assistance
- `/string-beads` - Convert plan to beads issues
