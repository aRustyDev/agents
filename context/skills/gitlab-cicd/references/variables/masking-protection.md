---
name: variable-masking-and-protection
description: Masking rules, ≥8 character constraint, protected branch scoping, and hidden variables
---

# Variable Masking & Protection

> **Scope:** Masking rules, ≥8 character constraint, protected branch scoping, and hidden variables
> **GitLab version:** 11.10+
> **Source cards:** VA-3
> **Tier:** A
> **Last verified:** 2026-03

## When to Use

- You need to prevent sensitive values from appearing in job logs
- You want to restrict variable access to protected branches/tags only
- You need to hide variable values from the UI and API ("Masked and hidden")
- You're choosing between variable types (env_var vs file) for secrets

**Do NOT use when:**
- You need encryption at rest (masking is log scrubbing only — see Vault/OIDC for true secrets management)
- Variables are non-sensitive configuration (use Visible for easier debugging)

## Key Concepts

### Three Visibility Levels

| Visibility | Log Behavior | UI/API Behavior | Use Case | Constraints |
|---|---|---|---|---|
| **Visible** | Value shown in logs | Shown in Settings | Non-sensitive config (URLs, flags) | None |
| **Masked** | Replaced with `[MASKED]` | Shown in Settings | Default for new vars. Tokens, API keys. | ≥8 chars, single line, no spaces |
| **Masked and hidden** | Replaced with `[MASKED]` | Hidden — cannot be revealed after creation | Highest security — prod secrets, signing keys | Same as Masked. Must delete & recreate to change. |

> **Critical:** Masking is **log scrubbing**, not encryption. The value is still present in the
> job environment — a malicious script can exfiltrate it. Combine masking with protected
> branches and review fork MR pipelines carefully.

### Masking Requirements

A variable value **must** meet ALL of these to be maskable:
- ≥ 8 characters
- Single line (no newlines)
- No spaces
- Cannot match a predefined variable name
- Only limited non-alphanumeric characters when `Expand variable reference` is enabled: `_ : @ - + . ~ = /`

If any requirement is not met, GitLab silently fails to mask — the value appears in logs.

### Protected Variables

