# Research Plan: MCP Servers Discovery

## Objective

Discover and inventory all MCP server registries and repositories.

## Scope

- **Component type:** mcp
- **File patterns:** `.mcp.json`, `mcp-server-*`, MCP configurations
- **Sources:** Independent sites, GitHub repos, npm/PyPI

---

## Search Terms

From search term matrix:

| Category | Terms |
|----------|-------|
| Primary | `mcp server`, `model context protocol`, `mcp claude` |
| Synonyms | `tool server`, `context server`, `integration` |
| Narrower | `.mcp.json`, `mcp-server-*`, `@modelcontextprotocol` |
| Broader | `claude tools`, `llm tools`, `ai integration` |

---

## Known Registries

| Registry | URL | Priority |
|----------|-----|----------|
| smithery | <https://smithery.ai/> | High |
| glama | <https://glama.ai/mcp/servers> | High |
| mcp.so | <https://mcp.so/> | High |
| mcpservers.org | <https://mcpservers.org/> | High |
| mcphub.io | <https://mcphub.io/> | Medium |
| mcpregistry | <https://mcpregistry.com/> | Medium |
| punkpeye | <https://punkpeye.github.io/awesome-mcp-servers/> | Medium |
| cursor.directory | <https://cursor.directory/mcp> | Low |
| lobehub | <https://lobehub.com/> | Low |

## Known GitHub Repos

| Repository | Expected MCP Servers |
|------------|----------------------|
| modelcontextprotocol/servers | Official servers |
| punkpeye/awesome-mcp-servers | Curated list |
| wong2/awesome-mcp-servers | Curated list |

---

## Experiments

### Experiment A: Registry Probe

```yaml
experiment:
  id: "exp-mcp-registry"
  title: "Probe MCP registries"

  procedure:
    - Fetch each registry URL
    - Count MCP server listings
    - Check for API documentation
    - Test search functionality
    - Document rate limits
```

### Experiment B: GitHub Search

```yaml
experiment:
  id: "exp-mcp-github"
  title: "Search GitHub for MCP servers"

  queries:
    - 'topic:mcp-server'
    - 'filename:mcp.json'
    - '"@modelcontextprotocol/sdk"'
    - 'mcp-server- language:typescript'
    - 'mcp-server- language:python'
```

### Experiment C: Package Search

```yaml
experiment:
  id: "exp-mcp-packages"

  searches:
    - npm: "@modelcontextprotocol", "mcp-server"
    - pypi: "mcp-server", "modelcontextprotocol"
```

---

## Tasks

### Independent Sites
- [ ] Fetch smithery and document API
- [ ] Fetch glama and document structure
- [ ] Fetch mcp.so and test search
- [ ] Fetch mcpservers.org and analyze
- [ ] Check remaining registries
- [ ] Document robots.txt for each

### GitHub
- [ ] Run all search queries
- [ ] Fetch READMEs from top repos
- [ ] Count MCP servers per repo
- [ ] Record star counts and last updated

### Packages
- [ ] Search npm for MCP packages
- [ ] Search PyPI for MCP packages

---

## Results Path

`research/results/mcp/`

---

## Deliverables

- `research/results/mcp/registries.yaml`
- `research/results/mcp/github-repos.yaml`
- `research/results/mcp/packages.yaml`
- `research/results/mcp/api-docs.yaml`

---

## Success Criteria

- [ ] All 9 known registries verified
- [ ] 20+ GitHub repos identified
- [ ] Package search completed
- [ ] API docs captured for top registries
