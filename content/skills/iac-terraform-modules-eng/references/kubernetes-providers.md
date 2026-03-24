# Kubernetes & Container Provider Patterns

## Kubernetes Provider (hashicorp/kubernetes)

### Provider Configuration
```hcl
terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# Option 1: From kubeconfig
provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = var.kube_context
}

# Option 2: From EKS
provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

# Option 3: From GKE
provider "kubernetes" {
  host                   = "https://${google_container_cluster.cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.cluster.master_auth[0].cluster_ca_certificate)
}
```

### Namespace Module
```hcl
variable "namespaces" {
  description = "Namespace configurations"
  type = map(object({
    labels      = optional(map(string), {})
    annotations = optional(map(string), {})
    resource_quota = optional(object({
      hard = map(string)
    }))
    limit_range = optional(object({
      default_limit   = map(string)
      default_request = map(string)
    }))
  }))
}

resource "kubernetes_namespace" "this" {
  for_each = var.namespaces

  metadata {
    name        = each.key
    labels      = each.value.labels
    annotations = each.value.annotations
  }
}

resource "kubernetes_resource_quota" "this" {
  for_each = { for k, v in var.namespaces : k => v if v.resource_quota != null }

  metadata {
    name      = "${each.key}-quota"
    namespace = kubernetes_namespace.this[each.key].metadata[0].name
  }

  spec {
    hard = each.value.resource_quota.hard
  }
}

resource "kubernetes_limit_range" "this" {
  for_each = { for k, v in var.namespaces : k => v if v.limit_range != null }

  metadata {
    name      = "${each.key}-limits"
    namespace = kubernetes_namespace.this[each.key].metadata[0].name
  }

  spec {
    limit {
      type           = "Container"
      default        = each.value.limit_range.default_limit
      default_request = each.value.limit_range.default_request
    }
  }
}
```

### ConfigMap & Secret Module
```hcl
resource "kubernetes_config_map" "this" {
  for_each = var.config_maps

  metadata {
    name      = each.key
    namespace = each.value.namespace
    labels    = each.value.labels
  }

  data        = each.value.data
  binary_data = each.value.binary_data
}

resource "kubernetes_secret" "this" {
  for_each = var.secrets

  metadata {
    name      = each.key
    namespace = each.value.namespace
    labels    = each.value.labels
  }

  type = each.value.type  # Opaque, kubernetes.io/tls, etc.
  data = each.value.data
}
```

### Service Account with RBAC
```hcl
resource "kubernetes_service_account" "this" {
  for_each = var.service_accounts

  metadata {
    name      = each.key
    namespace = each.value.namespace
    annotations = each.value.annotations  # For IRSA/Workload Identity
  }
}

resource "kubernetes_cluster_role" "this" {
  for_each = var.cluster_roles

  metadata {
    name = each.key
  }

  dynamic "rule" {
    for_each = each.value.rules
    content {
      api_groups = rule.value.api_groups
      resources  = rule.value.resources
      verbs      = rule.value.verbs
    }
  }
}

resource "kubernetes_cluster_role_binding" "this" {
  for_each = var.cluster_role_bindings

  metadata {
    name = each.key
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = each.value.cluster_role
  }

  dynamic "subject" {
    for_each = each.value.subjects
    content {
      kind      = subject.value.kind
      name      = subject.value.name
      namespace = subject.value.namespace
    }
  }
}
```

---

## Helm Provider (hashicorp/helm)

### Provider Configuration
```hcl
terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}
```

### Helm Release Module
```hcl
variable "helm_releases" {
  description = "Helm release configurations"
  type = map(object({
    repository       = string
    chart            = string
    version          = string
    namespace        = string
    create_namespace = optional(bool, true)
    values           = optional(list(string), [])
    set              = optional(map(string), {})
    set_sensitive    = optional(map(string), {})
    timeout          = optional(number, 300)
    wait             = optional(bool, true)
    wait_for_jobs    = optional(bool, false)
    atomic           = optional(bool, false)
    cleanup_on_fail  = optional(bool, true)
    max_history      = optional(number, 10)
    dependency_update = optional(bool, true)
  }))
}

resource "helm_release" "this" {
  for_each = var.helm_releases

  name             = each.key
  repository       = each.value.repository
  chart            = each.value.chart
  version          = each.value.version
  namespace        = each.value.namespace
  create_namespace = each.value.create_namespace
  timeout          = each.value.timeout
  wait             = each.value.wait
  wait_for_jobs    = each.value.wait_for_jobs
  atomic           = each.value.atomic
  cleanup_on_fail  = each.value.cleanup_on_fail
  max_history      = each.value.max_history
  dependency_update = each.value.dependency_update

  dynamic "set" {
    for_each = each.value.set
    content {
      name  = set.key
      value = set.value
    }
  }

  dynamic "set_sensitive" {
    for_each = each.value.set_sensitive
    content {
      name  = set_sensitive.key
      value = set_sensitive.value
    }
  }

  values = each.value.values
}
```

