# Utility Provider Patterns

## Template Provider (hashicorp/template)

> **Note**: The template provider is deprecated. Use `templatefile()` function instead.

### Provider Configuration
```hcl
terraform {
  required_providers {
    template = {
      source  = "hashicorp/template"
      version = "~> 2.2"
    }
  }
}
```

### Legacy Template Data Source
```hcl
# Deprecated - use templatefile() instead
data "template_file" "user_data" {
  template = file("${path.module}/templates/user_data.sh")

  vars = {
    cluster_name = var.cluster_name
    environment  = var.environment
  }
}
```

### Modern Approach: templatefile()
```hcl
# Preferred method - no provider needed
locals {
  user_data = templatefile("${path.module}/templates/user_data.sh", {
    cluster_name = var.cluster_name
    environment  = var.environment
    packages     = jsonencode(var.packages)
  })
}

# Template file: templates/user_data.sh
# #!/bin/bash
# CLUSTER_NAME="${cluster_name}"
# ENVIRONMENT="${environment}"
# PACKAGES='${packages}'
#
# for pkg in $(echo $PACKAGES | jq -r '.[]'); do
#   apt-get install -y $pkg
# done

# Using with for_each
locals {
  rendered_configs = {
    for name, config in var.services :
    name => templatefile("${path.module}/templates/service.yaml", {
      service_name = name
      port         = config.port
      replicas     = config.replicas
    })
  }
}
```

### Template Directives
```hcl
# templates/config.yaml.tpl

# String interpolation
name: ${service_name}
port: ${port}

# Conditionals
%{ if enable_ssl ~}
ssl:
  enabled: true
  certificate: /etc/ssl/cert.pem
%{ endif ~}

# Loops
replicas:
%{ for i in range(replica_count) ~}
  - id: replica-${i}
    zone: ${zones[i % length(zones)]}
%{ endfor ~}

# Strips newlines with ~
labels:
%{ for key, value in labels ~}
  ${key}: "${value}"
%{ endfor ~}
```

---

## Time Provider (hashicorp/time)

### Provider Configuration
```hcl
terraform {
  required_providers {
    time = {
      source  = "hashicorp/time"
      version = "~> 0.11"
    }
  }
}
```

### Static Time Reference
```hcl
# Capture timestamp at apply time
resource "time_static" "created" {}

output "creation_timestamp" {
  value = time_static.created.rfc3339
}

# With triggers for recreation
resource "time_static" "rotation" {
  triggers = {
    version = var.config_version
  }
}
```

### Offset Time
```hcl
# Calculate future/past times
resource "time_offset" "certificate_expiry" {
  offset_days   = 365
  offset_hours  = 0
  offset_months = 0
  offset_years  = 0

  # Or offset from specific time
  base_rfc3339 = "2024-01-01T00:00:00Z"
}

output "expiry_date" {
  value = time_offset.certificate_expiry.rfc3339
}

# Token expiration
resource "time_offset" "token_expiry" {
  offset_hours = 24

  triggers = {
    token_id = random_uuid.token.id
  }
}
```

### Rotating Time
```hcl
# Rotation schedule for secrets
resource "time_rotating" "secret_rotation" {
  rotation_days = 30
}

resource "aws_secretsmanager_secret_version" "app_secret" {
  secret_id     = aws_secretsmanager_secret.app.id
  secret_string = random_password.app.result

  lifecycle {
    replace_triggered_by = [time_rotating.secret_rotation.id]
  }
}

# More rotation options
resource "time_rotating" "daily" {
  rotation_hours = 24
}

resource "time_rotating" "weekly" {
  rotation_days = 7
}

resource "time_rotating" "monthly" {
  rotation_months = 1
}

resource "time_rotating" "yearly" {
  rotation_years = 1
}

# Rotation with specific start time
resource "time_rotating" "certificate" {
  rotation_days = 90
  rfc3339       = "2024-01-01T00:00:00Z"  # Start rotation from this time
}
```

