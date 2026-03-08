# Research Plan: Plugins Discovery

## Objective

Discover and inventory all plugin registries and repositories. Plugins are composite packages that bundle base component types.

## Scope

- **Component type:** plugin
- **File patterns:** `plugin.json`, `.claude-plugin/`, plugin manifests
- **Sources:** Independent sites, GitHub repos

---

## Search Terms

From search term matrix:

| Category | Terms |
|----------|-------|
| Primary | `claude plugin`, `claude code plugin`, `plugin marketplace` |
| Synonyms | `extension`, `addon`, `package`, `bundle` |
| Narrower | `plugin.json`, `.claude-plugin/`, `marketplace` |
| Broader | `claude code`, `ai extension`, `llm plugin` |

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

## Known Registries

| Registry | URL | Priority |
|----------|-----|----------|
| claudemarketplaces | <https://claudemarketplaces.com/> | High |
| buildwithclaude | <https://buildwithclaude.com/> | High |
| clauderegistry | <https://clauderegistry.com/> | High |
| litellm docs | <https://docs.litellm.ai/docs/tutorials/claude_code_plugin_marketplace> | Medium |
| paddo.dev | <https://paddo.dev/blog/claude-tools-plugin-marketplace/> | Medium |
| composio | <https://composio.dev/blog/top-claude-code-plugins> | Medium |

## Known GitHub Repos

| Repository | URL |
|------------|-----|
| ananddtyagi/cc-marketplace | <https://github.com/ananddtyagi/cc-marketplace> |
| Kamalnrf/claude-plugins | <https://github.com/Kamalnrf/claude-plugins> |

---

## Experiments

### Experiment A: Registry Probe

```yaml
experiment:
  id: "exp-plugins-registry"
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

### Experiment B: Plugin Structure Analysis

```yaml
experiment:
  id: "exp-plugins-structure"
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

### Experiment C: GitHub Search

```yaml
experiment:
  id: "exp-plugins-github"
  title: "Search GitHub for plugin repos"

  queries:
    - 'filename:plugin.json claude'
    - 'path:.claude-plugin/'
    - 'topic:claude-plugin'
    - '"claude plugin" marketplace'
```

---

## Tasks

### Independent Sites
- [ ] Fetch claudemarketplaces and document
- [ ] Fetch buildwithclaude and document
- [ ] Fetch clauderegistry and document
- [ ] Check remaining registries
- [ ] Document robots.txt for each

### GitHub
- [ ] Run all search queries
- [ ] Fetch READMEs from plugin repos
- [ ] Count plugins per repo
- [ ] Analyze plugin manifests

### Structure Analysis
- [ ] Sample 20 plugins
- [ ] Document bundled component counts
- [ ] Cross-reference with base component discoveries

---

## Results Path

`research/results/plugins/`

---

## Deliverables

- `research/results/plugins/registries.yaml`
- `research/results/plugins/github-repos.yaml`
- `research/results/plugins/plugin-structures.yaml`

---

## Finding: Plugin Bundling Patterns

After analysis, create:

```yaml
# analysis/findings/plugin-bundling.yaml
finding:
  id: "finding-plugin-bundling"
  title: "Plugin component bundling patterns"

  claim: "Average plugin bundles 3-5 components; skills most common"

  supporting_data:
    - "Average skills per plugin: N"
    - "Average agents per plugin: N"
    - "Plugins with MCP: N%"

  implications:
    - "Plugins are primary distribution for multi-component packages"
    - "Many plugins share common skills"

  recommendations:
    - "Index plugin → component relationships"
    - "Deduplicate components across plugins"
```

---

## Success Criteria

- [ ] All 6 known plugin registries probed
- [ ] 5+ GitHub repos identified
- [ ] 20+ plugin structures analyzed
- [ ] Bundling patterns documented
- [ ] Component relationships mapped
