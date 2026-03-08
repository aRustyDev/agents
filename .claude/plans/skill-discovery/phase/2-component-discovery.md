# Phase 2: Component Discovery

## Objective

Execute research plans for all 7 base component types in parallel.

## Duration

2 days (parallelizable)

## Dependencies

- Phase 0 (search term matrix)
- Phase 1 (tool selection)

---

## Execution Pattern

For each component type, execute its research plan:

| Component | Research Plan | Results Path |
|-----------|---------------|--------------|
| Skills | [research/plans/1-skills.md](../research/plans/1-skills.md) | `research/results/skills/` |
| Agents | [research/plans/2-agents.md](../research/plans/2-agents.md) | `research/results/agents/` |
| Commands | [research/plans/3-commands.md](../research/plans/3-commands.md) | `research/results/commands/` |
| Rules | [research/plans/4-rules.md](../research/plans/4-rules.md) | `research/results/rules/` |
| Prompts | [research/plans/5-prompts.md](../research/plans/5-prompts.md) | `research/results/prompts/` |
| Hooks | [research/plans/6-hooks.md](../research/plans/6-hooks.md) | `research/results/hooks/` |
| MCP | [research/plans/7-mcp.md](../research/plans/7-mcp.md) | `research/results/mcp/` |

---

## Experiment Template Per Component

Each component discovery uses three experiments:

### Experiment A: Registry Search

```yaml
experiment:
  id: "exp-{type}-registry"
  title: "Discover {type} registries"

  inputs:
    search_terms: # From search term matrix
    tools: # From Phase 1 recommendations

  procedure:
    - step: 1
      action: "WebSearch for '{type} registry claude'"
    - step: 2
      action: "Verify each result with WebFetch"
    - step: 3
      action: "Record in registries.yaml"
```

### Experiment B: GitHub Search

```yaml
experiment:
  id: "exp-{type}-github"
  title: "Discover {type} GitHub repos"

  inputs:
    queries:
      - 'filename:{TYPE}.md claude'
      - 'path:{type}s/'
      - 'topic:claude-{type}'
      - '"awesome-claude" {type}'

  procedure:
    - step: 1
      action: "gh api search/repositories for each query"
    - step: 2
      action: "Fetch README for top results"
    - step: 3
      action: "Count components per repo"
```

### Experiment C: Package Search

```yaml
experiment:
  id: "exp-{type}-packages"
  title: "Discover {type} packages"

  inputs:
    registries: ["npm", "pypi", "crates.io"]
    terms: ["claude-{type}", "claude-code-{type}"]

  procedure:
    - step: 1
      action: "Search each package registry"
    - step: 2
      action: "Record package names and descriptions"
```

---

## Result Schema Per Component

Each component produces:

```yaml
# research/results/{type}/registries.yaml
registries:
  - name: ""
    url: ""
    status: "active|inactive|unknown"
    component_count: 0
    api_docs: ""
    robots_txt: ""
    rate_limit: ""

# research/results/{type}/github-repos.yaml
github_repos:
  - name: ""
    url: ""
    stars: 0
    last_updated: ""
    component_count: 0
    readme_lists_components: true|false

# research/results/{type}/packages.yaml
packages:
  - registry: "npm|pypi|crates"
    name: ""
    version: ""
    downloads: 0
    description: ""
```

---

## Parallel Execution

Run component discoveries in parallel using Task tool:

```
Task(subagent_type="Explore", prompt="Execute research/plans/1-skills.md")
Task(subagent_type="Explore", prompt="Execute research/plans/2-agents.md")
# ... etc
```

---

## Observations During Execution

Record in `analysis/findings/phase-2-observations.yaml`:

```yaml
observations:
  - timestamp: "2026-03-08T14:30:00Z"
    component: "skills"
    type: "insight"
    description: "skillsmp.com has most comprehensive search API"

  - timestamp: "2026-03-08T15:00:00Z"
    component: "rules"
    type: "anomaly"
    description: "No dedicated rule registries found - rules bundled in other repos"
```

---

## Aggregation After Completion

After all components complete, create summary:

```yaml
# analysis/findings/component-coverage.yaml
finding:
  id: "finding-002-component-coverage"
  title: "Component type coverage summary"

  supporting_data:
    - component: "skills"
      registries_found: 12
      github_repos: 25
      packages: 5
    - component: "agents"
      registries_found: 3
      github_repos: 15
      packages: 2
    # ...

  recommendations:
    - "Skills have richest ecosystem - prioritize"
    - "Rules/prompts lack dedicated registries - search within plugins"
```

---

## Deliverables

For each component type:
- `research/results/{type}/registries.yaml`
- `research/results/{type}/github-repos.yaml`
- `research/results/{type}/packages.yaml`

Summary:
- `analysis/findings/component-coverage.yaml`

---

## Success Gate

| Criterion | Target |
|-----------|--------|
| Component types researched | 7/7 |
| Registries per type | 3+ (or documented as sparse) |
| GitHub repos per type | 10+ |
| Package search completed | All 3 registries |
| Observations recorded | Yes |

## Checklist

Use: `checklists/schemas/research-execution.schema.json`

Record: `checklists/instances/phase-2-{type}.json` per component
