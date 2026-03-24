# Terramate Reference

Terramate is a stack orchestration tool for Terraform that provides Git-based change detection, code generation, and parallel execution capabilities.

## Installation

```bash
# macOS
brew install terramate

# Linux
curl -L https://github.com/terramate-io/terramate/releases/latest/download/terramate_linux_amd64.tar.gz | tar xz
sudo mv terramate /usr/local/bin/

# Go install
go install github.com/terramate-io/terramate/cmd/terramate@latest

# Docker
docker run --rm -v $(pwd):/workspace ghcr.io/terramate-io/terramate:latest list
```

## CLI Commands

```bash
# Stack management
terramate list                    # List all stacks
terramate list --changed          # List changed stacks
terramate list --run-order        # Show execution order
terramate create <path>           # Create new stack

# Execution
terramate run <command>           # Run command in all stacks
terramate run --changed <cmd>     # Run only in changed stacks
terramate run --parallel <cmd>    # Run in parallel

# Code generation
terramate generate                # Generate code from templates
terramate generate --check        # Check if generation needed

# Other commands
terramate fmt                     # Format Terramate files
terramate validate               # Validate configuration
terramate debug show globals     # Show global values
terramate experimental clone     # Clone stack
```

## Project Structure

```
infrastructure/
├── terramate.tm.hcl            # Root configuration
├── stacks/
│   ├── _globals.tm.hcl         # Shared globals
│   ├── vpc/
│   │   ├── stack.tm.hcl
│   │   ├── main.tf
│   │   └── variables.tf
│   ├── eks/
│   │   ├── stack.tm.hcl
│   │   ├── main.tf
│   │   └── variables.tf
│   └── rds/
│       ├── stack.tm.hcl
│       └── ...
├── modules/                    # Shared modules
│   └── ...
└── imports/                    # Shared configurations
    ├── backend.tm.hcl
    └── providers.tm.hcl
```

## Root Configuration

```hcl
# terramate.tm.hcl
terramate {
  required_version = "~> 0.6"

  config {
    git {
      default_branch = "main"
      check_untracked = true
      check_uncommitted = true
    }

    run {
      env {
        TF_INPUT = "0"
      }
    }

    experiments = [
      "scripts"
    ]
  }
}
```

## Stack Definition

### Basic Stack

```hcl
# stacks/vpc/stack.tm.hcl
stack {
  name        = "vpc"
  description = "VPC infrastructure"
  id          = "vpc-us-west-2-prod"

  tags = [
    "network",
    "production"
  ]
}
```

### Stack with Dependencies

```hcl
# stacks/eks/stack.tm.hcl
stack {
  name        = "eks"
  description = "EKS cluster"
  id          = "eks-us-west-2-prod"

  # Run after VPC stack
  after = [
    "tag:network"
  ]

  # Or explicit path
  # after = ["../vpc"]

  tags = [
    "compute",
    "kubernetes",
    "production"
  ]
}
```

## Globals

### Project Globals

```hcl
# stacks/_globals.tm.hcl
globals {
  project     = "myproject"
  environment = "production"
  aws_region  = "us-west-2"

  common_tags = {
    Project     = global.project
    Environment = global.environment
    ManagedBy   = "terramate"
  }

  # Computed values
  state_bucket = "terraform-state-${global.project}-${global.environment}"
}
```

### Stack-Level Globals

```hcl
# stacks/vpc/stack.tm.hcl
stack {
  name = "vpc"
  id   = "vpc-prod"
}

globals {
  # Override or extend project globals
  component = "vpc"

  vpc_cidr = "10.0.0.0/16"

  availability_zones = [
    "${global.aws_region}a",
    "${global.aws_region}b",
    "${global.aws_region}c"
  ]
}
```

## Code Generation

### Generate Backend Configuration

```hcl
# imports/backend.tm.hcl
generate_hcl "_backend.tf" {
  content {
    terraform {
      backend "s3" {
        bucket         = global.state_bucket
        key            = "stacks/${terramate.stack.path.relative}/terraform.tfstate"
        region         = global.aws_region
        encrypt        = true
        dynamodb_table = "terraform-locks"
      }
    }
  }
}
```

### Generate Provider Configuration

```hcl
# imports/providers.tm.hcl
generate_hcl "_providers.tf" {
  content {
    provider "aws" {
      region = global.aws_region

      default_tags {
        tags = global.common_tags
      }
    }

    terraform {
      required_version = ">= 1.5.0"

      required_providers {
        aws = {
          source  = "hashicorp/aws"
          version = "~> 5.0"
        }
      }
    }
  }
}
```

### Generate Variables

```hcl
# stacks/vpc/generate.tm.hcl
generate_hcl "_variables.tf" {
  content {
    variable "environment" {
      type    = string
      default = global.environment
    }

    variable "vpc_cidr" {
      type    = string
      default = global.vpc_cidr
    }

    variable "availability_zones" {
      type    = list(string)
      default = global.availability_zones
    }
  }
}
```

### Generate from Templates

```hcl
generate_file "terraform.tfvars" {
  content = <<-EOT
    environment = "${global.environment}"
    vpc_cidr    = "${global.vpc_cidr}"

    availability_zones = ${tm_jsonencode(global.availability_zones)}
  EOT
}
```

### Conditional Generation

```hcl
generate_hcl "_monitoring.tf" {
  condition = tm_contains(terramate.stack.tags, "production")

  content {
    module "monitoring" {
      source = "../../modules/monitoring"

      environment = global.environment
      alert_email = global.alert_email
    }
  }
}
```

## Change Detection

### Git-Based Detection

```bash
# List stacks changed since main branch
terramate list --changed

# List stacks changed in last commit
terramate list --changed --git-change-base HEAD~1

# Run only in changed stacks
terramate run --changed -- terraform plan

# Force include unchanged stacks
terramate run --changed --enable-change-detection=false -- terraform plan
```

