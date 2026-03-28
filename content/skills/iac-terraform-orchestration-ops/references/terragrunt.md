# Terragrunt Reference

Terragrunt is a thin wrapper for Terraform that provides extra tools for keeping configurations DRY, working with multiple modules, and managing remote state.

## Installation

```bash
# macOS
brew install terragrunt

# Linux
curl -L https://github.com/gruntwork-io/terragrunt/releases/latest/download/terragrunt_linux_amd64 -o terragrunt
chmod +x terragrunt && sudo mv terragrunt /usr/local/bin/

# Windows
choco install terragrunt
```

## CLI Commands

```bash
terragrunt init          # Initialize Terraform
terragrunt plan          # Generate execution plan
terragrunt apply         # Apply changes
terragrunt destroy       # Destroy infrastructure
terragrunt output        # Show outputs
terragrunt validate      # Validate configuration

# Multi-module commands
terragrunt run-all init     # Init all modules in tree
terragrunt run-all plan     # Plan all modules
terragrunt run-all apply    # Apply all modules
terragrunt run-all destroy  # Destroy all modules

# Utility commands
terragrunt graph-dependencies  # Show dependency graph
terragrunt hclfmt              # Format terragrunt.hcl files
terragrunt render-json         # Render config as JSON
```

## Project Structure

```
infrastructure/
├── terragrunt.hcl              # Root configuration
├── environments/
│   ├── dev/
│   │   ├── env.hcl             # Environment-specific vars
│   │   ├── vpc/
│   │   │   └── terragrunt.hcl
│   │   ├── eks/
│   │   │   └── terragrunt.hcl
│   │   └── rds/
│   │       └── terragrunt.hcl
│   ├── staging/
│   │   └── ...
│   └── production/
│       └── ...
├── regions/
│   ├── us-west-2/
│   │   └── region.hcl
│   └── eu-west-1/
│       └── region.hcl
└── modules/                    # Local modules (optional)
    ├── vpc/
    └── eks/
```

## Root Configuration

```hcl
# terragrunt.hcl (root)
locals {
  account_vars = read_terragrunt_config(find_in_parent_folders("account.hcl"))
  region_vars  = read_terragrunt_config(find_in_parent_folders("region.hcl"))
  env_vars     = read_terragrunt_config(find_in_parent_folders("env.hcl"))

  account_id   = local.account_vars.locals.account_id
  account_name = local.account_vars.locals.account_name
  aws_region   = local.region_vars.locals.aws_region
  environment  = local.env_vars.locals.environment
}

# Generate provider configuration
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"

  default_tags {
    tags = {
      Environment = "${local.environment}"
      ManagedBy   = "terragrunt"
      Account     = "${local.account_name}"
    }
  }
}
EOF
}

# Remote state configuration
remote_state {
  backend = "s3"
  config = {
    bucket         = "mycompany-terraform-state-${local.account_id}"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = local.aws_region
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

# Common inputs for all modules
inputs = {
  environment = local.environment
  aws_region  = local.aws_region
}
```

## Module Configuration

```hcl
# environments/production/vpc/terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "git::git@github.com:myorg/terraform-modules.git//aws/vpc?ref=v2.1.0"
}

inputs = {
  name       = "production-vpc"
  cidr_block = "10.0.0.0/16"

  availability_zones = [
    "us-west-2a",
    "us-west-2b",
    "us-west-2c"
  ]

  public_subnet_cidrs = [
    "10.0.1.0/24",
    "10.0.2.0/24",
    "10.0.3.0/24"
  ]

  private_subnet_cidrs = [
    "10.0.11.0/24",
    "10.0.12.0/24",
    "10.0.13.0/24"
  ]
}
```

## Dependencies

### Basic Dependency

```hcl
# environments/production/eks/terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

dependency "vpc" {
  config_path = "../vpc"

  # Mock outputs for plan without apply
  mock_outputs = {
    vpc_id             = "vpc-mock"
    private_subnet_ids = ["subnet-mock-1", "subnet-mock-2"]
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

terraform {
  source = "git::git@github.com:myorg/terraform-modules.git//aws/eks?ref=v3.0.0"
}

inputs = {
  cluster_name = "production-eks"
  vpc_id       = dependency.vpc.outputs.vpc_id
  subnet_ids   = dependency.vpc.outputs.private_subnet_ids
}
```

### Multiple Dependencies

```hcl
# environments/production/app/terragrunt.hcl
dependency "vpc" {
  config_path = "../vpc"
}

dependency "eks" {
  config_path = "../eks"
}

dependency "rds" {
  config_path = "../rds"
}

inputs = {
  vpc_id              = dependency.vpc.outputs.vpc_id
  cluster_endpoint    = dependency.eks.outputs.cluster_endpoint
  database_endpoint   = dependency.rds.outputs.endpoint
  database_secret_arn = dependency.rds.outputs.secret_arn
}
```

### Cross-Environment Dependencies

```hcl
# environments/production/app/terragrunt.hcl
dependency "shared_services" {
  config_path = "../../shared/dns"
}

inputs = {
  hosted_zone_id = dependency.shared_services.outputs.hosted_zone_id
}
```

## Include Patterns

### Multiple Includes

```hcl
# environments/production/eks/terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

include "env" {
  path   = find_in_parent_folders("env.hcl")
  expose = true
}

include "eks_common" {
  path   = "${dirname(find_in_parent_folders())}/common/eks.hcl"
  expose = true
}

inputs = merge(
  include.eks_common.inputs,
  {
    cluster_name = "${include.env.locals.environment}-eks"
  }
)
```

