# Security Provider Patterns

## Vault Provider (hashicorp/vault)

### Provider Configuration
```hcl
terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 4.0"
    }
  }
}

# Option 1: Token auth
provider "vault" {
  address = var.vault_address
  token   = var.vault_token
}

# Option 2: AppRole auth
provider "vault" {
  address = var.vault_address

  auth_login {
    path = "auth/approle/login"

    parameters = {
      role_id   = var.vault_role_id
      secret_id = var.vault_secret_id
    }
  }
}

# Option 3: Kubernetes auth
provider "vault" {
  address = var.vault_address

  auth_login {
    path = "auth/kubernetes/login"

    parameters = {
      role = var.vault_role
      jwt  = file("/var/run/secrets/kubernetes.io/serviceaccount/token")
    }
  }
}
```

### Auth Backend Module
```hcl
# AppRole Auth
resource "vault_auth_backend" "approle" {
  type = "approle"
  path = var.approle_path
}

resource "vault_approle_auth_backend_role" "this" {
  for_each = var.approle_roles

  backend               = vault_auth_backend.approle.path
  role_name             = each.key
  token_policies        = each.value.token_policies
  token_ttl             = each.value.token_ttl
  token_max_ttl         = each.value.token_max_ttl
  secret_id_ttl         = each.value.secret_id_ttl
  secret_id_num_uses    = each.value.secret_id_num_uses
  token_num_uses        = each.value.token_num_uses
  bind_secret_id        = each.value.bind_secret_id
  secret_id_bound_cidrs = each.value.secret_id_bound_cidrs
}

# Kubernetes Auth
resource "vault_auth_backend" "kubernetes" {
  type = "kubernetes"
  path = var.kubernetes_path
}

resource "vault_kubernetes_auth_backend_config" "this" {
  backend            = vault_auth_backend.kubernetes.path
  kubernetes_host    = var.kubernetes_host
  kubernetes_ca_cert = var.kubernetes_ca_cert
  token_reviewer_jwt = var.token_reviewer_jwt
}

resource "vault_kubernetes_auth_backend_role" "this" {
  for_each = var.kubernetes_roles

  backend                          = vault_auth_backend.kubernetes.path
  role_name                        = each.key
  bound_service_account_names      = each.value.service_account_names
  bound_service_account_namespaces = each.value.service_account_namespaces
  token_policies                   = each.value.token_policies
  token_ttl                        = each.value.token_ttl
  token_max_ttl                    = each.value.token_max_ttl
  audience                         = each.value.audience
}

# OIDC Auth
resource "vault_jwt_auth_backend" "oidc" {
  count = var.enable_oidc ? 1 : 0

  path               = "oidc"
  type               = "oidc"
  oidc_discovery_url = var.oidc_discovery_url
  oidc_client_id     = var.oidc_client_id
  oidc_client_secret = var.oidc_client_secret
  default_role       = var.oidc_default_role
}

resource "vault_jwt_auth_backend_role" "oidc_roles" {
  for_each = var.oidc_roles

  backend        = vault_jwt_auth_backend.oidc[0].path
  role_name      = each.key
  role_type      = "oidc"
  token_policies = each.value.token_policies

  allowed_redirect_uris = each.value.allowed_redirect_uris
  user_claim            = each.value.user_claim
  groups_claim          = each.value.groups_claim
  bound_claims          = each.value.bound_claims
  claim_mappings        = each.value.claim_mappings
}
```

