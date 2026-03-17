# Experiment 7: SearXNG Integration

## Metadata

```yaml
experiment:
  id: "exp-007-searxng"
  title: "Integrate and evaluate SearXNG for meta-search"
  created: "2026-03-08"
  status: "pending"
  prerequisite: "SearXNG running on localhost:8888 with JSON format enabled"
  hypothesis: "SearXNG aggregates results from multiple engines for better coverage"
```

## Objective

Evaluate SearXNG as a meta-search tool for:
1. Registry discovery (finding new registries)
2. Component search (finding specific skills/agents)
3. Comparison with WebSearch

## SearXNG Configuration

```yaml
endpoint: "http://localhost:8888/search"
format: "json"
enabled_engines:
  - google
  - brave
  - duckduckgo
  - startpage
  - wikipedia
```

## Test Cases

### Test 1: Basic Search

```yaml
test_id: "sxng-001-basic"
query: "claude code skills"
parameters:
  q: "claude code skills"
  format: "json"
expected:
  - Returns JSON array of results
  - Results from multiple engines
  - Includes url, title, content
```

### Test 2: Registry Discovery

```yaml
test_id: "sxng-002-registry"
query: "claude skill marketplace registry"
parameters:
  q: "claude skill marketplace registry"
  format: "json"
compare_to:
  - WebSearch
expected:
  - Finds buildwithclaude.com
  - Finds skillsmp.com
  - Finds ccpm.dev
  - More results than single-engine search
```

### Test 3: MCP Server Search

```yaml
test_id: "sxng-003-mcp"
query: "mcp server model context protocol registry"
parameters:
  q: "mcp server model context protocol registry"
  format: "json"
expected:
  - Finds mcp.so
  - Finds glama.ai
  - Finds mcpservers.org
```

### Test 4: Specific Component Search

```yaml
test_id: "sxng-004-component"
query: '"SKILL.md" typescript github'
parameters:
  q: '"SKILL.md" typescript github'
  format: "json"
expected:
  - Finds GitHub repositories with SKILL.md
  - TypeScript-focused skills
```

### Test 5: Engine Comparison

```yaml
test_id: "sxng-005-engines"
queries:
  - "claude code skills"
  - "mcp server registry"
  - "awesome claude code"
analyze:
  - Which engines provide best results?
  - Result overlap between engines
  - Unique results per engine
```

### Test 6: Rate Limiting Test

```yaml
test_id: "sxng-006-ratelimit"
action: "Execute 10 searches in rapid succession"
queries:
  - "claude skills 1"
  - "claude skills 2"
  - ... (10 total)
measure:
  - Responses per second
  - Any rate limiting errors
  - Average response time
```

## Integration Pattern

### curl Command Template

```bash
# Basic search
curl -s "http://localhost:8888/search?q=QUERY&format=json" | jq '.results[]'

# With specific engines
curl -s "http://localhost:8888/search?q=QUERY&format=json&engines=google,brave" | jq '.results[]'

# Parse results
curl -s "http://localhost:8888/search?q=claude+skills&format=json" | \
  jq -r '.results[] | "\(.title)\t\(.url)"'
```

### Result Schema

```yaml
searxng_result:
  query: "string"
  number_of_results: number
  results:
    - url: "string"
      title: "string"
      content: "string"
      engine: "string"
      engines: ["string"]  # if found by multiple
      positions: [number]  # rank in each engine
      score: number
      category: "string"
      publishedDate: "string|null"
```

## Comparison Metrics

| Metric | SearXNG | WebSearch |
|--------|---------|-----------|
| Results per query | 20-30+ | ~10 |
| Unique sources | Multiple engines | Single |
| Response time | ? | ~1-2s |
| Rate limits | Local (none) | API |
| Cost | Free | Free |

## Success Criteria

- [ ] JSON API working reliably
- [ ] 6 test cases executed
- [ ] Response times < 5 seconds
- [ ] Results from multiple engines
- [ ] Clear comparison with WebSearch

## Output Files

- `analysis/results/searxng/test-001-basic.yaml`
- `analysis/results/searxng/test-002-registry.yaml`
- `analysis/results/searxng/test-003-mcp.yaml`
- `analysis/results/searxng/test-004-component.yaml`
- `analysis/results/searxng/test-005-engines.yaml`
- `analysis/results/searxng/test-006-ratelimit.yaml`
- `analysis/findings/searxng-evaluation.yaml`