### Partial Includes

```hcl
# common/eks.hcl
locals {
  cluster_version = "1.29"
  node_groups = {
    default = {
      instance_types = ["t3.large"]
      min_size       = 2
      max_size       = 10
    }
  }
}

inputs = {
  cluster_version = local.cluster_version
  node_groups     = local.node_groups
}
```

## Generate Blocks

### Dynamic Backend

```hcl
generate "backend" {
  path      = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  backend "s3" {
    bucket         = "${local.state_bucket}"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "${local.aws_region}"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
EOF
}
```

### Dynamic Providers

```hcl
generate "versions" {
  path      = "versions.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
  }
}
EOF
}
```

## Hooks

### Before and After Hooks

```hcl
terraform {
  source = "git::git@github.com:myorg/modules.git//vpc"

  before_hook "validate" {
    commands = ["apply", "plan"]
    execute  = ["tflint", "--init"]
  }

  before_hook "checkov" {
    commands = ["apply", "plan"]
    execute  = ["checkov", "-d", "."]
  }

  after_hook "notify" {
    commands     = ["apply"]
    execute      = ["./scripts/notify-slack.sh"]
    run_on_error = true
  }
}
```

### Error Hooks

```hcl
terraform {
  error_hook "notify_failure" {
    commands  = ["apply", "plan"]
    execute   = ["./scripts/alert-on-failure.sh"]
    on_errors = [".*"]
  }
}
```

## run-all Commands

### Apply All with Dependencies

```bash
# Apply all modules respecting dependencies
cd environments/production
terragrunt run-all apply

# Plan with parallel execution
terragrunt run-all plan --terragrunt-parallelism 5

# Destroy in reverse dependency order
terragrunt run-all destroy
```

### Selective Execution

```bash
# Only apply specific modules
terragrunt run-all apply \
  --terragrunt-include-dir "*/vpc" \
  --terragrunt-include-dir "*/eks"

# Exclude specific modules
terragrunt run-all plan \
  --terragrunt-exclude-dir "*/deprecated"

# Ignore dependencies (parallel, no order)
terragrunt run-all apply --terragrunt-ignore-dependency-errors
```

## Environment Files

```hcl
# environments/production/env.hcl
locals {
  environment = "production"

  common_tags = {
    Environment = "production"
    Team        = "platform"
    CostCenter  = "infrastructure"
  }

  # Environment-specific sizing
  instance_sizes = {
    small  = "t3.small"
    medium = "t3.medium"
    large  = "t3.large"
  }
}
```

```hcl
# regions/us-west-2/region.hcl
locals {
  aws_region = "us-west-2"

  availability_zones = [
    "us-west-2a",
    "us-west-2b",
    "us-west-2c"
  ]
}
```

```hcl
# accounts/production/account.hcl
locals {
  account_id   = "123456789012"
  account_name = "production"

  # Account-specific settings
  allowed_account_ids = ["123456789012"]
}
```

## Reading Configuration

```hcl
locals {
  # Read from parent folders
  account_vars = read_terragrunt_config(find_in_parent_folders("account.hcl"))
  region_vars  = read_terragrunt_config(find_in_parent_folders("region.hcl"))
  env_vars     = read_terragrunt_config(find_in_parent_folders("env.hcl"))

  # Access locals from included files
  account_id  = local.account_vars.locals.account_id
  aws_region  = local.region_vars.locals.aws_region
  environment = local.env_vars.locals.environment

  # Read YAML files
  config = yamldecode(file("${get_terragrunt_dir()}/config.yaml"))

  # Read JSON files
  settings = jsondecode(file("${get_terragrunt_dir()}/settings.json"))
}
```

## Functions

```hcl
locals {
  # Path functions
  root_dir    = get_repo_root()
  module_dir  = get_terragrunt_dir()
  parent_dir  = get_parent_terragrunt_dir()
  relative    = path_relative_to_include()

  # Environment variables
  ci_build = get_env("CI", "false")

  # AWS caller identity
  account_id = get_aws_account_id()

  # Conditional logic
  is_production = local.environment == "production"
  instance_type = local.is_production ? "t3.large" : "t3.small"
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Terragrunt
on:
  push:
    branches: [main]
  pull_request:

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_wrapper: false

      - name: Setup Terragrunt
        run: |
          curl -L https://github.com/gruntwork-io/terragrunt/releases/latest/download/terragrunt_linux_amd64 -o terragrunt
          chmod +x terragrunt && sudo mv terragrunt /usr/local/bin/

      - name: Plan All
        run: |
          cd environments/production
          terragrunt run-all plan --terragrunt-non-interactive

  apply:
    needs: plan
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Apply All
        run: |
          cd environments/production
          terragrunt run-all apply --terragrunt-non-interactive -auto-approve
```

## Best Practices

1. **Keep root terragrunt.hcl minimal** - Only common config
2. **Use include for shared patterns** - DRY configuration
3. **Pin module versions** - Always use refs, never branches
4. **Use mock outputs** - Enable planning without dependencies
5. **Separate state per module** - Use path_relative_to_include()
6. **Use terragrunt.hcl in each module** - Explicit configuration
7. **Leverage generate blocks** - Dynamic provider/backend configs
8. **Use run-all carefully** - Understand dependency implications
9. **Implement hooks** - Validation, linting, notifications
10. **Use --terragrunt-parallelism** - Control concurrent operations