### Secrets Engine Module
```hcl
# KV v2 Secrets Engine
resource "vault_mount" "kv" {
  for_each = var.kv_mounts

  path        = each.key
  type        = "kv"
  options     = { version = "2" }
  description = each.value.description
}

resource "vault_kv_secret_v2" "this" {
  for_each = var.kv_secrets

  mount               = each.value.mount
  name                = each.value.name
  cas                 = each.value.cas
  delete_all_versions = each.value.delete_all_versions
  data_json           = jsonencode(each.value.data)
}

# Database Secrets Engine
resource "vault_mount" "database" {
  for_each = var.database_mounts

  path = each.key
  type = "database"
}

resource "vault_database_secret_backend_connection" "postgres" {
  for_each = var.postgres_connections

  backend       = each.value.mount
  name          = each.key
  allowed_roles = each.value.allowed_roles

  postgresql {
    connection_url = each.value.connection_url
    max_open_connections = each.value.max_open_connections
    max_idle_connections = each.value.max_idle_connections
    max_connection_lifetime = each.value.max_connection_lifetime
  }
}

resource "vault_database_secret_backend_role" "this" {
  for_each = var.database_roles

  backend             = each.value.backend
  name                = each.key
  db_name             = each.value.db_name
  creation_statements = each.value.creation_statements
  revocation_statements = each.value.revocation_statements
  default_ttl         = each.value.default_ttl
  max_ttl             = each.value.max_ttl
}

# PKI Secrets Engine
resource "vault_mount" "pki" {
  for_each = var.pki_mounts

  path                      = each.key
  type                      = "pki"
  description               = each.value.description
  default_lease_ttl_seconds = each.value.default_lease_ttl
  max_lease_ttl_seconds     = each.value.max_lease_ttl
}

resource "vault_pki_secret_backend_root_cert" "root" {
  for_each = { for k, v in var.pki_mounts : k => v if v.is_root }

  backend              = vault_mount.pki[each.key].path
  type                 = "internal"
  common_name          = each.value.common_name
  ttl                  = each.value.ttl
  format               = "pem"
  private_key_format   = "der"
  key_type             = "rsa"
  key_bits             = 4096
  exclude_cn_from_sans = true
  organization         = each.value.organization
  ou                   = each.value.ou
}

resource "vault_pki_secret_backend_role" "this" {
  for_each = var.pki_roles

  backend          = each.value.backend
  name             = each.key
  ttl              = each.value.ttl
  max_ttl          = each.value.max_ttl
  allow_ip_sans    = each.value.allow_ip_sans
  key_type         = each.value.key_type
  key_bits         = each.value.key_bits
  allowed_domains  = each.value.allowed_domains
  allow_subdomains = each.value.allow_subdomains
  allow_glob_domains = each.value.allow_glob_domains
  allow_any_name   = each.value.allow_any_name
  enforce_hostnames = each.value.enforce_hostnames
  allow_bare_domains = each.value.allow_bare_domains
  server_flag      = each.value.server_flag
  client_flag      = each.value.client_flag
}

# AWS Secrets Engine
resource "vault_aws_secret_backend" "this" {
  for_each = var.aws_backends

  path       = each.key
  access_key = each.value.access_key
  secret_key = each.value.secret_key
  region     = each.value.region

  default_lease_ttl_seconds = each.value.default_lease_ttl
  max_lease_ttl_seconds     = each.value.max_lease_ttl
}

resource "vault_aws_secret_backend_role" "this" {
  for_each = var.aws_roles

  backend         = each.value.backend
  name            = each.key
  credential_type = each.value.credential_type  # iam_user, assumed_role, federation_token

  role_arns       = each.value.role_arns
  policy_arns     = each.value.policy_arns
  policy_document = each.value.policy_document
  default_sts_ttl = each.value.default_sts_ttl
  max_sts_ttl     = each.value.max_sts_ttl
}

# Transit Secrets Engine
resource "vault_mount" "transit" {
  count = var.enable_transit ? 1 : 0

  path        = "transit"
  type        = "transit"
  description = "Transit secrets engine for encryption as a service"
}

resource "vault_transit_secret_backend_key" "this" {
  for_each = var.transit_keys

  backend          = vault_mount.transit[0].path
  name             = each.key
  type             = each.value.type  # aes256-gcm96, chacha20-poly1305, rsa-2048, etc.
  deletion_allowed = each.value.deletion_allowed
  exportable       = each.value.exportable
  allow_plaintext_backup = each.value.allow_plaintext_backup

  min_decryption_version = each.value.min_decryption_version
  min_encryption_version = each.value.min_encryption_version

  auto_rotate_period = each.value.auto_rotate_period
}
```

