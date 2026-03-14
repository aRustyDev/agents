# Phase 6: Publish Commands & Hooks

## Objective

Get a reviewed draft live on the site, with safety automation via hooks.

## Architecture Note

Publish is the only phase without a refine loop. Commands are linear checks leading to promotion:

- **`seo-review`** — Check SEO best practices
- **`pre-check`** — Validate frontmatter and links
- **`promote`** — Move draft to `src/data/blog/`
- **`validate`** — Verify build succeeds

```
publish/
├── seo-review.md   → SEO optimization check
├── pre-check.md    → Frontmatter + link validation
├── promote.md      → Move to src/data/blog/
└── validate.md     → Build verification
```

Additionally, this phase introduces **hook scripts** that provide safety automation:

- **Frontmatter validator** — Warns on missing/wrong fields in `src/data/blog/`
- **Promote safety** — Prevents bypassing the promote workflow
- **Index staleness** — Warns if `index.md` wasn't updated

## Deliverables

### 1. Publish Commands

Create under `context/plugins/blog-workflow/commands/publish/`:

| Command | Purpose | Output |
|---------|---------|--------|
| `seo-review.md` | SEO optimization check | Advisory report |
| `pre-check.md` | Frontmatter + link validation | Pass/fail report |
| `promote.md` | Move draft to `src/data/blog/` | Published post |
| `validate.md` | Build verification | Build status |

**Command frontmatter pattern**:

```yaml
---
name: blog:publish:seo-review
description: SEO optimization check for blog draft
arguments:
  - name: path
    description: Path to the draft file
    required: true
---
```

### 2. SEO Review Checklist

Create `context/plugins/blog-workflow/.templates/review-checklists/seo.md`:

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

Create under `context/plugins/blog-workflow/hooks/`:

#### validate-blog-frontmatter.sh

```bash
#!/bin/bash
# Validates AstroPaper frontmatter on writes to src/data/blog/
# Configured in .claude/settings.json as PostToolUse hook

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

# Check for common mistakes (wrong field names)
WARNINGS=""
echo "$CONTENT" | grep -q "^date:" && WARNINGS="$WARNINGS 'date' found (use 'pubDatetime')."
echo "$CONTENT" | grep -q "^image:" && WARNINGS="$WARNINGS 'image' found (use 'ogImage')."
echo "$CONTENT" | grep -q "^canonical:" && WARNINGS="$WARNINGS 'canonical' found (use 'canonicalURL')."
echo "$CONTENT" | grep -q "^type:" && WARNINGS="$WARNINGS 'type' found (not in AstroPaper schema)."

if [ -n "$MISSING" ]; then
  jq -n --arg m "$MISSING" --arg w "$WARNINGS" '{
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: ("Blog post frontmatter issue: missing required fields:" + $m + ". " + $w + " See context/plugins/blog-workflow/rules/blog-frontmatter.md for the correct schema.")
    }
  }'
elif [ -n "$WARNINGS" ]; then
  jq -n --arg w "$WARNINGS" '{
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: ("Blog post frontmatter warning:" + $w + " See context/plugins/blog-workflow/rules/blog-frontmatter.md for the correct schema.")
    }
  }'
fi

exit 0
```

#### promote-safety.sh

```bash
#!/bin/bash
# Prevents accidental writes to src/data/blog/ that bypass the promote workflow
# Configured in .claude/settings.json as PreToolUse hook

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only check writes to src/data/blog/
if [[ "$FILE_PATH" != *"src/data/blog/"* ]]; then
  exit 0
fi

if [[ "$FILE_PATH" != *.md ]]; then
  exit 0
fi

CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')

# Skip if this write was made by the promote command
# The promote command adds this marker to bypass its own safety hook
if echo "$CONTENT" | grep -q "# promoted-by: /blog/publish/promote"; then
  exit 0
fi

# Warn if draft: true is NOT present (catches both draft: false and missing draft field)
if ! echo "$CONTENT" | grep -q "^draft: true"; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      additionalContext: "Writing to src/data/blog/ without draft: true. Use /blog/publish/promote to ensure all pre-checks pass first, or set draft: true if this post is not ready to publish."
    }
  }'
fi

exit 0
```

