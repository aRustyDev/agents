---
name: yaml-optimization
description: extends, includes, and DRY pipeline design patterns for maintainable configurations
---

# YAML Optimization

> **Scope:** extends, includes, and DRY pipeline design patterns for maintainable configurations
> **GitLab version:** 9.0+
> **Source cards:** PL-2, WF-2
> **Tier:** C
> **Last verified:** 2026-03

## When to Use

Consult when designing DRY pipeline configurations using extends, includes,
and compositional patterns to reduce duplication and improve maintainability.

## Key Concepts

### DRY Pipeline Design Levels

| Level | Mechanism | Scope | Complexity |
|-------|-----------|-------|------------|
| 1. Same-file reuse | YAML anchors (`&`/`*`) | Single file | Low |
| 2. Template inheritance | `extends:` keyword | Cross-file | Medium |
| 3. Selective extraction | `!reference` tag | Cross-file | Medium |
| 4. Multi-file org | `include:local/project` | Cross-repo | Medium |
| 5. Modular components | `include:component` | Catalog | High |

### Include Organization Strategies

| Strategy | Pattern | Best For |
|----------|---------|----------|
| **Flat** | All jobs in one file | Small projects (<10 jobs) |
| **By stage** | `.ci/build.yml`, `.ci/test.yml` | Medium projects |
| **By concern** | `.ci/security.yml`, `.ci/deploy.yml` | Large projects |
| **Shared templates** | `include:project` from shared repo | Organization standards |
| **Components** | `include:component` from CI Catalog | Reusable across orgs |

### Key Design Principles

- **Start simple** — only add composition when duplication causes maintenance burden
- **Favor `extends:` over anchors** when cross-file reuse is needed
- **Limit inheritance depth** — max 3 levels for readability
- **Use `!reference` for surgical reuse** — better than inheriting an entire job
- **Pin include versions** — `ref:` tag on `include:project`, semver on components

<!-- TODO: Expand with real-world refactoring examples -->

## Examples

```yaml
# Multi-file pipeline organization
# .gitlab-ci.yml (root)
include:
  - local: .ci/variables.yml
  - local: .ci/build.yml
  - local: .ci/test.yml
  - local: .ci/deploy.yml
  - component: $CI_SERVER_FQDN/org/security/sast@1.0.0
    rules:
      - if: $CI_PIPELINE_SOURCE == "merge_request_event"

stages:
  - build
  - test
  - security
  - deploy
```

```yaml
# Hidden template pattern — .ci/templates.yml
.docker_build:
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY

# Consuming template — .ci/build.yml
build_app:
  extends: .docker_build
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

```yaml
# Combining extends with !reference
.notification:
  after_script:
    - 'curl -X POST $SLACK_WEBHOOK -d "{\"text\": \"$CI_JOB_NAME completed\"}"'

deploy:
  extends: .docker_build
  after_script:
    - !reference [.notification, after_script]
  script:
    - ./deploy.sh
```

## Common Patterns

- **Hidden jobs as template base** — `.base_job` + `extends:` for standardized configs
- **`include:project` with `ref:` pinning** — version-controlled cross-project templates
- **Stage-based file split** — `.ci/{stage}.yml` per pipeline stage
- **`!reference` for rules reuse** — extract `rules:` blocks from shared templates
- **Conditional includes** — `include:rules` to load security scanning only on MR pipelines

## Anti-Patterns

- **Premature abstraction** — adding composition before duplication is a real problem
- **Deep extends chains (>3 levels)** — trace through 4+ files to understand a job
- **Anchors expecting cross-file behavior** — they're YAML pre-parse, don't cross includes
- **Unpinned includes** — `include:project` without `ref:` breaks on upstream changes
- **Over-engineering reuse** — sometimes simple duplication is clearer than complex composition

## Practitioner Pain Points

- No built-in way to visualize fully-resolved pipeline YAML (workaround: CI lint API)
- `extends:` reverse deep merge order is counterintuitive — last listed wins
- `include:rules` evaluation context differs from job-level `rules:`
- Debugging composition requires mentally merging multiple file layers

## Related Topics

- [../yaml/yaml-composition.md](../yaml/yaml-composition.md) — anchors, extends, !reference mechanics
- [../yaml/keyword-reference.md](../yaml/keyword-reference.md) — complete keyword syntax
- [../components/authoring.md](../components/authoring.md) — CI/CD component design
- [optimization.md](optimization.md) — pipeline execution optimization strategies

## Sources

- [GitLab YAML optimization](https://docs.gitlab.com/ci/yaml/yaml_optimization/)
- Context cards: PL-2, WF-2

