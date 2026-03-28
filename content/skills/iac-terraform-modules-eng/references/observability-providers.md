# Observability Provider Patterns

## Grafana Provider (grafana/grafana)

### Provider Configuration
```hcl
terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "~> 3.0"
    }
  }
}

# Grafana OSS/Enterprise
provider "grafana" {
  url  = var.grafana_url
  auth = var.grafana_api_key  # Or service account token

  # Optional TLS configuration
  tls_key              = var.tls_key
  tls_cert             = var.tls_cert
  insecure_skip_verify = var.skip_tls_verify
}

# Grafana Cloud
provider "grafana" {
  alias         = "cloud"
  cloud_api_key = var.grafana_cloud_api_key
}

# Multiple stacks
provider "grafana" {
  alias = "stack_1"
  url   = "https://stack1.grafana.net"
  auth  = var.stack1_token
}

provider "grafana" {
  alias = "stack_2"
  url   = "https://stack2.grafana.net"
  auth  = var.stack2_token
}
```

### Organization & User Module
```hcl
resource "grafana_organization" "this" {
  for_each = var.organizations

  name         = each.key
  admin_user   = each.value.admin_user
  create_users = each.value.create_users
  admins       = each.value.admins
  editors      = each.value.editors
  viewers      = each.value.viewers
}

resource "grafana_user" "this" {
  for_each = var.users

  email    = each.value.email
  name     = each.key
  login    = each.value.login
  password = each.value.password
  is_admin = each.value.is_admin
}

resource "grafana_team" "this" {
  for_each = var.teams

  name    = each.key
  email   = each.value.email
  members = each.value.members
}
```

### Folder Module
```hcl
resource "grafana_folder" "this" {
  for_each = var.folders

  title                        = each.key
  uid                          = each.value.uid
  parent_folder_uid            = each.value.parent_folder_uid
  prevent_destroy_if_not_empty = each.value.prevent_destroy
}

resource "grafana_folder_permission" "this" {
  for_each = var.folder_permissions

  folder_uid = each.value.folder_uid

  dynamic "permissions" {
    for_each = each.value.permissions
    content {
      role       = permissions.value.role
      permission = permissions.value.permission  # View, Edit, Admin
    }
  }

  dynamic "permissions" {
    for_each = each.value.team_permissions
    content {
      team_id    = permissions.value.team_id
      permission = permissions.value.permission
    }
  }

  dynamic "permissions" {
    for_each = each.value.user_permissions
    content {
      user_id    = permissions.value.user_id
      permission = permissions.value.permission
    }
  }
}
```

### Data Source Module
```hcl
resource "grafana_data_source" "prometheus" {
  for_each = var.prometheus_datasources

  name = each.key
  type = "prometheus"
  url  = each.value.url
  uid  = each.value.uid

  is_default               = each.value.is_default
  basic_auth_enabled       = each.value.basic_auth_enabled
  basic_auth_username      = each.value.basic_auth_username

  secure_json_data_encoded = jsonencode({
    basicAuthPassword = each.value.basic_auth_password
    httpHeaderValue1  = each.value.bearer_token
  })

  json_data_encoded = jsonencode({
    httpMethod           = "POST"
    manageAlerts         = each.value.manage_alerts
    prometheusType       = each.value.prometheus_type  # Prometheus, Cortex, Mimir, Thanos
    prometheusVersion    = each.value.prometheus_version
    cacheLevel           = each.value.cache_level
    incrementalQuerying  = each.value.incremental_querying
    httpHeaderName1      = each.value.bearer_token != null ? "Authorization" : null
  })
}

resource "grafana_data_source" "loki" {
  for_each = var.loki_datasources

  name = each.key
  type = "loki"
  url  = each.value.url
  uid  = each.value.uid

  json_data_encoded = jsonencode({
    maxLines              = each.value.max_lines
    derivedFields         = each.value.derived_fields
    alertmanagerUid       = each.value.alertmanager_uid
  })
}

resource "grafana_data_source" "tempo" {
  for_each = var.tempo_datasources

  name = each.key
  type = "tempo"
  url  = each.value.url
  uid  = each.value.uid

  json_data_encoded = jsonencode({
    tracesToLogs = {
      datasourceUid       = each.value.loki_uid
      filterByTraceID     = true
      filterBySpanID      = true
      mapTagNamesEnabled  = true
      mappedTags          = each.value.mapped_tags
    }
    tracesToMetrics = {
      datasourceUid = each.value.prometheus_uid
    }
    serviceMap = {
      datasourceUid = each.value.prometheus_uid
    }
    nodeGraph = {
      enabled = true
    }
    search = {
      hide = false
    }
    lokiSearch = {
      datasourceUid = each.value.loki_uid
    }
  })
}

resource "grafana_data_source" "cloudwatch" {
  for_each = var.cloudwatch_datasources

  name = each.key
  type = "cloudwatch"
  uid  = each.value.uid

  json_data_encoded = jsonencode({
    authType      = "keys"
    defaultRegion = each.value.default_region
  })

  secure_json_data_encoded = jsonencode({
    accessKey = each.value.access_key
    secretKey = each.value.secret_key
  })
}
```

