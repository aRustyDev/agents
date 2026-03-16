# Outline Templates

Outline templates provide starting structures for different post types.

## Available Outlines

| Template | Post Type | Sections |
|----------|-----------|----------|
| `tutorial.md` | Tutorial | Objectives, Prerequisites, Steps, Summary |
| `walk-through.md` | Walk-through | Goal, Setup, Steps, Learnings |
| `deep-dive.md` | Deep Dive | Context, Analysis, Implications |
| `research.md` | Research | Abstract, Methodology, Results, Discussion |
| `study-review.md` | Study Review | What Studied, Takeaways, Gaps |
| `review.md` | Review | Overview, Evaluation, Verdict |
| `comparison.md` | Comparison | Criteria, Analysis, Recommendation |
| `problems.md` | Problems | Statement, Evidence, Analysis |
| `open-questions.md` | Open Questions | Question, Context, Possibilities |
| `planning.md` | Planning | Goals, Approach, Risks |
| `retrospective.md` | Retrospective | Goal, Outcome, Learnings |
| `updates.md` | Updates | Progress, Status, Next Steps |
| `opinions.md` | Opinions | Opinion, Reasoning, Caveats |
| `dev-blog.md` | Dev Blog | Context, Insight, Examples |
| `announcement.md` | Announcement | What, Why, How |
| `reference.md` | Reference | Categories, Items |
| `eli5.md` | ELI5 | Complex Thing, Simple Explanation |
| `5-levels.md` | 5 Levels | Level 1-5 explanations |

## Template Format

Each outline template is a markdown file with:

```markdown
---
name: tutorial
post-type: tutorial
description: Structure for teaching a concept step-by-step
---

# {{title}}

## Introduction

- Hook the reader
- State what they'll learn
- Prerequisites

## Learning Objectives

After reading, you will:

- Objective 1
- Objective 2

## Prerequisites

- Prereq 1
- Prereq 2

## Main Content

### Step 1: {{step-title}}

{{content}}

### Step 2: {{step-title}}

{{content}}

## Summary

- Key takeaway 1
- Key takeaway 2

## Next Steps

- What to learn next
- Related resources
```

## Using Templates

### During Content Draft

```bash
/blog/content/draft <project> --template tutorial
```

### Manual Selection

1. Browse `content/_templates/outlines/`
2. Copy desired template
3. Fill in placeholders

## Customizing Templates

### Override Built-in

1. Copy from plugin to project:

   ```bash
   cp ~/.claude/plugins/blog-workflow/.templates/outlines/tutorial.md \
      content/_templates/outlines/tutorial.md
   ```

2. Edit as needed

3. Workflow prefers project-local templates

### Create Custom

1. Create in `content/_templates/outlines/`
2. Follow template format with frontmatter
3. Use `{{placeholder}}` syntax for variable content

## Template Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{{title}}` | Post title |
| `{{date}}` | Current date |
| `{{author}}` | Author name |
| `{{description}}` | Post description |
| `{{step-title}}` | Section title |
| `{{content}}` | Section content |

## See Also

- [Choosing a Post Type](../workflow/choosing-type.md)
- [Post Types Reference](../taxonomy/post/types.md)
