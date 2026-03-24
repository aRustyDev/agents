# Implementation Phase Workflow

Execute the plan with quality gates and review checkpoints.

---

## Overview

```
Start → Assign Issue + Draft PR → Implement → Sanity Checks → Review Stop → Submit PR → Post-Merge
```

Use this workflow for:
- Each phase of chart development
- Both MVP and enhancement phases
- Both full workflow and fast path implementations

---

## Step 1: Begin Implementation

### 1a. Assign Issue (If Using Issues)

```bash
# Assign yourself to the issue
gh issue edit <issue-number> --add-assignee @me

# Move to in-progress (if using project boards)
gh issue edit <issue-number> --add-label "status:in-progress"
```

### 1b. Create Worktree

```bash
# Fetch latest main
git fetch origin main

# Create worktree with feature branch
git worktree add .worktrees/<chart>-<phase> -b feat/chart-<chart>-<phase> origin/main

# Change to worktree
cd .worktrees/<chart>-<phase>
```

### 1c. Create Draft PR Immediately

Create draft PR at the start to:
- Signal work in progress
- Enable early feedback
- Link to issue for tracking

```bash
# After first commit (even just Chart.yaml)
git add .
git commit -m "feat(<chart>): initial <phase> structure (WIP)"
git push -u origin feat/chart-<chart>-<phase>

# Create draft PR
gh pr create \
  --draft \
  --title "feat(<chart>): <phase-description>" \
  --body "Work in progress. Closes #<issue-number>"
```

---

## Step 2: Implement

### Implementation Order (MVP Phase)

1. **Chart.yaml** - Metadata, dependencies
2. **values.yaml** - Configuration structure
3. **templates/_helpers.tpl** - Helper functions
4. **templates/deployment.yaml** - Main workload
5. **templates/service.yaml** - Networking
6. **templates/configmap.yaml** - Non-sensitive config
7. **templates/secret.yaml** - Sensitive config
8. **templates/NOTES.txt** - Post-install instructions
9. **README.md** - Documentation

### Implementation Order (Enhancement Phases)

1. **values.yaml** - Add new configuration section
2. **templates/<resource>.yaml** - New template
3. **templates/_helpers.tpl** - Helper if needed
4. **README.md** - Update documentation

### Commit Frequently

```bash
# Small, logical commits
git add templates/deployment.yaml
git commit -m "feat(<chart>): add deployment template"

git add templates/service.yaml
git commit -m "feat(<chart>): add service template"

# Push regularly to update draft PR
git push
```

---

## Step 3: Sanity Checks

Run before marking PR ready.

### Required Checks

```bash
# 1. Lint chart
helm lint charts/<chart>

# 2. Template rendering
helm template test-release charts/<chart>

# 3. Template with various values
helm template test-release charts/<chart> --set <feature>.enabled=true

# 4. Dependencies (if any)
helm dependency update charts/<chart>
helm dependency build charts/<chart>
```

### Enhanced Validation (If Available)

```bash
# Run skill validation script
bash ~/.claude/skills/k8s-helm-charts-dev/scripts/validate-chart.sh charts/<chart>

# CI simulation
ct lint --charts charts/<chart> --config ct.yaml
```

### Security Checks

- [ ] No hardcoded secrets in templates
- [ ] `securityContext` present (or planned for later phase)
- [ ] `resources` block present (even if empty)
- [ ] No privileged containers (unless required and documented)

### Sanity Check Checklist

- [ ] `helm lint` passes with no errors
- [ ] `helm template` renders all expected resources
- [ ] Conditional resources render only when enabled
- [ ] Default values work (no required values without defaults)
- [ ] No YAML syntax errors
- [ ] No duplicate resource names
- [ ] Labels and selectors match
- [ ] Port names are consistent

---

## Step 4: External Review Stops

Pause and request review when:

### Architectural Decisions

- Choosing between approaches (e.g., ConfigMap vs Secret)
- Adding new dependencies
- Changing values schema structure
- Deviating from plan

### Breaking Changes

- Renaming values
- Changing default behavior
- Removing configuration options

### Unclear Requirements

- Ambiguous user request
- Missing information from research
- Multiple valid interpretations

### Complex Logic

- Intricate template conditionals
- Custom helper functions
- Unusual patterns

### Review Request Format

```markdown
## Review Requested: <topic>

**Context**: <what you're working on>

**Question**: <specific question or decision>

**Options**:
1. <option-a> - <pros/cons>
2. <option-b> - <pros/cons>

**Recommendation**: <your suggestion>

Please advise before I continue.
```

---

## Step 5: Submit PR

### Prerequisites

- [ ] All sanity checks pass
- [ ] Documentation updated (README, NOTES.txt)
- [ ] Values documented with `# --` comments
- [ ] No TODO comments left in code
- [ ] Commit history is clean

### Mark PR Ready

```bash
# Convert draft to ready
gh pr ready

# Or via web UI: "Ready for review" button
```

### PR Description

Ensure PR description includes:
- Summary of changes
- Issue reference (`Closes #<number>`)
- Test checklist
- Screenshots/examples if applicable

### Final PR Checklist

```markdown
## Summary
<1-2 sentence description>

## Changes
- <change1>
- <change2>

## Testing
- [x] `helm lint` passes
- [x] `helm template` renders correctly
- [x] Feature works when enabled
- [x] No regression when disabled

## Checklist
- [x] Values documented with `# --` comments
- [x] README updated
- [x] NOTES.txt accurate
- [x] No hardcoded secrets

Closes #<issue-number>
```

---

## Step 6: Post-Merge

### Update Issue

```bash
# Issue should auto-close via "Closes #<number>" in PR
# If not, close manually
gh issue close <issue-number>
```

### Clean Up Worktree

```bash
# Return to main repo
cd /path/to/main/repo

# Remove worktree
git worktree remove .worktrees/<chart>-<phase>

# Prune stale references
git worktree prune
```

### Start Next Phase

```bash
# Fetch updated main (includes merged changes)
git fetch origin main

# Create new worktree for next phase
git worktree add .worktrees/<chart>-<next-phase> -b feat/chart-<chart>-<next-phase> origin/main
```

---

## Fast Path Implementation

For Simple/Standard charts without formal planning:

1. **Create worktree** (same as above)
2. **Implement directly** (no draft PR needed)
3. **Run sanity checks**
4. **Create PR** (ready, not draft)
5. **Clean up**

Skip: Issue assignment, draft PR, multiple review stops

---

## Troubleshooting

### Helm Lint Errors

| Error | Fix |
|-------|-----|
| `Chart.yaml: 'name' is required` | Add name field |
| `values.yaml: cannot unmarshal` | Check YAML syntax |
| `templates: parse error` | Check Go template syntax |

### Template Errors

| Error | Fix |
|-------|-----|
| `nil pointer evaluating` | Add `{{ if .Values.x }}` guard |
| `can't evaluate field X` | Check spelling, nesting |
| `function "X" not defined` | Check helper name, imports |

### Common Mistakes

- Forgetting to quote strings: `{{ .Values.x | quote }}`
- Wrong indentation with `nindent`
- Missing `{{- ` (trim whitespace)
- Selector labels don't match pod labels

---

## Related References

- `planning-phase-workflow.md` - Previous phase
- `research-strategy.md` - Research guidance
- `scripts/validate-chart.sh` - Validation script
- `chart-complexity.md` - CI handling based on complexity
