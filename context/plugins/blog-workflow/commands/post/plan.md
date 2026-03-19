---
name: blog:post:plan
description: Create structural outline from post spec
argument-hint: <path> [--template name]
arguments:
  - name: path
    description: Path to the post spec
    required: true
  - name: force
    description: Overwrite existing outline
    required: false
  - name: template
    description: Override outline template (slug)
    required: false
---

# Post Plan Command

Create a structural outline from a post specification. The outline defines sections, word estimates, code example locations, and transitions.

## Tools

- `Read` - Load spec and template
- `Write` - Create outline

## Behavior

1. **Validate input**:
   - Check spec exists at `{{path}}`
   - Check spec status (can be `draft` or `approved`)
   - Check outline doesn't exist (unless `--force`)

2. **Load outline template**:
   - If `--template` flag provided, use that
   - Otherwise, from `template` field in spec frontmatter
   - Or default based on `content_type` from phase
   - Path: `.templates/outlines/<template>.md`

3. **Template preview** (optional):
   - Show template structure: "Using template: tutorial.outline.md"
   - Display section count and typical word distribution

4. **Generate outline** following template structure:
   - Create sections with word estimates
   - Mark code example locations
   - Note diagram/visual placements
   - Plan transitions between sections

5. **Verify word estimates** sum to target length (+/-10%)

6. **Write outline**: `post/<phase-slug>/outline.md`

7. **Create bidirectional links**:
   - Set `parent` in outline to `./spec.md`
   - Add outline to `children` in spec

8. **Update Post Artifacts table** in `index.md`

9. **Self-review** (structure check):
   - Does structure follow template?
   - Are word estimates balanced?
   - Are all takeaways covered?

## Content Type to Template Mapping

| content_type | Default Template | Alternatives |
|--------------|------------------|--------------|
| `tutorial` | `tutorial.outline.md` | `getting-started.outline.md`, `how-i-built.outline.md` |
| `deep-dive` | `algorithm-deep-dive.outline.md` | `architecture-decision.outline.md`, `performance.outline.md` |
| `experiment` | `experiment.outline.md` | `debug-error.outline.md` |
| `explainer` | `first-look.outline.md` | `comparison.outline.md`, `library-evaluation.outline.md` |

## Output

```text
Created post outline: content/_projects/<slug>/post/<phase-slug>/outline.md

Template: {{template}}.outline.md
Sections: {{count}}
Total words: ~{{total}} (target: {{target}})

Section breakdown:
- Introduction: {{words}} words
- {{Section 1}}: {{words}} words
- {{Section 2}}: {{words}} words
- Conclusion: {{words}} words

Code examples: {{count}} locations marked
Diagrams: {{count}} locations marked

Self-review: {{passed|warnings}}

Next: Run `/blog/post/draft content/_projects/<slug>/post/<phase-slug>/outline.md`
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Spec doesn't exist | "Post spec not found at {{path}}" | Run /blog/post/spec first |
| Spec not approved | "Spec status is '{{status}}'. Review and approve first, or proceed anyway?" | Approve or confirm |
| Outline already exists | "Outline exists at {{path}}. Use --force to overwrite" | Use --force flag |
| Template not found | "Template '{{slug}}' not found in .templates/outlines/" | Verify template exists |
| Word estimate mismatch | "Outline total ({{N}}) differs from spec target ({{M}}) by >10%" | Adjust estimates |

## Example Usage

```text
# Normal outline creation
/blog/post/plan content/_projects/kubernetes-migration/post/tutorial-basics/spec.md

# Override template
/blog/post/plan content/_projects/kubernetes-migration/post/tutorial-basics/spec.md --template how-i-built

# Overwrite existing outline
/blog/post/plan content/_projects/kubernetes-migration/post/tutorial-basics/spec.md --force
```
