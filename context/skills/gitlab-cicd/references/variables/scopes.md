---
name: variable-scopes
description: Variable expansion contexts — rules vs script vs services vs includes — and debugging
---

# Variable Scopes

> **Scope:** Variable expansion contexts — rules vs script vs services vs includes — and debugging
> **GitLab version:** 9.0+
> **Source cards:** VA-4
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You need to know whether a variable works in `rules:if`, `include:`, `image:`, or `script:`
- A variable is unexpectedly empty in a specific YAML context
- You need to understand the three expansion mechanisms (GitLab, Runner, Shell)
- You're debugging variable expansion with `CI_DEBUG_TRACE`
- You need to pass data between `before_script` and `after_script`

**Do NOT use when:**
- You need to understand which value wins when multiple sources define the same variable — see [precedence.md](precedence.md)

## Key Concepts

### Three Expansion Mechanisms

| Mechanism | Forms | Behavior | Supports | Does NOT Support |
|---|---|---|---|---|
| **GitLab internal** | `$variable`, `${variable}`, `%variable%` | Recursive nested expansion before sending to Runner | Project/group vars, YAML vars, triggers, schedules | Runner `config.toml` vars, script-defined vars (`export`) |
| **GitLab Runner internal** | `$variable`, `${variable}` | Single-pass using Go `os.Expand()`. For artifacts/cache uses `mvdan.cc/sh/v3/expand` (supports parameter expansion). | Project/group vars, YAML vars, `config.toml` vars, triggers | Script-defined variables (`export`) |
| **Execution shell** | Shell-dependent: `$var` (bash), `%var%` (cmd), `$env:var` (PowerShell) | Standard shell expansion — all vars available including exports | Everything the shell has access to | Varies by shell |

### Variable Expansion by YAML Keyword

| Keyword | Expansion? | Mechanism | Notes |
|---|---|---|---|
| `script`, `before_script`, `after_script` | Yes | Execution shell | Full shell expansion — all variables available |
| `image`, `services:name` | Yes | Runner | Runner internal expansion — `$variable` and `${variable}` |
| `variables` | Yes | GitLab → Runner | GitLab expands first, Runner handles unrecognized vars |
| `include` | Yes | GitLab | Limited variable set — see docs |
| `rules:if` | **No** | N/A | Must use `$variable` form. No `CI_ENVIRONMENT_SLUG`, no persisted vars. |
| `rules:changes`, `rules:exists` | **No** | GitLab | **No variable expansion at all** |
| `environment:name` | Yes | GitLab | No `CI_ENVIRONMENT_*` vars, no persisted vars |
| `environment:url` | Yes | GitLab | All job vars except Runner `config.toml` and script-defined |
| `artifacts:name/paths/exclude` | Yes | Runner | Runner internal expansion |
| `cache:key/paths/policy` | Yes | Runner | Runner internal expansion |
| `tags` | Yes | GitLab | GitLab internal expansion |
| `trigger`, `trigger:project` | Yes | GitLab | `trigger:project` expansion added in 15.3 |
| `workflow:name` | Yes | GitLab | Project/group, global, `workflow:rules:variables`, parent, trigger vars. NOT runner or job vars. |
| `resource_group` | Yes | GitLab | No `CI_ENVIRONMENT_URL`, no persisted vars |

### Persisted Variables (Restricted Expansion)

These variables are restricted for security — they can only be used in Runner expansion and shell execution:

**Pipeline-level:** `CI_PIPELINE_ID`, `CI_PIPELINE_URL`

**Job-level:** `CI_DEPLOY_PASSWORD`, `CI_DEPLOY_USER`, `CI_JOB_ID`, `CI_JOB_STARTED_AT`, `CI_JOB_TOKEN`, `CI_JOB_URL`, `CI_PIPELINE_CREATED_AT`, `CI_REGISTRY_PASSWORD`, `CI_REGISTRY_USER`, `CI_REPOSITORY_URL`

> **Critical:** Persisted variables are **NOT available** in:
> - `rules:` variable expressions
> - `include:` directives
> - `trigger` jobs (job-level persisted vars)
> - Any GitLab internal expansion context

### Shell Context Isolation

- `before_script` + `script` share the **same shell context** — `export` in `before_script` is available in `script`
- `after_script` runs in a **separate shell** — it cannot see `export`-ed variables from `before_script`/`script`
- YAML-defined variables (`variables:`) and predefined variables ARE injected into `after_script`

## Examples

### Nested Variable Expansion (GitLab Resolves Recursively)

```yaml
variables:
  BUILD_ROOT_DIR: '${CI_BUILDS_DIR}'
  OUT_PATH: '${BUILD_ROOT_DIR}/out'
  PACKAGE_PATH: '${OUT_PATH}/pkg'
# GitLab resolves recursively: PACKAGE_PATH → /output/out/pkg
```

### Shell Context Isolation — after_script Cannot See Exports

```yaml
job:
  variables:
    JOB_VAR: "available everywhere"
  before_script:
    - export MY_VAR="from before_script"
  script:
    - echo "$MY_VAR"      # works — same shell context
    - echo "$JOB_VAR"     # works — YAML variable
  after_script:
    - echo "$MY_VAR"      # EMPTY — separate shell context
    - echo "$JOB_VAR"     # works — YAML/predefined vars are injected
```

### Advanced Variable Contexts

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"      # $variable form — no expansion
      variables:
        DEPLOY_ENV: "nightly"                    # workflow:rules:variables — cascades to all jobs
    - when: always
      variables:
        DEPLOY_ENV: "development"

