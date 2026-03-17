---
description: Review a plan document for gaps, improvements, and refinements
argument-hint: <plan-path> [--depth quick|thorough] [--validate-schema on|off|strict]
allowed-tools: Read, Glob, Grep, WebSearch, WebFetch
---

# Review Plan

Analyze a plan or phase-plan document to identify schema violations, logic gaps, consistency issues, and opportunities to extend or refine the approach.

## Arguments

- `$1` - Path to the plan document (required). Can be:
  - Direct file path: `.claude/plans/merge-convert-skills/phase/0-pattern-extraction.md`
  - Plan directory: `.claude/plans/merge-convert-skills/` (reviews index.md + all phases)
  - Phase number: `phase/3` (relative to current plan context)
- `$ARGUMENTS` - Full argument string for parsing additional flags:
  - `--depth quick|thorough` - Review depth (default: `quick`)
  - `--validate-schema on|off|strict` - Schema validation mode (default: `on`)

## Flag Behavior

### --validate-schema

| Value | Behavior |
|-------|----------|
| `on` (default) | Warn on schema violations, continue review |
| `strict` | Fail review if any required element missing |
| `off` | Skip schema validation entirely |

### --depth

| Value | Behavior |
|-------|----------|
| `quick` (default) | Structure, schema, internal consistency |
| `thorough` | Adds external research, project standards, related plans |

## Workflow

### Step 1: Parse Input

1. Extract the plan path from `$1`
2. Parse flags from `$ARGUMENTS`:
   - `--depth thorough` or `--depth quick` (default: `quick`)
   - `--validate-schema on|off|strict` (default: `on`)
3. Determine review scope:
   - Single file: Review that document
   - Directory with `PLAN.md` or `index.md`: Review main + all phase docs
   - Phase reference: Locate within current plan context

### Step 2: Read Plan Content

1. Read the target plan document(s)
2. For directory reviews, read in order:
   - `PLAN.md` or `index.md` (main plan document)
   - `phase/*.md` (numbered order)
   - `analysis/*.md` (if exists)
3. Load schema reference from `docs/src/context/plan/schema.md`

### Step 3: Schema Validation

If `--validate-schema` is `on` or `strict`:

**PLAN.md Validation:**

| Element | Required | Check |
|---------|----------|-------|
| Title (H1) | Yes | First non-empty line starts with `#` |
| `## Objectives` | Yes | Section exists with table |
| Objectives table | Yes | Has `Measurable` column |
| `## Current State` | Yes | Section exists with table |
| Current State table | Yes | Has `Current`/`Target`/`Gap` columns |
| `## Phases` | Yes | Section exists with table |
| Phases table | Yes | Has `ID`, `Status`, `Dependencies` columns |
| `## Risks` | Yes | Section exists with table |
| Risks table | Yes | Has `Mitigation` column |

