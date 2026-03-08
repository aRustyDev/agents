# Research Plan: [Component Type] Discovery

## Objective

Discover and inventory all [component type] registries and repositories.

## Scope

- **Component type:** [skill | agent | command | rule | prompt | hook | mcp | plugin]
- **Sources to search:**
  - Independent site registries
  - GitHub repository collections
  - Package managers (npm, PyPI, crates.io)

## Search Terms

From the search term matrix:

| Category | Terms |
|----------|-------|
| Primary | |
| Synonyms | |
| Narrower | |
| Broader | |

## Experiments

| Experiment | Purpose | Template |
|------------|---------|----------|
| Registry probe | Test each registry URL | `registry-probe.yaml` |
| GitHub search | Search for repos | `github-search.yaml` |
| Package search | Search npm/PyPI | `package-search.yaml` |

## Evidence to Gather

- [ ] Registry homepage content
- [ ] API documentation (if available)
- [ ] robots.txt for each registry
- [ ] GitHub repo metadata (stars, last commit)
- [ ] Package counts from npm/PyPI

## Tasks

### Independent Site Registries

- [ ] Fetch each registry URL
- [ ] Document API endpoints
- [ ] Check robots.txt
- [ ] Test search functionality
- [ ] Document rate limits

### GitHub Repository Collections

- [ ] Run GitHub search queries
- [ ] Analyze repo structure
- [ ] Count components per repo
- [ ] Document README for listings

### Package Managers

- [ ] Search npm for `claude-[type]`
- [ ] Search PyPI for `claude-[type]`
- [ ] Search crates.io for `claude-[type]`

## Success Criteria

- [ ] All known registries verified (active/inactive)
- [ ] API documentation captured for 80%+ of active registries
- [ ] robots.txt analyzed for each registry
- [ ] 10+ GitHub repos identified
- [ ] Package search completed

## Results Path

`research/results/[component-type]/`

## Dependencies

- **Requires:** Phase 0 (search term matrix), Phase 1 (tool selection)
- **Enables:** Phase 5 (aggregation)

## Deliverables

- `research/results/[type]/registries.yaml`
- `research/results/[type]/github-repos.yaml`
- `research/results/[type]/packages.yaml`
- `research/results/[type]/api-docs.yaml`
