---
name: gitlab-cicd
description: Expert-level guidance for GitLab CI/CD pipeline configuration, development, optimization, debugging, and best practices.
version: 1.0.0
globs:
  - "**/.gitlab-ci.yml"
  - "**/.gitlab-ci.yaml"
  - "**/ci/**/*.yml"
  - "**/.gitlab/**/*.yml"
  - "**/templates/**/*.yml"
  - "**/.releaserc*"
  - "**/release.config.*"
---

# GitLab CI/CD

Expert-level guidance for GitLab CI/CD pipeline configuration, development, optimization, debugging, and best practices. Covers GitLab 9.0 through 18.x with version-specific annotations.

## When to Use This Skill

- Configuring or modifying `.gitlab-ci.yml` files
- Debugging pipeline failures or unexpected job behavior
- Optimizing pipeline performance and compute minutes
- Setting up CI/CD components and include templates
- Managing runner infrastructure and autoscaling
- Implementing deployment strategies and environment lifecycle
- Configuring secrets, security scanning, and compliance
- Implementing semantic-release automation

## Do Not Use This Skill When

- Working with **GitHub Actions** or other non-GitLab CI systems
- Managing **GitLab instance administration** (not CI/CD pipeline config)
- Writing application code unrelated to CI/CD

---

## Quick Reference — Top 20 Keywords

| Keyword | Purpose | Detail |
|---------|---------|--------|
| `script` | Commands to execute in a job | Required for every job unless `trigger` is used |
| `rules` | Conditional job inclusion | Replaces deprecated `only/except`. See [rules-patterns](references/yaml/rules-patterns.md) |
| `needs` | DAG dependency declaration | Jobs run as soon as dependencies finish, ignoring stage order |
| `variables` | Define CI/CD variables | Scoped to job, pipeline, or global. See [variable scopes](references/variables/scopes.md) |
| `include` | Import external YAML | Types: `local`, `project`, `remote`, `template`, `component` |
| `extends` | Inherit from hidden jobs | Up to 11 levels deep; merged with job config |
| `cache` | Persist files between jobs | Use `cache:key:files` for content-addressable caching |
| `artifacts` | Pass files between stages | `expire_in`, `expose_as`, access control. See [artifacts](references/jobs/artifacts.md) |
| `image` | Docker image for job | Set globally via `default:image` or per-job |
| `services` | Sidecar containers | Common: `docker:dind`, database services for testing |
| `stages` | Ordered execution groups | Jobs in same stage run in parallel by default |
| `workflow` | Pipeline-level rules | Controls whether pipeline is created. See [workflow-rules](references/yaml/workflow-rules.md) |
| `trigger` | Start downstream pipeline | Parent-child (same project) or multi-project |
| `environment` | Deployment target | Tiers, `auto_stop_in`, `on_stop`. See [environments](references/pipelines/environments.md) |
| `default` | Global job defaults | `image`, `before_script`, `retry`, `interruptible` |
| `parallel` | Fan-out job execution | `parallel: N` or `parallel:matrix` for combinations |
| `retry` | Auto-retry on failure | `retry:when` for selective retry. See [retry](references/jobs/retry-resilience.md) |
| `when` | Job execution condition | `on_success`, `on_failure`, `always`, `manual`, `delayed` |
| `resource_group` | Concurrency control | Ensures only one job per group runs at a time |
| `interruptible` | Allow auto-cancel | Set `true` on non-deployment jobs for pipeline efficiency |

## Quick Reference — Top 10 Predefined Variables

| Variable | Value | Available |
|----------|-------|-----------|
| `CI_COMMIT_REF_NAME` | Branch or tag name | Always |
| `CI_COMMIT_SHA` | Full commit SHA | Always |
| `CI_PIPELINE_SOURCE` | Trigger type (`push`, `merge_request_event`, `schedule`, `api`, `trigger`) | Always |
| `CI_PROJECT_DIR` | Workspace directory path | Job only |
| `CI_JOB_TOKEN` | Auto-generated token for API calls | Job only |
| `CI_REGISTRY_IMAGE` | Container registry path | Always |
| `CI_MERGE_REQUEST_IID` | MR internal ID | MR pipelines only |
| `CI_MERGE_REQUEST_SOURCE_BRANCH_NAME` | MR source branch | MR pipelines only |
| `CI_ENVIRONMENT_NAME` | Current environment name | Deployment jobs only |
| `CI_COMMIT_BRANCH` | Branch name (not set for tags) | Branch pipelines only |