### 4. Settings Configuration

Add to `.claude/settings.json` (merge with existing hooks):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "./context/plugins/blog-workflow/hooks/validate-blog-frontmatter.sh",
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
            "command": "./context/plugins/blog-workflow/hooks/promote-safety.sh",
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
            "prompt": "Check if any files were written to content/_projects/ during this session. If so, verify that the corresponding index.md was also updated. If index.md was not updated, respond with {\"ok\": false, \"reason\": \"Project index.md may be out of date - artifacts were modified in content/_projects/<slug>/ but index.md was not updated.\"}. Otherwise respond {\"ok\": true}.",
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

**Input**: Path to draft

**Output**: SEO evaluation with recommendations (advisory, not blocking)

**Arguments**:
- `path` (required): Path to the draft file

**Tools Used**:
- `Read` — load draft and checklist

**Logic**:

1. **Load draft** at `{{path}}`
2. **Load SEO checklist** from `.templates/review-checklists/seo.md`
3. **Check title**:
   - Length < 60 characters
   - Contains primary keyword
   - Is compelling/clickable
4. **Check description**:
   - Length 150-160 characters
   - Summarizes value proposition
   - Contains primary keyword
5. **Analyze headings**:
   - H1 matches or approximates title
   - H2s contain secondary keywords
   - Hierarchy is logical (no skipped levels)
6. **Check content**:
   - Primary keyword in first 100 words
   - Related terms used naturally
   - Internal links present
7. **Check images**:
   - Alt text on all images
   - Descriptive filenames
   - File sizes reasonable
8. **Report findings** with specific suggestions

> **Note**: SEO review is advisory. It does not modify the draft or append a `## Review` section. Suggestions are presented for the user to apply manually or via `blog:post:refine`.

**Example output**:

```text
## SEO Review: building-ebpf-tracing-tools.md

### Title: "Building eBPF Tracing Tools: A Practical Guide"
- [x] Length: 47 chars (under 60) — pass
- [x] Contains keyword: "eBPF" — pass
- [x] Compelling — pass

### Description
- [~] Length: 89 chars — warn: consider expanding to 150-160 chars
- [x] Contains keyword — pass
- [x] Value proposition clear — pass

### Headings
- [x] H1 matches title — pass
- [x] H2s have keywords — pass
- [x] Logical hierarchy — pass

### Content
- [x] Keyword in first 100 words — pass
- [x] Related terms present — pass
- [~] Internal links — warn: consider adding links to related posts

### Images
- [x] All have alt text — pass
- [x] Descriptive filenames — pass

Summary: 10 pass, 2 warn, 0 fail

Suggestions:
1. Expand description to 150-160 characters for better SERP display
2. Add internal links to related posts (e.g., Linux tracing basics)

Next: Run `blog:publish:pre-check {{path}}` to validate frontmatter
```

### pre-check.md

**Input**: Path to draft

**Output**: Pass/fail validation report

**Arguments**:
- `path` (required): Path to the draft file

**Tools Used**:
- `Read` — load draft
- `Bash` — run lychee link checker (if available)

**Logic**:

1. **Load draft** at `{{path}}`
2. **Validate frontmatter** against AstroPaper schema:
   - Required fields present: `id`, `title`, `description`, `pubDatetime`, `tags`
   - No wrong field names: `date` (should be `pubDatetime`), `image` (should be `ogImage`)
   - `id` is valid UUIDv4
   - `pubDatetime` is valid ISO 8601
   - `description` ≤ 160 characters
3. **Check links** (if lychee available):
   - Run `lychee --no-progress {{path}}`
   - Report broken links
   - If lychee not available, note "link check skipped"
4. **Verify image paths**:
   - Check that referenced images exist
   - Check image paths are valid
5. **Report pass/fail** for each check

