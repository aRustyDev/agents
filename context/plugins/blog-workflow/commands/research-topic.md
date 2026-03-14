---
description: Research a blog topic and produce structured research notes for writing
argument-hint: <topic> [--type tutorial|deep-dive|research-summary|dev-journal] [--audience beginner|intermediate|advanced]
allowed-tools: Read, Write, Glob, Grep, WebSearch, WebFetch, Task
---

# Research Blog Topic

> **DEPRECATED:** This command is deprecated and will be removed in v3.0.0.
> Use `/blog/research/draft` instead, which provides improved workflow integration.

Gather sources, synthesize background material, and produce structured research notes for a technical blog post.

## Arguments

- `$1` - Topic to research. Example: "event sourcing in Python"
- `--type` - Post type (affects depth and focus):
  - `tutorial` - Focus on step-by-step implementation details
  - `deep-dive` (default) - Comprehensive conceptual coverage
  - `research-summary` - Multiple sources and synthesis
  - `dev-journal` - Personal experience focus
- `--audience` - Target audience expertise:
  - `beginner` - Assume minimal prior knowledge
  - `intermediate` (default) - Familiar with basics
  - `advanced` - Expert-level depth

## Output

Creates: `posts/_research/<slugified-topic>.md`

## Workflow

### Step 1: Parse and Validate

1. Extract topic from `$1`
2. Parse `--type` (default: `deep-dive`) and `--audience` (default: `intermediate`)
3. Generate slug from topic: lowercase, hyphens, max 50 chars
4. Create output directory: `mkdir -p posts/_research/`

### Step 2: Scope Research

Based on post type, determine research scope:

| Type | Primary Sources | Depth |
|------|-----------------|-------|
| tutorial | Official docs, GitHub repos, working examples | Implementation-focused |
| deep-dive | Specs, papers, architecture docs, comparisons | Conceptual depth |
| research-summary | Articles, reports, studies, expert opinions | Breadth across sources |
| dev-journal | Personal notes, issue trackers, commit history | Experience-focused |

### Step 3: Research

Spawn the `research-synthesizer` agent with:

- Topic and scope
- Audience level
- Post type

The agent will:

1. Search for official documentation
2. Find code examples and implementations
3. Locate authoritative articles and tutorials
4. Identify common patterns and anti-patterns
5. Note pitfalls and gotchas

### Step 4: Write Research Notes

Generate research notes following this structure:

```markdown
# Research Notes: <Topic>

**Post Type**: <type>
**Target Audience**: <audience>
**Researched**: <date>

## Overview

[1-2 sentence summary]

## Key Concepts

- **[Concept 1]**: [Brief explanation]
- **[Concept 2]**: [Brief explanation]

## Background

[Context, history, why this matters]

## Technical Details

[Core information for the post]

## Code Examples Found

[Notable snippets from research]

## Common Patterns

[Best practices discovered]

## Pitfalls & Gotchas

[Things to warn readers about]

## Open Questions

[Areas needing more research]

## Sources

- [Source 1](url) - [what it covers]
- [Source 2](url) - [what it covers]
```

### Step 5: Report

```text
## Research Complete

| Field | Value |
|-------|-------|
| Topic | <topic> |
| Type | <post-type> |
| Output | posts/_research/<slug>.md |
| Sources | N sources gathered |

**Next step**: `/outline-post posts/_research/<slug>.md`
```

## Examples

```text
/research-topic "WebAssembly in Python"
/research-topic "building a CLI with Rust" --type tutorial
/research-topic "state of JavaScript testing" --type research-summary --audience advanced
/research-topic "debugging memory leaks" --type dev-journal
```

## Quality Checklist

- [ ] Topic is well-scoped (not too broad)
- [ ] Multiple authoritative sources consulted
- [ ] Key concepts identified and explained
- [ ] Code examples collected where relevant
- [ ] Gaps and open questions noted
- [ ] Sources properly attributed
