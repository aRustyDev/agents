---
name: merge-request-pipelines
description: MR pipelines, detached/merged results, merge trains, fork handling, and duplicate prevention
---

# Merge Request Pipelines

> **Scope:** MR pipelines, detached/merged results, merge trains, fork handling, and duplicate prevention
> **GitLab version:** 11.6+
> **Source cards:** NEW-08
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You need pipelines that run specifically for merge requests
- You want to test the actual merge result before merging (merged results pipelines)
- You need serialized merging with merge trains
- You're dealing with duplicate branch + MR pipeline issues
- You need to handle fork contributions safely

**Do NOT use when:**
- Your project only uses branch pipelines with no MR workflow

## Key Concepts

### Three MR-Related Pipeline Types

| Type | Trigger | Runs On | Notes |
|---|---|---|---|
| **MR pipeline (detached)** | `CI_PIPELINE_SOURCE == "merge_request_event"` | Source branch code only | Created when MR is created/updated; labeled "detached" |
| **Merged results pipeline** | Same trigger, with project setting enabled | Merge of source + target (temporary merge ref) | Tests actual merge result before it happens |
| **Merge train pipeline** | User clicks "Set to auto-merge" | Source + target + all preceding MR changes combined | Max 20 parallel pipelines; additional MRs queued |

### Duplicate Pipeline Prevention

The #1 pain point (16k SO views). Without explicit `workflow:rules`, both a branch pipeline AND an MR pipeline are created for every push to a branch with an open MR.

**Recommended 3-rule workflow pattern:**

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'  # 1. Run MR pipelines
    - if: '$CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS'  # 2. Skip branch pipeline when MR exists
      when: never
    - if: '$CI_COMMIT_BRANCH || $CI_COMMIT_TAG'           # 3. Run branch/tag pipelines normally
```

### Merge Train Workflow

When multiple MRs are queued:
1. **MR A:** pipeline runs on A + target
2. **MR B:** pipeline runs on A + B + target (simultaneously)
3. **MR C:** pipeline runs on A + B + C + target (simultaneously)
4. If B fails → B removed → C restarts on A + C + target
5. If A succeeds → A merges → C continues with A merged

- Max parallel: 20 pipelines per train
- No limit on queued MRs waiting to join train
- Skip merge train available (experimental, 16.5+; GA 16.10+) — merges without restarting train

### Fork Pipeline Security

- Fork MR pipelines use **source (fork) project** CI content
- Protected variables and runners are **NOT available** to fork MR pipelines
- Parent project members can trigger pipeline in parent context (uses parent `.gitlab-ci.yml`)
- **Security warning:** Fork MR pipelines can contain malicious code — review before triggering

### Prerequisites

- Pipeline must have `rules` matching `CI_PIPELINE_SOURCE == "merge_request_event"`
- Rules in `include:` files do NOT satisfy this — must be in `.gitlab-ci.yml` directly
- For merged results: enable in project Settings → Merge requests → Merge options
- For merge trains: enable "Enable merge trains" (requires merged results enabled first)

## Examples

### Standard MR Pipeline with Duplicate Prevention

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH || $CI_COMMIT_TAG

test:
  script: echo "Runs in both branch and MR pipelines"

mr-only-job:
  script: echo "MR label = $CI_MERGE_REQUEST_LABELS"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### Job-Level MR Pipeline with File Changes

```yaml
lint:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        - "**/*.py"
  script: pylint src/
```

### Pipeline-Type Detection with Variables

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      variables:
        PIPE_MODE: MR
    - if: $CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_TAG
      variables:
        PIPE_MODE: TAG
    - if: $CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      variables:
        PIPE_MODE: RELEASE
```

### Merge Train Drop Recovery with Retry

```yaml
flaky-test:
  retry:
    max: 2
    when: script_failure
  script: pytest tests/
  # Without retry, flaky failure drops MR from train entirely
```

## Common Patterns

- **3-rule `workflow:rules` pattern** for duplicate prevention (MR + never-when-open + branch/tag)
- **`CI_PIPELINE_SOURCE == "merge_request_event"`** in `rules:if` for MR-specific jobs
- **`CI_OPEN_MERGE_REQUESTS`** to suppress branch pipeline when MR exists
- **Merged results pipelines** for pre-merge testing (catches integration conflicts)
- **Merge trains** with `retry:` keyword for flaky test resilience
- **`CI_MERGE_REQUEST_EVENT_TYPE`** for sub-typing MR pipeline behavior

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Running duplicate branch + MR pipelines | Wastes CI resources (2× compute) | Use 3-rule workflow pattern |
| Using `CI_MERGE_REQUEST_*` without guarding | Variables empty in non-MR pipelines | Guard with `rules:if: $CI_PIPELINE_SOURCE == "merge_request_event"` |
| Trusting fork MR pipelines with protected variables | Fork code is untrusted — can exfiltrate secrets | Disable protected variable access; require parent member to trigger |
| Not handling detached pipeline variable differences | Some vars behave differently in detached vs branch pipelines | Check MR variable availability table |

## Practitioner Pain Points

1. **Duplicate branch + MR pipelines** (16k SO views) — Without explicit `workflow:rules`, both pipeline types are created. **Fix:** Use the 3-rule workflow pattern. [SO #70290807](https://stackoverflow.com/questions/70290807)

2. **`CI_MERGE_REQUEST_*` unavailable in non-MR pipelines** — These 22 variables only exist when `CI_PIPELINE_SOURCE == "merge_request_event"`. **Fix:** Guard with `rules:if` check; use `CI_COMMIT_BRANCH` for branch pipeline context.

3. **Merge train failure drops MR and restarts subsequent MRs** — All subsequent train pipelines depend on the failing MR's changes. **Fix:** Use `retry:` for flaky tests; fix root cause quickly.

4. **Protected variables not available to fork MR pipelines** — Security by design. **Workaround:** Have parent project members trigger pipeline, or use separate post-merge pipeline for secure operations.

## Version Notes

| Version | Change |
|---|---|
| 11.6 | Merge request pipelines introduced |
| 13.4 | Merged results pipelines available |
| 16.0 | "Start merge train" → "Set to auto-merge" UI rename |
| 16.5 | Fast-forward/semi-linear merge train support; skip merge train (flag) |
| 17.2 | Auto-merge for merge trains (flag) |
| 17.7 | Auto-merge for merge trains GA (flag removed) |

## Decision Guide

| Scenario | Recommendation |
|---|---|
| Standard team, prevent duplicate pipelines | 3-rule `workflow:rules` pattern |
| Verify merge compatibility before merging | Enable merged results pipelines (project setting) |
| High-traffic default branch protection | Merge trains with adequate CI capacity (max 20 parallel) |
| Fork contributions with security | Disable protected variable access; require parent member to trigger |
| Emergency hotfix during active merge train | "Merge immediately" (cancels/restarts train) or `skip_merge_train` API (experimental) |

## Related Topics

- [../variables/predefined.md](../variables/predefined.md) — `CI_MERGE_REQUEST_*` variables (22 total, MR-only)
- [../yaml/workflow-rules.md](../yaml/workflow-rules.md) — `workflow:rules` for pipeline-type control
- [types-and-triggers.md](types-and-triggers.md) — All pipeline source types
- [downstream.md](downstream.md) — Parent-child pipeline interactions with MR pipelines

## Sources

- [GitLab MR Pipelines](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/)
- [GitLab Merge Trains](https://docs.gitlab.com/ci/pipelines/merge_trains/)
- [SO: Duplicate Pipeline Prevention](https://stackoverflow.com/questions/70290807)

