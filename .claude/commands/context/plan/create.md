---
description: Create a new plan document with proper structure for multi-phase work
argument-hint: <plan-name> [--phases N] [--location .claude|.plans]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(ls:*), AskUserQuestion
---

# Create Plan

Create a structured plan document for multi-phase work with proper organization.

## Arguments

- `$1` - Plan name (lowercase, hyphenated). Example: `api-migration`
- `--phases` - Number of phases to scaffold (default: 3)
- `--location` - Where to create the plan:
  - `.claude` (default): `.claude/plans/<plan-name>/`
  - `.plans`: `.plans/<plan-name>/`

## Output

```text
<location>/<plan-name>/
├── index.md           # Plan overview and status
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
5. Determine target path
6. Check if plan exists — ask to overwrite or rename

### Step 2: Gather Plan Information

Use AskUserQuestion to collect:

1. **Plan Title**: Human-readable title
2. **Objective**: What does this plan accomplish? (2-3 sentences)
3. **Success Criteria**: How do we know it's done? (3-5 bullet points)
4. **Phase Names**: Name for each phase (or use defaults)

### Step 3: Create Directory Structure

```bash
mkdir -p "<location>/<plan-name>/phase"
```

### Step 4: Generate Index

Write `index.md`:

```markdown
# <Plan Title>

## Objective

<objective from user>

## Status

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| 1 | <phase-1-name> | pending | |
| 2 | <phase-2-name> | pending | |
| ... | ... | ... | |

## Success Criteria

- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## Phases

1. [<Phase 1 Name>](./phase/1-<slug>.md)
2. [<Phase 2 Name>](./phase/2-<slug>.md)
...

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Planning complete | | |
| Phase 1 complete | | |
| All phases complete | | |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| | | | |

## Notes

<any additional context>
```

### Step 5: Generate Phase Documents

For each phase, write `phase/N-<slug>.md`:

```markdown
# Phase N: <Phase Name>

## Objective

<What this phase accomplishes>

## Prerequisites

- [ ] <dependency from previous phase>

## Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Deliverables

| Deliverable | Status | Location |
|-------------|--------|----------|
| | pending | |

## Acceptance Criteria

- [ ] <criterion 1>
- [ ] <criterion 2>

## Notes

<phase-specific notes>
```

### Step 6: Report

```text
## Plan Created

| Field | Value |
|-------|-------|
| Plan | <plan-name> |
| Location | <path> |
| Phases | N |

**Files created:**
- <path>/index.md
- <path>/phase/1-<name>.md
- <path>/phase/2-<name>.md
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
```

## Plan Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in-progress` | Currently being worked |
| `blocked` | Waiting on dependency |
| `complete` | Finished and verified |
| `deferred` | Postponed |

## Related Commands

- `/context:plan:review` - Review plan for gaps
- `/string-beads` - Convert plan to beads issues
