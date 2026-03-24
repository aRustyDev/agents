# AstroPaper Frontmatter Schema

Complete frontmatter reference for AstroPaper blog posts.

## Required Fields

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `id` | UUIDv4 | Stable artifact identifier | Valid UUIDv4 (generate with `crypto.randomUUID()`) |
| `title` | string | Post title | Max 60 chars for SEO |
| `description` | string | Summary for SEO | 150-160 chars recommended |
| `pubDatetime` | ISO 8601 | Publication datetime | Must include timezone (e.g., `2026-03-14T12:00:00Z`) |
| `tags` | string[] | Topic tags | At least one required, lowercase hyphenated |

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `modDatetime` | ISO 8601 \| null | null | Last modification datetime |
| `author` | string | "aRustyDev" | Author name (configurable per-project) |
| `featured` | boolean | false | Show on homepage |
| `draft` | boolean | true | Exclude from build until promoted |
| `ogImage` | string | "" | Open Graph image path |
| `canonicalURL` | string | "" | Canonical URL if cross-posted |
| `hideEditPost` | boolean | false | Hide edit link |
| `timezone` | string | "America/New_York" | Timezone for datetime display |

## Field Name Mapping

AstroPaper uses non-standard field names. This table maps generic blog concepts to AstroPaper-specific names:

| Generic Concept | AstroPaper Field | Other Platforms |
|-----------------|------------------|-----------------|
| Publication date | `pubDatetime` | Hugo: `date`, Next.js: `date` |
| Last modified | `modDatetime` | Hugo: `lastmod`, Next.js: `updatedAt` |
| Social image | `ogImage` | Hugo: `image`, Next.js: `image` |
| Canonical URL | `canonicalURL` | Hugo: `canonical`, Next.js: `canonical` |

## Common Mistakes

| Wrong | Correct | Notes |
|-------|---------|-------|
| `date:` | `pubDatetime:` | AstroPaper uses pubDatetime, not date |
| `image:` | `ogImage:` | AstroPaper naming convention |
| `canonical:` | `canonicalURL:` | AstroPaper naming convention |
| `type:` | (remove) | Not in AstroPaper schema |
| `lastmod:` | `modDatetime:` | AstroPaper naming convention |

## Validation Rules

1. `id` must be valid UUIDv4
2. `pubDatetime` must be ISO 8601 with timezone
3. `description` should not exceed 160 characters
4. `title` should not exceed 60 characters for SEO optimization
5. `tags` must contain at least one entry
6. `draft` should be `true` for unpublished content

## Example

```yaml
---
id: 550e8400-e29b-41d4-a716-446655440000
title: "Building eBPF Tracing Tools"
description: "A practical guide to building custom eBPF tracing tools for Linux performance analysis."
pubDatetime: 2026-03-14T12:00:00Z
modDatetime: null
author: "aRustyDev"
featured: false
draft: true
tags:
  - linux
  - ebpf
  - performance
ogImage: ""
canonicalURL: ""
---
```
