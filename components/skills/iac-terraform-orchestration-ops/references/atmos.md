# Atmos Reference

Atmos is a universal tool for DevOps and Cloud Automation that provides a framework for managing Terraform configurations at enterprise scale with component catalogs, stack inheritance, and workflow automation.

## Installation

```bash
# macOS
brew install cloudposse/tap/atmos

# Linux
curl -L https://github.com/cloudposse/atmos/releases/latest/download/atmos_linux_amd64 -o atmos
chmod +x atmos && sudo mv atmos /usr/local/bin/

# Go install
go install github.com/cloudposse/atmos@latest

# Docker
docker run --rm -v $(pwd):/workspace cloudposse/atmos:latest version
```

## CLI Commands

```bash
# Stack operations
atmos terraform plan <component> -s <stack>      # Plan component in stack
atmos terraform apply <component> -s <stack>     # Apply component
atmos terraform destroy <component> -s <stack>   # Destroy component
atmos terraform output <component> -s <stack>    # Show outputs

# Workflow operations
atmos workflow <workflow> -s <stack>             # Run workflow
atmos workflow <workflow> -s <stack> --dry-run   # Dry run

# Utility commands
atmos describe stacks                            # List all stacks
atmos describe component <component> -s <stack>  # Describe component
atmos validate stacks                            # Validate configuration
atmos vendor pull                                # Pull vendored dependencies

# Other
atmos version                                    # Show version
atmos docs                                       # Generate documentation
```

## Project Structure

```
infrastructure/
├── atmos.yaml                      # Main configuration
├── stacks/
│   ├── catalog/                    # Component defaults
│   │   ├── vpc/
│   │   │   └── defaults.yaml
│   │   ├── eks/
│   │   │   └── defaults.yaml
│   │   └── rds/
│   │       └── defaults.yaml
│   ├── mixins/                     # Shared configurations
│   │   ├── region/
│   │   │   ├── us-west-2.yaml
│   │   │   └── eu-west-1.yaml
│   │   └── stage/
│   │       ├── dev.yaml
│   │       ├── staging.yaml
│   │       └── prod.yaml
│   └── orgs/                       # Organization stacks
│       └── myorg/
│           └── prod/
│               └── us-west-2/
│                   ├── _defaults.yaml
│                   ├── vpc.yaml
│                   ├── eks.yaml
│                   └── rds.yaml
├── components/                     # Terraform components
│   └── terraform/
│       ├── vpc/
│       ├── eks/
│       └── rds/
└── vendor/                         # Vendored components
```

## Configuration (atmos.yaml)

```yaml
# atmos.yaml
base_path: "."

components:
  terraform:
    base_path: "components/terraform"
    apply_auto_approve: false
    deploy_run_init: true
    init_run_reconfigure: true
    auto_generate_backend_file: true

stacks:
  base_path: "stacks"
  included_paths:
    - "orgs/**/*"
  excluded_paths:
    - "**/catalog/**"
    - "**/mixins/**"
  name_pattern: "{stage}-{environment}"

logs:
  verbose: false
  colors: true

# Schema validation
schemas:
  jsonschema:
    base_path: "stacks/schemas"
  opa:
    base_path: "stacks/policies"

# Workflows
workflows:
  base_path: "stacks/workflows"
```

## Stack Configuration

### Basic Stack

```yaml
# stacks/orgs/myorg/prod/us-west-2/vpc.yaml
import:
  - catalog/vpc/defaults

vars:
  stage: prod
  environment: us-west-2
  namespace: myorg

components:
  terraform:
    vpc:
      metadata:
        component: vpc
      vars:
        name: production-vpc
        cidr_block: "10.0.0.0/16"
        availability_zones:
          - us-west-2a
          - us-west-2b
          - us-west-2c
```

### Component with Defaults

```yaml
# stacks/catalog/vpc/defaults.yaml
components:
  terraform:
    vpc:
      metadata:
        type: abstract
      settings:
        spacelift:
          workspace_enabled: true
      vars:
        enable_dns_hostnames: true
        enable_dns_support: true
        enable_nat_gateway: true
        single_nat_gateway: false
        tags:
          ManagedBy: atmos
```

### Stack with Inheritance

