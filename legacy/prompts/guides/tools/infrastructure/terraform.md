---
name: Terraform Infrastructure as Code Guide
module_type: guide
scope: temporary
priority: low
triggers: ["terraform", "tf", "infrastructure as code", "iac", "terraform plan", "terraform apply"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Terraform Infrastructure as Code Guide

## Purpose
Master Terraform for managing infrastructure as code, including providers, resources, modules, state management, and best practices for production deployments.

## Installation and Setup

### Installation Methods
```bash
# macOS with Homebrew
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Linux (Ubuntu/Debian)
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Using tfenv (Terraform Version Manager)
brew install tfenv
tfenv install latest
tfenv use latest

# Verify installation
terraform version
```

### Project Structure
```
terraform-project/
├── main.tf              # Main configuration
├── variables.tf         # Variable declarations
├── outputs.tf          # Output values
├── versions.tf         # Provider versions
├── terraform.tfvars    # Variable values (don't commit secrets!)
├── modules/            # Reusable modules
│   └── vpc/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/       # Environment-specific configs
    ├── dev/
    ├── staging/
    └── prod/
```

## Basic Configuration

### Provider Configuration
```hcl
# versions.tf
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

# main.tf
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
      Project     = var.project_name
    }
  }
}
```

### Variables
```hcl
# variables.tf
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_types" {
  description = "EC2 instance types by environment"
  type        = map(string)
  default = {
    dev     = "t3.micro"
    staging = "t3.small"
    prod    = "t3.medium"
  }
}

variable "enable_monitoring" {
  description = "Enable detailed monitoring"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
}
```

### Resources
```hcl
# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-vpc"
    }
  )
}

# EC2 Instance
resource "aws_instance" "web" {
  count = var.instance_count

  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_types[var.environment]
  subnet_id     = aws_subnet.private[count.index % length(aws_subnet.private)].id

  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = templatefile("${path.module}/user_data.sh", {
    environment = var.environment
    index       = count.index
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-web-${count.index + 1}"
    }
  )

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [ami]
  }
}
```

### Data Sources
```hcl
# Get latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Get existing resources
data "aws_vpc" "existing" {
  filter {
    name   = "tag:Name"
    values = ["production-vpc"]
  }
}

# Get availability zones
data "aws_availability_zones" "available" {
  state = "available"
  
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}
```

## State Management

### Backend Configuration
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    
    # Role-based access (recommended)
    role_arn = "arn:aws:iam::123456789012:role/TerraformStateRole"
  }
}