### Dashboard Module
```hcl
resource "grafana_dashboard" "this" {
  for_each = var.dashboards

  folder      = each.value.folder_uid
  config_json = each.value.config_json
  overwrite   = each.value.overwrite
  message     = each.value.message
}

# Dashboard from file
resource "grafana_dashboard" "from_file" {
  for_each = var.dashboard_files

  folder = each.value.folder_uid
  config_json = templatefile("${path.module}/dashboards/${each.key}.json", {
    datasource_uid = each.value.datasource_uid
    environment    = each.value.environment
  })
}

# Dashboard from JSON API
data "http" "dashboard" {
  for_each = var.dashboard_urls

  url = each.value
}

resource "grafana_dashboard" "from_url" {
  for_each = var.dashboard_urls

  config_json = data.http.dashboard[each.key].response_body
}
```

### Alerting Module
```hcl
resource "grafana_contact_point" "this" {
  for_each = var.contact_points

  name = each.key

  dynamic "slack" {
    for_each = each.value.slack != null ? [each.value.slack] : []
    content {
      url                     = slack.value.webhook_url
      recipient               = slack.value.recipient
      username                = slack.value.username
      icon_emoji              = slack.value.icon_emoji
      text                    = slack.value.text
      title                   = slack.value.title
      mention_channel         = slack.value.mention_channel
      mention_users           = slack.value.mention_users
      mention_groups          = slack.value.mention_groups
    }
  }

  dynamic "email" {
    for_each = each.value.email != null ? [each.value.email] : []
    content {
      addresses               = email.value.addresses
      single_email            = email.value.single_email
      message                 = email.value.message
      subject                 = email.value.subject
    }
  }

  dynamic "pagerduty" {
    for_each = each.value.pagerduty != null ? [each.value.pagerduty] : []
    content {
      integration_key = pagerduty.value.integration_key
      severity        = pagerduty.value.severity
      class           = pagerduty.value.class
      component       = pagerduty.value.component
      group           = pagerduty.value.group
    }
  }

  dynamic "opsgenie" {
    for_each = each.value.opsgenie != null ? [each.value.opsgenie] : []
    content {
      api_key          = opsgenie.value.api_key
      api_url          = opsgenie.value.api_url
      auto_close       = opsgenie.value.auto_close
      override_priority = opsgenie.value.override_priority
      send_tags_as     = opsgenie.value.send_tags_as
    }
  }

  dynamic "webhook" {
    for_each = each.value.webhook != null ? [each.value.webhook] : []
    content {
      url                   = webhook.value.url
      http_method           = webhook.value.http_method
      username              = webhook.value.username
      password              = webhook.value.password
      authorization_scheme  = webhook.value.auth_scheme
      authorization_credentials = webhook.value.auth_credentials
      max_alerts            = webhook.value.max_alerts
      message               = webhook.value.message
      title                 = webhook.value.title
    }
  }
}

resource "grafana_notification_policy" "this" {
  for_each = var.notification_policies

  contact_point   = each.value.contact_point
  group_by        = each.value.group_by
  group_wait      = each.value.group_wait
  group_interval  = each.value.group_interval
  repeat_interval = each.value.repeat_interval

  dynamic "policy" {
    for_each = each.value.policies
    content {
      contact_point = policy.value.contact_point
      group_by      = policy.value.group_by
      continue      = policy.value.continue

      dynamic "matcher" {
        for_each = policy.value.matchers
        content {
          label = matcher.value.label
          match = matcher.value.match  # =, !=, =~, !~
          value = matcher.value.value
        }
      }

      mute_timings = policy.value.mute_timings
    }
  }
}

resource "grafana_mute_timing" "this" {
  for_each = var.mute_timings

  name = each.key

  dynamic "intervals" {
    for_each = each.value.intervals
    content {
      weekdays      = intervals.value.weekdays
      days_of_month = intervals.value.days_of_month
      months        = intervals.value.months
      years         = intervals.value.years
      location      = intervals.value.location

      dynamic "times" {
        for_each = intervals.value.times
        content {
          start = times.value.start
          end   = times.value.end
        }
      }
    }
  }
}

resource "grafana_rule_group" "this" {
  for_each = var.rule_groups

  name             = each.key
  folder_uid       = each.value.folder_uid
  interval_seconds = each.value.interval_seconds
  org_id           = each.value.org_id

  dynamic "rule" {
    for_each = each.value.rules
    content {
      name           = rule.value.name
      for            = rule.value.for
      condition      = rule.value.condition
      no_data_state  = rule.value.no_data_state  # Alerting, NoData, OK
      exec_err_state = rule.value.exec_err_state  # Alerting, Error, OK

      annotations = rule.value.annotations
      labels      = rule.value.labels

      dynamic "data" {
        for_each = rule.value.data
        content {
          ref_id         = data.value.ref_id
          datasource_uid = data.value.datasource_uid
          query_type     = data.value.query_type

          relative_time_range {
            from = data.value.from
            to   = data.value.to
          }

          model = jsonencode(data.value.model)
        }
      }
    }
  }
}
```

