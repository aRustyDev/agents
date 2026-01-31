# GCP Terraform Module Patterns

## VPC Module

### Resources
- VPC Network
- Subnets (regional)
- Cloud Router
- Cloud NAT
- Firewall rules
- VPC Peering

### Common Variables
```hcl
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "network_name" {
  description = "Name of the VPC network"
  type        = string
}

variable "routing_mode" {
  description = "Network routing mode (GLOBAL or REGIONAL)"
  type        = string
  default     = "GLOBAL"
}

variable "subnets" {
  description = "Subnet configurations"
  type = list(object({
    name          = string
    ip_cidr_range = string
    region        = string
    secondary_ranges = optional(list(object({
      range_name    = string
      ip_cidr_range = string
    })), [])
    private_google_access = optional(bool, true)
    flow_logs = optional(object({
      aggregation_interval = string
      flow_sampling        = number
      metadata             = string
    }))
  }))
}

variable "enable_cloud_nat" {
  description = "Enable Cloud NAT for private instances"
  type        = bool
  default     = true
}
```

### Example
```hcl
resource "google_compute_network" "main" {
  name                    = var.network_name
  project                 = var.project_id
  auto_create_subnetworks = false
  routing_mode            = var.routing_mode
}

resource "google_compute_subnetwork" "this" {
  for_each = { for s in var.subnets : s.name => s }

  name                     = each.value.name
  project                  = var.project_id
  region                   = each.value.region
  network                  = google_compute_network.main.id
  ip_cidr_range            = each.value.ip_cidr_range
  private_ip_google_access = each.value.private_google_access

  dynamic "secondary_ip_range" {
    for_each = each.value.secondary_ranges
    content {
      range_name    = secondary_ip_range.value.range_name
      ip_cidr_range = secondary_ip_range.value.ip_cidr_range
    }
  }

  dynamic "log_config" {
    for_each = each.value.flow_logs != null ? [each.value.flow_logs] : []
    content {
      aggregation_interval = log_config.value.aggregation_interval
      flow_sampling        = log_config.value.flow_sampling
      metadata             = log_config.value.metadata
    }
  }
}

resource "google_compute_router" "main" {
  count   = var.enable_cloud_nat ? 1 : 0
  name    = "${var.network_name}-router"
  project = var.project_id
  region  = var.subnets[0].region
  network = google_compute_network.main.id
}

resource "google_compute_router_nat" "main" {
  count                              = var.enable_cloud_nat ? 1 : 0
  name                               = "${var.network_name}-nat"
  project                            = var.project_id
  router                             = google_compute_router.main[0].name
  region                             = google_compute_router.main[0].region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}
```

---

## GKE Module

### Resources
- GKE cluster (Autopilot or Standard)
- Node pools
- Workload Identity
- Network policies
- Binary Authorization

### Common Variables
```hcl
variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
}

variable "location" {
  description = "Cluster location (region or zone)"
  type        = string
}

variable "min_master_version" {
  description = "Minimum Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "enable_autopilot" {
  description = "Enable Autopilot mode"
  type        = bool
  default     = false
}

variable "node_pools" {
  description = "Node pool configurations (Standard mode only)"
  type = map(object({
    machine_type   = string
    min_node_count = number
    max_node_count = number
    disk_size_gb   = optional(number, 100)
    disk_type      = optional(string, "pd-standard")
    preemptible    = optional(bool, false)
    spot           = optional(bool, false)
    labels         = optional(map(string), {})
    taints = optional(list(object({
      key    = string
      value  = string
      effect = string
    })), [])
  }))
  default = {}
}

variable "master_authorized_networks" {
  description = "Networks authorized to access master"
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = []
}

variable "enable_private_nodes" {
  description = "Enable private nodes"
  type        = bool
  default     = true
}

variable "enable_private_endpoint" {
  description = "Enable private master endpoint"
  type        = bool
  default     = false
}
```

### Security Considerations
- Enable Workload Identity
- Use private clusters
- Enable Binary Authorization
- Enable network policies
- Use Shielded GKE Nodes
- Enable GKE Dataplane V2

---

## Cloud SQL Module

### Resources
- Cloud SQL instance
- Databases
- Users
- SSL certificates
- Replicas

