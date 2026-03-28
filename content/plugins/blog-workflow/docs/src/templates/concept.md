# Templates Concept

Templates provide consistent starting structures for different content types. Rather than starting from a blank page, templates give you a framework that guides your writing.

## Template Types

### Outline Templates

Structure templates for different post types. Each outline includes:

- Suggested sections
- Prompts for what to include
- Optional/required section markers

**Location**: `content/_templates/outlines/`

### Research Plan Templates

Structured approach to research:

- Questions to answer
- Sources to consult
- Verification criteria

**Location**: `content/_templates/research-plans/`

### Review Checklists

Quality gates for each workflow phase:

- Idea review checklist
- Research review checklist
- Content review checklist
- Post review checklist
- SEO review checklist

**Location**: `content/_templates/review-checklists/`

### Persona Templates

Writing voice and style definitions:

- Tone guidelines
- Vocabulary preferences
- Example phrases

**Location**: `content/_templates/personas/`

## Using Templates

Templates are applied during the draft phase of each workflow step:

```bash
/blog/post/draft --template deep-dive
```

The workflow copies the template and fills in your content.

## Customizing Templates

1. Copy a built-in template to your project's `content/_templates/`
2. Modify as needed
3. The workflow will prefer project-local templates over plugin defaults

## See Also

- [Outlines Reference](./outlines.md)
- [Research Plans Reference](./research-plans.md)
- [Review Checklists Reference](./review-checklists.md)
