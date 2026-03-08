# Phase 1: Search Tool Experiments

## Objective

Compare search tools to determine effectiveness per source type.

## Duration

1 day

## Dependencies

- Phase 0 (search term matrix, baseline)

---

## Tools Under Test

| Tool | Type | Best For | Cost |
|------|------|----------|------|
| `WebSearch` | Claude native | Quick web search | Free |
| `WebFetch` | Claude native | Static page scraping | Free |
| `gh api` | GitHub CLI | Repo/code search | Free |
| `crawl4ai` MCP | JS-rendered | SPAs, dynamic content | Free |
| `firecrawl` MCP | Batch crawl | Large-scale scraping | $ |
| SearXNG | Meta-search | Privacy-respecting, aggregated | Free (self-host) |

---

## Experiment 1: Tool Comparison

### Definition

Create: `analysis/experiments/1-tool-comparison.md`

```yaml
experiment:
  id: "exp-001-tool-comparison"
  title: "Compare search tools on standard queries"
  hypothesis: "Different tools excel at different source types"

  inputs:
    tools: ["WebSearch", "WebFetch", "gh api", "crawl4ai"]
    queries:
      - '"claude code skill" site:github.com'
      - '"awesome-claude" skills'
      - 'mcp server claude'
      - '"SKILL.md" claude'
      - 'claude plugin marketplace'

  metrics:
    - name: "recall"
      target: 0.8
    - name: "precision"
      target: 0.9
    - name: "latency_ms"
      target: 5000
    - name: "rate_limit_hit"
      target: false
```

### Procedure

For each tool × query combination:

1. Execute query
2. Record:
   - Response time
   - Number of results
   - Rate limit status
   - Error (if any)
3. Store in `analysis/results/tool-comparison-{tool}.yaml`

### Result Template

```yaml
# analysis/results/tool-comparison-websearch.yaml
result:
  experiment_id: "exp-001-tool-comparison"
  timestamp: "2026-03-08T10:00:00Z"

  raw_data:
    tool: "WebSearch"
    queries:
      - query: '"claude code skill" site:github.com'
        response_time_ms: 1200
        items_found: 15
        rate_limited: false
        items:
          - url: "https://github.com/..."
            title: "..."
```

---

## Experiment 2: Registry Probe

### Definition

Create: `analysis/experiments/2-registry-probe.md`

```yaml
experiment:
  id: "exp-002-registry-probe"
  title: "Test registry accessibility and features"

  inputs:
    registries:
      - url: "https://skillsmp.com/"
        expected_features: ["search", "api", "browse"]
      - url: "https://ccpm.dev/"
        expected_features: ["search", "install"]
      # ... all known registries

  procedure:
    - step: 1
      action: "Fetch homepage with WebFetch"
      expected: "200 OK, content about skills"
    - step: 2
      action: "Check for /docs/api or /api/v1"
      expected: "API documentation or 404"
    - step: 3
      action: "Fetch robots.txt"
      expected: "Crawl rules"
    - step: 4
      action: "Test search if available"
      expected: "Search results"
```

### Result Template

```yaml
# analysis/results/registry-probe-skillsmp.yaml
result:
  experiment_id: "exp-002-registry-probe"
  registry: "skillsmp"

  raw_data:
    homepage:
      status: 200
      title: "SkillsMP - Claude Skills Marketplace"
      has_search: true
    api:
      docs_url: "https://skillsmp.com/docs/api"
      endpoints_found: ["/api/v1/skills", "/api/v1/search"]
    robots_txt:
      url: "https://skillsmp.com/robots.txt"
      allows: ["/api/*"]
      disallows: ["/admin/*"]
      crawl_delay: 1
    rate_limits:
      documented: "100 req/min"
      observed: null
```

---

## Analysis

After experiments complete, create finding:

```yaml
# analysis/findings/tool-effectiveness.yaml
finding:
  id: "finding-001-tool-effectiveness"
  title: "Best search tools by source type"

  claim: "gh api is best for GitHub, WebSearch for general web"
  confidence: "high"

  experiment_ids: ["exp-001-tool-comparison"]

  supporting_data:
    - source: "analysis/results/tool-comparison-ghapi.yaml"
      data_point: "recall: 0.95 on GitHub queries"
    - source: "analysis/results/tool-comparison-websearch.yaml"
      data_point: "recall: 0.85 on web queries"

  recommendations:
    - "Use gh api for all GitHub searches"
    - "Use WebSearch for registry discovery"
    - "Use crawl4ai for JS-rendered registry pages"
```

---

## Deliverables

| File | Purpose |
|------|---------|
| `analysis/experiments/1-tool-comparison.md` | Experiment definition |
| `analysis/experiments/2-registry-probe.md` | Experiment definition |
| `analysis/results/tool-comparison-*.yaml` | Raw results per tool |
| `analysis/results/registry-probe-*.yaml` | Raw results per registry |
| `analysis/findings/tool-effectiveness.yaml` | Analysis |

---

## Success Gate

| Criterion | Target |
|-----------|--------|
| Tools tested | 6/6 |
| Queries per tool | 5/5 |
| Registries probed | 10+ |
| Best tool identified per source type | Yes |
| Rate limits documented | Yes |

## Checklist

Use: `checklists/schemas/research-execution.schema.json`

Record: `checklists/instances/phase-1.json`
