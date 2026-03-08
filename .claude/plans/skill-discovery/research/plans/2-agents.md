# Research Plan: Agents Discovery

## Objective

Discover and inventory all agent registries and repositories.

## Scope

- **Component type:** agent
- **File patterns:** `AGENT.md`, `agents/`, `agent-*.md`, `.claude/agents/`
- **Sources:** Independent sites, GitHub repos, npm/PyPI

---

## Search Terms

From search term matrix:

| Category | Terms |
|----------|-------|
| Primary | `claude agent`, `claude code agent`, `subagent` |
| Synonyms | `assistant`, `specialist`, `expert`, `orchestrator` |
| Narrower | `AGENT.md`, `.claude/agents/`, `subagent_type` |
| Broader | `claude code`, `ai agent`, `llm agent` |

---

## Known Registries

| Registry | URL | Priority |
|----------|-----|----------|
| skillsmp | <https://skillsmp.com/> | High |
| ccpm | <https://ccpm.dev/> | High |
| claude-plugins.dev | <https://claude-plugins.dev/> | High |
| agentskills.best | <https://agentskills.best/> | High |
| awesome-claude-code.com | <https://awesome-claude-code.com/> | Medium |

## Known GitHub Repos

| Repository | Expected Agents |
|------------|-----------------|
| VoltAgent/awesome-claude-code-subagents | 100+ subagents |
| anthropics/claude-code | Official agents |
| hesreallyhim/awesome-claude-code | Curated list |

---

## Experiments

### Experiment A: Registry Probe

```yaml
experiment:
  id: "exp-agents-registry"
  title: "Probe registries for agent listings"

  procedure:
    - Fetch each registry URL
    - Search for "agent" filter/category
    - Count agent listings
    - Document API endpoints
```

### Experiment B: GitHub Search

```yaml
experiment:
  id: "exp-agents-github"
  title: "Search GitHub for agent definitions"

  queries:
    - 'filename:AGENT.md claude'
    - 'path:.claude/agents/ "subagent_type"'
    - 'topic:claude-agents'
    - '"awesome-claude" agent'
    - '"subagent_type" language:markdown'
```

### Experiment C: Package Search

```yaml
experiment:
  id: "exp-agents-packages"

  searches:
    - npm: "claude-agent", "claude-code-agent"
    - pypi: "claude-agent"
```

---

## Tasks

### Independent Sites
- [ ] Check skillsmp for agent category
- [ ] Check ccpm for agent listings
- [ ] Check claude-plugins.dev for agents
- [ ] Check agentskills.best structure
- [ ] Document robots.txt for each

### GitHub
- [ ] Run all search queries
- [ ] Fetch README from awesome-claude-code-subagents
- [ ] Count agents per repo
- [ ] Record star counts and last updated

### Packages
- [ ] Search npm
- [ ] Search PyPI

---

## Results Path

`research/results/agents/`

---

## Deliverables

- `research/results/agents/registries.yaml`
- `research/results/agents/github-repos.yaml`
- `research/results/agents/packages.yaml`

---

## Success Criteria

- [ ] All known registries verified
- [ ] 10+ GitHub repos identified
- [ ] Package search completed
- [ ] Agent definition patterns documented
