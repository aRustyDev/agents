---
name: blog/content/refine
description: Update content artifact based on review feedback
arguments:
  - name: path
    description: Path to the artifact to refine
    required: true
  - name: feedback
    description: Direct feedback text (alternative to ## Review section)
    required: false
---

# Content Refine Command

Update a content artifact (brainstorm or phase file) based on review feedback. Removes the `## Review` section after applying fixes and resets status to `draft` for re-review.

## Tools

- `Read` - Load artifact and review
- `Edit` - Apply changes

## Behavior

1. **Load artifact** at `{{path}}`

2. **Detect artifact type** from frontmatter

3. **Load feedback**:
   - If `--feedback` provided, use that
   - Otherwise, read `## Review` section from artifact
   - If neither, error: "No feedback found. Provide --feedback or run review first."

4. **Load corresponding checklist** for reference

5. **Apply improvements**:

   **For content-brainstorm**:
   - Add missing content opportunities
   - Adjust priorities based on feedback
   - Clarify audience definitions
   - Fix effort estimates
   - Resolve scope issues
   - Update template assignments

   **For phase**:
   - Clarify scope boundaries
   - Add missing prerequisites
   - Fix dependency issues
   - Update code example specifications
   - Link additional research
   - Fix template selection

6. **Remove `## Review` section** (will be regenerated on next review)

7. **Reset status** → `draft`

8. **Update `updated` timestamp**

9. **Self-review** (fail items only):
   - Verify each fail item has been addressed
   - Report any remaining issues

10. **Update `index.md`** with status change

## Output

```text
Refined: content/_projects/<slug>/phase/1-deep-dive-state-management.md

Changes applied:
- Updated effort estimate (6h -> 8h)
- Added prerequisite: "Complete phase 0 first"
- Added dependency link to phase 0

Status reset to: draft

Next: Run `/blog/content/review content/_projects/<slug>/phase/1-deep-dive-state-management.md`
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| No feedback found | "No feedback found. Provide --feedback or run review first" | Run review or provide feedback |
| Artifact not found | "Artifact not found at {{path}}" | Verify path |

## Example Usage

```text
# Refine based on review section
/blog/content/refine content/_projects/kubernetes-migration/phase/1-deep-dive-state-management.md

# Refine with direct feedback
/blog/content/refine content/_projects/kubernetes-migration/content-brainstorm.md --feedback "Add more tutorial ideas for beginners"
```
