# AstroPaper Publishing Guide

Build, deploy, and rollback procedures specific to Astro/AstroPaper.

## Build Commands

| Command | Purpose |
|---------|---------|
| `astro build` | Production build to `dist/` |
| `astro dev` | Local dev server with hot reload |

## Build Validation

After promoting a post, verify the build succeeds:

```bash
# Run production build
astro build 2>&1

# Check post appears in output
ls dist/blog/<slug>/index.html
```

### Expected Output Structure

```
dist/
  blog/
    <slug>/
      index.html
  ...
```

### Dev Server

Start dev server for visual verification:

```bash
astro dev
# Local URL: http://localhost:4321
```

Note: Dev server requires manual stop (Ctrl+C).

## Rollback Procedures

### Quick Rollback (within session)

```bash
# Restore draft from git
git checkout content/_drafts/<slug>.md

# Remove published post (if new)
rm src/data/blog/<slug>.md

# Or restore previous version (if update)
git checkout src/data/blog/<slug>.md
```

### Manual Rollback Steps

1. **Copy published post back to drafts**:

   ```bash
   cp src/data/blog/<slug>.md content/_drafts/<slug>.md
   ```

2. **Edit draft** to restore draft state:
   - Remove `# promoted-by` marker (first line)
   - Set `draft: true`

3. **Remove published post**:

   ```bash
   rm src/data/blog/<slug>.md
   ```

4. **Rebuild to verify**:

   ```bash
   astro build
   ```

## Error Reference

| Error | Cause | Resolution |
|-------|-------|------------|
| `astro command not found` | Astro not installed | `npm install astro` |
| `Invalid frontmatter` | Schema violation | Check field names against AstroPaper schema |
| `Build failed` | Syntax or config error | Check build output for specific error |
| `Post not in dist/` | Build config issue | Verify `src/data/blog/` is in content collections |
| `Dev server port in use` | Another process on 4321 | Kill process or use `--port <N>` |

## Astro Configuration

AstroPaper uses Astro content collections. The blog collection is typically configured in:

- `src/content/config.ts` or `src/content.config.ts`
- Content directory: `src/data/blog/`

### Content Collection Schema

AstroPaper defines the blog schema in its content config. Posts must conform to this schema or the build will fail.
