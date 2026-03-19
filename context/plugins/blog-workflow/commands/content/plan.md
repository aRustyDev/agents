---
name: blog:content:plan
description: Decompose content brainstorm into numbered phase files
argument-hint: <path> [--dry-run]
arguments:
  - name: path
    description: Path to the content brainstorm
    required: true
  - name: dry-run
    description: Preview decomposition without creating files
    required: false
  - name: force
    description: Overwrite existing phase files
    required: false
---

# Content Plan Command

Decompose a content brainstorm into numbered phase files. Each phase represents a single post or content piece with its own specification.

## Tools

- `Read` - Load content brainstorm
- `Write` - Create phase files
- `Bash` - Create directories

## Behavior

1. **Validate input**:
   - Check content brainstorm exists at `{{path}}`
   - Check brainstorm status (can be `draft` or `approved`)
   - Check phase/ directory doesn't have files (unless `--force`)

2. **Dry-run mode** (if `--dry-run`):
   - Show planned phase files without creating
   - Show child project candidates
   - Exit without changes

3. **Create `phase/` directory** if needed

4. **For each content piece** in recommended sequence:
   - Generate slug from title (lowercase, hyphenated, max 50 chars)
   - Create phase file: `phase/{{N}}-{{slug}}.md`
   - Set `phase_number` in frontmatter
   - Set `parent` to relative path to content-brainstorm.md
   - Set `template` from brainstorm or default mapping
   - Populate from brainstorm data

5. **Identify child projects** (prompt user for each):
   - If phase scope is too large (multiple posts needed)
   - If phase topic diverges significantly from parent
   - Prompt: "Phase '{{title}}' may need its own project. Create child? (yes/no)"
   - If yes: create child project at `content/_projects/<child-slug>/`
   - Link via `children` in phase frontmatter
   - Link via `parent` in child `index.md`

6. **Update content brainstorm**:
   - Add all phase paths to `children` array

7. **Update parent project `index.md`**:
   - Add to Phases table
   - Add to Related Projects table (if children created)

8. **Self-review** (dependency check):
   - Are dependencies between phases explicit?
   - Is ordering logical for readers?
   - Do early phases avoid assuming later knowledge?
   - Any circular dependencies?

## Content Type to Template Mapping

| content_type | Default Template | Alternative Templates |
|--------------|------------------|----------------------|
| `tutorial` | `getting-started.outline.md` | `tutorial.outline.md`, `how-i-built.outline.md` |
| `deep-dive` | `algorithm-deep-dive.outline.md` | `architecture-decision.outline.md`, `performance.outline.md` |
| `experiment` | `experiment.outline.md` | `debug-error.outline.md` |
| `explainer` | `first-look.outline.md` | `comparison.outline.md`, `library-evaluation.outline.md` |

## Child Project Criteria

| Criterion | Suggests Child Project |
|-----------|------------------------|
| Estimated effort > 8 hours | Yes |
| Multiple posts needed | Yes |
| Different target audience | Yes |
| Standalone value | Yes |
| Tightly coupled to parent | No - keep as phase |

## Output

```text
Decomposed into phases: content/_projects/<slug>/phase/

Phases created:
- phase/0-tutorial-basic-migration.md (tutorial, getting-started, ~4h)
- phase/1-deep-dive-state-management.md (deep-dive, algorithm-deep-dive, ~6h)
- phase/2-experiment-canary-releases.md (experiment, experiment, ~3h)

Child projects created:
- content/_projects/tutorial-ebpf/ (from phase/0, spawned due to scope)

Updated index.md:
- Added {{count}} phases to Phases table
- Added {{count}} child to Related Projects table

Self-review: {{passed|warnings}}

Next: Run `/blog/content/review content/_projects/<slug>/phase/` to validate all
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Brainstorm doesn't exist | "Content brainstorm not found at {{path}}" | Run /blog/content/draft first |
| Phase files exist | "Phase files already exist in phase/. Use --force to regenerate" | Use --force or refine existing |
| Circular dependency | "Circular dependency detected: {{phase A}} <-> {{phase B}}" | Review dependency structure |
| Invalid content type | "Unknown content_type '{{type}}'. Use: tutorial, deep-dive, experiment, explainer" | Fix content type in brainstorm |
| No content items | "Brainstorm has no content opportunities to decompose" | Add content ideas to brainstorm |

## Re-planning Flow

If `--force` is used with existing phases:

1. Archive existing phases to `phase/.archive/` with timestamp
2. Generate new phases
3. Report what was archived

## Example Usage

```text
# Normal decomposition
/blog/content/plan content/_projects/kubernetes-migration/content-brainstorm.md

# Preview without creating
/blog/content/plan content/_projects/kubernetes-migration/content-brainstorm.md --dry-run

# Regenerate phases
/blog/content/plan content/_projects/kubernetes-migration/content-brainstorm.md --force
```
