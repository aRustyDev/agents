# Plan Schema Specification

**Version:** 1.0.0
**Status:** Active

This document defines the canonical structure for plan documents used by `/context:plan:create`, `/context:plan:review`, and `/context:plan:refine` commands.

## Overview

A compliant plan consists of:

- **PLAN.md** (or index.md) - Main plan document with objectives, phases, and risks
- **phase/*.md** - Individual phase documents with tasks and deliverables

## File Naming

| File | Purpose | Required |
|------|---------|----------|
| `PLAN.md` | Main plan document | Yes (or `index.md`) |
| `phase/N-<name>.md` | Phase detail document | Yes (one per phase) |

## PLAN.md Structure

### Required Elements

#### 1. Title (H1)

```markdown
# <Plan Title>
```

**Validation:** Must be first non-empty line, must start with `#`

#### 2. Metadata Header (Optional but Recommended)

```markdown
**Created:** YYYY-MM-DD
**Updated:** YYYY-MM-DD
**Owner:** <name or team>
```

**Validation:** If present, dates must be ISO format

#### 3. Objectives Table

```markdown
## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | <statement> | Yes | <how to measure> |
```

**Validation:**

- Section heading `## Objectives` must exist
- Table must have `Measurable` column
- All `Measurable` values should be `Yes`
- At least 1 objective required

#### 4. Current State Table

```markdown
## Current State

| Metric | Current Value | Target Value | Gap |
|--------|---------------|--------------|-----|
| <metric> | <current> | <target> | <delta> |
```

**Validation:**

- Section heading `## Current State` must exist
- Table must have columns: `Current Value` (or `Current`), `Target Value` (or `Target`), `Gap`
- At least 1 metric required

#### 5. Phases Table

```markdown
## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-1 | <name> | pending | - | <summary> |
| phase-2 | <name> | pending | phase-1 | <summary> |
```

**Validation:**

- Section heading `## Phases` must exist
- Table must have columns: `ID`, `Status`, `Dependencies`
- `ID` must match pattern: `phase-N` or slug format
- `Status` must be one of: `pending`, `in-progress`, `complete`, `blocked`, `skipped`
- At least 1 phase required

#### 6. Risks Table

```markdown
## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| <risk description> | High/Medium/Low | High/Medium/Low | <strategy> |
```

**Validation:**

- Section heading `## Risks` must exist
- Table must have `Mitigation` column
- At least 1 risk required (use "None identified" if truly none)

### Optional Elements

#### Timeline Table

```markdown
## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| <milestone> | <date> | <date or empty> |
```

#### Rollback Strategy

```markdown
## Rollback Strategy

<prose description of how to revert if needed>
```

#### Notes

```markdown
## Notes

<freeform prose>
```

## Phase Document Structure (phase/*.md)

### Required Elements

#### 1. Title and Metadata

```markdown
# Phase N: <Phase Name>

**ID:** `phase-N`
**Dependencies:** <phase-ids or None>
**Status:** pending
**Effort:** <estimate>
```

**Validation:**

- Title must start with `# Phase`
- `**ID:**` must match PLAN.md phases table
- `**Status:**` must be valid status value

#### 2. Objective

```markdown
## Objective

<1-2 sentence description of what this phase accomplishes>
```

**Validation:** Section must exist, non-empty

#### 3. Success Criteria

```markdown
## Success Criteria

- [ ] <measurable criterion 1>
- [ ] <measurable criterion 2>
```

**Validation:**

- Section must exist
- Must be checklist format (`- [ ]` or `- [x]`)
- At least 2 criteria required
- Criteria should be measurable (avoid vague language)

#### 4. Deliverables Table

```markdown
## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| <name> | <file path> | <type> |
```

**Validation:**

- Section must exist
- Table must have `Location` column
- At least 1 deliverable required

#### 5. Files Section

```markdown
## Files

**Create:**

- `<path/to/new/file>`

**Modify:**

- `<path/to/existing/file>`
```

**Validation:**

- Section must exist
- Must have `**Create:**` and/or `**Modify:**` subsections
- At least one file operation required (or explicitly state "None")

### Optional Elements

#### Tasks

```markdown
## Tasks

- [ ] <task 1>
- [ ] <task 2>
```

#### Notes

```markdown
## Notes

<phase-specific notes>
```

## Validation Modes

| Mode | Flag | Behavior |
|------|------|----------|
| **strict** | `--validate-schema=strict` | Fail on any missing required element |
| **warn** | `--validate-schema=warn` (default) | Log warnings, continue execution |
| **off** | `--validate-schema=off` | Skip all schema validation |

### When to Use Each Mode

| Use Case | Recommended Mode |
|----------|------------------|
| Creating new plans | `strict` (enforced by `/context:plan:create`) |
| Reviewing existing plans | `warn` (default) |
| Legacy/non-standard plans | `off` |
| CI/automation | `strict` |

## Error Messages

### Critical (Blocks in strict mode)

| Error | Cause | Fix |
|-------|-------|-----|
| `Missing ## Objectives section` | No objectives table | Add objectives table |
| `Missing ## Phases section` | No phases table | Add phases table |
| `Objectives table missing Measurable column` | Column not found | Add Measurable column |
| `Phase file missing Success Criteria` | No criteria section | Add success criteria checklist |

### Warning (Logged in warn mode)

| Warning | Cause | Fix |
|---------|-------|-----|
| `Objective N has Measurable=No` | Not all objectives measurable | Make measurable or document why |
| `Phase file missing Files section` | No file operations documented | Add Files section |
| `Risk table missing Mitigation column` | Column not found | Add Mitigation column |
| `Current State Gap column empty` | Gap not calculated | Calculate gap values |

## Examples

See `tests/plans/` for example plans:

- `valid-plan.md` - Fully compliant plan
- `invalid-missing-objectives.md` - Missing required section
- `invalid-missing-phases.md` - Missing required section
- `invalid-phase-missing-files.md` - Phase missing Files section

## Compatibility

### Supported Alternatives

| Standard | Alternative | Notes |
|----------|-------------|-------|
| `PLAN.md` | `index.md` | Both accepted as main document |
| `## Objectives` | `## Goals` | Goals accepted, warning logged |
| `Current Value` | `Current` | Short form accepted |
| `Target Value` | `Target` | Short form accepted |

### Migration from Legacy Plans

Plans created before this schema can be migrated using:

```bash
/context:plan:refine <path> --fix-schema
```

This adds missing required sections with placeholder values.
