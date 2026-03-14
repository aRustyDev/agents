---
description: Write a full blog post draft from an outline using style guidelines
argument-hint: <outline-file> [--style output-style]
allowed-tools: Read, Write, Edit, Glob, Grep, Task
---

# Draft Blog Post

> **DEPRECATED:** This command is deprecated and will be removed in v3.0.0.
> Use `/blog/post/draft` instead, which provides improved workflow integration.

Transform an outline into a complete blog post draft following writing style and code example best practices.

## Arguments

- `$1` - Path to outline file. Example: `posts/_outlines/event-sourcing.md`
- `--style` - Output style to apply (optional):
  - `tutorial-format` - For tutorials
  - `deep-dive-format` - For deep dives
  - If not specified, auto-detect from outline metadata

## Output

Creates: `posts/_drafts/<slug>.md`

## Workflow

### Step 1: Parse Input

1. Read outline from `$1`
2. Extract post type, topic, and target length
3. Load corresponding output style if specified
4. Create draft path from outline slug

### Step 2: Load Skills

Apply these skills during drafting:

- `technical-writing-style` - Voice, tone, clarity
- `code-example-best-practices` - Code formatting

### Step 3: Generate Draft

For each section in the outline:

1. **Expand Content**
   - Transform bullet points into prose
   - Apply one-idea-per-paragraph principle
   - Use active voice, direct address
   - Define technical terms on first use

2. **Write Code Examples**
   - Include necessary imports
   - Use meaningful variable names
   - Comment non-obvious lines (why, not what)
   - Show expected output where helpful
   - Keep blocks under 30 lines

3. **Add Transitions**
   - Connect sections with smooth transitions
   - Reinforce learning progression

### Step 4: Generate Frontmatter

Create YAML frontmatter for the post:

```yaml
---
title: "<title>"
description: "<1-2 sentence summary for SEO>"
date: <YYYY-MM-DD>
author: "<author>"
tags:
  - <tag1>
  - <tag2>
draft: true
type: <post-type>
---
```

### Step 5: Self-Review

Before writing the file, check:

| Guideline | Check |
|-----------|-------|
| Active voice | < 10% passive |
| Sentence length | Average < 25 words |
| Paragraph length | 3-4 sentences |
| Code blocks | All have language tags |
| Code | All examples runnable |
| Headings | Sentence case |

### Step 6: Write Draft

Write to `posts/_drafts/<slug>.md` with:

- YAML frontmatter
- Full post content
- All code examples

### Step 7: Report

```text
## Draft Complete

| Field | Value |
|-------|-------|
| Topic | <topic> |
| Type | <post-type> |
| Output | posts/_drafts/<slug>.md |
| Word Count | ~X words |
| Code Blocks | N |

**Quality Notes:**
- [Any concerns or areas needing review]

**Next steps**:
1. Review draft for technical accuracy
2. Optional: `/seo-pass posts/_drafts/<slug>.md`
3. `/publish-prep posts/_drafts/<slug>.md`
```

## Writing Guidelines Applied

### Voice & Tone

- Use "you" to address the reader directly
- Active voice: "Run the command" not "The command should be run"
- Confident but not arrogant
- Technical but accessible

### Code Examples

- Keep snippets focused and minimal
- Include comments for non-obvious lines
- Show expected output where helpful
- Use consistent formatting
- Use placeholder values like `your-api-key-here`

### Structure

- Lead with value (what will the reader learn?)
- One idea per paragraph
- Use headings to aid scanning
- Break up walls of text

## Examples

```text
/draft-post posts/_outlines/event-sourcing.md
/draft-post posts/_outlines/cli-rust.md --style tutorial-format
```

## Quality Checklist

- [ ] Frontmatter complete and valid YAML
- [ ] Introduction engages and sets expectations
- [ ] Writing is clear and concise
- [ ] Active voice predominates
- [ ] Code examples are correct and runnable
- [ ] Code blocks have language tags
- [ ] Style is consistent throughout
- [ ] Conclusion provides closure/next steps
