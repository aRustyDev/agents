# Blog Frontmatter Rules

## Required Fields

These fields are required regardless of platform. The exact field names may vary by platform — consult the active platform skill for platform-specific naming.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUIDv4 | Stable artifact identifier (auto-generated) |
| `title` | string | Post title (max 60 chars for SEO) |
| `description` | string | Summary (150-160 chars for SEO) |
| Publication date | ISO 8601 | Publication datetime with timezone |
| `tags` | string[] | At least one tag required |

> **Platform Mapping:** The publication date field name varies by platform. Read `platform.frontmatter.date_field` from the active platform skill to determine the correct name (e.g., `pubDatetime` for Astro, `date` for Hugo).

## Optional Fields with Defaults

| Field | Default | Description |
|-------|---------|-------------|
| Last modified date | null | Last modification datetime |
| `author` | "aRustyDev" | Author name (configurable per-project) |
| `featured` | false | Show on homepage |
| `draft` | true | Exclude from build until promoted |
| Social image | "" | Open Graph / social image path |
| Canonical URL | "" | Canonical URL if cross-posted |

> **Platform Mapping:** The fields "Last modified date", "Social image", and "Canonical URL" have platform-specific names. Read `platform.frontmatter.updated_field`, `platform.frontmatter.image_field`, and `platform.frontmatter.canonical_field` from the active platform skill.

## Platform-Specific Field Names

For the exact field names used by each platform, see the platform skill's `reference/frontmatter.md`:

- **Astro/AstroPaper:** `skills/platforms/astro/reference/frontmatter.md`

## Field Validation

- `id` must be valid UUIDv4 (generate with `crypto.randomUUID()`)
- Publication date must be ISO 8601 with timezone (e.g., `2026-03-14T12:00:00Z`)
- `description` should not exceed 160 characters
- `title` should not exceed 60 characters for SEO optimization

## Configuration

### Author

Default: `aRustyDev` — can be overridden in project frontmatter or future config.

### Timezone

Default: `America/New_York` — hardcoded for consistency across all posts.
