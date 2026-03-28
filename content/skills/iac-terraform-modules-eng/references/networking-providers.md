# Networking Provider Patterns

## Cloudflare Provider (cloudflare/cloudflare)

### Provider Configuration
```hcl
terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

provider "cloudflare" {
  # API token via CLOUDFLARE_API_TOKEN env var
}
```

### Zone Module
```hcl
variable "zones" {
  description = "Cloudflare zone configurations"
  type = map(object({
    account_id = string
    plan       = optional(string, "free")  # free, pro, business, enterprise
    type       = optional(string, "full")  # full, partial
    jump_start = optional(bool, false)
  }))
}

resource "cloudflare_zone" "this" {
  for_each = var.zones

  zone       = each.key
  account_id = each.value.account_id
  plan       = each.value.plan
  type       = each.value.type
  jump_start = each.value.jump_start
}
```

### DNS Records Module
```hcl
variable "dns_records" {
  description = "DNS record configurations"
  type = map(object({
    zone_id  = string
    name     = string
    type     = string  # A, AAAA, CNAME, TXT, MX, etc.
    value    = optional(string)
    data     = optional(map(string))  # For complex records
    priority = optional(number)
    ttl      = optional(number, 1)  # 1 = auto
    proxied  = optional(bool, false)
  }))
}

resource "cloudflare_record" "this" {
  for_each = var.dns_records

  zone_id  = each.value.zone_id
  name     = each.value.name
  type     = each.value.type
  value    = each.value.value
  priority = each.value.priority
  ttl      = each.value.ttl
  proxied  = each.value.proxied

  dynamic "data" {
    for_each = each.value.data != null ? [each.value.data] : []
    content {
      # SRV, CAA, etc. specific fields
    }
  }
}
```

### Workers Module
```hcl
resource "cloudflare_worker_script" "this" {
  for_each = var.worker_scripts

  account_id = each.value.account_id
  name       = each.key
  content    = each.value.content
  module     = each.value.module  # ES module format

  dynamic "plain_text_binding" {
    for_each = each.value.plain_text_bindings
    content {
      name = plain_text_binding.key
      text = plain_text_binding.value
    }
  }

  dynamic "secret_text_binding" {
    for_each = each.value.secret_text_bindings
    content {
      name = secret_text_binding.key
      text = secret_text_binding.value
    }
  }

  dynamic "kv_namespace_binding" {
    for_each = each.value.kv_namespace_bindings
    content {
      name         = kv_namespace_binding.key
      namespace_id = kv_namespace_binding.value
    }
  }

  dynamic "r2_bucket_binding" {
    for_each = each.value.r2_bucket_bindings
    content {
      name        = r2_bucket_binding.key
      bucket_name = r2_bucket_binding.value
    }
  }
}

resource "cloudflare_worker_route" "this" {
  for_each = var.worker_routes

  zone_id     = each.value.zone_id
  pattern     = each.value.pattern
  script_name = each.value.script_name
}
```

### Pages Project
```hcl
resource "cloudflare_pages_project" "this" {
  for_each = var.pages_projects

  account_id        = each.value.account_id
  name              = each.key
  production_branch = each.value.production_branch

  source {
    type = "github"
    config {
      owner                         = each.value.github_owner
      repo_name                     = each.value.github_repo
      production_branch             = each.value.production_branch
      pr_comments_enabled           = each.value.pr_comments_enabled
      deployments_enabled           = each.value.deployments_enabled
      production_deployment_enabled = each.value.production_deployment_enabled
    }
  }

  build_config {
    build_command   = each.value.build_command
    destination_dir = each.value.destination_dir
    root_dir        = each.value.root_dir
  }

  deployment_configs {
    production {
      environment_variables = each.value.production_env_vars
    }
    preview {
      environment_variables = each.value.preview_env_vars
    }
  }
}
```

