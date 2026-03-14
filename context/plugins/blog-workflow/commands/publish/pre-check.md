---
name: blog/publish/pre-check
description: Validate frontmatter and links before publish
argument-hint: <path> [--skip-links]
arguments:
  - name: path
    description: Path to the draft file
    required: true
  - name: skip-links
    description: Skip link validation (faster)
    required: false
  - name: force
    description: Mark as pre-checked even with warnings
    required: false
---

# Pre-Check Command

Validate frontmatter and links before publishing. Pre-check must pass before promotion unless `--force` is used on promote.

## Tools

- `Read` - Load draft
- `Edit` - Add `_precheck` status to frontmatter
- `Bash` - Run lychee link checker (if available)

## Behavior

1. **Load draft** at `{{path}}`

2. **Validate frontmatter** against AstroPaper schema:
   - Required fields present: `id`, `title`, `description`, `pubDatetime`, `tags`
   - No wrong field names: `date` (should be `pubDatetime`), `image` (should be `ogImage`)
   - `id` is valid UUIDv4
   - `pubDatetime` is valid ISO 8601
   - `description` <= 160 characters

3. **Check links** (unless `--skip-links`):
   - Run `lychee --no-progress --timeout 10 {{path}}`
   - Report broken links
   - If lychee not available, note "link check skipped"
   - Timeout after 30 seconds

4. **Verify image paths**:
   - Check that referenced images exist
   - Check image paths are valid

5. **Update frontmatter** with pre-check status:

   ```yaml
   _precheck:
     status: passed  # or failed
     timestamp: 2026-03-14T15:00:00Z
     warnings: 2
     fails: 0
   ```

6. **Report pass/fail** for each check

## Output (Passing)

```text
## Pre-Check: {{filename}}

### Frontmatter Validation
- [x] id: valid UUIDv4 - pass
- [x] title: present - pass
- [x] description: {{N}} chars (<=160) - pass
- [x] pubDatetime: valid ISO 8601 - pass
- [x] tags: present ({{N}} tags) - pass
- [x] No deprecated fields - pass

### Link Check
- [x] lychee: {{N}} links checked, 0 broken - pass

### Image Check
- [x] All {{N}} images exist - pass

Summary: {{pass}} pass, {{warn}} warn, {{fail}} fail

Pre-check status added to frontmatter.
Status: READY FOR PROMOTION

Next: Run `/blog/publish/promote {{path}}`
```

## Output (Failing)

```text
## Pre-Check: {{filename}}

### Frontmatter Validation
- [ ] id: missing - fail
- [x] title: present - pass
- [ ] description: {{N}} chars (>160) - fail
- [x] pubDatetime: valid - pass
- [ ] 'date' field found - fail: use 'pubDatetime' instead

Summary: {{pass}} pass, {{warn}} warn, {{fail}} fail
Status: NOT READY

Fix the issues above before promoting.
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Draft not found | "Draft not found at {{path}}" | Verify path |
| Missing required field | "Missing required field: {{field}}" | Add field to frontmatter |
| Invalid UUID | "id '{{value}}' is not valid UUIDv4" | Generate new UUID |
| Invalid date | "pubDatetime '{{value}}' is not valid ISO 8601" | Fix date format |
| Description too long | "description is {{N}} chars (max 160)" | Shorten description |
| Lychee not available | "Link check skipped (lychee not installed)" | Install lychee or use --skip-links |
| Lychee timeout | "Link check timed out after 30s" | Use --skip-links or check manually |
| Broken links found | "{{N}} broken links found: {{urls}}" | Fix or remove broken links |

## Example Usage

```text
# Full pre-check
/blog/publish/pre-check content/_drafts/building-ebpf-tracing-tools.md

# Skip link validation
/blog/publish/pre-check content/_drafts/building-ebpf-tracing-tools.md --skip-links

# Mark as passed even with warnings
/blog/publish/pre-check content/_drafts/building-ebpf-tracing-tools.md --force
```
