# Skill Discovery Research Plan

## Goal

Identify and document all available methods for discovering Claude Code skills from community sources, including registries, GitHub patterns, and web crawling strategies.

## Ownership

**Executor:** Single agent/developer
**Stakeholder:** Plugin ecosystem maintainers

---

## Phase 0: Baseline Creation

> **Purpose:** Establish ground truth for validation

### 0.1 Manual Skill Curation

Manually identify and document 20+ known community skills as baseline:

| Source | Expected Count | Method |
|--------|----------------|--------|
| This repo (`context/skills/`) | 10+ | Local inventory |
| awesome-claude-code repo | 5+ | Manual review |
| Known community repos | 5+ | Manual search |

### 0.2 Baseline Schema

```yaml
baseline_skills:
  - name: "skill-name"
    source_url: "https://github.com/..."
    category: "cli-tools|languages|frameworks|workflows"
    quality: "high|medium|low"
    last_verified: "2024-01-01"
```

### 0.3 Deliverables

- `baseline-skills.yaml` - Curated list of known skills
- Baseline count for validation metrics

### 0.4 Success Gate

- [ ] 20+ skills documented with URLs
- [ ] Categories assigned to all skills

---

## Phase 1: Registry Discovery

> **Methodology Note:** ALWAYS verify registry URLs directly with WebFetch before
> concluding they don't exist. GitHub search alone is insufficient.

### 1.1 Verified Skill Registries

| Registry | URL | Status | Notes |
|----------|-----|--------|-------|
| skillsmp | <https://skillsmp.com/> | Active | 2000+ skills, largest search engine |
| ccpm | <https://ccpm.dev/> | Active | Claude Code Package Manager |
| claude-plugins.dev | <https://claude-plugins.dev/> | Active | Community plugin registry |
| agentskills.best | <https://agentskills.best/> | Active | Enterprise-grade, quality-controlled |
| claudeskillsmarket | <https://claudeskillsmarket.com/> | Active | Community-powered registry |
| claudecodemarketplace | <https://claudecodemarketplace.com/> | Active | Plugins + Agent Skills hub |
| mcpservers.org/skills | <https://mcpservers.org/claude-skills> | Active | MCP-integrated skills |
| atcyrus | <https://www.atcyrus.com/skills> | Active | DevOps, security, docs skills |
| awesome-claude-code.com | <https://awesome-claude-code.com/> | Active | Web-based curated list |
| awesomeclaude.ai | <https://awesomeclaude.ai/> | Active | AI-focused aggregator |

### 1.2 Package Manager Registries

| Registry | URL | Search Pattern | Notes |
|----------|-----|----------------|-------|
| npm | <https://npmjs.com> | `claude-code-skill`, `claude-skill` | JS/TS skills |
| PyPI | <https://pypi.org> | `claude-skill`, `claude-code` | Python skills |
| crates.io | <https://crates.io> | `claude` | Rust-based tools |
| Smithery | <https://smithery.ai> | MCP servers | Companion skills |

### 1.3 Research Tasks

- [ ] Fetch each registry homepage and document API patterns
- [ ] Test search functionality on each registry
- [ ] Document authentication requirements (if any)
- [ ] Identify rate limits per registry
- [ ] Search npm/PyPI/crates.io for skill packages

### 1.3 Rate Limit Strategy

| Registry | Rate Limit | Strategy |
|----------|------------|----------|
| npm | 1000/hr | Cache results for 24h |
| PyPI | 100/min | 1 req/sec with backoff |
| crates.io | 1/sec | Sequential with delay |
| GitHub | 5000/hr (authenticated) | Use token, batch queries |

### 1.4 Fallback Strategy

```text
IF registries_found < 2:
  → Pivot to GitHub-first strategy (Phase 2)
  → Reduce registry-based success criteria
  → Document findings as "registry ecosystem immature"
```

### 1.5 Deliverables

- `registries.yaml` - Documented registry endpoints and APIs
- `registry-search.sh` - Script to query all registries
- `registry-status.md` - Which registries exist/work

### 1.6 Success Gate

- [ ] 3+ registries verified OR fallback documented
- [ ] API patterns documented for working registries

---

