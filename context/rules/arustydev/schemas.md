---
paths:
  - "*.schema.json"
  - "*.schema.yaml"
---

# Schema Management

## Source of Truth

`aRustyDev/schemas` → serves `schemas.arusty.dev`

## Rules

1. **Never duplicate schemas** - reference from `schemas.arusty.dev`
2. **Use `$schema` references** in JSON/YAML files:
   ```json
   { "$schema": "https://schemas.arusty.dev/<domain>/<name>/latest.schema.json" }
   ```
3. **Version schemas** using directory structure: `<domain>/<name>/<version>.schema.json`
4. **`latest`** is a symlink/redirect to the current stable version

## Creating Schemas

1. Draft schema locally in project
2. Validate against real data
3. PR to `aRustyDev/schemas` when stable
4. Update consumers to reference `schemas.arusty.dev` URL

## Known Schemas

| Schema | URL |
|--------|-----|
| Frontmatter | `schemas.arusty.dev/markdown/frontmatter/latest.schema.json` |

## Schema Development

- Use JSON Schema Draft 2020-12
- Include `title`, `description`, and `examples` in schemas
- Validate with `ajv` or equivalent before publishing
