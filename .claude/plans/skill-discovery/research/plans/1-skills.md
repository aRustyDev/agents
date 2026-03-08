# Research Plan: Skills Discovery

## Objective

Discover and inventory all skill registries and repositories.

## Scope

- **Component type:** skill
- **File patterns:** `SKILL.md`, `skills/`, `skill-*.md`
- **Sources:** Independent sites, GitHub repos, npm/PyPI

---

## Search Terms

From search term matrix:

| Category | Terms |
|----------|-------|
| Primary | `claude skill`, `agent skill`, `claude code skill` |
| Synonyms | `capability`, `knowledge module`, `domain knowledge` |
| Narrower | `SKILL.md`, `skill-creator`, `/skills/` |
| Broader | `claude code`, `ai assistant`, `llm skill` |

---

## Known Registries

| Registry | URL | Priority |
|----------|-----|----------|
| skillsmp | <https://skillsmp.com/> | High |
| ccpm | <https://ccpm.dev/> | High |
| claude-plugins.dev | <https://claude-plugins.dev/> | High |
| agentskills.best | <https://agentskills.best/> | High |
| claudeskillsmarket | <https://claudeskillsmarket.com/> | Medium |
| claudecodemarketplace | <https://claudecodemarketplace.com/> | Medium |
| mcpservers.org/skills | <https://mcpservers.org/claude-skills> | Medium |
| atcyrus | <https://www.atcyrus.com/skills> | Medium |
| awesome-claude-code.com | <https://awesome-claude-code.com/> | Medium |
| awesomeclaude.ai | <https://awesomeclaude.ai/> | Low |
| lobehub | <https://lobehub.com/> | Low |
| notion-skills | Notion page | Low |

## Known GitHub Repos

| Repository | Expected Skills |
|------------|-----------------|
| anthropics/skills | 17 official |
| trailofbits/skills | 35 security |
| obra/superpowers | 14 workflow |
| hesreallyhim/awesome-claude-code | Curated list |
| VoltAgent/awesome-claude-code-subagents | 100+ subagents |
| travisvn/awesome-claude-skills | Curated index |
| ComposioHQ/awesome-claude-skills | Productivity |
| Jeffallan/claude-skills | 66 full-stack |
| alirezarezvani/claude-skills | 42 enterprise |
| wshobson/agents | 47 skills |
| tech-leads-club/agent-skills | TBD |

## Related Ecosystems

| Ecosystem | URL |
|-----------|-----|
| Goose Skills | <https://block.github.io/goose/skills/> |
| OpenClaw | lobehub registry |

---

## Experiments

### Experiment A: Registry Probe

```yaml
experiment:
  id: "exp-skills-registry"
  title: "Probe skill registries"

  procedure:
    - Fetch each registry URL
    - Check for API docs
    - Test search functionality
    - Document rate limits
```

### Experiment B: GitHub Search

```yaml
experiment:
  id: "exp-skills-github"
  title: "Search GitHub for skill repos"

  queries:
    - 'filename:SKILL.md claude'
    - 'path:skills/ SKILL.md'
    - 'topic:claude-skills'
    - '"awesome-claude" skill'
    - 'org:anthropics skills'
```

### Experiment C: Package Search

```yaml
experiment:
  id: "exp-skills-packages"

  searches:
    - npm: "claude-skill", "claude-code-skill"
    - pypi: "claude-skill"
    - crates: "claude-skill"
```

---

## Tasks

### Independent Sites
- [ ] Fetch skillsmp.com and document API
- [ ] Fetch ccpm.dev and document structure
- [ ] Fetch claude-plugins.dev and test search
- [ ] Fetch agentskills.best and analyze
- [ ] Check remaining registries
- [ ] Document robots.txt for each

### GitHub
- [ ] Run all search queries
- [ ] Fetch READMEs from top repos
- [ ] Count skills per repo
- [ ] Record star counts and last updated

### Packages
- [ ] Search npm
- [ ] Search PyPI
- [ ] Search crates.io

---

## Results Path

`research/results/skills/`

---

## Deliverables

- `research/results/skills/registries.yaml`
- `research/results/skills/github-repos.yaml`
- `research/results/skills/packages.yaml`
- `research/results/skills/api-docs.yaml`

---

## Success Criteria

- [ ] All 12 known registries verified
- [ ] 20+ GitHub repos identified
- [ ] Package search completed
- [ ] API docs captured for top registries