## Phase 2: GitHub Search Patterns

### 2.1 Query Builder

Parameterized search patterns:

```python
GITHUB_QUERIES = {
    "file_based": [
        "filename:SKILL.md claude",
        "filename:SKILL.md path:skills",
        "filename:plugin.json skills",
        "filename:.claude-plugin",
        "path:skills/ SKILL.md",
        "path:context/skills",
    ],
    "content_based": [
        '"tags: [" claude skill',
        '"## Quick Reference" "claude code"',
        '"## When to Use" "## Workflow" claude',
        '"## Common Patterns" "## Anti-Patterns"',
    ],
    "repository": [
        "awesome-claude-code",
        "awesome-claude skills",
        "claude-code-skill-template",
        "claude-skill-starter",
    ],
    "organization": [
        "org:anthropics skills",
        "org:modelcontextprotocol",
    ],
    "topic": [
        "topic:claude-code",
        "topic:claude-skills",
        "topic:ai-skills",
        "topic:llm-skills",
    ],
}
```

### 2.2 Rate Limit Strategy

| API | Limit | Strategy |
|-----|-------|----------|
| GitHub Search | 30/min (unauth), 30/min (auth) | Batch queries, 2s delay between |
| GitHub API | 5000/hr (auth) | Use PAT, cache aggressively |
| GraphQL | 5000 points/hr | Optimize query complexity |

```bash
# Token rotation for higher limits
export GITHUB_TOKENS="token1,token2,token3"
```

### 2.3 Error Handling

```bash
# Checkpoint/resume capability
CHECKPOINT_FILE=".github-search-checkpoint.json"

on_error() {
  save_checkpoint "$CHECKPOINT_FILE"
  echo "Saved progress. Resume with: ./github-search.sh --resume"
}

trap on_error ERR
```

### 2.4 Deliverables

- `github-queries.md` - Documented search queries with expected results
- `github-search.sh` - Script with checkpoint/resume
- `github-results.json` - Raw search results

### 2.5 Success Gate

- [ ] All query patterns executed
- [ ] 50+ unique repositories identified

---

## Phase 3: Web Crawling Strategies

### 3.1 Target Sites

| Site | Strategy | Tools | Rate Limit |
|------|----------|-------|------------|
| GitHub | API + Search | `gh api`, GraphQL | 5000/hr |
| GitLab | API | `glab`, REST API | 2000/hr |
| Dev.to | Tag search | WebFetch, RSS | 30/min |
| Medium | Tag search | WebFetch | 100/hr |
| Reddit | Subreddit search | Reddit API | 60/min |
| HackerNews | Algolia search | HN API | No limit |
| Bluesky | Hashtag search | AT Protocol | TBD |
| Mastodon | Hashtag search | ActivityPub | Instance-dependent |
| Discord | Server search | Manual | N/A |

### 3.2 Crawling Tools

| Tool | Use Case | Cache TTL | Notes |
|------|----------|-----------|-------|
| `crawl4ai` MCP | JS-rendered pages | 7 days | Full page crawl |
| `firecrawl` MCP | Batch crawling | 7 days | Rate-limited, costs $ |
| `WebFetch` | Static pages | 24 hours | Fast, simple |
| `gh api` | GitHub data | 24 hours | Structured |
| `curl` + `jq` | REST APIs | 24 hours | Lightweight |

### 3.3 Caching Strategy

```yaml
cache:
  directory: ".cache/skill-discovery/"
  ttl:
    registries: 24h
    github: 7d
    web_pages: 7d
    api_responses: 24h
  max_size: 500MB
```

### 3.4 Search Queries by Platform

**Dev.to:**

```text
https://dev.to/search?q=claude%20code%20skill
https://dev.to/t/claudecode
```

**Reddit:**

```text
site:reddit.com "claude code" skill
r/ClaudeAI skills
r/LocalLLaMA claude code
```

**HackerNews:**

```text
https://hn.algolia.com/api/v1/search?query=claude+code+skill
```

**Bluesky:**

```text
#claudecode
#claudeai skills
```

### 3.5 Deliverables

- `crawl-targets.yaml` - Sites and endpoints to crawl
- `crawl-skill-registry.sh` - Unified crawling script with caching
- `crawl-results/` - Directory of cached responses