### Ignore Patterns

```hcl
# terramate.tm.hcl
terramate {
  config {
    change_detection {
      git {
        untracked   = "error"
        uncommitted = "error"

        ignore_paths = [
          "*.md",
          "docs/**",
          ".github/**"
        ]
      }
    }
  }
}
```

## Running Commands

### Basic Execution

```bash
# Run terraform init in all stacks
terramate run -- terraform init

# Run in specific stacks by tag
terramate run --tags production -- terraform plan

# Run with environment variables
terramate run --env AWS_PROFILE=production -- terraform apply
```

### Parallel Execution

```bash
# Run in parallel (default: 5 workers)
terramate run --parallel -- terraform init

# Control parallelism
terramate run --parallel 10 -- terraform plan

# Parallel with changed stacks only
terramate run --parallel --changed -- terraform apply
```

### Ordered Execution

```bash
# Show execution order
terramate list --run-order

# Run respecting dependencies
terramate run -- terraform apply -auto-approve

# Reverse order (for destroy)
terramate run --reverse -- terraform destroy -auto-approve
```

## Scripts

```hcl
# terramate.tm.hcl
terramate {
  config {
    experiments = ["scripts"]
  }
}

script "deploy" {
  name        = "Deploy Stack"
  description = "Initialize and apply Terraform"

  job {
    name = "init"
    commands = [
      ["terraform", "init", "-upgrade"]
    ]
  }

  job {
    name = "apply"
    commands = [
      ["terraform", "apply", "-auto-approve"]
    ]
  }
}

script "destroy" {
  name = "Destroy Stack"

  job {
    commands = [
      ["terraform", "destroy", "-auto-approve"]
    ]
  }
}
```

Run scripts:
```bash
terramate script run deploy
terramate script run --changed deploy
```

## Import Patterns

### Shared Configurations

```hcl
# stacks/vpc/stack.tm.hcl
import {
  source = "/imports/backend.tm.hcl"
}

import {
  source = "/imports/providers.tm.hcl"
}

stack {
  name = "vpc"
  id   = "vpc-prod"
}
```

### Conditional Imports

```hcl
import {
  source = "/imports/monitoring.tm.hcl"
  condition = tm_contains(terramate.stack.tags, "production")
}
```

## Metadata

```hcl
# stacks/vpc/stack.tm.hcl
stack {
  name = "vpc"
  id   = "vpc-prod"
  tags = ["network", "production"]
}

# Access in other stacks
globals {
  vpc_stack_path = "/stacks/vpc"
}

# Remote state reference
generate_hcl "_data.tf" {
  content {
    data "terraform_remote_state" "vpc" {
      backend = "s3"
      config = {
        bucket = global.state_bucket
        key    = "stacks/vpc/terraform.tfstate"
        region = global.aws_region
      }
    }
  }
}
```

## Terramate Cloud Integration

```hcl
# terramate.tm.hcl
terramate {
  config {
    cloud {
      organization = "my-org"
    }
  }
}
```

```bash
# Login to Terramate Cloud
terramate cloud login

# Sync stacks
terramate cloud sync

# Trigger cloud deployment
terramate run --cloud-sync-deployment -- terraform apply
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Terramate
on:
  push:
    branches: [main]
  pull_request:

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: terramate-io/terramate-action@v1
        with:
          version: latest

      - name: List Changed Stacks
        id: changed
        run: |
          terramate list --changed | tee changed.txt
          echo "count=$(wc -l < changed.txt)" >> $GITHUB_OUTPUT

      - name: Plan Changed Stacks
        if: steps.changed.outputs.count > 0
        run: |
          terramate run --changed -- terraform init
          terramate run --changed -- terraform plan -out=plan.tfplan

  deploy:
    needs: preview
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: terramate-io/terramate-action@v1

      - name: Deploy Changed Stacks
        run: |
          terramate run --changed -- terraform init
          terramate run --changed -- terraform apply -auto-approve
```

### GitLab CI

```yaml
stages:
  - plan
  - apply

.terramate:
  image: ghcr.io/terramate-io/terramate:latest
  before_script:
    - git fetch origin main

plan:
  extends: .terramate
  stage: plan
  script:
    - terramate list --changed
    - terramate run --changed -- terraform init
    - terramate run --changed -- terraform plan
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

apply:
  extends: .terramate
  stage: apply
  script:
    - terramate run --changed -- terraform init
    - terramate run --changed -- terraform apply -auto-approve
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
  when: manual
```

## Functions

```hcl
globals {
  # String functions
  upper_env = tm_upper(global.environment)

  # Collection functions
  az_count = tm_length(global.availability_zones)
  first_az = tm_element(global.availability_zones, 0)

  # JSON encoding
  tags_json = tm_jsonencode(global.common_tags)

  # Conditionals
  is_prod = global.environment == "production"
  instance_type = tm_ternary(global.is_prod, "t3.large", "t3.small")

  # Path functions
  stack_name = terramate.stack.name
  stack_path = terramate.stack.path.relative
}
```

## Best Practices

1. **Use meaningful stack IDs** - Unique, descriptive identifiers
2. **Leverage globals hierarchy** - Project → Environment → Stack
3. **Implement change detection** - Only deploy what changed
4. **Use tags for grouping** - Filter stacks by tag
5. **Generate boilerplate** - Backend, providers, common resources
6. **Define explicit dependencies** - Use `after` for ordering
7. **Use scripts for workflows** - Encapsulate common operations
8. **Integrate with CI/CD** - Automatic change detection
9. **Validate before commit** - `terramate validate`
10. **Keep stacks small** - Single responsibility per stack
