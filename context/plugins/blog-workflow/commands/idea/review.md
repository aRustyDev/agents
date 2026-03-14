---
name: blog/idea/review
description: Evaluate an idea or plan artifact against its review checklist
argument-hint: <path> [--approve]
arguments:
  - name: path
    description: Path to the artifact (idea.md or plan.md)
    required: true
  - name: --approve
    description: Auto-approve if all items pass (skip confirmation)
    required: false
  - name: --no-approve
    description: Evaluate only, never set approved status
    required: false
---

# Idea/Plan Review

Evaluate an idea or plan artifact against its review checklist, with optional approval workflow.

## Behavior

1. **Load artifact** from provided path

2. **Detect type** from frontmatter:
   - `type: idea` → use `.templates/review-checklists/idea.md`
   - `type: plan` → use `.templates/review-checklists/plan.md`
   - Other types → error: "Unsupported artifact type for idea review"

3. **Load checklist** from `.templates/review-checklists/`

4. **Evaluate each criterion**:
   - Mark as **pass**, **warn**, or **fail**
   - Provide brief justification for each

5. **Update artifact status** → `in-review`

6. **Update `index.md`** Artifacts table with new status

7. **Approval workflow** (if all items pass):
   - If `--no-approve`: Skip approval, just report results
   - If `--approve`: Auto-approve without prompt
   - Otherwise: Prompt user "All checks passed. Approve this artifact? [y/n]"
   - If approved: Set status → `approved`, update `index.md`

## Output Format

```text
## Review: <artifact type>

### <Checklist Section>
- [x] <criterion> — pass
- [~] <criterion> — warn: <reason>
- [ ] <criterion> — fail: <reason>

### Summary
- Pass: X
- Warn: Y
- Fail: Z

Status: in-review → [approved | in-review]
```

## Flags

| Flag | Behavior |
|------|----------|
| `--approve` | Skip confirmation, auto-approve if all pass |
| `--no-approve` | Evaluate only, never set `approved` status |

## Example

**Input**: `blog:idea:review content/_projects/ebpf-tracing/idea.md`

**Output**:

```text
## Review: idea

### Scope Clarity
- [x] Target audience defined — pass
- [x] Core message identifiable — pass
- [x] Scope is achievable — pass

### Differentiation
- [x] Unique angle or perspective — pass
- [~] Not rehashing existing content — warn: similar tutorials exist, angle is unique

### Research Needs
- [x] Research requirements clear — pass
- [x] Sources/experts identified — pass

### Feasibility
- [x] Expertise available — pass
- [x] Time estimate reasonable — pass

### Summary
- Pass: 9
- Warn: 1
- Fail: 0

All checks passed. Approve this artifact? [y/n]
> y

Status: in-review → approved
```