### 3.6 Success Gate

- [ ] All target sites crawled
- [ ] 20+ additional skills discovered beyond GitHub

---

## Phase 4: Aggregation & Indexing

### 4.1 Data Model

```yaml
schema_version: 2

skill:
  # Identity
  name: string
  canonical_url: string  # For deduplication
  content_hash: string   # SHA256 of SKILL.md content

  # Description
  description: string
  category: "cli-tools|languages|frameworks|workflows|infrastructure|testing"
  tags: [string]

  # Source
  source:
    type: github|npm|registry|web
    url: string
    last_checked: datetime

  # Quality signals
  quality:
    score: float  # 0.0 - 1.0
    stars: int
    last_commit: datetime
    has_examples: boolean
    has_tests: boolean
    documentation_completeness: float

  # Metadata
  metadata:
    author: string
    version: string
    license: string
    dependencies: [string]

  # Content
  content:
    raw_url: string
    cached_path: string
```

### 4.2 Deduplication Strategy

```python
def deduplicate(skills: list[Skill]) -> list[Skill]:
    """
    Deduplication priority:
    1. Exact URL match → keep first seen
    2. Content hash match → keep highest quality score
    3. Name + author match → merge metadata, keep best source
    """
    seen_urls = {}
    seen_hashes = {}

    for skill in skills:
        canonical = normalize_url(skill.canonical_url)

        if canonical in seen_urls:
            continue  # Exact duplicate

        if skill.content_hash in seen_hashes:
            existing = seen_hashes[skill.content_hash]
            if skill.quality.score > existing.quality.score:
                seen_hashes[skill.content_hash] = skill
            continue

        seen_urls[canonical] = skill
        seen_hashes[skill.content_hash] = skill

    return list(seen_urls.values())
```

### 4.3 Quality Scoring

```python
def calculate_quality_score(skill: Skill) -> float:
    weights = {
        "has_documentation": 0.25,
        "recent_activity": 0.20,  # Commit in last 6 months
        "has_examples": 0.20,
        "star_count": 0.15,      # Normalized
        "has_tests": 0.10,
        "complete_metadata": 0.10,
    }

    score = 0.0
    for factor, weight in weights.items():
        score += evaluate_factor(skill, factor) * weight

    return score
```

### 4.4 Storage: SQLite + FTS5

```sql
-- Schema
CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    canonical_url TEXT UNIQUE,
    content_hash TEXT,
    description TEXT,
    category TEXT,
    quality_score REAL,
    source_type TEXT,
    source_url TEXT,
    last_checked DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE skills_fts USING fts5(
    name, description, tags, content,
    content='skills', content_rowid='id'
);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_quality ON skills(quality_score DESC);
```

### 4.5 Deliverables

- `skill-index.db` - SQLite database of discovered skills
- `skill-search.py` - CLI to search indexed skills
- `skill-sync.sh` - Script to refresh index from all sources
- `dedup-report.md` - Statistics on duplicates found/merged

### 4.6 Success Gate

- [ ] All skills from Phases 1-3 indexed
- [ ] Deduplication removes 10%+ duplicates
- [ ] Search returns results in <100ms

---

## Phase 5: Integration

### 5.1 Agent Integration

Update `plugin-skill-researcher` agent to use discovered sources:

```python
SKILL_SOURCES = [
    {"type": "local", "path": "context/skills/", "priority": 1},
    {"type": "index", "path": ".data/skill-index.db", "priority": 2},
    {"type": "github", "queries": GITHUB_QUERIES, "priority": 3},
    {"type": "registry", "urls": REGISTRIES, "priority": 4},
]

async def search_skills(query: str) -> list[Skill]:
    results = []
    for source in sorted(SKILL_SOURCES, key=lambda s: s["priority"]):
        results.extend(await search_source(source, query))
        if len(results) >= 10:
            break  # Early exit with enough results
    return deduplicate(results)
```

### 5.2 CLI Integration

```bash
# Search for skills
just skill-search "changelog generation"

# Fetch and cache a skill
just skill-fetch github:user/repo/path/to/SKILL.md

# List all indexed skills
just skill-list --tag cli

# Refresh index from all sources
just skill-sync

# Show index statistics
just skill-stats
```

