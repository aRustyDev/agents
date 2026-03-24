---
name: blog:publish:validate
description: Verify platform build succeeds with published post
argument-hint: <path> [--dev]
arguments:
  - name: path
    description: Path to the published post in the platform's published directory
    required: true
  - name: dev
    description: Start dev server to visually verify
    required: false
---

# Validate Command

Verify that the platform build succeeds with the published post and the post appears correctly in the site output.

## Prerequisites

- **Requires:** Active platform skill. If no platform skill is loaded, display:
  "No platform configured. Run `/blog/init` to detect your platform or install a platform skill manually."

## Tools

- `Bash` - Run build command and optionally dev server (read commands from active platform skill)

## Behavior

1. **Run build**: Execute the `platform.commands.build` command from the active platform skill (e.g., `astro build` for Astro):

   ```bash
   <platform.commands.build> 2>&1
   ```

2. **Check for errors**:
   - If build fails, report error details
   - If build succeeds, continue

3. **Verify post in output**:
   - Check that post appears in the `platform.paths.build_output` directory (e.g., `dist/` for Astro)
   - Verify post URL path is correct

4. **Dev server** (if `--dev`):
   - Start the `platform.commands.dev` command from the active platform skill (e.g., `astro dev`)
   - Report local URL for visual verification
   - Note: requires manual stop

5. **Report success/failure**

## Output (Success)

```text
## Build Validation: {{filename}}

### Platform Build
- [x] Build completed successfully - pass
- [x] No errors - pass
- [x] No warnings - pass

### Post Verification
- [x] Post found in <build_output>/blog/{{slug}}/ - pass
- [x] HTML generated correctly - pass

Build time: {{N}}s
Output size: {{N}}KB

Status: PUBLISHED SUCCESSFULLY

Post URL: /blog/{{slug}}/
```

## Output (Failure)

```text
## Build Validation: {{filename}}

### Platform Build
- [ ] Build failed - fail

Error:
  [ERROR] Invalid frontmatter in <published_path>/{{filename}}
  Date field is not a valid date

Status: BUILD FAILED

Fix the error and run `/blog/publish/validate` again.

Rollback options:
1. Quick: git checkout <published_path>/{{filename}}
2. Full: See Rollback Procedure section
```

## Rollback Procedure

If validation fails or issues discovered after promote:

### Quick Rollback (within session)

```bash
# Restore draft from git
git checkout content/_drafts/<slug>.md

# Remove published post (if new)
rm <published_path>/<slug>.md

# Or restore previous version (if update)
git checkout <published_path>/<slug>.md
```

### Manual Rollback Steps

1. **Copy published post back to drafts**:

   ```bash
   cp <published_path>/<slug>.md content/_drafts/<slug>.md
   ```

2. **Edit draft** to restore draft state:
   - Remove `# promoted-by` marker (first line)
   - Set `draft: true`

3. **Remove published post**:

   ```bash
   rm <published_path>/<slug>.md
   ```

4. **Update project `index.md`**:
   - Change Published Posts table status to `drafting`
   - Update project status if needed

5. **Rebuild to verify**: Run the `platform.commands.build` command from the active platform skill

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Post not found | "Post not found at {{path}}" | Verify path is in the platform's published directory |
| Wrong directory | "Expected path in platform published directory, got {{path}}" | Use correct path |
| Build tool not available | "Build command not found. Check platform skill for install instructions" | Install platform build tool |
| Build failed | "Build failed: {{error}}" | Fix error, consider rollback |
| Post not in output | "Post not found in build output after build" | Check build config |
| Dev server failed | "Could not start dev server: {{error}}" | Check port availability |

## Example Usage

```text
# Validate build (path depends on platform)
/blog/publish/validate <published_path>/building-ebpf-tracing-tools.md

# Start dev server for visual verification
/blog/publish/validate <published_path>/building-ebpf-tracing-tools.md --dev
```
