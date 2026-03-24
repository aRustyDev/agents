# Claude Code Component Discovery Research Plan

> **ARCHIVED** — This document has been superseded by the restructured plan.
> See [PLAN.md](PLAN.md) for the current source of truth.
>
> This file is retained for historical context and the detailed registry/repo listings
> which informed the new structure.

---

## Goal

Survey and inventory **all Claude Code component registries** across 8 categories:

1. **Skills** — Domain knowledge and procedures
2. **Agents** — Specialized subagents for complex tasks
3. **Commands** — Slash commands (user-invoked workflows)
4. **Rules** — Behavioral constraints and guidelines
5. **Prompts** — Reusable prompt templates
6. **Hooks** — Lifecycle interceptors
7. **MCP Servers** — External tool integrations
8. **Plugins** — Packages bundling multiple component types

For each independent website registry, document:

- API endpoints and documentation
- Crawling/scraping restrictions (robots.txt, ToS, rate limits)
- Search functionality and query patterns

## Ownership

**Executor:** Single agent/developer
**Stakeholder:** Plugin ecosystem maintainers

## Key Insight: Plugin Dependency Order

Plugins are **packages that bundle** Skills, Rules, Commands, Agents, Hooks, and MCP configs.
Therefore: **Discover base components FIRST, then Plugins LAST**.

```text
┌─────────────────────────────────────────────────────────┐
│                      PLUGINS                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Skills  │ │ Agents  │ │Commands │ │  Rules  │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│  │ Prompts │ │  Hooks  │ │   MCP   │                   │
│  └─────────┘ └─────────┘ └─────────┘                   │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 0: Search Term Matrix & Baseline

> **Purpose:** Establish systematic search vocabulary and ground truth

### 0.1 Search Term Matrix

Build a matrix of search terms for comprehensive coverage:

| Concept | Primary Terms | Synonyms | Narrower Terms | Broader Terms |
|---------|---------------|----------|----------------|---------------|
| **Skills** | `claude skill`, `agent skill` | `capability`, `knowledge module` | `SKILL.md`, `skill-creator` | `claude code`, `ai assistant` |
| **Agents** | `claude agent`, `subagent` | `specialist`, `expert agent` | `agent.md`, `subagent-type` | `agentic`, `orchestrator` |
| **Commands** | `slash command`, `claude command` | `workflow`, `action` | `/command`, `commands/` | `cli`, `interface` |
| **Rules** | `claude rules`, `RULES.md` | `constraints`, `guidelines` | `behavioral rules`, `guardrails` | `safety`, `policy` |
| **Prompts** | `claude prompt`, `prompt template` | `instruction`, `system prompt` | `CLAUDE.md`, `prompts/` | `llm prompt`, `ai prompt` |
| **Hooks** | `claude hooks`, `lifecycle hook` | `interceptor`, `callback` | `pre-commit hook`, `post-tool hook` | `automation`, `trigger` |
| **MCP** | `mcp server`, `model context protocol` | `tool server`, `integration` | `mcp.json`, `mcpServers` | `api`, `connector` |
| **Plugins** | `claude plugin`, `claude code plugin` | `extension`, `package`, `addon` | `plugin.json`, `.claude-plugin` | `marketplace`, `registry` |

### 0.2 Boolean Query Patterns

For each search engine, construct queries using:

```text
# AND patterns
"claude code" AND skill
"claude" AND "agent" AND "subagent"

# OR patterns (synonyms)
(skill OR capability OR "knowledge module") AND claude

# Exclusion patterns
"claude skill" NOT "anthropic employee" NOT "job posting"

