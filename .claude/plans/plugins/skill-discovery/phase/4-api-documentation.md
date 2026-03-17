# Phase 4: API Documentation

## Objective

Document API access patterns, rate limits, and restrictions for all independent site registries.

## Duration

1 day (parallelizable with Phase 3)

## Dependencies

- Phase 2 (registry URLs identified)

---

## Scope

For each independent site registry discovered in Phase 2:

1. API endpoint discovery
2. Authentication requirements
3. Rate limit documentation
4. robots.txt analysis
5. Terms of Service review

---

## Experiment: API Endpoint Discovery

Create: `analysis/experiments/5-api-discovery.md`

```yaml
experiment:
  id: "exp-005-api-discovery"
  title: "Discover and document registry APIs"

  inputs:
    registries: # All from Phase 2 discoveries

  procedure:
    - step: 1
      action: "Check common API paths"
      paths:
        - "/api"
        - "/api/v1"
        - "/docs/api"
        - "/swagger"
        - "/openapi.json"
        - "/.well-known/api"
      expected: "API documentation or 404"

    - step: 2
      action: "Analyze documentation"
      expected: "List of endpoints"

    - step: 3
      action: "Test search endpoint"
      expected: "Response format"

    - step: 4
      action: "Check authentication"
      expected: "Auth method or 'none'"
```

---

## Experiment: Restriction Analysis

Create: `analysis/experiments/6-restriction-analysis.md`

```yaml
experiment:
  id: "exp-006-restrictions"
  title: "Analyze scraping restrictions per registry"

  procedure:
    - step: 1
      action: "Fetch robots.txt"
      expected: "Allow/Disallow rules"

    - step: 2
      action: "Check response headers for rate limits"
      headers:
        - "X-RateLimit-Limit"
        - "X-RateLimit-Remaining"
        - "Retry-After"
      expected: "Rate limit values"

    - step: 3
      action: "Find Terms of Service"
      paths:
        - "/terms"
        - "/tos"
        - "/legal"
      expected: "ToS URL"

    - step: 4
      action: "Analyze ToS for API/scraping policy"
      expected: "Policy summary"
```

---

## Result Schema

```yaml
# analysis/results/registry-api-{name}.yaml
registry_api:
  name: "skillsmp"
  base_url: "https://skillsmp.com"

  api:
    docs_url: "https://skillsmp.com/docs/api"
    spec_format: "openapi|swagger|custom|none"
    authentication:
      type: "api_key|oauth|none"
      header: "Authorization"
      signup_url: ""
    endpoints:
      - path: "/api/v1/skills"
        method: "GET"
        params: ["query", "category", "page", "limit"]
        response_format: "json"
      - path: "/api/v1/skills/{id}"
        method: "GET"
        response_format: "json"

  restrictions:
    robots_txt:
      url: "https://skillsmp.com/robots.txt"
      user_agent: "*"
      allowed: ["/api/*", "/skills/*"]
      disallowed: ["/admin/*", "/internal/*"]
      crawl_delay: 1

    rate_limits:
      documented: "100 req/min"
      observed_header: "X-RateLimit-Limit: 100"
      retry_after: "60s"

    terms_of_service:
      url: "https://skillsmp.com/terms"
      scraping_policy: "allowed with attribution"
      api_policy: "free tier available"
      commercial_use: "contact required"

  observations:
    - "API well-documented with OpenAPI spec"
    - "Free tier sufficient for discovery"
```

---

## Aggregated Report

Compile into summary:

```yaml
# analysis/reports/registry-apis.yaml
summary:
  total_registries: 15
  with_api_docs: 10
  with_search_api: 8
  requiring_auth: 3
  rate_limited: 12
  allow_scraping: 14

registries:
  - name: "skillsmp"
    api: true
    search: true
    auth_required: false
    rate_limit: "100/min"
    scraping: "allowed"

  - name: "ccpm"
    api: true
    search: true
    auth_required: false
    rate_limit: "unknown"
    scraping: "allowed"
  # ...

recommendations:
  - "Use skillsmp API for primary skill search"
  - "Implement rate limiting for ccpm (undocumented)"
  - "Avoid scraping admin paths on all registries"
```

---

## Deliverables

| File | Purpose |
|------|---------|
| `analysis/results/registry-api-{name}.yaml` | Per-registry API docs |
| `analysis/reports/registry-apis.yaml` | Summary report |

---

## Success Gate

| Criterion | Target |
|-----------|--------|
| Registries analyzed | All from Phase 2 |
| API documentation coverage | 80%+ |
| robots.txt checked | 100% |
| Rate limits documented | 100% |
| ToS reviewed | 100% |

## Checklist

Use: `checklists/schemas/data-validation.schema.json`

Record: `checklists/instances/phase-4.json`
