# Planning Phase Workflow

Translate research findings into actionable implementation plan with approval gates.

---

## Overview

```
Findings → High-Level Plan → Atomic Components → Phase Plans → Approvals → Issue Mapping
```

Use this workflow for:
- Complex/Operator charts
- Multi-phase development (MVP + enhancements)
- Extending existing charts with multiple improvements
- When user requests formal planning

Skip for Simple/Standard charts with Fast Path.

---

## Step 1: Use Research Findings

Before planning, ensure research is complete.

### Prerequisites

- [ ] Research summary documented
- [ ] Chart complexity classified
- [ ] Dependencies identified
- [ ] Open questions resolved (or documented as assumptions)

### Inputs to Planning

| From Research | Used For |
|---------------|----------|
| Complexity classification | CI handling, phase count |
| External dependencies | Subchart selection, exclusions |
| Ports and probes | Template structure |
| Environment variables | Values schema |
| Resource requirements | Default values |

---

## Step 2: Create High-Level Plan

Overall chart structure and feature set.

### High-Level Plan Template

See `assets/templates/high-level-plan.md` for full template.

```markdown
## High-Level Plan: <Chart-Name>

### Chart Metadata
- Name: <chart-name>
- Type: application / library
- Complexity: Simple / Standard / Complex / Operator
- CI Handling: Full / Lint-only (add to ct-install.yaml)

### Target Features

**MVP (Required)**
- [ ] Deployment with container
- [ ] Service (ClusterIP)
- [ ] ConfigMap/Secret for configuration
- [ ] NOTES.txt with access instructions

**Phase 2+ (Enhancements)**
- [ ] Health probes (liveness, readiness, startup)
- [ ] Resource defaults
- [ ] SecurityContext
- [ ] Ingress (optional)
- [ ] HPA (optional)
- [ ] PDB (optional)
- [ ] Persistence (if needed)
- [ ] ServiceMonitor (optional)

### Dependencies
- [ ] <subchart1> (condition: `<name>.enabled`)
- [ ] <subchart2> (condition: `<name>.enabled`)

### Values Structure (Outline)
- image: repository, tag, pullPolicy
- service: type, port
- ingress: enabled, hosts, tls
- resources: requests, limits
- <app-specific>: ...

### Risks and Mitigations
| Risk | Mitigation |
|------|------------|
| <risk1> | <mitigation1> |
```

---

## Step 3: Identify Atomic Components

Break down into independently deployable features.

### Atomicity Criteria

A component is atomic if it:
1. **Single Concern** - Does one thing well
2. **Independently Testable** - Can validate in isolation
3. **Clear Boundaries** - Doesn't require other pending work
4. **SemVer Appropriate** - Results in Minor or Patch bump

### Standard Helm Chart Phases

| Phase | Component | SemVer | Priority |
|-------|-----------|--------|----------|
| 1 | MVP (Deployment, Service, Config) | Minor (0.1.0) | Required |
| 2 | Health Probes | Patch (0.1.1) | High |
| 3 | Resource Defaults | Patch (0.1.2) | High |
| 4 | SecurityContext | Patch (0.1.3) | High |
| 5 | Ingress | Minor (0.2.0) | Medium |
| 6 | Persistence | Minor (0.3.0) | Medium |
| 7 | HPA | Minor (0.4.0) | Low |
| 8 | PDB | Patch (0.4.1) | Low |
| 9 | ServiceMonitor | Minor (0.5.0) | Low |

### Dependency Order

Some phases depend on others:

```
MVP ──┬── Probes
      ├── Resources
      ├── SecurityContext
      ├── Ingress ──── TLS
      ├── Persistence
      └── HPA ──── PDB
              └── ServiceMonitor
```

---

## Step 4: Draft Phase Plans

Create detailed plan for each atomic component.

### Phase Plan Template

See `assets/templates/phase-plan.md` for full template.