# Site-specific
site:github.com "claude skill" SKILL.md
site:dev.to "claude code" tutorial
```

### 0.3 Baseline Inventory

Document known components per category from this repo:

| Category | Local Path | Expected Count |
|----------|------------|----------------|
| Skills | `content/skills/` | 100+ |
| Agents | `content/agents/` | 10+ |
| Commands | `content/commands/` | 20+ |
| Rules | `content/rules/` | 5+ |
| Prompts | `content/output-styles/` | 10+ |
| Hooks | `content/hooks/` | 5+ |
| MCP | `settings/mcp/` | 10+ |
| Plugins | `content/plugins/` | 6 |

### 0.4 Deliverables

- `phase-0/search-term-matrix.yaml` — Complete matrix with all terms
- `phase-0/boolean-queries.md` — Query templates per search engine
- `phase-0/baseline-inventory.yaml` — Local component counts

### 0.5 Success Gate

- [ ] Matrix covers all 8 categories
- [ ] 5+ synonyms per category identified
- [ ] Local baseline documented

---

## Phase 1: Search Tool Experiments

> **Purpose:** Compare search tools to determine effectiveness per source type

### 1.1 Tools Under Test

| Tool | Type | Best For | Cost |
|------|------|----------|------|
| `WebSearch` | Claude native | Quick web search | Free (API) |
| `WebFetch` | Claude native | Static page scraping | Free (API) |
| `gh api` | GitHub CLI | Repo/code search | Free (auth) |
| `crawl4ai` MCP | JS-rendered | SPAs, dynamic content | Free |
| `firecrawl` MCP | Batch crawl | Large-scale scraping | $ |
| Serper API | Google wrapper | Broad web search | $ |
| SearXNG | Meta-search | Privacy, aggregation | Self-host |
| DuckDuckGo | Direct search | No tracking | Free |

### 1.2 Experiment Design

For each tool, run the **same 5 test queries** and measure:

| Metric | Definition |
|--------|------------|
| **Recall** | % of known baseline items found |
| **Precision** | % of results that are actual components |
| **Latency** | Time to complete query |
| **Rate Limit** | Requests before throttling |
| **Coverage** | Unique sources discovered |

**Test Queries:**

1. `"claude code skill" site:github.com`
2. `"awesome-claude" skills`
3. `mcp server claude`
4. `"SKILL.md" claude`
5. `claude plugin marketplace`

### 1.3 Experiment Matrix

| Query | WebSearch | WebFetch | gh api | crawl4ai | firecrawl | Serper |
|-------|-----------|----------|--------|----------|-----------|--------|
| Q1 | — | — | — | — | — | — |
| Q2 | — | — | — | — | — | — |
| Q3 | — | — | — | — | — | — |
| Q4 | — | — | — | — | — | — |
| Q5 | — | — | — | — | — | — |

Fill with: ✓ (found), ✗ (missed), ⚠ (partial), ⏱ (rate limited)

### 1.4 Deliverables

- `phase-1/tool-experiment-results.yaml` — Raw results per tool
- `phase-1/tool-comparison-report.md` — Analysis and recommendations
- `phase-1/recommended-tools.yaml` — Best tool per source type

### 1.5 Success Gate

- [ ] All 6 tools tested with 5 queries each
- [ ] Best tool identified per source type
- [ ] Rate limits documented

---

## Phase 2: Component Discovery (Repeatable Template)

> **Purpose:** Discover registries and repos for each component type

This phase repeats for **each of the 7 base component types** (Skills, Agents, Commands, Rules, Prompts, Hooks, MCP). Use the same template structure.

### Template: Component Type Discovery

#### 2.X.1 Independent Site Registries

| Registry | URL | Status | API Docs | robots.txt | Rate Limit |
|----------|-----|--------|----------|------------|------------|
| [name] | [url] | Active/Unknown | [url] | Allow/Disallow | [limit] |

**Research Tasks:**

- [ ] Fetch homepage and verify active
- [ ] Check `/docs/api`, `/api/v1`, `/swagger` for API docs
- [ ] Fetch `robots.txt` and document restrictions
- [ ] Test search functionality
- [ ] Document authentication requirements
- [ ] Check ToS for scraping policy

#### 2.X.2 GitHub Repository Collections

| Repository | URL | Stars | Component Count | Last Updated |
|------------|-----|-------|-----------------|--------------|
| [name] | [url] | [n] | [n] | [date] |

**Research Tasks:**

- [ ] Search GitHub for `awesome-*` repos
- [ ] Search for repos with relevant topics
- [ ] Check repo structure for component files
- [ ] Document README for component listings

#### 2.X.3 Package Manager Search

| Registry | Search Terms | Results |
|----------|--------------|---------|
| npm | `claude-[type]` | [n] |
| PyPI | `claude-[type]` | [n] |
| crates.io | `claude-[type]` | [n] |

#### 2.X.4 Deliverables

- `phase-2/[type]/registries.yaml`
- `phase-2/[type]/github-repos.yaml`
- `phase-2/[type]/api-docs.md`

---

## Phase 2.1: Skills Discovery

### 2.1.1 Independent Site Registries

| Registry | URL | Status | API Docs | Notes |
|----------|-----|--------|----------|-------|
| skillsmp | <https://skillsmp.com/> | Active | <https://skillsmp.com/docs/api> | 2000+ skills, largest |
| ccpm | <https://ccpm.dev/> | Active | TBD | Claude Code Package Manager |
| claude-plugins.dev | <https://claude-plugins.dev/> | Active | TBD | Community registry |
| agentskills.best | <https://agentskills.best/> | Active | TBD | Enterprise-grade |
| claudeskillsmarket | <https://claudeskillsmarket.com/> | Active | TBD | Community-powered |
| claudecodemarketplace | <https://claudecodemarketplace.com/> | Active | TBD | Plugins + Skills |
| mcpservers.org/skills | <https://mcpservers.org/claude-skills> | Active | TBD | MCP-integrated |
| atcyrus | <https://www.atcyrus.com/skills> | Active | TBD | DevOps, security |
| awesome-claude-code.com | <https://awesome-claude-code.com/> | Active | TBD | Web curated list |
| awesomeclaude.ai | <https://awesomeclaude.ai/> | Active | TBD | AI aggregator |
| lobehub | <https://lobehub.com/> | Active | TBD | Skills registry |
| notion-skills | <https://notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0> | Active | TBD | Notion integration |

**Research Tasks:**

- [ ] Fetch `https://skillsmp.com/docs/api` and document endpoints
- [ ] Check robots.txt for each registry
- [ ] Test search APIs where available
- [ ] Document rate limits from response headers