For the complete 170+ variable reference, see [predefined variables](references/variables/predefined.md).

---

## Quick-Start Example

```yaml
# Minimal pipeline — see references/ for each topic
stages: [build, test, deploy]                    # → types-and-triggers.md

variables:                                        # → variables/definition.md
  NODE_VERSION: "20"

default:
  image: node:${NODE_VERSION}
  cache:                                          # → jobs/caching.md
    key:
      files: [package-lock.json]
    paths: [node_modules/]

build:
  stage: build
  script:
    - npm ci
    - npm run build
  artifacts:                                      # → jobs/artifacts.md
    paths: [dist/]
    expire_in: 1 week

test:
  stage: test
  script: npm test
  coverage: '/Statements\s*:\s*(\d+\.?\d*)%/'    # → jobs/testing.md
  needs: [build]                                  # → jobs/execution-flow.md

deploy:
  stage: deploy
  script: ./deploy.sh
  environment:                                    # → pipelines/environments.md
    name: production
  rules:                                          # → yaml/rules-patterns.md
    - if: $CI_COMMIT_BRANCH == "main"
      when: manual
  needs: [test]
```

---

## Pipeline Configuration

GitLab supports multiple pipeline types with distinct triggering rules and variable availability.

| Pipeline Type | Trigger | Key Variable |
|---------------|---------|--------------|
| Branch pipeline | Push to branch | `CI_COMMIT_BRANCH` |
| Tag pipeline | Push tag | `CI_COMMIT_TAG` |
| MR pipeline | MR created/updated | `CI_MERGE_REQUEST_IID` |
| Merged results | MR with merged results enabled | `CI_MERGE_REQUEST_EVENT_TYPE=merged_result` |
| Merge train | MR added to merge train | `CI_MERGE_REQUEST_EVENT_TYPE=merge_train` |
| Scheduled | Cron schedule triggers | `CI_PIPELINE_SOURCE=schedule` |
| Parent-child | `trigger:include` | `CI_PIPELINE_SOURCE=parent_pipeline` |
| Multi-project | `trigger:project` | `CI_PIPELINE_SOURCE=pipeline` |

**Key gotcha:** `CI_MERGE_REQUEST_*` variables are **only** available when `CI_PIPELINE_SOURCE=merge_request_event`. Use `workflow:rules` to prevent duplicate branch+MR pipelines.

**References:**
- [Pipeline Types & Triggers](references/pipelines/types-and-triggers.md)
- [Merge Request Pipelines](references/pipelines/merge-request.md) — detached, merged results, merge trains, fork handling
- [Downstream Pipelines](references/pipelines/downstream.md) — parent-child, multi-project, dynamic child
- [Monorepo Strategies](references/pipelines/monorepo.md) — `rules:changes`, per-service child pipelines
- [Pipeline Optimization](references/pipelines/optimization.md) — DAG, parallelism, compute minutes
- [Scheduled Pipelines](references/pipelines/scheduling.md) — cron syntax, schedule-only patterns
- [Manual Gates](references/pipelines/manual-gates.md) — `when:manual`, approvals, deploy freezes
- [Cross-Project Pipelines](references/integrations/cross-project.md) — multi-project triggers, artifact sharing
- [Notifications & Badges](references/integrations/notifications.md) — pipeline badges, email/Slack integration

---

## YAML Authoring

Pipeline YAML supports composition patterns for DRY, maintainable configurations.

| Pattern | Mechanism | Scope |
|---------|-----------|-------|
| `extends` | Job inheritance (11-level deep merge) | Same file or included files |
| YAML anchors (`&`/`*`) | Same-file reference | Single file only |
| `!reference` | Cross-file array extraction | Included files (GitLab 13.0+) |
| `include` | External YAML import | local, project, remote, template, component |