```yaml
# stacks/orgs/myorg/prod/us-west-2/eks.yaml
import:
  - catalog/eks/defaults
  - mixins/region/us-west-2
  - mixins/stage/prod

components:
  terraform:
    eks:
      metadata:
        component: eks
        inherits:
          - eks/defaults
      vars:
        cluster_name: production-eks
        cluster_version: "1.29"
        # Reference VPC outputs
        vpc_id: !terraform.output vpc vpc_id
        subnet_ids: !terraform.output vpc private_subnet_ids
```

## Component Catalog

### Abstract Component

```yaml
# stacks/catalog/eks/defaults.yaml
components:
  terraform:
    eks/defaults:
      metadata:
        type: abstract
      vars:
        kubernetes_version: "1.29"
        enabled_cluster_log_types:
          - api
          - audit
          - authenticator
        node_groups:
          default:
            instance_types:
              - t3.large
            desired_size: 3
            min_size: 2
            max_size: 10
        addons:
          - name: vpc-cni
            version: latest
          - name: kube-proxy
            version: latest
          - name: coredns
            version: latest
```

### Derived Component

```yaml
# stacks/orgs/myorg/prod/us-west-2/eks.yaml
components:
  terraform:
    eks:
      metadata:
        component: eks
        inherits:
          - eks/defaults
      vars:
        cluster_name: ${namespace}-${stage}-eks
        node_groups:
          # Override defaults
          default:
            instance_types:
              - m5.xlarge
            desired_size: 5
            min_size: 3
            max_size: 20
          # Add new node group
          gpu:
            instance_types:
              - p3.2xlarge
            desired_size: 2
            max_size: 10
            taints:
              - key: nvidia.com/gpu
                value: "true"
                effect: NoSchedule
```

## Mixins

### Region Mixin

```yaml
# stacks/mixins/region/us-west-2.yaml
vars:
  region: us-west-2
  availability_zones:
    - us-west-2a
    - us-west-2b
    - us-west-2c

settings:
  aws:
    region: us-west-2
```

### Stage Mixin

```yaml
# stacks/mixins/stage/prod.yaml
vars:
  stage: prod

  # Production sizing
  instance_size: large

  # Production settings
  deletion_protection: true
  multi_az: true
  backup_retention_period: 30

settings:
  spacelift:
    protect_from_deletion: true
```

## Cross-Component References

### Output References

```yaml
# stacks/orgs/myorg/prod/us-west-2/eks.yaml
components:
  terraform:
    eks:
      vars:
        # Reference outputs from VPC component
        vpc_id: !terraform.output vpc vpc_id
        private_subnet_ids: !terraform.output vpc private_subnet_ids

        # Reference from different stack
        shared_security_group: !terraform.output security//shared-sg security_group_id
```

### Remote State

```yaml
# stacks/orgs/myorg/prod/us-west-2/rds.yaml
components:
  terraform:
    rds:
      vars:
        vpc_id: !terraform.output vpc vpc_id
        subnet_ids: !terraform.output vpc database_subnet_ids

        # Reference from another account/stack
        kms_key_arn: !terraform.output security/kms//database-key key_arn
```

## Workflows

### Basic Workflow

```yaml
# stacks/workflows/deploy.yaml
name: Deploy Infrastructure
description: Deploy all components in order

workflows:
  deploy:
    description: Deploy full stack
    steps:
      - command: terraform apply vpc -s ${stack} -auto-approve
      - command: terraform apply eks -s ${stack} -auto-approve
      - command: terraform apply rds -s ${stack} -auto-approve
      - command: terraform apply app -s ${stack} -auto-approve
```

### Parameterized Workflow

```yaml
# stacks/workflows/promote.yaml
name: Promote to Production
description: Promote changes from staging to production

workflows:
  promote:
    description: Promote component to production
    steps:
      - command: terraform plan ${component} -s staging-us-west-2
      - command: terraform plan ${component} -s prod-us-west-2
      - command: terraform apply ${component} -s prod-us-west-2 -auto-approve
```

### Complex Workflow

```yaml
# stacks/workflows/full-deploy.yaml
workflows:
  full-deploy:
    description: Full infrastructure deployment
    steps:
      # Network layer
      - command: terraform apply vpc -s ${stack} -auto-approve
        name: Deploy VPC

      # Security layer
      - command: terraform apply security-groups -s ${stack} -auto-approve
        name: Deploy Security Groups

      # Data layer (parallel)
      - command: terraform apply rds -s ${stack} -auto-approve
        name: Deploy RDS
      - command: terraform apply elasticache -s ${stack} -auto-approve
        name: Deploy ElastiCache

      # Compute layer
      - command: terraform apply eks -s ${stack} -auto-approve
        name: Deploy EKS

      # Application layer
      - command: terraform apply app -s ${stack} -auto-approve
        name: Deploy Application
```