### 2.1.2 GitHub Repository Collections

| Repository | URL | Stars | Skills |
|------------|-----|-------|--------|
| anthropics/skills | <https://github.com/anthropics/skills> | — | 17 official |
| trailofbits/skills | <https://github.com/trailofbits/skills> | 3.4k | 35 security |
| obra/superpowers | <https://github.com/obra/superpowers> | — | 14 workflow |
| hesreallyhim/awesome-claude-code | <https://github.com/hesreallyhim/awesome-claude-code> | 26.7k | Curated list |
| VoltAgent/awesome-claude-code-subagents | <https://github.com/VoltAgent/awesome-claude-code-subagents> | 12.8k | 100+ subagents |
| travisvn/awesome-claude-skills | <https://github.com/travisvn/awesome-claude-skills> | 8.4k | Curated index |
| ComposioHQ/awesome-claude-skills | <https://github.com/ComposioHQ/awesome-claude-skills> | 41.7k | Productivity |
| BehiSecc/awesome-claude-skills | <https://github.com/BehiSecc/awesome-claude-skills> | 7.2k | Tutorials |
| VoltAgent/awesome-claude-skills | <https://github.com/VoltAgent/awesome-claude-skills> | — | Orchestration |
| Jeffallan/claude-skills | <https://github.com/Jeffallan/claude-skills> | 5.5k | 66 full-stack |
| alirezarezvani/claude-skills | <https://github.com/alirezarezvani/claude-skills> | 2.6k | 42 enterprise |
| alirezarezvani/claude-code-skill-factory | <https://github.com/alirezarezvani/claude-code-skill-factory> | — | Meta-factory |
| wshobson/agents | <https://github.com/wshobson/agents> | — | 47 skills |
| abubakarsiddik31/claude-skills-collection | <https://github.com/abubakarsiddik31/claude-skills-collection> | — | Categorized |
| ashleytower/claude-skills-collection | <https://github.com/ashleytower/claude-skills-collection> | — | Ecosystem |
| meetrais/claude-agent-skills | <https://github.com/meetrais/claude-agent-skills> | — | API examples |
| tech-leads-club/agent-skills | <https://github.com/tech-leads-club/agent-skills> | — | TBD |
| lackeyjb/playwright-skill | <https://github.com/lackeyjb/playwright-skill> | — | Playwright |
| adrianpuiu/claude-skills-marketplace | <https://github.com/adrianpuiu/claude-skills-marketplace> | — | Marketplace |

