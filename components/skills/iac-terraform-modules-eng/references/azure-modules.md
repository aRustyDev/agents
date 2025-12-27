# Azure Terraform Module Patterns

## VNet Module

### Resources
- Virtual Network with subnets
- Network Security Groups
- Route Tables
- NAT Gateway
- VNet Peering

### Common Variables
```hcl
variable "name" {
  description = "Name of the VNet"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "address_space" {
  description = "VNet address space"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnets" {
  description = "Subnet configurations"
  type = map(object({
    address_prefixes = list(string)
    service_endpoints = optional(list(string), [])
    delegation = optional(object({
      name    = string
      actions = list(string)
    }))
  }))
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for outbound connectivity"
  type        = bool
  default     = true
}
```

### Example
```hcl
resource "azurerm_virtual_network" "main" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = var.address_space

  tags = var.tags
}

resource "azurerm_subnet" "this" {
  for_each = var.subnets

  name                 = each.key
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = each.value.address_prefixes
  service_endpoints    = each.value.service_endpoints

  dynamic "delegation" {
    for_each = each.value.delegation != null ? [each.value.delegation] : []
    content {
      name = delegation.value.name
      service_delegation {
        name    = delegation.value.name
        actions = delegation.value.actions
      }
    }
  }
}
```

---

## AKS Module

### Resources
- AKS cluster with node pools
- Azure AD integration
- Container Registry integration
- Network policies
- Cluster autoscaler

### Common Variables
```hcl
variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "default_node_pool" {
  description = "Default node pool configuration"
  type = object({
    name                = string
    vm_size             = string
    node_count          = number
    min_count           = optional(number)
    max_count           = optional(number)
    enable_auto_scaling = optional(bool, true)
    os_disk_size_gb     = optional(number, 50)
    zones               = optional(list(string), ["1", "2", "3"])
  })
}

variable "network_profile" {
  description = "Network configuration"
  type = object({
    network_plugin     = string  # azure or kubenet
    network_policy     = optional(string, "calico")
    service_cidr       = string
    dns_service_ip     = string
    docker_bridge_cidr = optional(string)
  })
}

variable "azure_ad_rbac" {
  description = "Azure AD RBAC configuration"
  type = object({
    managed                = bool
    admin_group_object_ids = list(string)
  })
  default = null
}
```

### Security Considerations
- Enable Azure AD integration
- Use managed identities
- Enable network policies (Calico or Azure)
- Use private cluster endpoint
- Enable Defender for Containers

---

## Azure SQL Module

### Resources
- Azure SQL Server
- Databases
- Firewall rules
- Elastic pools
- Failover groups

### Common Variables
```hcl
variable "server_name" {
  description = "SQL Server name"
  type        = string
}

variable "administrator_login" {
  description = "Admin username"
  type        = string
}

variable "databases" {
  description = "Database configurations"
  type = map(object({
    sku_name    = string
    max_size_gb = number
    collation   = optional(string, "SQL_Latin1_General_CP1_CI_AS")
  }))
}

variable "enable_threat_detection" {
  description = "Enable Advanced Threat Protection"
  type        = bool
  default     = true
}

variable "minimum_tls_version" {
  description = "Minimum TLS version"
  type        = string
  default     = "1.2"
}
```

### Security Considerations
- Use Azure AD authentication
- Enable TDE (Transparent Data Encryption)
- Enable auditing to Log Analytics
- Use private endpoints
- Enable Advanced Threat Protection

---

## Storage Account Module

### Resources
- Storage Account
- Blob containers
- File shares
- Queues
- Tables

### Common Variables
```hcl
variable "name" {
  description = "Storage account name"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.name))
    error_message = "Storage account name must be 3-24 lowercase alphanumeric characters."
  }
}

variable "account_tier" {
  description = "Account tier (Standard or Premium)"
  type        = string
  default     = "Standard"
}

variable "account_replication_type" {
  description = "Replication type (LRS, GRS, RAGRS, ZRS)"
  type        = string
  default     = "GRS"
}

variable "enable_https_traffic_only" {
  description = "Force HTTPS"
  type        = bool
  default     = true
}

variable "min_tls_version" {
  description = "Minimum TLS version"
  type        = string
  default     = "TLS1_2"
}

variable "blob_containers" {
  description = "Blob container configurations"
  type = map(object({
    container_access_type = string  # private, blob, container
  }))
  default = {}
}
```

### Security Considerations
- Disable public blob access
- Use private endpoints
- Enable soft delete for blobs
- Enable versioning
- Use customer-managed keys for encryption

---

## Application Gateway Module

### Resources
- Application Gateway
- Backend pools
- HTTP settings
- Listeners
- Routing rules
- WAF policies

### Common Variables
```hcl
variable "name" {
  description = "Application Gateway name"
  type        = string
}

variable "sku" {
  description = "SKU configuration"
  type = object({
    name     = string  # Standard_v2, WAF_v2
    tier     = string
    capacity = number
  })
  default = {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }
}

variable "waf_configuration" {
  description = "WAF configuration"
  type = object({
    enabled          = bool
    firewall_mode    = string  # Detection or Prevention
    rule_set_type    = string
    rule_set_version = string
  })
  default = {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }
}
```

---

## Best Practices

1. **Use AzureRM provider version ~> 3.0** - Latest features
2. **Use managed identities** - Avoid storing credentials
3. **Enable diagnostic settings** - Log Analytics workspace
4. **Use private endpoints** - Keep traffic on Azure backbone
5. **Enable Azure Defender** - Threat detection
6. **Use availability zones** - High availability
7. **Tag all resources** - Cost management, ownership
8. **Use resource locks** - Prevent accidental deletion
9. **Enable soft delete** - Recovery options
10. **Follow Azure Well-Architected Framework**

## Provider Configuration

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }
}
```
