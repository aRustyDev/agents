# MCP Server Relevance Assessment

This document describes how relevance scores are determined when evaluating MCP servers against a stated need or domain.

## Overview

When profiling an MCP server, the `mcp-server-profiler` agent calculates two key metrics:

| Metric | Range | Description |
|--------|-------|-------------|
| `relevance_score` | 0-100 | How well the server's capabilities match the stated need |
| `coverage_pct` | 0-100% | What percentage of the need is satisfied by this server |

These metrics inform the `recommendation` field: `reuse`, `extend`, or `create`.

## Relevance Scoring Criteria

### 1. Feature Matching (40 points)

The profiler extracts feature tags from the server's README and documentation, then calculates:

```
feature_score = (matching_keywords / total_need_keywords) × 40
```

**Example:**
- Need: "code analysis, AST parsing, security scanning"
- Server features: "ast-parsing, code-analysis, linting, refactoring"
- Matching: 2/3 keywords → `(2/3) × 40 = 26.7 points`

### 2. Maintenance Quality (25 points)

Assessed from GitHub repository signals:

| Signal | Criteria | Points |
|--------|----------|--------|
| **Stars** | >100 | 10 |
| | 50-100 | 7 |
| | 10-50 | 4 |
| | 1-10 | 2 |
| | 0 or unknown | 0 |
| **Recency** | <3 months since last commit | 15 |
| | 3-6 months | 10 |
| | 6-12 months | 5 |
| | >12 months | 2 |
| | Unknown | 0 |

### 3. Installation Ease (20 points)

| Install Method | Points | Rationale |
|----------------|--------|-----------|
| `brew` | 20 | Single command, managed updates |
| `npx` | 18 | No install needed, auto-fetches |
| `pip` / `uvx` | 15 | Requires Python environment |
| `docker` | 10 | Requires Docker runtime |
| `manual` | 5 | Clone, build, configure |

### 4. Tool Coverage (15 points)

Based on the number of MCP tools the server exposes:

```
tool_score = min(tool_count, 10) / 10 × 15
```

Servers with 10+ tools receive full points. This rewards comprehensive functionality.

## Coverage Percentage

Coverage represents how much of the stated need is satisfied:

| Coverage | Interpretation |
|----------|----------------|
| 90-100% | Server fully satisfies the need |
| 70-89% | Minor gaps, may need supplementation |
| 50-69% | Significant gaps, consider alternatives |
| <50% | Poor match, likely need different server |

### Calculation Method

The profiler evaluates coverage by:

1. **Decomposing the need** into atomic capabilities
2. **Mapping each capability** to server tools/features
3. **Scoring gaps** for missing functionality
4. **Weighting** by importance (core vs. nice-to-have)

**Example:**

Need: "code indexing with semantic search"

| Capability | Weight | Server Has? | Score |
|------------|--------|-------------|-------|
| File indexing | 40% | Yes | 40% |
| Symbol extraction | 30% | Yes | 30% |
| Semantic search | 20% | No | 0% |
| Incremental updates | 10% | Yes | 10% |
| **Total** | | | **80%** |

## Recommendation Logic

Based on scores, the profiler recommends an action:

| Recommendation | Criteria | Action |
|----------------|----------|--------|
| `reuse` | relevance ≥ 80, coverage ≥ 70% | Use as-is |
| `extend` | relevance ≥ 60, coverage 50-70% | Fork and add features |
| `create` | relevance < 60 OR coverage < 50% | Build new server |

## Database Storage

Assessments are stored in `mcp_server_assessments`:

```sql
INSERT INTO mcp_server_assessments (
  server_id, domain, relevance_score, coverage_pct,
  recommendation, notes, assessed_at
) VALUES (
  <entity_id>,
  'code analysis and indexing',  -- the stated need
  92.5,                          -- relevance score
  85.0,                          -- coverage percentage
  'reuse',                       -- recommendation
  'Excellent match. Covers all core requirements...',
  datetime('now')
);
```

## Querying Assessments

Find servers that best match a domain:

```sql
SELECT e.name, e.slug, a.relevance_score, a.coverage_pct, a.recommendation
FROM mcp_server_assessments a
JOIN entities e ON a.server_id = e.id
WHERE a.domain LIKE '%code analysis%'
ORDER BY a.relevance_score DESC;
```

## Limitations

Current assessment limitations:

1. **Subjective weighting**: Feature matching depends on keyword extraction quality
2. **No runtime validation**: Scores based on documentation, not actual testing
3. **Single-point-in-time**: Assessments may become stale as servers evolve
4. **Domain-specific**: A server may score differently for different needs

## Future Improvements

Planned enhancements to relevance scoring:

- [ ] Semantic similarity using embeddings instead of keyword matching
- [ ] Runtime capability probing via MCP introspection
- [ ] User feedback integration for score calibration
- [ ] Automated re-assessment on repository updates
