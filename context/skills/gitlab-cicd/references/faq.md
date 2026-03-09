---
name: faq-and-common-gotchas
description: Top 25+ gotchas across rules, YAML syntax, variables, caching, runner, and pipelines — with fixes
---

# FAQ & Common Gotchas

> **Scope:** Top 25+ gotchas across rules, YAML syntax, variables, caching, runner, and pipelines — with fixes
> **GitLab version:** 9.0+
> **Source cards:** Aggregated from GL-1, WF-1, JB-2, RN-1, RN-2, SR-1, NEW-20 (no dedicated card)
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- Diagnosing unexpected CI pipeline behavior
- Debugging YAML syntax errors, rules evaluation, or cache misses
- Answering "why isn't my pipeline running?" or "why does my job run twice?"
- Quick reference for known gotchas before writing pipeline config

## Key Concepts

This file uses a categorized Q&A format instead of the standard reference structure. Each gotcha table below serves as the "Key Concepts" for its category. For deep-dive reference on any topic, follow the links in Related Topics.

## YAML Syntax Gotchas

| # | Gotcha | Fix |
|---|---|---|
| 1 | **Invalid badge link syntax** — link/image markdown broken in badges | Use `[![badge](image_url)](link_url)` format |
| 2 | **UTF-8 BOM in `.gitlab-ci.yml`** — parser chokes on invisible byte-order mark | Re-save file as UTF-8 without BOM |
| 3 | **`!reference` tag fails** — processed by YAML parser as type | Must be in correct position; cannot be used inside `script:` inline |
| 4 | **YAML anchors don't work across files** — anchors are file-scoped | Use `!reference` or `extends:` for cross-file reuse |
| 5 | **`extends:` merge order surprises** — deep merge replaces arrays | Arrays (like `script:`) are replaced, not appended. Use `!reference` to combine |
| 6 | **Nested `script:` blocks too deep** — max 10 levels | Flatten script blocks; extract to shell scripts |
| 7 | **"Parsed YAML is too big"** — pipeline YAML exceeds size limit | Split config with `include:`; reduce duplication |

## Rules & Pipeline Control Gotchas

| # | Gotcha | Fix |
|---|---|---|
| 1 | **`changes:` evaluates to `true` on new branches** — no base to compare | Add `if: $CI_PIPELINE_SOURCE == "merge_request_event"` before `changes:` |
| 2 | **Pipeline not starting** — no matching rules | Check `workflow:rules` and job `rules:` — at least one must match |
| 3 | **Duplicate pipelines** — branch + MR pipelines fire | Use `workflow:rules` with `$CI_PIPELINE_SOURCE` filter (see pattern below) |
| 4 | **Mixing `rules:` and `only:/except:`** — error | Cannot mix in the same job. Migrate to `rules:` exclusively |
| 5 | **Variable expansion in `rules:if`** — `$VAR == "value"` fails | Use `==` (not `=`). Variables expand but complex expressions need `=~` for regex |
| 6 | **`CI_MERGE_REQUEST_*` unavailable in branch pipeline** — only in MR pipelines | Use `workflow:rules` to force MR pipelines, or check `$CI_PIPELINE_SOURCE` |

## Caching & Artifacts Gotchas

| # | Gotcha | Fix |
|---|---|---|
| 1 | **Cache scope confusion** — cache is per-runner by default, not global | Set `key:` to control scope; distributed cache needs S3/GCS backend |
| 2 | **Artifacts vs. cache mix-up** — different retention/scope | **Artifacts:** passed between stages, uploaded to GitLab. **Cache:** optimization hint, may be absent |
| 3 | **Cross-pipeline artifact download** — `needs:project` syntax tricky | `needs: [{ project: "group/project", job: "build", ref: "main", artifacts: true }]` — 64K+ views on SO |
| 4 | **Artifact storage costs** — large artifacts eat quota | Set `expire_in:` on artifacts; use cache for dependencies |

## Runner Gotchas

| # | Gotcha | Fix |
|---|---|---|
| 1 | **Docker-in-Docker requires `privileged: true`** — security risk | Use `docker` executor with bind-mounted Docker socket, or Kaniko for builds |
| 2 | **`if-not-present` pull policy** — cache poisoning risk | Use `always` pull policy in shared environments |
| 3 | **`helper_image` version mismatch** — runner/helper version skew | Pin `helper_image` to match runner version |
| 4 | **Runner on application machine** — shared resources | Dedicated runner VMs; never share with production workloads |
| 5 | **"Failed to pull image"** — auth or network issue | Check `DOCKER_AUTH_CONFIG`, registry credentials, network access |

## Git Gotchas