```markdown
## Phase Plan: <Phase-Name>

### Overview
- Phase: <N>
- Component: <name>
- Branch: `feat/chart-<chartname>-<component>`
- SemVer Impact: Minor / Patch

### Prerequisites
- [ ] Phase <N-1> merged
- [ ] <other prerequisites>

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `templates/<resource>.yaml` | Create | New template |
| `values.yaml` | Modify | Add <section> |
| `_helpers.tpl` | Modify | Add helper if needed |

### Values to Add
```yaml
<new-values-structure>
```

### Template Logic
<description of conditional logic, iterations, etc.>

### Validation Criteria
- [ ] `helm lint` passes
- [ ] `helm template` renders correctly
- [ ] New resource appears when enabled
- [ ] Existing behavior unchanged when disabled

### Dependencies on Other Phases
- Requires: <phase>
- Blocks: <phase>
```

---

## Step 5: Sequential Approvals

Review and approve each phase before proceeding.

### Approval Flow

```
High-Level Plan
      ↓ [Approval Required]
Phase 1 (MVP) Plan
      ↓ [Approval Required]
Implement Phase 1
      ↓ [PR Merged]
Phase 2 Plan
      ↓ [Approval Optional for Low-Risk]
Implement Phase 2
      ↓ [PR Merged]
...continue...
```

### When Approval is Required

| Scenario | Approval |
|----------|----------|
| High-level plan | **Required** |
| MVP phase | **Required** |
| Adding new resources (Ingress, PVC) | **Required** |
| Adding optional features (HPA, PDB) | Optional |
| Bug fixes, minor improvements | Optional |

### Approval Request Format

```markdown
## Phase Plan Ready: <Phase-Name>

**Component**: <name>
**Impact**: <Minor/Patch> version bump
**Files Changed**: <count>

### Summary
<1-2 sentence description>

### Key Decisions
- <decision1>: <choice made>
- <decision2>: <choice made>

### Questions
- <any open questions>?

Approve to proceed with implementation?
```

---

## Step 6: Map to Issues

Structure work as GitHub issues for tracking.

### Issue Hierarchy

```
Parent Issue: feat(<chart>): add Helm chart
├── Child: feat(<chart>): MVP chart structure
├── Child: feat(<chart>): add health probes
├── Child: feat(<chart>): add resource defaults
├── Child: feat(<chart>): add security context
├── Child: feat(<chart>): add ingress support
└── Child: feat(<chart>): add HPA support
```

### Issue Template

See `assets/templates/issue-structure.md` for full template.

```markdown
## Issue: feat(<chart>): <component>

### Description
<Phase plan summary>

### Acceptance Criteria
- [ ] <criterion1>
- [ ] <criterion2>
- [ ] PR passes CI
- [ ] Documentation updated

### Implementation Notes
<Key decisions, file changes, validation steps>

### Dependencies
- Blocked by: #<parent-issue>
- Blocks: #<child-issue>

### Labels
- `helm-chart`
- `<chart-name>`
- `phase-<N>`
```

### SemVer Mapping

| Issue Type | Commit Prefix | SemVer |
|------------|---------------|--------|
| New feature (HPA, Ingress) | `feat(<chart>):` | Minor |
| Improvement/fix | `fix(<chart>):` | Patch |
| Breaking change | `feat(<chart>)!:` | Major |

---

## Planning Outputs

At the end of planning phase, you should have:

1. **High-Level Plan** (`.claude/plans/<chart>-chart/high-level-plan.md`)
2. **Phase Plans** (`.claude/plans/<chart>-chart/phase-<N>-<name>.md`)
3. **Issue Structure** (ready to create in GitHub or documented)
4. **Approvals Recorded** (in plan files)

---

## Fast Path (Skip Planning)

For Simple/Standard charts:

1. Mental model of MVP only
2. Create chart directly
3. Add enhancements as single PR or skip

No formal planning documents needed.

---

## Related References

- `research-phase-workflow.md` - Previous phase
- `implementation-workflow.md` - Next phase
- `assets/templates/high-level-plan.md` - High-level plan template
- `assets/templates/phase-plan.md` - Phase plan template
- `assets/templates/issue-structure.md` - Issue template