### 2.1.3 Related Ecosystems

| Ecosystem | URL | Notes |
|-----------|-----|-------|
| Goose Skills | <https://block.github.io/goose/skills/> | Compatible format |
| OpenClaw | <https://lobehub.com/bg/skills/sundial-org-awesome-openclaw-skills-agent-registry> | Cross-platform |

### 2.1.4 Reference Articles

| Article | URL |
|---------|-----|
| Official Docs | <https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview> |
| 25 Top Registries | <https://medium.com/@frulouis/25-top-claude-agent-skills-registries-community-collections-you-should-know-2025-52aab45c877d> |

---

## Phase 2.2: Agents Discovery

### 2.2.1 Independent Site Registries

| Registry | URL | Status | Notes |
|----------|-----|--------|-------|
| (TBD - research needed) | | | |

### 2.2.2 GitHub Repository Collections

| Repository | URL | Stars | Agents |
|------------|-----|-------|--------|
| VoltAgent/awesome-claude-code-subagents | <https://github.com/VoltAgent/awesome-claude-code-subagents> | 12.8k | 100+ subagents |
| rahulvrane/awesome-claude-agents | <https://github.com/rahulvrane/awesome-claude-agents> | — | Directory |
| 0xfurai/claude-code-subagents | <https://github.com/0xfurai/claude-code-subagents> | — | 100+ domain |
| vijaythecoder/awesome-claude-agents | <https://github.com/vijaythecoder/awesome-claude-agents> | — | Dev team |
| iannuttall/claude-agents | <https://github.com/iannuttall/claude-agents> | 1.9k | Refactoring |
| wshobson/agents | <https://github.com/wshobson/agents> | — | 85 agents |
| FrancyJGLisboa/agent-skill-creator | <https://github.com/FrancyJGLisboa/agent-skill-creator> | — | Meta-agent |

---

## Phase 2.3: Commands Discovery

### 2.3.1 Independent Site Registries

| Registry | URL | Status | Notes |
|----------|-----|--------|-------|
| (TBD - research needed) | | | |

### 2.3.2 GitHub Repository Collections

| Repository | URL | Notes |
|------------|-----|-------|
| hesreallyhim/awesome-claude-code | <https://github.com/hesreallyhim/awesome-claude-code> | Commands section |
| anthropics/claude-code | <https://github.com/anthropics/claude-code> | Official CLI docs |

---

## Phase 2.4: Rules Discovery

### 2.4.1 Independent Site Registries

| Registry | URL | Status | Notes |
|----------|-----|--------|-------|
| (TBD - research needed) | | | |

### 2.4.2 GitHub Repository Collections

| Repository | URL | Notes |
|------------|-----|-------|
| (TBD - search for RULES.md patterns) | | |

---

## Phase 2.5: Prompts Discovery

### 2.5.1 Independent Site Registries

| Registry | URL | Status | Notes |
|----------|-----|--------|-------|
| (TBD - research needed) | | | |

### 2.5.2 GitHub Repository Collections

| Repository | URL | Notes |
|------------|-----|-------|
| (TBD - search for CLAUDE.md, prompts/) | | |

---

## Phase 2.6: Hooks Discovery

### 2.6.1 Independent Site Registries

| Registry | URL | Status | Notes |
|----------|-----|--------|-------|
| (TBD - research needed) | | | |

### 2.6.2 GitHub Repository Collections

| Repository | URL | Notes |
|------------|-----|-------|
| hesreallyhim/awesome-claude-code | <https://github.com/hesreallyhim/awesome-claude-code> | Hooks section |

---

## Phase 2.7: MCP Servers Discovery

### 2.7.1 Independent Site Registries

