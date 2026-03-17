# Experiment 4: Component Verification & Deduplication Plan

## Metadata

```yaml
experiment:
  id: "exp-004-verification-deduplication"
  title: "Verify, deduplicate, and quality-tier collected components"
  created: "2026-03-09"
  updated: "2026-03-09"
  status: "approved"
```

## Data Quality Tiers

### Bronze (Raw)

- Directly scraped from registries
- No verification
- May contain duplicates, placeholders, or broken links

```json
{
  "quality_tier": "bronze",
  "scraped_at": "2026-03-09T12:00:00Z"
}
```

### Silver (Verified)

**Requirements:**
1. GitHub reference is valid (repo exists, is accessible)
2. Referenced content is NOT just an outline or placeholder
3. Name normalized
4. Deduplication pass complete

**Exception:** Registries that provide component content directly on the listing page (not just a reference to GitHub). Example: skillsmp.com provides an interface to view the skill, but the actual skill lives on GitHub - the GitHub version must be verified.

**Placeholder/Outline Detection:**
- README < 100 characters
- No actual code files (only README, LICENSE, etc.)
- Template boilerplate not filled in
- "TODO", "Coming soon", "WIP" in description without substance

**Components that are ONLY placeholders are:**
- Dropped from Silver consideration
- Archived in `raw/archived-placeholders.ndjson`
- Ineligible for Gold promotion

```json
{
  "quality_tier": "silver",
  "verified_at": "2026-03-09T14:00:00Z",
  "verification_checks": [
    "github_exists",
    "github_accessible",
    "content_not_placeholder",
    "name_normalized",
    "deduplicated"
  ],
  "github_verification": {
    "repo_exists": true,
    "has_code_files": true,
    "readme_length": 2500,
    "last_commit": "2026-02-15"
  }
}
```

### Gold (Curated)

- All Silver requirements met
- Complete metadata
- Quality score assigned
- Active maintenance confirmed (commit in last 12 months)

```json
{
  "quality_tier": "gold",
  "curated_at": "2026-03-09T16:00:00Z",
  "quality_score": 0.95,
  "maintenance_status": "active"
}
```

## Deduplication Strategy (Approved)

### Fork Handling Decision Matrix

| Scenario | Action |
|----------|--------|
| Same content, different names | **MERGE** - Keep canonical, add alias to `related_ids` |
| Syntax-only changes (casing, formatting) | **MERGE** - Not structural, add to `related_ids` as clone |
| Significant/structural changes | **KEEP SEPARATE** - Add `fork_of` link in `related_ids` |
| Completely different content | **KEEP SEPARATE** - Note naming collision |

**"Significant changes" defined as:**
- Different features or functionality
- Structural modifications to code
- Different dependencies
- Emphasis-focused rewrites that change meaning

**"Syntax-only changes" defined as:**
- Casing differences (camelCase vs snake_case)
- Formatting/whitespace
- Comment-only changes
- Variable renames without logic changes

### Naming Authority (Approved)

**Priority order:**
1. Official source (modelcontextprotocol org, anthropic, etc.)
2. Most stars/downloads

**Naming collisions with different content:**
- Create TWO separate entries
- Both are unique components
- Add `naming_collision` flag with reference to the other
- Let users decide which they want

```json
{
  "id": "postgres-mcp_modelcontextprotocol",
  "name": "postgres-mcp",
  "naming_collision": ["postgres-mcp_johndoe"],
  "is_official": true
}
```

### Stale Component Handling (Approved)

- Mark as `maintenance_status: "stale"` after 12 months no activity
- **Keep in database** (do not remove)
- Eligible to remain at current tier
- Display stale indicator in search results

```json
{
  "maintenance_status": "stale",
  "last_activity": "2025-01-15T00:00:00Z",
  "stale_since": "2026-01-15T00:00:00Z"
}
```

### Cross-Registry Metadata (Approved)

**Prefer specific registry order:**

1. Official sources (modelcontextprotocol, anthropic)
2. GitHub direct
3. smithery.ai
4. buildwithclaude.com
5. mcpservers.org
6. mcp.so
7. skillsmp.com
8. Other registries

When merging from multiple sources:
- Use metadata from highest-priority source
- Populate `scrape_sources` array with all sources found