### 5.3 Periodic Refresh

```bash
# Cron job for weekly refresh
0 2 * * 0 cd /path/to/repo && just skill-sync >> /var/log/skill-sync.log 2>&1
```

### 5.4 Deliverables

- Updated `plugin-skill-researcher` agent
- `just` recipes for skill discovery
- Documentation in `docs/src/skill-discovery.md`
- Cron configuration for periodic refresh

### 5.5 Success Gate

- [ ] Agent successfully queries index
- [ ] CLI tools functional
- [ ] Documentation complete

---

## Phase 6: Validation

### 6.1 Baseline Comparison

```python
def validate_recall(discovered: set, baseline: set) -> float:
    """What % of known skills did we find?"""
    found = discovered.intersection(baseline)
    return len(found) / len(baseline)

# Target: 80% recall on baseline skills
```

### 6.2 Test Queries

| Query | Expected Results | Baseline Skills |
|-------|------------------|-----------------|
| "git changelog" | git-cliff, conventional-changelog | 2 known |
| "kubernetes" | k8s deployment, helm | 3 known |
| "terraform" | tf module, infrastructure | 2 known |
| "react component" | react, frontend | 2 known |

### 6.3 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recall | 80% | % of baseline skills found |
| Precision | 90% | % of results that are actual skills |
| Freshness | <7 days | Age of indexed data |
| Coverage | 90% | % of sources successfully crawled |
| Search latency | <100ms | P95 response time |

### 6.4 Deliverables

- `validation-report.md` - Full metrics report
- `false-positives.yaml` - Non-skills incorrectly indexed
- `missing-skills.yaml` - Baseline skills not found

### 6.5 Success Gate

- [ ] Recall ≥ 80% on baseline
- [ ] Precision ≥ 90% on sample
- [ ] All test queries return relevant results

---

## Phase Dependency Graph

```text
Phase 0 (Baseline)
    │
    ▼
Phase 1 (Registries) ──────┐
    │                      │
    ▼                      │
Phase 2 (GitHub) ──────────┼──► Phase 4 (Aggregation)
    │                      │         │
    ▼                      │         ▼
Phase 3 (Web Crawling) ────┘    Phase 5 (Integration)
                                     │
                                     ▼
                               Phase 6 (Validation)
```

**Parallelization:**

- Phases 1, 2, 3 can run in parallel after Phase 0
- Phase 4 requires all of 1-3 to complete
- Phases 5-6 are sequential

---

## Execution Order

| Phase | Name | Duration | Dependencies | Parallelizable |
|-------|------|----------|--------------|----------------|
| 0 | Baseline Creation | 0.5 day | None | No |
| 1 | Registry Discovery | 1 day | Phase 0 | Yes (with 2,3) |
| 2 | GitHub Patterns | 1 day | Phase 0 | Yes (with 1,3) |
| 3 | Web Crawling | 2 days | Phase 0 | Yes (with 1,2) |
| 4 | Aggregation | 1 day | Phases 1-3 | No |
| 5 | Integration | 1 day | Phase 4 | No |
| 6 | Validation | 0.5 day | Phase 5 | No |

**Sequential execution:** 7 days
**Parallel execution (1-3):** 4.5 days

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Registries don't exist | High | Medium | Fallback to GitHub-first |
| Rate limits block progress | Medium | High | Token rotation, caching, delays |
| Low skill count discovered | Medium | Medium | Expand search patterns, lower quality threshold |
| Duplicates inflate count | High | Low | Deduplication in Phase 4 |
| Index grows stale | Medium | Medium | Weekly cron refresh |

---

## Success Criteria

- [ ] Baseline of 20+ known skills documented
- [ ] 3+ skill registries documented (or fallback documented)
- [ ] GitHub search finds 50+ community skills
- [ ] Web crawling discovers 20+ additional skills
- [ ] Deduplication reduces count by 10%+
- [ ] Unified index is searchable in <100ms
- [ ] 80% recall on baseline skills
- [ ] Integration with existing agents complete
- [ ] Test queries return relevant results
