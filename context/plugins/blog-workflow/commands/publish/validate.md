---
name: blog/publish/validate
description: Verify Astro build succeeds with published post
arguments:
  - name: path
    description: Path to the published post in src/data/blog/
    required: true
  - name: dev
    description: Start dev server to visually verify
    required: false
---

# Validate Command

Verify that the Astro build succeeds with the published post and the post appears correctly in the site output.

## Tools

- `Bash` - Run astro build and optionally dev server

## Behavior

1. **Run Astro build**:

   ```bash
   astro build 2>&1
   ```

2. **Check for errors**:
   - If build fails, report error details
   - If build succeeds, continue

3. **Verify post in output**:
   - Check that post appears in `dist/` output
   - Verify post URL path is correct

4. **Dev server** (if `--dev`):
   - Start `astro dev`
   - Report local URL for visual verification
   - Note: requires manual stop

5. **Report success/failure**

## Output (Success)

```text
## Build Validation: {{filename}}

### Astro Build
- [x] Build completed successfully - pass
- [x] No errors - pass
- [x] No warnings - pass

### Post Verification
- [x] Post found in dist/blog/{{slug}}/ - pass
- [x] HTML generated correctly - pass

Build time: {{N}}s
Output size: {{N}}KB

Status: PUBLISHED SUCCESSFULLY

Post URL: /blog/{{slug}}/
```

## Output (Failure)

```text
## Build Validation: {{filename}}

### Astro Build
- [ ] Build failed - fail

Error:
  [ERROR] Invalid frontmatter in src/data/blog/{{filename}}
  pubDatetime is not a valid date

Status: BUILD FAILED

Fix the error and run `/blog/publish/validate` again.

Rollback options:
1. Quick: git checkout src/data/blog/{{filename}}
2. Full: See Rollback Procedure section
```

## Rollback Procedure

If validation fails or issues discovered after promote:

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

4. **Update project `index.md`**:
   - Change Published Posts table status to `drafting`
   - Update project status if needed

5. **Rebuild to verify**:

   ```bash
   astro build
   ```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Post not found | "Post not found at {{path}}" | Verify path is in src/data/blog/ |
| Wrong directory | "Expected path in src/data/blog/, got {{path}}" | Use correct path |
| Astro not available | "astro command not found. Install with: npm install astro" | Install Astro |
| Build failed | "Astro build failed: {{error}}" | Fix error, consider rollback |
| Post not in output | "Post not found in dist/ after build" | Check build config |
| Dev server failed | "Could not start dev server: {{error}}" | Check port availability |

## Example Usage

```text
# Validate build
/blog/publish/validate src/data/blog/building-ebpf-tracing-tools.md

# Start dev server for visual verification
/blog/publish/validate src/data/blog/building-ebpf-tracing-tools.md --dev
```
