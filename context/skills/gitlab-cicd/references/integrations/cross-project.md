---
name: cross-project-integration
description: Multi-project pipelines, CI_JOB_TOKEN scope, cross-project artifact sharing, and API triggers
---

# Cross-Project Integration

> **Scope:** Multi-project pipelines, CI_JOB_TOKEN scope, cross-project artifact sharing, and API triggers
> **GitLab version:** 9.0+
> **Source cards:** NEW-18
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Consult when implementing multi-project pipelines, cross-project artifact
sharing, or API-based pipeline triggers between repositories.

## Key Concepts

- **`trigger:project`** — start downstream pipeline in another project
- **`needs:project`** — download artifacts from another project's pipeline
- **`CI_JOB_TOKEN`** — automatic authentication for cross-project API access
- **`include:project`** — share template YAML across projects
- **Token scope** — CI_JOB_TOKEN access must be explicitly allowed per project

<!-- TODO: Expand with CI_JOB_TOKEN scope configuration and API trigger patterns -->

## Examples

```yaml
# Trigger downstream project
trigger_deploy:
  trigger:
    project: my-org/deploy-service
    branch: main
    strategy: depend

# Consume cross-project artifacts
consume_artifacts:
  needs:
    - project: my-org/build-service
      job: build
      ref: main
      artifacts: true
  script:
    - ls build/
```

<!-- TODO: Expand with API triggers and CI_JOB_TOKEN configuration -->

## Common Patterns

- `trigger:project` for downstream multi-project pipelines
- `needs:project` for cross-project artifact consumption
- `include:project` for shared template libraries with `ref:` pinning

## Anti-Patterns

- Circular multi-project triggers — causes infinite pipeline loops
- Not scoping `CI_JOB_TOKEN` access appropriately — overly permissive

## Practitioner Pain Points

<!-- TODO: Expand with deeper research -->

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [../pipelines/downstream.md](../pipelines/downstream.md) — downstream pipeline types
- [notifications.md](notifications.md) — pipeline notification integrations
- [../jobs/artifacts.md](../jobs/artifacts.md) — artifact configuration

## Sources

- [GitLab downstream pipelines](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/)
- Context card: NEW-18


<!-- TODO: Expand with deeper research -->
