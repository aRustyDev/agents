# Research Strategy for Helm Charts

Systematic approach to gathering information when creating Helm charts for applications.

## Overview

Before writing templates, gather:
1. Existing charts (don't reinvent)
2. Container configuration (image, ports, env vars)
3. Health endpoints
4. Resource requirements
5. Dependencies

---

## Step 1: Check for Existing Charts

**Always check first** - the project may maintain an official chart.

### GitHub Search

```bash
# Search for helm chart in project's org
gh search repos "<project> helm" --owner <org>

# Check common locations in project repo
curl -s "https://api.github.com/repos/<org>/<project>/contents" | jq -r '.[].name' | grep -iE "chart|helm|deploy|kubernetes"

# Common chart locations:
# - charts/
# - deploy/helm/
# - helm/
# - .helm/
# - kubernetes/helm/
```

### Artifact Hub Search

```bash
# Search Artifact Hub API
curl -s "https://artifacthub.io/api/v1/packages/search?ts_query_web=<project>&kind=0" | \
  jq '.packages[] | {name, repository: .repository.name, url: .repository.url}'

# Or browse: https://artifacthub.io/packages/search?ts_query_web=<project>
```

### Helm Hub / Bitnami

```bash
# Check Bitnami charts
helm search hub <project>

# Add and search Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm search repo bitnami/<project>
```

### Decision: Existing Chart Found

If an official or well-maintained chart exists:

| Scenario | Action | Next Step |
|----------|--------|-----------|
| Official chart meets needs | **Use directly** | Skip chart creation |
| Official chart missing features | **Extend** | See `extend-contribute-strategy.md` |
| Official chart, different architecture | **Create independent** | Proceed with new chart |
| Official chart, abandoned (>1yr stale) | **Fork and adopt** | See `extend-contribute-strategy.md` |
| Community chart, good quality | **Review patterns** | Adapt or extend |
| Multiple charts exist | **Compare** | Pick best to extend or create fresh |
| No charts found | **Create new** | Proceed with research |

**Activity Check for "Abandoned":**
```bash
# Check last commit date
gh repo view <org>/<repo> --json pushedAt --jq '.pushedAt'

# Check open issues/PRs age
gh issue list -R <org>/<repo> --state open --json createdAt | jq '.[0].createdAt'
```

### Workflow Selection

Based on the decision above, select your workflow:

| Decision | Chart Complexity | Workflow |
|----------|------------------|----------|
| Use directly | - | **Skip** - No chart to create |
| Extend | Any | **Full Workflow** - See `extend-contribute-strategy.md` |
| Create independent | Simple/Standard | **Fast Path** - Quick create, validate, PR |
| Create independent | Complex/Operator | **Full Workflow** - Research → Plan → Implement |

**Fast Path** (Simple/Standard charts with clear requirements):
1. Quick research (5-10 min)
2. Create chart directly using templates
3. Validate and create PR

**Full Workflow** (Complex charts or when extending):
1. Research Phase - Systematic investigation, plan, approve
2. Planning Phase - High-level plan, atomic components, issue mapping
3. Implementation Phase - Worktree, draft PR, sanity checks, submit

> **Details**: See `research-phase-workflow.md`, `planning-phase-workflow.md`, `implementation-workflow.md`

**When adapting/extending**: Review their `values.yaml` for configuration patterns, check `Chart.yaml` for dependency approach. See `extend-contribute-strategy.md` for compatibility checklist.

---

## Step 2: Gather Configuration Details

### Primary: Official Documentation

Use WebFetch or firecrawl on official docs:

```
https://docs.example.com/deployment
https://docs.example.com/configuration
https://docs.example.com/docker
https://docs.example.com/kubernetes
https://docs.example.com/helm
```

### Fallback: Documentation Scraping Fails

When docs return cookie consent, require JS, or are blocked:

#### 2a. Check Project's GitHub

```bash
# Dockerfile - image base, ports, entrypoint
gh api "repos/<org>/<project>/contents/Dockerfile" | jq -r '.content' | base64 -d

# docker-compose.yml - ports, env vars, volumes
gh api "repos/<org>/<project>/contents/docker-compose.yml" | jq -r '.content' | base64 -d

# Search for config examples
gh search code "environment:" --repo <org>/<project> --filename docker-compose

# Check for Kubernetes examples
gh search code "kind: Deployment" --repo <org>/<project>
```

#### 2b. Check Docker Hub / Container Registry

```bash
# Docker Hub - often has env vars documented
curl -s "https://hub.docker.com/v2/repositories/<org>/<image>/" | jq

# View image labels
docker pull <image>:<tag>
docker inspect <image>:<tag> | jq '.[0].Config.Labels'

# View exposed ports
docker inspect <image>:<tag> | jq '.[0].Config.ExposedPorts'

# View environment variables
docker inspect <image>:<tag> | jq '.[0].Config.Env'
```

#### 2c. Inspect Container Directly

```bash
# Help output often documents options
docker run --rm <image> --help
docker run --rm <image> help

# Check for config files
docker run --rm --entrypoint cat <image> /app/config.yaml
docker run --rm --entrypoint cat <image> /etc/app/config.yml
docker run --rm --entrypoint ls <image> /app/

# Check entrypoint script
docker run --rm --entrypoint cat <image> /entrypoint.sh
docker run --rm --entrypoint cat <image> /docker-entrypoint.sh
```

#### 2d. Search for Community Deployments

```bash
# Search GitHub for Kubernetes deployments
gh search code "image: <org>/<image>" --filename deployment.yaml

# Search for Helm values examples
gh search code "<project>" --filename values.yaml
```

---

## Step 3: Information Gathering Checklist

Collect this information before writing templates:

### Container Image

| Item | Source | Example |
|------|--------|---------|
| Registry | Docker Hub, GitHub Registry, custom | `docker.io`, `ghcr.io` |
| Repository | Image name | `openmetadata/server` |
| Tag pattern | Version format | `1.6.2`, `v1.6.2`, `latest` |
| Platforms | Architecture support | `linux/amd64`, `linux/arm64` |

### Ports

| Port | Purpose | Source |
|------|---------|--------|
| Main | Web UI / API | Dockerfile EXPOSE, docs |
| Admin | Health, metrics, management | Docs, docker-compose |
| Debug | Remote debugging | Docs (usually optional) |
| JMX | Java monitoring | Docs (usually optional) |

### Health Endpoints

| Probe | Endpoint | Port | Notes |
|-------|----------|------|-------|
| Liveness | `/healthcheck`, `/health`, `/healthz` | admin or main | Infrastructure health |
| Readiness | `/ready`, `/readyz`, `/` | main | App ready to serve |
| Startup | Same as liveness | admin | Slow-starting apps |

**Common patterns by framework:**

| Framework | Liveness | Readiness | Port |
|-----------|----------|-----------|------|
| Spring Boot | `/actuator/health/liveness` | `/actuator/health/readiness` | management |
| Dropwizard | `/healthcheck` | `/` | admin |
| Express.js | `/health` | `/ready` | main |
| Go stdlib | `/healthz` | `/readyz` | main |
| FastAPI | `/health` | `/` | main |

### Environment Variables

| Category | Examples |
|----------|----------|
| **Database** | `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DATABASE_URL` |
| **Search** | `ELASTICSEARCH_HOST`, `ES_JAVA_OPTS` |
| **Auth** | `AUTH_PROVIDER`, `OIDC_CLIENT_ID`, `JWT_SECRET` |
| **Logging** | `LOG_LEVEL`, `LOG_FORMAT` |
| **JVM** | `JAVA_OPTS`, `JAVA_TOOL_OPTIONS`, `HEAP_SIZE` |

### Resource Requirements

| Level | CPU | Memory | Source |
|-------|-----|--------|--------|
| Minimum | requests | requests | Docs, docker-compose |
| Recommended | limits | limits | Production guides |

### Dependencies

| Type | Service | Required? |
|------|---------|-----------|
| Database | MySQL, PostgreSQL | Yes/No |
| Search | Elasticsearch | Yes/No |
| Cache | Redis | Yes/No |
| Messaging | Kafka, Airflow | Yes/No |

---

## Step 4: Template: Information Summary

Use this template to document findings:

```markdown
## <Application> Helm Chart Research

### Image
- Registry: `<registry>`
- Repository: `<org>/<image>`
- Latest stable tag: `<version>`

### Ports
| Port | Purpose |
|------|---------|
| 8080 | Web UI |
| 8081 | Admin/Health |
| 9090 | Metrics |

### Health Endpoints
- Liveness: `GET /healthcheck` (port 8081)
- Readiness: `GET /` (port 8080)

### Required Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database hostname | - |
| `DB_PORT` | Database port | `3306` |

### Optional Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` |

### Dependencies
- [x] MySQL or PostgreSQL (required)
- [x] Elasticsearch (required)
- [ ] Redis (optional)

### Resources
- Recommended: 2 CPU, 4Gi memory
- Minimum: 500m CPU, 2Gi memory

### References
- Docs: <url>
- Docker Hub: <url>
- GitHub: <url>
```

---

## Troubleshooting

### Documentation Not Accessible

| Problem | Solution |
|---------|----------|
| Cookie consent blocking | Use GitHub/Docker Hub directly |
| JavaScript-rendered | Inspect container or GitHub |
| API docs only | Check for deployment guide section |
| Outdated docs | Check GitHub releases for recent changes |

### Can't Find Configuration

| Problem | Solution |
|---------|----------|
| No env vars documented | Inspect Dockerfile ENV, entrypoint script |
| No ports documented | Check Dockerfile EXPOSE |
| No health endpoints | Try common patterns: `/health`, `/healthz`, `/` |
| No resource recommendations | Start conservative, adjust based on testing |

### Multiple Conflicting Sources

| Problem | Solution |
|---------|----------|
| Docs say X, docker-compose says Y | Prefer docker-compose (tested config) |
| Old docs, new image | Check GitHub releases, CHANGELOG |
| Community examples vary | Check official examples first |
