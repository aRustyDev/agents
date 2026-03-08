# Phase 3: Plugin Discovery

## Objective

Discover plugin registries and repositories. Plugins are composite packages that bundle base component types (skills, agents, commands, rules, hooks, MCP).

## Duration

1 day

## Dependencies

- Phase 2 (base component discovery must complete first)

---

## Why Plugins Are Last

Plugins **bundle** other component types:

```
Plugin
├── skills/
├── agents/
├── commands/
├── rules/
├── hooks/
└── .mcp.json
```

Understanding base components first helps us:
1. Recognize when a plugin bundles known components
2. Avoid double-counting components
3. Map plugin → component relationships

---

## Known Plugin Registries

| Registry | URL | Status |
|----------|-----|--------|
| claudemarketplaces | <https://claudemarketplaces.com/> | TBD |
| buildwithclaude | <https://buildwithclaude.com/> | TBD |
| clauderegistry | <https://clauderegistry.com/> | TBD |
| litellm docs | <https://docs.litellm.ai/docs/tutorials/claude_code_plugin_marketplace> | TBD |
| paddo.dev | <https://paddo.dev/blog/claude-tools-plugin-marketplace/> | TBD |
| composio | <https://composio.dev/blog/top-claude-code-plugins> | TBD |

## Known Plugin GitHub Repos

| Repository | URL |
|------------|-----|
| ananddtyagi/cc-marketplace | <https://github.com/ananddtyagi/cc-marketplace> |
| Kamalnrf/claude-plugins | <https://github.com/Kamalnrf/claude-plugins> |

---

## Experiment: Plugin Registry Probe

Create: `analysis/experiments/3-plugin-registry-probe.md`

```yaml
experiment:
  id: "exp-003-plugin-registry"
  title: "Probe plugin registries for structure and API"

  inputs:
    registries:
      - url: "https://claudemarketplaces.com/"
      - url: "https://buildwithclaude.com/"
      - url: "https://clauderegistry.com/"

  procedure:
    - step: 1
      action: "WebFetch homepage"
      expected: "Plugin listings"
    - step: 2
      action: "Check for API documentation"
      expected: "API endpoints or 404"
    - step: 3
      action: "Sample 5 plugins"
      expected: "Plugin structure data"
    - step: 4
      action: "Identify bundled components"
      expected: "List of skills/agents/etc per plugin"
```

---

## Experiment: Plugin Structure Analysis

Create: `analysis/experiments/4-plugin-structure.md`

```yaml
experiment:
  id: "exp-004-plugin-structure"
  title: "Analyze plugin bundling patterns"

  inputs:
    sample_plugins: 20  # Random sample from discoveries

  procedure:
    - step: 1
      action: "Fetch plugin.json or manifest"
      expected: "Component listings"
    - step: 2
      action: "Categorize bundled components"
      expected: "Count per type"
    - step: 3
      action: "Cross-reference with Phase 2 discoveries"
      expected: "Known vs new components"
```

---

## Result Schema

```yaml
# research/results/plugins/registries.yaml
registries:
  - name: "claudemarketplaces"
    url: "https://claudemarketplaces.com/"
    status: "active"
    plugin_count: 0
    api_docs: ""
    has_search: true|false

# research/results/plugins/github-repos.yaml
github_repos:
  - name: "cc-marketplace"
    url: "https://github.com/ananddtyagi/cc-marketplace"
    plugin_count: 0

# research/results/plugins/plugin-structures.yaml
plugins:
  - name: "example-plugin"
    source: "github:user/repo"
    bundled_components:
      skills: ["skill-a", "skill-b"]
      agents: ["agent-x"]
      commands: ["/cmd1"]
      rules: []
      hooks: ["post-tool"]
      mcp_servers: ["server-a"]
    is_new_components: 3  # Components not seen in Phase 2
    is_known_components: 4  # Components already discovered
```

---

## Finding: Plugin Bundling Patterns

After analysis, create:

```yaml
# analysis/findings/plugin-bundling.yaml
finding:
  id: "finding-003-plugin-bundling"
  title: "Plugin component bundling patterns"

  claim: "Average plugin bundles 3-5 components; skills most common"

  supporting_data:
    - "Average skills per plugin: 2.3"
    - "Average agents per plugin: 0.8"
    - "Plugins with MCP: 45%"

  implications:
    - "Plugins are primary distribution for multi-component packages"
    - "Many plugins share common skills"

  recommendations:
    - "Index plugin → component relationships"
    - "Deduplicate components across plugins"
```

---

## Deliverables

| File | Purpose |
|------|---------|
| `research/results/plugins/registries.yaml` | Plugin registry inventory |
| `research/results/plugins/github-repos.yaml` | Plugin repo inventory |
| `research/results/plugins/plugin-structures.yaml` | Bundling analysis |
| `analysis/findings/plugin-bundling.yaml` | Pattern analysis |

---

## Success Gate

| Criterion | Target |
|-----------|--------|
| Plugin registries probed | All 6 known |
| GitHub repos identified | 5+ |
| Plugin structures analyzed | 20+ samples |
| Bundling patterns documented | Yes |

## Checklist

Use: `checklists/schemas/research-execution.schema.json`

Record: `checklists/instances/phase-3.json`