### Policy Module
```hcl
resource "vault_policy" "this" {
  for_each = var.policies

  name   = each.key
  policy = each.value.policy
}

# Example policy HCL
locals {
  app_policy = <<-EOT
    # Read application secrets
    path "secret/data/app/*" {
      capabilities = ["read", "list"]
    }

    # Issue certificates
    path "pki/issue/app-role" {
      capabilities = ["create", "update"]
    }

    # Get database credentials
    path "database/creds/app-role" {
      capabilities = ["read"]
    }

    # Encrypt/decrypt with transit
    path "transit/encrypt/app-key" {
      capabilities = ["update"]
    }

    path "transit/decrypt/app-key" {
      capabilities = ["update"]
    }
  EOT
}
```

### Namespace Module (Enterprise)
```hcl
resource "vault_namespace" "this" {
  for_each = var.namespaces

  path = each.key
}

# Cross-namespace auth
resource "vault_namespace" "child" {
  for_each = var.child_namespaces

  namespace = each.value.parent
  path      = each.key
}
```

---

## TLS Provider (hashicorp/tls)

### Provider Configuration
```hcl
terraform {
  required_providers {
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}
```

### Private Key Module
```hcl
variable "private_keys" {
  description = "Private key configurations"
  type = map(object({
    algorithm   = string  # RSA, ECDSA, ED25519
    rsa_bits    = optional(number, 4096)
    ecdsa_curve = optional(string, "P384")  # P224, P256, P384, P521
  }))
}

resource "tls_private_key" "this" {
  for_each = var.private_keys

  algorithm   = each.value.algorithm
  rsa_bits    = each.value.algorithm == "RSA" ? each.value.rsa_bits : null
  ecdsa_curve = each.value.algorithm == "ECDSA" ? each.value.ecdsa_curve : null
}

output "private_keys_pem" {
  value     = { for k, v in tls_private_key.this : k => v.private_key_pem }
  sensitive = true
}

output "public_keys_pem" {
  value = { for k, v in tls_private_key.this : k => v.public_key_pem }
}

output "public_keys_openssh" {
  value = { for k, v in tls_private_key.this : k => v.public_key_openssh }
}
```

### Self-Signed Certificate Module
```hcl
variable "self_signed_certs" {
  description = "Self-signed certificate configurations"
  type = map(object({
    private_key_pem = string
    subject = object({
      common_name         = string
      organization        = optional(string)
      organizational_unit = optional(string)
      locality            = optional(string)
      province            = optional(string)
      country             = optional(string)
    })
    validity_period_hours = number
    is_ca_certificate     = optional(bool, false)
    allowed_uses          = list(string)
    dns_names             = optional(list(string), [])
    ip_addresses          = optional(list(string), [])
  }))
}

resource "tls_self_signed_cert" "this" {
  for_each = var.self_signed_certs

  private_key_pem = each.value.private_key_pem

  subject {
    common_name         = each.value.subject.common_name
    organization        = each.value.subject.organization
    organizational_unit = each.value.subject.organizational_unit
    locality            = each.value.subject.locality
    province            = each.value.subject.province
    country             = each.value.subject.country
  }

  validity_period_hours = each.value.validity_period_hours
  is_ca_certificate     = each.value.is_ca_certificate
  allowed_uses          = each.value.allowed_uses
  dns_names             = each.value.dns_names
  ip_addresses          = each.value.ip_addresses
}

# Common allowed_uses values:
# - key_encipherment
# - digital_signature
# - server_auth
# - client_auth
# - cert_signing
# - crl_signing
# - code_signing
# - email_protection
# - ipsec_end_system
# - ipsec_tunnel
# - ipsec_user
# - timestamping
# - ocsp_signing
```

### Certificate Request (CSR) Module
```hcl
resource "tls_cert_request" "this" {
  for_each = var.cert_requests

  private_key_pem = each.value.private_key_pem

  subject {
    common_name         = each.value.subject.common_name
    organization        = each.value.subject.organization
    organizational_unit = each.value.subject.organizational_unit
  }

  dns_names    = each.value.dns_names
  ip_addresses = each.value.ip_addresses
  uris         = each.value.uris
}

output "cert_requests_pem" {
  value = { for k, v in tls_cert_request.this : k => v.cert_request_pem }
}
```

### Locally Signed Certificate Module
```hcl
resource "tls_locally_signed_cert" "this" {
  for_each = var.locally_signed_certs

  cert_request_pem   = each.value.cert_request_pem
  ca_private_key_pem = each.value.ca_private_key_pem
  ca_cert_pem        = each.value.ca_cert_pem

  validity_period_hours = each.value.validity_period_hours
  allowed_uses          = each.value.allowed_uses

  is_ca_certificate = each.value.is_ca_certificate

  set_subject_key_id = true
}
```

