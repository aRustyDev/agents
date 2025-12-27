# Orchestration Provider Patterns

## Ansible Automation Platform Provider (ansible/aap)

### Provider Configuration
```hcl
terraform {
  required_providers {
    aap = {
      source  = "ansible/aap"
      version = "~> 1.0"
    }
  }
}

provider "aap" {
  host     = var.aap_host
  username = var.aap_username
  password = var.aap_password

  # Or use token
  # token = var.aap_token

  insecure_skip_verify = var.skip_tls_verify
}
```

### Organization Module
```hcl
resource "aap_organization" "this" {
  for_each = var.organizations

  name        = each.key
  description = each.value.description

  max_hosts                = each.value.max_hosts
  default_environment      = each.value.default_environment
  custom_virtualenv        = each.value.custom_virtualenv
}
```

### Inventory Module
```hcl
resource "aap_inventory" "this" {
  for_each = var.inventories

  name         = each.key
  description  = each.value.description
  organization = each.value.organization_id

  variables = yamlencode(each.value.variables)
}

resource "aap_host" "this" {
  for_each = var.hosts

  name        = each.key
  description = each.value.description
  inventory   = each.value.inventory_id
  enabled     = each.value.enabled

  variables = yamlencode({
    ansible_host       = each.value.ansible_host
    ansible_user       = each.value.ansible_user
    ansible_connection = each.value.ansible_connection
  })
}

resource "aap_group" "this" {
  for_each = var.groups

  name        = each.key
  description = each.value.description
  inventory   = each.value.inventory_id

  variables = yamlencode(each.value.variables)
}

# Dynamic inventory source
resource "aap_inventory_source" "aws" {
  for_each = var.aws_inventory_sources

  name                 = each.key
  description          = each.value.description
  inventory            = each.value.inventory_id
  source               = "amazon.aws.aws_ec2"
  credential           = each.value.credential_id
  update_on_launch     = each.value.update_on_launch
  overwrite            = each.value.overwrite
  overwrite_variables  = each.value.overwrite_variables

  source_variables = yamlencode({
    regions          = each.value.regions
    keyed_groups     = each.value.keyed_groups
    hostnames        = each.value.hostnames
    filters          = each.value.filters
    compose          = each.value.compose
  })
}
```

### Project Module
```hcl
resource "aap_project" "this" {
  for_each = var.projects

  name         = each.key
  description  = each.value.description
  organization = each.value.organization_id

  scm_type             = each.value.scm_type  # git, svn, insights, archive
  scm_url              = each.value.scm_url
  scm_branch           = each.value.scm_branch
  scm_credential       = each.value.scm_credential_id
  scm_clean            = each.value.scm_clean
  scm_delete_on_update = each.value.scm_delete_on_update
  scm_update_on_launch = each.value.scm_update_on_launch

  default_environment = each.value.default_environment
}
```

### Job Template Module
```hcl
resource "aap_job_template" "this" {
  for_each = var.job_templates

  name         = each.key
  description  = each.value.description
  organization = each.value.organization_id
  inventory    = each.value.inventory_id
  project      = each.value.project_id
  playbook     = each.value.playbook

  job_type          = each.value.job_type  # run, check
  limit             = each.value.limit
  verbosity         = each.value.verbosity  # 0-5
  forks             = each.value.forks
  extra_vars        = yamlencode(each.value.extra_vars)
  ask_variables_on_launch = each.value.ask_variables_on_launch
  ask_limit_on_launch     = each.value.ask_limit_on_launch
  ask_inventory_on_launch = each.value.ask_inventory_on_launch

  become_enabled = each.value.become_enabled
  diff_mode      = each.value.diff_mode

  execution_environment = each.value.execution_environment_id
  credentials           = each.value.credential_ids
}
```

### Workflow Template Module
```hcl
resource "aap_workflow_job_template" "this" {
  for_each = var.workflow_templates

  name         = each.key
  description  = each.value.description
  organization = each.value.organization_id
  inventory    = each.value.inventory_id

  extra_vars                  = yamlencode(each.value.extra_vars)
  ask_variables_on_launch     = each.value.ask_variables_on_launch
  ask_inventory_on_launch     = each.value.ask_inventory_on_launch
  allow_simultaneous          = each.value.allow_simultaneous
  survey_enabled              = each.value.survey_enabled
  webhook_service             = each.value.webhook_service
  webhook_credential          = each.value.webhook_credential_id
}

resource "aap_workflow_job_template_node" "this" {
  for_each = var.workflow_nodes

  workflow_job_template = each.value.workflow_template_id
  identifier            = each.key
  unified_job_template  = each.value.job_template_id

  all_parents_must_converge = each.value.all_parents_must_converge
  extra_data                = yamlencode(each.value.extra_data)
}
```

