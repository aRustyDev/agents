# Blog Frontmatter Rules

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUIDv4 | Stable artifact identifier (auto-generated) |
| `title` | string | Post title (max 60 chars for SEO) |
| `description` | string | Summary (150-160 chars for SEO) |
| `pubDatetime` | ISO 8601 | Publication datetime with timezone |
| `tags` | string[] | At least one tag required |

## Optional Fields with Defaults

| Field | Default | Description |
|-------|---------|-------------|
| `modDatetime` | null | Last modification datetime |
| `author` | "aRustyDev" | Author name (configurable per-project) |
| `featured` | false | Show on homepage |
| `draft` | true | Exclude from build until promoted |
| `ogImage` | "" | Open Graph image path |
| `canonicalURL` | "" | Canonical URL if cross-posted |
| `hideEditPost` | false | Hide edit link |
| `timezone` | "America/New_York" | Timezone for datetime display |

## Common Mistakes

| Wrong | Correct | Notes |
|-------|---------|-------|
| `date:` | `pubDatetime:` | AstroPaper uses pubDatetime |
| `image:` | `ogImage:` | AstroPaper naming convention |
| `canonical:` | `canonicalURL:` | AstroPaper naming convention |
| `type:` | (remove) | Not in AstroPaper schema |

## Field Validation

- `id` must be valid UUIDv4 (generate with `crypto.randomUUID()`)
- `pubDatetime` must be ISO 8601 with timezone (e.g., `2026-03-14T12:00:00Z`)
- `description` should not exceed 160 characters
- `title` should not exceed 60 characters for SEO optimization

## Configuration

### Author

Default: `aRustyDev` — can be overridden in project frontmatter or future config.

### Timezone

Default: `America/New_York` — hardcoded for consistency across all posts.
