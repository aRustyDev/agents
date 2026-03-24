# CI/CD Provider Patterns

## GitHub Provider (integrations/github)

### Provider Configuration
```hcl
terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "github" {
  owner = var.github_owner
  # Token via GITHUB_TOKEN env var
}
```

### Repository Module
```hcl
variable "repositories" {
  description = "Repository configurations"
  type = map(object({
    description          = string
    visibility           = optional(string, "private")
    has_issues           = optional(bool, true)
    has_wiki             = optional(bool, false)
    has_projects         = optional(bool, false)
    allow_merge_commit   = optional(bool, true)
    allow_squash_merge   = optional(bool, true)
    allow_rebase_merge   = optional(bool, false)
    delete_branch_on_merge = optional(bool, true)
    auto_init            = optional(bool, true)
    gitignore_template   = optional(string)
    license_template     = optional(string)
    topics               = optional(list(string), [])
    vulnerability_alerts = optional(bool, true)
    archive_on_destroy   = optional(bool, true)
  }))
}

resource "github_repository" "this" {
  for_each = var.repositories

  name                   = each.key
  description            = each.value.description
  visibility             = each.value.visibility
  has_issues             = each.value.has_issues
  has_wiki               = each.value.has_wiki
  has_projects           = each.value.has_projects
  allow_merge_commit     = each.value.allow_merge_commit
  allow_squash_merge     = each.value.allow_squash_merge
  allow_rebase_merge     = each.value.allow_rebase_merge
  delete_branch_on_merge = each.value.delete_branch_on_merge
  auto_init              = each.value.auto_init
  gitignore_template     = each.value.gitignore_template
  license_template       = each.value.license_template
  topics                 = each.value.topics
  vulnerability_alerts   = each.value.vulnerability_alerts
  archive_on_destroy     = each.value.archive_on_destroy
}
```

### Branch Protection Module
```hcl
variable "branch_protections" {
  description = "Branch protection rules"
  type = map(object({
    repository                  = string
    pattern                     = string
    enforce_admins              = optional(bool, true)
    require_signed_commits      = optional(bool, false)
    required_linear_history     = optional(bool, false)
    require_conversation_resolution = optional(bool, true)
    required_status_checks = optional(object({
      strict   = bool
      contexts = list(string)
    }))
    required_pull_request_reviews = optional(object({
      dismiss_stale_reviews           = bool
      require_code_owner_reviews      = bool
      required_approving_review_count = number
    }))
  }))
}

resource "github_branch_protection" "this" {
  for_each = var.branch_protections

  repository_id                   = each.value.repository
  pattern                         = each.value.pattern
  enforce_admins                  = each.value.enforce_admins
  require_signed_commits          = each.value.require_signed_commits
  required_linear_history         = each.value.required_linear_history
  require_conversation_resolution = each.value.require_conversation_resolution

  dynamic "required_status_checks" {
    for_each = each.value.required_status_checks != null ? [each.value.required_status_checks] : []
    content {
      strict   = required_status_checks.value.strict
      contexts = required_status_checks.value.contexts
    }
  }

  dynamic "required_pull_request_reviews" {
    for_each = each.value.required_pull_request_reviews != null ? [each.value.required_pull_request_reviews] : []
    content {
      dismiss_stale_reviews           = required_pull_request_reviews.value.dismiss_stale_reviews
      require_code_owner_reviews      = required_pull_request_reviews.value.require_code_owner_reviews
      required_approving_review_count = required_pull_request_reviews.value.required_approving_review_count
    }
  }
}
```

### GitHub Actions Secrets
```hcl
resource "github_actions_secret" "this" {
  for_each = var.repository_secrets

  repository      = each.value.repository
  secret_name     = each.value.name
  plaintext_value = each.value.value  # Use encrypted_value in production
}

resource "github_actions_organization_secret" "this" {
  for_each = var.organization_secrets

  secret_name     = each.key
  visibility      = each.value.visibility  # all, private, selected
  plaintext_value = each.value.value
}
```

---

## GitLab Provider (gitlabhq/gitlab)

### Provider Configuration
```hcl
terraform {
  required_providers {
    gitlab = {
      source  = "gitlabhq/gitlab"
      version = "~> 16.0"
    }
  }
}

provider "gitlab" {
  base_url = var.gitlab_url  # Optional for self-hosted
  # Token via GITLAB_TOKEN env var
}
```