### Credential Module
```hcl
resource "aap_credential" "machine" {
  for_each = var.machine_credentials

  name         = each.key
  description  = each.value.description
  organization = each.value.organization_id
  credential_type = aap_credential_type.machine.id

  inputs = jsonencode({
    username       = each.value.username
    password       = each.value.password
    ssh_key_data   = each.value.ssh_key
    become_method  = each.value.become_method
    become_username = each.value.become_username
    become_password = each.value.become_password
  })
}

resource "aap_credential" "aws" {
  for_each = var.aws_credentials

  name         = each.key
  description  = each.value.description
  organization = each.value.organization_id
  credential_type = aap_credential_type.amazon_web_services.id

  inputs = jsonencode({
    username = each.value.access_key
    password = each.value.secret_key
    security_token = each.value.session_token
  })
}
```

---

## Kestra Provider (kestra-io/kestra)

### Provider Configuration
```hcl
terraform {
  required_providers {
    kestra = {
      source  = "kestra-io/kestra"
      version = "~> 0.15"
    }
  }
}

provider "kestra" {
  url      = var.kestra_url
  username = var.kestra_username
  password = var.kestra_password

  # Or API token
  # api_token = var.kestra_api_token
}
```

### Namespace Module
```hcl
resource "kestra_namespace" "this" {
  for_each = var.namespaces

  namespace_id = each.key
  description  = each.value.description
}

resource "kestra_namespace_secret" "this" {
  for_each = var.namespace_secrets

  namespace    = each.value.namespace
  secret_key   = each.key
  secret_value = each.value.value
}
```

### Flow Module
```hcl
resource "kestra_flow" "this" {
  for_each = var.flows

  namespace = each.value.namespace
  flow_id   = each.key
  content   = each.value.content  # YAML flow definition
}

# Example flow content
locals {
  example_flow = <<-YAML
    id: example-etl
    namespace: production
    description: Example ETL pipeline

    inputs:
      - id: date
        type: DATE
        defaults: "{{ now() | date('yyyy-MM-dd') }}"

    tasks:
      - id: extract
        type: io.kestra.plugin.jdbc.postgresql.Query
        url: jdbc:postgresql://db:5432/source
        username: "{{ secret('DB_USER') }}"
        password: "{{ secret('DB_PASS') }}"
        sql: SELECT * FROM data WHERE date = '{{ inputs.date }}'
        store: true

      - id: transform
        type: io.kestra.plugin.scripts.python.Script
        script: |
          import pandas as pd
          df = pd.read_csv('{{ outputs.extract.uri }}')
          df['processed'] = True
          df.to_csv('output.csv', index=False)
        outputFiles:
          - output.csv

      - id: load
        type: io.kestra.plugin.gcp.bigquery.Load
        from: "{{ outputs.transform.outputFiles['output.csv'] }}"
        projectId: my-project
        dataset: analytics
        table: processed_data
        format: CSV

    triggers:
      - id: daily
        type: io.kestra.core.models.triggers.types.Schedule
        cron: "0 2 * * *"
  YAML
}
```

### Template Module
```hcl
resource "kestra_template" "this" {
  for_each = var.templates

  namespace   = each.value.namespace
  template_id = each.key
  content     = each.value.content
}

# Reusable task template
locals {
  slack_notification_template = <<-YAML
    id: slack-notification
    namespace: shared.templates

    tasks:
      - id: notify
        type: io.kestra.plugin.notifications.slack.SlackIncomingWebhook
        url: "{{ secret('SLACK_WEBHOOK') }}"
        payload: |
          {
            "text": "{{ inputs.message }}"
          }
  YAML
}
```

### Trigger Configuration
```hcl
resource "kestra_flow" "webhook_triggered" {
  namespace = "production"
  flow_id   = "webhook-handler"

  content = <<-YAML
    id: webhook-handler
    namespace: production

    inputs:
      - id: payload
        type: JSON

    tasks:
      - id: process
        type: io.kestra.plugin.scripts.shell.Commands
        commands:
          - echo "Processing webhook payload"

    triggers:
      - id: webhook
        type: io.kestra.core.models.triggers.types.Webhook
        key: "{{ secret('WEBHOOK_KEY') }}"
  YAML
}
```

---

## Prefect Provider (PrefectHQ/prefect)

