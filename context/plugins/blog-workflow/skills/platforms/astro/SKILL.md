---
name: platform-astro
description: Astro/AstroPaper platform configuration for the blog-workflow plugin
platform:
  name: astro
  display_name: "Astro/AstroPaper"
  paths:
    published: "src/data/blog/"
    build_output: "dist/"
  frontmatter:
    date_field: pubDatetime
    updated_field: modDatetime
    image_field: ogImage
    canonical_field: canonicalURL
  commands:
    build: "astro build"
    dev: "astro dev"
  detection:
    files:
      - astro.config.mjs
      - astro.config.ts
---

# Astro/AstroPaper Platform Skill

This skill provides Astro and AstroPaper-specific configuration for the blog-workflow plugin.

## Platform Summary

| Setting | Value |
|---------|-------|
| Published posts | `src/data/blog/` |
| Build output | `dist/` |
| Build command | `astro build` |
| Dev server | `astro dev` |
| Date field | `pubDatetime` |
| Updated field | `modDatetime` |
| Image field | `ogImage` |
| Canonical field | `canonicalURL` |

## Frontmatter Quick Reference

### Required Fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUIDv4 | Stable artifact identifier |
| `title` | string | Max 60 chars for SEO |
| `description` | string | 150-160 chars for SEO |
| `pubDatetime` | ISO 8601 | Must include timezone |
| `tags` | string[] | At least one required |

### Optional Fields

| Field | Default | Notes |
|-------|---------|-------|
| `modDatetime` | null | Set on updates |
| `author` | "aRustyDev" | Configurable per-project |
| `featured` | false | Show on homepage |
| `draft` | true | Exclude from build |
| `ogImage` | "" | Open Graph image path |
| `canonicalURL` | "" | For cross-posted content |

### Common Mistakes

| Wrong | Correct | Reason |
|-------|---------|--------|
| `date:` | `pubDatetime:` | AstroPaper naming convention |
| `image:` | `ogImage:` | AstroPaper naming convention |
| `canonical:` | `canonicalURL:` | AstroPaper naming convention |
| `type:` | (remove) | Not in AstroPaper schema |

## Detection

This platform is detected when any of these files exist in the project root:

- `astro.config.mjs`
- `astro.config.ts`

## Reference

For detailed documentation, see:

- [Frontmatter Schema](reference/frontmatter.md) - Complete field definitions and validation rules
- [Publishing Guide](reference/publishing.md) - Build, deploy, and rollback procedures
- [Directory Conventions](reference/paths.md) - Content locations and file structure
