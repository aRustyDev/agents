# Post Relationships

Posts connect to each other through explicit relationships. This system enables navigation, context, and understanding of how content relates.

## Relationships vs Tags

| Aspect | Relationships | Tags |
|--------|---------------|------|
| Purpose | Structural/semantic connections | Thematic/topical classification |
| Definition | Explicit in frontmatter | Also explicit, but for discovery |
| Examples | Part of series, responds-to | `rust`, `security`, `tooling` |
| Navigation | Direct links between posts | Filter/search by topic |

Both are used together—relationships for structure, tags for discoverability.

---

## Relationship Types

### series

Indicates the post is part of an ordered sequence.

```yaml
relationships:
  - type: series
    name: rust-from-zero
    part: 2
    total: 5  # Optional
```

**Fields:**

- `name`: Series identifier (matches series index)
- `part`: Position in sequence (1-indexed)
- `total`: Total planned parts (optional, for "Part 2 of 5")

**Use when**: Writing multi-part content that should be read in order.

---

### project-arc

Links posts that follow a natural project lifecycle: Planning → Updates → Retrospective.

```yaml
relationships:
  - type: project-arc
    project: rust-compiler-2026
    phase: updates
```

**Fields:**

- `project`: Project identifier
- `phase`: One of `planning`, `updates`, `retrospective`

**Use when**: Posts document different phases of the same project.

**Difference from series**: Project-arc has semantic phase meaning; series is just ordered parts.

---

### responds-to

Indicates this post builds on, argues with, or responds to another post.

```yaml
relationships:
  - type: responds-to
    path: /blog/why-rust-is-overrated
    note: "A counterpoint discussing the benefits"  # Optional
```

**Fields:**

- `path`: URL path of the referenced post
- `note`: Brief description of the relationship (optional)

**Use when**: Your post is a direct response to specific content.

---

### supersedes

Indicates this post replaces an older post.

```yaml
relationships:
  - type: supersedes
    path: /blog/my-2025-rust-toolkit
    reason: "Annual update with new tools"  # Optional
```

**Fields:**

- `path`: URL path of the superseded post
- `reason`: Why the old post was replaced (optional)

**Use when**: Publishing an updated version that makes the old version obsolete.

**Note**: The superseded post should link back with `superseded-by`.

---

### superseded-by

Indicates this post has been replaced by a newer post.

```yaml
relationships:
  - type: superseded-by
    path: /blog/my-2026-rust-toolkit
```

**Fields:**

- `path`: URL path of the newer post

**Use when**: An old post has been replaced. Readers should see this prominently.

---

### see-also

Curated links to related posts (not auto-generated from tags).

```yaml
relationships:
  - type: see-also
    path: /blog/memory-safety-primer
  - type: see-also
    path: /blog/ownership-deep-dive
    note: "Deeper coverage of ownership concepts"
```

**Fields:**

- `path`: URL path of related post
- `note`: Why this is relevant (optional)

**Use when**: You want to explicitly recommend related reading beyond tag-based suggestions.

---

## Full Example

```yaml
---
title: "Rust Ownership: Part 2 - Borrowing"
type: tutorial
tags:
  - rust
  - ownership
  - memory-safety

relationships:
  - type: series
    name: rust-ownership-guide
    part: 2
    total: 4

  - type: responds-to
    path: /blog/ownership-is-confusing
    note: "Addressing common confusion points"

  - type: see-also
    path: /blog/rust-lifetimes-explained

  - type: see-also
    path: /blog/memory-safety-primer
    note: "Background on why this matters"
---
```

---

## Relationship Schema

All relationships follow a flat list structure for easy parsing:

```yaml
relationships:
  - type: <relationship-type>
    <type-specific-fields>
```

### Type-Specific Fields

| Type | Required Fields | Optional Fields |
|------|-----------------|-----------------|
| `series` | `name`, `part` | `total` |
| `project-arc` | `project`, `phase` | - |
| `responds-to` | `path` | `note` |
| `supersedes` | `path` | `reason` |
| `superseded-by` | `path` | - |
| `see-also` | `path` | `note` |

---

## Relationship Patterns

### The Project Lifecycle

A common pattern for project-based content:

```text
Planning Post
    ↓ (project-arc: planning)
Update Post 1
    ↓ (project-arc: updates)
Update Post 2
    ↓ (project-arc: updates)
Update Post 3
    ↓ (project-arc: updates)
Retrospective Post
    (project-arc: retrospective)
```

### The Annual Update

For living content that gets replaced yearly:

```text
My 2024 Toolkit
    ↓ (superseded-by)
My 2025 Toolkit
    ↓ (superseded-by)
My 2026 Toolkit (current)
```

### The Response Chain

For posts that build on each other:

```text
Original Post: "Hot Take on X"
    ↑ (responds-to)
Response Post: "Why X is Actually Good"
    ↑ (responds-to)
Synthesis Post: "Reconciling Views on X"
```

---

## Implementation Notes

### Bidirectional Links

Some relationships have natural inverses:

- `supersedes` ↔ `superseded-by`
- `series` posts link to each other via series index

The blog build system can auto-generate reverse links where appropriate.

### Validation

At build time, validate:

- All `path` references point to existing posts
- Series parts are sequential without gaps
- `superseded-by` posts actually exist
- No circular `responds-to` chains (warn only)

### Display

Relationships should be prominently displayed:

- Series: Navigation bar (← Part 1 | Part 3 →)
- Superseded: Warning banner ("This post has been updated...")
- See-also: Footer section
- Responds-to: Inline reference in introduction
