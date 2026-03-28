---
name: variable-precedence
description: 11-level variable precedence hierarchy with override examples and advanced contexts
---

# Variable Precedence

> **Scope:** 11-level variable precedence hierarchy with override examples and advanced contexts
> **GitLab version:** 9.0+
> **Source cards:** VA-2, VA-6
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You need to understand why a variable has an unexpected value (most common reason)
- You're designing a multi-level variable strategy (instance → group → project → job)
- You're using `trigger:forward` and downstream pipelines see wrong values
- You need to override a project-level variable from YAML (requires a workaround)

**Do NOT use when:**
- You only use variables defined in one place (precedence is irrelevant)
- You need expansion context info — see [scopes.md](scopes.md) instead

## Key Concepts

### 11-Level Precedence Hierarchy (Highest → Lowest)

| Level | Source | Notes |
|---|---|---|
| 1 | Pipeline execution policy variables | Security policy enforcement |
| 2 | Scan execution policy variables | Security scanning enforcement |
| 3 | **Pipeline variables** | Trigger, scheduled, manual, API, manual job, downstream — **all same precedence** |
| 4 | **Project variables** | Settings → CI/CD → Variables |
| 5 | **Group variables** | Closest subgroup to project wins for same-named vars |
| 6 | Instance variables | Admin → Settings → CI/CD (self-managed only) |
| 7 | `artifacts:reports:dotenv` variables | From dotenv report in earlier jobs |
| 8 | **Job YAML variables** | `variables:` within a job in `.gitlab-ci.yml` |
| 9 | **Default YAML variables** | Top-level `variables:` in `.gitlab-ci.yml` |
| 10 | Deployment variables | Auto-generated for deployment jobs |
| 11 | Predefined variables | Built-in `CI_*` and `GITLAB_*` — lowest priority |

> **Key insight:** Project variables (level 4) **always override** YAML job variables (level 8).
> This is the #1 source of confusion — developers expect YAML to "win" but it doesn't.

### Precedence Elevation with `trigger:forward`

When using `trigger:forward:pipeline_variables: true`, YAML variables in the parent pipeline
are **elevated to trigger variable precedence (level 3)** in the downstream pipeline. This means
they override project-level variables in the child/downstream project.

### Group Subgroup Resolution

When the same variable name exists in multiple group levels, the **closest subgroup to the project
wins**. Example: `org/team/project` — a variable in `org/team` overrides one in `org`.

### Environment-Scoped Variables

Variables can be scoped to environments using wildcards:
- `production` — exact match
- `review/*` — matches `review/feature-1`, `review/bugfix-2`, etc.
- `*` — all environments (default)

## Examples

### Job-Level YAML Overrides Global YAML (Level 8 > Level 9)

```yaml
variables:
  API_TOKEN: "default"      # level 9 — default YAML

job1:
  variables:
    API_TOKEN: "secure"     # level 8 — job YAML (wins)
  script:
    - echo "The variable is '$API_TOKEN'"  # outputs: secure
```

### Workaround: Override Project-Level Vars from YAML

```yaml
# Problem: Project var WEB_HOST (level 4) always beats YAML (level 8/9)
# Solution: Use before_script shell reassignment
variables:
  LOCAL_WEB_HOST: localhost
  LOCAL_DB_HOST: db

my_job:
  before_script:
    - export WEB_HOST=$LOCAL_WEB_HOST  # shell override in execution context
    - export DB_HOST=$LOCAL_DB_HOST
  script:
    - echo "Using WEB_HOST=$WEB_HOST"  # now uses YAML-defined value
```

### trigger:forward Elevates YAML Vars to Pipeline Precedence

```yaml
# CAUTION: forward makes YAML vars into trigger vars (level 3) in downstream
# This REGION will override project-level REGION in the downstream project
trigger-child:
  variables:
    REGION: "us-east-1"
  trigger:
    include: child-pipeline.yml
    strategy: depend
    forward:
      pipeline_variables: true  # elevates ALL vars to trigger precedence
```

### Controlled Variable Forwarding (Best Practice)

```yaml
trigger-deploy:
  stage: deploy
  variables:
    DEPLOY_VERSION: $CI_COMMIT_SHORT_SHA
    DEPLOY_ENV: "staging"
  trigger:
    project: my-group/deploy-pipeline
    strategy: depend
    forward:
      yaml_variables: true       # forward DEPLOY_VERSION and DEPLOY_ENV only
      pipeline_variables: false   # don't forward manual/trigger vars (safer)
```

### Environment-Scoped Variable Matching

```yaml
# In UI: Key=DATABASE_URL, Value=postgres://staging-db:5432, Scope=review/*
deploy-review:
  stage: deploy
  environment:
    name: review/$CI_COMMIT_REF_SLUG
  script:
    - echo "DB is $DATABASE_URL"  # gets review/* scoped value
```

### workflow:rules:variables for Pipeline-Wide Overrides

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
      variables:
        DEPLOY_ENV: "nightly"
        FULL_SUITE: "true"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      variables:
        DEPLOY_ENV: "review"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      variables:
        DEPLOY_ENV: "production"
    - when: always
      variables:
        DEPLOY_ENV: "development"