Run workflows:
```bash
atmos workflow deploy -s prod-us-west-2
atmos workflow promote -s staging-us-west-2 component=eks
atmos workflow full-deploy -s prod-us-west-2 --dry-run
```

## Vendoring

### Vendor Configuration

```yaml
# vendor.yaml
apiVersion: atmos/v1
kind: AtmosVendorConfig
metadata:
  name: vendor-config

spec:
  sources:
    - component: vpc
      source: github.com/cloudposse/terraform-aws-vpc
      version: 2.1.0
      included_paths:
        - "**/*.tf"
      excluded_paths:
        - "examples/**"

    - component: eks
      source: github.com/cloudposse/terraform-aws-eks-cluster
      version: 3.0.0

    - component: label
      source: github.com/cloudposse/terraform-null-label
      version: 0.25.0
```

Pull vendors:
```bash
atmos vendor pull
atmos vendor pull --component vpc
```

## Stack Validation

### JSON Schema

```yaml
# stacks/schemas/vpc.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "vars": {
      "type": "object",
      "properties": {
        "cidr_block": {
          "type": "string",
          "pattern": "^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$"
        }
      },
      "required": ["cidr_block"]
    }
  }
}
```

### OPA Policy

```rego
# stacks/policies/production.rego
package atmos

deny[msg] {
  input.vars.stage == "prod"
  not input.vars.deletion_protection
  msg = "Production resources must have deletion_protection enabled"
}

deny[msg] {
  input.vars.stage == "prod"
  not input.vars.multi_az
  msg = "Production databases must be multi-AZ"
}
```

Validate:
```bash
atmos validate stacks
atmos validate stacks --schemas-atmos-manifest
```

## Spacelift Integration

```yaml
# Stack configuration with Spacelift settings
components:
  terraform:
    vpc:
      settings:
        spacelift:
          workspace_enabled: true
          autodeploy: true
          branch: main
          triggers:
            - vpc-trigger
          labels:
            - production
            - network
          policies:
            - approval-policy
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Atmos
on:
  push:
    branches: [main]
  pull_request:
    paths:
      - 'stacks/**'
      - 'components/**'

jobs:
  plan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        stack: [dev-us-west-2, staging-us-west-2, prod-us-west-2]
        component: [vpc, eks, rds]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Atmos
        run: |
          curl -L https://github.com/cloudposse/atmos/releases/latest/download/atmos_linux_amd64 -o atmos
          chmod +x atmos && sudo mv atmos /usr/local/bin/

      - name: Plan
        run: atmos terraform plan ${{ matrix.component }} -s ${{ matrix.stack }}

  apply:
    needs: plan
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy
        run: atmos workflow deploy -s prod-us-west-2
```

## Terraform Component

```hcl
# components/terraform/vpc/main.tf
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = var.name
  cidr = var.cidr_block

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway = var.enable_nat_gateway
  single_nat_gateway = var.single_nat_gateway

  tags = module.this.tags
}

# components/terraform/vpc/context.tf
module "this" {
  source  = "cloudposse/label/null"
  version = "0.25.0"

  namespace   = var.namespace
  stage       = var.stage
  environment = var.environment
  name        = var.name

  tags = var.tags
}
```

## Template Functions

```yaml
# stacks/orgs/myorg/prod/us-west-2/app.yaml
vars:
  # String interpolation
  cluster_name: ${namespace}-${stage}-${environment}-eks

  # Terraform functions in YAML
  instance_count: ${{ if eq .vars.stage "prod" }}10${{ else }}2${{ end }}

  # Environment references
  aws_account_id: ${AWS_ACCOUNT_ID}
```

## Best Practices

1. **Use component catalog** - Abstract components for reuse
2. **Leverage mixins** - Shared configurations for regions/stages
3. **Implement inheritance** - DRY configurations
4. **Define workflows** - Encapsulate deployment processes
5. **Validate with schemas** - JSON Schema and OPA policies
6. **Vendor dependencies** - Pin and manage external modules
7. **Use consistent naming** - namespace-stage-environment pattern
8. **Reference outputs** - Cross-component dependencies
9. **Integrate Spacelift** - Enterprise deployment automation
10. **Document stacks** - Use describe commands for documentation
