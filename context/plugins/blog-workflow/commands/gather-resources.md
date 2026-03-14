---
description: Gather additional resources and references for a blog topic
argument-hint: <topic-or-research-file> [--type docs|repos|articles|all]
allowed-tools: Read, Write, Glob, Grep, WebSearch, WebFetch
---

# Gather Resources

> **DEPRECATED:** This command is deprecated and will be removed in v3.0.0.
> Use `/blog/research/draft` instead, which provides improved workflow integration.

Collect additional resources, references, and links for a blog topic.

## Arguments

- `$1` - Topic string or path to research file. Examples:
  - `"event sourcing python"` - Topic string
  - `posts/_research/event-sourcing.md` - Research file
- `--type` - Type of resources to gather:
  - `docs` - Official documentation
  - `repos` - GitHub repositories and examples
  - `articles` - Blog posts and tutorials
  - `all` (default) - All resource types

## Output

Creates or updates: `posts/_resources/<slug>.md`

## Workflow

### Step 1: Parse Input

1. Determine if input is topic string or file path
2. If file, extract topic from research notes
3. Parse `--type` filter (default: `all`)

### Step 2: Search for Resources

#### Official Documentation

Search for:

- Language/framework official docs
- API references
- RFC or specification documents
- Official tutorials

#### GitHub Repositories

Search for:

- Example implementations
- Libraries and tools
- Project templates
- Popular repos using the technology

#### Articles and Tutorials

Search for:

- Technical blog posts
- Tutorial series
- Conference talks (video links)
- Community guides

### Step 3: Evaluate Resources

For each resource, assess:

| Criteria | Check |
|----------|-------|
| Authority | Official source or recognized expert? |
| Recency | Published/updated recently? |
| Depth | Substantial content? |
| Relevance | Directly applicable? |

### Step 4: Organize Resources

Write to `posts/_resources/<slug>.md`:

```markdown
# Resources: [Topic]

**Gathered**: [date]

## Official Documentation

- [Resource Name](url)
  - **Type**: Reference / Tutorial / Guide
  - **Covers**: [What it covers]
  - **Note**: [Why it's useful]

## Repositories

- [repo-name](url) ⭐ [stars]
  - **Language**: [lang]
  - **Covers**: [What it demonstrates]
  - **Note**: [Why it's useful]

## Articles & Tutorials

- [Article Title](url) by [Author]
  - **Published**: [date]
  - **Covers**: [What it covers]
  - **Level**: Beginner / Intermediate / Advanced

## Videos & Talks

- [Talk Title](url) by [Speaker]
  - **Event**: [Conference/channel]
  - **Duration**: [length]
  - **Covers**: [Topics]

## Summary

| Type | Count |
|------|-------|
| Docs | N |
| Repos | N |
| Articles | N |
| Videos | N |
| **Total** | N |
```

### Step 5: Report

```text
## Resources Gathered

| Field | Value |
|-------|-------|
| Topic | <topic> |
| Output | posts/_resources/<slug>.md |
| Resources | N total |

**Breakdown**:
- Docs: N
- Repos: N
- Articles: N
- Videos: N
```

## Examples

```text
/gather-resources "rust async programming"
/gather-resources posts/_research/graphql-intro.md
/gather-resources "kubernetes operators" --type repos
/gather-resources "css grid layout" --type articles
```

## Quality Checklist

- [ ] Resources are authoritative
- [ ] Mix of resource types included
- [ ] Descriptions explain relevance
- [ ] Links are valid and accessible
