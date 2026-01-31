# OpenTofu Reference

OpenTofu is an open-source, community-driven fork of Terraform maintained under the Linux Foundation. It provides full HCL compatibility with additional features not available in Terraform's BSL-licensed versions.

## Installation

```bash
# macOS
brew install opentofu

# Linux (Debian/Ubuntu)
curl -fsSL https://get.opentofu.org/install-opentofu.sh | sudo bash -s -- --install-method deb

# Linux (RHEL/Fedora)
curl -fsSL https://get.opentofu.org/install-opentofu.sh | sudo bash -s -- --install-method rpm

# Docker
docker run --rm -v $(pwd):/workspace -w /workspace ghcr.io/opentofu/opentofu:latest init
```

## CLI Commands

OpenTofu uses `tofu` instead of `terraform`. All subcommands are identical:

```bash
tofu init        # Initialize working directory
tofu validate    # Validate configuration
tofu plan        # Generate execution plan
tofu apply       # Apply changes
tofu destroy     # Destroy infrastructure
tofu fmt         # Format configuration
tofu state       # State management
tofu import      # Import existing resources
tofu output      # Show output values
```

## Version Compatibility

| OpenTofu Version | Terraform Equivalent | Key Features |
|------------------|---------------------|--------------|
| 1.6.x | 1.6.x | Initial fork, full compatibility |
| 1.7.x | N/A | State encryption, improved testing |
| 1.8.x | N/A | Early evaluation, provider-defined functions |
| 1.9.x | N/A | Enhanced encryption, -exclude flag |

## Migration from Terraform

### Simple Migration

For most projects, migration requires no configuration changes:

```bash
# In existing Terraform project
tofu init     # Re-initializes with OpenTofu
tofu plan     # Verify no unexpected changes
tofu apply    # Continue as normal
```

### Provider Registry

OpenTofu maintains a compatible registry at `registry.opentofu.org`. Most providers work without changes:

```hcl
# Terraform registry (still works)
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Explicit OpenTofu registry
terraform {
  required_providers {
    aws = {
      source  = "registry.opentofu.org/hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### Lock File Compatibility

The `.terraform.lock.hcl` file is fully compatible:

```bash
# Existing lock file works with OpenTofu
tofu init

# Generate new lock file for both platforms
tofu providers lock -platform=linux_amd64 -platform=darwin_amd64
```

## State Encryption (1.7+)

OpenTofu provides built-in state encryption, a feature only available in Terraform Enterprise.

### PBKDF2 Key Provider

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "main" {
      passphrase = var.state_passphrase

      # Optional: customize derivation
      key_length   = 32
      iterations   = 600000
      salt_length  = 32
      hash_function = "sha512"
    }

    method "aes_gcm" "encrypt" {
      keys = key_provider.pbkdf2.main
    }

    state {
      method = method.aes_gcm.encrypt
    }

    plan {
      method = method.aes_gcm.encrypt
    }
  }
}

variable "state_passphrase" {
  type      = string
  sensitive = true
}
```

### AWS KMS Key Provider

```hcl
terraform {
  encryption {
    key_provider "aws_kms" "main" {
      kms_key_id = "alias/tofu-state-key"
      region     = "us-west-2"

      # Optional: assume role
      assume_role {
        role_arn = "arn:aws:iam::123456789012:role/TofuStateEncryption"
      }
    }

    method "aes_gcm" "encrypt" {
      keys = key_provider.aws_kms.main
    }

    state {
      method = method.aes_gcm.encrypt
    }
  }
}
```

### GCP KMS Key Provider

```hcl
terraform {
  encryption {
    key_provider "gcp_kms" "main" {
      kms_encryption_key = "projects/my-project/locations/global/keyRings/tofu/cryptoKeys/state"
    }

    method "aes_gcm" "encrypt" {
      keys = key_provider.gcp_kms.main
    }

    state {
      method = method.aes_gcm.encrypt
    }
  }
}
```

### Encryption Migration

Migrate from unencrypted to encrypted state:

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "new" {
      passphrase = var.new_passphrase
    }

    method "aes_gcm" "encrypt" {
      keys = key_provider.pbkdf2.new
    }

    method "unencrypted" "migrate" {}

    state {
      method   = method.aes_gcm.encrypt
      fallback {
        method = method.unencrypted.migrate
      }
    }
  }
}
```

## Early Evaluation (1.8+)

OpenTofu 1.8+ allows variables in backend and module source configurations.

### Dynamic Backend Configuration

```hcl
variable "environment" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

