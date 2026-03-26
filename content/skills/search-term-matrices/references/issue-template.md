# Issue Reporting Template

One template, two labels. Use this for both bugs and improvement suggestions found while using the search-term-matrices skill.

## Template

```markdown
---
title: "[search-term-matrices] CONCISE_TITLE_HERE"
labels: ["search-term-matrices", "TYPE_LABEL"]
---

## Type

- [ ] bug — something is wrong (incorrect operators, broken workflow, inaccurate guidance)
- [ ] improvement — something could be better (missing engine, unclear instruction, new feature)

## Severity

- [ ] blocks-work — cannot complete research planning without a workaround
- [ ] degrades-quality — produces a matrix but with suboptimal or incorrect results
- [ ] nice-to-have — minor friction, cosmetic issue, or documentation gap

## Summary

[1-2 sentences describing the problem or improvement. Be specific.]

## Steps to Reproduce (bugs only)

1. [What research question were you building a matrix for?]
2. [Which step of the workflow were you on?]
3. [What did you expect to happen?]
4. [What actually happened?]

## Context

**Skill file:** [which file — SKILL.md or references/specific-file.md]
**Section:** [which section of that file]
**Line or content:** [quote or paraphrase the relevant content]

## Suggested Fix (if known)

[What should change? Include corrected operators, updated syntax, or revised wording if you know the fix.]
```

## Labels

| Label | When to use |
|-------|-------------|
| `bug` | Something in the skill is factually wrong, produces errors, or contradicts observed behavior. Examples: an operator that does not work on the listed engine, a workflow step that produces no output, grading criteria that do not match real results. |
| `improvement` | Something could be added, clarified, or reorganized to make the skill more effective. Examples: a missing search engine, an unclear instruction, a new operator that an engine added, a decomposition pattern that should be documented. |

## Severity Levels

| Severity | Definition | Examples |
|----------|------------|---------|
| **blocks-work** | Cannot complete research planning without a workaround. The skill actively prevents you from producing a usable matrix. | Core workflow step is missing or contradictory; the matrix template has a structural error; a required reference file is absent. |
| **degrades-quality** | Can produce a matrix, but it is suboptimal or contains incorrect information. You had to work around the issue or override the skill's guidance. | An engine's operator syntax is wrong (queries fail); grading rubric does not account for a common result pattern; decomposition guidance causes over-splitting. |
| **nice-to-have** | Minor friction that does not affect matrix quality. Cosmetic issues, small documentation gaps, or feature requests. | A tip that could be added for an engine; a typo in an example; a new paid service that should be listed. |

## Progressive Disclosure

Not every issue needs every field. Match detail to severity:

### blocks-work

Fill in all fields. These issues prevent productive use of the skill and need full context to diagnose and fix.

### degrades-quality

Fill in: Type, Severity, Summary, Context, and Suggested Fix (if known). Steps to Reproduce are helpful but optional if the problem is clearly described.

### nice-to-have

Fill in: Type, Severity, Summary. Context is helpful. Steps to Reproduce and Suggested Fix are optional.

## Filing Process

1. Draft the issue using the template above
2. Present it to the user for review — agents do not file issues autonomously
3. The user decides whether to file, edit, or discard
4. If filed, target repository: `github.com/arustydev/agents`
5. Apply both the `search-term-matrices` label and the type label (`bug` or `improvement`)
