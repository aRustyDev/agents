---
paths:
  - "*.md"
---

# Frontmatter Pattern

## When to Use

Apply frontmatter to markdown files in repos under `aRustyDev/*`, `libsdk/*`, or `civicbyte/*`.

## Schema

Reference: `https://schemas.arusty.dev/markdown/frontmatter/latest.schema.json`

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUIDv4 | Document-specific identifier |
| `project.id` | UUIDv4 | Project this document belongs to |
| `status` | enum | Document lifecycle state |

### Project ID

The `project.id` value must be consistent across the repo. It exists in two places:
1. Git note on the root commit
2. Git config as `project.id`

### Status Enum

Use consistent status values: `draft`, `active`, `deprecated`, `superseded`, `archived`

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-readable title |
| `description` | string | Brief summary |
| `version` | semver | Document version |
| `tags` | string[] | Categorization tags |
| `authors` | string[] | Author list |
| `related` | map | Related document references |

## Related Field

Maps relation types to lists of UUIDs:

```yaml
related:
  extends: [<uuid>]
  supersedes: [<uuid>]
  depends-on: [<uuid>]
  references: [<uuid>]
```

Reference documents by `id` (UUIDv4), not by file path. This allows documents to move without breaking references.

## Example

```yaml
---
id: 550e8400-e29b-41d4-a716-446655440000
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
title: Feature Design
status: active
tags: [design, core]
related:
  depends-on: [7c9e6679-7425-40de-944b-e07fc1f90ae7]
---
```
