# Publishing Process

The final phase of the workflow moves content from draft to published state.

## Overview

```text
content/_drafts/<slug>.md     →     src/data/blog/<slug>.md
         ↓                                  ↓
    SEO Review                          Build
         ↓                                  ↓
    Pre-Check                           Validate
         ↓                                  ↓
    Promote                              Done
```

## Publish Commands

### 1. SEO Review

```bash
/blog/publish/seo-review content/_drafts/<slug>.md
```

Checks:

- Title length and keyword presence
- Meta description quality
- Heading structure
- Image alt text
- Internal/external links
- URL slug quality

### 2. Pre-Check

```bash
/blog/publish/pre-check content/_drafts/<slug>.md
```

Validates:

- Frontmatter completeness
- Date is set correctly
- No TODO/TBD markers
- Links resolve
- Images exist
- Code blocks are formatted

### 3. Promote

```bash
/blog/publish/promote content/_drafts/<slug>.md
```

Actions:

- Copies draft to `src/data/blog/<slug>.md`
- Sets `draft: false`
- Updates timestamps
- Archives source from `content/_drafts/`

### 4. Validate

```bash
/blog/publish/validate src/data/blog/<slug>.md [--dev]
```

Verifies:

- Build succeeds
- Post appears in output
- No build errors or warnings
- (Optional) Starts dev server for visual check

## Publish Hooks

### Pre-Promote Safety

Before promoting, the workflow checks for:

- Uncommitted changes in target directory
- Existing file at destination
- Valid frontmatter

### Post-Promote Validation

After promoting:

- Runs build to verify
- Reports success/failure
- Provides rollback instructions if failed

## File Locations

| Stage | Location |
|-------|----------|
| Project drafts | `content/_projects/<name>/drafts/` |
| Ready to publish | `content/_drafts/` |
| Published | `src/data/blog/` |

### Promotion Path

```text
content/_projects/rust-ownership/drafts/final.md
    ↓ (move to drafts/)
content/_drafts/understanding-rust-ownership.md
    ↓ (promote)
src/data/blog/understanding-rust-ownership.md
```

## Frontmatter Changes

During promotion, frontmatter is updated:

### Before (Draft)

```yaml
---
title: "Understanding Rust Ownership"
draft: true
pubDatetime: 2026-03-16T10:00:00Z
---
```

### After (Published)

```yaml
---
title: "Understanding Rust Ownership"
draft: false
pubDatetime: 2026-03-16T10:00:00Z
modDatetime: 2026-03-16T10:30:00Z
---
```

## Rollback Procedure

If something goes wrong after publish:

### Quick Rollback

```bash
# Restore from git
git checkout src/data/blog/<slug>.md

# Or remove new post
rm src/data/blog/<slug>.md
```

### Full Rollback

1. Copy published post back to drafts:

   ```bash
   cp src/data/blog/<slug>.md content/_drafts/<slug>.md
   ```

2. Edit draft to restore draft state:
   - Set `draft: true`
   - Remove `modDatetime`

3. Remove published post:

   ```bash
   rm src/data/blog/<slug>.md
   ```

4. Rebuild to verify:

   ```bash
   astro build
   ```

## Post-Publish Tasks

After successful publish:

### Update Project

1. Mark post as published in project `index.md`
2. Update project status if all posts done
3. Consider archiving completed project

### Announce (Optional)

1. Share on social media
2. Update any series index pages
3. Add to newsletter if applicable

### Monitor

1. Check analytics after 24-48 hours
2. Monitor for comments/feedback
3. Fix any reported issues

## Living Document Updates

For posts with `living: true`:

### Update Process

1. Edit published post directly
2. Update `living-updated` date
3. Add entry to `living-history`
4. Rebuild and redeploy

### Example Update

```yaml
living: true
living-updated: 2026-04-15
living-history:
  - date: 2026-04-15
    summary: "Added section on new API"
  - date: 2026-03-16
    summary: "Initial publication"
```

## Best Practices

1. **Always validate build** before considering publish complete
2. **Use dev server** for visual verification on important posts
3. **Commit after promote** to preserve rollback ability
4. **Update project tracking** to maintain accurate status
5. **Consider timing** for publication (audience timezone, day of week)
