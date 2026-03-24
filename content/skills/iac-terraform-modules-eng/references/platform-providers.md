# Platform Provider Patterns

## Vercel Provider (vercel/vercel)

### Provider Configuration
```hcl
terraform {
  required_providers {
    vercel = {
      source  = "vercel/vercel"
      version = "~> 1.0"
    }
  }
}

provider "vercel" {
  # API token via VERCEL_API_TOKEN env var
  team = var.vercel_team_id
}
```

### Project Module
```hcl
resource "vercel_project" "this" {
  for_each = var.projects

  name      = each.key
  framework = each.value.framework  # nextjs, nuxtjs, gatsby, etc.
  team_id   = var.team_id

  git_repository {
    type              = each.value.git_type  # github, gitlab, bitbucket
    repo              = each.value.git_repo
    production_branch = each.value.production_branch
  }

  root_directory           = each.value.root_directory
  build_command            = each.value.build_command
  output_directory         = each.value.output_directory
  install_command          = each.value.install_command
  dev_command              = each.value.dev_command
  ignore_command           = each.value.ignore_command
  serverless_function_region = each.value.serverless_region

  public_source            = each.value.public_source
  automatically_expose_system_environment_variables = each.value.expose_system_vars

  vercel_authentication {
    deployment_type = each.value.auth_type  # standard_protection, none
  }
}

resource "vercel_project_environment_variable" "this" {
  for_each = var.project_env_vars

  project_id = each.value.project_id
  key        = each.value.key
  value      = each.value.value
  target     = each.value.target  # production, preview, development
  sensitive  = each.value.sensitive
  git_branch = each.value.git_branch
}
```

### Deployment Module
```hcl
resource "vercel_deployment" "this" {
  for_each = var.deployments

  project_id  = each.value.project_id
  production  = each.value.production
  ref         = each.value.ref
  path_prefix = each.value.path_prefix

  files = each.value.files

  environment = each.value.environment

  project_settings {
    build_command    = each.value.build_command
    output_directory = each.value.output_directory
    framework        = each.value.framework
  }
}
```

### Domain Module
```hcl
resource "vercel_project_domain" "this" {
  for_each = var.project_domains

  project_id = each.value.project_id
  domain     = each.key

  redirect             = each.value.redirect
  redirect_status_code = each.value.redirect_status_code
  git_branch           = each.value.git_branch
}

resource "vercel_dns_record" "this" {
  for_each = var.dns_records

  domain  = each.value.domain
  name    = each.value.name
  type    = each.value.type  # A, AAAA, CNAME, TXT, MX, etc.
  value   = each.value.value
  ttl     = each.value.ttl
  mx_priority = each.value.mx_priority
}
```

### Edge Config
```hcl
resource "vercel_edge_config" "this" {
  for_each = var.edge_configs

  name = each.key
}

resource "vercel_edge_config_item" "this" {
  for_each = var.edge_config_items

  edge_config_id = each.value.edge_config_id
  key            = each.value.key
  value          = each.value.value
}

resource "vercel_edge_config_token" "this" {
  for_each = var.edge_config_tokens

  edge_config_id = each.value.edge_config_id
  label          = each.key
}

resource "vercel_project_environment_variable" "edge_config" {
  for_each = var.edge_config_connections

  project_id = each.value.project_id
  key        = "EDGE_CONFIG"
  value      = vercel_edge_config_token.this[each.value.token_key].connection_string
  target     = ["production", "preview", "development"]
}
```

---

## Heroku Provider (heroku/heroku)

### Provider Configuration
```hcl
terraform {
  required_providers {
    heroku = {
      source  = "heroku/heroku"
      version = "~> 5.0"
    }
  }
}

provider "heroku" {
  # API key via HEROKU_API_KEY env var
  # Email via HEROKU_EMAIL env var
}
```

### App Module
```hcl
resource "heroku_app" "this" {
  for_each = var.apps

  name   = each.key
  region = each.value.region  # us, eu
  stack  = each.value.stack   # heroku-22, heroku-20, container

  space        = each.value.space
  organization = each.value.organization
  acm          = each.value.acm  # Automated Certificate Management
  internal_routing = each.value.internal_routing

  buildpacks = each.value.buildpacks

  sensitive_config_vars = each.value.sensitive_config_vars
  config_vars           = each.value.config_vars
}

resource "heroku_app_config_association" "this" {
  for_each = var.app_configs

  app_id = each.value.app_id

  vars           = each.value.vars
  sensitive_vars = each.value.sensitive_vars
}
```

