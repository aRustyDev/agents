---
description: Cryptographic Security Guidelines
languages: []
alwaysApply: true
---

# Cryptographic Security Guidelines

## Banned (Insecure) Algorithms

The following algorithms are known to be broken or fundamentally insecure. **NEVER** generate or use code with these algorithms.
Examples:

- Hash: `MD2`, `MD4`, `MD5`, `SHA-0`
- Symmetric: `RC2`, `RC4`, `Blowfish`, `DES`, `3DES`
- Key Exchange: Static RSA, Anonymous Diffie-Hellman
- Classical: `Vigenère`

## Deprecated (Legacy/Weak) Algorithms

The following algorithms are not outright broken, but have known weaknesses, or are considered obsolete. **NEVER** generate or use code with these algorithms.
Examples:

- Hash: `SHA-1`
- Symmetric: `AES-CBC`, `AES-ECB`
- Signature: RSA with `PKCS#1 v1.5` padding
- Key Exchange: DHE with weak/common primes

## Legacy Crypto Tooling Risks

- Require Terraform, OpenTofu, Terragrunt, Packer, Ansible, and CI/CD runners to ship with OpenSSL 1.1.1+ or Libsodium equivalents that support TLS 1.2/1.3, AEAD (AES-GCM, ChaCha20-Poly1305), and modern curves; deny pipelines that rely on legacy OpenSSL compatibility layers.
- Block use of environment flags or build options (for example, enabling legacy crypto providers) that reintroduce deprecated cipher suites when launching infrastructure tooling or containers.
- Pin container images, Terraform providers, Packer plugins, and orchestration binaries to signed releases that publish SBOMs or attestations proving current cryptographic libraries; fail builds when signatures or checksums are missing or invalid.
- Continuously audit control-plane services and automation hosts to ensure TLS policies, cipher suites, and crypto libraries stay aligned with FIPS-validated or platform security baselines, and rotate tooling images promptly when CVEs impact bundled crypto stacks.

## Banned Insecure Algorithms - STRICTLY FORBIDDEN

These algorithms MUST NOT be used in any form:

### Hash Algorithms (Banned)

- MD2, MD4, MD5, SHA-0
- Reason: Cryptographically broken, vulnerable to collision attacks
- Use Instead: SHA-256, SHA-384, SHA-512

### Symmetric Ciphers (Banned)

- RC2, RC4, Blowfish, DES, 3DES
- Reason: Weak key sizes, known vulnerabilities
- Use Instead: AES-128, AES-256, ChaCha20

### Key Exchange (Banned)

- Static RSA key exchange
- Anonymous Diffie-Hellman
- Reason: No forward secrecy, vulnerable to man-in-the-middle attacks
- Use Instead: ECDHE, DHE with proper validation

## Secure Infrastructure Crypto Patterns

### Terraform / OpenTofu

- Enforce TLS 1.2+ and SSE-KMS on remote state buckets with customer-managed keys and deny insecure transport.

```terraform
# terraform_state.tf
resource "aws_kms_key" "state" {
  description         = "Terraform state CMK"
  enable_key_rotation = true
}

resource "aws_s3_bucket" "state" {
  bucket = "example-tf-state"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.state.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket_policy" "state_tls" {
  bucket = aws_s3_bucket.state.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:*"
      Resource  = [
        "${aws_s3_bucket.state.arn}",
        "${aws_s3_bucket.state.arn}/*"
      ]
      Condition = {
        Bool = {
          "aws:SecureTransport" = "false"
        }
      }
    }]
  })
}
```

### Packer

- Require artifact verification and modern SSH algorithms during provisioning.

```hcl
# secure.pkr.hcl
packer {
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = ">= 1.1.0"
    }
  }
}

source "amazon-ebs" "secure" {
  region            = var.region
  instance_type     = "t3.micro"
  ssh_username      = "ubuntu"
  ssh_timeout       = "5m"
  ssh_agent_auth    = false
  ssh_key_pair_name = var.ssh_key_pair
  ssh_host_key_file = var.ssh_host_key_file
  communicator      = "ssh"
}

build {
  sources = ["source.amazon-ebs.secure"]

  provisioner "shell" {
    inline = [
      "sha256sum -c /tmp/binary.sha256",
      "rm -f /tmp/binary.sha256"
    ]
  }
}
```

### Ansible

- Harden SSH parameters and Vault usage when automating configuration.

