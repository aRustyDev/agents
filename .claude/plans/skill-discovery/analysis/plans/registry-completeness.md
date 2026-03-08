# Analysis Plan: Registry Completeness

## Objective

Assess coverage and completeness of discovered registries across all component types.

## Scope

Measure completeness for:
- Number of registries per component type
- Components available per registry
- Cross-registry overlap (deduplication potential)
- Gaps in coverage

---

## Completeness Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Registry breadth | Unique registries per type | 3+ |
| Component depth | Components per registry | 20+ |
| Overlap rate | % components in >1 registry | 10-30% |
| Gap rate | Types with <3 registries | 0 |

---

## Analysis Process

### Step 1: Aggregate Registry Data

From Phase 2-3 results:
- `research/results/*/registries.yaml`
- `research/results/*/github-repos.yaml`

### Step 2: Build Coverage Matrix

```yaml
coverage_matrix:
  skills:
    registries: 12
    github_repos: 11
    total_components: 450
    top_registry: "skillsmp"
    gap: null

  agents:
    registries: 5
    github_repos: 8
    total_components: 120
    top_registry: "voltAgent"
    gap: "Limited standalone agent registries"

  # ... etc
```

### Step 3: Identify Gaps

For each component type:
- < 3 registries → "Insufficient coverage"
- < 50 components → "Low volume"
- < 3 sources → "Single point of failure"

### Step 4: Cross-Registry Analysis

Calculate overlap:
- Same component name in multiple registries
- Content hash matches across sources
- URL deduplication potential

---

## Deliverables

| File | Purpose |
|------|---------|
| `analysis/results/coverage-matrix.yaml` | Raw coverage data |
| `analysis/findings/registry-gaps.yaml` | Gap analysis |
| `analysis/reports/registry-completeness.md` | Summary report |

---

## Success Criteria

- [ ] All 8 component types analyzed
- [ ] Coverage matrix complete
- [ ] Gaps identified and documented
- [ ] Overlap rate calculated
- [ ] Recommendations for improving coverage
