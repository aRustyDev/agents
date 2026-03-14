---
name: blog/publish/seo-review
description: SEO optimization check for blog draft
argument-hint: <path> [--fix]
arguments:
  - name: path
    description: Path to the draft file
    required: true
  - name: fix
    description: Auto-fix simple issues (expand description, add keywords)
    required: false
---

# SEO Review Command

Check SEO best practices for a blog draft. This is an advisory check that provides recommendations without blocking publication.

## Tools

- `Read` - Load draft and checklist
- `Edit` - Apply fixes (if `--fix`)

## Behavior

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

8. **Auto-fix** (if `--fix`):
   - Expand short descriptions with content summary
   - Add missing alt text placeholders
   - Report what was fixed

9. **Report findings** with specific suggestions

> **Note**: SEO review is advisory. Without `--fix`, it does not modify the draft or append a `## Review` section.

## Output

```text
## SEO Review: {{filename}}

### Title: "{{title}}"
- [x] Length: {{N}} chars (under 60) - pass
- [x] Contains keyword: "{{keyword}}" - pass
- [x] Compelling - pass

### Description
- [~] Length: {{N}} chars - warn: consider expanding to 150-160 chars
- [x] Contains keyword - pass
- [x] Value proposition clear - pass

### Headings
- [x] H1 matches title - pass
- [x] H2s have keywords - pass
- [x] Logical hierarchy - pass

### Content
- [x] Keyword in first 100 words - pass
- [x] Related terms present - pass
- [~] Internal links - warn: consider adding links to related posts

### Images
- [x] All have alt text - pass
- [x] Descriptive filenames - pass

Summary: {{pass}} pass, {{warn}} warn, {{fail}} fail

Suggestions:
1. {{specific suggestion}}
2. {{specific suggestion}}

Next: Run `/blog/publish/pre-check {{path}}`
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Draft not found | "Draft not found at {{path}}" | Verify path |
| Not a markdown file | "Expected .md file, got {{ext}}" | Check file extension |
| No frontmatter | "Draft has no frontmatter" | Add YAML frontmatter |
| Fix failed | "Could not auto-fix: {{reason}}" | Apply fix manually |

## Example Usage

```text
# SEO review
/blog/publish/seo-review content/_drafts/building-ebpf-tracing-tools.md

# Auto-fix simple issues
/blog/publish/seo-review content/_drafts/building-ebpf-tracing-tools.md --fix
```
