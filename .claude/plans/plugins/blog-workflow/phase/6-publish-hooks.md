# Phase 6: Publish Commands & Hooks

## Objective

Get a reviewed draft live on the site, with safety automation.

## Deliverables

### 1. Publish Commands

Create under `.claude/commands/blog/publish/`:

| Command | Purpose |
|---------|---------|
| `seo-review.md` | SEO optimization check |
| `pre-check.md` | Frontmatter + link validation |
| `promote.md` | Move draft to `src/data/blog/` |
| `validate.md` | Build verification |

### 2. SEO Review Checklist

Create `content/_templates/review-checklists/seo.md`:

```markdown
---
type: review-checklist
name: SEO Review
applies_to: draft
---

## Title

- [ ] Under 60 characters
- [ ] Contains primary keyword
- [ ] Compelling/clickable

## Description

- [ ] 150-160 characters
- [ ] Summarizes value proposition
- [ ] Contains primary keyword

## Headings

- [ ] H1 matches title (or close)
- [ ] H2s contain secondary keywords
- [ ] Logical heading hierarchy

## Content

- [ ] Primary keyword in first 100 words
- [ ] Related terms used naturally
- [ ] Internal links to relevant posts

## Images

- [ ] Alt text on all images
- [ ] Descriptive filenames
- [ ] Optimized file sizes
```

### 3. Hook Scripts

Create `.claude/hooks/`:

#### validate-blog-frontmatter.sh

```bash
#!/bin/bash
# Validates AstroPaper frontmatter on writes to src/data/blog/
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

# Only check files in src/data/blog/
[[ "$FILE_PATH" != *"src/data/blog/"* ]] && exit 0
[[ "$FILE_PATH" != *.md ]] && exit 0

CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')
[ -z "$CONTENT" ] && CONTENT=$(cat "$FILE_PATH" 2>/dev/null)

# Check required fields
MISSING=""
echo "$CONTENT" | grep -q "^id:" || MISSING="$MISSING id"
echo "$CONTENT" | grep -q "^pubDatetime:" || MISSING="$MISSING pubDatetime"
echo "$CONTENT" | grep -q "^title:" || MISSING="$MISSING title"
echo "$CONTENT" | grep -q "^description:" || MISSING="$MISSING description"
echo "$CONTENT" | grep -q "^tags:" || MISSING="$MISSING tags"

# Check for common mistakes
WARNINGS=""
echo "$CONTENT" | grep -q "^date:" && WARNINGS="$WARNINGS 'date' found (use 'pubDatetime')."
echo "$CONTENT" | grep -q "^image:" && WARNINGS="$WARNINGS 'image' found (use 'ogImage')."
echo "$CONTENT" | grep -q "^canonical:" && WARNINGS="$WARNINGS 'canonical' found (use 'canonicalURL')."
echo "$CONTENT" | grep -q "^type:" && WARNINGS="$WARNINGS 'type' found (not in AstroPaper schema)."

if [ -n "$MISSING" ]; then
  jq -n --arg m "$MISSING" --arg w "$WARNINGS" '{
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: ("Missing required fields:" + $m + ". " + $w)
    }
  }'
elif [ -n "$WARNINGS" ]; then
  jq -n --arg w "$WARNINGS" '{
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: ("Frontmatter warning:" + $w)
    }
  }'
fi
exit 0
```

#### promote-safety.sh

```bash
#!/bin/bash
# Prevents accidental publish without going through promote command
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

[[ "$FILE_PATH" != *"src/data/blog/"* ]] && exit 0
[[ "$FILE_PATH" != *.md ]] && exit 0

CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')

if echo "$CONTENT" | grep -q "^draft: false"; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      additionalContext: "Post has draft: false. Use /blog/publish/promote for safety checks."
    }
  }'
fi
exit 0
```

