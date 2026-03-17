# Experiment 5: Output Quality Comparison

## Metadata

```yaml
experiment:
  id: "exp-005-output-quality"
  title: "Compare output quality across tools on same registries"
  created: "2026-03-08"
  status: "pending"
  hypothesis: "Different tools produce different quality outputs on same target"
```

## Objective

Run ALL available tools against the SAME registries and compare:
1. Content structure (JSON vs markdown vs HTML)
2. Completeness (what fields are captured)
3. Parseability (ease of programmatic extraction)
4. Accuracy (correct data values)

## Tools Under Test

| Tool | Type | Expected Strength |
|------|------|-------------------|
| WebFetch | Claude native | Fast, reliable for static |
| WebSearch | Claude native | Discovery |
| crawl4ai (crawl_url) | MCP | JS rendering, structured extraction |
| crawl4ai (deep_crawl) | MCP | Recursive crawling |
| crawl4ai (extract_links) | MCP | Link discovery |
| SearXNG | Local | Meta-search aggregation |
| gh api | CLI | Structured GitHub data |

## Test Registries (3 Types)

### Type A: Static HTML Registry

```yaml
registry: "buildwithclaude.com"
url: "https://buildwithclaude.com/skills"
characteristics:
  - Static HTML
  - Well-structured
  - No auth required
tools_to_test:
  - WebFetch
  - crawl4ai (crawl_url)
  - SearXNG (for discovery)
```

### Type B: JS-Heavy Registry

```yaml
registry: "mcp.so"
url: "https://mcp.so/"
characteristics:
  - Heavy JavaScript
  - Dynamic loading
  - No auth required
tools_to_test:
  - WebFetch (baseline - expected to fail)
  - crawl4ai (crawl_url)
  - crawl4ai (deep_crawl)
```

### Type C: Protected Registry

```yaml
registry: "skillsmp.com"
url: "https://skillsmp.com/"
characteristics:
  - Cloudflare protection
  - API available
  - Auth required for API
tools_to_test:
  - WebFetch (expected: 403)
  - crawl4ai (crawl_with_auth)
  - API (curl with Bearer)
```

## Comparison Matrix

For each (tool × registry) combination, record:

```yaml
comparison_fields:
  - tool_name
  - registry
  - success: true/false
  - response_time_ms
  - content_length_bytes
  - structure_score: 1-5
  - completeness_score: 1-5
  - parseability_score: 1-5
  - items_extracted: count
  - sample_item: first item
  - fields_captured: [name, url, description, stars, ...]
  - fields_missing: [expected but not found]
  - raw_sample: first 300 chars
```

## Scoring Rubric

### Structure Score (1-5)

| Score | Criteria |
|-------|----------|
| 5 | Returns structured JSON with consistent schema |
| 4 | Returns well-formatted markdown with clear sections |
| 3 | Returns parseable HTML with semantic tags |
| 2 | Returns mixed/inconsistent format |
| 1 | Returns raw text or fails |

### Completeness Score (1-5)

| Score | Criteria |
|-------|----------|
| 5 | All expected fields present (name, url, desc, author, stars) |
| 4 | 4/5 fields present |
| 3 | 3/5 fields present |
| 2 | 2/5 fields present |
| 1 | Only 1 or 0 fields present |

### Parseability Score (1-5)

| Score | Criteria |
|-------|----------|
| 5 | Direct JSON, no parsing needed |
| 4 | Consistent pattern, simple regex/split |
| 3 | Needs HTML parser (BeautifulSoup) |
| 2 | Needs complex NLP/extraction |
| 1 | Unparseable without LLM |

## Success Criteria

- [ ] All tools tested on Type A registry
- [ ] JS-capable tools tested on Type B registry
- [ ] Protected registry tested with multiple approaches
- [ ] Scores recorded for all combinations
- [ ] Clear winner identified per registry type

## Output Files

- `analysis/results/quality-comparison/buildwithclaude-matrix.yaml`
- `analysis/results/quality-comparison/mcpso-matrix.yaml`
- `analysis/results/quality-comparison/skillsmp-matrix.yaml`
- `analysis/findings/tool-quality-ranking.yaml`
