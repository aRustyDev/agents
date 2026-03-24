# Platform Support

The blog-workflow plugin supports multiple blog platforms through platform skills. Each platform skill provides the configuration that commands need to work with a specific static site generator.

## Supported Platforms

| Platform | Skill | Status |
|----------|-------|--------|
| Astro/AstroPaper | `skills/platforms/astro/` | Supported |
| Hugo | - | Planned |
| Next.js MDX | - | Planned |

## How Platform Skills Work

1. **During `/blog/init`**, you specify or auto-detect your platform
2. The platform choice is saved to `.blog-workflow.yaml` in your project root
3. Commands read platform-specific values (paths, field names, build commands) from the active platform skill's frontmatter
4. Reference files provide detailed documentation (loaded on demand)

## Platform Configuration

### .blog-workflow.yaml

Created by `/blog/init` in your project root:

```yaml
platform: astro
overrides:
  paths:
    published: src/content/blog/  # Override default if needed
```

### Override Behavior

| Field | Default Source | Override |
|-------|---------------|---------|
| `paths.published` | Platform skill frontmatter | `.blog-workflow.yaml` overrides |
| `paths.build_output` | Platform skill frontmatter | `.blog-workflow.yaml` overrides |
| `commands.build` | Platform skill frontmatter | `.blog-workflow.yaml` overrides |
| `commands.dev` | Platform skill frontmatter | `.blog-workflow.yaml` overrides |

## Adding a New Platform

To add support for a new platform:

1. Create the skill directory: `skills/platforms/<name>/`
2. Create `SKILL.md` implementing the [platform interface contract](../../../skills/platforms/_interface.md)
3. Create reference files in `reference/`:
   - `frontmatter.md` — Complete frontmatter schema
   - `publishing.md` — Build and deploy procedures
   - `paths.md` — Directory conventions
4. Test with `/blog/init --platform <name>`

No changes to core plugin commands are needed. The interface contract ensures all platforms provide the same configuration fields.

## Platform Detection

When running `/blog/init` without `--platform`, the command checks for platform indicator files:

| File | Platform |
|------|----------|
| `astro.config.mjs`, `astro.config.ts` | Astro |
| `hugo.toml`, `config.toml` (with Hugo config) | Hugo (future) |
| `next.config.js` + `@next/mdx` | Next.js MDX (future) |

If no platform is detected or multiple are found, the user is prompted to choose.