**Key gotcha:** YAML anchors do NOT work across `include` boundaries — use `extends` or `!reference` instead.

**References:**
- [Keyword Reference](references/yaml/keyword-reference.md) — full .gitlab-ci.yml keyword documentation
- [Rules Patterns](references/yaml/rules-patterns.md) — `rules:if`, `rules:changes`, `rules:exists`
- [YAML Composition](references/yaml/yaml-composition.md) — anchors, extends, `!reference`, merge keys
- [Workflow Rules](references/yaml/workflow-rules.md) — `workflow:rules`, `auto_cancel`, naming
- [YAML Optimization](references/pipelines/yaml-optimization.md) — DRY pipeline design patterns

---

## Variables

Variables follow an **11-level precedence hierarchy** — knowing the order prevents hours of debugging.

**Precedence (highest → lowest):**
1. Pipeline execution policy variables
2. Scan execution policy variables
3. Pipeline variables (trigger, scheduled, manual, API)
4. Project variables (UI/API)
5. Group variables (inherited, closest subgroup wins)
6. Instance variables
7. `dotenv` report variables
8. Job-level YAML `variables:`
9. Default (global) YAML `variables:`
10. Deployment variables
11. Predefined variables

> **Note:** `trigger:forward:pipeline_variables: true` elevates parent YAML variables to pipeline variable precedence (level 3) in downstream pipelines. It is a mechanism, not a separate precedence level.

**Key gotcha:** Variables defined in `rules:variables` override job-level variables but only when that rule matches.

**References:**
- [Predefined Variables](references/variables/predefined.md) — 170+ variables by category and version
- [Variable Precedence](references/variables/precedence.md) — 11-level hierarchy with override examples
- [Masking & Protection](references/variables/masking-protection.md) — masking rules, ≥8 chars, protected scoping
- [Variable Scopes](references/variables/scopes.md) — expansion in rules vs script vs services
- [Variable Definition](references/variables/definition.md) — YAML, UI, API, `options`, `description`

---

## Jobs & Execution

| Feature | Keyword | Key Detail |
|---------|---------|------------|
| DAG execution | `needs:` | Up to 50 dependencies; ignores stage ordering |
| Parallel fan-out | `parallel:matrix:` | Generates N×M jobs from variable combinations |
| Concurrency lock | `resource_group:` | Only one job per group runs at a time |
| Test reporting | `artifacts:reports:junit:` | Parses JUnit XML into MR widgets |
| Coverage | `coverage: '/regex/'` | Extracted from job log for MR display |
| Container builds | `services: [docker:dind]` | Or use Kaniko/Buildah for rootless builds |

**Key gotcha:** `cache` is for speed (may miss); `artifacts` are for correctness (guaranteed). Don't use cache to pass build outputs between jobs — use artifacts.

**References:**
- [Testing Strategies](references/jobs/testing.md) — JUnit, coverage, quality reports
- [Caching](references/jobs/caching.md) — `cache:key:files`, fallback_keys, distributed cache
- [Artifacts](references/jobs/artifacts.md) — `expire_in`, `expose_as`, cross-pipeline sharing
- [Execution Flow](references/jobs/execution-flow.md) — `needs:`, `dependencies`, DAG patterns
- [Docker Builds](references/jobs/docker-builds.md) — DinD, Kaniko, Buildah, multi-stage
- [Git Strategies](references/jobs/git-strategies.md) — `GIT_STRATEGY`, `GIT_DEPTH`, submodules
- [Retry & Resilience](references/jobs/retry-resilience.md) — `retry:when`, `allow_failure`, timeout

---

## Runner Infrastructure

Runners execute jobs. Executor choice determines security model, performance, and isolation.