**Phase Document Validation (phase/*.md):**

| Element | Required | Check |
|---------|----------|-------|
| Title | Yes | Starts with `# Phase` |
| `**ID:**` | Yes | Matches PLAN.md phases table |
| `**Status:**` | Yes | Valid status value |
| `## Objective` | Yes | Section exists, non-empty |
| `## Success Criteria` | Yes | Checklist format (`- [ ]`), min 2 items |
| `## Deliverables` | Yes | Table with `Location` column |
| `## Files` | Yes | Has `**Create:**` and/or `**Modify:**` sections |

**Validation Behavior:**

- `--validate-schema=on`: Record violations as warnings, continue review
- `--validate-schema=strict`: Stop review and report violations if any required element missing
- `--validate-schema=off`: Skip this step entirely

Record all violations in the Schema Violations table for the report.

### Step 4: Logic Gap Analysis

Analyze the plan for logical coherence:

**Causal Gaps:**

- Steps that don't logically follow their predecessors
- Missing intermediate steps between major transitions
- Unstated assumptions that could fail
- Conclusions without supporting evidence

**Completeness Gaps:**

- Edge cases not handled
- Error scenarios not addressed
- Rollback procedures missing
- Recovery strategies undefined
- Missing validation/verification steps

**Dependency Gaps:**

- Circular dependencies between phases
- Missing prerequisites not listed as dependencies
- Parallel work that should be sequential (or vice versa)
- External dependencies not called out
- Blocking paths not identified

Classify each gap as Critical (blocks execution) or Important (degrades quality).

### Step 5: Consistency Checks

**Internal Consistency (always):**

| Check | Description | Violation Type |
|-------|-------------|----------------|
| Objectives ↔ Success Criteria | Phase success criteria roll up to plan objectives? | Logic gap |
| Deliverables ↔ Files | All deliverables listed in Files section? | Schema gap |
| Dependencies ↔ Phase Order | Phase order matches dependency graph? | Logic gap |
| Current ↔ Target | Gap column accurately reflects delta? | Data gap |
| IDs Match | Phase file IDs match PLAN.md table IDs? | Schema gap |
| Status Consistency | Phase statuses reflect actual progress? | Data gap |

**External Consistency (if --depth thorough):**

| Check | Source | Action |
|-------|--------|--------|
| Naming conventions | CLAUDE.md, project patterns | Glob for conventions |
| Directory structure | Project layout | Verify paths exist or are valid |
| Tool choices | brewfile, pyproject.toml | Check tools are available |
| Related plans | `.claude/plans/` | Check for conflicts/overlaps |
| Project standards | `.claude/rules/` | Verify compliance |

### Step 6: Identify Improvements

Look for opportunities to:

**Strengthen:**

- Vague requirements → concrete acceptance criteria
- Implicit assumptions → explicit preconditions
- General approaches → specific techniques
- Rough estimates → informed projections

**Extend:**

- Missing phases that would improve outcomes
- Additional deliverables that would add value
- Parallel work streams that could accelerate
- Automation opportunities

**Refine:**

- Overly complex steps → simpler alternatives
- Redundant sections → consolidated content
- Unclear language → precise terminology
- Missing examples → concrete illustrations

### Step 7: External Research (if --depth thorough)

If thorough review requested:

1. **Industry Patterns:**
   - Search for similar approaches in industry
   - Check for established patterns or frameworks
   - Look for relevant prior art

2. **Related Plans:**
   - Glob for other plans in `.claude/plans/`
   - Check for conflicts or overlaps
   - Identify integration points

3. **Project Context:**
   - Review CLAUDE.md for relevant guidelines
   - Check `.claude/rules/` for applicable rules
   - Verify alignment with project conventions

### Step 8: Generate Review Report

Output structured findings:

```markdown
# Plan Review: <Plan Name>

**Reviewed:** <date>
**Mode:** <quick|thorough>
**Schema Validation:** <on|strict|off>

## Summary

<1-2 sentence assessment of plan quality and readiness>

## Schema Violations

| Severity | Element | Location | Issue | Fix |
|----------|---------|----------|-------|-----|
| Critical | `## Objectives` | PLAN.md | Missing section | Add objectives table |
| Warning | `Measurable` column | Objectives table | Missing column | Add Measurable column |
| ... | ... | ... | ... | ... |

Schema compliance: X of Y required elements present

## Logic Gaps

### Critical (Blocks Execution)

| Gap | Location | Impact | Resolution |
|-----|----------|--------|------------|
| <gap description> | <file:section> | <what fails> | <how to fix> |

### Important (Degrades Quality)

| Gap | Location | Impact | Resolution |
|-----|----------|--------|------------|
| <gap description> | <file:section> | <what suffers> | <how to fix> |

## Consistency Issues

### Internal Consistency

| Check | Status | Issue | Resolution |
|-------|--------|-------|------------|
| Objectives ↔ Success | PASS/FAIL | <mismatch details> | <fix> |
| Deliverables ↔ Files | PASS/FAIL | <mismatch details> | <fix> |
| Dependencies ↔ Order | PASS/FAIL | <mismatch details> | <fix> |

### External Consistency

(Only shown if --depth thorough)

| Check | Status | Issue | Resolution |
|-------|--------|-------|------------|
| Naming conventions | PASS/FAIL | <deviation> | <fix> |
| Directory structure | PASS/FAIL | <invalid paths> | <fix> |
| Related plans | PASS/FAIL | <conflicts> | <fix> |

## Improvement Opportunities

### Strengthen

- <specific improvement with rationale>

### Extend

- <additional scope with value proposition>

### Refine

- <simplification with before/after>

## Questions for Clarification

1. <question that would help refine the plan>
2. ...

## Overall Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Schema Compliance | 1-5 | Required elements present, tables well-formed |
| Logic Soundness | 1-5 | Steps follow logically, no gaps in reasoning |
| Internal Consistency | 1-5 | Cross-references align, data matches |
| External Consistency | 1-5 | Follows project standards (N/A if quick) |
| Clarity | 1-5 | Unambiguous language, concrete details |

**Overall Score:** <average>/5

**Recommendation:** <Ready to Execute | Needs Minor Revisions | Needs Major Revisions | Requires Rethinking>

### Recommendation Criteria

| Recommendation | Criteria |
|----------------|----------|
| Ready to Execute | No critical gaps, avg score >= 4 |
| Needs Minor Revisions | No critical gaps, avg score 3-4 |
| Needs Major Revisions | Has critical gaps OR avg score < 3 |
| Requires Rethinking | Multiple critical gaps OR avg score < 2 |
```

## Examples

```bash
# Review a single phase
/context:plan:review .claude/plans/merge-convert-skills/phase/0-pattern-extraction.md

# Review entire plan (all phases)
/context:plan:review .claude/plans/merge-convert-skills/

# Thorough review with external research
/context:plan:review .claude/plans/merge-convert-skills/ --depth thorough

# Strict schema validation (fail on violations)
/context:plan:review .claude/plans/my-plan/ --validate-schema strict

# Skip schema validation (legacy plans)
/context:plan:review .claude/plans/old-plan/ --validate-schema off

# Review current plan context (if set)
/context:plan:review phase/3
```

## Review Criteria Reference

### Schema Compliance Scoring

| Score | Criteria |
|-------|----------|
| 5 | All required elements present, all tables well-formed |
| 4 | All required elements present, minor table issues |
| 3 | 1-2 required elements missing or malformed |
| 2 | Multiple required elements missing |
| 1 | Fundamental structure missing |

### Logic Soundness Scoring

| Score | Criteria |
|-------|----------|
| 5 | No gaps, all steps follow logically |
| 4 | Minor gaps, no critical issues |
| 3 | Some gaps that need addressing |
| 2 | Multiple gaps, execution at risk |
| 1 | Fundamental logic flaws |

### Internal Consistency Scoring

| Score | Criteria |
|-------|----------|
| 5 | All cross-references align perfectly |
| 4 | Minor misalignments, easily fixed |
| 3 | Some inconsistencies between sections |
| 2 | Significant misalignments |
| 1 | Contradictory information |

### External Consistency Scoring

| Score | Criteria |
|-------|----------|
| 5 | Fully aligned with project standards |
| 4 | Minor deviations from conventions |
| 3 | Some standard violations |
| 2 | Significant standards conflicts |
| 1 | Incompatible with project patterns |
| N/A | Not checked (quick mode) |

### Clarity Scoring

| Score | Criteria |
|-------|----------|
| 5 | Unambiguous, concrete, well-illustrated |
| 4 | Clear with minor ambiguities |
| 3 | Some vague sections |
| 2 | Multiple unclear areas |
| 1 | Pervasively vague or confusing |

## Notes

- Quick reviews focus on schema, logic, and internal consistency
- Thorough reviews add external consistency and research
- Schema violations are always Critical gaps when in strict mode
- Always provide actionable suggestions, not just criticisms
- Score dimensions honestly - inflated scores don't help
- Use `--validate-schema off` for legacy plans that predate the schema