Protected variables are **only injected into jobs running on protected branches or tags**.
Jobs on unprotected branches will not see the variable at all (it's empty/undefined).

### Variable Types

| Type | Behavior | Use Case |
|---|---|---|
| **Variable** (env_var) | Key = env var name, Value = env var value | Most variables — strings, tokens, URLs |
| **File** | Key = env var name, Value written to temp file, env var = **file path** | Tools requiring file input — `kubectl`, AWS config, certificates |

### Variable Limits

| Scope | Max Variables | Max Value Length |
|---|---|---|
| Project | 8,000 | 10,000 chars |
| Group | 30,000 | 10,000 chars |
| Instance | Unlimited | 10,000 chars |

## Examples

### File-Type Variable with kubectl

```yaml
# In UI: KUBE_CA_PEM = file-type variable with CA certificate content
# In UI: KUBE_URL = variable-type with https://cluster.example.com
deploy:
  script:
    - kubectl config set-cluster e2e
        --server="$KUBE_URL"
        --certificate-authority="$KUBE_CA_PEM"  # this is a PATH to a temp file
```

### Workaround: YAML Variable Needing File-Type Behavior

```yaml
variables:
  SITE_URL: "https://gitlab.example.com"

job:
  script:
    - echo "$SITE_URL" > "site-url.txt"
    - mytool --url-file="site-url.txt"
```

### Security-Conscious Variable Configuration

```yaml
# Production secrets: Masked + Protected + Environment-scoped
# UI Settings:
#   Key: DEPLOY_TOKEN
#   Visibility: Masked and hidden
#   Protect variable: checked
#   Environment scope: production/*

deploy-prod:
  stage: deploy
  script:
    - deploy --token $DEPLOY_TOKEN  # masked in logs, only on protected branches
  environment:
    name: production
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Common Patterns

- **Always mask AND protect production secrets** — masking prevents log leaks; protected restricts branch access
- **Use "Masked and hidden"** for highest-security values (signing keys, cloud credentials) — value cannot be retrieved after creation
- **Test masking in non-production first** — verify the value meets masking requirements before relying on it
- **Scope variables to specific environments** (`production/*`, `staging/*`) to limit blast radius
- **Use file-type variables** for certificates, kubeconfig, and AWS CLI config files
- **Use external secrets (Vault/OIDC)** for high-security needs — avoid storing secrets in GitLab at all

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Assuming masking = encryption | Masking is log scrubbing only — value exists in job env | Combine with protected branches; use Vault for true encryption |
| Failing to protect branch-restricted secrets | Unprotected branches can access the variable | Check "Protect variable" for production secrets |
| Using short values that can't be masked (< 8 chars) | GitLab silently fails to mask — value appears in logs | Pad short values or use a longer secret format |
| Echoing masked variables in debug steps | Masked value still replaced, but creative formatting can bypass | Avoid any echo/printf of sensitive vars; use `CI_DEBUG_TRACE` carefully |
| Combining masking with `$` expansion | Only limited special chars allowed when expansion is enabled | Uncheck "Expand variable reference" or use file-type variable |
| Running fork MR pipelines without reviewing `.gitlab-ci.yml` | Fork authors can add `curl` to exfiltrate all parent project secrets | Review fork changes; use separate fork runner with no secrets |
| Using `CI_DEBUG_SERVICES` in production | May reveal masked variable values in service container logs | Only enable on non-sensitive runners |

## Practitioner Pain Points

1. **"Masked variable not masking — value appears in logs"** (high frequency) — Value doesn't meet masking requirements: < 8 chars, contains spaces/newlines, or matches predefined var name. Shell escaping can also cause mismatches (e.g., `My[value]` becomes `My\[value\]` which doesn't match the mask pattern).

2. **"Can't use `$` in masked variable value"** (medium frequency) — When masking + expansion are both enabled, only limited non-alphanumeric chars are allowed: `_ : @ - + . ~ = /`. **Fix:** Uncheck "Expand variable reference" to allow `$` in the value, or use a file-type variable.

3. **"Protected variable invisible to developers on unprotected branches"** (high frequency) — By design. Protected variables are only injected on protected branches/tags. **Fix:** Document which vars are protected. Consider environment-scoped vars as an alternative.

4. **"MR pipeline from fork accessing parent project secrets"** (medium frequency) — Running an MR pipeline in the parent project for a fork MR exposes all variables to the fork's `.gitlab-ci.yml`. **Fix:** Review fork changes before running. Consider fork-specific runners without secret access.

## Version Notes

| Version | Change |
|---|---|
| 12.0+ | Variable masking introduced |
| 13.0+ | Protected variable integration with protected branches |
| 17.4+ | "Masked and hidden" visibility option — value cannot be revealed after creation |

## Decision Guide

| Scenario | Recommendation |
|---|---|
| Non-sensitive project config (database URL, feature flags) | Visible variable in YAML or project settings |
| API token needed by all environments | Masked variable, project-level, no environment scope |
| Production-only deployment secret | Masked and hidden + Protected + Environment scope: `production/*` |
| Certificate or kubeconfig for kubectl | File-type variable, Masked, Protected, environment-scoped |
| Highly sensitive secret (signing key, cloud credentials) | External secrets via Vault/OIDC (`ci/secrets/`) — avoid storing in GitLab at all |

## Related Topics

- [predefined.md](predefined.md) — Some predefined vars (CI_JOB_TOKEN, CI_REGISTRY_PASSWORD) are auto-masked
- [precedence.md](precedence.md) — Protected/masked variables follow the same precedence hierarchy
- [scopes.md](scopes.md) — Masked variables and their interaction with expansion contexts
- [../security/secrets-management.md](../security/secrets-management.md) — Vault/OIDC integration for external secrets

## Sources

- [GitLab CI/CD Variables — Mask a Variable](https://docs.gitlab.com/ci/variables/#mask-a-cicd-variable)
- [GitLab CI/CD Variables — Protected Variables](https://docs.gitlab.com/ci/variables/#protect-a-cicd-variable)
- [File-Type Variables](https://docs.gitlab.com/ci/variables/#use-file-type-cicd-variables)
- [Where Variables Can Be Used](https://docs.gitlab.com/ci/variables/where_variables_can_be_used/)

