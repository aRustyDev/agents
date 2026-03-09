---
name: pipeline-security
description: SHA pinning, include:integrity, CI/CD inputs validation, and protected branch rules
---

# Pipeline Security

> **Scope:** SHA pinning, include:integrity, CI/CD inputs validation, and protected branch rules
> **GitLab version:** 15.0+
> **Source cards:** PL-3
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Securing pipeline configuration against supply chain attacks
- Implementing SHA pinning for external includes
- Configuring secrets management (Vault, cloud providers, OIDC)
- Choosing between CI/CD variables and component inputs for type safety
- Protecting sensitive jobs on dedicated runners

## Key Concepts

### Include Integrity

| Mechanism | Purpose | Since |
|---|---|---|
| `include:integrity:sha256:` | Verify SHA256 hash of remote includes | 17.2+ |
| Pin to specific tag/commit | Prevent unreviewed config changes | Always |
| `include:component:` with version | Immutable version reference | 17.0+ |

### Dependency Locking

Verify lockfile integrity in CI to prevent supply chain attacks:
- `Gemfile.lock`, `package-lock.json`, `poetry.lock`
- Use `npm ci` (not `npm install`) to enforce lockfile
- Fail the job if lockfile is modified during install

### Secrets Management

| Provider | Integration | Auth Method |
|---|---|---|
| **HashiCorp Vault** | `vault:` keyword (native) | JWT/OIDC, AppRole |
| **GCP Secret Manager** | `secrets:gcp_secret_manager:` | OIDC with `id_tokens:` |
| **Azure Key Vault** | `secrets:azure_key_vault:` | OIDC with `id_tokens:` |
| **AWS Secrets Manager** | `secrets:aws_secrets_manager:` | OIDC with `id_tokens:` |

### OIDC Authentication

```yaml
job:
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com
  secrets:
    DATABASE_PASSWORD:
      vault: secret/data/production/db/password@secrets
      token: $VAULT_ID_TOKEN
```

> **Preferred over CI/CD variables** for cloud secrets — short-lived tokens, no stored credentials.

### CI/CD Inputs vs Variables

| Feature | Variables | Inputs (spec:inputs) |
|---|---|---|
| Type checking | None | `string`, `number`, `boolean` |
| Validation | None | `options:`, `regex:` |
| Default values | Yes | Yes |
| Runtime override | Yes (UI, API) | No (template-time only) |

**Prefer inputs** for configuration that should be validated at pipeline creation, not runtime.

### Protected Runners

- Tag sensitive jobs with protected runner tags
- Protected runners only run jobs from protected branches/tags
- Use `allowed_images` / `allowed_services` to restrict Docker images

## Examples

### SHA-Pinned Include

```yaml
include:
  - component: $CI_SERVER_FQDN/my-org/ci-templates/sast@1.2.0
  - remote: https://example.com/templates/deploy.yml
    integrity:
      sha256: "abc123def456..."
```

### Vault Secret Injection

```yaml
deploy:
  stage: deploy
  id_tokens:
    VAULT_TOKEN:
      aud: https://vault.company.com
  secrets:
    DB_PASSWORD:
      vault: production/db/password@secrets
      token: $VAULT_TOKEN
  script:
    - deploy --db-password "$DB_PASSWORD"
```

### Lockfile Verification

```yaml
install:
  stage: build
  script:
    - npm ci --ignore-scripts
    - git diff --exit-code package-lock.json  # Fail if lockfile changed
```

## Common Patterns

- **Pin all external includes** to SHA or specific tags
- **`include:integrity`** for SHA256 verification of remote includes
- **`id_tokens:` + `secrets:`** for OIDC authentication to cloud providers
- **`npm ci` / `pip install --require-hashes`** for lockfile enforcement
- **Protected runners** with tag-based job routing for sensitive deployments
- **Component inputs** over variables for type-safe config

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Remote includes without version pinning | Upstream changes break or compromise pipeline | Pin to tag, commit SHA, or use `integrity:` |
| Secrets in CI/CD variables | Broader access than needed, no rotation | Use secrets manager with OIDC |
| Variables when inputs would validate | No type/value checking at creation time | Use `spec:inputs:` with `options:` or `regex:` |
| Sensitive jobs on shared runners | Shared runners have broader access | Use protected, tagged runners |
| `npm install` instead of `npm ci` | Lockfile not enforced — dependencies drift | Use `npm ci` in CI |

## Practitioner Pain Points

1. **`include:integrity` is new** (17.2+) — many teams still rely on tag pinning alone.
2. **OIDC setup is complex** — requires identity provider configuration in Vault/cloud + matching `aud:` claims.
3. **Secrets in variables are pervasive** — migration to secrets manager requires per-job changes.
<!-- TODO: Expand with deeper research on compliance frameworks and security policy enforcement -->

## Related Topics

- [../variables/masking-protection.md](../variables/masking-protection.md) — Variable masking and protection
- [../runner/security.md](../runner/security.md) — Runner-level security controls
- [../security/secrets-management.md](../security/secrets-management.md) — Detailed secrets provider config
- [../security/compliance.md](../security/compliance.md) — Compliance frameworks

## Sources

- [Pipeline security](https://docs.gitlab.com/ci/pipeline_security/)
- [Using external secrets](https://docs.gitlab.com/ci/secrets/)

