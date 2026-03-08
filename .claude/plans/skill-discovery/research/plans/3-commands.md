# Research Plan: Commands Discovery

## Objective

Discover and inventory all slash command registries and repositories.

## Scope

- **Component type:** command
- **File patterns:** `*.md` in `commands/`, `.claude/commands/`, slash command definitions
- **Sources:** Independent sites, GitHub repos, npm/PyPI

---

## Search Terms

From search term matrix:

| Category | Terms |
|----------|-------|
| Primary | `claude command`, `slash command`, `claude code command` |
| Synonyms | `workflow`, `macro`, `shortcut` |
| Narrower | `.claude/commands/`, `/command`, `slash-command` |
| Broader | `claude code`, `cli command`, `ai workflow` |

---

## Known Registries

| Registry | URL | Priority |
|----------|-----|----------|
| skillsmp | <https://skillsmp.com/> | High |
| ccpm | <https://ccpm.dev/> | High |
| claude-plugins.dev | <https://claude-plugins.dev/> | High |

## Known GitHub Repos

| Repository | Expected Commands |
|------------|-------------------|
| anthropics/claude-code | Official commands |
| hesreallyhim/awesome-claude-code | Curated list |

---

## Experiments

### Experiment A: Registry Probe

```yaml
experiment:
  id: "exp-commands-registry"
  title: "Probe registries for command listings"

  procedure:
    - Fetch each registry URL
    - Search for "command" filter/category
    - Count command listings
    - Document command invocation patterns
```

### Experiment B: GitHub Search

```yaml
experiment:
  id: "exp-commands-github"
  title: "Search GitHub for command definitions"

  queries:
    - 'path:.claude/commands/ language:markdown'
    - '"slash command" claude'
    - 'path:commands/ "# /" language:markdown'
    - 'topic:claude-commands'
```

### Experiment C: Documentation Search

```yaml
experiment:
  id: "exp-commands-docs"
  title: "Search official documentation"

  procedure:
    - Check Anthropic docs for command patterns
    - Search for community command tutorials
```

---

## Tasks

### Independent Sites
- [ ] Check skillsmp for command category
- [ ] Check ccpm for command listings
- [ ] Check claude-plugins.dev for commands
- [ ] Document robots.txt for each

### GitHub
- [ ] Run all search queries
- [ ] Count commands per repo
- [ ] Record command naming patterns

### Documentation
- [ ] Review official Claude Code docs
- [ ] Document command structure requirements

---

## Results Path

`research/results/commands/`

---

## Deliverables

- `research/results/commands/registries.yaml`
- `research/results/commands/github-repos.yaml`
- `research/results/commands/patterns.yaml`

---

## Success Criteria

- [ ] All known registries verified
- [ ] 5+ GitHub repos identified
- [ ] Command structure documented
- [ ] Naming conventions cataloged
