# Research Plan: Hooks Discovery

## Objective

Discover and inventory all hook registries and repositories.

## Scope

- **Component type:** hook
- **File patterns:** `hooks/`, `hooks.json`, lifecycle hooks
- **Sources:** Independent sites, GitHub repos

---

## Search Terms

From search term matrix:

| Category | Terms |
|----------|-------|
| Primary | `claude hook`, `claude code hook`, `lifecycle hook` |
| Synonyms | `interceptor`, `callback`, `event handler` |
| Narrower | `hooks.json`, `PreToolUse`, `PostToolUse`, `Notification` |
| Broader | `claude code`, `git hook`, `automation` |

---

## Known Registries

| Registry | URL | Priority |
|----------|-----|----------|
| skillsmp | <https://skillsmp.com/> | High |
| ccpm | <https://ccpm.dev/> | High |

## Known GitHub Repos

| Repository | Expected Hooks |
|------------|----------------|
| anthropics/claude-code | Official hooks |
| hesreallyhim/awesome-claude-code | Curated list |

---

## Experiments

### Experiment A: Registry Probe

```yaml
experiment:
  id: "exp-hooks-registry"
  title: "Probe registries for hook listings"

  procedure:
    - Fetch each registry URL
    - Search for "hook" filter/category
    - Count hook listings
    - Document hook patterns
```

### Experiment B: GitHub Search

```yaml
experiment:
  id: "exp-hooks-github"
  title: "Search GitHub for hook definitions"

  queries:
    - 'filename:hooks.json claude'
    - 'path:hooks/ "PreToolUse" OR "PostToolUse"'
    - '"claude hook" language:json'
    - 'topic:claude-hooks'
    - '"Notification" "Stop" hook'
```

### Experiment C: Settings Analysis

```yaml
experiment:
  id: "exp-hooks-settings"
  title: "Analyze settings.json hook configurations"

  procedure:
    - Search GitHub for .claude/settings.json
    - Extract hook configurations
    - Categorize hook types
```

---

## Tasks

### Independent Sites
- [ ] Check skillsmp for hook category
- [ ] Check ccpm for hook listings
- [ ] Document robots.txt for each

### GitHub
- [ ] Run all search queries
- [ ] Analyze settings.json hook sections
- [ ] Count hooks per repo
- [ ] Document hook patterns

### Analysis
- [ ] Categorize hook types (PreToolUse, PostToolUse, etc.)
- [ ] Document event types

---

## Results Path

`research/results/hooks/`

---

## Deliverables

- `research/results/hooks/registries.yaml`
- `research/results/hooks/github-repos.yaml`
- `research/results/hooks/patterns.yaml`

---

## Success Criteria

- [ ] All known registries verified
- [ ] 5+ GitHub repos identified
- [ ] Hook event types documented
- [ ] Hook patterns cataloged
