---
name: workflow-rules
description: workflow:rules, auto_cancel, and pipeline naming patterns
---

# Workflow Rules

> **Scope:** workflow:rules, auto_cancel, and pipeline naming patterns
> **GitLab version:** 12.5+
> **Source cards:** WF-1
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Controlling when pipelines are created (pipeline-level gating)
- Preventing duplicate branch + MR pipelines
- Setting pipeline-wide variables via `workflow:rules:variables`
- Configuring auto-cancel behavior for outdated pipelines
- Naming pipelines dynamically with `workflow:name`

## Key Concepts

### workflow:rules

Evaluated **before any job rules**. Determines whether a pipeline is created at all.

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
    - if: $CI_COMMIT_TAG
```

This is the **standard 3-rule pattern** to prevent duplicate pipelines: run MR pipelines, suppress branch pipelines when MR exists, run branch/tag pipelines otherwise.

### workflow:rules:variables

Set or override variables at the pipeline level based on rules:

```yaml
workflow:
  rules:
    - if: $CI_COMMIT_TAG
      variables:
        IS_RELEASE: "true"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      variables:
        IS_MR: "true"
    - when: always
```

> **Warning:** `workflow:rules:variables` affect **all jobs** — they override job-level defaults.

### workflow:name

Dynamic pipeline naming for dashboard clarity:

```yaml
workflow:
  name: "$CI_PIPELINE_SOURCE: $CI_COMMIT_REF_NAME"
```

### Auto-Cancel

| Setting | Values | Purpose |
|---|---|---|
| `auto_cancel:on_new_commit:` | `conservative`, `interruptible`, `none` | Cancel outdated pipelines on push |
| `auto_cancel:on_job_failure:` | `none`, `all` | Cancel pipeline on first failure |
| Per-rule `auto_cancel:` | Override per `workflow:rules` entry | Different cancel behavior per context |

```yaml
workflow:
  auto_cancel:
    on_new_commit: interruptible
  rules:
    - if: $CI_COMMIT_TAG
      auto_cancel:
        on_new_commit: none  # Never cancel tag pipelines
    - when: always
```

### Common if Clauses

| Variable | Check |
|---|---|
| `$CI_PIPELINE_SOURCE` | Pipeline trigger type |
| `$CI_COMMIT_BRANCH` | Branch name (absent on tags) |
| `$CI_COMMIT_TAG` | Tag name (absent on branches) |
| `$CI_OPEN_MERGE_REQUESTS` | Open MR exists for branch |
| `$CI_MERGE_REQUEST_DRAFT` | MR is draft/WIP |

## Examples

### Prevent Duplicate Pipelines

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
    - if: $CI_COMMIT_TAG
```

### Skip Draft MR Pipelines

```yaml
workflow:
  rules:
    - if: $CI_MERGE_REQUEST_DRAFT
      when: never
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
```

### Git Flow Pattern

```yaml
workflow:
  name: "$CI_PIPELINE_SOURCE - $CI_COMMIT_REF_NAME"
  auto_cancel:
    on_new_commit: interruptible
  rules:
    - if: $CI_COMMIT_TAG
      variables:
        DEPLOY_ENV: production
    - if: $CI_COMMIT_BRANCH == "main"
      variables:
        DEPLOY_ENV: staging
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH
```

## Common Patterns

- **3-rule duplicate prevention** — MR → suppress branch-with-MR → branch/tag
- **`workflow:name`** with `CI_COMMIT_REF_NAME` for identifiable pipelines
- **`auto_cancel:on_new_commit: interruptible`** for fast feedback loops
- **`workflow:rules:variables`** to set `DEPLOY_ENV` based on branch/tag context
- **Skip draft MRs** with `$CI_MERGE_REQUEST_DRAFT` check

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| No `workflow:rules` | Duplicate branch + MR pipelines | Add 3-rule pattern |
| Overly complex workflow:rules | Hard to reason about | Keep to 3–5 rules max |
| Forgetting `workflow:rules:variables` affect all jobs | Unexpected variable values | Document and review pipeline-level vars |
| `auto_cancel` on deployment pipelines | Cancels in-progress deployments | Use `interruptible: false` on deploy jobs |

## Practitioner Pain Points

1. **"Checking pipeline status" spinner** — usually caused by `workflow:rules` not matching any condition. Ensure at least one rule matches.
2. **`CI_OPEN_MERGE_REQUESTS` timing** — variable may not be set for the very first push before MR is created.
3. **`workflow:rules` vs job `rules:`** — different evaluation context. `workflow:rules` runs before job rules and affects pipeline creation.
<!-- TODO: Expand with deeper research on per-rule auto_cancel overrides and complex Git Flow patterns -->

## Related Topics

- [rules-patterns.md](rules-patterns.md) — Job-level `rules:` patterns
- [../pipelines/merge-request.md](../pipelines/merge-request.md) — MR pipeline duplicate prevention
- [../pipelines/types-and-triggers.md](../pipelines/types-and-triggers.md) — CI_PIPELINE_SOURCE values

## Sources

- [workflow keyword](https://docs.gitlab.com/ci/yaml/workflow/)
- [Auto-cancel pipelines](https://docs.gitlab.com/ci/pipelines/settings/#auto-cancel-redundant-pipelines)