### Addon Module
```hcl
resource "heroku_addon" "this" {
  for_each = var.addons

  app_id = each.value.app_id
  plan   = each.value.plan  # heroku-postgresql:standard-0, heroku-redis:premium-0

  config = each.value.config
}

resource "heroku_addon_attachment" "this" {
  for_each = var.addon_attachments

  app_id   = each.value.app_id
  addon_id = each.value.addon_id
  name     = each.key
}
```

### Formation (Dyno) Module
```hcl
resource "heroku_formation" "this" {
  for_each = var.formations

  app_id   = each.value.app_id
  type     = each.value.type  # web, worker, etc.
  quantity = each.value.quantity
  size     = each.value.size  # basic, standard-1x, standard-2x, performance-m, etc.
}
```

### Domain & SSL
```hcl
resource "heroku_domain" "this" {
  for_each = var.domains

  app_id   = each.value.app_id
  hostname = each.key

  sni_endpoint_id = each.value.sni_endpoint_id
}

resource "heroku_ssl" "this" {
  for_each = var.ssl_certs

  app_id            = each.value.app_id
  certificate_chain = each.value.certificate_chain
  private_key       = each.value.private_key
}
```

### Pipeline Module
```hcl
resource "heroku_pipeline" "this" {
  for_each = var.pipelines

  name = each.key

  owner {
    id   = each.value.owner_id
    type = each.value.owner_type  # user, team
  }
}

resource "heroku_pipeline_coupling" "this" {
  for_each = var.pipeline_couplings

  app_id   = each.value.app_id
  pipeline = each.value.pipeline_id
  stage    = each.value.stage  # review, development, staging, production
}
```

---

## DigitalOcean Provider (digitalocean/digitalocean)

### Provider Configuration
```hcl
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  # Token via DIGITALOCEAN_TOKEN env var
  # Or Spaces access credentials
  spaces_access_id  = var.spaces_access_id
  spaces_secret_key = var.spaces_secret_key
}
```

### Droplet Module
```hcl
variable "droplets" {
  description = "Droplet configurations"
  type = map(object({
    image              = string
    region             = string
    size               = string
    backups            = optional(bool, false)
    monitoring         = optional(bool, true)
    ipv6               = optional(bool, false)
    vpc_uuid           = optional(string)
    ssh_keys           = optional(list(string), [])
    resize_disk        = optional(bool, true)
    tags               = optional(list(string), [])
    user_data          = optional(string)
    droplet_agent      = optional(bool, true)
    graceful_shutdown  = optional(bool, false)
  }))
}

resource "digitalocean_droplet" "this" {
  for_each = var.droplets

  name               = each.key
  image              = each.value.image
  region             = each.value.region
  size               = each.value.size
  backups            = each.value.backups
  monitoring         = each.value.monitoring
  ipv6               = each.value.ipv6
  vpc_uuid           = each.value.vpc_uuid
  ssh_keys           = each.value.ssh_keys
  resize_disk        = each.value.resize_disk
  tags               = each.value.tags
  user_data          = each.value.user_data
  droplet_agent      = each.value.droplet_agent
  graceful_shutdown  = each.value.graceful_shutdown
}

resource "digitalocean_reserved_ip" "this" {
  for_each = { for k, v in var.droplets : k => v if v.reserved_ip }

  region     = each.value.region
  droplet_id = digitalocean_droplet.this[each.key].id
}
```

