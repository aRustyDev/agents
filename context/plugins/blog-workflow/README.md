# Blog Workflow Plugin

Structured workflow for creating technical blog posts from research through publication. Supports tutorials, deep dives, research summaries, and development journals.

## Post Types

| Type | Use Case |
|------|----------|
| Tutorial | Step-by-step guides, how-tos, implementation walkthroughs |
| Deep Dive | In-depth analysis of tools, patterns, architectures |
| Research Summary | Synthesizing findings, literature reviews |
| Dev Journal | Project updates, lessons learned, build logs |

## Components

| Type | Count | Status |
|------|-------|--------|
| Skills | 4 | 4 create |
| Commands | 8 | 8 create |
| Agents | 3 | 2 extend, 1 create |
| Styles | 4 | 4 create |
| Hooks | 3 | 1 reuse, 2 create |

## Workflow Pipeline

```text
/research-topic
      │
      ▼
/refine-research-plan (optional)
      │
      ▼
/gather-resources (optional)
      │
      ▼
/outline-post
      │
      ▼
/draft-post ──► technical-editor review
      │
      ▼
/seo-pass
      │
      ▼
/publish-prep ──► validation hooks
      │
      ▼
   Published!
```

## Setup

1. Install dependencies:

   ```bash
   just install-plugin blog-workflow
   ```

## Key Commands

- `/research-topic` - Gather sources, synthesize background
- `/outline-post` - Generate structured outline
- `/draft-post` - Write full draft from outline
- `/seo-pass` - Optimize for search
- `/publish-prep` - Final validation and formatting
- `/series-plan` - Plan multi-part series

## Output Styles

- `tutorial-format` - Prerequisites, steps, code blocks, outcomes
- `deep-dive-format` - Context, exploration, insights
- `research-summary-format` - Methodology, results, implications
- `dev-journal-format` - Chronological with learnings

## Hooks

- `frontmatter-validator` - Check required YAML fields
- `link-checker` - Validate internal/external links
- `code-block-linter` - Ensure code blocks have language tags

## Roadmap

See `.plans/plugins/blog-workflow/roadmap.md` for the full development plan.
