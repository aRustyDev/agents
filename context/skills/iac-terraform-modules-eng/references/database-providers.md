# Database Provider Patterns

## MongoDB Atlas (mongodb/mongodbatlas)

### Provider Configuration
```hcl
terraform {
  required_providers {
    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.14"
    }
  }
}

provider "mongodbatlas" {
  public_key  = var.mongodb_public_key
  private_key = var.mongodb_private_key
}
```

### Cluster Module
```hcl
variable "clusters" {
  description = "MongoDB Atlas cluster configurations"
  type = map(object({
    project_id                   = string
    provider_name                = string  # AWS, GCP, AZURE
    provider_region_name         = string
    provider_instance_size_name  = string
    cluster_type                 = optional(string, "REPLICASET")
    mongo_db_major_version       = optional(string, "7.0")
    disk_size_gb                 = optional(number, 10)
    auto_scaling_disk_gb_enabled = optional(bool, true)
    auto_scaling_compute_enabled = optional(bool, true)
    backup_enabled               = optional(bool, true)
    pit_enabled                  = optional(bool, true)
    termination_protection_enabled = optional(bool, true)
  }))
}

resource "mongodbatlas_cluster" "this" {
  for_each = var.clusters

  project_id                   = each.value.project_id
  name                         = each.key
  provider_name                = each.value.provider_name
  provider_region_name         = each.value.provider_region_name
  provider_instance_size_name  = each.value.provider_instance_size_name
  cluster_type                 = each.value.cluster_type
  mongo_db_major_version       = each.value.mongo_db_major_version
  disk_size_gb                 = each.value.disk_size_gb
  auto_scaling_disk_gb_enabled = each.value.auto_scaling_disk_gb_enabled
  auto_scaling_compute_enabled = each.value.auto_scaling_compute_enabled
  backup_enabled               = each.value.backup_enabled
  pit_enabled                  = each.value.pit_enabled
  termination_protection_enabled = each.value.termination_protection_enabled
}
```

### Database User Module
```hcl
resource "mongodbatlas_database_user" "this" {
  for_each = var.database_users

  project_id         = each.value.project_id
  username           = each.key
  password           = each.value.password
  auth_database_name = "admin"

  dynamic "roles" {
    for_each = each.value.roles
    content {
      role_name       = roles.value.role_name
      database_name   = roles.value.database_name
      collection_name = roles.value.collection_name
    }
  }

  dynamic "scopes" {
    for_each = each.value.scopes
    content {
      name = scopes.value.name
      type = scopes.value.type  # CLUSTER, DATA_LAKE
    }
  }
}
```

---

## CockroachDB (cockroachdb/cockroach)

### Provider Configuration
```hcl
terraform {
  required_providers {
    cockroach = {
      source  = "cockroachdb/cockroach"
      version = "~> 1.0"
    }
  }
}

provider "cockroach" {
  # API key via COCKROACH_API_KEY env var
}
```

### Cluster Module
```hcl
variable "clusters" {
  description = "CockroachDB cluster configurations"
  type = map(object({
    cloud_provider = string  # GCP, AWS, AZURE
    plan           = string  # BASIC, STANDARD, ADVANCED
    regions = list(object({
      name       = string
      node_count = number
    }))
    serverless = optional(object({
      spend_limit   = number
      routing_id    = string
      usage_limits  = optional(object({
        request_unit_limit = number
        storage_mib_limit  = number
      }))
    }))
    dedicated = optional(object({
      machine_type       = string
      storage_gib        = number
      disk_iops          = optional(number)
      memory_gib         = optional(number)
      num_virtual_cpus   = optional(number)
    }))
  }))
}

resource "cockroach_cluster" "this" {
  for_each = var.clusters

  name           = each.key
  cloud_provider = each.value.cloud_provider
  plan           = each.value.plan

  dynamic "regions" {
    for_each = each.value.regions
    content {
      name       = regions.value.name
      node_count = regions.value.node_count
    }
  }

  dynamic "serverless" {
    for_each = each.value.serverless != null ? [each.value.serverless] : []
    content {
      spend_limit  = serverless.value.spend_limit
      routing_id   = serverless.value.routing_id
    }
  }

  dynamic "dedicated" {
    for_each = each.value.dedicated != null ? [each.value.dedicated] : []
    content {
      machine_type     = dedicated.value.machine_type
      storage_gib      = dedicated.value.storage_gib
      disk_iops        = dedicated.value.disk_iops
      memory_gib       = dedicated.value.memory_gib
      num_virtual_cpus = dedicated.value.num_virtual_cpus
    }
  }
}
```

---

## Elastic Stack (elastic/elasticstack)

### Provider Configuration
```hcl
terraform {
  required_providers {
    elasticstack = {
      source  = "elastic/elasticstack"
      version = "~> 0.11"
    }
  }
}

provider "elasticstack" {
  elasticsearch {
    endpoints = var.elasticsearch_endpoints
    username  = var.elasticsearch_username
    password  = var.elasticsearch_password
  }

  kibana {
    endpoints = var.kibana_endpoints
  }
}
```

### Index Lifecycle Policy
```hcl
resource "elasticstack_elasticsearch_index_lifecycle" "this" {
  for_each = var.ilm_policies

  name = each.key

  hot {
    min_age = each.value.hot_min_age
    rollover {
      max_age  = each.value.rollover_max_age
      max_size = each.value.rollover_max_size
    }
    set_priority {
      priority = 100
    }
  }

  warm {
    min_age = each.value.warm_min_age
    set_priority {
      priority = 50
    }
    shrink {
      number_of_shards = 1
    }
    forcemerge {
      max_num_segments = 1
    }
  }

  cold {
    min_age = each.value.cold_min_age
    set_priority {
      priority = 0
    }
  }

  delete {
    min_age = each.value.delete_min_age
    delete {}
  }
}
```

