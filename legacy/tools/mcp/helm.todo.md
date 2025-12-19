## MCP

### Tools

- "search"
  - ast-grep
  - ref
  - duckduckgo
  - context7
  - astro-docs
  - cloudflare-docs
  - dockerhub
  - github
  - gitlab
- "control"
  - dockerhub
  - github
  - gitlab
  - git
  - gitea
  - airtable
- "memory" | "context"
  - graphiti
- "process" | "compute"
  - fetch
  - ollama
  - time
  - math
- "plan" | "think"
  - taskorchestrator
  - sequentialthinking
  - chain-of-thought

### Domains

- arusty.dev : Landing Page
- just.arusty.dev : Justfile static endpoints
- schemas.arusty.dev : Schema hosting
  <!--- https://dev.to/nikl/json-is-slower-here-are-its-4-faster-alternatives-2g30 -->
  <!-- https://json-schema.org/overview/similar-technologies -->
  <!-- https://rocketfiles.com/blog/json-alternative -->
  <!-- https://github.com/colinhacks/zod -->
  - /json
  - /proto
  - /bson
  - /msgpk (message pack)
  - /avro
  - CBOR Constrained Data Description Language (CBL)
  - CBOR Data Definition Language (Cddl)
  - flatbuffers
  - JSON Constraint Rules (JCR)
- blog.arusty.dev : Personal blog site
- git.arusty.dev : Private Git hosting
- id.arusty.dev : Private OAuth2 / OpenID Connect Identity Provider
- auth.arusty.dev : Private AuthZed Authorization Provider
- docs.arusty.dev : Documentation Site for all my projects
- logs.arusty.dev : Logging Aggregation endpoints
  - /ui : Loki Log Explorer UI
- metrics.arusty.dev : Prometheus endpoints
  - /ui : Prometheus + Grafana dashboards
- otel.arusty.dev : OpenTelemetry Collector endpoint
  - /ui : Tempo Trace Explorer UI
- mcp.arusty.dev
  - /search
    - (Header) kind: [code,docs,tasks,refs,issues]
  - /context
  - /plan
  - /compute
  - /feedback
  - /rag
  - /status: service status and metrics
- ai.arusty.dev
  - /ui
    - /plan
    - /chats
    - /projects
    - /specs
  - /static
    - /rules
    - /prompts
    - /agents
    - /templates
    - /specs
    - /skills
    - /roles
    - /hooks
    - /output
      - /styles
      - /templates
      - /formats
  - /plugins
  - /status: SPA that calls /api/v1/get_status
  - /api/v1
    - build_plugin: dynamically builds plugin from available static resources
    - get_status: service status and metrics
- arusty.dev
  - /status: SPA that calls /api/v1/public/get_status
  - /about
  - /contact
  - /api/v1/public
    - get_status: service status and metrics

## Core

- Secrets:
  - externalsecrets
- DNS:
  - externaldns (Manages Cloudflare & Local DNS)
- Certificates:
  - cert-manager
  - step-ca
- Service Mesh:
  - linkerd
- Ingress:
  - traefik || API6