| Registry | URL | Status | Notes |
|----------|-----|--------|-------|
| Smithery | <https://smithery.ai/> | Active | Primary MCP registry |
| mcpservers.org | <https://mcpservers.org/> | Active | MCP directory |
| mcp.so | <https://mcp.so/> | Active | MCP search |
| glama.ai/mcp | <https://glama.ai/mcp/> | Active | MCP directory |

### 2.7.2 GitHub Repository Collections

| Repository | URL | Notes |
|------------|-----|-------|
| modelcontextprotocol/servers | <https://github.com/modelcontextprotocol/servers> | Official |
| punkpeye/awesome-mcp-servers | <https://github.com/punkpeye/awesome-mcp-servers> | Curated |

---

## Phase 3: Plugin Discovery

> **Purpose:** Discover plugins AFTER base components (since plugins bundle them)

### 3.1 Independent Site Registries

| Registry | URL | Status | Notes |
|----------|-----|--------|-------|
| claudemarketplaces | <https://claudemarketplaces.com/> | Active | Plugin hub |
| buildwithclaude | <https://buildwithclaude.com/> | Active | Builder community |
| clauderegistry | <https://clauderegistry.com/> | Active | Central registry |
| litellm plugin docs | <https://docs.litellm.ai/docs/tutorials/claude_code_plugin_marketplace> | Active | Tutorial |
| paddo.dev | <https://paddo.dev/blog/claude-tools-plugin-marketplace/> | Active | Blog + marketplace |

### 3.2 GitHub Repository Collections

| Repository | URL | Notes |
|------------|-----|-------|
| ananddtyagi/cc-marketplace | <https://github.com/ananddtyagi/cc-marketplace> | Plugin marketplace |
| Kamalnrf/claude-plugins | <https://github.com/Kamalnrf/claude-plugins> | Plugin collection |
| composio.dev | <https://composio.dev/blog/top-claude-code-plugins> | Top plugins list |

### 3.3 Plugin Structure Analysis

For each discovered plugin, document which components it bundles:

```yaml
plugin:
  name: "example-plugin"
  components:
    skills: ["skill-a", "skill-b"]
    agents: ["agent-x"]
    commands: ["/cmd1", "/cmd2"]
    rules: ["rule-1"]
    hooks: ["post-tool-hook"]
    mcp_servers: ["server-a"]
```

---

## Phase 4: API Documentation Research

> **Purpose:** Document API access for programmatic registry queries

### 4.1 Research Template Per Registry

For each independent site registry:

```yaml
registry:
  name: "skillsmp"
  base_url: "https://skillsmp.com"

  api:
    docs_url: "https://skillsmp.com/docs/api"
    authentication: "api_key" | "oauth" | "none"
    endpoints:
      - path: "/api/v1/skills"
        method: "GET"
        params: ["query", "category", "page"]
      - path: "/api/v1/skills/{id}"
        method: "GET"

  restrictions:
    robots_txt: "https://skillsmp.com/robots.txt"
    allowed_paths: ["/api/*"]
    disallowed_paths: ["/admin/*"]
    crawl_delay: 1  # seconds
    rate_limit: "100 req/min"
    tos_url: "https://skillsmp.com/terms"
    scraping_allowed: true | false | "with attribution"
```

### 4.2 Deliverables

- `phase-4/registry-apis.yaml` — Consolidated API documentation
- `phase-4/rate-limits.yaml` — Rate limits per registry
- `phase-4/access-restrictions.md` — ToS and robots.txt summary

---

## Phase 5: Aggregation & Indexing

### 5.1 Unified Data Model

```yaml
schema_version: 3

component:
  # Identity
  id: string  # UUID
  name: string
  type: "skill|agent|command|rule|prompt|hook|mcp|plugin"
  canonical_url: string
  content_hash: string  # SHA256

  # Description
  description: string
  category: string
  tags: [string]

  # Source
  source:
    type: "github|npm|registry|web"
    registry_name: string  # e.g., "skillsmp", "smithery"
    url: string
    last_checked: datetime

  # Quality signals
  quality:
    score: float
    stars: int
    last_commit: datetime
    has_examples: boolean
    has_tests: boolean

  # For plugins only
  bundled_components:
    skills: [component_id]
    agents: [component_id]
    commands: [component_id]
    rules: [component_id]
    hooks: [component_id]
    mcp_servers: [component_id]
```

