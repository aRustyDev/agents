# Wrangler Configuration Reference

Complete reference for `wrangler.toml` configuration options.

## Basic Configuration

```toml
# Required
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

# Optional
account_id = "your-account-id"
workers_dev = true
compatibility_flags = ["nodejs_compat"]
```

## Environment Variables

```toml
# Plain text variables
[vars]
API_URL = "https://api.example.com"
DEBUG = "false"

# Secrets (set via CLI, not in file)
# wrangler secret put API_KEY
```

## Multi-Environment

```toml
name = "my-worker"
main = "src/index.ts"

# Production (default)
[vars]
ENVIRONMENT = "production"

# Staging environment
[env.staging]
name = "my-worker-staging"
vars = { ENVIRONMENT = "staging" }

# Development environment
[env.dev]
name = "my-worker-dev"
workers_dev = true
vars = { ENVIRONMENT = "development" }
```

Deploy with: `wrangler deploy --env staging`

## D1 Database Bindings

```toml
[[d1_databases]]
binding = "DB"                    # Variable name in code
database_name = "my-database"     # Human-readable name
database_id = "xxx-xxx-xxx"       # From wrangler d1 create
migrations_dir = "migrations"     # Optional, default: migrations

# Multiple databases
[[d1_databases]]
binding = "ANALYTICS_DB"
database_name = "analytics"
database_id = "yyy-yyy-yyy"
```

## KV Namespace Bindings

```toml
[[kv_namespaces]]
binding = "KV"
id = "xxxxxxxxxx"

# Preview namespace for dev
[[kv_namespaces]]
binding = "KV"
id = "xxxxxxxxxx"
preview_id = "yyyyyyyyyy"
```

## R2 Bucket Bindings

```toml
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"

# With jurisdiction (EU data residency)
[[r2_buckets]]
binding = "EU_BUCKET"
bucket_name = "eu-bucket"
jurisdiction = "eu"
```

## Durable Objects

```toml
# Binding to use Durable Objects
[[durable_objects.bindings]]
name = "COUNTER"
class_name = "Counter"

# For cross-script Durable Objects
[[durable_objects.bindings]]
name = "EXTERNAL_DO"
class_name = "ExternalClass"
script_name = "other-worker"

# Migrations for new/renamed classes
[[migrations]]
tag = "v1"
new_classes = ["Counter"]

[[migrations]]
tag = "v2"
renamed_classes = [{ from = "OldName", to = "NewName" }]
deleted_classes = ["DeprecatedClass"]
```

## Queues

```toml
# Producer binding
[[queues.producers]]
queue = "my-queue"
binding = "QUEUE"

# Consumer configuration
[[queues.consumers]]
queue = "my-queue"
max_batch_size = 10
max_batch_timeout = 5
max_retries = 3
dead_letter_queue = "my-dlq"
```

## Scheduled Triggers (Cron)

```toml
[triggers]
crons = [
  "0 * * * *",      # Every hour
  "0 0 * * *",      # Daily at midnight
  "0 0 * * 0",      # Weekly on Sunday
  "0 0 1 * *",      # Monthly on 1st
]
```

## Service Bindings

```toml
# Call other Workers
[[services]]
binding = "AUTH_SERVICE"
service = "auth-worker"
environment = "production"
```

## Analytics Engine

```toml
[[analytics_engine_datasets]]
binding = "ANALYTICS"
dataset = "my-dataset"
```

## AI Bindings

```toml
[ai]
binding = "AI"
```

## Hyperdrive (Database Proxy)

```toml
[[hyperdrive]]
binding = "HYPERDRIVE"
id = "xxxxxxxxxx"
```

## mTLS Certificates

```toml
[[mtls_certificates]]
binding = "MY_CERT"
certificate_id = "xxxxxxxxxx"
```

## Build Configuration

```toml
[build]
command = "npm run build"
cwd = "."
watch_dir = "src"

[build.upload]
format = "modules"
main = "./dist/index.js"
```

## Limits

```toml
[limits]
cpu_ms = 50
```

## Placement

```toml
[placement]
mode = "smart"  # or "off"
```

## Tail Workers

```toml
[[tail_consumers]]
service = "logging-worker"
```

## Node.js Compatibility

```toml
compatibility_flags = ["nodejs_compat"]

# Or for specific Node.js APIs
node_compat = true
```

## Custom Domains and Routes

```toml
# Custom domain
routes = [
  { pattern = "api.example.com/*", zone_name = "example.com" }
]

# Or simpler
route = "api.example.com/*"
```

## Complete Example

```toml
name = "production-api"
main = "src/index.ts"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[vars]
API_VERSION = "v2"

[[d1_databases]]
binding = "DB"
database_name = "main-db"
database_id = "xxx"

[[kv_namespaces]]
binding = "CACHE"
id = "yyy"

[[r2_buckets]]
binding = "UPLOADS"
bucket_name = "user-uploads"

[[durable_objects.bindings]]
name = "SESSIONS"
class_name = "SessionManager"

[[migrations]]
tag = "v1"
new_classes = ["SessionManager"]

[[queues.producers]]
queue = "tasks"
binding = "TASK_QUEUE"

[triggers]
crons = ["0 0 * * *"]

[ai]
binding = "AI"

routes = [
  { pattern = "api.example.com/*", zone_name = "example.com" }
]

[env.staging]
name = "staging-api"
vars = { API_VERSION = "v2-staging" }
routes = [
  { pattern = "api-staging.example.com/*", zone_name = "example.com" }
]
```