### Common Variables
```hcl
variable "name" {
  description = "Instance name"
  type        = string
}

variable "database_version" {
  description = "Database version (POSTGRES_15, MYSQL_8_0)"
  type        = string
}

variable "region" {
  description = "Instance region"
  type        = string
}

variable "tier" {
  description = "Machine tier"
  type        = string
  default     = "db-custom-2-4096"
}

variable "availability_type" {
  description = "HA type (REGIONAL or ZONAL)"
  type        = string
  default     = "REGIONAL"
}

variable "disk_size" {
  description = "Disk size in GB"
  type        = number
  default     = 20
}

variable "disk_autoresize" {
  description = "Enable disk autoresize"
  type        = bool
  default     = true
}

variable "backup_configuration" {
  description = "Backup configuration"
  type = object({
    enabled                        = bool
    binary_log_enabled             = optional(bool, false)
    start_time                     = optional(string, "03:00")
    point_in_time_recovery_enabled = optional(bool, true)
    transaction_log_retention_days = optional(number, 7)
    retained_backups               = optional(number, 7)
  })
  default = {
    enabled = true
  }
}

variable "require_ssl" {
  description = "Require SSL connections"
  type        = bool
  default     = true
}
```

### Security Considerations
- Use private IP only
- Enable SSL/TLS
- Use Cloud SQL Auth Proxy
- Enable automated backups
- Use IAM database authentication

---

## Cloud Storage Module

### Resources
- Storage bucket
- Lifecycle rules
- IAM bindings
- Versioning
- Encryption

### Common Variables
```hcl
variable "name" {
  description = "Bucket name"
  type        = string
}

variable "location" {
  description = "Bucket location"
  type        = string
}

variable "storage_class" {
  description = "Storage class"
  type        = string
  default     = "STANDARD"
}

variable "versioning" {
  description = "Enable versioning"
  type        = bool
  default     = true
}

variable "uniform_bucket_level_access" {
  description = "Enable uniform bucket-level access"
  type        = bool
  default     = true
}

variable "lifecycle_rules" {
  description = "Lifecycle rules"
  type = list(object({
    action = object({
      type          = string
      storage_class = optional(string)
    })
    condition = object({
      age                   = optional(number)
      with_state            = optional(string)
      num_newer_versions    = optional(number)
      matches_storage_class = optional(list(string))
    })
  }))
  default = []
}

variable "encryption_key" {
  description = "Customer-managed encryption key"
  type        = string
  default     = null
}
```

### Security Considerations
- Enable uniform bucket-level access
- Use customer-managed encryption keys (CMEK)
- Enable versioning for critical data
- Use signed URLs for temporary access
- Enable access logs

---

## Cloud Run Module

### Resources
- Cloud Run service
- IAM bindings
- Domain mappings
- Traffic splitting

### Common Variables
```hcl
variable "name" {
  description = "Service name"
  type        = string
}

variable "location" {
  description = "Service location"
  type        = string
}

variable "image" {
  description = "Container image"
  type        = string
}

variable "port" {
  description = "Container port"
  type        = number
  default     = 8080
}

variable "cpu" {
  description = "CPU allocation"
  type        = string
  default     = "1000m"
}

variable "memory" {
  description = "Memory allocation"
  type        = string
  default     = "512Mi"
}

variable "min_instances" {
  description = "Minimum instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum instances"
  type        = number
  default     = 100
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated access"
  type        = bool
  default     = false
}

variable "vpc_connector" {
  description = "VPC connector for private networking"
  type        = string
  default     = null
}
```

---

## Best Practices

1. **Use Google provider version ~> 5.0** - Latest features
2. **Use Workload Identity** - Avoid service account keys
3. **Enable VPC Service Controls** - Data exfiltration prevention
4. **Use private networking** - Private Google Access, Private Service Connect
5. **Enable audit logging** - Cloud Audit Logs
6. **Use customer-managed encryption keys** - Cloud KMS
7. **Enable organization policies** - Guardrails
8. **Use hierarchical firewall policies** - Centralized security
9. **Enable Security Command Center** - Threat detection
10. **Follow Google Cloud Architecture Framework**

## Provider Configuration

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}
```
