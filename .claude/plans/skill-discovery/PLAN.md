# Claude Code Component Discovery

## Overview

Survey and inventory **all Claude Code component registries** across 8 categories to build a unified discovery index.

## Goals

1. **Inventory all registries** — Independent sites + GitHub repos for each component type
2. **Document API access** — Endpoints, rate limits, robots.txt, ToS
3. **Compare search tools** — Determine best tool per source type
4. **Build unified index** — Searchable database of all components
5. **Enable programmatic discovery** — CLI tools and agent integration

## Component Types

| Type | Description | Bundle Level |
|------|-------------|--------------|
| Skills | Domain knowledge and procedures | Base |
| Agents | Specialized subagents | Base |
| Commands | Slash commands (user workflows) | Base |
| Rules | Behavioral constraints | Base |
| Prompts | Reusable prompt templates | Base |
| Hooks | Lifecycle interceptors | Base |
| MCP Servers | External tool integrations | Base |
| **Plugins** | Packages bundling above types | Composite |

**Key Insight:** Plugins bundle base components → Discover base types FIRST.

## Directory Structure

```
skill-discovery/
├── PLAN.md                 # This file
├── analysis/               # Experiments, findings, evidence
├── checklists/             # Execution validation
├── phase/                  # Phase execution plans
└── research/               # Per-component research plans + results
```

## Phases

| Phase | Plan | Purpose |
|-------|------|---------|
| 0 | [phase/0-baseline-and-matrix.md](phase/0-baseline-and-matrix.md) | Search term matrix + baseline inventory |
| 1 | [phase/1-tool-experiments.md](phase/1-tool-experiments.md) | Compare search tools |
| 2 | [phase/2-component-discovery.md](phase/2-component-discovery.md) | Discover all 7 base component types |
| 3 | [phase/3-plugin-discovery.md](phase/3-plugin-discovery.md) | Discover plugins (after base types) |
| 4 | [phase/4-api-documentation.md](phase/4-api-documentation.md) | Document registry APIs |
| 5 | [phase/5-aggregation.md](phase/5-aggregation.md) | Build unified index |
| 6 | [phase/6-validation.md](phase/6-validation.md) | Validate coverage and quality |

## Research Plans

Per-component research executed in Phase 2:

| Component | Research Plan |
|-----------|---------------|
| Skills | [research/plans/1-skills.md](research/plans/1-skills.md) |
| Agents | [research/plans/2-agents.md](research/plans/2-agents.md) |
| Commands | [research/plans/3-commands.md](research/plans/3-commands.md) |
| Rules | [research/plans/4-rules.md](research/plans/4-rules.md) |
| Prompts | [research/plans/5-prompts.md](research/plans/5-prompts.md) |
| Hooks | [research/plans/6-hooks.md](research/plans/6-hooks.md) |
| MCP | [research/plans/7-mcp.md](research/plans/7-mcp.md) |
| Plugins | [research/plans/8-plugins.md](research/plans/8-plugins.md) |

## Analysis Plans

| Analysis | Plan | Purpose |
|----------|------|---------|
| Tool Evaluation | [analysis/plans/tool-evaluation.md](analysis/plans/tool-evaluation.md) | Determine best search tools |
| Registry Completeness | [analysis/plans/registry-completeness.md](analysis/plans/registry-completeness.md) | Assess registry coverage |

## Execution Timeline

| Phase | Duration | Dependencies | Parallelizable |
|-------|----------|--------------|----------------|
| 0 | 0.5 day | None | No |
| 1 | 1 day | Phase 0 | No |
| 2 | 2 days | Phase 1 | Yes (per component) |
| 3 | 1 day | Phase 2 | No |
| 4 | 1 day | Phase 2 | Yes (with Phase 3) |
| 5 | 1 day | Phase 3, 4 | No |
| 6 | 0.5 day | Phase 5 | No |

**Total: 7 days** (with parallelization)

## Success Criteria

- [ ] Search term matrix covers all 8 categories
- [ ] Tool comparison identifies best tools per source
- [ ] All 8 component types have registry/repo listings
- [ ] API documentation for 80%+ of independent sites
- [ ] robots.txt and rate limits documented
- [ ] Unified index searchable in <100ms
- [ ] 80% recall on baseline components
- [ ] Plugin bundling relationships captured

## Ownership

**Executor:** Single agent/developer
**Stakeholder:** Plugin ecosystem maintainers