### Service Account Module
```hcl
resource "grafana_service_account" "this" {
  for_each = var.service_accounts

  name        = each.key
  role        = each.value.role  # Viewer, Editor, Admin
  is_disabled = each.value.is_disabled
}

resource "grafana_service_account_token" "this" {
  for_each = var.service_account_tokens

  name               = each.key
  service_account_id = each.value.service_account_id
  seconds_to_live    = each.value.seconds_to_live
}

resource "grafana_service_account_permission" "this" {
  for_each = var.service_account_permissions

  service_account_id = each.value.service_account_id

  dynamic "permissions" {
    for_each = each.value.permissions
    content {
      team_id    = permissions.value.team_id
      user_id    = permissions.value.user_id
      permission = permissions.value.permission  # Edit, Admin
    }
  }
}
```

---

## Grafana Cloud Module

### Stack Management
```hcl
resource "grafana_cloud_stack" "this" {
  provider = grafana.cloud

  for_each = var.cloud_stacks

  name        = each.key
  slug        = each.value.slug
  region_slug = each.value.region  # us, eu, au, prod-ap-southeast-0, etc.
  description = each.value.description

  wait_for_readiness = each.value.wait_for_readiness
}

resource "grafana_cloud_stack_service_account" "this" {
  provider = grafana.cloud

  for_each = var.cloud_service_accounts

  stack_slug  = each.value.stack_slug
  name        = each.key
  role        = each.value.role
  is_disabled = each.value.is_disabled
}

resource "grafana_cloud_stack_service_account_token" "this" {
  provider = grafana.cloud

  for_each = var.cloud_service_account_tokens

  stack_slug         = each.value.stack_slug
  service_account_id = each.value.service_account_id
  name               = each.key
  seconds_to_live    = each.value.seconds_to_live
}
```