### Sleep Resource
```hcl
# Add delays between resources
resource "time_sleep" "wait_for_propagation" {
  depends_on = [aws_route53_record.main]

  create_duration  = "60s"
  destroy_duration = "30s"
}

resource "aws_acm_certificate_validation" "cert" {
  depends_on = [time_sleep.wait_for_propagation]

  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.validation : record.fqdn]
}

# Conditional delays
resource "time_sleep" "conditional_wait" {
  count = var.wait_enabled ? 1 : 0

  create_duration = "${var.wait_seconds}s"
}
```

---

## Local Provider (hashicorp/local)

### Provider Configuration
```hcl
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}
```

### Local File
```hcl
# Write content to file
resource "local_file" "kubeconfig" {
  content  = data.aws_eks_cluster.cluster.kubeconfig
  filename = "${path.module}/kubeconfig"

  file_permission      = "0600"
  directory_permission = "0755"
}

# Write sensitive content
resource "local_sensitive_file" "private_key" {
  content         = tls_private_key.main.private_key_pem
  filename        = "${path.module}/private_key.pem"
  file_permission = "0600"
}

# Write from template
resource "local_file" "config" {
  content = templatefile("${path.module}/templates/config.yaml.tpl", {
    environment = var.environment
    endpoints   = var.endpoints
  })
  filename = "${path.module}/generated/config.yaml"
}

# Multiple files with for_each
resource "local_file" "configs" {
  for_each = var.config_files

  content  = each.value.content
  filename = "${path.module}/generated/${each.key}"
}
```

### Read File Data Source
```hcl
# Read file content
data "local_file" "existing_config" {
  filename = "${path.module}/configs/base.yaml"
}

output "config_content" {
  value = data.local_file.existing_config.content
}

# Read sensitive file
data "local_sensitive_file" "existing_key" {
  filename = var.private_key_path
}
```

### Common Use Cases
```hcl
# Generate kubeconfig
resource "local_file" "kubeconfig" {
  content = yamlencode({
    apiVersion = "v1"
    kind       = "Config"
    clusters = [{
      name = var.cluster_name
      cluster = {
        certificate-authority-data = base64encode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
        server                     = data.aws_eks_cluster.cluster.endpoint
      }
    }]
    contexts = [{
      name = var.cluster_name
      context = {
        cluster = var.cluster_name
        user    = var.cluster_name
      }
    }]
    current-context = var.cluster_name
    users = [{
      name = var.cluster_name
      user = {
        exec = {
          apiVersion = "client.authentication.k8s.io/v1beta1"
          command    = "aws"
          args       = ["eks", "get-token", "--cluster-name", var.cluster_name]
        }
      }
    }]
  })
  filename = "${path.root}/kubeconfig-${var.cluster_name}"
}

# Generate SSH config
resource "local_file" "ssh_config" {
  content = join("\n", [
    for name, instance in aws_instance.this :
    <<-EOT
    Host ${name}
      HostName ${instance.public_ip}
      User ubuntu
      IdentityFile ~/.ssh/id_rsa
      StrictHostKeyChecking no
    EOT
  ])
  filename = "${path.root}/ssh_config"
}

# Write Ansible inventory
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/templates/inventory.ini.tpl", {
    web_servers = { for k, v in aws_instance.web : k => v.private_ip }
    db_servers  = { for k, v in aws_instance.db : k => v.private_ip }
  })
  filename = "${path.root}/inventory.ini"
}
```

---

## HTTP Provider (hashicorp/http)

### Provider Configuration
```hcl
terraform {
  required_providers {
    http = {
      source  = "hashicorp/http"
      version = "~> 3.4"
    }
  }
}
```

### Basic HTTP Request
```hcl
# Simple GET request
data "http" "myip" {
  url = "https://api.ipify.org?format=json"
}

output "my_public_ip" {
  value = jsondecode(data.http.myip.response_body).ip
}

# With request headers
data "http" "github_user" {
  url = "https://api.github.com/users/${var.github_username}"

  request_headers = {
    Accept        = "application/vnd.github.v3+json"
    Authorization = "Bearer ${var.github_token}"
  }
}

# With retry
data "http" "external_api" {
  url = var.api_endpoint

  retry {
    attempts     = 3
    min_delay_ms = 1000
    max_delay_ms = 5000
  }
}
```

