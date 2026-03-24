# Research Summary: <Application>

Research completed: <date>
Researcher: Claude Code

---

## Overview

| Property | Value |
|----------|-------|
| Application | <name> |
| Version | <version> |
| Chart Complexity | Simple / Standard / Complex / Operator |
| Official Chart Exists | Yes / No / Abandoned |
| Decision | Create New / Extend / Use Existing |

---

## Container Image

| Property | Value | Confidence |
|----------|-------|------------|
| Registry | `docker.io` / `ghcr.io` / custom | High/Medium/Low |
| Repository | `<org>/<image>` | High/Medium/Low |
| Latest Stable Tag | `<version>` | High/Medium/Low |
| Tag Pattern | `X.Y.Z` / `vX.Y.Z` / `latest` | High/Medium/Low |
| Platforms | `linux/amd64`, `linux/arm64` | High/Medium/Low |

**Source**: <url>

---

## Ports

| Port | Name | Purpose | Required | Source |
|------|------|---------|----------|--------|
| 8080 | http | Web UI / API | Yes | Dockerfile |
| 8081 | admin | Health / Metrics | No | Docs |
| 9090 | metrics | Prometheus metrics | No | Docs |

**Notes**: <any port-related notes>

---

## Health Endpoints

| Probe | Endpoint | Port | Method | Success Code |
|-------|----------|------|--------|--------------|
| Liveness | `/health` | 8080 | GET | 200 |
| Readiness | `/ready` | 8080 | GET | 200 |
| Startup | `/health` | 8080 | GET | 200 |

**Notes**: <any probe-related notes, e.g., slow startup considerations>

---

## Environment Variables

### Required

| Variable | Description | Default | Secret |
|----------|-------------|---------|--------|
| `DATABASE_URL` | Database connection string | - | Yes |
| `SECRET_KEY` | Application secret | - | Yes |

### Optional

| Variable | Description | Default | Secret |
|----------|-------------|---------|--------|
| `LOG_LEVEL` | Logging verbosity | `INFO` | No |
| `BASE_URL` | External URL | - | No |

**Source**: <url>

---

## External Dependencies

| Service | Type | Required | Notes |
|---------|------|----------|-------|
| PostgreSQL | Database | Yes | v12+ recommended |
| Redis | Cache | No | For session storage |
| Elasticsearch | Search | No | For full-text search |

**Implications**:
- Required services: Chart is **Complex**, needs CI exclusion
- Optional services: Can use subcharts with conditions

---

## Resource Requirements

| Level | CPU | Memory | Source |
|-------|-----|--------|--------|
| Minimum | 250m | 512Mi | Docs |
| Recommended | 1000m | 2Gi | Production guide |
| Default (chart) | 500m | 1Gi | Balanced |

**Notes**: <any resource-related notes, e.g., JVM heap considerations>

---

## Persistence

| Volume | Path | Purpose | Required |
|--------|------|---------|----------|
| data | `/app/data` | Application data | Yes |
| config | `/app/config` | Configuration files | No |

**Notes**: <any persistence-related notes>

---

## Configuration

### Format

- [ ] Environment variables only
- [ ] Config file (YAML/JSON/TOML)
- [ ] Both (env vars override config file)
- [ ] Command-line arguments

### Key Configuration Options

| Option | Env Var | Config Key | Description |
|--------|---------|------------|-------------|
| Database | `DATABASE_URL` | `database.url` | Connection string |
| Log Level | `LOG_LEVEL` | `logging.level` | Verbosity |

---

## Existing Charts

### Official Chart

| Property | Value |
|----------|-------|
| Repository | <url> |
| Version | <version> |
| Last Updated | <date> |
| Maintainer Active | Yes / No |

### Community Charts

| Repository | Stars | Last Updated | Notes |
|------------|-------|--------------|-------|
| <url> | <n> | <date> | <notes> |

---

## Open Questions

1. <Question that couldn't be answered>
2. <Assumption that needs validation>

---

## Risks and Blockers

| Risk | Severity | Mitigation |
|------|----------|------------|
| <risk1> | High/Medium/Low | <mitigation> |
| <risk2> | High/Medium/Low | <mitigation> |

---

## References

- Official Docs: <url>
- Docker Hub: <url>
- GitHub: <url>
- Existing Chart: <url>

---

## Approval

- [ ] Research reviewed
- [ ] Questions answered
- [ ] Proceed to planning approved

Approved by: <name/timestamp>
