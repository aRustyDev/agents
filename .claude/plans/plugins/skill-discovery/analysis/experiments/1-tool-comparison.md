# Experiment 1: Tool Comparison

## Metadata

```yaml
experiment:
  id: "exp-001-tool-comparison"
  title: "Compare search tools on standard queries"
  created: "2026-03-08"
  status: "defined"
  hypothesis: "Different tools excel at different source types"
```

## Objective

Determine which search tool performs best for each source type (GitHub, web registries, package managers).

## Tools Under Test

| Tool | Type | Expected Strength |
|------|------|-------------------|
| `WebSearch` | Claude native | General web discovery |
| `WebFetch` | Claude native | Static page content |
| `gh api` | GitHub CLI | Repository and code search |
| `crawl4ai` | MCP server | JavaScript-rendered pages |

## Standard Queries

```yaml
queries:
  - id: "q1-github-skills"
    query: '"claude skill" site:github.com'
    target: "GitHub skill repositories"
    expected_results: 10+

  - id: "q2-awesome-lists"
    query: '"awesome-claude" skills'
    target: "Curated awesome lists"
    expected_results: 5+

  - id: "q3-mcp-servers"
    query: '"mcp server" claude registry'
    target: "MCP server registries"
    expected_results: 5+

  - id: "q4-skill-files"
    query: 'filename:SKILL.md claude'
    target: "SKILL.md files on GitHub"
    expected_results: 20+
    github_only: true

  - id: "q5-plugin-marketplace"
    query: '"claude plugin" marketplace'
    target: "Plugin marketplaces"
    expected_results: 3+
```

## Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| `results_count` | Number of results returned | Varies by query |
| `response_time_ms` | Time to get results | < 5000ms |
| `rate_limited` | Whether rate limit was hit | false |
| `error` | Any error encountered | null |
| `relevance_score` | Manual assessment 1-5 | >= 4 |

## Procedure

For each (tool, query) combination:

1. Record start timestamp
2. Execute query using tool
3. Record end timestamp
4. Count results
5. Check for rate limiting or errors
6. Sample 3 results for relevance assessment
7. Store in `analysis/results/tool-comparison-{tool}.yaml`

## Output Files

- `analysis/results/tool-comparison-websearch.yaml`
- `analysis/results/tool-comparison-webfetch.yaml`
- `analysis/results/tool-comparison-ghapi.yaml`
- `analysis/results/tool-comparison-crawl4ai.yaml`

## Success Criteria

- All 4 tools tested
- All 5 queries executed per tool (where applicable)
- Response times recorded
- Rate limit behavior documented
- Clear winner identified per source type