### Provider Configuration
```hcl
terraform {
  required_providers {
    prefect = {
      source  = "PrefectHQ/prefect"
      version = "~> 2.0"
    }
  }
}

provider "prefect" {
  # Uses PREFECT_API_URL and PREFECT_API_KEY env vars
  # Or configure explicitly
  api_url = var.prefect_api_url
  api_key = var.prefect_api_key
}
```

### Work Pool Module
```hcl
resource "prefect_work_pool" "this" {
  for_each = var.work_pools

  name        = each.key
  type        = each.value.type  # kubernetes, docker, process, etc.
  description = each.value.description
  paused      = each.value.paused

  base_job_template = jsonencode(each.value.base_job_template)
}

# Kubernetes work pool example
resource "prefect_work_pool" "kubernetes" {
  name = "k8s-pool"
  type = "kubernetes"

  base_job_template = jsonencode({
    job_configuration = {
      image                  = "prefecthq/prefect:2-python3.11"
      namespace              = "prefect"
      service_account_name   = "prefect-worker"
      finished_job_ttl       = 300
      image_pull_policy      = "IfNotPresent"

      resources = {
        requests = {
          cpu    = "100m"
          memory = "256Mi"
        }
        limits = {
          cpu    = "500m"
          memory = "512Mi"
        }
      }
    }
    variables = {
      type = "object"
      properties = {
        image = {
          type        = "string"
          default     = "prefecthq/prefect:2-python3.11"
          description = "Container image to use"
        }
      }
    }
  })
}
```

### Deployment Module
```hcl
resource "prefect_deployment" "this" {
  for_each = var.deployments

  name        = each.key
  flow_name   = each.value.flow_name
  entrypoint  = each.value.entrypoint  # path/to/flow.py:flow_function
  description = each.value.description

  work_pool_name  = each.value.work_pool_name
  work_queue_name = each.value.work_queue_name

  parameters = jsonencode(each.value.parameters)
  tags       = each.value.tags

  enforce_parameter_schema = each.value.enforce_parameter_schema
  paused                   = each.value.paused

  # Storage block reference
  storage_document_id = each.value.storage_document_id

  # Schedule
  schedule {
    cron     = each.value.schedule_cron
    timezone = each.value.schedule_timezone
    active   = each.value.schedule_active
  }
}
```

### Block Module
```hcl
resource "prefect_block" "s3_storage" {
  for_each = var.s3_blocks

  name       = each.key
  type_slug  = "s3"

  data = jsonencode({
    bucket_path           = each.value.bucket_path
    aws_access_key_id     = each.value.access_key_id
    aws_secret_access_key = each.value.secret_access_key
    region_name           = each.value.region
  })
}

resource "prefect_block" "gcs_storage" {
  for_each = var.gcs_blocks

  name       = each.key
  type_slug  = "gcs"

  data = jsonencode({
    bucket_path               = each.value.bucket_path
    service_account_info      = each.value.service_account_json
  })
}

resource "prefect_block" "slack_webhook" {
  for_each = var.slack_blocks

  name       = each.key
  type_slug  = "slack-webhook"

  data = jsonencode({
    url = each.value.webhook_url
  })
}

resource "prefect_block" "secret" {
  for_each = var.secret_blocks

  name       = each.key
  type_slug  = "secret"

  data = jsonencode({
    value = each.value.value
  })
}
```

### Automation Module
```hcl
resource "prefect_automation" "this" {
  for_each = var.automations

  name        = each.key
  description = each.value.description
  enabled     = each.value.enabled

  trigger {
    type = each.value.trigger_type  # event, compound, sequence

    # For event triggers
    expect     = each.value.expect
    match      = each.value.match
    after      = each.value.after
    posture    = each.value.posture  # Reactive, Proactive

    # For compound triggers
    require = each.value.require  # all, any, number
    within  = each.value.within
  }

  actions {
    type = each.value.action_type  # run-deployment, pause-work-pool, send-notification

    # For run-deployment
    deployment_id = each.value.deployment_id
    parameters    = each.value.parameters

    # For notifications
    block_document_id = each.value.notification_block_id
    body              = each.value.notification_body
    subject           = each.value.notification_subject
  }
}
```

---

## Flagsmith Provider (Flagsmith/flagsmith)

### Provider Configuration
```hcl
terraform {
  required_providers {
    flagsmith = {
      source  = "Flagsmith/flagsmith"
      version = "~> 0.5"
    }
  }
}

provider "flagsmith" {
  # Master API key via FLAGSMITH_MASTER_API_KEY env var
  # Or configure explicitly
  master_api_key = var.flagsmith_master_api_key
  base_api_url   = var.flagsmith_api_url
}
```