terraform {
  backend "s3" {
    bucket = "mycompany-tfstate-${var.environment}"
    key    = "infrastructure/terraform.tfstate"
    region = var.aws_region
  }
}
```

### Dynamic Module Sources

```hcl
variable "module_version" {
  type    = string
  default = "v1.2.0"
}

module "vpc" {
  source = "git::https://github.com/myorg/terraform-modules.git//vpc?ref=${var.module_version}"

  cidr_block = "10.0.0.0/16"
}
```

### Conditional Module Loading

```hcl
variable "use_private_registry" {
  type    = bool
  default = false
}

module "compute" {
  source = var.use_private_registry ? (
    "app.terraform.io/myorg/compute/aws"
  ) : (
    "registry.opentofu.org/hashicorp/compute/aws"
  )

  version = "~> 3.0"
}
```

## Provider-Defined Functions

OpenTofu extends support for provider-defined functions:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Use provider-defined functions
locals {
  arn_parts = provider::aws::arn_parse("arn:aws:s3:::my-bucket")
  bucket_name = local.arn_parts.resource
}
```

## Testing Framework

OpenTofu includes enhanced testing capabilities:

```hcl
# tests/vpc.tftest.hcl
run "create_vpc" {
  command = apply

  variables {
    name       = "test-vpc"
    cidr_block = "10.0.0.0/16"
  }

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR block mismatch"
  }
}

run "verify_subnets" {
  command = plan

  variables {
    name                = "test-vpc"
    cidr_block          = "10.0.0.0/16"
    public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  }

  assert {
    condition     = length(aws_subnet.public) == 2
    error_message = "Expected 2 public subnets"
  }
}
```

Run tests:

```bash
tofu test
tofu test -filter=tests/vpc.tftest.hcl
tofu test -verbose
```

## Resource Exclusion (1.9+)

Exclude specific resources from operations:

```bash
# Exclude specific resource
tofu plan -exclude=aws_instance.expensive

# Exclude module
tofu apply -exclude=module.database

# Multiple exclusions
tofu destroy -exclude=aws_rds_instance.production -exclude=aws_s3_bucket.backups
```

## CI/CD Integration

### GitHub Actions

```yaml
name: OpenTofu
on:
  push:
    branches: [main]
  pull_request:

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: 1.8.0

      - name: Init
        run: tofu init

      - name: Plan
        run: tofu plan -out=tfplan

      - name: Apply
        if: github.ref == 'refs/heads/main'
        run: tofu apply -auto-approve tfplan
```

### GitLab CI

```yaml
.tofu:
  image: ghcr.io/opentofu/opentofu:1.8
  before_script:
    - tofu init

plan:
  extends: .tofu
  script:
    - tofu plan -out=tfplan
  artifacts:
    paths:
      - tfplan

apply:
  extends: .tofu
  script:
    - tofu apply -auto-approve tfplan
  when: manual
  only:
    - main
```

## Module Compatibility Pattern

Create modules compatible with both Terraform and OpenTofu:

```hcl
# versions.tf - works with both
terraform {
  required_version = ">= 1.5.0"  # Minimum for both tools

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Optional: OpenTofu-specific features
# versions.tofu.tf - only loaded by OpenTofu
terraform {
  required_version = ">= 1.8.0"

  # State encryption for OpenTofu users
  encryption {
    key_provider "pbkdf2" "default" {
      passphrase = var.encryption_passphrase
    }
    method "aes_gcm" "default" {
      keys = key_provider.pbkdf2.default
    }
    state {
      method = method.aes_gcm.default
      enforced = false  # Allow unencrypted fallback
    }
  }
}
```

## Troubleshooting

### Provider Not Found

```bash
# Clear cache and reinitialize
rm -rf .terraform
tofu init -upgrade
```

### State Lock Issues

```bash
# Force unlock (use with caution)
tofu force-unlock LOCK_ID
```

### Encryption Key Issues

```bash
# Decrypt state for debugging
tofu state pull > state.json

# Re-encrypt with new key
TF_VAR_new_passphrase="newkey" tofu init -reconfigure
```

## Resources

- [OpenTofu Documentation](https://opentofu.org/docs/)
- [OpenTofu Registry](https://registry.opentofu.org/)
- [GitHub Repository](https://github.com/opentofu/opentofu)
- [Migration Guide](https://opentofu.org/docs/intro/migration/)
- [State Encryption](https://opentofu.org/docs/language/state/encryption/)