### Tunnel (Cloudflare Argo)
```hcl
resource "cloudflare_tunnel" "this" {
  for_each = var.tunnels

  account_id = each.value.account_id
  name       = each.key
  secret     = each.value.secret
}

resource "cloudflare_tunnel_config" "this" {
  for_each = var.tunnels

  account_id = each.value.account_id
  tunnel_id  = cloudflare_tunnel.this[each.key].id

  config {
    dynamic "ingress_rule" {
      for_each = each.value.ingress_rules
      content {
        hostname = ingress_rule.value.hostname
        path     = ingress_rule.value.path
        service  = ingress_rule.value.service
      }
    }

    # Catch-all rule (required)
    ingress_rule {
      service = "http_status:404"
    }
  }
}
```

---

## DNS Provider (hashicorp/dns)

### Provider Configuration
```hcl
terraform {
  required_providers {
    dns = {
      source  = "hashicorp/dns"
      version = "~> 3.0"
    }
  }
}

# For RFC 2136 dynamic updates
provider "dns" {
  update {
    server        = var.dns_server
    key_name      = var.tsig_key_name
    key_algorithm = var.tsig_key_algorithm
    key_secret    = var.tsig_key_secret
  }
}
```

### A Record Set
```hcl
resource "dns_a_record_set" "this" {
  for_each = var.a_records

  zone      = each.value.zone
  name      = each.value.name
  addresses = each.value.addresses
  ttl       = each.value.ttl
}
```

### CNAME Record Set
```hcl
resource "dns_cname_record" "this" {
  for_each = var.cname_records

  zone  = each.value.zone
  name  = each.value.name
  cname = each.value.cname
  ttl   = each.value.ttl
}
```

### PTR Record Set
```hcl
resource "dns_ptr_record" "this" {
  for_each = var.ptr_records

  zone = each.value.zone
  name = each.value.name
  ptr  = each.value.ptr
  ttl  = each.value.ttl
}
```

---

## NS1 Provider (ns1-terraform/ns1)

### Provider Configuration
```hcl
terraform {
  required_providers {
    ns1 = {
      source  = "ns1-terraform/ns1"
      version = "~> 2.0"
    }
  }
}

provider "ns1" {
  # API key via NS1_APIKEY env var
}
```

### Zone Module
```hcl
resource "ns1_zone" "this" {
  for_each = var.zones

  zone    = each.key
  ttl     = each.value.ttl
  refresh = each.value.refresh
  retry   = each.value.retry
  expiry  = each.value.expiry
  nx_ttl  = each.value.nx_ttl

  primary   = each.value.primary
  dnssec    = each.value.dnssec
  link      = each.value.link
  networks  = each.value.networks
}
```

### Record Module
```hcl
resource "ns1_record" "this" {
  for_each = var.records

  zone   = each.value.zone
  domain = each.value.domain
  type   = each.value.type
  ttl    = each.value.ttl

  dynamic "answers" {
    for_each = each.value.answers
    content {
      answer = answers.value.answer
      region = answers.value.region
      meta   = answers.value.meta
    }
  }

  dynamic "filters" {
    for_each = each.value.filters
    content {
      filter = filters.value.filter
      config = filters.value.config
    }
  }
}
```

### Monitoring Job
```hcl
resource "ns1_monitoringjob" "this" {
  for_each = var.monitoring_jobs

  name          = each.key
  active        = each.value.active
  regions       = each.value.regions
  job_type      = each.value.job_type  # tcp, http, ping, dns
  frequency     = each.value.frequency
  rapid_recheck = each.value.rapid_recheck

  config = each.value.config  # Job-type specific config

  rules {
    value      = each.value.rules.value
    comparison = each.value.rules.comparison
    key        = each.value.rules.key
  }

  notify_delay     = each.value.notify_delay
  notify_repeat    = each.value.notify_repeat
  notify_failback  = each.value.notify_failback
  notify_regional  = each.value.notify_regional
  notify_list      = each.value.notify_list
}
```