> **Note**: Pre-check must pass before promote. Any fail blocks promotion.

**Example output**:

```text
## Pre-Check: building-ebpf-tracing-tools.md

### Frontmatter Validation
- [x] id: valid UUIDv4 — pass
- [x] title: present — pass
- [x] description: 89 chars (≤160) — pass
- [x] pubDatetime: valid ISO 8601 — pass
- [x] tags: present (3 tags) — pass
- [x] No deprecated fields — pass

### Link Check
- [x] lychee: 12 links checked, 0 broken — pass

### Image Check
- [x] All 2 images exist — pass

Summary: 8 pass, 0 warn, 0 fail
Status: READY FOR PROMOTION

Next: Run `blog:publish:promote {{path}}` to publish
```

**Example output (failing)**:

```text
## Pre-Check: my-draft.md

### Frontmatter Validation
- [ ] id: missing — fail
- [x] title: present — pass
- [ ] description: 245 chars (>160) — fail
- [x] pubDatetime: valid — pass
- [ ] 'date' field found — fail: use 'pubDatetime' instead

Summary: 2 pass, 0 warn, 3 fail
Status: NOT READY

Fix the issues above before promoting.
```

### promote.md

**Input**: Path to validated draft

**Output**: Published post at `src/data/blog/<slug>.md`

**Arguments**:
- `path` (required): Path to the draft file

**Tools Used**:
- `Read` — load draft
- `Write` — write to `src/data/blog/`
- `Bash` — delete from `_drafts/`

**Logic**:

1. **Load draft** from `content/_drafts/<slug>.md`
2. **Verify pre-check passed**:
   - If not, error: "Draft must pass pre-check before promotion. Run `blog:publish:pre-check` first."
3. **Update frontmatter**:
   - Add `# promoted-by: /blog/publish/promote` as first line (bypasses safety hook)
   - Set `draft: false`
   - Set `pubDatetime: <current ISO 8601>` (if not already set)
   - Set `modDatetime: null` (first publish)
4. **Write to** `src/data/blog/<slug>.md`
5. **Delete from** `content/_drafts/<slug>.md`
   - The draft is now at its final location
6. **Update project** (if draft is part of a project):
   - Update phase status → `complete`
   - Check if all phases are complete
   - If all complete, update project status → `complete` in `index.md`
   - Otherwise, update project status → `publish`
7. **Report success** with published path

> **Important**: The `# promoted-by: /blog/publish/promote` marker is required. The `promote-safety.sh` hook checks for this marker and skips its warning when present. This is the ONLY intended path to write `draft: false` content to `src/data/blog/`.

**Example output**:

```text
Promoted: content/_drafts/building-ebpf-tracing-tools.md
      →   src/data/blog/building-ebpf-tracing-tools.md

Frontmatter updated:
- draft: false
- pubDatetime: 2026-03-14T15:30:00Z

Draft deleted from: content/_drafts/

Project status: publish (2/3 phases complete)

Next: Run `blog:publish:validate {{path}}` to verify build
```

### validate.md

**Input**: Path to published post

**Output**: Build verification result

**Arguments**:
- `path` (required): Path to the published post in `src/data/blog/`

**Tools Used**:
- `Bash` — run astro build

**Logic**:

1. **Run Astro build**:

   ```bash
   astro build 2>&1
   ```

2. **Check for errors**:
   - If build fails, report error details
   - If build succeeds, continue
3. **Verify post in output**:
   - Check that post appears in `dist/` output
   - Verify post URL is accessible
4. **Report success/failure**

**Example output (success)**:

```text
## Build Validation: building-ebpf-tracing-tools.md

### Astro Build
- [x] Build completed successfully — pass
- [x] No errors — pass
- [x] No warnings — pass

### Post Verification
- [x] Post found in dist/blog/building-ebpf-tracing-tools/ — pass
- [x] HTML generated correctly — pass

Build time: 4.2s
Output size: 23KB

Status: PUBLISHED SUCCESSFULLY

Post URL: /blog/building-ebpf-tracing-tools/
```