### Index Template
```hcl
resource "elasticstack_elasticsearch_index_template" "this" {
  for_each = var.index_templates

  name           = each.key
  index_patterns = each.value.index_patterns
  priority       = each.value.priority

  template {
    settings = jsonencode({
      number_of_shards   = each.value.number_of_shards
      number_of_replicas = each.value.number_of_replicas
      "index.lifecycle.name" = each.value.ilm_policy
    })

    mappings = jsonencode(each.value.mappings)
  }
}
```

---

## Pinecone (pinecone-io/pinecone)

### Provider Configuration
```hcl
terraform {
  required_providers {
    pinecone = {
      source  = "pinecone-io/pinecone"
      version = "~> 0.7"
    }
  }
}

provider "pinecone" {
  # API key via PINECONE_API_KEY env var
}
```

### Index Module
```hcl
variable "indexes" {
  description = "Pinecone index configurations"
  type = map(object({
    dimension  = number
    metric     = optional(string, "cosine")  # cosine, euclidean, dotproduct
    cloud      = optional(string, "aws")
    region     = optional(string, "us-east-1")
    spec = object({
      serverless = optional(object({}))
      pod = optional(object({
        environment  = string
        pod_type     = string
        pods         = number
        replicas     = optional(number, 1)
        shards       = optional(number, 1)
        metadata_config = optional(object({
          indexed = list(string)
        }))
      }))
    })
  }))
}

resource "pinecone_index" "this" {
  for_each = var.indexes

  name      = each.key
  dimension = each.value.dimension
  metric    = each.value.metric

  spec {
    dynamic "serverless" {
      for_each = each.value.spec.serverless != null ? [1] : []
      content {
        cloud  = each.value.cloud
        region = each.value.region
      }
    }

    dynamic "pod" {
      for_each = each.value.spec.pod != null ? [each.value.spec.pod] : []
      content {
        environment = pod.value.environment
        pod_type    = pod.value.pod_type
        pods        = pod.value.pods
        replicas    = pod.value.replicas
        shards      = pod.value.shards

        dynamic "metadata_config" {
          for_each = pod.value.metadata_config != null ? [pod.value.metadata_config] : []
          content {
            indexed = metadata_config.value.indexed
          }
        }
      }
    }
  }
}
```

---

## Atlas (ariga/atlas)

### Provider Configuration
```hcl
terraform {
  required_providers {
    atlas = {
      source  = "ariga/atlas"
      version = "~> 0.4"
    }
  }
}

provider "atlas" {}
```

### Schema Migration
```hcl
resource "atlas_schema" "this" {
  for_each = var.schemas

  hcl = each.value.hcl
  url = each.value.database_url

  dev_url = each.value.dev_database_url
}

# Example HCL schema
locals {
  user_schema = <<-EOT
    table "users" {
      schema = schema.public
      column "id" {
        null = false
        type = uuid
        default = sql("gen_random_uuid()")
      }
      column "email" {
        null = false
        type = varchar(255)
      }
      column "created_at" {
        null = false
        type = timestamptz
        default = sql("now()")
      }
      primary_key {
        columns = [column.id]
      }
      index "users_email_idx" {
        unique = true
        columns = [column.email]
      }
    }
  EOT
}
```

---

## Airbyte (airbytehq/airbyte)

### Provider Configuration
```hcl
terraform {
  required_providers {
    airbyte = {
      source  = "airbytehq/airbyte"
      version = "~> 0.5"
    }
  }
}

provider "airbyte" {
  server_url = var.airbyte_server_url
  # Bearer token via AIRBYTE_BEARER_TOKEN env var
}
```

### Connection Module
```hcl
resource "airbyte_source_postgres" "source" {
  name          = "production-db"
  workspace_id  = var.workspace_id

  configuration = {
    host     = var.source_host
    port     = var.source_port
    database = var.source_database
    username = var.source_username
    password = var.source_password
    ssl_mode = {
      mode = "require"
    }
    replication_method = {
      method = "CDC"
      publication = "airbyte_publication"
      replication_slot = "airbyte_slot"
    }
  }
}

resource "airbyte_destination_bigquery" "destination" {
  name          = "analytics-warehouse"
  workspace_id  = var.workspace_id

  configuration = {
    project_id  = var.gcp_project_id
    dataset_id  = var.bigquery_dataset
    credentials_json = var.gcp_credentials
    loading_method = {
      method = "GCS Staging"
      gcs_bucket_name = var.staging_bucket
      gcs_bucket_path = "airbyte"
    }
  }
}

resource "airbyte_connection" "this" {
  name           = "postgres-to-bigquery"
  source_id      = airbyte_source_postgres.source.source_id
  destination_id = airbyte_destination_bigquery.destination.destination_id

  schedule = {
    schedule_type = "cron"
    cron_expression = "0 0 * * *"
  }

  namespace_definition = "destination"
  namespace_format     = "raw_${SOURCE_NAMESPACE}"
}
```

---

## Best Practices

1. **Use connection strings from secrets** - Never hardcode credentials
2. **Enable encryption at rest** - All database providers support this
3. **Configure automated backups** - Point-in-time recovery
4. **Use private networking** - VPC peering, Private Link
5. **Implement connection pooling** - PgBouncer, ProxySQL
6. **Monitor performance** - Metrics, slow query logs
7. **Use read replicas** - Offload read traffic
8. **Plan for scaling** - Auto-scaling, sharding
9. **Test migrations** - Use dev/staging environments
10. **Document schema changes** - Version control migrations
