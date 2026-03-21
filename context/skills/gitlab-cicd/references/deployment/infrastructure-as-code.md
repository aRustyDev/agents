---
name: infrastructure-as-code
description: Terraform/OpenTofu integration, GitLab-managed state, module registry, and plan/apply patterns
---

# Infrastructure as Code

> **Scope:** Terraform/OpenTofu integration, GitLab-managed state, module registry, and plan/apply patterns
> **GitLab version:** 12.0+
> **Source cards:** NEW-10, GD-1
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Running Terraform/OpenTofu in GitLab CI pipelines
- Using GitLab-managed state backend for team collaboration
- Integrating plan output into merge request reviews
- Publishing reusable Terraform modules to GitLab Module Registry

## Key Concepts

### OpenTofu CI/CD Component

The official GitLab component provides a standardized IaC pipeline:

```yaml
include:
  - component: $CI_SERVER_FQDN/components/opentofu/validate-plan-apply@1.0.0
    inputs:
      version: "1.8"
      root_dir: infrastructure/
```

### Pipeline Flow

```
validate → plan → (MR review) → apply
```

| Stage | Purpose | Trigger |
|---|---|---|
| **validate** | Syntax and configuration check | Every pipeline |
| **plan** | Show planned changes | Every pipeline |
| **apply** | Execute changes | Default branch only, manual |

### GitLab-Managed State Backend

| Feature | Detail |
|---|---|
| **Protocol** | HTTP state backend |
| **Authentication** | `CI_JOB_TOKEN` (automatic) |
| **Locking** | Automatic state locking |
| **Versioning** | State version history |
| **Encryption** | At rest (GitLab-managed) |

Backend configuration:
```hcl
terraform {
  backend "http" {}  # GitLab fills in via CI environment variables
}
```

### Module Registry

Publish reusable Terraform/OpenTofu modules:
- **Settings > Packages & Registries > Terraform Module Registry**
- Publish via CI with `terraform-module` package type
- Consume with standard module source syntax

### MR Integration

Plan output displayed in merge request:
- Plan diff shown as MR note
- Reviewers approve infrastructure changes before apply
- `TF_PLAN_JSON` artifact for programmatic analysis

## Examples

### OpenTofu Component Pipeline

```yaml
include:
  - component: $CI_SERVER_FQDN/components/opentofu/validate-plan-apply@1.0.0
    inputs:
      version: "1.8"
      root_dir: infrastructure/
      plan_args: "-var-file=prod.tfvars"
```

### Custom Terraform Pipeline

```yaml
stages: [validate, plan, apply]

variables:
  TF_ROOT: infrastructure/

validate:
  stage: validate
  image: hashicorp/terraform:1.8
  script:
    - cd $TF_ROOT
    - terraform init -backend=false
    - terraform validate

plan:
  stage: plan
  image: hashicorp/terraform:1.8
  script:
    - cd $TF_ROOT
    - terraform init
    - terraform plan -out=plan.cache
  artifacts:
    paths: [infrastructure/plan.cache]

apply:
  stage: apply
  image: hashicorp/terraform:1.8
  script:
    - cd $TF_ROOT
    - terraform init
    - terraform apply plan.cache
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  environment:
    name: production
  resource_group: terraform-production
```

## Common Patterns

- **OpenTofu CI/CD component** for standardized IaC pipelines
- **GitLab-managed state backend** for team collaboration (no S3 setup)
- **MR integration** for plan review before apply
- **`resource_group:`** on apply jobs to prevent concurrent state modifications
- **`when: manual`** on apply for explicit approval

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Manual `terraform apply` outside CI | No audit trail, no review | Always apply through CI pipeline |
| Local state files | No collaboration, no locking | Use GitLab-managed or remote backend |
| Apply without plan review | Unreviewed infrastructure changes | Require MR approval before apply |
| No `resource_group` on apply | Concurrent applies corrupt state | Add `resource_group:` |

## Practitioner Pain Points

1. **GitLab state backend requires `CI_JOB_TOKEN`** — works automatically in CI but needs manual setup for local development.
2. **Plan output in MR requires CI/CD integration** — use `TF_PLAN_JSON` artifact for structured output.
3. **Terragrunt adds complexity** — GitLab's OpenTofu component doesn't natively support Terragrunt; custom pipeline required.
<!-- TODO: Expand with deeper research on Terragrunt patterns, module registry publishing, and multi-environment state -->

## Related Topics

- [../pipelines/environments.md](../pipelines/environments.md) — Environment and resource_group config
- [../pipelines/manual-gates.md](../pipelines/manual-gates.md) — Manual approval for apply
- [../security/secrets-management.md](../security/secrets-management.md) — Cloud provider authentication

## Sources

- [Infrastructure as Code](https://docs.gitlab.com/user/infrastructure/iac/)
- [OpenTofu CI/CD component](https://gitlab.com/components/opentofu)