### Complete PKI Example
```hcl
# Root CA
resource "tls_private_key" "ca" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "tls_self_signed_cert" "ca" {
  private_key_pem = tls_private_key.ca.private_key_pem

  subject {
    common_name  = "Example Root CA"
    organization = "Example Inc"
  }

  validity_period_hours = 87600  # 10 years
  is_ca_certificate     = true

  allowed_uses = [
    "cert_signing",
    "crl_signing",
    "digital_signature",
    "key_encipherment",
  ]
}

# Server certificate
resource "tls_private_key" "server" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_cert_request" "server" {
  private_key_pem = tls_private_key.server.private_key_pem

  subject {
    common_name  = "server.example.com"
    organization = "Example Inc"
  }

  dns_names = [
    "server.example.com",
    "*.server.example.com",
    "localhost",
  ]

  ip_addresses = ["127.0.0.1"]
}

resource "tls_locally_signed_cert" "server" {
  cert_request_pem   = tls_cert_request.server.cert_request_pem
  ca_private_key_pem = tls_private_key.ca.private_key_pem
  ca_cert_pem        = tls_self_signed_cert.ca.cert_pem

  validity_period_hours = 8760  # 1 year

  allowed_uses = [
    "digital_signature",
    "key_encipherment",
    "server_auth",
  ]
}

# Client certificate
resource "tls_private_key" "client" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_cert_request" "client" {
  private_key_pem = tls_private_key.client.private_key_pem

  subject {
    common_name  = "client@example.com"
    organization = "Example Inc"
  }
}

resource "tls_locally_signed_cert" "client" {
  cert_request_pem   = tls_cert_request.client.cert_request_pem
  ca_private_key_pem = tls_private_key.ca.private_key_pem
  ca_cert_pem        = tls_self_signed_cert.ca.cert_pem

  validity_period_hours = 8760

  allowed_uses = [
    "digital_signature",
    "key_encipherment",
    "client_auth",
  ]
}
```

### SSH Key Module
```hcl
resource "tls_private_key" "ssh" {
  for_each = var.ssh_keys

  algorithm = each.value.algorithm  # RSA, ED25519, ECDSA
  rsa_bits  = each.value.rsa_bits
}

# Store in AWS Secrets Manager
resource "aws_secretsmanager_secret" "ssh_key" {
  for_each = var.ssh_keys

  name = "ssh-key-${each.key}"
}

resource "aws_secretsmanager_secret_version" "ssh_key" {
  for_each = var.ssh_keys

  secret_id = aws_secretsmanager_secret.ssh_key[each.key].id
  secret_string = jsonencode({
    private_key = tls_private_key.ssh[each.key].private_key_openssh
    public_key  = tls_private_key.ssh[each.key].public_key_openssh
  })
}
```

---

## Best Practices

### Vault
1. **Use dynamic secrets** - Short-lived, automatically rotated
2. **Enable audit logging** - All operations logged
3. **Use namespaces** - Tenant isolation (Enterprise)
4. **Implement least privilege policies** - Fine-grained access
5. **Enable response wrapping** - Secure secret delivery
6. **Use auto-unseal** - AWS KMS, Azure Key Vault, GCP KMS
7. **Enable high availability** - Raft or Consul storage
8. **Regular token rotation** - Limit token lifetime
9. **Use AppRole for automation** - Machine-to-machine auth
10. **Enable telemetry** - Monitor Vault health

### TLS
1. **Use RSA-4096 or ECDSA P-384** - Strong key sizes
2. **Short certificate lifetimes** - 90 days max for leaf certs
3. **Store private keys securely** - Vault, AWS Secrets Manager
4. **Use SANs over CN** - Modern certificate practice
5. **Implement certificate rotation** - Automated renewal
6. **Use separate keys per service** - Limit blast radius
7. **Enable OCSP stapling** - Certificate revocation
8. **Use hardware security modules** - HSM for production CAs
9. **Implement certificate pinning** - For critical services
10. **Monitor certificate expiration** - Alerting before expiry