### Common Helm Charts
```hcl
# Ingress NGINX
resource "helm_release" "ingress_nginx" {
  name             = "ingress-nginx"
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  version          = "4.9.0"
  namespace        = "ingress-nginx"
  create_namespace = true

  set {
    name  = "controller.replicaCount"
    value = "2"
  }
}

# Cert Manager
resource "helm_release" "cert_manager" {
  name             = "cert-manager"
  repository       = "https://charts.jetstack.io"
  chart            = "cert-manager"
  version          = "v1.14.0"
  namespace        = "cert-manager"
  create_namespace = true

  set {
    name  = "installCRDs"
    value = "true"
  }
}

# External Secrets
resource "helm_release" "external_secrets" {
  name             = "external-secrets"
  repository       = "https://charts.external-secrets.io"
  chart            = "external-secrets"
  version          = "0.9.0"
  namespace        = "external-secrets"
  create_namespace = true
}
```

---

## Talos Provider (siderolabs/talos)

### Provider Configuration
```hcl
terraform {
  required_providers {
    talos = {
      source  = "siderolabs/talos"
      version = "~> 0.5"
    }
  }
}

provider "talos" {}
```

### Talos Cluster Module
```hcl
resource "talos_machine_secrets" "this" {}

data "talos_machine_configuration" "controlplane" {
  cluster_name     = var.cluster_name
  machine_type     = "controlplane"
  cluster_endpoint = var.cluster_endpoint
  machine_secrets  = talos_machine_secrets.this.machine_secrets

  config_patches = [
    yamlencode({
      cluster = {
        network = {
          cni = {
            name = "none"  # Use Cilium
          }
        }
      }
    })
  ]
}

data "talos_machine_configuration" "worker" {
  cluster_name     = var.cluster_name
  machine_type     = "worker"
  cluster_endpoint = var.cluster_endpoint
  machine_secrets  = talos_machine_secrets.this.machine_secrets
}

resource "talos_machine_configuration_apply" "controlplane" {
  for_each = var.controlplane_nodes

  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.controlplane.machine_configuration
  node                        = each.value.ip
}

resource "talos_machine_configuration_apply" "worker" {
  for_each = var.worker_nodes

  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.worker.machine_configuration
  node                        = each.value.ip
}

resource "talos_machine_bootstrap" "this" {
  depends_on = [talos_machine_configuration_apply.controlplane]

  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = values(var.controlplane_nodes)[0].ip
}

data "talos_cluster_kubeconfig" "this" {
  depends_on = [talos_machine_bootstrap.this]

  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = values(var.controlplane_nodes)[0].ip
}
```

---

## Coder Provider (coder/coder)

### Provider Configuration
```hcl
terraform {
  required_providers {
    coder = {
      source  = "coder/coder"
      version = "~> 0.12"
    }
  }
}

provider "coder" {
  url = var.coder_url
  # Token via CODER_SESSION_TOKEN env var
}
```

### Workspace Template
```hcl
data "coder_workspace" "me" {}

resource "coder_agent" "main" {
  os   = "linux"
  arch = "amd64"

  startup_script = <<-EOT
    #!/bin/bash
    # Install development tools
    sudo apt-get update
    sudo apt-get install -y git vim
  EOT

  env = {
    GIT_AUTHOR_NAME     = data.coder_workspace.me.owner
    GIT_AUTHOR_EMAIL    = "${data.coder_workspace.me.owner}@example.com"
    GIT_COMMITTER_NAME  = data.coder_workspace.me.owner
    GIT_COMMITTER_EMAIL = "${data.coder_workspace.me.owner}@example.com"
  }
}

resource "coder_app" "code_server" {
  agent_id     = coder_agent.main.id
  slug         = "code-server"
  display_name = "VS Code"
  url          = "http://localhost:8080?folder=/home/coder"
  icon         = "/icon/code.svg"
  subdomain    = true
}
```

---

## Best Practices

1. **Use provider aliases** - Manage multiple clusters
2. **Pin chart versions** - Reproducible deployments
3. **Use values files** - Keep configurations in source control
4. **Enable atomic deploys** - Rollback on failure
5. **Limit history** - Clean up old releases
6. **Use namespaces** - Isolation and resource quotas
7. **Implement RBAC** - Least privilege access
8. **Use service accounts** - Pod-level permissions
9. **Configure resource limits** - Prevent resource exhaustion
10. **Use Helm hooks** - Lifecycle management