### Response Validation
```hcl
data "http" "health_check" {
  url = "${var.service_url}/health"

  request_headers = {
    Accept = "application/json"
  }
}

# Check response
locals {
  health_status = jsondecode(data.http.health_check.response_body)
  is_healthy    = data.http.health_check.status_code == 200
}

# Validate expected response
data "http" "validated_response" {
  url = var.api_url

  lifecycle {
    postcondition {
      condition     = self.status_code == 200
      error_message = "API returned non-200 status: ${self.status_code}"
    }

    postcondition {
      condition     = can(jsondecode(self.response_body))
      error_message = "Response is not valid JSON"
    }
  }
}
```

### Common Use Cases
```hcl
# Get AWS IP ranges
data "http" "aws_ip_ranges" {
  url = "https://ip-ranges.amazonaws.com/ip-ranges.json"
}

locals {
  aws_ip_ranges = jsondecode(data.http.aws_ip_ranges.response_body)

  cloudfront_ips = [
    for prefix in local.aws_ip_ranges.prefixes :
    prefix.ip_prefix
    if prefix.service == "CLOUDFRONT"
  ]
}

# Get GitHub meta information
data "http" "github_meta" {
  url = "https://api.github.com/meta"

  request_headers = {
    Accept = "application/vnd.github.v3+json"
  }
}

locals {
  github_actions_ips = jsondecode(data.http.github_meta.response_body).actions
}

# Fetch remote configuration
data "http" "remote_config" {
  url = "https://raw.githubusercontent.com/org/repo/main/config.json"

  request_headers = {
    Authorization = "token ${var.github_token}"
  }
}

locals {
  remote_config = jsondecode(data.http.remote_config.response_body)
}

# Dynamic security group rules from external source
data "http" "allowed_ips" {
  url = var.allowed_ips_url
}

resource "aws_security_group_rule" "dynamic_ingress" {
  for_each = toset(split("\n", trimspace(data.http.allowed_ips.response_body)))

  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = [each.value]
  security_group_id = aws_security_group.main.id
}
```

### POST Request (Data Source Workaround)
```hcl
# HTTP provider only supports GET
# For POST requests, use external provider or null_resource with local-exec

# Using null_resource for POST
resource "null_resource" "api_call" {
  triggers = {
    payload_hash = sha256(jsonencode(var.payload))
  }

  provisioner "local-exec" {
    command = <<-EOT
      curl -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${var.api_token}" \
        -d '${jsonencode(var.payload)}' \
        ${var.api_url} > ${path.module}/response.json
    EOT
  }
}

data "local_file" "api_response" {
  depends_on = [null_resource.api_call]
  filename   = "${path.module}/response.json"
}
```

---

## Best Practices

### Template
1. **Use templatefile() over template provider** - Modern, no provider dependency
2. **Use ~ for whitespace control** - Clean output formatting
3. **Validate template syntax** - Test templates before apply
4. **Use jsonencode() for complex data** - Proper escaping
5. **Keep templates in separate files** - Better maintainability

### Time
1. **Use time_rotating for secrets** - Automatic rotation schedules
2. **Use time_sleep sparingly** - Prefer proper dependencies
3. **Use triggers for controlled recreation** - Predictable behavior
4. **Store timestamps in state** - Consistent reference points
5. **Use RFC3339 format** - Standard, parseable format

### Local
1. **Set restrictive permissions** - 0600 for sensitive files
2. **Use local_sensitive_file for secrets** - Proper handling
3. **Clean up generated files** - Use destroy-time provisioners
4. **Use path.module/path.root** - Portable paths
5. **Don't commit generated files** - Add to .gitignore

### HTTP
1. **Add retry configuration** - Handle transient failures
2. **Validate responses** - Use postconditions
3. **Cache responses if static** - Avoid repeated requests
4. **Use authentication headers** - Secure API access
5. **Handle errors gracefully** - Check status codes