### Kubernetes Module
```hcl
resource "digitalocean_kubernetes_cluster" "this" {
  for_each = var.kubernetes_clusters

  name         = each.key
  region       = each.value.region
  version      = each.value.version  # 1.29.x, 1.28.x
  vpc_uuid     = each.value.vpc_uuid
  auto_upgrade = each.value.auto_upgrade
  surge_upgrade = each.value.surge_upgrade
  ha           = each.value.ha

  maintenance_policy {
    start_time = each.value.maintenance_start
    day        = each.value.maintenance_day
  }

  dynamic "node_pool" {
    for_each = each.value.node_pools
    content {
      name       = node_pool.value.name
      size       = node_pool.value.size
      node_count = node_pool.value.node_count
      auto_scale = node_pool.value.auto_scale
      min_nodes  = node_pool.value.min_nodes
      max_nodes  = node_pool.value.max_nodes
      tags       = node_pool.value.tags
      labels     = node_pool.value.labels

      dynamic "taint" {
        for_each = node_pool.value.taints
        content {
          key    = taint.value.key
          value  = taint.value.value
          effect = taint.value.effect
        }
      }
    }
  }

  tags = each.value.tags
}
```

### Database Module
```hcl
resource "digitalocean_database_cluster" "this" {
  for_each = var.database_clusters

  name       = each.key
  engine     = each.value.engine  # pg, mysql, redis, mongodb
  version    = each.value.version
  size       = each.value.size
  region     = each.value.region
  node_count = each.value.node_count

  private_network_uuid = each.value.private_network_uuid

  maintenance_window {
    day  = each.value.maintenance_day
    hour = each.value.maintenance_hour
  }

  tags = each.value.tags
}

resource "digitalocean_database_db" "this" {
  for_each = var.databases

  cluster_id = each.value.cluster_id
  name       = each.key
}

resource "digitalocean_database_user" "this" {
  for_each = var.database_users

  cluster_id = each.value.cluster_id
  name       = each.key
  mysql_auth_plugin = each.value.mysql_auth_plugin
}

resource "digitalocean_database_firewall" "this" {
  for_each = var.database_firewalls

  cluster_id = each.value.cluster_id

  dynamic "rule" {
    for_each = each.value.rules
    content {
      type  = rule.value.type  # droplet, k8s, ip_addr, tag, app
      value = rule.value.value
    }
  }
}
```

### Spaces (Object Storage) Module
```hcl
resource "digitalocean_spaces_bucket" "this" {
  for_each = var.spaces_buckets

  name   = each.key
  region = each.value.region
  acl    = each.value.acl  # private, public-read

  cors_rule {
    allowed_headers = each.value.cors_headers
    allowed_methods = each.value.cors_methods
    allowed_origins = each.value.cors_origins
    max_age_seconds = each.value.cors_max_age
  }

  lifecycle_rule {
    id                                     = "cleanup"
    enabled                                = each.value.lifecycle_enabled
    abort_incomplete_multipart_upload_days = each.value.abort_incomplete_days
    expiration {
      days = each.value.expiration_days
    }
  }

  versioning {
    enabled = each.value.versioning
  }

  force_destroy = each.value.force_destroy
}

resource "digitalocean_spaces_bucket_policy" "this" {
  for_each = var.spaces_bucket_policies

  bucket = each.value.bucket
  region = each.value.region
  policy = each.value.policy
}

resource "digitalocean_cdn" "this" {
  for_each = var.cdn_endpoints

  origin         = each.value.origin
  ttl            = each.value.ttl
  certificate_id = each.value.certificate_id
  custom_domain  = each.value.custom_domain
}
```

### App Platform
```hcl
resource "digitalocean_app" "this" {
  for_each = var.apps

  spec {
    name   = each.key
    region = each.value.region

    dynamic "service" {
      for_each = each.value.services
      content {
        name               = service.value.name
        instance_count     = service.value.instance_count
        instance_size_slug = service.value.instance_size
        http_port          = service.value.http_port

        git {
          repo_clone_url = service.value.repo_url
          branch         = service.value.branch
        }

        build_command = service.value.build_command
        run_command   = service.value.run_command
        source_dir    = service.value.source_dir

        dynamic "env" {
          for_each = service.value.env_vars
          content {
            key   = env.key
            value = env.value
            scope = "RUN_AND_BUILD_TIME"
            type  = "GENERAL"
          }
        }

        health_check {
          http_path             = service.value.health_path
          initial_delay_seconds = service.value.initial_delay
          period_seconds        = service.value.period_seconds
        }

        dynamic "autoscaling" {
          for_each = service.value.autoscaling != null ? [service.value.autoscaling] : []
          content {
            min_instance_count = autoscaling.value.min_instances
            max_instance_count = autoscaling.value.max_instances
            metrics {
              cpu {
                percent = autoscaling.value.cpu_percent
              }
            }
          }
        }
      }
    }

    dynamic "database" {
      for_each = each.value.databases
      content {
        name         = database.value.name
        engine       = database.value.engine
        version      = database.value.version
        production   = database.value.production
        cluster_name = database.value.cluster_name
        db_name      = database.value.db_name
        db_user      = database.value.db_user
      }
    }

    dynamic "domain" {
      for_each = each.value.domains
      content {
        name = domain.value.name
        type = domain.value.type  # DEFAULT, PRIMARY, ALIAS
        zone = domain.value.zone
      }
    }
  }
}
```

