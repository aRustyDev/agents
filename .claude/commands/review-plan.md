---
description: Review a plan document for gaps, improvements, and refinements
argument-hint: <plan-path> [--depth quick|thorough]
allowed-tools: Read, Glob, Grep, WebSearch, WebFetch
---

# Review Plan

Analyze a plan or phase-plan document to identify gaps, areas for improvement, and opportunities to extend or refine the approach.

## Arguments

- `$1` - Path to the plan document (required). Can be:
  - Direct file path: `.claude/plans/merge-convert-skills/phase/0-pattern-extraction.md`
  - Plan directory: `.claude/plans/merge-convert-skills/` (reviews index.md + all phases)
  - Phase number: `phase/3` (relative to current plan context)
- `$ARGUMENTS` - Full argument string for parsing additional flags

## Workflow

### Step 1: Parse Input

1. Extract the plan path from `$1`
2. Check if `--depth thorough` is specified (default: `quick`)
3. Determine review scope:
   - Single file: Review that document
   - Directory with `index.md`: Review index + all phase docs
   - Phase reference: Locate within current plan context

### Step 2: Read Plan Content

1. Read the target plan document(s)
2. For directory reviews, read in order:
   - `index.md` (overview)
   - `phase/*.md` (numbered order)
   - `analysis/*.md` (if exists)

### Step 3: Analyze for Gaps

Review each section for:

**Completeness Gaps:**
- [ ] Missing success criteria
- [ ] Undefined deliverables
- [ ] Unspecified dependencies
- [ ] Missing effort estimates
- [ ] Unclear ownership/responsibility

**Technical Gaps:**
- [ ] Undefined terms or concepts
- [ ] Missing edge cases
- [ ] Unhandled error scenarios
- [ ] Missing validation steps
- [ ] Incomplete data schemas

**Process Gaps:**
- [ ] Missing phase transitions
- [ ] Unclear handoff points
- [ ] No rollback strategy
- [ ] Missing checkpoints
- [ ] No feedback loops

### Step 4: Identify Improvements

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

### Step 5: Cross-Reference (if --depth thorough)

If thorough review requested:

1. **External Research:**
   - Search for similar approaches in industry
   - Check for established patterns or frameworks
   - Look for relevant prior art

2. **Internal Consistency:**
   - Verify deliverables match success criteria
   - Check phase dependencies are satisfied
   - Ensure estimates align with scope

3. **Related Plans:**
   - Glob for other plans in `.claude/plans/`
   - Check for conflicts or overlaps
   - Identify integration points

### Step 6: Generate Review Report

Output structured findings:

```markdown
# Plan Review: <Plan Name>

## Summary
<1-2 sentence assessment of plan quality and readiness>

## Gaps Identified

### Critical (Must Address)
| Gap | Location | Impact | Suggested Fix |
|-----|----------|--------|---------------|
| ... | ... | ... | ... |

### Important (Should Address)
| Gap | Location | Impact | Suggested Fix |
|-----|----------|--------|---------------|
| ... | ... | ... | ... |

### Minor (Nice to Have)
| Gap | Location | Impact | Suggested Fix |
|-----|----------|--------|---------------|
| ... | ... | ... | ... |

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
| Completeness | 1-5 | ... |
| Clarity | 1-5 | ... |
| Feasibility | 1-5 | ... |
| Risk Coverage | 1-5 | ... |

**Recommendation:** <Ready to Execute | Needs Minor Revisions | Needs Major Revisions | Requires Rethinking>
```

## Examples

```bash
# Review a single phase
/review-plan .claude/plans/merge-convert-skills/phase/0-pattern-extraction.md

# Review entire plan (all phases)
/review-plan .claude/plans/merge-convert-skills/

# Thorough review with external research
/review-plan .claude/plans/merge-convert-skills/ --depth thorough

# Review current plan context (if set)
/review-plan phase/3
```

## Review Criteria Reference

### Success Criteria Checklist
- [ ] Measurable outcomes defined
- [ ] Clear done/not-done distinction
- [ ] Acceptance tests specified
- [ ] Stakeholder sign-off criteria

### Deliverables Checklist
- [ ] Output artifacts listed
- [ ] File locations specified
- [ ] Format/schema defined
- [ ] Quality standards stated

### Dependencies Checklist
- [ ] Prerequisites identified
- [ ] Blocking dependencies noted
- [ ] Optional dependencies marked
- [ ] External dependencies called out

### Risk Checklist
- [ ] Technical risks identified
- [ ] Mitigation strategies defined
- [ ] Fallback plans documented
- [ ] Risk owners assigned

## Notes

- Quick reviews focus on structure and obvious gaps
- Thorough reviews include external research and deep analysis
- Always provide actionable suggestions, not just criticisms
- Score dimensions honestly - inflated scores don't help