# Create state bucket and lock table
resource "aws_s3_bucket" "terraform_state" {
  bucket = "my-terraform-state-bucket"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "terraform-state-lock"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

### State Commands
```bash
# List resources in state
terraform state list

# Show specific resource
terraform state show aws_instance.web[0]

# Move resource in state
terraform state mv aws_instance.web aws_instance.app

# Remove from state (doesn't destroy actual resource)
terraform state rm aws_instance.web

# Pull current state
terraform state pull > terraform.tfstate.backup

# Push state (dangerous!)
terraform state push terraform.tfstate.backup

# Replace provider
terraform state replace-provider hashicorp/aws registry.terraform.io/hashicorp/aws
```

## Modules

### Creating Modules
```hcl
# modules/webapp/main.tf
resource "aws_instance" "app" {
  count = var.instance_count

  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_ids[count.index % length(var.subnet_ids)]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.name_prefix}-${count.index + 1}"
    }
  )
}

resource "aws_lb_target_group_attachment" "app" {
  count = var.instance_count

  target_group_arn = var.target_group_arn
  target_id        = aws_instance.app[count.index].id
  port             = var.app_port
}

# modules/webapp/variables.tf
variable "instance_count" {
  description = "Number of instances"
  type        = number
  default     = 2
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

# modules/webapp/outputs.tf
output "instance_ids" {
  description = "IDs of created instances"
  value       = aws_instance.app[*].id
}

output "private_ips" {
  description = "Private IP addresses"
  value       = aws_instance.app[*].private_ip
}
```

### Using Modules
```hcl
# main.tf
module "web_cluster" {
  source = "./modules/webapp"

  instance_count   = 3
  instance_type    = "t3.medium"
  ami_id          = data.aws_ami.ubuntu.id
  subnet_ids      = aws_subnet.private[*].id
  target_group_arn = aws_lb_target_group.web.arn
  name_prefix     = "${var.project_name}-web"
  common_tags     = var.tags
}

# Using published modules
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "${var.project_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = data.aws_availability_zones.available.names
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = var.tags
}
```

## Advanced Features

### Dynamic Blocks
```hcl
resource "aws_security_group" "dynamic" {
  name_prefix = "${var.project_name}-sg"
  vpc_id      = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }

  dynamic "egress" {
    for_each = var.allow_all_egress ? [1] : []
    content {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}
```

### For Expressions
```hcl
# Transform a list
locals {
  # Create CIDR blocks for subnets
  private_subnet_cidrs = [for i in range(var.az_count) : 
    cidrsubnet(var.vpc_cidr, 8, i)]
  
  # Create a map from a list
  instance_name_map = {for idx, instance in aws_instance.web : 
    instance.tags.Name => instance.private_ip}
  
  # Filter items
  prod_instances = [for instance in aws_instance.web : 
    instance if instance.tags.Environment == "prod"]
}

# Use in resources
resource "aws_subnet" "private" {
  count = length(local.private_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
}
```

### Conditionals
```hcl
# Conditional resource creation
resource "aws_instance" "bastion" {
  count = var.create_bastion ? 1 : 0

  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public[0].id
}

# Conditional values
resource "aws_db_instance" "main" {
  allocated_storage = var.environment == "prod" ? 100 : 20
  instance_class    = var.environment == "prod" ? "db.r5.large" : "db.t3.micro"
  
  # Conditional block
  dynamic "restore_to_point_in_time" {
    for_each = var.restore_snapshot_identifier != null ? [1] : []
    content {
      source_db_instance_identifier = var.restore_snapshot_identifier
      restore_time                  = var.restore_time
    }
  }
}
```

## Workspace Management

### Using Workspaces
```bash
# List workspaces
terraform workspace list

# Create new workspace
terraform workspace new dev
terraform workspace new prod

# Switch workspace
terraform workspace select prod

# Show current workspace
terraform workspace show

# Delete workspace
terraform workspace delete dev
```

### Workspace in Configuration
```hcl
# Use workspace in configuration
resource "aws_instance" "web" {
  count = terraform.workspace == "prod" ? 5 : 1
  
  instance_type = var.instance_types[terraform.workspace]
  
  tags = {
    Name        = "${var.project_name}-${terraform.workspace}-web"
    Environment = terraform.workspace
  }
}

# Workspace-specific variables
locals {
  env_config = {
    dev = {
      instance_type = "t3.micro"
      min_size      = 1
      max_size      = 3
    }
    prod = {
      instance_type = "t3.large"
      min_size      = 3
      max_size      = 10
    }
  }
  
  config = local.env_config[terraform.workspace]
}
```

## Testing and Validation

### Validation
```hcl
# Variable validation
variable "instance_type" {
  type = string
  validation {
    condition = can(regex("^t3\\.", var.instance_type))
    error_message = "Instance type must be from t3 family."
  }
}

# Precondition and postcondition
resource "aws_instance" "web" {
  # Precondition
  lifecycle {
    precondition {
      condition     = data.aws_ami.ubuntu.architecture == "x86_64"
      error_message = "AMI must be x86_64 architecture."
    }
    
    postcondition {
      condition     = self.public_ip != ""
      error_message = "Instance must have a public IP."
    }
  }
}
```

### Testing with Terratest
```go
// test/vpc_test.go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCCreation(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../modules/vpc",
        Vars: map[string]interface{}{
            "vpc_cidr": "10.0.0.0/16",
            "environment": "test",
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcId := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcId)
}
```

## Best Practices

### Code Organization
```hcl
# Separate configuration by purpose
# networking.tf - VPC, subnets, routing
# compute.tf - EC2, Auto Scaling
# storage.tf - S3, EBS, EFS
# database.tf - RDS, DynamoDB
# security.tf - Security groups, IAM

# Use consistent naming
resource "aws_instance" "web" {}     # Good
resource "aws_instance" "my_ec2" {}  # Avoid

# Tag everything
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    CostCenter  = var.cost_center
  }
}
```

### Security Best Practices
```hcl
# Don't hardcode secrets
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Use AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "rds/${var.environment}/password"
}

# Use IAM roles, not keys
provider "aws" {
  assume_role {
    role_arn = "arn:aws:iam::123456789012:role/TerraformRole"
  }
}

# Encrypt everything
resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

## Common Patterns

### Blue-Green Deployment
```hcl
# Blue-green with weighted routing
resource "aws_lb_target_group" "blue" {
  name_prefix = "blue-"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
}

resource "aws_lb_target_group" "green" {
  name_prefix = "green-"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
}

resource "aws_lb_listener_rule" "weighted" {
  listener_arn = aws_lb_listener.front_end.arn
  priority     = 100

  action {
    type = "forward"
    forward {
      target_group {
        arn    = aws_lb_target_group.blue.arn
        weight = var.blue_weight
      }
      target_group {
        arn    = aws_lb_target_group.green.arn
        weight = var.green_weight
      }
    }
  }

  condition {
    path_pattern {
      values = ["/*"]
    }
  }
}
```

### Multi-Region Setup
```hcl
# Define providers for multiple regions
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu_west_1"
  region = "eu-west-1"
}

# Create resources in multiple regions
resource "aws_s3_bucket" "us_bucket" {
  provider = aws.us_east_1
  bucket   = "${var.project_name}-us-east-1"
}

resource "aws_s3_bucket" "eu_bucket" {
  provider = aws.eu_west_1
  bucket   = "${var.project_name}-eu-west-1"
}

# Cross-region replication
resource "aws_s3_bucket_replication_configuration" "replication" {
  provider = aws.us_east_1
  
  role   = aws_iam_role.replication.arn
  bucket = aws_s3_bucket.us_bucket.id

  rule {
    id     = "replicate-to-eu"
    status = "Enabled"

    destination {
      bucket = aws_s3_bucket.eu_bucket.arn
    }
  }
}
```

## Troubleshooting

### Common Issues
```bash
# Initialize issues
terraform init -upgrade
terraform init -reconfigure
terraform init -backend=false  # Skip backend

# Plan/Apply issues
terraform plan -refresh=false  # Skip refresh
terraform apply -parallelism=1  # Reduce parallelism
terraform apply -target=aws_instance.web  # Target specific resource

# State issues
terraform refresh  # Update state
terraform state pull > backup.tfstate  # Backup state
terraform force-unlock <lock-id>  # Force unlock

# Debug mode
TF_LOG=DEBUG terraform plan
TF_LOG_PATH=terraform.log terraform apply
```

---
*Terraform enables infrastructure as code, providing a declarative way to define and manage cloud resources with version control, collaboration, and repeatability.*