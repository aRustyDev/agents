# Research Plan: Prompts Discovery

## Objective

Discover and inventory all prompt template registries and repositories.

## Scope

- **Component type:** prompt
- **File patterns:** `prompts/`, `*.prompt.md`, prompt templates
- **Sources:** Independent sites, GitHub repos, prompt libraries

---

## Search Terms

From search term matrix:

| Category | Terms |
|----------|-------|
| Primary | `claude prompt`, `prompt template`, `claude code prompt` |
| Synonyms | `system prompt`, `instruction`, `template` |
| Narrower | `prompts/`, `.prompt.md`, `system_prompt` |
| Broader | `llm prompt`, `ai prompt`, `prompt engineering` |

---

## Known Registries

| Registry | URL | Priority |
|----------|-----|----------|
| skillsmp | <https://skillsmp.com/> | High |
| ccpm | <https://ccpm.dev/> | High |
| promptbase | <https://promptbase.com/> | Medium |
| flowgpt | <https://flowgpt.com/> | Medium |

## Known GitHub Repos

| Repository | Expected Prompts |
|------------|------------------|
| anthropics/prompt-library | Official prompts |
| f/awesome-chatgpt-prompts | General prompts |

---

## Experiments

### Experiment A: Registry Probe

```yaml
experiment:
  id: "exp-prompts-registry"
  title: "Probe registries for prompt listings"

  procedure:
    - Fetch each registry URL
    - Search for "prompt" filter/category
    - Count prompt listings
    - Document prompt formats
```

### Experiment B: GitHub Search

```yaml
experiment:
  id: "exp-prompts-github"
  title: "Search GitHub for prompt templates"

  queries:
    - 'path:prompts/ claude language:markdown'
    - '"system prompt" claude'
    - 'filename:*.prompt.md'
    - 'topic:claude-prompts'
    - '"prompt template" anthropic'
```

### Experiment C: Prompt Library Search

```yaml
experiment:
  id: "exp-prompts-libraries"
  title: "Search prompt libraries"

  procedure:
    - Search PromptBase for Claude prompts
    - Search FlowGPT for Claude prompts
    - Document pricing/access models
```

---

## Tasks

### Independent Sites
- [ ] Check skillsmp for prompt category
- [ ] Check ccpm for prompt listings
- [ ] Check PromptBase for Claude prompts
- [ ] Check FlowGPT for Claude prompts
- [ ] Document robots.txt for each

### GitHub
- [ ] Run all search queries
- [ ] Count prompts per repo
- [ ] Document prompt formats

### Analysis
- [ ] Categorize prompt types
- [ ] Document variable patterns

---

## Results Path

`research/results/prompts/`

---

## Deliverables

- `research/results/prompts/registries.yaml`
- `research/results/prompts/github-repos.yaml`
- `research/results/prompts/formats.yaml`

---

## Success Criteria

- [ ] All known registries verified
- [ ] 5+ GitHub repos identified
- [ ] Prompt formats documented
- [ ] Variable patterns cataloged