deploy:
  image: $CI_REGISTRY_IMAGE:latest               # Runner expansion — works
  environment:
    name: $DEPLOY_ENV                            # GitLab expansion — works
    url: https://$DEPLOY_ENV.$CI_PROJECT_NAME.example.com  # GitLab expansion
  rules:
    - if: $DEPLOY_ENV == "production"            # $variable comparison — works
    - changes:                                   # NO variable expansion here
        - deploy/**
  script:
    - echo "Deploying with token: $CI_JOB_TOKEN" # Shell expansion — persisted var works here
```

## Common Patterns

- **Group-level variables for shared secrets** — inherited by all projects in the group
- **Environment-scoped variables for per-env config** — use wildcards like `review/*`
- **Temporarily set `CI_DEBUG_TRACE=true`** to diagnose variable resolution (but see anti-patterns)
- **Use pipeline editor** to validate variable references before committing
- **Add echo statements for non-sensitive vars** when debugging expansion issues
- **Check the expansion support table** when variables appear unexpectedly empty

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Using `CI_JOB_TOKEN` in `include:` or `rules:if` | Persisted variable — not available in GitLab expansion | Use a non-persisted variable, or restructure the pipeline |
| Expecting expansion in `rules:changes` or `rules:exists` | No variable expansion supported at all | Hardcode paths, or use `rules:if` with a variable condition |
| Using `CI_ENVIRONMENT_SLUG` in `environment:name` | Not available in `environment:name` context | Use `CI_COMMIT_REF_SLUG` or another pre-pipeline variable |
| Leaving `CI_DEBUG_TRACE` enabled in production | Logs ALL variables including masked secrets | Use `debug_trace_disabled` in runner `config.toml` to prevent |
| Debugging with `echo` on masked variable values | Masked values appear as `[MASKED]` in logs — unhelpful | Verify the variable name and scope instead; check Settings UI |
| Expecting `export` from `before_script` in `after_script` | `after_script` runs in a separate shell context | Write to a file in `before_script`, read it in `after_script`; or use `artifacts:reports:dotenv` |
| Expecting variable expansion in all YAML keywords | Different keywords use different expansion mechanisms | Consult the expansion support table above |
| Using `CI_ENVIRONMENT_*` in `rules:if` | Environment vars are pipeline-level — not available pre-pipeline | Use `CI_COMMIT_BRANCH` or custom `workflow:rules:variables` instead |

## Practitioner Pain Points

1. **"Variable empty in `rules:if` but works in `script:`"** (high frequency) — `rules:if` uses GitLab internal expansion — only `$variable` form, no persisted vars, no `CI_ENVIRONMENT_*`. `script:` uses shell expansion where everything is available.

2. **"Setting group-level environment variables"** (26k SO views) — Environment scope for group variables requires **Premium+ tier**. Navigate to Group → Settings → CI/CD → Variables → Edit → Environment scope. [SO #16551](https://stackoverflow.com/questions/16551)

3. **"Variable expansion works differently in `rules:` vs `script:`"** (high frequency) — `rules:` uses GitLab internal expansion (pre-pipeline); `script:` uses shell expansion (runtime). They're fundamentally different mechanisms with different variable availability.

4. **"`CI_DEBUG_TRACE` exposes ALL variables including secrets"** (medium frequency) — By design. Debug trace logs all environment variables. **Fix:** Use `debug_trace_disabled` in runner `config.toml` to prevent enabling on sensitive runners.

5. **"`export MY_VAR` in `before_script` not available in `after_script`"** (medium frequency) — `after_script` runs in a separate shell context with no access to exports. **Fix:** Write to a file or use `artifacts:reports:dotenv` to pass data between jobs.

## Version Notes

| Version | Change |
|---|---|
| 15.3+ | `trigger:project` supports variable expansion |
| 16.1+ | `id_tokens:aud` supports variable expansion |

## Decision Guide

| Scenario | Recommendation |
|---|---|
| Need variable in `rules:if` | Use `$variable` form. Only pre-pipeline and pipeline-level vars available. No persisted vars. |
| Need `CI_JOB_TOKEN` in `include:` or `rules:` | Not possible — it's a persisted variable. Restructure to use a non-persisted alternative. |
| Need dynamic artifact path | Use Runner-expanded vars: `artifacts: paths: ['build/${CI_COMMIT_SHORT_SHA}']` |
| Need to pass data from `before_script` to `after_script` | Write to a file in `before_script`, read in `after_script`. Or use `artifacts:reports:dotenv`. |
| Need to debug variable expansion | Temporarily set `CI_DEBUG_TRACE=true` (leaks secrets!) or echo non-sensitive vars in `script:`. |
| Variable appears empty in a keyword | Check the expansion support table — the keyword may not support expansion, or may use GitLab expansion (no persisted/runtime vars). |

## Related Topics

- [predefined.md](predefined.md) — Availability levels determine which expansion contexts a variable works in
- [precedence.md](precedence.md) — When a variable has the right scope but wrong value, check precedence
- [masking-protection.md](masking-protection.md) — Masking interaction with `CI_DEBUG_TRACE`
- [../yaml/keyword-reference.md](../yaml/keyword-reference.md) — YAML keyword definitions referenced in the expansion table

## Sources

- [Where Variables Can Be Used](https://docs.gitlab.com/ci/variables/where_variables_can_be_used/)
- [Variable Expansion Mechanisms](https://docs.gitlab.com/ci/variables/where_variables_can_be_used/#expansion-mechanisms)
- [Persisted Variables](https://docs.gitlab.com/ci/variables/where_variables_can_be_used/#persisted-variables)
- [GitLab CI/CD Debugging](https://docs.gitlab.com/ci/debugging/)
