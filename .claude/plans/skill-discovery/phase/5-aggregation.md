# Phase 5: Aggregation & Indexing

## Objective

Aggregate all discoveries into a unified, searchable index.

## Duration

1 day

## Dependencies

- Phase 3 (plugin discovery)
- Phase 4 (API documentation)

---

## Data Sources

Aggregate from:

| Source | Path | Contains |
|--------|------|----------|
| Skills | `research/results/skills/` | registries, repos, packages |
| Agents | `research/results/agents/` | registries, repos, packages |
| Commands | `research/results/commands/` | registries, repos, packages |
| Rules | `research/results/rules/` | registries, repos, packages |
| Prompts | `research/results/prompts/` | registries, repos, packages |
| Hooks | `research/results/hooks/` | registries, repos, packages |
| MCP | `research/results/mcp/` | registries, repos, packages |
| Plugins | `research/results/plugins/` | registries, repos, structures |
| APIs | `analysis/results/registry-api-*.yaml` | API docs |

---

## Unified Schema

```sql
-- component-index.db

CREATE TABLE components (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN (
        'skill', 'agent', 'command', 'rule',
        'prompt', 'hook', 'mcp', 'plugin'
    )),
    description TEXT,
    canonical_url TEXT UNIQUE,
    content_hash TEXT,
    category TEXT,
    tags TEXT,  -- JSON array
    quality_score REAL,
    source_type TEXT CHECK (source_type IN ('registry', 'github', 'npm', 'pypi', 'crates')),
    source_name TEXT,  -- e.g., "skillsmp", "anthropics/skills"
    source_url TEXT,
    last_checked DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plugin_components (
    plugin_id TEXT REFERENCES components(id),
    component_id TEXT REFERENCES components(id),
    component_type TEXT,
    PRIMARY KEY (plugin_id, component_id)
);

CREATE TABLE registries (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT UNIQUE,
    component_types TEXT,  -- JSON array of types it contains
    api_docs_url TEXT,
    has_search BOOLEAN,
    auth_required BOOLEAN,
    rate_limit TEXT,
    scraping_allowed BOOLEAN,
    last_checked DATETIME
);

CREATE VIRTUAL TABLE components_fts USING fts5(
    name, description, tags,
    content='components', content_rowid='rowid'
);

CREATE INDEX idx_components_type ON components(type);
CREATE INDEX idx_components_source ON components(source_name);
CREATE INDEX idx_components_quality ON components(quality_score DESC);
```

---

## Aggregation Process

### Step 1: Load Raw Results

```python
def load_research_results():
    """Load all YAML results from research/results/"""
    results = {}
    for component_type in COMPONENT_TYPES:
        path = f"research/results/{component_type}/"
        results[component_type] = {
            "registries": load_yaml(f"{path}/registries.yaml"),
            "github_repos": load_yaml(f"{path}/github-repos.yaml"),
            "packages": load_yaml(f"{path}/packages.yaml"),
        }
    return results
```

### Step 2: Normalize to Unified Schema

```python
def normalize_component(raw, source_type, source_name):
    """Convert raw result to unified component record"""
    return {
        "id": generate_id(raw),
        "name": raw["name"],
        "type": raw["component_type"],
        "canonical_url": normalize_url(raw["url"]),
        "content_hash": hash_content(raw.get("content")),
        "source_type": source_type,
        "source_name": source_name,
        # ...
    }
```

### Step 3: Deduplicate

```python
def deduplicate(components):
    """
    Deduplication priority:
    1. Exact URL match → keep first seen
    2. Content hash match → keep highest quality score
    3. Name + type match → merge metadata
    """
    seen_urls = {}
    seen_hashes = {}

    for c in components:
        url = c["canonical_url"]
        if url in seen_urls:
            continue  # Exact duplicate

        if c["content_hash"] in seen_hashes:
            existing = seen_hashes[c["content_hash"]]
            if c["quality_score"] > existing["quality_score"]:
                seen_hashes[c["content_hash"]] = c
            continue

        seen_urls[url] = c
        seen_hashes[c["content_hash"]] = c

    return list(seen_urls.values())
```

### Step 4: Calculate Quality Scores

```python
def calculate_quality(component, repo_data=None):
    """Score 0.0 - 1.0 based on signals"""
    weights = {
        "has_documentation": 0.25,
        "recent_activity": 0.20,  # Updated in last 6 months
        "has_examples": 0.20,
        "star_count": 0.15,  # Normalized
        "has_tests": 0.10,
        "complete_metadata": 0.10,
    }
    # ...
```

### Step 5: Build FTS Index

```python
def build_search_index(db):
    """Populate FTS5 virtual table"""
    db.execute("""
        INSERT INTO components_fts(rowid, name, description, tags)
        SELECT rowid, name, description, tags FROM components
    """)
```

---

## Experiment: Deduplication Analysis

Create: `analysis/experiments/7-deduplication.md`

```yaml
experiment:
  id: "exp-007-deduplication"
  title: "Measure duplicate component rate"

  hypothesis: "10-20% of components appear in multiple sources"

  procedure:
    - step: 1
      action: "Count total raw components"
    - step: 2
      action: "Run deduplication"
    - step: 3
      action: "Count unique components"
    - step: 4
      action: "Analyze duplicate sources"

  metrics:
    - name: "duplicate_rate"
      definition: "(total - unique) / total"
      target: 0.1  # At least 10% deduplication
```

---

## Deliverables

| File | Purpose |
|------|---------|
| `component-index.db` | SQLite database |
| `analysis/results/deduplication-stats.yaml` | Dedup metrics |
| `analysis/findings/aggregation-quality.yaml` | Quality analysis |

---

## Success Gate

| Criterion | Target |
|-----------|--------|
| All research results loaded | 8/8 component types |
| Components indexed | 500+ unique |
| Deduplication rate | 10%+ |
| FTS search working | <100ms queries |
| Plugin relationships mapped | Yes |

## Checklist

Use: `checklists/schemas/data-aggregation.schema.json`

Record: `checklists/instances/phase-5.json`
