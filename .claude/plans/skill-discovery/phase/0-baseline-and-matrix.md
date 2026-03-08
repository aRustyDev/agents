# Phase 0: Baseline & Search Term Matrix

## Objective

Establish systematic search vocabulary and ground truth for validation.

## Duration

0.5 day

## Dependencies

None (first phase)

---

## Task 0.1: Build Search Term Matrix

### Experiment

Use template: `analysis/experiments/templates/experiment.yaml`

Create: `analysis/experiments/0-search-term-matrix.md`

### Procedure

1. For each of 8 component types, identify:
   - Primary terms (most common names)
   - Synonyms (alternative names)
   - Narrower terms (specific file patterns)
   - Broader terms (category names)

2. Record in matrix format:

```yaml
# analysis/results/search-term-matrix.yaml
matrix:
  skills:
    primary: ["claude skill", "agent skill"]
    synonyms: ["capability", "knowledge module"]
    narrower: ["SKILL.md", "skill-creator"]
    broader: ["claude code", "ai assistant"]
  agents:
    primary: ["claude agent", "subagent"]
    # ...
```

### Boolean Query Patterns

For each search engine, document query syntax:

```yaml
# analysis/results/boolean-queries.yaml
patterns:
  github:
    and: '"term1" "term2"'
    or: "term1 OR term2"
    not: "term1 NOT term2"
    file: "filename:SKILL.md"
    path: "path:skills/"
    org: "org:anthropics"
  websearch:
    and: "term1 AND term2"
    or: "term1 OR term2"
    site: "site:github.com"
```

### Deliverables

- `analysis/results/search-term-matrix.yaml`
- `analysis/results/boolean-queries.yaml`

---

## Task 0.2: Baseline Inventory

### Procedure

1. Count local components per type:

```bash
# Skills
find context/skills -name "SKILL.md" | wc -l

# Agents
find context/agents -name "*.md" | wc -l

# Commands
find context/commands -name "*.md" | wc -l

# etc.
```

2. Record baseline:

```yaml
# analysis/evidence/local-baseline.yaml
evidence:
  id: "baseline-local"
  collected: "2026-03-08"
  source_type: "manual"
  content:
    skills: 100
    agents: 10
    commands: 20
    rules: 5
    prompts: 10
    hooks: 5
    mcp: 10
    plugins: 6
```

3. Document known external components (from Phase 0 prior work):

```yaml
# analysis/evidence/known-external.yaml
evidence:
  id: "baseline-external"
  content:
    skills:
      - name: "anthropics/skills"
        count: 17
      - name: "trailofbits/skills"
        count: 35
      # ...
```

### Deliverables

- `analysis/evidence/local-baseline.yaml`
- `analysis/evidence/known-external.yaml`

---

## Success Gate

| Criterion | Target | Validation |
|-----------|--------|------------|
| Matrix coverage | 8/8 types | All component types have terms |
| Synonyms per type | 5+ | Sufficient vocabulary |
| Local baseline | Documented | Counts recorded |
| External baseline | 20+ components | Known community components |

## Checklist

Use: `checklists/schemas/research-prep.schema.json`

Record: `checklists/instances/phase-0.json`

---

## Observations Log

Record observations during execution:

```yaml
# analysis/findings/phase-0-observations.yaml
observations:
  - timestamp: ""
    type: "insight"
    description: ""
```
