# Series

A series is a first-class entity representing an ordered collection of related posts. Series exist independently of the projects that produce them.

## Series vs Project

| Aspect | Series | Project |
|--------|--------|---------|
| Purpose | Published grouping for readers | Internal workflow for authors |
| Visibility | Public, navigable | Internal to blog-workflow |
| Scope | Multiple posts in order | Development of posts |
| Lifespan | Persists after completion | Ends when posts published |
| Location | `content/_series/` | `content/_projects/` |

A project can produce:

- A single post
- Multiple unrelated posts
- One series
- Parts of multiple series (spanning projects)

## Series Structure

### Directory Layout

```text
content/_series/
└── rust-from-zero/
    └── index.md
```

### Series Index

Each series has an `index.md` with metadata:

```yaml
---
name: rust-from-zero
title: "Rust from Zero"
description: "My journey learning Rust from complete beginner to confident user"
status: in-progress
started: 2026-01-15
# Posts are discovered from post frontmatter, not listed here
---

Series introduction content here. This can include:

- What the series covers
- Who it's for
- Prerequisites
- How to follow along
```

### Series Metadata Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (matches posts' series name) |
| `title` | Yes | Display title |
| `description` | Yes | Brief description |
| `status` | Yes | `in-progress`, `complete`, `abandoned` |
| `started` | Yes | ISO date when series began |
| `completed` | No | ISO date when series finished |
| `total` | No | Planned total parts (if known) |

### Status Values

| Status | Meaning |
|--------|---------|
| `in-progress` | Actively being written |
| `complete` | All planned parts published |
| `abandoned` | Discontinued (explain why in content) |

---

## Post Membership

Posts declare series membership in their frontmatter:

```yaml
relationships:
  - type: series
    name: rust-from-zero
    part: 2
    total: 5  # Optional
```

The blog build system:

1. Finds all posts with matching `series.name`
2. Orders by `series.part`
3. Generates navigation and index pages

### Ordering

- Parts are 1-indexed
- Gaps are allowed (Part 1, Part 3 - maybe Part 2 was cut)
- Build warns on gaps but doesn't fail

---

## Creating a Series

### 1. Create Series Index

```bash
/blog/series/create "Rust from Zero"
```

This creates `content/_series/rust-from-zero/index.md`.

### 2. Add Posts to Series

When creating posts, specify series membership:

```bash
/blog/post/draft --series rust-from-zero --part 1
```

Or add to existing post:

```bash
/blog/series/add-post rust-from-zero content/_drafts/rust-intro.md --part 1
```

### 3. Manage Series

```bash
# List all series
/blog/series/list

# Reorder parts
/blog/series/reorder rust-from-zero

# Mark complete
/blog/series/complete rust-from-zero
```

---

## Series Commands

| Command | Purpose |
|---------|---------|
| `/blog/series/create <name>` | Create new series with index.md |
| `/blog/series/list` | List all series with status |
| `/blog/series/show <name>` | Show series details and posts |
| `/blog/series/add-post <name> <post> --part N` | Add post to series |
| `/blog/series/reorder <name>` | Interactive reordering |
| `/blog/series/complete <name>` | Mark series as complete |
| `/blog/series/abandon <name>` | Mark series as abandoned |

---

## Future: Series Landing Pages

> **Note**: Series landing pages are planned but not yet implemented.

Eventually, each series will have a public landing page at `/blog/series/<name>/` showing:

- Series title and description
- Progress indicator (3 of 5 parts)
- Ordered list of posts with status
- Introduction content from index.md

For now, series navigation is embedded in individual posts.

---

## Examples

### Technical Learning Series

```yaml
---
name: rust-from-zero
title: "Rust from Zero"
description: "Learning Rust from scratch as an experienced developer"
status: in-progress
started: 2026-01-15
total: 10
---

This series documents my journey learning Rust...
```

Posts:

1. "Why I'm Learning Rust"
2. "Setting Up the Environment"
3. "Ownership and Borrowing"
4. "Error Handling"
5. (in progress...)

### Project Documentation Series

```yaml
---
name: building-a-compiler
title: "Building a Compiler"
description: "Step-by-step construction of a simple compiler"
status: complete
started: 2025-06-01
completed: 2025-12-15
---
```

### Abandoned Series

```yaml
---
name: kubernetes-deep-dive
title: "Kubernetes Deep Dive"
description: "Exploring K8s internals"
status: abandoned
started: 2025-03-01
---

I started this series but shifted focus to other topics.
Parts 1-3 are still useful standalone resources.
```

---

## Best Practices

1. **Plan before starting**: Know roughly how many parts and scope
2. **Consistent naming**: Use slugified name that reads well
3. **Part independence**: Each part should be valuable alone when possible
4. **Clear progression**: Readers should know where they are (Part 2 of 5)
5. **Honest status**: Mark abandoned rather than leaving in limbo
6. **Cross-link carefully**: Don't over-connect unrelated series
