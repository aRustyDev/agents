# Chart Complexity Classification

Guide for assessing Helm chart complexity to determine appropriate development approach and CI configuration.

## Complexity Levels

| Level | Characteristics | CI Behavior | Examples |
|-------|-----------------|-------------|----------|
| **Simple** | Single container, no external deps | Full lint + install | nginx, static sites, simple APIs |
| **Standard** | Single container, optional deps (subcharts) | Full lint + install | Web apps with optional Redis/PostgreSQL |
| **Complex** | External services required | Lint only | OpenMetadata, Airflow, data platforms |
| **Operator** | Deploys CRDs and controllers | Special handling | cert-manager, ArgoCD, Prometheus Operator |

---

## Identifying Complexity

### Simple Chart Indicators

- Self-contained application
- No database, cache, or message queue required
- No secrets needed for basic functionality
- Single port exposure
- Stateless (no PersistentVolumeClaims)

**Example**: Static website server, simple REST API, CLI tools

### Standard Chart Indicators

- Optional dependencies via subcharts (condition-enabled)
- Can function in degraded mode without dependencies
- Dependencies can be deployed alongside via `helm dependency`

**Example**: Web app that optionally uses Redis for caching

```yaml
# Chart.yaml
dependencies:
  - name: redis
    version: "17.0.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled  # Optional
```

### Complex Chart Indicators

Application **requires** one or more of:

| Category | Services |
|----------|----------|
| **Database** | MySQL, PostgreSQL, MongoDB, Cassandra, CockroachDB |
| **Search** | Elasticsearch, OpenSearch, Solr, Meilisearch |
| **Messaging** | Kafka, RabbitMQ, NATS, Pulsar |
| **Pipeline** | Airflow, Dagster, Prefect, Temporal |
| **Cache** | Redis (as primary store), Memcached |
| **Auth** | External LDAP, OIDC provider, Keycloak |
| **Storage** | S3-compatible, MinIO, external NFS |

**Key distinction**: Application **cannot start** or **fails health checks** without these services.

**Example**: OpenMetadata requires MySQL + Elasticsearch + Airflow

### Operator Chart Indicators

- Installs CustomResourceDefinitions (CRDs)
- Deploys controller/operator pods
- Manages lifecycle of custom resources
- May require cluster-admin permissions

**Example**: cert-manager, Prometheus Operator, ArgoCD

---

## CI Configuration by Complexity

### Simple & Standard Charts

Full CI pipeline applies:

```yaml
# ct.yaml (lint) - included
# ct-install.yaml (install) - included
```

### Complex Charts

**Lint only** - exclude from install tests:

```yaml
# ct-install.yaml
excluded-charts:
  - openmetadata      # Requires external MySQL, Elasticsearch, Airflow
  - airflow           # Requires external PostgreSQL, Redis
  - temporal          # Requires external PostgreSQL, Elasticsearch
```

**Comment format**: Always document why the chart is excluded.

### Operator Charts

May require special handling:

```yaml
# ct-install.yaml
excluded-charts:
  - cert-manager  # Requires CRD installation permissions
```

Or use helm-extra-args for CRD installation:

```yaml
helm-extra-args: --set installCRDs=true
```

---

## Decision Tree

```
Is application self-contained?
├── Yes → Simple
└── No → Does it have optional dependencies?
    ├── Yes (can run without them) → Standard
    └── No (requires external services) → Complex
        └── Does it install CRDs? → Operator
```

---

## Complexity-Specific Patterns

### Complex Charts: External Service Configuration

Use the external service pattern templates:

- `assets/patterns/external-database.yaml`
- `assets/patterns/external-search.yaml`
- `assets/patterns/external-messaging.yaml`

Key patterns:
- `existingSecret` for production credentials
- Separate host/port/scheme configuration
- Connection timeout settings
- SSL/TLS configuration options

### Complex Charts: Values Structure

```yaml
# External database (not a subchart)
database:
  type: mysql
  host: ""           # Required - no default
  port: 3306
  name: "app_db"
  username: ""
  password: ""
  existingSecret: "" # Production: use this instead of password
  existingSecretKey: "password"

# vs Standard chart subchart:
postgresql:
  enabled: true      # Optional - has default
  auth:
    database: myapp
```

### Operator Charts: CRD Handling

```yaml
# values.yaml
crds:
  install: true      # Install CRDs with chart
  keep: true         # Keep CRDs on uninstall

# templates/crds/*.yaml
{{- if .Values.crds.install }}
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
...
{{- end }}
```

---

## Checklist: Determining Complexity

Before starting chart development:

- [ ] Can the application start without external databases?
- [ ] Can it pass health checks without external services?
- [ ] Are all dependencies optional (condition-enabled)?
- [ ] Does it install CRDs?
- [ ] What's the minimum viable configuration?

Based on answers, classify and configure CI accordingly.