| Executor | Isolation | Best For | Autoscalable |
|----------|-----------|----------|--------------|
| Docker | Container | Most CI jobs | Yes (docker-autoscaler) |
| Kubernetes | Pod | Cloud-native, multi-container | Yes (native) |
| Shell | None | Simple scripts, host access | No |
| Docker Autoscaler | VM + Container | Cost-optimized cloud fleets | Yes |
| Instance | VM | Full isolation | Yes (fleeting) |
| VirtualBox | VM | Legacy, local testing | Yes (legacy) |

**Key gotcha:** Docker-in-Docker (`dind`) requires `privileged: true` — significant security risk. Prefer Kaniko for container builds when possible.

**References:**
- [Runner Architecture](references/runner/architecture.md) — manager model, executor types, compatibility
- [Executors](references/runner/executors.md) — Docker, K8s, shell config and comparison
- [Autoscaling](references/runner/autoscaling.md) — docker-autoscaler, fleeting, scaling policies
- [Runner Security](references/runner/security.md) — tokens, `allowed_images`, hardening
- [Performance](references/runner/performance.md) — `concurrent`, `check_interval`, tuning
- [Fleet Management](references/runner/fleet-management.md) — config.toml, Prometheus metrics

---

## CI/CD Components

Components are reusable pipeline building blocks published to the CI/CD Catalog (GitLab 17.0+).

```yaml
include:
  - component: $CI_SERVER_FQDN/my-org/my-component@1.2.0
    inputs:
      stage: test
      scan_level: full
```

**Key gotcha:** Always pin component versions (`@1.2.0` or `@1` for major). Unpinned components are a supply-chain risk.

**References:**
- [Component Authoring](references/components/authoring.md) — project structure, `spec:inputs`, Catalog
- [Catalog](references/components/catalog.md) — discovery, version pinning, evaluation
- [Inputs](references/components/inputs.md) — types, validation, defaults
- [Testing](references/components/testing.md) — self-referencing, integration tests
- [Security](references/components/security.md) — pinning audit, `include:integrity`

---

## Semantic Release

Automated versioning with `@semantic-release/gitlab` and the `to-be-continuous` component.

**Token setup:** Requires `GITLAB_TOKEN` (project access token with `api` scope) or `GL_TOKEN`. Must be masked and protected.

**Key gotcha:** Set `GIT_DEPTH: 0` in the release job — shallow clones break commit analysis.

**References:**
- [GitLab Integration](references/semantic-release/gitlab-integration.md) — plugin lifecycle, TBC, tokens
- [Configuration](references/semantic-release/configuration.md) — `.releaserc`, presets, hooks, GPG
- [Testing](references/semantic-release/testing.md) — dry-run, verification

---

## Deployment & Environments

| Strategy | Pattern | Risk | Rollback |
|----------|---------|------|----------|
| Rolling | Replace instances incrementally | Medium | Redeploy previous version |
| Blue-Green | Switch traffic between environments | Low | Switch back |
| Canary | Route % of traffic to new version | Low | Reduce to 0% |
| Feature Flags | Toggle features in-app | Lowest | Disable flag |

**Key gotcha:** Always set `auto_stop_in` on dynamic environments. Without it, review apps accumulate and leak resources.

**References:**
- [Deployment Strategies](references/deployment/strategies.md) — blue-green, canary, rolling, feature flags
- [Dynamic Environments](references/deployment/environments.md) — review apps, auto_stop, cleanup
- [Infrastructure as Code](references/deployment/infrastructure-as-code.md) — Terraform/OpenTofu, state
- [Release Automation](references/deployment/release-automation.md) — changelog, orchestration

---

## Security

| Feature | Keywords/Config | GitLab Tier |
|---------|----------------|-------------|
| Secret variables | `Settings > CI/CD > Variables` (masked + protected) | Free |
| Vault integration | `secrets:vault:` | Premium |
| OIDC/JWT auth | `id_tokens:` | Free (15.7+) |
| SAST | `include: SAST.gitlab-ci.yml` | Ultimate |
| Dependency scanning | `include: Dependency-Scanning.gitlab-ci.yml` | Ultimate |
| Container scanning | `include: Container-Scanning.gitlab-ci.yml` | Ultimate |
| Compliance frameworks | Project settings | Ultimate |

