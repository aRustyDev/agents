---
name: blog/content/review
description: Evaluate content brainstorm or phase file
arguments:
  - name: path
    description: Path to the artifact to review (file or directory)
    required: true
  - name: approve
    description: Auto-approve if no fails (skip prompt)
    required: false
  - name: no-approve
    description: Keep in-review status even if passing
    required: false
---

# Content Review Command

Evaluate a content brainstorm or phase file against its review checklist. Auto-detects artifact type from frontmatter. Supports batch review of entire phase directory.

## Tools

- `Read` - Load artifact(s) and checklist
- `Edit` - Append review section
- `Glob` - Find phase files if directory provided

## Behavior

1. **Detect input type**:
   - If path ends with `/` or is directory → batch review all phase files
   - If file → single artifact review

2. **For each artifact**:
   a. Load artifact at `{{path}}`
   b. Detect artifact type from frontmatter (`content-brainstorm` or `phase`)
   c. Load appropriate checklist:
   - `content-brainstorm` → `.templates/review-checklists/content-brainstorm.md`
   - `phase` → `.templates/review-checklists/phase.md`
   d. Evaluate each criterion (pass/warn/fail)
   e. Remove existing `## Review` section if present
   f. Append new `## Review` section to artifact

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

   1. {{specific action to address issue}}
   2. {{specific action to address issue}}
   ```

4. **Determine approval**:

   | Condition | `--approve` flag | `--no-approve` flag | Default |
   |-----------|------------------|---------------------|---------|
   | All pass | approved | in-review | Prompt user |
   | Warns only | approved | in-review | Prompt user |
   | Any fail | in-review | in-review | in-review |

5. **Update status** in frontmatter

6. **Update `index.md`** with status change

## Batch Review Output

When reviewing a phase directory:

```text
## Content Planning Review: {{project-slug}}

Reviewed {{count}} phase files:

| Phase | Result | Pass | Warn | Fail |
|-------|--------|------|------|------|
| 0-tutorial-basic-migration | pass | 12 | 0 | 0 |
| 1-deep-dive-state-management | warn | 10 | 2 | 0 |
| 2-experiment-canary-releases | pass | 12 | 0 | 0 |

Overall: {{pass}} pass, {{warn}} warn, {{fail}} fail

Warnings in phase/1-deep-dive-state-management.md:
- Estimated effort may be low for scope
- Missing prerequisite link to phase 0

Next: Run `/blog/content/refine` on phases with warnings
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Artifact not found | "Artifact not found at {{path}}" | Verify path |
| Unknown artifact type | "Cannot determine artifact type from frontmatter" | Check frontmatter has valid `type` |
| Checklist not found | "Review checklist not found for type '{{type}}'" | Verify checklist exists |
| Empty directory | "No phase files found in {{path}}" | Run /blog/content/plan first |

## Example Usage

```text
# Review content brainstorm
/blog/content/review content/_projects/kubernetes-migration/content-brainstorm.md

# Review single phase
/blog/content/review content/_projects/kubernetes-migration/phase/0-tutorial-basics.md

# Batch review all phases
/blog/content/review content/_projects/kubernetes-migration/phase/

# Auto-approve if passing
/blog/content/review content/_projects/kubernetes-migration/content-brainstorm.md --approve

# Keep in-review even if passing
/blog/content/review content/_projects/kubernetes-migration/content-brainstorm.md --no-approve
```
