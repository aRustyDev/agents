# AWS Terraform Module Patterns

## VPC Module

### Resources
- VPC with public/private subnets
- Internet Gateway and NAT Gateways
- Route tables and associations
- Network ACLs
- VPC Flow Logs

### Common Variables
```hcl
variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

variable "flow_log_destination_type" {
  description = "Type of destination for flow logs (cloud-watch-logs, s3)"
  type        = string
  default     = "cloud-watch-logs"
}
```

### Security Considerations
- Enable VPC Flow Logs for network monitoring
- Use private subnets for databases and internal services
- Restrict default security group rules

---

## EKS Module

### Resources
- EKS cluster with managed node groups
- IRSA (IAM Roles for Service Accounts)
- Cluster autoscaler
- VPC CNI configuration
- Cluster logging

### Common Variables
```hcl
variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.29"
}

variable "cluster_endpoint_private_access" {
  description = "Enable private API endpoint"
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access" {
  description = "Enable public API endpoint"
  type        = bool
  default     = false
}

variable "node_groups" {
  description = "Map of node group configurations"
  type = map(object({
    instance_types = list(string)
    min_size       = number
    max_size       = number
    desired_size   = number
    disk_size      = optional(number, 50)
    labels         = optional(map(string), {})
    taints         = optional(list(object({
      key    = string
      value  = string
      effect = string
    })), [])
  }))
}
```

### Security Considerations
- Use private endpoint access only in production
- Enable secrets encryption with KMS
- Implement Pod Security Standards
- Use IRSA instead of node instance profiles

---

## RDS Module

### Resources
- RDS instance or Aurora cluster
- Automated backups
- Read replicas
- Parameter groups
- Subnet groups
- Security groups

### Common Variables
```hcl
variable "engine" {
  description = "Database engine (postgres, mysql, mariadb)"
  type        = string
}

variable "engine_version" {
  description = "Database engine version"
  type        = string
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "allocated_storage" {
  description = "Storage size in GB"
  type        = number
  default     = 20
}

variable "storage_encrypted" {
  description = "Enable storage encryption"
  type        = bool
  default     = true
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "backup_retention_period" {
  description = "Days to retain backups"
  type        = number
  default     = 7
}
```

### Security Considerations
- Always enable storage encryption
- Use Secrets Manager for credentials
- Enable deletion protection in production
- Use private subnets only

---

## S3 Module

### Resources
- S3 bucket with versioning
- Encryption at rest (SSE-S3 or SSE-KMS)
- Bucket policies
- Lifecycle rules
- Replication configuration

### Common Variables
```hcl
variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "versioning_enabled" {
  description = "Enable versioning"
  type        = bool
  default     = true
}

variable "encryption_type" {
  description = "Encryption type (AES256, aws:kms)"
  type        = string
  default     = "AES256"
}

variable "block_public_access" {
  description = "Block all public access"
  type        = bool
  default     = true
}

variable "lifecycle_rules" {
  description = "Lifecycle rules for objects"
  type = list(object({
    id                       = string
    enabled                  = bool
    prefix                   = optional(string, "")
    expiration_days          = optional(number)
    noncurrent_expiration_days = optional(number)
    transition = optional(list(object({
      days          = number
      storage_class = string
    })), [])
  }))
  default = []
}
```

### Security Considerations
- Block public access by default
- Enable versioning for critical data
- Use KMS encryption for sensitive data
- Enable access logging

---

## ALB Module

### Resources
- Application Load Balancer
- Target groups
- Listener rules
- SSL/TLS certificates
- Access logs

### Common Variables
```hcl
variable "name" {
  description = "Name of the ALB"
  type        = string
}

variable "internal" {
  description = "Internal or internet-facing"
  type        = bool
  default     = false
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = true
}

variable "access_logs_bucket" {
  description = "S3 bucket for access logs"
  type        = string
  default     = null
}

variable "ssl_policy" {
  description = "SSL policy for HTTPS listeners"
  type        = string
  default     = "ELBSecurityPolicy-TLS13-1-2-2021-06"
}
```

---

## Lambda Module

### Resources
- Lambda function
- IAM execution role
- CloudWatch Logs
- Environment variables
- VPC configuration (optional)

### Common Variables
```hcl
variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "handler" {
  description = "Function handler"
  type        = string
  default     = "main.handler"
}

variable "memory_size" {
  description = "Memory in MB"
  type        = number
  default     = 128
}

variable "timeout" {
  description = "Timeout in seconds"
  type        = number
  default     = 30
}

variable "vpc_config" {
  description = "VPC configuration"
  type = object({
    subnet_ids         = list(string)
    security_group_ids = list(string)
  })
  default = null
}
```

---

## Security Group Module

### Pattern
```hcl
variable "rules" {
  description = "Security group rules"
  type = list(object({
    type        = string  # ingress or egress
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = optional(list(string))
    source_security_group_id = optional(string)
    description = string
  }))
}

resource "aws_security_group_rule" "this" {
  for_each = { for idx, rule in var.rules : idx => rule }

  type                     = each.value.type
  from_port                = each.value.from_port
  to_port                  = each.value.to_port
  protocol                 = each.value.protocol
  cidr_blocks              = each.value.cidr_blocks
  source_security_group_id = each.value.source_security_group_id
  security_group_id        = aws_security_group.this.id
  description              = each.value.description
}
```

---

## Best Practices

1. **Use AWS provider version ~> 5.0** - Latest features and security patches
2. **Enable encryption by default** - S3, RDS, EBS, Secrets Manager
3. **Use least-privilege IAM** - Specific policies per resource
4. **Tag all resources consistently** - Cost allocation, ownership
5. **Enable logging and monitoring** - CloudWatch, VPC Flow Logs
6. **Use KMS for encryption** - Customer-managed keys for sensitive data
7. **Implement backup strategies** - RDS snapshots, S3 versioning
8. **Use PrivateLink when possible** - Keep traffic within AWS
9. **Enable GuardDuty/SecurityHub** - Threat detection
10. **Follow AWS Well-Architected Framework** - Reliability, security, cost
