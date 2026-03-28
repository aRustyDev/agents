# Migration Guide: v2.x → v3.0.0

## What Changed

v3.0.0 introduces **platform extensibility** — platform-specific configuration (paths, field names, build commands) is now provided by platform skills instead of being hardcoded into commands.

### For Existing Astro/AstroPaper Users

**Impact: Minimal.** All Astro-specific values are preserved in the Astro platform skill. You just need to initialize the platform config.

### Breaking Changes

| Change | Impact | Action Required |
|--------|--------|-----------------|
| Commands reference platform skill | Commands no longer hardcode `src/data/blog/` | Run `/blog/init` once |
| `.blog-workflow.yaml` required | Commands check for platform config | Created by `/blog/init` |
| Frontmatter rules are generic | Field names come from platform skill | No action (same values for Astro) |

## Migration Steps

### Step 1: Run `/blog/init`

```text
/blog/init --platform astro
```

This creates `.blog-workflow.yaml` in your project root:

```yaml
platform: astro
```

If you have `astro.config.mjs` or `astro.config.ts`, you can omit `--platform` and let auto-detection work:

```text
/blog/init
```

### Step 2: Verify Setup

Check that the platform skill loaded correctly:

1. `.blog-workflow.yaml` exists with `platform: astro`
2. Commands reference the correct paths:
   - Published posts: `src/data/blog/`
   - Build output: `dist/`
   - Build command: `astro build`

### Step 3: Continue Working

No changes to your workflow. All commands work the same — they just read configuration from the platform skill instead of having it hardcoded.

## What Didn't Change

- **Directory structure**: `content/_projects/`, `content/_drafts/`, `content/_templates/` unchanged
- **Command names**: All `/blog/*` commands unchanged
- **Templates**: All outline, persona, and review templates unchanged
- **Frontmatter values**: For Astro, all field names are identical (`pubDatetime`, `modDatetime`, `ogImage`, etc.)
- **Hooks**: `validate-blog-frontmatter.sh` and `promote-safety.sh` unchanged

## Custom Path Overrides

If your project uses non-standard paths, you can override them in `.blog-workflow.yaml`:

```yaml
platform: astro
overrides:
  paths:
    published: src/content/blog/  # Override default src/data/blog/
```

Override fields take precedence over the platform skill's defaults.

## Troubleshooting

### "No platform configured"

Run `/blog/init` to create `.blog-workflow.yaml`.

### "Unknown platform"

Check that the platform name matches an available skill in `skills/platforms/`. Currently supported: `astro`.

### Commands use wrong paths

Check `.blog-workflow.yaml` for typos. If you have overrides, verify the paths are correct. Remove the `overrides` section to use platform defaults.

### Frontmatter validation fails

The Astro platform skill uses the same field names as v2.x. If validation fails, check that your posts use `pubDatetime` (not `date`) and `modDatetime` (not `updated`).
