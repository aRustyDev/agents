---
name: blog/post/review
description: Evaluate post artifact (spec, outline, or draft)
arguments:
  - name: path
    description: Path to the artifact or post/ directory for batch review
    required: true
  - name: approve
    description: Auto-approve if no fails (skip prompt)
    required: false
  - name: no-approve
    description: Keep in-review status even if passing
    required: false
---

# Post Review Command

Evaluate a post artifact (spec, outline, or draft) against its review checklist. Auto-detects artifact type from frontmatter. Supports batch review of entire post directory.

## Tools

- `Read` - Load artifact(s), persona, checklist
- `Edit` - Append review section
- `Glob` - Find artifacts if directory provided

## Behavior

1. **Detect input type**:
   - If path is `post/` directory -> batch review all specs and outlines
   - If path ends with `.md` -> single artifact review
   - If path is `content/_drafts/` directory -> batch review all drafts

2. **For each artifact**:

   a. Load artifact at `{{path}}`

   b. Detect artifact type:
   - `type: post-spec` in frontmatter -> post-spec
   - `type: post-outline` in frontmatter -> post-outline
   - `draft: true` in frontmatter (AstroPaper) -> draft

   c. Load appropriate checklist:
   - `post-spec` -> `.templates/review-checklists/post-spec.md`
   - `post-outline` -> `.templates/review-checklists/post-outline.md`
   - `draft` -> `.templates/review-checklists/post-draft.md`

   d. Load persona (for voice consistency check on drafts)

   e. Evaluate each criterion (pass/warn/fail)

   f. For drafts: Check voice against persona, verify word counts

   g. Remove existing `## Review` section if present

   h. Append new `## Review` section

3. **Review section format**:

   ```markdown
   ## Review

   **Reviewed**: {{ISO 8601 timestamp}}
   **Result**: {{pass|warn|fail}}

   ### {{Category Name}}

   - [x] Criterion - pass
   - [~] Criterion - warn: {{reason}}
   - [ ] Criterion - fail: {{reason}}

   ...

   **Summary**: {{pass_count}} pass, {{warn_count}} warn, {{fail_count}} fail

   ### Action Items

   1. {{specific action}}
   2. {{specific action}}
   ```

4. **Determine approval**:

   | Condition | `--approve` flag | `--no-approve` flag | Default |
   |-----------|------------------|---------------------|---------|
   | All pass | approved | in-review | Prompt user |
   | Warns only | approved | in-review | Prompt user |
   | Any fail | in-review | in-review | in-review |

5. **Update status** in frontmatter (for spec/outline) or note in draft

6. **Update `index.md`** with status change

## Batch Review Output

```text
## Post Artifacts Review: {{project-slug}}

Reviewed {{count}} artifacts:

| Artifact | Type | Result | Pass | Warn | Fail |
|----------|------|--------|------|------|------|
| post/tutorial-basics/spec.md | post-spec | pass | 12 | 0 | 0 |
| post/tutorial-basics/outline.md | post-outline | pass | 11 | 0 | 0 |
| post/deep-dive-state/spec.md | post-spec | warn | 10 | 2 | 0 |
| _drafts/kubernetes-migration-tutorial-basics.md | draft | pass | 15 | 0 | 0 |

Overall: {{pass}} pass, {{warn}} warn, {{fail}} fail

Warnings in post/deep-dive-state/spec.md:
- Word count estimate may be too high for scope
- Missing one prerequisite link

Next: Run `/blog/post/refine` on artifacts with warnings
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Artifact not found | "Artifact not found at {{path}}" | Verify path |
| Unknown artifact type | "Cannot determine artifact type. Expected post-spec, post-outline, or draft" | Check frontmatter |
| Checklist not found | "Review checklist not found for type '{{type}}'" | Verify checklist exists |
| Empty directory | "No post artifacts found in {{path}}" | Run /blog/post/spec first |
| Persona missing for draft | "Draft references persona '{{slug}}' but it wasn't found" | Verify persona |

## Example Usage

```text
# Review spec
/blog/post/review content/_projects/kubernetes-migration/post/tutorial-basics/spec.md

# Review outline
/blog/post/review content/_projects/kubernetes-migration/post/tutorial-basics/outline.md

# Review draft
/blog/post/review content/_drafts/kubernetes-migration-tutorial-basics.md

# Batch review all post artifacts
/blog/post/review content/_projects/kubernetes-migration/post/

# Auto-approve if passing
/blog/post/review content/_projects/kubernetes-migration/post/tutorial-basics/spec.md --approve
```
