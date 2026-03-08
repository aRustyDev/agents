# Experiment 2: Registry Probe

## Metadata

```yaml
experiment:
  id: "exp-002-registry-probe"
  title: "Test registry accessibility and features"
  created: "2026-03-08"
  status: "defined"
  hypothesis: "Registries vary in API availability and crawlability"
```

## Objective

Assess each known registry for:

- Accessibility (HTTP status, content type)
- API availability (documented endpoints)
- Crawl permissions (robots.txt)
- Search capability (web search, API search)

## Registries to Probe

### High Priority (10)

| Registry | URL | Expected Features |
|----------|-----|-------------------|
| skillsmp | <https://skillsmp.com/> | search, api, browse |
| smithery | <https://smithery.ai/> | search, api |
| ccpm | <https://ccpm.dev/> | search, install |
| claude-plugins.dev | <https://claude-plugins.dev/> | search, browse |
| agentskills.best | <https://agentskills.best/> | search, browse |
| mcp.so | <https://mcp.so/> | search, api |
| mcpservers.org | <https://mcpservers.org/> | search, browse |
| glama | <https://glama.ai/mcp/servers> | search, api |
| claudemarketplaces | <https://claudemarketplaces.com/> | browse |
| claudecodemarketplace | <https://claudecodemarketplace.com/> | browse |

### Medium Priority (5)

| Registry | URL |
|----------|-----|
| claudeskillsmarket | <https://claudeskillsmarket.com/> |
| atcyrus | <https://www.atcyrus.com/skills> |
| awesome-claude-code.com | <https://awesome-claude-code.com/> |
| awesomeclaude.ai | <https://awesomeclaude.ai/> |
| lobehub | <https://lobehub.com/> |

## Probe Procedure

For each registry:

### Step 1: Homepage Probe

```yaml
action: "Fetch homepage"
tool: "WebFetch"
check:
  - HTTP status code
  - Content type
  - Page title
  - Has search input
  - Has skill/plugin listings
```

### Step 2: API Discovery

```yaml
action: "Check for API documentation"
paths_to_try:
  - "/api"
  - "/api/v1"
  - "/docs/api"
  - "/api-docs"
  - "/swagger"
  - "/openapi.json"
check:
  - API docs present
  - Endpoints listed
  - Auth required
```

### Step 3: Robots.txt

```yaml
action: "Fetch robots.txt"
url: "{base_url}/robots.txt"
extract:
  - User-agent rules
  - Allowed paths
  - Disallowed paths
  - Crawl-delay
  - Sitemap URLs
```

### Step 4: Search Test

```yaml
action: "Test search functionality"
query: "typescript"
methods:
  - Web UI search (if available)
  - API search (if documented)
check:
  - Returns results
  - Result format (JSON, HTML)
  - Pagination support
```

## Output Template

```yaml
# analysis/results/registry-probe-{name}.yaml
result:
  experiment_id: "exp-002-registry-probe"
  registry: "{name}"
  url: "{url}"
  probed_at: "{timestamp}"

  homepage:
    status: 200
    content_type: "text/html"
    title: "..."
    has_search: true
    has_listings: true
    js_rendered: false

  api:
    available: true
    docs_url: "..."
    endpoints:
      - path: "/api/v1/skills"
        method: "GET"
        auth: "none"
    rate_limit: "100/min"

  robots_txt:
    exists: true
    allows: ["/api/*", "/skills/*"]
    disallows: ["/admin/*"]
    crawl_delay: 1
    sitemaps: ["https://.../sitemap.xml"]

  search:
    web_ui: true
    api: true
    test_query: "typescript"
    results_count: 25
    result_format: "json"

  assessment:
    crawlable: true
    api_usable: true
    recommended_tool: "WebFetch"
    notes: "..."
```

## Output Files

One file per registry:

- `analysis/results/registry-probe-skillsmp.yaml`
- `analysis/results/registry-probe-smithery.yaml`
- ... (15 total)

## Success Criteria

- 10+ registries probed (all high priority)
- API availability documented for each
- robots.txt analyzed for each
- Search capability tested
- Recommended tool identified per registry