---

## Linode Provider (linode/linode)

### Provider Configuration
```hcl
terraform {
  required_providers {
    linode = {
      source  = "linode/linode"
      version = "~> 2.0"
    }
  }
}

provider "linode" {
  # Token via LINODE_TOKEN env var
}
```

### Instance Module
```hcl
resource "linode_instance" "this" {
  for_each = var.instances

  label           = each.key
  image           = each.value.image
  region          = each.value.region
  type            = each.value.type
  authorized_keys = each.value.authorized_keys
  root_pass       = each.value.root_pass
  tags            = each.value.tags
  private_ip      = each.value.private_ip
  watchdog_enabled = each.value.watchdog_enabled
  backups_enabled  = each.value.backups_enabled
  booted          = each.value.booted
  resize_disk     = each.value.resize_disk
  swap_size       = each.value.swap_size
  group           = each.value.group

  stackscript_id   = each.value.stackscript_id
  stackscript_data = each.value.stackscript_data
}
```

### LKE (Kubernetes) Module
```hcl
resource "linode_lke_cluster" "this" {
  for_each = var.lke_clusters

  label       = each.key
  k8s_version = each.value.k8s_version
  region      = each.value.region
  tags        = each.value.tags

  control_plane {
    high_availability = each.value.ha
  }

  dynamic "pool" {
    for_each = each.value.pools
    content {
      type  = pool.value.type
      count = pool.value.count

      dynamic "autoscaler" {
        for_each = pool.value.autoscaler != null ? [pool.value.autoscaler] : []
        content {
          min = autoscaler.value.min
          max = autoscaler.value.max
        }
      }
    }
  }
}
```

### Object Storage Module
```hcl
resource "linode_object_storage_key" "this" {
  for_each = var.object_storage_keys

  label = each.key

  dynamic "bucket_access" {
    for_each = each.value.bucket_access
    content {
      bucket_name = bucket_access.value.bucket_name
      cluster     = bucket_access.value.cluster
      permissions = bucket_access.value.permissions  # read_only, read_write
    }
  }
}

resource "linode_object_storage_bucket" "this" {
  for_each = var.object_storage_buckets

  cluster = each.value.cluster
  label   = each.key
  acl     = each.value.acl  # private, public-read, etc.

  dynamic "lifecycle_rule" {
    for_each = each.value.lifecycle_rules
    content {
      id      = lifecycle_rule.value.id
      enabled = lifecycle_rule.value.enabled
      prefix  = lifecycle_rule.value.prefix

      expiration {
        days = lifecycle_rule.value.expiration_days
      }
    }
  }

  versioning = each.value.versioning
}
```

---

## Vultr Provider (vultr/vultr)

### Provider Configuration
```hcl
terraform {
  required_providers {
    vultr = {
      source  = "vultr/vultr"
      version = "~> 2.0"
    }
  }
}

provider "vultr" {
  # API key via VULTR_API_KEY env var
}
```

### Instance Module
```hcl
resource "vultr_instance" "this" {
  for_each = var.instances

  label       = each.key
  plan        = each.value.plan
  region      = each.value.region
  os_id       = each.value.os_id
  app_id      = each.value.app_id
  iso_id      = each.value.iso_id
  snapshot_id = each.value.snapshot_id

  enable_ipv6           = each.value.enable_ipv6
  enable_vpc            = each.value.enable_vpc
  vpc_ids               = each.value.vpc_ids
  ddos_protection       = each.value.ddos_protection
  activation_email      = each.value.activation_email
  hostname              = each.value.hostname
  firewall_group_id     = each.value.firewall_group_id
  backups               = each.value.backups ? "enabled" : "disabled"
  reserved_ip_id        = each.value.reserved_ip_id

  ssh_key_ids = each.value.ssh_key_ids
  user_data   = each.value.user_data
  tags        = each.value.tags

  script_id = each.value.script_id
}
```