```json
{
  "source_name": "smithery.ai",  // Primary source
  "scrape_sources": [
    {"name": "smithery.ai", "url": "...", "scraped_at": "..."},
    {"name": "mcp.so", "url": "...", "scraped_at": "..."},
    {"name": "mcpservers.org", "url": "...", "scraped_at": "..."}
  ]
}
```

## Updated Schema

```json
{
  // Existing fields
  "id": "string",
  "name": "string",
  "type": "string",
  "description": "string",
  "author": "string",
  "canonical_url": "string",
  "github_url": "string",
  "star_count": 0,
  "source_type": "string",
  "source_name": "string",
  "source_url": "string",
  "tags": [],
  "discovered_at": "string",

  // NEW: Quality tier fields
  "quality_tier": "bronze|silver|gold",
  "quality_score": 0.0,
  "verified_at": "string|null",
  "verification_checks": [],

  // NEW: Normalization fields
  "name_normalized": "string",
  "content_hash": "string",

  // NEW: Relationship fields
  "related_ids": {
    "clones": [],      // Syntax-only duplicates (merged)
    "forks": [],       // Significant modifications (fork_of)
    "aliases": []      // Alternative names for same component
  },
  "naming_collision": [],  // Other components with same name but different content
  "is_official": false,

  // NEW: Source tracking
  "scrape_sources": [],

  // NEW: Maintenance tracking
  "maintenance_status": "active|stale|abandoned|unknown",
  "last_activity": "string|null",
  "stale_since": "string|null",

  // NEW: GitHub verification (Silver+)
  "github_verification": {
    "repo_exists": true,
    "has_code_files": true,
    "readme_length": 0,
    "last_commit": "string",
    "is_placeholder": false
  }
}
```

## Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                         BRONZE (Raw)                             │
│  - Scrape from registries                                       │
│  - Basic parse and store                                        │
│  - No verification                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VERIFICATION GATE                             │
│  1. GitHub URL reachable?                                       │
│  2. Repo exists and accessible?                                 │
│  3. Has actual code (not just README)?                          │
│  4. Not a placeholder/template?                                 │
│                                                                 │
│  FAIL → Archive to raw/archived-placeholders.ndjson             │
│  PASS → Continue to Silver                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SILVER (Verified)                        │
│  - Normalize names                                              │
│  - Compute content hash                                         │
│  - Deduplication pass                                           │
│  - Cross-reference sources                                      │
│  - Apply naming authority rules                                 │
│  - Merge clones, link forks                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUALITY SCORING GATE                          │
│  - Has description: +0.15                                       │
│  - Has GitHub URL: +0.15                                        │
│  - Has stars: +0.10                                             │
│  - Recent activity (6mo): +0.20                                 │
│  - Has README: +0.15                                            │
│  - Has license: +0.10                                           │
│  - Multiple sources: +0.05                                      │
│  - Official source: +0.10                                       │
│                                                                 │
│  Score >= 0.7 → Eligible for Gold                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         GOLD (Curated)                           │
│  - Complete metadata                                            │
│  - Quality score assigned                                       │
│  - Maintenance status confirmed                                 │
│  - Ready for production index                                   │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
/meilisearch/indices/
├── components.json              # Gold tier (production)
├── components-silver.json       # Silver tier (verified)
├── raw/
│   ├── {source}-bronze.ndjson   # Per-source raw scrapes
│   └── archived-placeholders.ndjson  # Failed verification
├── scripts/
│   ├── split-components-by-source.py
│   ├── verify-github.py
│   ├── detect-placeholders.py
│   ├── normalize-names.py
│   ├── compute-content-hash.py
│   ├── deduplicate.py
│   ├── compute-quality-score.py
│   └── promote-tier.py
└── reports/
    ├── verification-report.json
    ├── dedup-report.json
    ├── placeholder-report.json
    └── quality-report.json
```

## Implementation Order

1. Split existing components.json by source (Phase 0)
2. Implement placeholder detection
3. Implement GitHub verification
4. Implement name normalization
5. Implement content hashing
6. Implement deduplication with fork/clone detection
7. Implement quality scoring
8. Create promotion scripts
