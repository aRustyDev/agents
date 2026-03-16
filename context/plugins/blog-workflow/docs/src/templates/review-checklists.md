# Review Checklist Templates

Review checklists ensure quality gates between workflow phases.

## Available Checklists

| Checklist | Phase | Items |
|-----------|-------|-------|
| `idea.md` | Idea → Research | 7 items |
| `research.md` | Research → Planning | 7 items |
| `content.md` | Planning → Drafting | 7 items |
| `post.md` | Drafting → Publish | 10 items |
| `seo.md` | Pre-publish | 10 items |
| `publish.md` | Final check | 10 items |

## Checklist Format

```markdown
---
name: post-review
phase: post
description: Review checklist for post drafts
---

# Post Review Checklist

## Required

These must pass to proceed:

- [ ] Title is compelling and accurate
- [ ] Introduction engages quickly
- [ ] Content matches outline
- [ ] No unfinished sections

## Recommended

Should pass, can proceed with justification:

- [ ] Code examples are tested
- [ ] Images have alt text
- [ ] Voice is consistent

## Optional

Nice to have:

- [ ] Social sharing preview checked
- [ ] Mobile rendering verified
```

## Using Checklists

### Automatic Application

Review commands apply the appropriate checklist:

```bash
/blog/post/review content/_drafts/<slug>.md
# Applies post review checklist automatically
```

### Manual Review

1. Open relevant checklist
2. Go through each item
3. Note failures and suggestions
4. Determine verdict (pass/revise/fail)

## Customizing Checklists

### Override Built-in

Copy and modify:

```bash
cp ~/.claude/plugins/blog-workflow/.templates/review-checklists/post.md \
   content/_templates/review-checklists/post.md
```

### Add Custom Checklist

Create new checklist for specific needs:

```markdown
---
name: code-heavy-post
phase: post
extends: post  # Inherits from post.md
description: Additional checks for code-heavy posts
---

# Code-Heavy Post Review

## Additional Required

- [ ] All code snippets run without errors
- [ ] Output shown matches actual output
- [ ] Error handling demonstrated
- [ ] Edge cases discussed
```

### Type-Specific Checklists

Create checklists for specific post types:

```text
content/_templates/review-checklists/
├── tutorial-post.md    # Tutorial-specific items
├── review-post.md      # Review-specific items
└── research-post.md    # Research-specific items
```

## Review Output Format

Checklists produce structured output:

```markdown
## Review: understanding-rust-ownership.md

### Passed (7/10)

- [x] Title is compelling
- [x] Introduction engages
- [x] Content matches outline
...

### Failed (2/10)

- [ ] Code examples not tested
  → Run code locally to verify
- [ ] Alt text missing on diagram
  → Add: "Diagram showing ownership transfer"

### Warnings (1/10)

- [ ] Voice shifts in section 3
  → Consider: Maintain first-person throughout

### Verdict: NEEDS REVISION

Fix 2 failed items before proceeding.
```

## Verdict Criteria

| Verdict | Meaning |
|---------|---------|
| PASS | All required items pass |
| NEEDS REVISION | Some required items fail |
| MAJOR REVISION | Multiple required items fail |
| FAIL | Fundamental issues, reconsider approach |

## Best Practices

1. **Don't skip checklists** - They catch real issues
2. **Address all failures** - Don't proceed with known issues
3. **Document waivers** - If proceeding despite failure, note why
4. **Update checklists** - Add items for recurring issues
5. **Time-box reviews** - Don't over-analyze; trust the checklist

## See Also

- [Review Commands](../reference/commands.md)
- [Publishing Process](../workflow/publishing.md)
