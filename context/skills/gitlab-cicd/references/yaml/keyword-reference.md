---
name: gitlab-ci-cd-keyword-reference
description: Complete .gitlab-ci.yml keyword reference — global, job, and include keywords
---

# GitLab CI/CD Keyword Reference

> **Scope:** Complete .gitlab-ci.yml keyword reference — global, job, and include keywords
> **GitLab version:** 9.0+
> **Source cards:** GL-1
> **Tier:** C
> **Last verified:** 2026-03

## When to Use

Consult this reference when you need to look up exact keyword syntax, nesting rules,
or version availability for any `.gitlab-ci.yml` keyword.

## Key Concepts

### Global Keywords

| Keyword | Purpose | Version |
|---------|---------|--------|
| `default:` | Set defaults inherited by all jobs (image, before_script, retry, etc.) | 9.0+ |
| `include:` | Import external YAML (component, local, project, remote, template) | 11.4+ |
| `stages:` | Define ordered stage names | 9.0+ |
| `variables:` | Pipeline-wide variable defaults | 9.0+ |
| `workflow:` | Control entire pipeline creation (rules, name, auto_cancel) | 12.5+ |

### Include Sub-Keywords

| Sub-keyword | Purpose | Version |
|------------|---------|--------|
| `include:component` | CI/CD Catalog component reference | 17.0+ |
| `include:local` | Same-repository file | 11.4+ |
| `include:project` | Cross-project file with `ref:` pinning | 11.4+ |
| `include:remote` | URL-based include | 11.4+ |
| `include:template` | GitLab-managed template | 11.4+ |
| `include:rules` | Conditional include evaluation | 14.2+ |
| `include:inputs` | Typed parameter passing via `spec:inputs` | 15.11+ |
| `include:integrity` | SHA256 verification of remote includes | ? |

### Job Keywords

| Category | Keywords |
|----------|----------|
| **Script** | `script`, `before_script`, `after_script` |
| **Image** | `image`, `services` |
| **Execution** | `rules`, `needs`, `dependencies`, `when`, `allow_failure` |
| **Artifacts** | `artifacts`, `cache` |
| **Deploy** | `environment`, `release`, `resource_group` |
| **Advanced** | `trigger`, `parallel`, `interruptible`, `retry`, `timeout` |
| **Experimental** | `run` (CI Steps), `hooks:pre_get_sources_script` |

<!-- TODO: Expand with complete keyword table from GitLab docs -->

### Special Keywords

- **`pages`** — `publish:`, `path_prefix:`, `expire_in:` for GitLab Pages deployment
- **`release`** — `tag_name:`, `description:`, `assets:` for release creation (integrates with `glab` CLI)

## Examples

```yaml
# Global defaults applied to all jobs
default:
  image: ruby:3.2
  before_script:
    - echo "Global setup"
  retry:
    max: 2
    when:
      - runner_system_failure
  interruptible: true

stages:
  - build
  - test
  - deploy

variables:
  APP_ENV: production
```

```yaml
# Include patterns
include:
  - component: $CI_SERVER_FQDN/my-org/components/sast@1.0.0
    inputs:
      stage: test
  - local: .ci/jobs/*.yml
    rules:
      - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  - project: shared/ci-templates
    ref: v2.1.0
    file: /templates/deploy.yml
```

## Common Patterns

- **`default:` block** for global image/before_script/retry settings — avoid duplicating per-job
- **`rules:changes:compare_to`** for reliable file-change detection against a target branch
- **`rules:exists:project`** for cross-project file existence checks
- **`interruptible: true`** on all non-deployment jobs to save resources on superseded pipelines

## Anti-Patterns

- **Not using `default:` block** — duplicating image/retry/tags across every job
- **Mixing `rules` with `only/except`** — causes confusing evaluation behavior; `only/except` is deprecated
- **Not setting `interruptible`** on long-running non-critical jobs — wastes compute on stale pipelines

## Related Topics

- [yaml-composition.md](yaml-composition.md) — YAML reuse: anchors, extends, !reference
- [rules-patterns.md](rules-patterns.md) — rules clause reference and patterns
- [workflow-rules.md](workflow-rules.md) — workflow:rules for pipeline-level control
- [../components/authoring.md](../components/authoring.md) — CI/CD component authoring with spec:inputs

## Sources

- [GitLab CI/CD YAML reference](https://docs.gitlab.com/ci/yaml/)
- Context card: GL-1