**Example output (failure)**:

```text
## Build Validation: my-post.md

### Astro Build
- [ ] Build failed — fail

Error:
  [ERROR] Invalid frontmatter in src/data/blog/my-post.md
  pubDatetime is not a valid date

Status: BUILD FAILED

Fix the error and run `blog:publish:validate` again.
Consider rolling back with: git checkout src/data/blog/my-post.md
```

## Hook Behavior Details

### Hook 1: Frontmatter Validator

**Event**: `PostToolUse` (after Write/Edit)
**Scope**: Files in `src/data/blog/*.md` only
**Purpose**: Warn about missing or incorrect frontmatter fields

| Trigger | Action |
|---------|--------|
| Missing required field | Warn with field name and schema reference |
| Wrong field name (e.g., `date:`) | Warn with correct field name |
| File outside `src/data/blog/` | Skip (no action) |

### Hook 2: Promote Safety

**Event**: `PreToolUse` (before Write)
**Scope**: Files in `src/data/blog/*.md` only
**Purpose**: Prevent bypassing the promote workflow

| Trigger | Action |
|---------|--------|
| `draft: false` without marker | Warn to use promote command |
| Missing `draft` field | Warn to use promote command |
| `# promoted-by` marker present | Skip (allow write) |
| `draft: true` | Skip (allow write) |
| File outside `src/data/blog/` | Skip (no action) |

### Hook 3: Index Staleness

**Event**: `Stop` (when Claude stops)
**Scope**: All `content/_projects/` modifications
**Purpose**: Remind to update `index.md` when artifacts change

| Trigger | Action |
|---------|--------|
| Artifacts modified, `index.md` unchanged | Warn about potential staleness |
| `index.md` updated | No warning |

## Project Structure After Publish

```text
content/_projects/<slug>/
├── index.md                    # status: complete (all phases done)
├── idea.md                     # status: complete
├── plan.md                     # status: complete
├── research/
│   └── ...                     # all complete
├── content-brainstorm.md       # status: complete
├── phase/
│   ├── 0-tutorial-basics.md    # status: complete
│   └── 1-deep-dive-state.md    # status: complete
└── post/
    ├── tutorial-basics/
    │   ├── spec.md             # status: complete
    │   └── outline.md          # status: complete
    └── deep-dive-state/
        ├── spec.md             # status: complete
        └── outline.md          # status: complete

content/_drafts/
└── (empty - drafts promoted)

src/data/blog/
├── kubernetes-migration-tutorial-basics.md    # draft: false
└── kubernetes-migration-deep-dive-state.md    # draft: false
```

## Entry Points

Per SPEC, publish phase can be entered at:

| Scenario | Start At | Notes |
|----------|----------|-------|
| From post review | `blog:publish:seo-review` | Normal flow |
| Existing draft | `blog:publish:seo-review` | Any draft in `_drafts/` |
| Skip SEO | `blog:publish:pre-check` | Proceed directly to validation |

### Direct Entry Without Project

When publishing a standalone draft not tied to a project:

1. Accept any markdown file in `content/_drafts/`
2. No project context required
3. Skip project status updates
4. Proceed with normal publish flow

## Error Handling

| Scenario | Response |
|----------|----------|
| Pre-check fails | Block promotion, report issues |
| Astro build fails | Report error, suggest rollback |
| Lychee not available | Skip link check, note in output |
| Draft not found | Error with path suggestion |
| Already promoted | Error: "Post already exists at src/data/blog/" |

## Alignment with SPEC

This phase implements SPEC sections:

- **Phase 5: Publish** (lines 160-175) — command structure and flow
- **Hooks** (lines 766-936) — all three hooks with settings config
- **Promote marker** (line 854) — `# promoted-by` bypass mechanism

Key SPEC quotes implemented:

> "promote | Validated draft | Moves file to `src/data/blog/<slug>.md`, sets `draft: false`, sets `pubDatetime`, adds `# promoted-by: /blog/publish/promote` marker (bypasses promote safety hook)"
>
> "The `/blog/publish/promote` command is the **only** intended path to write `draft: false` into `src/data/blog/`. To avoid the hook warning on its own output, the `promote` command writes with a `# promoted-by: /blog/publish/promote` comment in the frontmatter."

## Tasks

### Commands (4 files)

- [ ] Create `context/plugins/blog-workflow/commands/publish/` directory
- [ ] Write `commands/publish/seo-review.md` with command frontmatter
- [ ] Write `commands/publish/pre-check.md` with command frontmatter
- [ ] Write `commands/publish/promote.md` with command frontmatter
- [ ] Write `commands/publish/validate.md` with command frontmatter

### Templates (1 file)

- [ ] Create `.templates/review-checklists/seo.md`

### Hooks (2 scripts + config)

- [ ] Create `context/plugins/blog-workflow/hooks/` directory
- [ ] Write `hooks/validate-blog-frontmatter.sh`
- [ ] Write `hooks/promote-safety.sh`
- [ ] Make hook scripts executable (`chmod +x`)
- [ ] Merge hook config into `.claude/settings.json`

### Plugin Updates

- [ ] Update `plugin.json` with 4 new commands
- [ ] Update `marketplace.json` version (1.5.0 → 1.6.0)

### Testing

- [ ] Test seo-review: title length, description length, keywords
- [ ] Test pre-check: frontmatter validation, link check
- [ ] Test promote: draft → src/data/blog/, marker added
- [ ] Test promote: draft deleted from _drafts/
- [ ] Test validate: astro build runs, post appears
- [ ] Test hook: missing field triggers warning
- [ ] Test hook: wrong field name triggers warning
- [ ] Test hook: promote marker bypasses safety hook
- [ ] Test hook: draft: true bypasses safety hook
- [ ] Test hook: files outside src/data/blog/ not checked
- [ ] Test project completion: all phases → status: complete

## Acceptance Tests

### Command Tests

- [ ] `/blog/publish/seo-review` checks title (<60 chars), description (150-160)
- [ ] SEO review checks heading keywords and image alt text
- [ ] SEO review is advisory (doesn't modify draft)
- [ ] `/blog/publish/pre-check` validates frontmatter against AstroPaper schema
- [ ] Pre-check reports missing/incorrect fields
- [ ] Pre-check runs link checker or reports skipped
- [ ] Pre-check failure blocks promotion
- [ ] `/blog/publish/promote` moves from `_drafts/` to `src/data/blog/`
- [ ] Promote adds `# promoted-by: /blog/publish/promote` marker
- [ ] After promote: `draft: false`, `pubDatetime` set
- [ ] After promote: draft deleted from `_drafts/`
- [ ] `/blog/publish/validate` runs `astro build`
- [ ] Validate confirms post in site output

### Hook Tests

- [ ] **Frontmatter validator**: missing `pubDatetime` triggers warning
- [ ] **Frontmatter validator**: `date:` instead of `pubDatetime:` triggers warning
- [ ] **Frontmatter validator**: files outside `src/data/blog/` not checked
- [ ] **Promote safety**: `draft: false` without marker triggers warning
- [ ] **Promote safety**: `# promoted-by` marker bypasses warning
- [ ] **Promote safety**: `draft: true` bypasses warning
- [ ] **Index staleness**: artifact change without `index.md` update triggers warning
- [ ] Hook scripts are executable

### State Tests

- [ ] Project `index.md` status updated to `publish` when first post promoted
- [ ] Project `index.md` status updated to `complete` after all posts promoted

## Dependencies

- Phase 0 (Foundation) — required for rules and schemas
- Phase 5 (Post) — optional (can publish existing drafts)
- External tools: `astro` (required), `lychee` (optional)

## Estimated Effort

4-5 hours

- Commands (4 files): 2 hours
- SEO checklist (1 file): 15 min
- Hook scripts (2 files): 1 hour
- Settings config: 15 min
- Plugin manifest updates: 15 min
- Testing all workflows: 1 hour
