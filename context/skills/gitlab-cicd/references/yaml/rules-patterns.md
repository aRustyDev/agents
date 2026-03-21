---
name: rules-patterns
description: rules:if, rules:changes, rules:exists patterns for conditional job execution
---

# Rules Patterns

> **Scope:** rules:if, rules:changes, rules:exists patterns for conditional job execution
> **GitLab version:** 12.3+
> **Source cards:** NEW-05
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Writing `rules:if`, `rules:changes`, `rules:exists` conditions
- Implementing conditional job execution based on pipeline source
- Using `compare_to:` for reliable change detection in MR pipelines
- Migrating from `only:/except:` to `rules:`

## Key Concepts

### Rules Evaluation

Rules are evaluated **top to bottom** — first matching rule wins. If no rule matches, the job is **excluded** from the pipeline.

| Clause | Purpose | Since |
|---|---|---|
| `rules:if:` | Boolean expression on variables | 12.3 |
| `rules:changes:paths:` | File path glob matching | 12.4 |
| `rules:changes:compare_to:` | Base ref for diff comparison | 16.0 |
| `rules:exists:` | File existence check | 12.4 |
| `rules:exists:project:` | Cross-project file check | 17.0+ |
| `rules:needs:` | Conditional dependency override | 16.0+ |
| `rules:interruptible:` | Per-rule interruptible override | 16.5+ |

### Common if Clauses

| Condition | Matches |
|---|---|
| `$CI_PIPELINE_SOURCE == "merge_request_event"` | MR pipelines only |
| `$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH` | Default branch pushes |
| `$CI_COMMIT_TAG` | Tag pipelines |
| `$CI_PIPELINE_SOURCE == "schedule"` | Scheduled pipelines |
| `$CI_PIPELINE_SOURCE == "web"` | Manual "Run pipeline" |
| `$CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS` | Branch push with open MR |
| `$CI_MERGE_REQUEST_DRAFT` | Draft MR (skip pattern) |

### rules:changes Gotchas

> **Critical:** On new branches with no merge base, `changes:` evaluates to **true**. Always pair with:
> - `compare_to: refs/heads/$CI_DEFAULT_BRANCH` (explicit base)
> - Or guard with `if: $CI_PIPELINE_SOURCE == "merge_request_event"`

### when: Values in Rules

| Value | Behavior |
|---|---|
| `on_success` (default) | Run if prior stages succeed |
| `manual` | Require manual trigger |
| `delayed` | Run after `start_in:` duration |
| `always` | Run regardless |
| `never` | Exclude job |

## Examples

### Standard MR + Branch + Tag Rules

```yaml
test:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG
  script: make test
```

### Path-Based with compare_to

```yaml
build-frontend:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        paths: [frontend/**/*]
        compare_to: refs/heads/$CI_DEFAULT_BRANCH
  script: cd frontend && npm run build
```

### Skip Draft MRs

```yaml
test:
  rules:
    - if: $CI_MERGE_REQUEST_DRAFT
      when: never
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script: make test
```

## Common Patterns

- **`rules:if` with `CI_PIPELINE_SOURCE`** for pipeline type filtering
- **`rules:changes` with `compare_to:`** for reliable monorepo path triggers
- **`rules:exists`** for conditional jobs based on config file presence
- **Combine `when: manual` with rules** for approval gates
- **Put `when: never` rules first** for exclusion patterns

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Mixing `only/except` and `rules:` | Error — mutually exclusive | Migrate fully to `rules:` |
| `rules:changes` without `compare_to:` or MR guard | True on new branches | Add `compare_to:` or MR condition |
| Complex nested rules without `workflow:rules` | Hard to reason about | Move pipeline-level logic to `workflow:rules` |
| Overusing experimental keywords in production | Breaking changes likely | Pin to stable features |
| No `when: never` rule for exclusion | Job runs when it shouldn't | Add explicit exclusion rules |

## Practitioner Pain Points

1. **`rules:changes` on new branches evaluates true** — #1 gotcha. Use `compare_to:` or MR pipeline guard.
2. **Rules evaluation order matters** — first match wins, not most specific. Place exclusions (`when: never`) first.
3. **`CI_MERGE_REQUEST_*` variables only available in MR pipelines** — guard with `if: $CI_PIPELINE_SOURCE == "merge_request_event"`.
<!-- TODO: Expand with deeper research on rules:needs, rules:interruptible, and hooks:pre_get_sources_script -->

## Related Topics

- [workflow-rules.md](workflow-rules.md) — Pipeline-level `workflow:rules`
- [../pipelines/merge-request.md](../pipelines/merge-request.md) — MR pipeline types
- [../pipelines/monorepo.md](../pipelines/monorepo.md) — Path-based triggering patterns

## Sources

- [rules keyword](https://docs.gitlab.com/ci/yaml/#rules)
- [CI/CD YAML reference](https://docs.gitlab.com/ci/yaml/)