---

## ZeroTier Provider (zerotier/zerotier)

### Provider Configuration
```hcl
terraform {
  required_providers {
    zerotier = {
      source  = "zerotier/zerotier"
      version = "~> 1.0"
    }
  }
}

provider "zerotier" {
  # API token via ZEROTIER_CENTRAL_TOKEN env var
}
```

### Network Module
```hcl
resource "zerotier_network" "this" {
  for_each = var.networks

  name        = each.key
  description = each.value.description
  private     = each.value.private

  route {
    target = each.value.route_target
    via    = each.value.route_via
  }

  assignment_pool {
    start = each.value.ip_pool_start
    end   = each.value.ip_pool_end
  }

  flow_rules = each.value.flow_rules
}
```

### Member Module
```hcl
resource "zerotier_member" "this" {
  for_each = var.members

  network_id  = each.value.network_id
  member_id   = each.value.member_id
  name        = each.key
  description = each.value.description
  hidden      = each.value.hidden

  authorized              = each.value.authorized
  allow_ethernet_bridging = each.value.allow_ethernet_bridging
  no_auto_assign_ips      = each.value.no_auto_assign_ips
  ip_assignments          = each.value.ip_assignments
  capabilities            = each.value.capabilities
  tags                    = each.value.tags
}
```

---

## Fastly Provider (fastly/fastly)

### Provider Configuration
```hcl
terraform {
  required_providers {
    fastly = {
      source  = "fastly/fastly"
      version = "~> 5.0"
    }
  }
}

provider "fastly" {
  # API key via FASTLY_API_KEY env var
}
```

### Service VCL Module
```hcl
resource "fastly_service_vcl" "this" {
  for_each = var.services

  name = each.key

  dynamic "domain" {
    for_each = each.value.domains
    content {
      name    = domain.value.name
      comment = domain.value.comment
    }
  }

  dynamic "backend" {
    for_each = each.value.backends
    content {
      address           = backend.value.address
      name              = backend.value.name
      port              = backend.value.port
      ssl_cert_hostname = backend.value.ssl_cert_hostname
      ssl_sni_hostname  = backend.value.ssl_sni_hostname
      use_ssl           = backend.value.use_ssl
      override_host     = backend.value.override_host

      # Health check
      healthcheck = backend.value.healthcheck
    }
  }

  dynamic "healthcheck" {
    for_each = each.value.healthchecks
    content {
      name              = healthcheck.value.name
      host              = healthcheck.value.host
      path              = healthcheck.value.path
      check_interval    = healthcheck.value.check_interval
      expected_response = healthcheck.value.expected_response
      initial           = healthcheck.value.initial
      threshold         = healthcheck.value.threshold
      timeout           = healthcheck.value.timeout
      window            = healthcheck.value.window
    }
  }

  dynamic "gzip" {
    for_each = each.value.gzip_enabled ? [1] : []
    content {
      name       = "gzip"
      extensions = ["css", "js", "html", "json", "svg"]
    }
  }

  dynamic "request_setting" {
    for_each = each.value.request_settings
    content {
      name      = request_setting.value.name
      force_ssl = request_setting.value.force_ssl
    }
  }

  dynamic "vcl" {
    for_each = each.value.custom_vcl
    content {
      name    = vcl.value.name
      content = vcl.value.content
      main    = vcl.value.main
    }
  }

  force_destroy = each.value.force_destroy
}
```

### TLS Certificate
```hcl
resource "fastly_tls_certificate" "this" {
  for_each = var.tls_certificates

  name                 = each.key
  certificate_body     = each.value.certificate_body
  intermediates_blob   = each.value.intermediates_blob
}

resource "fastly_tls_activation" "this" {
  for_each = var.tls_activations

  certificate_id       = each.value.certificate_id
  configuration_id     = each.value.configuration_id
  domain               = each.value.domain
  mutual_authentication_id = each.value.mtls_id
}
```

