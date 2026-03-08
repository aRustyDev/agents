# Claude Code Component Discovery

> **Source of Truth** — This file and the `phase/`, `research/`, `analysis/` directories are the authoritative plan. See `research-plan.ARCHIVED.md` for historical context.

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
├── PLAN.md                          # This file (source of truth)
├── analysis/
│   ├── evidence/                    # External references
│   │   └── templates/evidence.yaml
│   ├── experiments/                 # Experiment definitions
│   │   └── templates/experiment.yaml
│   ├── findings/                    # Conclusions from experiments
│   │   └── templates/finding.yaml
│   ├── plans/                       # Analysis strategies
│   │   ├── tool-evaluation.md
│   │   └── registry-completeness.md
│   ├── reports/                     # Final deliverables
│   └── results/                     # Raw experiment data
│       └── templates/result.yaml
├── checklists/
│   ├── instances/                   # Completed checklist records
│   └── schemas/                     # JSON validation schemas
│       ├── data-aggregation.schema.json
│       ├── data-validation.schema.json
│       ├── research-execution.schema.json
│       ├── research-planning.schema.json
│       └── scope-definition.schema.json
├── phase/                           # Phase execution plans
│   ├── 0-baseline-and-matrix.md
│   ├── 1-tool-experiments.md
│   ├── 2-component-discovery.md
│   ├── 3-plugin-discovery.md
│   ├── 4-api-documentation.md
│   ├── 5-aggregation.md
│   └── 6-validation.md
├── phase-0/                         # Phase 0 artifacts
│   ├── baseline-skills.yaml
│   └── registries.yaml
└── research/
    ├── plans/                       # Per-component research plans
    │   ├── 1-skills.md
    │   ├── 2-agents.md
    │   ├── 3-commands.md
    │   ├── 4-rules.md
    │   ├── 5-prompts.md
    │   ├── 6-hooks.md
    │   ├── 7-mcp.md
    │   ├── 8-plugins.md
    │   └── templates/component-research.md
    └── results/                     # Research outputs by type
        ├── skills/
        ├── agents/
        └── ...
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

## Templates

Use these templates for consistent documentation:

| Template | Path | Purpose |
|----------|------|---------|
| Experiment | [analysis/experiments/templates/experiment.yaml](analysis/experiments/templates/experiment.yaml) | Define hypothesis, procedure, metrics |
| Result | [analysis/results/templates/result.yaml](analysis/results/templates/result.yaml) | Record raw experiment data |
| Finding | [analysis/findings/templates/finding.yaml](analysis/findings/templates/finding.yaml) | Document claims with evidence |
| Evidence | [analysis/evidence/templates/evidence.yaml](analysis/evidence/templates/evidence.yaml) | Capture external references |
| Research | [research/plans/templates/component-research.md](research/plans/templates/component-research.md) | Component discovery template |

## Checklists

Validate phase completion with JSON schemas:

| Checklist | Schema | Used In |
|-----------|--------|---------|
| Scope Definition | [checklists/schemas/scope-definition.schema.json](checklists/schemas/scope-definition.schema.json) | Phase 0 |
| Research Planning | [checklists/schemas/research-planning.schema.json](checklists/schemas/research-planning.schema.json) | Phase 0-1 |
| Research Execution | [checklists/schemas/research-execution.schema.json](checklists/schemas/research-execution.schema.json) | Phase 2-4 |
| Data Validation | [checklists/schemas/data-validation.schema.json](checklists/schemas/data-validation.schema.json) | Phase 4, 6 |
| Data Aggregation | [checklists/schemas/data-aggregation.schema.json](checklists/schemas/data-aggregation.schema.json) | Phase 5 |

Record completed checklists in `checklists/instances/phase-N.json`.

## Evidence & Finding Process

### Recording Evidence

When discovering external information:

1. Create evidence file: `analysis/evidence/<source>-<date>.yaml`
2. Include: source URL, access date, content hash, relevance
3. Reference in findings and results

### Documenting Findings

When drawing conclusions from experiments:

1. Create finding file: `analysis/findings/<finding-id>.yaml`
2. Link to supporting experiment IDs
3. State confidence level (high/medium/low)
4. Include actionable recommendations

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation | Rollback |
|------|------------|--------|------------|----------|
| Registry API undocumented | Medium | Medium | Manual exploration, network inspection | Use cached results |
| Rate limits block progress | Medium | High | Caching, delays, tool rotation | Switch to alternate tool |
| robots.txt blocks crawling | Low | Medium | Use search APIs instead | Document as "API only" |
| Sparse registries for some types | High | Low | Focus on GitHub patterns | Note gap in findings |
| Plugin structure varies | Medium | Medium | Flexible schema, manual review | Capture raw structure |

### Recovery Checkpoints

Each phase creates checkpoints for recovery:

| Phase | Checkpoint | Recovery Action |
|-------|------------|-----------------|
| 0 | `phase-0/baseline-*.yaml` | Restart from baseline |
| 1 | `analysis/results/tool-comparison-*.yaml` | Rerun failed tool only |
| 2 | `research/results/<type>/` | Rerun single component type |
| 3 | `research/results/plugins/` | Rerun plugin discovery |
| 4 | `analysis/results/registry-api-*.yaml` | Rerun single registry |
| 5 | `component-index.db` | Rebuild from YAML results |
| 6 | `analysis/results/validation.yaml` | Rerun validation queries |

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
