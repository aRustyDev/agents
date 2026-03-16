# Frontmatter Schema

This document defines the complete frontmatter schema for blog posts.

## Required Fields

All posts must include:

```yaml
---
title: "Post Title"
description: "Brief description for SEO and previews"
type: tutorial  # One of the 19 post types
pubDatetime: 2026-03-16T10:00:00Z
author: "Author Name"
tags:
  - tag1
  - tag2
---
```

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Post title |
| `description` | string | SEO description (150-160 chars recommended) |
| `type` | enum | Post type (see [Post Types](./post/types.md)) |
| `pubDatetime` | ISO datetime | Publication timestamp |
| `author` | string | Author name |
| `tags` | string[] | Topic tags for discoverability |

---

## Optional Fields

### Content Metadata

```yaml
draft: false  # Default: false
featured: false  # Default: false
ogImage: "/images/og/my-post.png"  # Open Graph image
canonicalUrl: "https://example.com/original"  # If republished
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `draft` | boolean | false | If true, not published |
| `featured` | boolean | false | Highlight on homepage |
| `ogImage` | string | - | Path to Open Graph image |
| `canonicalUrl` | string | - | Original source if republished |

### Dimensions

```yaml
formality: 2  # 1-4 or named: casual, structured, formal, academic
complexity: 3  # 1-5 or named: accessible, introductory, intermediate, advanced, expert
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `formality` | number\|string | 2 | Formality level (1-4) |
| `complexity` | number\|string | 2 | Complexity level (1-5) |

### Living Document

```yaml
living: true
living-updated: 2026-03-16
living-history:
  - date: 2026-03-16
    summary: "Added new section"
  - date: 2026-02-01
    summary: "Initial publication"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `living` | boolean | false | Is this a living document? |
| `living-updated` | ISO date | - | Last content update |
| `living-history` | array | - | Update history |

### Relationships

```yaml
relationships:
  - type: series
    name: rust-from-zero
    part: 2
    total: 5
  - type: responds-to
    path: /blog/original-post
    note: "A counterpoint"
  - type: supersedes
    path: /blog/old-post
    reason: "Annual update"
  - type: see-also
    path: /blog/related-post
```

See [Relationships](./relationships.md) for full documentation.

---

## Type-Specific Fields

### Tutorial

```yaml
type: tutorial
prerequisites:
  - "Basic Rust syntax"
  - "Understanding of memory management"
objectives:
  - "Understand ownership rules"
  - "Apply borrowing patterns"
estimated-time: "30 minutes"
```

### Research

```yaml
type: research
abstract: "Brief summary of findings..."
methodology: "Approach taken..."
keywords:
  - "performance"
  - "benchmarking"
```

### Review

```yaml
type: review
review-subtype: tool  # course, library, book, tool, policy, custom
rating: 4  # 1-5, optional
rating-breakdown:
  documentation: 4
  ease-of-use: 5
  performance: 3
last-evaluated: 2026-03-01
```

### Comparison

```yaml
type: comparison
compared-items:
  - name: "Neovim"
    url: "https://neovim.io"
  - name: "Helix"
    url: "https://helix-editor.com"
comparison-criteria:
  - "Performance"
  - "Plugin ecosystem"
  - "Learning curve"
```

### 5 Levels

```yaml
type: 5-levels
topic: "Machine Learning"
levels:
  - name: "Child"
    description: "5-year-old explanation"
  - name: "Teenager"
    description: "High school level"
  - name: "Undergraduate"
    description: "CS major level"
  - name: "Graduate"
    description: "ML specialization"
  - name: "Expert"
    description: "Researcher level"
```

---

## Full Example

```yaml
---
title: "Understanding Rust Ownership"
description: "A comprehensive guide to Rust's ownership system for developers coming from garbage-collected languages."
type: tutorial
pubDatetime: 2026-03-16T10:00:00Z
author: "Adam Smith"

tags:
  - rust
  - memory-management
  - ownership

draft: false
featured: true
ogImage: "/images/og/rust-ownership.png"

formality: 2
complexity: 3

living: true
living-updated: 2026-03-16
living-history:
  - date: 2026-03-16
    summary: "Added section on common patterns"
  - date: 2026-03-01
    summary: "Initial publication"

relationships:
  - type: series
    name: rust-ownership-guide
    part: 1
    total: 4
  - type: see-also
    path: /blog/rust-lifetimes-explained
    note: "Deep dive on lifetimes"

# Type-specific fields
prerequisites:
  - "Basic programming experience"
  - "Familiarity with pointers (helpful but not required)"
objectives:
  - "Understand the three ownership rules"
  - "Apply borrowing correctly"
  - "Recognize common ownership patterns"
estimated-time: "45 minutes"
---
```

---

## Validation Rules

### Required Validation

- `title`: Non-empty string, max 100 chars
- `description`: Non-empty string, 50-200 chars recommended
- `type`: Must be valid post type
- `pubDatetime`: Valid ISO 8601 datetime
- `author`: Non-empty string
- `tags`: At least one tag

### Conditional Validation

- If `living: true`, `living-updated` should be present
- If `type: review`, `review-subtype` is recommended
- If `type: series` relationship, `part` is required

### Warnings (non-blocking)

- `description` outside 150-160 char range
- No `ogImage` specified
- `formality` or `complexity` not set (defaults used)

---

## Schema Evolution

When adding new fields:

1. Add to this schema document
2. Update validation in build system
3. Add to relevant templates
4. Document in CHANGELOG

Fields should be backwards compatible—existing posts without new fields should still build.
