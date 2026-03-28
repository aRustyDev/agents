---
name: yaml-composition
description: Anchors, extends, !reference, and merge keys for DRY pipeline configuration
---

# YAML Composition

> **Scope:** Anchors, extends, !reference, and merge keys for DRY pipeline configuration
> **GitLab version:** 13.0+
> **Source cards:** NEW-15, PL-2, WF-2
> **Tier:** C
> **Last verified:** 2026-03

## When to Use

Use YAML composition techniques to reduce duplication across pipeline configs.
Choose the right mechanism based on scope (single-file vs cross-file) and complexity.

## Key Concepts

### Composition Mechanisms Comparison

| Mechanism | Scope | Merge Behavior | Max Depth | Best For |
|-----------|-------|---------------|-----------|----------|
| YAML anchors (`&`/`*`) | Same file only | Simple substitution (pre-parse) | N/A | Repeated values in one file |
| Merge key (`<<:`) | Same file only | Hash merge | N/A | Deprecated in YAML 1.2 — avoid |
| `extends:` | Cross-file | Reverse deep merge | 11 levels | Template inheritance |
| `!reference` tag | Cross-file | Selective key extraction | 10 levels | Cherry-picking specific keys |
| `include:` | Cross-file | File composition | N/A | Multi-file organization |

### YAML Anchors (`&` / `*`)

- Define with `&anchor_name`, reference with `*anchor_name`
- **Cannot cross file boundaries** — most common gotcha with includes
- Pure YAML pre-parse feature, no GitLab-specific behavior

### `extends:` Keyword

- Deep merges keys from parent job(s) into child
- **Reverse deep merge order** — last listed parent wins, deepest key overrides
- Supports up to 11 levels of inheritance
- Can extend multiple jobs: `extends: [.job_a, .job_b]`
- Hidden jobs (`.job_name`) as template bases

### `!reference` Tag

- Extracts specific keys from any job (including included files)
- Returns the value of a nested path: `!reference [.job, script]`
- Supports up to 10 levels of nesting
- More surgical than `extends:` — pick exactly what you need

### `include:` Sub-keywords

| Type | Syntax | Use Case |
|------|--------|----------|
| `local` | `include:local: .ci/base.yml` | Same-repo files |
| `project` | `include:project` + `ref:` | Cross-project with version pin |
| `component` | `include:component` | CI/CD Catalog modules |
| `remote` | `include:remote` | External URL |
| `template` | `include:template` | GitLab-managed templates |

- `include:rules` — conditional include evaluation (different context than job rules)
- `include:inputs` — typed parameters via `spec:inputs` validation
- `include:integrity` — SHA256 verification for remote includes

## Examples

```yaml
# YAML anchors — same file only
.default_retry: &default_retry
  max: 2
  when:
    - runner_system_failure
    - stuck_or_timeout_failure

job_a:
  retry: *default_retry
  script: echo "uses anchor"
```

```yaml
# extends — cross-file template inheritance
.base_test:
  image: python:3.12
  before_script:
    - pip install -r requirements.txt
  retry:
    max: 1

unit_tests:
  extends: .base_test
  script:
    - pytest tests/unit/   # deep merge keeps image, before_script, retry

integration_tests:
  extends: .base_test
  image: python:3.12-bookworm  # overrides parent image
  script:
    - pytest tests/integration/
```

```yaml
# !reference — selective key extraction
.setup:
  before_script:
    - apt-get update
    - apt-get install -y curl

.teardown:
  after_script:
    - rm -rf tmp/

my_job:
  before_script:
    - !reference [.setup, before_script]
    - echo "additional setup"
  after_script:
    - !reference [.teardown, after_script]
  script:
    - run-tests
```

## Common Patterns

- **Hidden job templates** — `.base_job` + `extends:` for DRY job definitions
- **`include:project` with `ref:` pinning** — version-locked cross-project reuse
- **`!reference` for selective reuse** — extract `before_script` or `rules` from templates without inheriting everything
- **`include:component`** for Catalog-based modular CI

## Anti-Patterns

- **Anchors expecting cross-file behavior** — anchors are YAML pre-parse, don't cross `include:` boundaries
- **Deep extends chains (>3 levels)** — becomes undebuggable; flatten or use `!reference` instead
- **Relying on merge keys (`<<:`)** — deprecated in YAML 1.2, may break in future parsers
- **Over-engineering reuse** — simple duplication is sometimes clearer than complex composition
- **Remote includes without integrity** — use `include:integrity` for SHA256 verification
- **Mixing anchors and extends confusingly** — pick one pattern per use case

## Practitioner Pain Points

- YAML anchors don't cross file boundaries — most frequently encountered gotcha
- `extends:` deep merge order is reverse (last wins) — counterintuitive
- Debugging `!reference` resolution requires manual trace through included files
- `include:rules` has different evaluation context than job-level `rules:`
- No built-in way to visualize the fully-resolved pipeline YAML (use `ci lint` API)

<!-- TODO: Expand with resolved YAML visualization techniques -->

## Related Topics

- [keyword-reference.md](keyword-reference.md) — complete keyword syntax reference
- [rules-patterns.md](rules-patterns.md) — rules clause patterns
- [../components/authoring.md](../components/authoring.md) — CI/CD component authoring
- [../pipelines/yaml-optimization.md](../pipelines/yaml-optimization.md) — DRY pipeline design patterns

## Sources

- [GitLab YAML optimization](https://docs.gitlab.com/ci/yaml/yaml_optimization/)
- Context cards: NEW-15, PL-2, WF-2
