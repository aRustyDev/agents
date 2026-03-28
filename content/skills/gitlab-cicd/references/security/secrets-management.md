---
name: secrets-management
description: HashiCorp Vault, GCP SM, Azure KV, AWS SM integration with OIDC/JWT authentication
---

# Secrets Management

> **Scope:** HashiCorp Vault, GCP SM, Azure KV, AWS SM integration with OIDC/JWT authentication
> **GitLab version:** 12.0+
> **Source cards:** NEW-06, WF-3
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Integrating external secrets managers (Vault, GCP, Azure, AWS) with CI jobs
- Configuring OIDC/JWT authentication for short-lived credentials
- Migrating from CI/CD variables to secrets managers
- Understanding Vault KV v1 vs v2 engine paths

## Key Concepts

### Native Secrets Providers

| Provider | Keyword | Auth Method |
|---|---|---|
| **HashiCorp Vault** | `secrets:vault:` | JWT/OIDC, AppRole |
| **GCP Secret Manager** | `secrets:gcp_secret_manager:` | Workload Identity Federation |
| **Azure Key Vault** | `secrets:azure_key_vault:` | Workload Identity Federation |
| **AWS Secrets Manager** | `secrets:aws_secrets_manager:` | OIDC with STS |

### id_tokens (OIDC)

```yaml
job:
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com
```

Creates a JWT with claims:

| Claim | Value |
|---|---|
| `iss` | GitLab instance URL |
| `sub` | `project_path:group/project:ref_type:branch:ref:main` |
| `aud` | Configured audience |
| `namespace_path` | Group/subgroup path |
| `project_path` | Full project path |
| `ref` | Branch or tag name |

> **Preferred over CI_JOB_JWT** (deprecated). Use `id_tokens:` with explicit `aud` claim.

### Vault KV Engine Paths

| Engine | Path Format |
|---|---|
| **KV v1** | `secret/data/path` — **no** `data/` prefix |
| **KV v2** | `secret/data/path` — `data/` prefix required |

```yaml
secrets:
  DATABASE_PASSWORD:
    vault:
      engine:
        name: kv-v2
        path: secret
      path: production/db
      field: password
    token: $VAULT_ID_TOKEN
```

### Vault Role Binding

Configure Vault roles to restrict access:

```hcl
# Vault policy — bind to specific project and ref
bound_claims = {
  project_path = "my-group/my-project"
  ref          = "main"
  ref_type     = "branch"
}
```

### JWT Claims for Cloud Providers

**GCP Workload Identity Federation:**
```yaml
id_tokens:
  GCP_TOKEN:
    aud: https://iam.googleapis.com/projects/PROJECT_NUM/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID
```

**Azure Workload Identity:**
```yaml
id_tokens:
  AZURE_TOKEN:
    aud: api://AzureADTokenExchange
```

## Examples

### Vault Secret Injection

```yaml
deploy:
  id_tokens:
    VAULT_TOKEN:
      aud: https://vault.company.com
  secrets:
    DB_PASSWORD:
      vault:
        path: production/db
        field: password
      token: $VAULT_TOKEN
    API_KEY:
      vault:
        path: production/api
        field: key
      token: $VAULT_TOKEN
  script:
    - deploy --db-password "$DB_PASSWORD" --api-key "$API_KEY"
```

### GCP Secret Manager

```yaml
deploy-gcp:
  id_tokens:
    GCP_TOKEN:
      aud: https://iam.googleapis.com/projects/123/locations/global/workloadIdentityPools/pool/providers/gitlab
  secrets:
    SERVICE_ACCOUNT_KEY:
      gcp_secret_manager:
        name: my-service-key
        version: latest
      token: $GCP_TOKEN
  script:
    - gcloud auth activate-service-account --key-file <(echo "$SERVICE_ACCOUNT_KEY")
```

### AWS Secrets Manager

```yaml
deploy-aws:
  id_tokens:
    AWS_TOKEN:
      aud: https://gitlab.example.com
  secrets:
    AWS_SECRET:
      aws_secrets_manager:
        name: production/api-key
        version_id: latest
      token: $AWS_TOKEN
  script:
    - aws deploy --secret "$AWS_SECRET"
```

## Common Patterns

- **`id_tokens:` with specific `aud` claim** for OIDC authentication
- **`secrets:vault:`** for HashiCorp Vault integration
- **OIDC over long-lived credentials** for cloud provider access
- **Environment-scoped secrets** for deployment target separation
- **Vault role binding** to project_path and ref for least-privilege

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Secrets in CI/CD variables | Broader access, no rotation | Use secrets manager + OIDC |
| `CI_JOB_JWT` (deprecated) | Removed in future versions | Migrate to `id_tokens:` |
| Broad JWT audience claims | Reduces security boundary | Use specific `aud` per provider |
| Broad Vault role binding | Any project/ref can access secrets | Bind to specific project_path + ref |
| Not rotating credentials | Stale credentials if compromised | OIDC provides short-lived tokens |

## Practitioner Pain Points

1. **OIDC setup is complex** — requires identity provider configuration in Vault/cloud AND matching `aud:` claims in GitLab.
2. **Vault KV v1 vs v2 path difference** — v2 requires `data/` prefix in path, v1 doesn't. Most common Vault integration error.
3. **`CI_JOB_JWT` deprecation** — teams must migrate to `id_tokens:` keyword. New projects should never use `CI_JOB_JWT`.
<!-- TODO: Expand with deeper research on GCP/Azure Workload Identity Federation setup and Vault AppRole patterns -->

## Related Topics

- [../pipelines/security.md](../pipelines/security.md) — Pipeline security overview
- [../variables/masking-protection.md](../variables/masking-protection.md) — Variable masking for secrets
- [compliance.md](compliance.md) — Compliance frameworks and audit

## Sources

- [External secrets](https://docs.gitlab.com/ci/secrets/)
- [OIDC authentication](https://docs.gitlab.com/ci/secrets/id_token_authentication/)
