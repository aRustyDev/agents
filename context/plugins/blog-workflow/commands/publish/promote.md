---
name: blog/publish/promote
description: Move validated draft to the platform's published content directory
argument-hint: <path> [--schedule date]
arguments:
  - name: path
    description: Path to the draft file
    required: true
  - name: schedule
    description: Future publish date (ISO 8601), keeps draft:true until then
    required: false
  - name: force
    description: Promote even without pre-check (not recommended)
    required: false
---

# Promote Command

Move a validated draft to the platform's published content directory for publication. This is the only intended path to publish content.

## Prerequisites

- **Requires:** Active platform skill. If no platform skill is loaded, display:
  "No platform configured. Run `/blog/init` to detect your platform or install a platform skill manually."

## Tools

- `Read` - Load draft and platform skill frontmatter
- `Write` - Write to published content directory (read `platform.paths.published` from active platform skill)
- `Bash` - Delete from `_drafts/`

## Behavior

1. **Load draft** from `content/_drafts/<slug>.md`

2. **Verify pre-check passed** (unless `--force`):
   - Check `_precheck.status` equals `passed`
   - Check `_precheck.timestamp` is within 24 hours
   - If not: "Draft must pass pre-check before promotion. Run `/blog/publish/pre-check` first."

3. **Handle scheduling** (if `--schedule`):
   - Set `pubDatetime` to scheduled time
   - Keep `draft: true`
   - Write to `src/data/blog/` (will publish at scheduled time)
   - Skip deletion from `_drafts/`
   - Report scheduled status

4. **Update frontmatter** (normal promote):
   - Add `# promoted-by: /blog/publish/promote` as first line (bypasses safety hook)
   - Set `draft: false`
   - Set `pubDatetime: <current ISO 8601>` (if not already set to future)
   - Set `modDatetime: null` (first publish)
   - Remove `_precheck` field (no longer needed)

5. **Write to** the platform's published directory (read `platform.paths.published` from the active platform skill, e.g., `src/data/blog/` for Astro): `<published_path>/<slug>.md`

6. **Delete from** `content/_drafts/<slug>.md`

7. **Update project** (if draft is part of a project):
   - Update phase status -> `complete`
   - Check if all phases are complete
   - If all complete, update project status -> `complete` in `index.md`
   - Otherwise, update project status -> `publish`
   - Update Published Posts table in `index.md`

8. **Report success** with published path

> **Important**: The `# promoted-by: /blog/publish/promote` marker is required. The `promote-safety.sh` hook checks for this marker and skips its warning when present.

## Output

```text
Promoted: content/_drafts/{{slug}}.md
      ->  src/data/blog/{{slug}}.md

Frontmatter updated:
- draft: false
- pubDatetime: {{timestamp}}
- Added promote marker

Draft deleted from: content/_drafts/

Project status: {{status}} ({{completed}}/{{total}} phases complete)
Published Posts table updated in index.md

Next: Run `/blog/publish/validate src/data/blog/{{slug}}.md`
```

## Output (Scheduled)

```text
Scheduled: content/_drafts/{{slug}}.md
       ->  src/data/blog/{{slug}}.md

Frontmatter updated:
- draft: true (will auto-publish)
- pubDatetime: {{scheduled_time}} (scheduled)

Draft kept in: content/_drafts/ (for reference)

Note: Post will go live when pubDatetime passes and site rebuilds.

Next: Run `/blog/publish/validate` after scheduled time to verify
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Draft not found | "Draft not found at {{path}}" | Verify path |
| Pre-check not passed | "Pre-check required. Run `/blog/publish/pre-check` first" | Run pre-check |
| Pre-check stale | "Pre-check is {{N}} hours old (>24h). Re-run to verify" | Run pre-check again |
| Pre-check failed | "Pre-check status is 'failed'. Fix issues first" | Fix and re-run pre-check |
| Already promoted | "Post already exists at <published_path>/{{slug}}.md. Edit in place or use --force" | Edit existing or use --force |
| Invalid schedule date | "Schedule date '{{value}}' must be in the future" | Use future date |
| Write failed | "Failed to write to published directory: {{error}}" | Check permissions |
| Delete failed | "Failed to remove draft from _drafts/: {{error}}" | Remove manually |

## Example Usage

```text
# Normal promotion
/blog/publish/promote content/_drafts/building-ebpf-tracing-tools.md

# Schedule for future
/blog/publish/promote content/_drafts/building-ebpf-tracing-tools.md --schedule 2026-03-20T09:00:00Z

# Force without pre-check (not recommended)
/blog/publish/promote content/_drafts/building-ebpf-tracing-tools.md --force
```

## Re-publish Flow

When updating a published post:

1. Edit directly in `src/data/blog/` (marker already present)
2. Update `modDatetime` field
3. Run `/blog/publish/validate` to verify build
4. No re-promotion needed for updates
