# External Services Reference

Quick reference for common external service configurations when creating Helm charts.

## Database Services

### MySQL

| Property | Value |
|----------|-------|
| Default Port | 3306 |
| JDBC Driver | `com.mysql.cj.jdbc.Driver` |
| JDBC URL | `jdbc:mysql://host:port/database?params` |
| Common Params | `useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true` |
| SSL Params | `useSSL=true&requireSSL=true&verifyServerCertificate=true` |

**Environment Variables:**
```yaml
- DB_HOST, MYSQL_HOST
- DB_PORT, MYSQL_PORT (3306)
- DB_NAME, MYSQL_DATABASE
- DB_USER, MYSQL_USER
- DB_PASSWORD, MYSQL_PASSWORD
```

**Health Check:**
```bash
mysqladmin ping -h host -u user -p
```

---

### PostgreSQL

| Property | Value |
|----------|-------|
| Default Port | 5432 |
| JDBC Driver | `org.postgresql.Driver` |
| JDBC URL | `jdbc:postgresql://host:port/database` |
| SSL Params | `sslmode=require` or `sslmode=verify-full` |

**Environment Variables:**
```yaml
- PGHOST, DB_HOST
- PGPORT, DB_PORT (5432)
- PGDATABASE, DB_NAME
- PGUSER, DB_USER
- PGPASSWORD, DB_PASSWORD
```

**Connection URL Format:**
```
postgresql://user:password@host:port/database?sslmode=require
```

**Health Check:**
```bash
pg_isready -h host -p 5432 -U user
```

---

### MongoDB

| Property | Value |
|----------|-------|
| Default Port | 27017 |
| Connection URL | `mongodb://host:port/database` |
| Replica Set URL | `mongodb://host1:port1,host2:port2/database?replicaSet=rs0` |

**Environment Variables:**
```yaml
- MONGODB_HOST
- MONGODB_PORT (27017)
- MONGODB_DATABASE
- MONGODB_USERNAME
- MONGODB_PASSWORD
- MONGODB_URI (full connection string)
```

---

## Search Services

### Elasticsearch

| Property | Value |
|----------|-------|
| HTTP Port | 9200 |
| Transport Port | 9300 |
| Health Endpoint | `/_cluster/health` |
| Version Check | `GET /` |

**Environment Variables:**
```yaml
- ELASTICSEARCH_HOST, ES_HOST
- ELASTICSEARCH_PORT, ES_PORT (9200)
- ELASTICSEARCH_SCHEME (http/https)
- ELASTICSEARCH_USER, ES_USER
- ELASTICSEARCH_PASSWORD, ES_PASSWORD
```

**Health Check:**
```bash
curl -s http://host:9200/_cluster/health | jq '.status'
# Returns: "green", "yellow", or "red"
```

**Index Management:**
```bash
# List indices
curl http://host:9200/_cat/indices

# Check index health
curl http://host:9200/_cluster/health/index_name
```

---

### OpenSearch

| Property | Value |
|----------|-------|
| HTTP Port | 9200 |
| Transport Port | 9300 |
| Health Endpoint | `/_cluster/health` |
| Dashboards Port | 5601 |

**Environment Variables:**
```yaml
# Compatible with Elasticsearch vars
- OPENSEARCH_HOST
- OPENSEARCH_PORT (9200)
- OPENSEARCH_SCHEME (http/https)
- OPENSEARCH_USER
- OPENSEARCH_PASSWORD
```

**Note:** OpenSearch is API-compatible with Elasticsearch 7.x. Most Elasticsearch clients work with OpenSearch.

---

## Messaging Services

### Apache Kafka

| Property | Value |
|----------|-------|
| Plaintext Port | 9092 |
| SSL Port | 9093 |
| SASL Port | 9094 |

**Security Protocols:**
- `PLAINTEXT` - No encryption or authentication
- `SSL` - TLS encryption
- `SASL_PLAINTEXT` - SASL authentication, no encryption
- `SASL_SSL` - SASL authentication with TLS

**SASL Mechanisms:**
- `PLAIN` - Username/password
- `SCRAM-SHA-256` - Salted challenge-response
- `SCRAM-SHA-512` - Salted challenge-response (stronger)
- `GSSAPI` - Kerberos
- `OAUTHBEARER` - OAuth 2.0

**Environment Variables:**
```yaml
- KAFKA_BOOTSTRAP_SERVERS (host1:9092,host2:9092)
- KAFKA_SECURITY_PROTOCOL
- KAFKA_SASL_MECHANISM
- KAFKA_SASL_USERNAME
- KAFKA_SASL_PASSWORD
- KAFKA_SSL_TRUSTSTORE_LOCATION
- KAFKA_SSL_TRUSTSTORE_PASSWORD
```

---

### RabbitMQ

| Property | Value |
|----------|-------|
| AMQP Port | 5672 |
| AMQPS Port | 5671 |
| Management Port | 15672 |
| Clustering Port | 25672 |

**Environment Variables:**
```yaml
- RABBITMQ_HOST
- RABBITMQ_PORT (5672)
- RABBITMQ_VHOST (/)
- RABBITMQ_USERNAME (guest)
- RABBITMQ_PASSWORD (guest)
```

