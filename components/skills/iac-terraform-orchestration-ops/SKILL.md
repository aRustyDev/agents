---
name: iac-terraform-orchestration-ops
description: Orchestrate Terraform and OpenTofu at scale using Terragrunt, Terramate, or Atmos. Use when managing multiple environments, implementing DRY configurations, handling cross-stack dependencies, deploying to many accounts, or establishing infrastructure platform patterns.
---

# Terraform Orchestration Tools

Manage Terraform/OpenTofu configurations at scale using orchestration tools. Choose the right tool for your team's workflow and scale requirements.

## Purpose

Orchestrate infrastructure deployments across multiple environments, accounts, and regions. Implement DRY principles, manage dependencies between stacks, and establish platform engineering patterns for Terraform/OpenTofu.

## When to Use

- Deploy the same modules across multiple AWS accounts or environments
- Manage dependencies between Terraform configurations
- Keep Terraform configurations DRY (Don't Repeat Yourself)
- Implement GitOps workflows for infrastructure
- Detect and deploy only changed infrastructure
- Manage remote state configuration consistently
- Establish enterprise infrastructure platforms
- Migrate from monolithic Terraform to modular stacks

## Tool Comparison

| Feature | Terragrunt | Terramate | Atmos |
|---------|------------|-----------|-------|
| **Primary Use** | DRY wrapper | Stack orchestration | Framework/platform |
| **Configuration** | HCL (terragrunt.hcl) | HCL (terramate.tm.hcl) | YAML + HCL |
| **Learning Curve** | Low | Medium | High |
| **Change Detection** | Basic | Advanced (Git-based) | Component-based |
| **Code Generation** | Limited | Yes | Yes |
| **Inheritance** | include blocks | Globals/metadata | Stack inheritance |
| **Best For** | Simple multi-env | Monorepo orchestration | Enterprise platforms |

## Quick Start Decision Tree

```
Need to orchestrate Terraform?
│
├─ Simple DRY configs, few environments?
│  └─ Terragrunt
│
├─ Monorepo, change detection, CI/CD focus?
│  └─ Terramate
│
└─ Enterprise platform, many teams, component catalog?
   └─ Atmos
```

## Terragrunt Overview

Thin wrapper that keeps Terraform code DRY with minimal overhead.

```hcl
# terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "git::git@github.com:org/modules.git//vpc?ref=v1.0.0"
}

inputs = {
  name       = "production-vpc"
  cidr_block = "10.0.0.0/16"
}
```

**Key Features:**
- Remote state configuration inheritance
- Dependency management between modules
- Before/after hooks for custom logic
- Generate blocks for dynamic files
- Run-all for multi-module operations

See `references/terragrunt.md` for complete patterns.

## Terramate Overview

Stack orchestration with Git-based change detection.

```hcl
# terramate.tm.hcl
terramate {
  config {
    git {
      default_branch = "main"
    }
  }
}

stack {
  name        = "production-vpc"
  description = "Production VPC infrastructure"
  id          = "vpc-prod-us-west-2"
}

globals {
  environment = "production"
  region      = "us-west-2"
}
```

**Key Features:**
- Git-based change detection
- Code generation with templates
- Globals and metadata inheritance
- Parallel stack execution
- Native CI/CD integrations

See `references/terramate.md` for complete patterns.

## Atmos Overview

Full-featured framework for enterprise infrastructure platforms.

```yaml
# stacks/prod/us-west-2/vpc.yaml
import:
  - catalog/vpc/defaults

components:
  terraform:
    vpc:
      metadata:
        component: vpc
        inherits:
          - vpc/defaults
      vars:
        name: production-vpc
        cidr_block: "10.0.0.0/16"
```

**Key Features:**
- Component catalog with inheritance
- Stack configurations with imports
- Workflows for complex operations
- Vendoring for dependency management
- Deep integration with Spacelift

See `references/atmos.md` for complete patterns.

## Common Patterns

### Multi-Environment Structure

```
infrastructure/
├── terragrunt.hcl          # Root config (Terragrunt)
├── terramate.tm.hcl        # Root config (Terramate)
├── atmos.yaml              # Root config (Atmos)
├── modules/                # Shared modules
│   ├── vpc/
│   ├── eks/
│   └── rds/
├── environments/           # Environment configs
│   ├── dev/
│   ├── staging/
│   └── production/
└── regions/               # Regional configs
    ├── us-west-2/
    └── eu-west-1/
```

### Multi-Account AWS Pattern

```
infrastructure/
├── accounts/
│   ├── management/        # AWS Organizations management
│   ├── security/          # Security tooling account
│   ├── networking/        # Transit Gateway, DNS
│   ├── development/       # Dev workloads
│   ├── staging/           # Staging workloads
│   └── production/        # Production workloads
└── modules/
    ├── account-baseline/  # Common account setup
    ├── networking/        # VPC, TGW attachments
    └── workloads/         # Application infrastructure
```

### Dependency Management

All three tools handle dependencies differently:

**Terragrunt:**
```hcl
dependency "vpc" {
  config_path = "../vpc"
}

inputs = {
  vpc_id     = dependency.vpc.outputs.vpc_id
  subnet_ids = dependency.vpc.outputs.private_subnet_ids
}
```

**Terramate:**
```hcl
stack {
  after = ["../vpc"]
}

generate_hcl "_backend.tf" {
  content {
    data "terraform_remote_state" "vpc" {
      backend = "s3"
      config = {
        bucket = global.state_bucket
        key    = "vpc/terraform.tfstate"
      }
    }
  }
}
```

**Atmos:**
```yaml
components:
  terraform:
    eks:
      vars:
        vpc_id: !terraform.output vpc vpc_id
        subnet_ids: !terraform.output vpc private_subnet_ids
```

## CI/CD Integration

### GitHub Actions Pattern

```yaml
name: Infrastructure
on:
  push:
    branches: [main]
  pull_request:

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      stacks: ${{ steps.detect.outputs.stacks }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # Terramate change detection
      - uses: terramate-io/terramate-action@v1
        id: detect
        with:
          args: list --changed

  deploy:
    needs: detect-changes
    if: needs.detect-changes.outputs.stacks != '[]'
    strategy:
      matrix:
        stack: ${{ fromJson(needs.detect-changes.outputs.stacks) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy ${{ matrix.stack }}
        run: |
          cd ${{ matrix.stack }}
          tofu init
          tofu apply -auto-approve
```

## Best Practices

1. **Start simple** - Begin with Terragrunt if new to orchestration
2. **Use consistent naming** - Establish naming conventions early
3. **Version your modules** - Pin module versions in all stacks
4. **Implement change detection** - Only deploy what changed
5. **Separate state per stack** - Avoid monolithic state files
6. **Use workspaces sparingly** - Prefer directory-based separation
7. **Automate everything** - CI/CD for all infrastructure changes
8. **Document dependencies** - Make cross-stack dependencies explicit
9. **Test in lower environments** - Promote through environments
10. **Monitor drift** - Regularly check for configuration drift

## Reference Files

- `references/terragrunt.md` - Complete Terragrunt patterns and examples
- `references/terramate.md` - Complete Terramate patterns and examples
- `references/atmos.md` - Complete Atmos patterns and examples

## Related Skills

- `iac-terraform-modules-eng` - Writing reusable Terraform modules
- `cloud-aws-organizations-ops` - AWS multi-account patterns