### 5.2 Storage Schema

```sql
CREATE TABLE components (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- skill|agent|command|rule|prompt|hook|mcp|plugin
    canonical_url TEXT UNIQUE,
    content_hash TEXT,
    description TEXT,
    category TEXT,
    quality_score REAL,
    source_type TEXT,
    source_registry TEXT,
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

CREATE VIRTUAL TABLE components_fts USING fts5(
    name, description, tags,
    content='components', content_rowid='rowid'
);

CREATE INDEX idx_components_type ON components(type);
CREATE INDEX idx_components_quality ON components(quality_score DESC);
```

### 5.3 Deliverables

- `component-index.db` — SQLite database
- `component-search.py` — Search CLI
- `dedup-report.md` — Duplicate analysis

---

## Phase 6: Integration & Validation

### 6.1 CLI Integration

```bash
# Search by type
just component-search --type skill "changelog"
just component-search --type mcp "database"
just component-search --type plugin "devops"

# List by registry
just component-list --registry skillsmp
just component-list --registry smithery

# Sync from all sources
just component-sync

# Show statistics
just component-stats
```

### 6.2 Validation Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Component types covered | 8/8 | All types have discoveries |
| Registries documented | 20+ | Across all types |
| API docs captured | 80% | Of independent sites |
| Recall on baseline | 80% | Known components found |
| Precision | 90% | Results are actual components |

---

## Phase Dependency Graph

```text
Phase 0 (Matrix + Baseline)
    │
    ▼
Phase 1 (Tool Experiments)
    │
    ├──────────────────────────────────────────────┐
    ▼                                              │
Phase 2.1 (Skills) ──┐                             │
Phase 2.2 (Agents) ──┤                             │
Phase 2.3 (Commands)─┤                             │
Phase 2.4 (Rules) ───┼──► Phase 4 (API Docs) ──────┤
Phase 2.5 (Prompts) ─┤                             │
Phase 2.6 (Hooks) ───┤                             │
Phase 2.7 (MCP) ─────┘                             │
    │                                              │
    ▼                                              │
Phase 3 (Plugins) ─────────────────────────────────┘
    │
    ▼
Phase 5 (Aggregation)
    │
    ▼
Phase 6 (Integration + Validation)
```

**Parallelization:**

- Phase 2.1-2.7 can run in parallel
- Phase 3 (Plugins) waits for Phase 2 (needs component context)
- Phase 4 (API Docs) can run in parallel with Phase 2-3

---

## Execution Order

| Phase | Name | Duration | Dependencies |
|-------|------|----------|--------------|
| 0 | Search Term Matrix | 0.5 day | None |
| 1 | Tool Experiments | 1 day | Phase 0 |
| 2.1-2.7 | Component Discovery | 2 days | Phase 1 (parallel) |
| 3 | Plugin Discovery | 1 day | Phase 2 |
| 4 | API Documentation | 1 day | Phase 2 (parallel) |
| 5 | Aggregation | 1 day | Phase 3, 4 |
| 6 | Validation | 0.5 day | Phase 5 |

**Total: 7 days** (with parallelization)

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Registry API undocumented | Medium | Medium | Manual exploration, network inspection |
| Rate limits block progress | Medium | High | Caching, delays, tool rotation |
| robots.txt blocks crawling | Low | Medium | Use search APIs instead |
| Sparse registries for some types | High | Low | Focus on GitHub patterns |
| Plugin structure varies | Medium | Medium | Flexible schema, manual review |

---

## Success Criteria

- [ ] Search term matrix covers all 8 categories
- [ ] Tool comparison identifies best tools per source
- [ ] All 8 component types have registry/repo listings
- [ ] API documentation for 80%+ of independent sites
- [ ] robots.txt and rate limits documented
- [ ] Unified index searchable in <100ms
- [ ] 80% recall on baseline components
- [ ] Plugin bundling relationships captured