```cfg
; ansible.cfg
[all:vars]
ansible_ssh_common_args=-oHostKeyAlgorithms=ssh-ed25519 -oCiphers=chacha20-poly1305@openssh.com,aes256-gcm@openssh.com -oMACs=hmac-sha2-256
ansible_vault_encrypt_identity_list=vault@/etc/ansible/.vault_pass
ansible_become=true
```

## Universal IaC Cryptography Principles

- Enforce TLS 1.2+/1.3 for every control-plane and data-plane endpoint; disable legacy cipher suites, weak DH parameters, and insecure renegotiation.
- Protect state files, build artifacts, and secret payloads with customer-managed encryption keys (KMS/CMK/HSM) and capture key usage through audit logs.
- Prefer authenticated encryption modes (AES-256-GCM, ChaCha20-Poly1305) and SHA-256/384/512 hashing; never rely on CBC/ECB or SHA-1 for new workloads.
- Sign and verify modules, plugins, and artifacts (GPG, Sigstore, KMS signing) and validate SHA-256/512 checksums before execution.
- Minimize secret exposure with dynamic credentials, short-lived tokens, and centralized secret stores that support automatic rotation and revocation.

## Terraform Cryptography Guidance

- Back remote state with KMS-encrypted storage (e.g., AWS S3 + KMS, Azure Blob + Key Vault, GCS + CMEK) and require HTTPS/TLS 1.2+ via bucket or storage policies.
- Set provider/resource `tls_min_version` or equivalent arguments and prefer endpoints exposing modern suites (ECDHE + AES-GCM/ChaCha20).
- Use `provider_installation` blocks or dependency lock files to restrict providers to signed registries over HTTPS; verify signatures with OIDC or GPG where offered.
- Keep sensitive variables encrypted at rest using SOPS/Vault integrations and rotate them using KMS or Vault transit engines aligned with the universal principles.

## HashiCorp Vault Cryptography Guidance

- Enable auto-unseal with HSM/KMS-backed AES-256-GCM master keys and encrypt root/leader keys; never store Shamir key shares in plaintext.
- Force TLS 1.2+ with mTLS on the Vault API (`tls_min_version = "tls12"`) and disable insecure cipher suites, TLS compression, and downgrade negotiation.
- Use the Transit engine for envelope encryption and signing with modern algorithms (AES-256-GCM, Ed25519, ECDSA P-256+) and enforce key rotation policies.
- Harden PKI secrets engines to issue certificates signed with SHA-256/384 and ECDSA or RSA ≥ 3072, rejecting SHA-1 and short RSA keys.
- Prefer dynamic or response-wrapped secrets with short TTLs; audit leases and revoke early if compromise is suspected.

## Terragrunt Cryptography Guidance

- Inherit encrypted remote state backends and KMS keys by centralizing backend configs and referencing them via `include` or `read_terragrunt_config`.
- Use `generate` or `extra_arguments` blocks to inject provider TLS constraints (`tls_min_version`) and enforce signature verification via `terraform providers lock`.
- Store Terragrunt inputs that contain secrets in SOPS/Vault files, decrypting only in memory and shredding temporary files after execution.
- Gate Terragrunt workflows with hooks that verify module checksums and deny execution when signatures or hashes fail validation.

## OpenTofu Cryptography Guidance

- Treat OpenTofu backends and providers identically to Terraform: require KMS-encrypted remote state and TLS 1.2+/1.3 connections.
- Commit `tofu.lock.hcl` and verify provider checksums/signatures; disable fallback to insecure mirrors.
- Use `provider_installation` directives to pin to HTTPS registries with verified certificates and enable Sigstore/GPG verification when supported.
- Integrate with Vault/KMS for secrets and rotate credentials through dynamic providers to avoid long-lived plaintext values.

## Packer Cryptography Guidance

- Sign manifests, AMI IDs, and disk artifacts with GPG, KMS, or Sigstore to preserve supply-chain integrity per the universal principles.
- Force SSH provisioners to use modern host key algorithms (Ed25519, ECDSA) and strong ciphers/MACs (`chacha20-poly1305@openssh.com`, `aes256-gcm@openssh.com`, `hmac-sha2-256`).
- Source secrets from Vault/KMS, expose them only via short-lived environment variables or files, and securely shred them once provisioning completes.
- Verify uploaded files, cloud-init archives, and user data with SHA-256 or stronger checksums before execution; fail builds when verification differs.
- Enable plugin and communicator TLS verification (WinRM, HTTPS) and ensure custom builders trust only modern CA chains.

