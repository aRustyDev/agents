---
name: blog:research:spec:review
description: Evaluate research plan quality against checklist
argument-hint: <path> [--approve]
arguments:
  - name: path
    description: Path to the research plan to review
    required: true
  - name: approve
    description: Auto-approve if only warnings remain (no fails)
    required: false
  - name: no-approve
    description: Evaluate only, never set approved status
    required: false
---

# Research Spec Review

Evaluate a research plan against the quality checklist and optionally approve it.

## Prerequisites

- Research plan exists at specified path
- Research plan has `type: research-plan` in frontmatter

## Behavior

### 1. Load Research Plan

```
Read the research plan at {{path}}
Extract project path from research plan location
Load project index.md
```

### 2. Load Review Checklist

Load checklist from: `context/plugins/blog-workflow/.templates/review-checklists/research-plan.md`

### 3. Evaluate Each Criterion

For each checklist item, evaluate as:

- **pass** `[x]` - Criterion fully met
- **warn** `[~]` - Criterion partially met or could be improved
- **fail** `[ ]` - Criterion not met, blocks approval

#### Scope Clarity

- [ ] Primary research question is clearly defined
- [ ] Secondary questions support the primary question
- [ ] Boundaries established (what's in/out of scope)

#### Methodology Quality

- [ ] Source types identified with purpose
- [ ] Search strategy is specific and actionable
- [ ] Quality criteria defined for source selection

#### Feasibility

- [ ] Time estimate is reasonable for scope
- [ ] Required tools/access are available
- [ ] Expertise gaps identified (if any)

#### Alignment

- [ ] Research questions trace back to project plan goals
- [ ] Expected outputs match what content phase needs

### 4. Append Review Section

Remove any existing `## Review` section from the artifact, then append:

```markdown
## Review

**Reviewed**: {{ISO 8601 timestamp}}
**Result**: {{pass|warn|fail}}

### Scope Clarity
- [x] Primary question clearly defined — pass
- [x] Secondary questions support primary — pass
- [~] Boundaries established — warn: out-of-scope could be more explicit

### Methodology Quality
- [x] Source types identified — pass
- [x] Search strategy actionable — pass
- [x] Quality criteria defined — pass

### Feasibility
- [x] Time estimate reasonable — pass
- [x] Tools available — pass
- [x] Expertise gaps identified — pass

### Alignment
- [x] Questions trace to project goals — pass
- [x] Outputs match content needs — pass

**Summary**: {{pass_count}} pass, {{warn_count}} warn, {{fail_count}} fail

{{If warnings or fails}}

### Action Items
1. {{specific action to address issue}}
2. {{specific action to address issue}}
{{/If}}
```

### 5. Determine Approval

| Condition | `--approve` flag | `--no-approve` flag | Default |
|-----------|------------------|---------------------|---------|
| All pass | approved | in-review | Prompt user |
| Warns only | approved | in-review | Prompt user |
| Any fail | in-review | in-review | in-review |

If prompting user: "Review complete with {{summary}}. Approve this research plan? (yes/no)"

### 6. Update Status

If approved:
- Set research plan `status: approved` in frontmatter
- Update `updated` timestamp

If not approved:
- Set research plan `status: in-review` in frontmatter
- Update `updated` timestamp

### 7. Update Project Index

Update the Artifacts table with new status:

```markdown
| Research Plan | {{status}} | ./research/plans/{{slug}}.md |
```

## Output Format

```
## Research Plan Review: {{filename}}

### Scope Clarity
- [x] Primary question clearly defined — pass
- [x] Secondary questions support primary — pass
- [x] Boundaries established — pass

### Methodology Quality
- [x] Source types identified — pass
- [x] Search strategy actionable — pass
- [~] Quality criteria defined — warn: could be more specific

### Feasibility
- [x] Time estimate reasonable — pass
- [x] Tools available — pass
- [x] Expertise gaps identified — pass

### Alignment
- [x] Questions trace to project goals — pass
- [x] Outputs match content needs — pass

Summary: 11 pass, 1 warn, 0 fail
Status: {{approved|in-review}}

Next: Run `blog:research:draft {{path}}` to begin research
```

## Error Handling

| Condition | Response |
|-----------|----------|
| Plan not found | Error with path suggestion |
| Wrong artifact type | Error indicating expected type |
| Checklist not found | Error with checklist path |