### Kubernetes Module
```hcl
resource "vultr_kubernetes" "this" {
  for_each = var.kubernetes_clusters

  label   = each.key
  region  = each.value.region
  version = each.value.version
  ha_controlplanes = each.value.ha
  enable_firewall  = each.value.enable_firewall

  dynamic "node_pools" {
    for_each = each.value.node_pools
    content {
      node_quantity = node_pools.value.node_quantity
      plan          = node_pools.value.plan
      label         = node_pools.value.label
      auto_scaler   = node_pools.value.auto_scaler
      min_nodes     = node_pools.value.min_nodes
      max_nodes     = node_pools.value.max_nodes
    }
  }
}

resource "vultr_kubernetes_node_pools" "this" {
  for_each = var.additional_node_pools

  cluster_id    = each.value.cluster_id
  node_quantity = each.value.node_quantity
  plan          = each.value.plan
  label         = each.key
  auto_scaler   = each.value.auto_scaler
  min_nodes     = each.value.min_nodes
  max_nodes     = each.value.max_nodes
}
```

### Database Module
```hcl
resource "vultr_database" "this" {
  for_each = var.databases

  label                   = each.key
  database_engine         = each.value.engine
  database_engine_version = each.value.version
  region                  = each.value.region
  plan                    = each.value.plan
  cluster_time_zone       = each.value.timezone

  maintenance_dow  = each.value.maintenance_dow
  maintenance_time = each.value.maintenance_time

  mysql_sql_modes                 = each.value.mysql_sql_modes
  mysql_require_primary_key       = each.value.mysql_require_primary_key
  mysql_slow_query_log            = each.value.mysql_slow_query_log
  mysql_long_query_time           = each.value.mysql_long_query_time

  redis_eviction_policy = each.value.redis_eviction_policy

  trusted_ips       = each.value.trusted_ips
  vpc_id            = each.value.vpc_id
  public_host       = each.value.public_host

  read_replicas = each.value.read_replicas
}

resource "vultr_database_user" "this" {
  for_each = var.database_users

  database_id = each.value.database_id
  username    = each.key
  password    = each.value.password
}

resource "vultr_database_db" "this" {
  for_each = var.database_dbs

  database_id = each.value.database_id
  name        = each.key
}
```

### Object Storage Module
```hcl
resource "vultr_object_storage" "this" {
  for_each = var.object_storage

  cluster_id = each.value.cluster_id
  label      = each.key
}
```

---

## Best Practices

### Vercel
1. **Use Edge Config** - Fast global key-value store
2. **Configure environment properly** - Production, preview, development
3. **Use monorepo support** - root_directory configuration
4. **Enable build cache** - Faster deployments
5. **Configure domain verification** - DNS records

### Heroku
1. **Use review apps** - Pipeline-based testing
2. **Configure formation** - Appropriate dyno sizes
3. **Use addons** - Managed services
4. **Enable ACM** - Automated certificates
5. **Use private spaces** - Enterprise isolation

### DigitalOcean
1. **Use VPC** - Private networking
2. **Enable monitoring** - Built-in metrics
3. **Use managed databases** - Automatic backups
4. **Configure firewalls** - Cloud firewalls
5. **Use App Platform** - PaaS simplicity

### Linode
1. **Use StackScripts** - Automated provisioning
2. **Enable backups** - Automatic backup service
3. **Use LKE** - Managed Kubernetes
4. **Configure VLANs** - Private networking
5. **Use NodeBalancers** - Load balancing

### Vultr
1. **Use VPC** - Private networking
2. **Enable DDoS protection** - Built-in protection
3. **Use managed databases** - Automatic failover
4. **Configure firewall groups** - Security rules
5. **Use block storage** - Scalable volumes