| # | Gotcha | Fix |
|---|---|---|
| 1 | **Shallow clone breaks tools** — `GIT_DEPTH: 20` default | Set `GIT_DEPTH: 0` for semantic-release, blame, changelog generators |
| 2 | **Cannot push from CI** — auth failure | Use `GITLAB_TOKEN` with `write_repository` scope; configure git remote URL |
| 3 | **Submodule auth failure** — relative URLs or missing credentials | Use `GIT_SUBMODULE_STRATEGY: recursive` + `GIT_SUBMODULE_FORCE_HTTPS: "true"` |

## Semantic Release Gotchas

| # | Gotcha | Fix |
|---|---|---|
| 1 | **Token scopes insufficient** — `verifyConditions` fails | `GITLAB_TOKEN` needs `api` + `write_repository` scopes |
| 2 | **`[skip ci]` in release commit** — tag pipeline suppressed | Remove `[skip ci]` from commit message template or use `[skip ci on prod]` |
| 3 | **`${version}` in tag format** — CI interprets `$` | Use `$${version}` (double dollar sign) |
| 4 | **Plugin version incompatibility** — `conventional-changelog-conventionalcommits` v8 breaks | Upgrade to semantic-release v24+ |

## Pipeline Messages

| Message | Cause | Fix |
|---|---|---|
| "Checking pipeline status" spinner | Pipeline hasn't been created yet | Wait; check `workflow:rules` if stuck |
| "Checking merge ability" | MR merge checks running | Normal behavior; wait for checks to complete |
| "Project not found or access denied" | Token lacks access to project | Verify token scopes and project membership |
| "Many jobs failed to start" | Runner capacity exhausted | Check runner fleet; scale up or add tags |
| "Identity verification required" | New account on gitlab.com | Complete identity verification in user settings |

## Debugging Techniques

| Technique | When to Use |
|---|---|
| **Pipeline Editor / CI Lint** | Validate YAML syntax before committing |
| **`CI_DEBUG_TRACE: "true"`** | Expose all variable values and shell trace (avoid on protected branches!) |
| **`printenv \| sort`** in `before_script` | List available environment variables at runtime |
| **Run container locally** | Reproduce failures: `docker run -it <image> bash` |
| **GitLab Duo Root Cause Analysis** | AI-powered failure analysis (GitLab 16.2+ Ultimate) |
| **Save reports as artifacts** | `artifacts: reports: { junit: report.xml }` for test visibility |

## Examples

### Preventing Duplicate Pipelines

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never
    - if: $CI_COMMIT_BRANCH
```

### Debugging Variables in a Job

```yaml
debug-vars:
  stage: .pre
  script:
    - printenv | sort
    - echo "Pipeline source = $CI_PIPELINE_SOURCE"
    - echo "MR IID = $CI_MERGE_REQUEST_IID"
  rules:
    - if: $CI_DEBUG_TRACE == "true"
```

## Version Notes

| Version | Change |
|---|---|
| 13.0 | `rules:` became recommended over `only:/except:` |
| 14.0 | Tags API removed — semantic-release plugin ≥ 6.0.7 required |
| 16.2 | GitLab Duo Root Cause Analysis (Ultimate) |

## Decision Guide

| Symptom | Check Order |
|---|---|
| Pipeline not running | `workflow:rules` → job `rules:` → branch protection → runner availability |
| Job runs when it shouldn't | `rules:` evaluation order → `changes:` on new branches → default `when: on_success` |
| Cache miss | `key:` mismatch → runner affinity → distributed cache config → `policy: pull` |
| "Parsed YAML is too big" | Count includes → reduce duplication → split config files |
| Duplicate pipelines | Add `workflow:rules` with `CI_OPEN_MERGE_REQUESTS` guard |

## Related Topics

- [variables/precedence.md](variables/precedence.md) — Variable override and expansion rules
- [variables/scopes.md](variables/scopes.md) — Variable expansion contexts
- [pipelines/merge-request.md](pipelines/merge-request.md) — MR pipeline types and duplicate prevention
- [jobs/git-strategies.md](jobs/git-strategies.md) — GIT_DEPTH and clone strategies
- [semantic-release/gitlab-integration.md](semantic-release/gitlab-integration.md) — Token and plugin configuration
- [runner/security.md](runner/security.md) — DinD and pull policy risks

## Sources

- [GitLab CI/CD FAQ](https://docs.gitlab.com/ci/debugging/)
- [GitLab CI/CD Troubleshooting](https://docs.gitlab.com/ci/jobs/job_troubleshooting/)
- [Stack Overflow — gitlab-ci tag](https://stackoverflow.com/questions/tagged/gitlab-ci)

