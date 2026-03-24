# Blog Post Taxonomy

This taxonomy defines the structure, classification, and relationships for blog content. It provides a consistent framework for creating, organizing, and relating posts.

## Core Concepts

The taxonomy is built on four foundational concepts:

| Concept | Purpose |
|---------|---------|
| [Post Types](./post/types.md) | What kind of content is this? |
| [Dimensions](./dimensions.md) | How formal, complex, and timely? |
| [Relationships](./relationships.md) | How does this connect to other posts? |
| [Series](./series.md) | How do posts form ordered sequences? |

## Quick Reference

### Post Type Selection

```text
"I want to..."
├── Teach something → Tutorial, ELI5, 5 Levels
├── Show my process → Walk-through, Study Review
├── Evaluate something → Review, Comparison
├── Share my opinion → Opinions, Dev Blog
├── Document research → Research, Deep Dive
├── Track a project → Planning, Updates, Retrospective
├── Pose a question → Open Questions, Problems
├── Announce something → Announcement
└── Curate resources → Reference
```

### Formality Quick Guide

| Level | Name | When to Use |
|-------|------|-------------|
| 1 | Casual | Quick takes, informal thoughts |
| 2 | Structured | Most blog posts, conference talk level |
| 3 | Formal | Technical whitepapers, detailed analysis |
| 4 | Academic | Research with methodology, citations |

### Relationship Types

- **series** - Part of an ordered sequence
- **project-arc** - Planning→Updates→Retrospective chain
- **responds-to** - Builds on or argues with another post
- **supersedes** - Replaces an older post
- **see-also** - Curated related reading

## Document Map

```text
taxonomy/
├── index.md              # This file
├── post/
│   ├── types.md          # Overview of all types
│   ├── tutorial.md       # Tutorial type details
│   ├── walk-through.md   # Walk-through type details
│   └── ...               # Other post types
├── dimensions.md         # Formality, complexity, temporality
├── relationships.md      # Post relationship system
├── series.md             # Series as first-class entity
└── schema.md             # Frontmatter schema reference
```

## See Also

- [Concepts Overview](../concepts.md) - High-level blog-workflow concepts
- [Workflow Guide](../workflow/concept.md) - How to use the workflow
- [Reference](../reference/frontmatter.md) - Complete frontmatter reference
