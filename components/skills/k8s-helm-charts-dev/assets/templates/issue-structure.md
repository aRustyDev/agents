# Issue Structure for Helm Chart Development

Template for creating GitHub issues with parent-child relationships.

---

## Parent Issue Template

Used for the overall chart development tracking.

```markdown
## feat(<chart>): add Helm chart

### Overview

Add Helm chart for [<Application>](<url>) - <brief description>.

### Chart Information

| Property | Value |
|----------|-------|
| Chart Name | `<chart>` |
| Complexity | Simple / Standard / Complex / Operator |
| Official Chart Exists | Yes (extending) / No |
| CI Handling | Full / Lint-only |

### Phases

- [ ] #<issue> Phase 1: MVP chart structure
- [ ] #<issue> Phase 2: Health probes
- [ ] #<issue> Phase 3: Resource defaults
- [ ] #<issue> Phase 4: Security context
- [ ] #<issue> Phase 5: Ingress support
- [ ] #<issue> Phase 6: Persistence
- [ ] #<issue> Phase 7: HPA support
- [ ] #<issue> Phase 8: PDB support

### Research

Research summary: `.claude/plans/<chart>-chart/research-summary.md`

### Acceptance Criteria

- [ ] Chart passes `helm lint`
- [ ] Chart passes `helm template`
- [ ] Documentation complete (README, NOTES.txt)
- [ ] All planned phases implemented
- [ ] CI passing

### Labels

- `helm-chart`
- `<chart-name>`
- `epic`
```

---

## Child Issue Template (Per Phase)

Used for individual phase tracking.

```markdown
## feat(<chart>): <phase-description>

### Overview

<1-2 sentence description of what this phase adds>

### Phase Information

| Property | Value |
|----------|-------|
| Phase | <N> |
| Component | <component-name> |
| Branch | `feat/chart-<chart>-<component>` |
| SemVer | Minor / Patch |
| Priority | High / Medium / Low |

### Parent Issue

Blocked by: #<parent-issue>

### Changes

**Files to Create:**
- `templates/<resource>.yaml`

**Files to Modify:**
- `values.yaml` - Add `<section>` configuration
- `README.md` - Document new feature

### Values Added

```yaml
<section>:
  enabled: false
  option1: <default>
```

### Acceptance Criteria

- [ ] `helm lint charts/<chart>` passes
- [ ] `helm template` renders correctly
- [ ] Feature works when enabled
- [ ] No regression when disabled
- [ ] README updated
- [ ] PR passes CI

### Implementation Notes

<Key decisions, patterns to follow, gotchas>

### Labels

- `helm-chart`
- `<chart-name>`
- `phase-<N>`
```

---

## Issue Hierarchy Example

```
#100 feat(bugsink): add Helm chart                    [epic]
├── #101 feat(bugsink): MVP chart structure           [phase-1]
├── #102 feat(bugsink): add health probes             [phase-2]
├── #103 feat(bugsink): add resource defaults         [phase-3]
├── #104 feat(bugsink): add security context          [phase-4]
├── #105 feat(bugsink): add ingress support           [phase-5]
├── #106 feat(bugsink): add persistence               [phase-6]
├── #107 feat(bugsink): add HPA support               [phase-7]
└── #108 feat(bugsink): add PDB support               [phase-8]
```

---

## SemVer Mapping

| Issue Type | Commit Prefix | Version Bump | Example |
|------------|---------------|--------------|---------|
| MVP | `feat(<chart>):` | Minor (0.1.0) | Initial chart |
| New Feature | `feat(<chart>):` | Minor (0.2.0) | Add Ingress |
| Enhancement | `feat(<chart>):` | Patch (0.2.1) | Add probes |
| Bug Fix | `fix(<chart>):` | Patch (0.2.2) | Fix template |
| Breaking | `feat(<chart>)!:` | Major (1.0.0) | Restructure values |

---

## Labels

### Chart Labels

| Label | Color | Description |
|-------|-------|-------------|
| `helm-chart` | `#0e8a16` | Helm chart work |
| `<chart-name>` | `#1d76db` | Specific chart |

### Phase Labels

| Label | Color | Description |
|-------|-------|-------------|
| `phase-1` | `#fbca04` | MVP phase |
| `phase-2` | `#fbca04` | Probes phase |
| `phase-3` | `#fbca04` | Resources phase |
| `epic` | `#d876e3` | Parent tracking issue |

### Priority Labels

| Label | Color | Description |
|-------|-------|-------------|
| `priority:high` | `#b60205` | Required for release |
| `priority:medium` | `#d93f0b` | Should have |
| `priority:low` | `#fbca04` | Nice to have |

---

## Creating Issues with gh CLI

```bash
# Create parent issue
gh issue create \
  --title "feat(bugsink): add Helm chart" \
  --body-file .claude/plans/bugsink-chart/parent-issue.md \
  --label "helm-chart,bugsink,epic"

# Create child issue (after getting parent issue number)
gh issue create \
  --title "feat(bugsink): MVP chart structure" \
  --body-file .claude/plans/bugsink-chart/phase-1-issue.md \
  --label "helm-chart,bugsink,phase-1"
```

---

## Linking Issues in PR

```markdown
## Summary

Add health probes to bugsink chart.

Closes #102
Part of #100
```

---

## Notes

1. **Create parent issue first** to get issue number for children
2. **Update parent issue** with child issue links after creation
3. **Use consistent commit prefixes** for release-please changelog
4. **Close issues via PR** using `Closes #<number>` in PR description