**Key gotcha:** `CI_JOB_TOKEN` default scope allows access to all reachable projects. Restrict it via `Settings > CI/CD > Token Access`.

**References:**
- [Secrets Management](references/security/secrets-management.md) — Vault, GCP, Azure, AWS, OIDC
- [Security Scanning](references/security/scanning.md) — SAST, DAST, container, dependency
- [Compliance](references/security/compliance.md) — frameworks, audit trails, governance
- [Pipeline Security](references/pipelines/security.md) — CI_JOB_TOKEN scoping, protected runners, fork safety

---

## Troubleshooting

**Debugging decision tree:**

1. **YAML syntax error?** → Use Pipeline Editor or CI Lint API
2. **Job not starting?** → Check `rules:` evaluation — View "merged YAML" in Pipeline Editor
3. **Variable not expanding?** → Check [scopes](references/variables/scopes.md) and [precedence](references/variables/precedence.md)
4. **Cache miss?** → Verify `cache:key` matches — check runner cache backend
5. **Artifact not found?** → Check `expire_in`, `dependencies:`, and `needs:artifacts:`
6. **Runner issues?** → Check tags, runner availability, executor config
7. **Need verbose output?** → Set `CI_DEBUG_TRACE=true` (⚠️ exposes secrets)

**References:**
- [Troubleshooting Guide](references/troubleshooting.md) — editor, lint, debug trace, common errors
- [FAQ & Gotchas](references/faq.md) — top 25+ categorized gotchas with fixes

---

## Output Formats

When producing specific types of analysis, use the corresponding output format spec:

| Task | Output Style |
|------|-------------|
| Analyzing MegaLinter results | [megalinter-analysis](output-styles/megalinter-analysis.md) |
| Debugging pipeline failures | [troubleshooting-report](output-styles/troubleshooting-report.md) |
| Reviewing test results | [ci-tester-report](output-styles/ci-tester-report.md) |
| Reviewing pipeline architecture | [ci-architecture-review](output-styles/ci-architecture-review.md) |

---

## Version Compatibility

Key feature introductions across GitLab versions:

| Version | Feature | Impact |
|---------|---------|--------|
| 12.5 | `workflow:rules` | Pipeline-level conditional creation |
| 13.0 | `!reference` tag | Cross-file YAML references |
| 15.3 | `rules:changes:compare_to` | Baseline comparison for `rules:changes` (GA 16.0) |
| 13.9 | `needs:` cross-stage | DAG dependencies across stages |
| 14.2 | `include:rules` | Conditional file includes |
| 15.0 | `include:integrity` | SHA-pinned includes for supply chain security |
| 15.1 | `docker-autoscaler` executor | Modern runner autoscaling (replaces docker+machine) |
| 15.7 | `id_tokens:` | OIDC/JWT for external auth (Vault, cloud providers) |
| 16.0 | `CI/CD Components` beta | Reusable pipeline building blocks |
| 16.3 | `workflow:name` | Dynamic pipeline naming |
| 16.6 | `needs:parallel:matrix` | Fan-in from matrix jobs |
| 17.0 | CI/CD Catalog GA | Component discovery and versioning |
| 17.2 | `GIT_CLONE_EXTRA_FLAGS` | Custom git clone flags + native clone FF |
| 17.4 | `include:inputs` | Pass inputs to any included file |
| 18.0 | `run:` keyword | CI Steps (experimental) — replaces `script:` model |

---

## Related Resources

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ci/)
- [.gitlab-ci.yml Reference](https://docs.gitlab.com/ci/yaml/)
- [Predefined Variables](https://docs.gitlab.com/ci/variables/predefined_variables/)
- [CI/CD Component Catalog](https://gitlab.com/explore/catalog)
- [GitLab Runner Documentation](https://docs.gitlab.com/runner/)

---

## Workspace Examples

Annotated analyses of real pipelines from this workspace:

- [MAP Terragrunt Pipeline](examples/map-pipeline.md) — component includes, MegaLinter, release automation
- [Component Include Patterns](examples/component-patterns.md) — template structure, `spec:inputs` usage