### Project & Environment Module
```hcl
resource "flagsmith_project" "this" {
  for_each = var.projects

  name         = each.key
  organisation = each.value.organisation_id
}

resource "flagsmith_environment" "this" {
  for_each = var.environments

  name    = each.key
  project = each.value.project_id

  description              = each.value.description
  hide_disabled_flags      = each.value.hide_disabled_flags
  allow_client_traits      = each.value.allow_client_traits
  use_identity_composite_key_for_hashing = each.value.use_identity_composite_key
}
```

### Feature Flag Module
```hcl
resource "flagsmith_feature" "this" {
  for_each = var.features

  feature_name = each.key
  project_id   = each.value.project_id
  type         = each.value.type  # STANDARD, MULTIVARIATE

  description      = each.value.description
  initial_value    = each.value.initial_value
  default_enabled  = each.value.default_enabled
  is_archived      = each.value.is_archived

  tags = each.value.tags
}

resource "flagsmith_feature_state" "this" {
  for_each = var.feature_states

  feature        = each.value.feature_id
  environment    = each.value.environment_id
  enabled        = each.value.enabled
  feature_state_value {
    type         = each.value.value_type  # string, int, bool
    string_value = each.value.string_value
    integer_value = each.value.integer_value
    boolean_value = each.value.boolean_value
  }
}
```

### Segment Module
```hcl
resource "flagsmith_segment" "this" {
  for_each = var.segments

  name       = each.key
  project    = each.value.project_id
  feature    = each.value.feature_id

  description = each.value.description

  dynamic "rules" {
    for_each = each.value.rules
    content {
      type = rules.value.type  # ALL, ANY, NONE

      dynamic "conditions" {
        for_each = rules.value.conditions
        content {
          operator = conditions.value.operator  # EQUAL, NOT_EQUAL, GREATER_THAN, etc.
          property = conditions.value.property
          value    = conditions.value.value
        }
      }
    }
  }
}
```

### Multivariate Feature
```hcl
resource "flagsmith_feature" "multivariate" {
  feature_name = "checkout-button-color"
  project_id   = flagsmith_project.main.id
  type         = "MULTIVARIATE"

  description     = "A/B test for checkout button colors"
  default_enabled = true
}

resource "flagsmith_mv_feature_option" "blue" {
  feature = flagsmith_feature.multivariate.id
  environment = flagsmith_environment.production.id

  type         = "string"
  string_value = "blue"
  default_percentage_allocation = 50
}

resource "flagsmith_mv_feature_option" "green" {
  feature = flagsmith_feature.multivariate.id
  environment = flagsmith_environment.production.id

  type         = "string"
  string_value = "green"
  default_percentage_allocation = 50
}
```

---

## Best Practices

### Ansible AAP
1. **Use execution environments** - Containerized consistency
2. **Implement RBAC** - Role-based access control
3. **Use credential types** - Secure secret management
4. **Enable job isolation** - Container group isolation
5. **Use workflow templates** - Complex orchestration
6. **Enable inventory sources** - Dynamic inventory
7. **Configure webhooks** - Event-driven automation
8. **Use surveys** - Parameterized job templates
9. **Enable logging** - External logging integration
10. **Implement approval workflows** - Change control

### Kestra
1. **Use namespaces for isolation** - Multi-tenant workflows
2. **Store secrets in namespace secrets** - Secure credential storage
3. **Use templates for reusability** - DRY principles
4. **Implement error handling** - Retry and fallback
5. **Use flow inputs** - Parameterized execution
6. **Enable flow versioning** - Track changes
7. **Configure triggers appropriately** - Schedule, webhook, flow
8. **Use task outputs** - Chain task data
9. **Implement notifications** - Alert on failures
10. **Monitor flow metrics** - Observability

### Prefect
1. **Use work pools** - Environment-specific execution
2. **Configure proper storage** - Remote code storage
3. **Use blocks for credentials** - Centralized secrets
4. **Implement automations** - Event-driven responses
5. **Use deployment parameters** - Flexible execution
6. **Enable caching** - Performance optimization
7. **Use tags for organization** - Filter and group
8. **Configure retries** - Fault tolerance
9. **Use subflows** - Modular flow design
10. **Monitor with Prefect Cloud** - Observability

### Flagsmith
1. **Use environments** - Dev/staging/prod isolation
2. **Implement segments** - Targeted rollouts
3. **Use multivariate flags** - A/B testing
4. **Enable audit logs** - Track changes
5. **Use remote config** - Dynamic configuration
6. **Implement percentage rollouts** - Gradual releases
7. **Use feature tags** - Organization
8. **Enable webhooks** - Integration events
9. **Use server-side evaluation** - Security
10. **Cache feature states** - Performance