### Synthetic Monitoring
```hcl
resource "grafana_synthetic_monitoring_installation" "this" {
  provider = grafana.cloud

  stack_id              = grafana_cloud_stack.main.id
  metrics_publisher_key = var.metrics_publisher_key
}

resource "grafana_synthetic_monitoring_check" "http" {
  for_each = var.synthetic_http_checks

  job     = each.key
  target  = each.value.target
  enabled = each.value.enabled
  probes  = each.value.probes

  labels = each.value.labels

  settings {
    http {
      method           = each.value.method
      body             = each.value.body
      bearer_token     = each.value.bearer_token
      cache_busting_query_param_name = each.value.cache_busting_param

      valid_status_codes   = each.value.valid_status_codes
      valid_http_versions  = each.value.valid_http_versions

      tls_config {
        insecure_skip_verify = each.value.skip_tls_verify
        server_name          = each.value.tls_server_name
      }

      dynamic "basic_auth" {
        for_each = each.value.basic_auth != null ? [each.value.basic_auth] : []
        content {
          username = basic_auth.value.username
          password = basic_auth.value.password
        }
      }
    }
  }

  frequency   = each.value.frequency
  timeout     = each.value.timeout
  alert_sensitivity = each.value.alert_sensitivity
}

resource "grafana_synthetic_monitoring_check" "dns" {
  for_each = var.synthetic_dns_checks

  job     = each.key
  target  = each.value.target
  enabled = each.value.enabled
  probes  = each.value.probes

  settings {
    dns {
      record_type = each.value.record_type  # A, AAAA, CNAME, MX, NS, etc.
      server      = each.value.server
      port        = each.value.port
      protocol    = each.value.protocol  # UDP, TCP

      valid_r_codes = each.value.valid_rcodes
    }
  }

  frequency = each.value.frequency
  timeout   = each.value.timeout
}

resource "grafana_synthetic_monitoring_check" "tcp" {
  for_each = var.synthetic_tcp_checks

  job     = each.key
  target  = each.value.target
  enabled = each.value.enabled
  probes  = each.value.probes

  settings {
    tcp {
      tls = each.value.tls

      tls_config {
        insecure_skip_verify = each.value.skip_tls_verify
      }
    }
  }

  frequency = each.value.frequency
  timeout   = each.value.timeout
}
```

### Adaptive Metrics
```hcl
# grafana/grafana-adaptive-metrics provider
terraform {
  required_providers {
    grafana-adaptive-metrics = {
      source  = "grafana/grafana-adaptive-metrics"
      version = "~> 0.2"
    }
  }
}

provider "grafana-adaptive-metrics" {
  url   = "${grafana_cloud_stack.main.url}/api/v1/recommendations"
  token = grafana_cloud_stack_service_account_token.main.key
}

resource "grafana-adaptive-metrics_exemption" "this" {
  for_each = var.metric_exemptions

  metric           = each.key
  reason           = each.value.reason
  keep_labels      = each.value.keep_labels
  disable_recommendations = each.value.disable_recommendations
}

resource "grafana-adaptive-metrics_rule" "this" {
  for_each = var.aggregation_rules

  metric      = each.key
  match_type  = each.value.match_type  # exact, prefix
  drop_labels = each.value.drop_labels
  aggregations = each.value.aggregations  # ["sum", "count"]
  aggregation_interval = each.value.aggregation_interval
  aggregation_delay    = each.value.aggregation_delay
}
```

---

## Best Practices

1. **Use folders for organization** - Logical dashboard grouping
2. **Implement role-based access** - Teams and permissions
3. **Use provisioning where possible** - GitOps workflows
4. **Configure alerting properly** - Contact points, policies, mute timings
5. **Use service accounts** - Machine-to-machine auth over user tokens
6. **Set up data source correlation** - Link logs, traces, metrics
7. **Enable synthetic monitoring** - Proactive availability checks
8. **Use adaptive metrics** - Cost optimization for Grafana Cloud
9. **Version control dashboards** - JSON export/import
10. **Monitor Grafana itself** - Self-monitoring dashboards
