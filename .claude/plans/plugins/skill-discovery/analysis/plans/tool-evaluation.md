# Analysis Plan: Tool Evaluation

## Objective

Determine the best search tool for each source type based on experimental results.

## Scope

Evaluate search tools across:
- Independent site registries
- GitHub repositories
- Package managers (npm, PyPI, crates.io)

---

## Tools Under Evaluation

| Tool | Source Types | Strengths |
|------|--------------|-----------|
| WebSearch | General web | Broad coverage |
| WebFetch | Static sites | Fast, direct |
| crawl4ai | JS-rendered sites | Handles SPAs |
| firecrawl | Large-scale crawls | Rate limiting |
| gh api | GitHub | Official API |
| npm search | npm packages | Package-specific |
| PyPI API | Python packages | Package-specific |

---

## Evaluation Criteria

| Criterion | Weight | Measurement |
|-----------|--------|-------------|
| Recall | 0.30 | % of baseline found |
| Precision | 0.25 | % relevant in results |
| Latency | 0.20 | Avg query time |
| Rate limits | 0.15 | Requests before throttle |
| Cost | 0.10 | API costs if any |

---

## Analysis Process

### Step 1: Collect Experiment Results

Gather from Phase 1 experiments:
- `analysis/results/tool-comparison-*.yaml`
- `analysis/results/registry-probe-*.yaml`

### Step 2: Score Each Tool

For each tool × source type combination:

```yaml
tool_score:
  tool: "WebSearch"
  source_type: "registry"
  recall: 0.85
  precision: 0.72
  latency_ms: 1200
  rate_limit: "100/day"
  cost: "$0"
  weighted_score: 0.78
```

### Step 3: Rank and Recommend

Create recommendation matrix:

```yaml
recommendations:
  registry:
    primary: "WebFetch"
    fallback: "crawl4ai"
    rationale: "Most registries are static; crawl4ai for JS-heavy"

  github:
    primary: "gh api"
    fallback: "WebSearch"
    rationale: "Official API has best precision and rate limits"

  packages:
    npm:
      primary: "npm search CLI"
      rationale: "Direct API access"
    pypi:
      primary: "PyPI JSON API"
      rationale: "No rate limits, structured data"
```

---

## Deliverables

| File | Purpose |
|------|---------|
| `analysis/results/tool-scores.yaml` | Raw scores per tool |
| `analysis/findings/tool-recommendations.yaml` | Final recommendations |
| `analysis/reports/tool-evaluation.md` | Summary report |

---

## Success Criteria

- [ ] All 6 tools evaluated
- [ ] Scores computed for all criteria
- [ ] Primary tool identified for each source type
- [ ] Fallback strategy documented
