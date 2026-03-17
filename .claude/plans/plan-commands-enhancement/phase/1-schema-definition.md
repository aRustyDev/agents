# Phase 1: Schema Definition

**ID:** `phase-1`
**Dependencies:** phase-0
**Status:** complete
**Effort:** 2 hours

## Objective

Define the canonical plan schema that all three commands will enforce.

## Success Criteria

- [x] Schema spec documented in markdown
- [x] Validation rules defined for each required element
- [x] Example valid and invalid plans created
- [x] Schema allows optional sections without failing

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Schema specification | `context/commands/context/plan/SCHEMA.md` | Markdown |
| Valid example | `context/commands/context/plan/examples/valid-plan.md` | Markdown |
| Invalid examples | `context/commands/context/plan/examples/invalid-*.md` | Markdown |

## Files

**Create:**

- `context/commands/context/plan/SCHEMA.md`
- `context/commands/context/plan/examples/valid-plan.md`
- `context/commands/context/plan/examples/invalid-missing-objectives.md`
- `context/commands/context/plan/examples/invalid-missing-phases.md`

**Modify:**

- None

## Schema Specification

### Required Top-Level Elements

| Element | Format | Validation |
|---------|--------|------------|
| `# Title` | H1 heading | Must exist |
| `## Objectives` | Table | Must have `Measurable` column, all values `Yes` |
| `## Current State` | Table | Must have `Current Value`, `Target Value`, `Gap` columns |
| `## Phases` | Table | Must have `ID`, `Status`, `Dependencies` columns |
| `## Risks` | Table | Must have `Mitigation` column |

### Required Per-Phase Elements

| Element | Format | Validation |
|---------|--------|------------|
| `## Success Criteria` | Checklist | At least 2 items, measurable language |
| `## Deliverables` | Table | Must have `Location` column |
| `## Files` | Sections | `Create:` and `Modify:` subsections |

### Optional Elements

| Element | Format | Notes |
|---------|--------|-------|
| `## Timeline` | Table | Recommended but not required |
| `## Notes` | Prose | Freeform |
| `## Related` | Links | Cross-references |

### Validation Modes

| Mode | Behavior |
|------|----------|
| `strict` | Fail on any missing required element |
| `warn` | Log warnings but don't fail |
| `off` | Skip schema validation |

## Tasks

- [x] Draft SCHEMA.md with all validation rules
- [x] Create valid example plan following schema
- [x] Create 2-3 invalid examples showing common failures
- [x] Document validation modes and flags

## Notes

- Schema should be lenient enough for quick drafts
- `--validate-schema=strict` for CI/formal plans
- Default mode: `warn` (inform but don't block)
