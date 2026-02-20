---
description: Final validation and preparation before publishing a blog post
argument-hint: <draft-file> [--check-links] [--generate-social]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(lychee:*), Bash(python3:*)
---

# Publish Prep

Final validation and preparation before publishing a blog post.

## Arguments

- `$1` - Path to draft file. Example: `posts/_drafts/event-sourcing.md`
- `--check-links` - Run link validation with lychee (default: true)
- `--generate-social` - Generate social media snippets (default: false)

## Output

- Validated post at: `posts/<slug>.md`
- Optional social snippets at: `posts/_social/<slug>.md`

## Workflow

### Step 1: Parse Input

1. Read draft from `$1`
2. Parse flags: `--check-links`, `--generate-social`
3. Extract slug from filename

### Step 2: Validate Frontmatter

Run frontmatter validation:

```bash
python3 -c "import sys,yaml; yaml.safe_load(open(sys.argv[1]).read().split('---')[1])" "$DRAFT_FILE"
```

Required fields:

- [ ] `title` - Non-empty string
- [ ] `description` - Non-empty, under 160 chars
- [ ] `date` - Valid YYYY-MM-DD format
- [ ] `tags` - At least 1 tag
- [ ] `type` - One of: tutorial, deep-dive, research-summary, dev-journal

### Step 3: Code Block Validation

Check all code blocks have language tags:

```bash
grep -E '^```$' "$DRAFT_FILE" && echo "Warning: code block without language tag"
```

### Step 4: Link Validation (Optional)

If `--check-links` (default):

```bash
lychee --no-progress "$DRAFT_FILE"
```

Report any broken links for manual review.

### Step 5: Final Checklist

| Check | Status |
|-------|--------|
| Frontmatter valid | ✓/✗ |
| All code blocks tagged | ✓/✗ |
| Links valid | ✓/✗/skipped |
| Images have alt text | ✓/✗/N/A |
| Draft flag removed | ✓/✗ |

### Step 6: Prepare for Publishing

1. Update frontmatter:
   - Remove `draft: true` or set to `false`
   - Verify date is correct

2. Move to final location:

   ```text
   posts/_drafts/<slug>.md → posts/<slug>.md
   ```

### Step 7: Generate Social Snippets (Optional)

If `--generate-social`:

Create `posts/_social/<slug>.md`:

```markdown
# Social Snippets: <Title>

## Twitter/X (280 chars)

<concise hook + link>

## LinkedIn

<professional summary, 2-3 sentences>

## Mastodon (500 chars)

<detailed summary with hashtags>

## Hacker News Title

<title optimized for HN, no clickbait>
```

### Step 8: Report

```text
## Ready to Publish

| Field | Value |
|-------|-------|
| Title | <title> |
| Output | posts/<slug>.md |
| Word Count | ~X words |
| Tags | tag1, tag2 |

**Validation Results:**
- Frontmatter: ✓ Valid
- Code blocks: ✓ All tagged
- Links: ✓ All valid (or list issues)

**Files:**
- Post: `posts/<slug>.md`
- Social: `posts/_social/<slug>.md` (if generated)

**To publish:**
1. Review the final file
2. Commit: `git add posts/<slug>.md && git commit -m "Add post: <title>"`
3. Push to trigger deploy
```

## Examples

```text
/publish-prep posts/_drafts/event-sourcing.md
/publish-prep posts/_drafts/cli-rust.md --check-links --generate-social
/publish-prep posts/_drafts/quick-tip.md --check-links=false
```

## Validation Reference

### Frontmatter Schema

```yaml
---
title: string (required, non-empty)
description: string (required, max 160 chars)
date: YYYY-MM-DD (required)
author: string (optional)
tags: [string] (required, min 1)
type: tutorial|deep-dive|research-summary|dev-journal (required)
draft: boolean (removed on publish)
image: string (optional, path to hero image)
canonical: string (optional, URL if cross-posted)
---
```

### Common Issues

| Issue | Fix |
|-------|-----|
| Missing description | Add 1-2 sentence summary |
| Description too long | Keep under 160 chars for SEO |
| Invalid date format | Use YYYY-MM-DD |
| No tags | Add at least 1 relevant tag |

| Code block without lang | Add language after ``` |
| Broken link | Fix URL or remove link |
