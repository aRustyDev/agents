---
name: troubleshooting
description: Pipeline editor, CI Lint, CI_DEBUG_TRACE, common error patterns, and debugging decision tree
---

# Troubleshooting

> **Scope:** Pipeline editor, CI Lint, CI_DEBUG_TRACE, common error patterns, and debugging decision tree
> **GitLab version:** 9.0+
> **Source cards:** TR-1
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Debugging pipeline failures (YAML errors, stuck jobs, rules issues)
- Validating `.gitlab-ci.yml` before pushing
- Using CI_DEBUG_TRACE for verbose output
- Diagnosing service container failures

## Key Concepts

### Validation Tools

| Tool | Where | Purpose |
|---|---|---|
| **Pipeline Editor** | GitLab UI > CI/CD > Editor | Visual YAML editing + lint + job graph |
| **CI Lint** | GitLab UI > CI/CD > Lint | Validate and expand YAML (merged view) |
| **CI Lint API** | `POST /projects/:id/ci/lint` | Programmatic validation (pre-commit hooks) |
| **Merged YAML view** | Pipeline Editor "Full configuration" tab | See includes/extends fully expanded |

### Debug Variables

| Variable | Effect |
|---|---|
| `CI_DEBUG_TRACE: "true"` | Shell trace + all variable values printed |
| `CI_DEBUG_SERVICES: "true"` | Debug output for service containers |

> **Warning:** `CI_DEBUG_TRACE` prints **all** variable values including secrets. Never leave enabled on protected branches.

### Common Error Patterns

| Symptom | Likely Cause | Fix |
|---|---|---|
| "Checking pipeline status" spinner | No `workflow:rules` match | Ensure at least one workflow rule matches |
| "Pipeline not found" | Token/permission issue | Check `CI_JOB_TOKEN` permissions |
| Job "stuck" (pending forever) | No available runner with matching tags | Check runner tags and availability |
| "YAML syntax error" | Invalid YAML (tabs, missing quotes) | Validate in Pipeline Editor |
| "Parsed YAML is too big" | Too many includes/expansions | Reduce `include:` nesting, DRY config |
| Job runs unexpectedly | Rules evaluation order | Check rules top-to-bottom, first match wins |
| "Cannot find file" in artifacts | Paths don't match | Check relative paths and working directory |
| Service container fails | Image pull or startup error | Check `services:` image and `CI_DEBUG_SERVICES` |

### Debugging Workflow

1. **Reproduce** — identify which job fails and the error message
2. **Validate YAML** — check in Pipeline Editor or CI Lint
3. **Check merged config** — "Full configuration" tab to see expanded includes
4. **Check variables** — verify with `printenv | sort` in `before_script`
5. **Check runner** — verify tags, availability, and executor type
6. **Enable trace** — `CI_DEBUG_TRACE=true` for verbose output (temporary!)
7. **Test locally** — run the Docker image locally with `docker run -it <image> bash`

## Examples

### Validate with CI Lint API

```bash
# Pre-commit hook
curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --data-urlencode "content=$(cat .gitlab-ci.yml)" \
  "https://gitlab.example.com/api/v4/projects/$PROJECT_ID/ci/lint" \
  | jq '.valid'
```

### Debug Variables in Job

```yaml
debug:
  stage: .pre
  script:
    - printenv | sort
    - echo "Source: $CI_PIPELINE_SOURCE"
    - echo "Branch: $CI_COMMIT_BRANCH"
    - echo "Tag: $CI_COMMIT_TAG"
    - echo "MR IID: $CI_MERGE_REQUEST_IID"
  rules:
    - if: $DEBUG == "true"
```

### Service Container Debugging

```yaml
test:
  services:
    - name: postgres:16
      alias: db
  variables:
    CI_DEBUG_SERVICES: "true"
    POSTGRES_DB: test
    POSTGRES_USER: runner
    POSTGRES_PASSWORD: password
  script:
    - wait-for-it db:5432 --timeout=30
    - run_tests
```

## Common Patterns

- **Pipeline Editor** for visual YAML validation before committing
- **CI Lint API** in pre-commit hooks for early validation
- **`CI_DEBUG_TRACE`** for short-term variable debugging (remove immediately after)
- **Merged YAML view** to debug `include:` / `extends:` resolution
- **`printenv | sort`** to check available variables at runtime
- **`docker run -it <image> bash`** to reproduce locally

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| "Push and pray" debugging | Slow feedback loop | Validate with Pipeline Editor before push |
| `CI_DEBUG_TRACE` left enabled | Prints secrets to logs | Remove immediately after debugging |
| Not checking merged YAML | Includes produce unexpected results | Check "Full configuration" tab |
| Ignoring the pipeline graph | Miss dependency issues | Review visual DAG in Pipeline Editor |

## Practitioner Pain Points

1. **`CI_DEBUG_TRACE` prints all secrets** — never commit `CI_DEBUG_TRACE: "true"` to the repository. Use pipeline-level variable override.
2. **"Stuck" jobs** — almost always a runner tag mismatch. Check job tags vs. runner tags in **Settings > CI/CD > Runners**.
3. **Include resolution order** — when multiple includes define the same job, last include wins. Use merged YAML view to verify.
<!-- TODO: Expand with deeper research on CI Lint API integration patterns and GitLab Duo Root Cause Analysis -->

## Related Topics

- [faq.md](faq.md) — Common gotchas and quick fixes
- [yaml/rules-patterns.md](yaml/rules-patterns.md) — Rules evaluation debugging
- [yaml/workflow-rules.md](yaml/workflow-rules.md) — Workflow rules issues
- [variables/scopes.md](variables/scopes.md) — Variable expansion debugging

## Sources

- [Debugging CI/CD](https://docs.gitlab.com/ci/debugging/)
- [Pipeline Editor](https://docs.gitlab.com/ci/pipeline_editor/)
- [CI Lint API](https://docs.gitlab.com/api/lint/)