### Project Module
```hcl
variable "projects" {
  description = "GitLab project configurations"
  type = map(object({
    namespace_id               = number
    description                = string
    visibility_level           = optional(string, "private")
    default_branch             = optional(string, "main")
    merge_method               = optional(string, "merge")  # merge, rebase_merge, ff
    squash_option              = optional(string, "default_on")
    remove_source_branch_after_merge = optional(bool, true)
    only_allow_merge_if_pipeline_succeeds = optional(bool, true)
    only_allow_merge_if_all_discussions_are_resolved = optional(bool, true)
    container_registry_enabled = optional(bool, true)
    packages_enabled           = optional(bool, true)
    wiki_enabled               = optional(bool, false)
    issues_enabled             = optional(bool, true)
    shared_runners_enabled     = optional(bool, true)
    topics                     = optional(list(string), [])
  }))
}

resource "gitlab_project" "this" {
  for_each = var.projects

  name                       = each.key
  namespace_id               = each.value.namespace_id
  description                = each.value.description
  visibility_level           = each.value.visibility_level
  default_branch             = each.value.default_branch
  merge_method               = each.value.merge_method
  squash_option              = each.value.squash_option
  remove_source_branch_after_merge = each.value.remove_source_branch_after_merge
  only_allow_merge_if_pipeline_succeeds = each.value.only_allow_merge_if_pipeline_succeeds
  only_allow_merge_if_all_discussions_are_resolved = each.value.only_allow_merge_if_all_discussions_are_resolved
  container_registry_enabled = each.value.container_registry_enabled
  packages_enabled           = each.value.packages_enabled
  wiki_enabled               = each.value.wiki_enabled
  issues_enabled             = each.value.issues_enabled
  shared_runners_enabled     = each.value.shared_runners_enabled
  topics                     = each.value.topics
}
```

### GitLab CI/CD Variables
```hcl
resource "gitlab_project_variable" "this" {
  for_each = var.project_variables

  project           = each.value.project
  key               = each.value.key
  value             = each.value.value
  protected         = each.value.protected
  masked            = each.value.masked
  environment_scope = each.value.environment_scope
}

resource "gitlab_group_variable" "this" {
  for_each = var.group_variables

  group             = each.value.group
  key               = each.value.key
  value             = each.value.value
  protected         = each.value.protected
  masked            = each.value.masked
  environment_scope = each.value.environment_scope
}
```

---

## Buildkite Provider (buildkite/buildkite)

### Provider Configuration
```hcl
terraform {
  required_providers {
    buildkite = {
      source  = "buildkite/buildkite"
      version = "~> 1.0"
    }
  }
}

provider "buildkite" {
  organization = var.buildkite_org
  # Token via BUILDKITE_API_TOKEN env var
}
```

### Pipeline Module
```hcl
variable "pipelines" {
  description = "Buildkite pipeline configurations"
  type = map(object({
    repository                     = string
    description                    = optional(string)
    default_branch                 = optional(string, "main")
    branch_configuration           = optional(string)
    skip_queued_branch_builds      = optional(bool, true)
    skip_queued_branch_builds_filter = optional(string, "!main")
    cancel_running_branch_builds   = optional(bool, true)
    cancel_running_branch_builds_filter = optional(string, "!main")
    steps                          = string  # YAML pipeline definition
    cluster_id                     = optional(string)
    tags                           = optional(list(string), [])
  }))
}

resource "buildkite_pipeline" "this" {
  for_each = var.pipelines

  name                           = each.key
  repository                     = each.value.repository
  description                    = each.value.description
  default_branch                 = each.value.default_branch
  branch_configuration           = each.value.branch_configuration
  skip_queued_branch_builds      = each.value.skip_queued_branch_builds
  skip_queued_branch_builds_filter = each.value.skip_queued_branch_builds_filter
  cancel_running_branch_builds   = each.value.cancel_running_branch_builds
  cancel_running_branch_builds_filter = each.value.cancel_running_branch_builds_filter
  steps                          = each.value.steps
  cluster_id                     = each.value.cluster_id
  tags                           = each.value.tags
}
```

### Pipeline Schedule
```hcl
resource "buildkite_pipeline_schedule" "this" {
  for_each = var.pipeline_schedules

  pipeline_id = each.value.pipeline_id
  label       = each.value.label
  cronline    = each.value.cronline
  branch      = each.value.branch
  message     = each.value.message
  enabled     = each.value.enabled
  env         = each.value.env
}
```

---

## Best Practices

1. **Use environment variables for tokens** - Never hardcode credentials
2. **Enable branch protection** - Require reviews and status checks
3. **Use organization/group-level secrets** - Reduce duplication
4. **Archive instead of delete** - Preserve history
5. **Enable vulnerability alerts** - Security scanning
6. **Use CODEOWNERS files** - Automate review assignments
7. **Configure merge strategies** - Squash for clean history
8. **Enable required status checks** - Gate on CI passing
9. **Use project/repo templates** - Standardize configurations
10. **Implement least-privilege access** - Team-based permissions
