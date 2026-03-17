# Phase 6: Validation

## Objective

Validate coverage, quality, and search effectiveness of the unified index.

## Duration

0.5 day

## Dependencies

- Phase 5 (aggregation complete)

---

## Validation Experiments

### Experiment 1: Baseline Recall

Create: `analysis/experiments/8-baseline-recall.md`

```yaml
experiment:
  id: "exp-008-baseline-recall"
  title: "Measure recall against known baseline"

  hypothesis: "Index contains 80%+ of known baseline components"

  inputs:
    baseline: "analysis/evidence/known-external.yaml"
    index: "component-index.db"

  procedure:
    - step: 1
      action: "Load baseline components"
    - step: 2
      action: "Search index for each baseline item"
    - step: 3
      action: "Calculate recall = found / baseline"

  metrics:
    - name: "recall"
      definition: "% of baseline items found in index"
      target: 0.8
```

### Experiment 2: Search Quality

Create: `analysis/experiments/9-search-quality.md`

```yaml
experiment:
  id: "exp-009-search-quality"
  title: "Test search with sample queries"

  inputs:
    queries:
      - query: "git changelog"
        expected: ["git-cliff", "conventional-changelog"]
      - query: "kubernetes"
        expected: ["k8s deployment", "helm"]
      - query: "terraform"
        expected: ["tf module", "infrastructure"]
      - query: "react component"
        expected: ["react", "frontend"]
      - query: "security audit"
        expected: ["semgrep", "static-analysis"]

  procedure:
    - step: 1
      action: "Run each query against FTS index"
    - step: 2
      action: "Check if expected results in top 10"
    - step: 3
      action: "Calculate precision and MRR"

  metrics:
    - name: "precision_at_10"
      definition: "% of relevant results in top 10"
      target: 0.9
    - name: "mrr"
      definition: "Mean Reciprocal Rank"
      target: 0.5
```

### Experiment 3: Coverage Analysis

Create: `analysis/experiments/10-coverage-analysis.md`

```yaml
experiment:
  id: "exp-010-coverage"
  title: "Analyze coverage by component type and source"

  procedure:
    - step: 1
      action: "Count components by type"
    - step: 2
      action: "Count components by source"
    - step: 3
      action: "Identify gaps"

  metrics:
    - name: "type_coverage"
      definition: "All 8 types have components"
      target: 1.0
    - name: "source_coverage"
      definition: "% of known registries represented"
      target: 0.9
```

---

## Validation Results Schema

```yaml
# analysis/results/validation.yaml
validation:
  timestamp: "2026-03-08T16:00:00Z"

  baseline_recall:
    baseline_count: 85
    found_count: 72
    recall: 0.847
    missing:
      - name: "some-skill"
        expected_source: "github"
        search_attempted: true

  search_quality:
    queries_tested: 5
    precision_at_10: 0.92
    mrr: 0.67
    failed_queries:
      - query: "..."
        expected: "..."
        actual_top_10: [...]

  coverage:
    by_type:
      skill: 450
      agent: 85
      command: 45
      rule: 12
      prompt: 28
      hook: 15
      mcp: 120
      plugin: 65
    by_source:
      skillsmp: 180
      github: 400
      npm: 35
      # ...
    gaps:
      - "Rules have limited registry presence"
      - "Prompts mostly in plugins"
```

---

## Final Report

Compile: `analysis/reports/ecosystem-survey.md`

```markdown
# Claude Code Component Ecosystem Survey

## Executive Summary

[Key findings in 2-3 sentences]

## Coverage

| Component Type | Count | Sources | Quality |
|----------------|-------|---------|---------|
| Skills | 450 | 12 | High |
| Agents | 85 | 8 | High |
| ... | ... | ... | ... |

## Top Registries

| Registry | Components | API | Rate Limit |
|----------|------------|-----|------------|
| skillsmp | 180 | Yes | 100/min |
| ... | ... | ... | ... |

## Gaps Identified

1. [Gap description]
2. [Gap description]

## Recommendations

1. [Recommendation]
2. [Recommendation]

## Appendix: Methodology

[Brief description of process]
```

---

## Finding: Overall Quality

```yaml
# analysis/findings/overall-quality.yaml
finding:
  id: "finding-final"
  title: "Ecosystem discovery completeness"

  claim: "Index captures 85% of known ecosystem"
  confidence: "high"

  experiment_ids:
    - "exp-008-baseline-recall"
    - "exp-009-search-quality"
    - "exp-010-coverage"

  implications:
    - "Index is suitable for production use"
    - "Some component types need manual curation"

  recommendations:
    - "Schedule weekly refresh via cron"
    - "Add manual curation for rules/prompts"
```

---

## Deliverables

| File | Purpose |
|------|---------|
| `analysis/results/validation.yaml` | Validation metrics |
| `analysis/findings/overall-quality.yaml` | Quality assessment |
| `analysis/reports/ecosystem-survey.md` | Final report |

---

## Success Gate

| Criterion | Target | Actual |
|-----------|--------|--------|
| Baseline recall | ≥80% | |
| Precision@10 | ≥90% | |
| Type coverage | 8/8 | |
| Source coverage | ≥90% | |
| Search latency | <100ms | |

## Checklist

Use: `checklists/schemas/data-validation.schema.json`

Record: `checklists/instances/phase-6.json`