## Ansible Cryptography Guidance

- Configure Ansible Vault to default to AES-256 (`ansible-vault encrypt --vault-id ...`) and manage vault passwords via secure stores (HashiCorp Vault, KMS, 1Password CLI) per the universal secrets guidance.
- Require SSH parameters (`HostKeyAlgorithms`, `PubkeyAcceptedKeyTypes`, `Ciphers`, `MACs`) that align with hardened/FIPS baselines (Ed25519/ECDSA keys, AES-GCM, ChaCha20-Poly1305, HMAC-SHA2).
- Use `community.crypto` modules for certificate issuance, CSR validation, and TLS inspections to keep automation on TLS 1.2+/1.3 with strong cipher suites.
- When targeting FIPS-enforced systems, confirm the Python interpreter/OpenSSL build is FIPS-capable and avoid modules that fall back to insecure algorithms.
- Leverage lookup plugins to fetch short-lived secrets from Vault/KMS and avoid storing sensitive values in inventories, playbooks, or logs.

## AWS Platform Cryptography Guidance

- Enforce customer-managed AWS KMS keys (SSE-KMS) for S3 buckets, EBS volumes, RDS snapshots, ECR images, Secrets Manager, and Parameter Store; enable automatic key rotation.
- Require TLS 1.2+ using modern security policies on ALB/NLB/CloudFront and bucket policies that enforce `aws:SecureTransport`; disable legacy ELB cipher suites.
- Issue ACM certificates with RSA 2048+/ECDSA P-256+ and rotate certificates proactively; enable OCSP stapling and revoke compromised certificates immediately.
- Monitor encryption posture with CloudTrail, AWS Config, and Security Hub to detect drift in key usage, TLS policies, or secret storage.

## Google Cloud Platform Cryptography Guidance

- Protect GCS buckets, Compute persistent disks, BigQuery datasets, and Pub/Sub topics with Cloud KMS CMEK or Cloud HSM keys and rotate them regularly.
- Apply HTTPS load balancer SSL policies set to `MODERN` or `RESTRICTED` to guarantee TLS 1.2+/1.3; require mTLS where private service access is used.
- Store secrets in Secret Manager with CMEK-backed encryption and automatic rotation; avoid embedding secrets in instance metadata or templates.
- Enable Cloud Audit Logs and Event Threat Detection for KMS and Secret Manager to track key usage and alert on anomalous access.

## Azure Platform Cryptography Guidance

- Store secrets and certificates in Azure Key Vault or Managed HSM with soft-delete, purge protection, and minimum key sizes of RSA 3072 or elliptic curve P-256+.
- Set `minimumTlsVersion` to `TLS1_2` (or `TLS1_3` where supported) for App Service, Storage, SQL Database, and other endpoints; disable legacy cipher suites.
- Use Azure Disk Encryption sets and Storage Account encryption with customer-managed keys; enforce compliance through Azure Policy assignments.
- Capture Key Vault and Managed HSM logs in Azure Monitor/Sentinel to audit key usage and detect unauthorized operations.

## Code Review Checklist

- [ ] Universal IaC cryptography principles are satisfied (TLS 1.2+/1.3, CMKs/HSMs, AEAD, artifact signing, short-lived secrets)
- [ ] Tooling supply chain is locked to signed releases with modern crypto libraries (no legacy compatibility modes)
- [ ] No banned algorithms (MD5, DES, RC4, etc.) appear in infrastructure configurations or automation scripts
- [ ] Secrets remain in managed stores (Vault/KMS/SOPS) with rotation policies and never land in state files, logs, or artifacts
- [ ] Terraform/Terragrunt/OpenTofu configurations enforce encrypted remote state, provider verification, and minimum TLS versions
- [ ] HashiCorp Vault policies enforce modern TLS, AEAD, and dynamic secrets with audited rotation
- [ ] Packer pipelines sign artifacts and restrict provisioner communications to modern ciphers/MACs
- [ ] Ansible Vault, SSH, and crypto modules use AES-256-GCM or ChaCha20-Poly1305 with modern key algorithms
- [ ] Cloud platform controls (AWS/GCP/Azure) enforce CMK-backed encryption and modern TLS security policies