**Connection URL Format:**
```
amqp://user:password@host:port/vhost
amqps://user:password@host:port/vhost  # With TLS
```

**Health Check:**
```bash
# Management API
curl -u user:pass http://host:15672/api/health/checks/alarms

# CLI (if available)
rabbitmqctl status
```

---

### Redis

| Property | Value |
|----------|-------|
| Default Port | 6379 |
| Sentinel Port | 26379 |
| Cluster Bus Port | 16379 |

**Environment Variables:**
```yaml
- REDIS_HOST
- REDIS_PORT (6379)
- REDIS_PASSWORD
- REDIS_DB (0)
- REDIS_URL (redis://[:password@]host:port/db)
```

**Connection URL Formats:**
```
redis://host:port/db
redis://:password@host:port/db
rediss://host:port/db  # With TLS
```

**Health Check:**
```bash
redis-cli -h host -p 6379 ping
# Returns: PONG
```

---

## Pipeline/Orchestration Services

### Apache Airflow

| Property | Value |
|----------|-------|
| Webserver Port | 8080 |
| Flower Port | 5555 |
| API Base Path | `/api/v1` |
| Health Endpoint | `/health` |

**Environment Variables:**
```yaml
- AIRFLOW_HOST (http://airflow-webserver:8080)
- AIRFLOW_USERNAME
- AIRFLOW_PASSWORD
# OR
- AIRFLOW_API_TOKEN
```

**API Endpoints:**
```bash
# Health check
GET /health

# List DAGs
GET /api/v1/dags

# Trigger DAG
POST /api/v1/dags/{dag_id}/dagRuns
```

---

### Temporal

| Property | Value |
|----------|-------|
| Frontend Port | 7233 |
| Web UI Port | 8080 |
| History Port | 7234 |
| Matching Port | 7235 |

**Environment Variables:**
```yaml
- TEMPORAL_HOST (temporal-frontend:7233)
- TEMPORAL_NAMESPACE (default)
- TEMPORAL_TLS_ENABLED
```

---

## Cache Services

### Memcached

| Property | Value |
|----------|-------|
| Default Port | 11211 |

**Environment Variables:**
```yaml
- MEMCACHED_HOST
- MEMCACHED_PORT (11211)
```

**Health Check:**
```bash
echo "stats" | nc host 11211
```

---

## Object Storage

### S3-Compatible (MinIO, AWS S3)

| Property | Value |
|----------|-------|
| API Port | 9000 (MinIO) |
| Console Port | 9001 (MinIO) |

**Environment Variables:**
```yaml
- AWS_ACCESS_KEY_ID, S3_ACCESS_KEY
- AWS_SECRET_ACCESS_KEY, S3_SECRET_KEY
- AWS_REGION, S3_REGION
- S3_ENDPOINT (for non-AWS)
- S3_BUCKET
```

**Endpoint Formats:**
```
# AWS S3
https://s3.region.amazonaws.com

# MinIO
http://minio:9000

# Path-style vs Virtual-hosted
http://minio:9000/bucket/key  # Path-style
http://bucket.minio:9000/key  # Virtual-hosted
```

---

## Health Check Patterns

### Common Endpoints

| Service | Liveness | Readiness |
|---------|----------|-----------|
| MySQL | TCP 3306 | `mysqladmin ping` |
| PostgreSQL | TCP 5432 | `pg_isready` |
| Elasticsearch | `GET /` | `GET /_cluster/health` |
| Redis | `PING` command | `PING` command |
| Kafka | TCP 9092 | Metadata request |
| RabbitMQ | TCP 5672 | `GET /api/health` |

### Kubernetes Probe Examples

```yaml
# TCP Socket (databases)
livenessProbe:
  tcpSocket:
    port: 5432
  periodSeconds: 10

# HTTP GET (web services)
livenessProbe:
  httpGet:
    path: /_cluster/health
    port: 9200
  periodSeconds: 30

# Exec command
livenessProbe:
  exec:
    command:
      - redis-cli
      - ping
  periodSeconds: 10
```

---

## Connection String Formats

| Service | Format |
|---------|--------|
| MySQL JDBC | `jdbc:mysql://host:port/db?params` |
| PostgreSQL JDBC | `jdbc:postgresql://host:port/db` |
| PostgreSQL URL | `postgresql://user:pass@host:port/db` |
| MongoDB | `mongodb://user:pass@host:port/db` |
| Redis | `redis://:pass@host:port/db` |
| RabbitMQ | `amqp://user:pass@host:port/vhost` |
| Kafka | `host1:port1,host2:port2` (bootstrap servers) |

---

## Kubernetes Service DNS

When services run in the same cluster:

```
# Same namespace
service-name:port

# Different namespace
service-name.namespace.svc.cluster.local:port

# Headless service (StatefulSet pods)
pod-0.service-name.namespace.svc.cluster.local:port
```

**Examples:**
```yaml
database:
  host: mysql.database.svc.cluster.local
  port: 3306

elasticsearch:
  host: elasticsearch-master.elastic.svc.cluster.local
  port: 9200

redis:
  host: redis-master.cache.svc.cluster.local
  port: 6379
```
