# Frontmatter Reference

Complete reference for all frontmatter fields used in blog posts.

> **Note**: For schema details and validation rules, see [Frontmatter Schema](../taxonomy/schema.md).

## Quick Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Post title |
| `description` | string | SEO description |
| `type` | enum | Post type |
| `pubDatetime` | datetime | Publication timestamp |
| `author` | string | Author name |
| `tags` | string[] | Topic tags |

### Common Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `draft` | boolean | false | Unpublished draft |
| `featured` | boolean | false | Featured post |
| `formality` | 1-4 | 2 | Formality level |
| `complexity` | 1-5 | 2 | Complexity level |
| `living` | boolean | false | Living document |
| `relationships` | array | [] | Post relationships |

## Field Details

### title

```yaml
title: "Understanding Rust Ownership"
```

- Required
- Max 100 characters recommended
- Used in page title and social sharing

### description

```yaml
description: "A comprehensive guide to Rust's ownership system for developers coming from garbage-collected languages."
```

- Required
- 150-160 characters recommended for SEO
- Used in meta description and social sharing

### type

```yaml
type: tutorial
```

- Required
- One of: `tutorial`, `walk-through`, `deep-dive`, `research`, `study-review`, `review`, `comparison`, `problems`, `open-questions`, `planning`, `retrospective`, `updates`, `opinions`, `dev-blog`, `announcement`, `reference`, `eli5`, `5-levels`

See [Post Types](../taxonomy/post/types.md) for details.

### pubDatetime

```yaml
pubDatetime: 2026-03-16T10:00:00Z
```

- Required
- ISO 8601 format
- Include timezone (Z for UTC recommended)

### author

```yaml
author: "Adam Smith"
```

- Required
- Display name of author

### tags

```yaml
tags:
  - rust
  - memory-management
  - ownership
```

- Required (at least one)
- Lowercase, hyphenated
- Used for categorization and discovery

### draft

```yaml
draft: true
```

- Optional, default: false
- If true, post is not published
- Useful for work-in-progress

### featured

```yaml
featured: true
```

- Optional, default: false
- Highlights post on homepage or feeds

### formality

```yaml
formality: 2
# or
formality: structured
```

- Optional, default: 2
- Levels: 1 (casual), 2 (structured), 3 (formal), 4 (academic)

### complexity

```yaml
complexity: 3
# or
complexity: intermediate
```

- Optional, default: 2
- Levels: 1-5 (accessible to expert)

### living

```yaml
living: true
living-updated: 2026-03-16
```

- Optional, default: false
- If true, document is maintained over time
- Include `living-updated` with last content update date

### relationships

```yaml
relationships:
  - type: series
    name: rust-from-zero
    part: 2
  - type: see-also
    path: /blog/related-post
```

- Optional
- Flat list with `type` field
- See [Relationships](../taxonomy/relationships.md) for all types

## Platform-Specific Fields

Some frontmatter field names vary by platform (e.g., `pubDatetime` vs `date`). The fields documented above use the plugin's generic names. For the exact field names used by your platform, see:

- **Astro/AstroPaper:** `skills/platforms/astro/reference/frontmatter.md`

The active platform skill's frontmatter mapping is loaded when you run `/blog/init`. Commands automatically use the correct field names from the loaded platform skill.

## Type-Specific Fields

See [Frontmatter Schema](../taxonomy/schema.md#type-specific-fields) for fields specific to each post type.
