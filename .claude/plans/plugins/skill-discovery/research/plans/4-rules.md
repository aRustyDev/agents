# Research Plan: Rules Discovery

## Objective

Discover and inventory all rule registries and repositories.

## Scope

- **Component type:** rule
- **File patterns:** `*.md` in `rules/`, `.claude/rules/`, rule definitions
- **Sources:** Independent sites, GitHub repos

---

## Search Terms

From search term matrix:

| Category | Terms |
|----------|-------|
| Primary | `claude rule`, `claude code rule`, `project rule` |
| Synonyms | `constraint`, `guideline`, `policy`, `directive` |
| Narrower | `.claude/rules/`, `CLAUDE.md rules`, `rule:` |
| Broader | `claude code`, `ai constraint`, `coding standard` |

---

## Known Registries

| Registry | URL | Priority |
|----------|-----|----------|
| skillsmp | <https://skillsmp.com/> | High |
| ccpm | <https://ccpm.dev/> | High |

## Known GitHub Repos

| Repository | Expected Rules |
|------------|----------------|
| anthropics/claude-code | Official rules |
| hesreallyhim/awesome-claude-code | Curated list |

---

## Experiments

### Experiment A: Registry Probe

```yaml
experiment:
  id: "exp-rules-registry"
  title: "Probe registries for rule listings"

  procedure:
    - Fetch each registry URL
    - Search for "rule" filter/category
    - Count rule listings
    - Document rule patterns
```

### Experiment B: GitHub Search

```yaml
experiment:
  id: "exp-rules-github"
  title: "Search GitHub for rule definitions"

  queries:
    - 'path:.claude/rules/ language:markdown'
    - '"claude rule" OR "project rule"'
    - 'path:rules/ "CLAUDE.md" language:markdown'
    - 'topic:claude-rules'
```

### Experiment C: CLAUDE.md Analysis

```yaml
experiment:
  id: "exp-rules-claudemd"
  title: "Analyze CLAUDE.md files for embedded rules"

  procedure:
    - Search GitHub for CLAUDE.md files
    - Extract rule sections
    - Categorize rule patterns
```

---

## Tasks

### Independent Sites
- [ ] Check skillsmp for rule category
- [ ] Check ccpm for rule listings
- [ ] Document robots.txt for each

### GitHub
- [ ] Run all search queries
- [ ] Analyze CLAUDE.md rule sections
- [ ] Count rules per repo
- [ ] Document rule patterns

### Analysis
- [ ] Categorize rule types
- [ ] Document enforcement mechanisms

---

## Results Path

`research/results/rules/`

---

## Deliverables

- `research/results/rules/registries.yaml`
- `research/results/rules/github-repos.yaml`
- `research/results/rules/patterns.yaml`

---

## Success Criteria

- [ ] All known registries verified
- [ ] 5+ GitHub repos identified
- [ ] Rule structure documented
- [ ] Rule categories identified