---

## Akamai Provider (akamai/akamai)

### Provider Configuration
```hcl
terraform {
  required_providers {
    akamai = {
      source  = "akamai/akamai"
      version = "~> 6.0"
    }
  }
}

provider "akamai" {
  edgerc         = "~/.edgerc"
  config_section = var.akamai_section
}
```

### Property Module
```hcl
data "akamai_group" "this" {
  group_name  = var.group_name
  contract_id = var.contract_id
}

data "akamai_contract" "this" {
  group_name = data.akamai_group.this.group_name
}

resource "akamai_cp_code" "this" {
  for_each = var.cp_codes

  product_id  = each.value.product_id
  contract_id = data.akamai_contract.this.id
  group_id    = data.akamai_group.this.id
  name        = each.key
}

resource "akamai_edge_hostname" "this" {
  for_each = var.edge_hostnames

  product_id    = each.value.product_id
  contract_id   = data.akamai_contract.this.id
  group_id      = data.akamai_group.this.id
  ip_behavior   = each.value.ip_behavior  # IPV4, IPV6_COMPLIANCE, IPV6_PERFORMANCE
  edge_hostname = each.key
  certificate   = each.value.certificate
}

resource "akamai_property" "this" {
  for_each = var.properties

  name        = each.key
  product_id  = each.value.product_id
  contract_id = data.akamai_contract.this.id
  group_id    = data.akamai_group.this.id

  dynamic "hostnames" {
    for_each = each.value.hostnames
    content {
      cname_from             = hostnames.value.cname_from
      cname_to               = hostnames.value.cname_to
      cert_provisioning_type = hostnames.value.cert_provisioning_type
    }
  }

  rule_format = each.value.rule_format
  rules       = each.value.rules  # JSON rules tree
}

resource "akamai_property_activation" "this" {
  for_each = var.property_activations

  property_id                    = each.value.property_id
  contact                        = each.value.contacts
  version                        = each.value.version
  network                        = each.value.network  # STAGING, PRODUCTION
  note                           = each.value.note
  auto_acknowledge_rule_warnings = each.value.auto_acknowledge
}
```

### DNS Zone
```hcl
resource "akamai_dns_zone" "this" {
  for_each = var.dns_zones

  contract      = data.akamai_contract.this.id
  group         = data.akamai_group.this.id
  zone          = each.key
  type          = each.value.type  # PRIMARY, SECONDARY, ALIAS
  masters       = each.value.masters
  comment       = each.value.comment
  sign_and_serve = each.value.dnssec_enabled
}

resource "akamai_dns_record" "this" {
  for_each = var.dns_records

  zone       = each.value.zone
  name       = each.value.name
  recordtype = each.value.recordtype
  ttl        = each.value.ttl
  target     = each.value.target
  priority   = each.value.priority
  weight     = each.value.weight
  port       = each.value.port
}
```

### Application Security
```hcl
resource "akamai_appsec_configuration" "this" {
  for_each = var.appsec_configs

  name        = each.key
  description = each.value.description
  contract_id = data.akamai_contract.this.id
  group_id    = data.akamai_group.this.id
  host_names  = each.value.host_names
}

resource "akamai_appsec_security_policy" "this" {
  for_each = var.security_policies

  config_id              = each.value.config_id
  security_policy_name   = each.key
  security_policy_prefix = each.value.prefix
}
```

---

## Best Practices

1. **Use API tokens over global API keys** - Least privilege access
2. **Enable DNSSEC where supported** - DNS integrity
3. **Use origin certificates** - Secure backend connections
4. **Enable WAF rules** - Application protection
5. **Configure rate limiting** - DDoS mitigation
6. **Use cache keys wisely** - Optimal cache hit rates
7. **Enable logging** - Request/response visibility
8. **Test in staging** - Validate before production
9. **Use version control for rules** - Track configuration changes
10. **Monitor edge performance** - Real User Metrics (RUM)
