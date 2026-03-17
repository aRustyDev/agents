# Platform Interface Contract

Every platform skill in `skills/platforms/<name>/` must implement this contract. The agent reads platform-specific values from the skill's YAML frontmatter and reference files.

## Required Frontmatter Fields

The platform skill's `SKILL.md` must include these fields in its YAML frontmatter:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `platform.name` | string | Machine identifier (e.g., `astro`) | lowercase, alphanumeric + hyphens |
| `platform.display_name` | string | Human-readable name (e.g., `Astro/AstroPaper`) | non-empty |
| `platform.paths.published` | string | Where published posts live | must end with `/` |
| `platform.paths.build_output` | string | Build output directory | must end with `/` |
| `platform.frontmatter.date_field` | string | Publication date field name | valid YAML key |
| `platform.frontmatter.updated_field` | string | Last modified field name | valid YAML key |
| `platform.frontmatter.image_field` | string | OG/social image field name | valid YAML key |
| `platform.frontmatter.canonical_field` | string | Canonical URL field name | valid YAML key |
| `platform.commands.build` | string | Build command | non-empty |
| `platform.commands.dev` | string | Dev server command | non-empty |
| `platform.detection.files` | string[] | Files indicating this platform | at least one entry |

## Example Frontmatter

```yaml
---
name: platform-astro
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
```

## Required Reference Files

Each platform skill must provide these reference documents in `reference/`:

| File | Purpose | Content |
|------|---------|---------|
| `frontmatter.md` | Complete frontmatter schema for this platform | Required/optional fields, types, validation rules, common mistakes |
| `publishing.md` | Build and deployment details | Build commands, output structure, dev server usage, rollback procedures |
| `paths.md` | Directory conventions | Content locations, project structure, file naming |

## How Commands Use Platform Config

Commands do not use template variables. Instead, they reference the platform skill's configuration in natural language:

**Pattern:** "Read the `<field>` value from the active platform skill's frontmatter"

**Example in a command:**

```markdown
## Behavior

1. **Determine published path**: Read the `platform.paths.published` value from the
   active platform skill's frontmatter (e.g., `src/data/blog/` for Astro).

2. **Run build**: Execute the `platform.commands.build` command from the active
   platform skill (e.g., `astro build` for Astro).
```

**Fallback when no platform skill is loaded:**

```markdown
## Prerequisites

- **Requires:** Active platform skill. If no platform skill is loaded, display:
  "No platform configured. Run `/blog/init` to detect your platform or
  install a platform skill manually."
```

## Adding a New Platform

1. Create `skills/platforms/<name>/SKILL.md` with all required frontmatter fields
2. Create `skills/platforms/<name>/reference/frontmatter.md`
3. Create `skills/platforms/<name>/reference/publishing.md`
4. Create `skills/platforms/<name>/reference/paths.md`
5. Add platform name to `detection.files` with unique indicator files
6. Test with `/blog/init` to verify detection works

No core plugin files need modification to add a new platform.