```

### Preventing Variable Expansion

```yaml
variables:
  DEPLOY_COMMAND:
    value: 'deploy --token=$TOKEN'
    expand: false  # $TOKEN is NOT expanded — passed literally to script
```

## Common Patterns

- **Set defaults at group level, override at project/job** — follows the hierarchy naturally
- **Use protected variables for production secrets** — only injected on protected branches
- **Environment-scoped variables for stage-specific config** — use wildcards like `review/*`
- **`variables:expand: false`** for literal values containing `$` characters
- **File-type variables** for Docker/K8s config injection (value written to temp file, env var = path)

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Expecting YAML to override project-level vars | Project (4) outranks job YAML (8) | Use `before_script` shell reassignment workaround |
| Not understanding that job YAML overrides global YAML | Level 8 beats level 9 | Define at job level for intentional overrides |
| Using `trigger:forward:pipeline_variables` broadly | Elevates all vars to level 3, overriding downstream project vars | Only forward `yaml_variables` when needed |
| Storing secrets in YAML instead of CI/CD settings | Secrets in repo are visible to all contributors | Use project/group variables with masking |
| Assuming trigger variables have lower precedence | Trigger vars (level 3) outrank project vars (level 4) | Be intentional about what you pass via triggers |
| Forgetting group subgroup resolution order | Closest subgroup wins, not highest-level group | Define at the closest group level to the project |

## Practitioner Pain Points

1. **"Why is my YAML variable being overridden?"** (27k SO views) — Project variables (level 4) beat YAML job variables (level 8). **Workaround:** reassign in `before_script` using `export VAR=$YAML_VAR`. [SO #72009402](https://stackoverflow.com/questions/72009402)

2. **"trigger:forward causes wrong variable value"** (4k SO views) — `trigger:forward:pipeline_variables=true` elevates YAML vars to trigger precedence (level 3), overriding project-level vars in downstream. **Fix:** use `yaml_variables: true` + `pipeline_variables: false`. [SO #77484773](https://stackoverflow.com/questions/77484773)

3. **"How to debug which precedence level is winning?"** — No built-in variable-source indicator in GitLab. **Workaround:** Temporarily set `CI_DEBUG_TRACE=true`, or echo variables in script to compare expected vs actual values.

4. **"File-type variables behave differently"** — File-type vars write the value to a temp file; the env var holds the **file path**, not the value itself. Use `cat $MY_FILE_VAR` to read value, or pass `$MY_FILE_VAR` as `--config-file` argument.

5. **"workflow:rules:variables not taking effect"** (5k SO views) — `workflow:rules` are evaluated early (pre-pipeline). Only pre-pipeline vars are available in the `if:` condition. Variables set by `workflow:rules:variables` cascade to all jobs. [SO #72304507](https://stackoverflow.com/questions/72304507)

## Version Notes

| Version | Change |
|---|---|
| 13.7+ | Pipeline-level variables added (CI/CD settings) |
| 15.6+ | `trigger:forward:yaml_variables` and `trigger:forward:pipeline_variables` |
| 17.7+ | Pipeline variable restrictions by role — minimum role enforcement. Pipeline inputs recommended over pipeline variables. |

## Decision Guide

| Scenario | Recommendation |
|---|---|
| Shared config across all projects in a group | Group-level variable (level 5). Inherited by all projects. |
| Secret that varies per environment | Project variable (level 4) with environment scope (e.g., `production/*`) |
| Need YAML to override a project-level var | Cannot directly. Use `before_script` reassignment workaround. |
| Pass vars to downstream without precedence issues | Use `trigger:forward` judiciously — only forward `yaml_variables`, not `pipeline_variables`. |
| Disable pipeline variables for security | Set _Minimum role to use pipeline variables_ to `no_one_allowed` (17.7+). Use pipeline inputs instead. |
| Set pipeline-wide variable based on source type | Use `workflow:rules:variables` — sets once at pipeline level, cascades to all jobs. |
| Need literal `$` in a variable value | Use `variables:expand: false` on that specific variable. |
| Need to parameterize included CI config | Use `include:inputs` with `spec:inputs` in the included file (component pattern). |

## Related Topics

- [predefined.md](predefined.md) — Predefined variables occupy the lowest precedence level (11)
- [scopes.md](scopes.md) — Where variables can be expanded depends on the expansion mechanism
- [masking-protection.md](masking-protection.md) — Masking and protection are orthogonal to precedence
- [../pipelines/downstream.md](../pipelines/downstream.md) — How `trigger:forward` affects downstream variable values
- [../yaml/workflow-rules.md](../yaml/workflow-rules.md) — `workflow:rules:variables` for pipeline-wide overrides

## Sources

- [GitLab CI/CD Variable Precedence](https://docs.gitlab.com/ci/variables/#cicd-variable-precedence)
- [Where Variables Can Be Used](https://docs.gitlab.com/ci/variables/where_variables_can_be_used/)
- [trigger:forward](https://docs.gitlab.com/ci/yaml/#triggerforward)
- [SO: Variable override confusion](https://stackoverflow.com/questions/72009402)
- [SO: trigger:forward precedence](https://stackoverflow.com/questions/77484773)
