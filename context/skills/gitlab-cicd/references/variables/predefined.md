---
name: predefined-variables
description: 170+ predefined CI/CD variables organized by category with availability and version notes
---

# Predefined Variables

> **Scope:** 170+ predefined CI/CD variables organized by category with availability and version notes
> **GitLab version:** 9.0+
> **Source cards:** VA-1
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You need branch, tag, project, or pipeline metadata in CI job scripts
- You want to avoid hardcoding values that GitLab already provides
- You need auth tokens for cross-project access or container registry
- You need to detect the pipeline trigger type for conditional logic

**Do NOT use when:**
- A custom variable better represents your intent (avoid overloading predefined vars)
- `CI_MERGE_REQUEST_*` vars are needed outside `merge_request_event` pipelines (they're empty)

## Key Concepts

### Variable Categories (170+ total)

| Category | Count | Key Variables |
|---|---|---|
| Commit | 16 | `CI_COMMIT_BRANCH`, `CI_COMMIT_REF_NAME`, `CI_COMMIT_SHA`, `CI_COMMIT_SHORT_SHA`, `CI_COMMIT_TAG`, `CI_COMMIT_REF_SLUG` |
| Pipeline | 10 | `CI_PIPELINE_ID`, `CI_PIPELINE_IID`, `CI_PIPELINE_SOURCE`, `CI_PIPELINE_URL`, `CI_PIPELINE_NAME` |
| Job | 13 | `CI_JOB_ID`, `CI_JOB_NAME`, `CI_JOB_STAGE`, `CI_JOB_TOKEN`, `CI_JOB_URL`, `CI_JOB_MANUAL` |
| Project | 14 | `CI_PROJECT_ID`, `CI_PROJECT_NAME`, `CI_PROJECT_PATH`, `CI_PROJECT_URL`, `CI_PROJECT_DIR` |
| Merge Request | 22 | `CI_MERGE_REQUEST_IID`, `CI_MERGE_REQUEST_SOURCE_BRANCH_NAME`, `CI_MERGE_REQUEST_TARGET_BRANCH_NAME`, `CI_MERGE_REQUEST_LABELS` |
| Registry | 4 | `CI_REGISTRY`, `CI_REGISTRY_IMAGE`, `CI_REGISTRY_USER`, `CI_REGISTRY_PASSWORD` |
| Runner | 7 | `CI_RUNNER_ID`, `CI_RUNNER_DESCRIPTION`, `CI_RUNNER_TAGS`, `CI_RUNNER_EXECUTABLE_ARCH` |
| Server | 14 | `CI_SERVER_URL`, `CI_SERVER_HOST`, `CI_SERVER_VERSION`, `CI_SERVER_FQDN` |
| Environment | 6 | `CI_ENVIRONMENT_NAME`, `CI_ENVIRONMENT_SLUG`, `CI_ENVIRONMENT_URL`, `CI_ENVIRONMENT_TIER` |
| Dependency Proxy | 5 | `CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX`, `CI_DEPENDENCY_PROXY_USER` |
| Deploy Token | 2 | `CI_DEPLOY_USER`, `CI_DEPLOY_PASSWORD` |
| External PR | 7 | `CI_EXTERNAL_PULL_REQUEST_IID`, `CI_EXTERNAL_PULL_REQUEST_SOURCE_BRANCH_NAME` |
| Upstream Pipeline | 3 | `CI_UPSTREAM_JOB_ID`, `CI_UPSTREAM_PIPELINE_ID`, `CI_UPSTREAM_PROJECT_ID` (18.9+) |
| Other | 16 | `CI`, `GITLAB_CI`, `CI_CONFIG_PATH`, `CI_DEFAULT_BRANCH`, `CI_DEBUG_TRACE`, `KUBECONFIG` |

> **MR variables caveat:** The 22 `CI_MERGE_REQUEST_*` variables are **only** populated when
> `CI_PIPELINE_SOURCE == "merge_request_event"`. Guard any MR-variable usage with a matching rule.

### Availability Levels

Variables become available at different pipeline lifecycle stages:

| Level | Description | Example Variables | Usable In |
|---|---|---|---|
| Pre-pipeline | Available before pipeline creates jobs | `CI_COMMIT_BRANCH`, `CI_PIPELINE_SOURCE`, `CI_PROJECT_ID`, `CI_DEFAULT_BRANCH` | `rules:if`, `workflow:rules`, `include:` |
| Pipeline | Available after pipeline creation | `CI_JOB_NAME`, `CI_JOB_STAGE`, `CI_ENVIRONMENT_NAME`, `CI_NODE_INDEX` | Job `variables:`, `script:` |
| Job-only | Available only during job execution | `CI_JOB_TOKEN`, `CI_JOB_ID`, `CI_PROJECT_DIR`, `CI_BUILDS_DIR`, `CI_RUNNER_ID` | `script:` only — NOT in `rules:if` or `include:` |

> **Critical:** Job-only variables like `CI_JOB_TOKEN` are _persisted variables_ — they cannot be
> used in `rules:if`, `include:`, or any GitLab-internal expansion context.
> See [scopes.md](scopes.md) for the full expansion matrix.

## Examples

### Branch-Aware Deployment

```yaml
deploy-staging:
  stage: deploy
  script:
    - echo "Deploying $CI_COMMIT_SHORT_SHA to staging"
    - echo "Project: $CI_PROJECT_NAME ($CI_PROJECT_ID)"
    - echo "Pipeline: $CI_PIPELINE_URL"
  environment:
    name: staging
    url: https://staging.$CI_PROJECT_NAME.example.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Pipeline Source Branching

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_PIPELINE_SOURCE == "schedule"
      variables:
        DEPLOY_ENV: "nightly"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG

test:
  script: echo "Running tests for $CI_PIPELINE_SOURCE pipeline"
```

### Container Registry Build

```yaml
build-image:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
```

## Common Patterns

- **Branch/tag detection:** Use `CI_COMMIT_REF_NAME` (always set). `CI_COMMIT_BRANCH` is empty for tags; `CI_COMMIT_TAG` is empty for branches.
- **Trigger-type branching:** Use `CI_PIPELINE_SOURCE` — values include `push`, `merge_request_event`, `schedule`, `api`, `trigger`, `pipeline`, `parent_pipeline`, `web`.
- **Working directory anchor:** Use `CI_PROJECT_DIR` as the workspace root path.
- **Cross-project auth:** Use `CI_JOB_TOKEN` for artifact fetching and API calls — valid only while the job runs.
- **Docker tagging:** Use `$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA` for builds, `:latest` for default branch.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Hardcoding values that predefined vars provide | Breaks portability across projects/branches | Use the corresponding `CI_*` variable |
| Using `CI_MERGE_REQUEST_*` outside MR pipelines | Variables are empty — jobs silently misbehave | Guard with `rules: - if: $CI_PIPELINE_SOURCE == "merge_request_event"` |
| Assuming `CI_COMMIT_BRANCH` is set in tag pipelines | It's empty for tags — only `CI_COMMIT_TAG` is set | Use `CI_COMMIT_REF_NAME` for branch-or-tag contexts |
| Overriding predefined variables with custom values | May cause unexpected pipeline behavior | Use a different variable name |
| Depending on undocumented internal variables | Break without notice across GitLab upgrades | Use only documented `CI_*` / `GITLAB_*` vars |

## Practitioner Pain Points

1. **`CI_MERGE_REQUEST_*` empty in branch pipelines** — These 22 variables require `pipeline_source=merge_request_event`. Use `workflow:rules` to ensure MR pipeline runs when needed.

2. **`CI_COMMIT_BRANCH` vs `CI_COMMIT_REF_NAME` confusion** — In tag pipelines, `CI_COMMIT_BRANCH` is empty. `CI_COMMIT_REF_NAME` always resolves to the branch or tag name.

3. **`CI_COMMIT_BEFORE_SHA` is all zeros** — For MR pipelines, scheduled pipelines, and first commits, this variable is `0000000000000000000000000000000000000000`. Don't rely on it for diff calculations in these contexts.

4. **`CI_OPEN_MERGE_REQUESTS` limited to 4** — Only returns up to 4 open MRs. Not suitable for monorepos with many concurrent MRs targeting the same branch.

5. **`CI_DEBUG_TRACE` exposes secrets** — Setting `CI_DEBUG_TRACE=true` logs ALL variables, including masked ones. Never enable on production runners without understanding the risk. See [masking-protection.md](masking-protection.md).

6. **Predefined variable availability differs by pipeline type** — Schedule pipelines don't set `CI_MERGE_REQUEST_*`; tag pipelines don't set `CI_COMMIT_BRANCH`. Always check the availability level before assuming a variable exists.

## Version Notes

| Version | Change |
|---|---|
| 15.5+ | `CI_COMMIT_TAG_MESSAGE` and `CI_RELEASE_DESCRIPTION` added for tag pipelines |
| 16.3+ | `CI_PIPELINE_NAME` added (populated from `workflow:name`) |
| 17.0+ | `CI_TRIGGER_SHORT_TOKEN` added (first 4 chars of trigger token) |
| 17.10+ | `CI_JOB_GROUP_NAME` added for parallel/grouped jobs |
| 18.6+ | `CI_COMMIT_MESSAGE_IS_TRUNCATED` added (100KB default message limit) |
| 18.9+ | `CI_UPSTREAM_JOB_ID`, `CI_UPSTREAM_PIPELINE_ID`, `CI_UPSTREAM_PROJECT_ID` for parent-child context |

## Decision Guide

| Scenario | Recommendation |
|---|---|
| Need the branch or tag name | Use `CI_COMMIT_REF_NAME` (always set). Use `CI_COMMIT_BRANCH`/`CI_COMMIT_TAG` only when you need to distinguish. |
| Need to detect pipeline trigger type | Use `CI_PIPELINE_SOURCE`. Values: `push`, `merge_request_event`, `schedule`, `api`, `trigger`, `pipeline`, `parent_pipeline`, `web`. |
| Need MR metadata (title, labels, source branch) | Use `CI_MERGE_REQUEST_*` — but ONLY in MR pipelines. Guard with `rules: - if: $CI_PIPELINE_SOURCE == "merge_request_event"`. |
| Cross-project artifact access | Use `CI_JOB_TOKEN` for authentication. It's Job-only and valid only while the job runs. |
| Docker image tagging | Use `$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA` for builds. Use `:latest` tag for default branch builds. |

## Related Topics

- [precedence.md](precedence.md) — How predefined variables rank in the 11-level hierarchy (lowest)
- [scopes.md](scopes.md) — Where predefined variables can be expanded (rules, script, services, etc.)
- [masking-protection.md](masking-protection.md) — Protecting sensitive predefined variable values
- [../pipelines/types-and-triggers.md](../pipelines/types-and-triggers.md) — Pipeline types that determine which variables are populated

## Sources

- [GitLab Predefined Variables Reference](https://docs.gitlab.com/ci/variables/predefined_variables/)
- [GitLab CI/CD Variables](https://docs.gitlab.com/ci/variables/)
- [Where Variables Can Be Used](https://docs.gitlab.com/ci/variables/where_variables_can_be_used/)