### 4. Settings Configuration

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/validate-blog-frontmatter.sh",
            "timeout": 5,
            "statusMessage": "Validating frontmatter"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/promote-safety.sh",
            "timeout": 5,
            "statusMessage": "Checking publish safety"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if files were written to content/_projects/ without updating index.md. Report if stale.",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

## Command Behaviors

### seo-review.md

**Input**: Draft path

**Output**: SEO evaluation with recommendations

**Logic**:

1. Load draft
2. Load SEO checklist
3. Check title length (<60 chars)
4. Check description (150-160 chars)
5. Analyze heading keywords
6. Check image alt text
7. Report findings with suggestions

### pre-check.md

**Input**: Draft path

**Output**: Validation report

**Logic**:

1. Load draft
2. Validate frontmatter against AstroPaper schema
3. Check for required fields
4. Check for wrong field names
5. Run link checker (lychee) if available
6. Verify image paths exist
7. Report pass/fail for each check

### promote.md

**Input**: Validated draft path

**Output**: Published post

**Logic**:

1. Verify draft passed pre-check
2. Read draft from `content/_drafts/<slug>.md`
3. Update frontmatter:
   - `draft: false`
   - `pubDatetime: <current ISO 8601 datetime>`
   - `modDatetime: null` (first publish)
4. Write to `src/data/blog/<slug>.md`
5. **Delete** the file from `content/_drafts/<slug>.md` (content now lives in `src/data/blog/`)
6. Update project status → `publish` in `index.md`
7. If all project posts promoted, update status → `complete`
8. Report success with published URL

### validate.md

**Input**: Published post path

**Output**: Build verification

**Logic**:

1. Run `astro build`
2. Check for errors
3. Verify post appears in output
4. Report success/failure

## Tasks

- [ ] Create `.claude/commands/blog/publish/` directory
- [ ] Write `publish/seo-review.md` command
- [ ] Write `publish/pre-check.md` command
- [ ] Write `publish/promote.md` command
- [ ] Write `publish/validate.md` command
- [ ] Create `content/_templates/review-checklists/seo.md`
- [ ] Create `.claude/hooks/` directory
- [ ] Write `validate-blog-frontmatter.sh` hook
- [ ] Write `promote-safety.sh` hook
- [ ] Make hook scripts executable (`chmod +x`)
- [ ] Merge hook config into `.claude/settings.json`
- [ ] Test hooks fire correctly
- [ ] Test full publish flow

## Acceptance Tests

### Command Tests

- [ ] `/blog/publish/seo-review` checks title (<60 chars), description (150-160)
- [ ] SEO review checks heading keywords and image alt text
- [ ] `/blog/publish/pre-check` validates frontmatter
- [ ] Pre-check reports missing/incorrect fields
- [ ] Pre-check runs link checker or reports skipped
- [ ] `/blog/publish/promote` moves from `_drafts/` to `src/data/blog/`
- [ ] After promote: `draft: false`, `pubDatetime` set
- [ ] `/blog/publish/validate` runs `astro build`
- [ ] Validate confirms post in site output

### Hook Tests

- [ ] **Frontmatter validator**: missing `pubDatetime` triggers warning
- [ ] **Frontmatter validator**: `date:` instead of `pubDatetime:` triggers warning
- [ ] **Frontmatter validator**: files outside `src/data/blog/` not checked
- [ ] **Promote safety**: `draft: false` triggers warning
- [ ] **Index staleness**: artifact change without `index.md` update triggers warning
- [ ] Hook scripts are executable

### State Tests

- [ ] Project `index.md` status updated to `complete` after all posts promoted

## Entry Points

Per SPEC, publish phase can be entered:

- **From post**: After draft is reviewed (normal flow)
- **Directly**: With `/blog/publish/seo-review` for an existing draft

When entering directly:

1. Accept any markdown file in `content/_drafts/`
2. No project context required (though recommended)
3. Can publish standalone drafts not tied to projects

## Dependencies

- Phase 0 (Foundation) — required
- Phase 5 (Post) — optional (can publish existing drafts)

## Estimated Effort

3-4 hours
