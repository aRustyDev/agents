---
name: downstream-pipelines
description: Parent-child, multi-project, and dynamic child pipelines with trigger configuration
---

# Downstream Pipelines

> **Scope:** Parent-child, multi-project, and dynamic child pipelines with trigger configuration
> **GitLab version:** 11.8+
> **Source cards:** NEW-04
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Splitting complex pipelines into parent-child for maintainability
- Orchestrating builds across multiple projects (multi-project pipelines)
- Generating pipeline configuration dynamically from build artifacts
- Passing variables or artifacts between upstream and downstream pipelines

**Do NOT use when:** A single pipeline with `needs:` DAG would suffice — downstream pipelines add debugging complexity.

## Key Concepts

### Downstream Pipeline Types

| Type | Keyword | Scope | Max Nesting |
|---|---|---|---|
| **Parent-child** | `trigger:include:local/artifact` | Same project, same ref, same SHA | 2 levels |
| **Multi-project** | `trigger:project:` | Different project, independent pipeline | N/A |
| **Dynamic child** | `trigger:include:artifact` | Generated YAML from parent job artifact | 2 levels |

### Key Configuration

| Keyword | Purpose |
|---|---|
| `trigger:include:local:` | Include static child pipeline YAML |
| `trigger:include:artifact:` | Include generated YAML from job artifact |
| `trigger:project:` | Trigger pipeline in another project |
| `trigger:strategy: depend` | Mirror downstream pipeline status to parent |
| `trigger:forward:yaml_variables: true` | Forward YAML-defined variables downstream |
| `trigger:forward:pipeline_variables: true` | Forward pipeline-level variables downstream |
| `trigger:include:inputs:` | Pass typed inputs to child pipeline (17.0+) |

### Status Mirroring

Without `strategy: depend`, the parent job succeeds as soon as the downstream pipeline is created — even if the downstream pipeline later fails.

### CI_PIPELINE_SOURCE in Downstream

| Pipeline Type | CI_PIPELINE_SOURCE |
|---|---|
| Multi-project downstream | `pipeline` |
| Parent-child downstream | `parent_pipeline` |

### Cross-Pipeline Artifacts

| Pattern | Syntax |
|---|---|
| Child → parent (same pipeline) | `needs: [{ pipeline: $CI_PARENT_PIPELINE_ID, job: "job-name" }]` |
| Cross-project | `needs: [{ project: "group/project", job: "build", ref: "main", artifacts: true }]` |

## Examples

### Parent-Child Pipeline

```yaml
# Parent .gitlab-ci.yml
trigger-tests:
  stage: test
  trigger:
    include: .ci/test-pipeline.yml
    strategy: depend
    forward:
      yaml_variables: true
```

### Dynamic Child Pipeline

```yaml
generate-config:
  stage: build
  script:
    - python generate_pipeline.py > child.yml
  artifacts:
    paths: [child.yml]

trigger-dynamic:
  stage: test
  trigger:
    include:
      - artifact: child.yml
        job: generate-config
    strategy: depend
```

### Multi-Project Trigger

```yaml
trigger-deploy:
  stage: deploy
  trigger:
    project: infra/deploy-service
    branch: main
    strategy: depend
  variables:
    UPSTREAM_VERSION: $CI_COMMIT_TAG
```

## Common Patterns

- **`trigger:strategy: depend`** for parent-child status mirroring (almost always wanted)
- **`trigger:forward:yaml_variables: true`** for config passing to children
- **`trigger:include:artifact`** for dynamically generated child pipelines
- **`needs:pipeline:job`** for cross-pipeline artifact consumption

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Parent-child > 2 levels deep | Hard limit — pipeline creation fails | Flatten hierarchy or use multi-project |
| No `strategy: depend` | Parent succeeds before child finishes | Add `strategy: depend` |
| Forward all variables downstream | Security risk — leaks secrets | Use `forward:yaml_variables` selectively |
| Dynamic child without valid YAML | Pipeline creation fails silently | Validate generated YAML in parent job |

## Practitioner Pain Points

1. **Max 2 levels nesting** — hard constraint, frequently hits teams decomposing complex monorepos.
2. **Dynamic child config must be valid YAML** — generate step should validate before saving artifact.
3. **Debugging across parent-child boundaries** — logs split across pipelines. Use `strategy: depend` and check child pipeline link in parent job.
<!-- TODO: Expand with deeper research on cross-project artifact authentication and limits -->

## Related Topics

- [types-and-triggers.md](types-and-triggers.md) — Pipeline types overview and CI_PIPELINE_SOURCE
- [monorepo.md](monorepo.md) — Per-service child pipelines for monorepos
- [../variables/precedence.md](../variables/precedence.md) — Variable forwarding with `trigger:forward`

## Sources

- [Downstream pipelines](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/)
- [Parent-child pipelines](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/#parent-child-pipelines)

