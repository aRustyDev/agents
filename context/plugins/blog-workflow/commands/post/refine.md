---
name: blog/post/refine
description: Update post artifact based on review feedback
arguments:
  - name: path
    description: Path to the artifact to refine
    required: true
  - name: feedback
    description: Direct feedback text (alternative to ## Review section)
    required: false
---

# Post Refine Command

Update a post artifact (spec, outline, or draft) based on review feedback. Removes the `## Review` section after applying fixes and resets status to `draft` for re-review.

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

4. **Load persona** (for voice consistency on drafts)

5. **Apply improvements**:

   **For post-spec**:
   - Clarify audience definition
   - Refine takeaways
   - Update prerequisites
   - Adjust scope
   - Fix template selection

   **For post-outline**:
   - Rebalance section lengths
   - Improve transitions
   - Add missing code/diagram markers
   - Fix structure issues
   - Adjust word estimates

   **For draft**:
   - Improve clarity
   - Fix technical issues
   - Adjust voice/tone to match persona
   - Complete missing sections
   - Balance word counts
   - Maintain persona voice throughout

6. **Remove `## Review` section**

7. **Reset status** -> `draft` (for spec/outline)

8. **Update `updated` timestamp**

9. **Self-review** (fail items only):
   - Verify each fail item has been addressed
   - Report any remaining issues

10. **Update `index.md`** with status change

## Output

```text
Refined: content/_drafts/kubernetes-migration-tutorial-basics.md

Changes applied:
- Added kernel version requirements to Prerequisites section
- Expanded edge case discussion in Step 3
- Adjusted Setup section (-50 words, was over estimate)
- Maintained practitioner voice throughout

Word count: {{new}} (was {{old}})
Status reset to: draft

Next: Run `/blog/post/review content/_drafts/kubernetes-migration-tutorial-basics.md`
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| No feedback found | "No feedback found. Provide --feedback or run review first" | Run review or provide feedback |
| Artifact not found | "Artifact not found at {{path}}" | Verify path |
| Persona missing | "Cannot verify voice without persona '{{slug}}'" | Create or update persona reference |

## Example Usage

```text
# Refine based on review section
/blog/post/refine content/_projects/kubernetes-migration/post/tutorial-basics/spec.md

# Refine draft
/blog/post/refine content/_drafts/kubernetes-migration-tutorial-basics.md

# Refine with direct feedback
/blog/post/refine content/_drafts/kubernetes-migration-tutorial-basics.md --feedback "Make the introduction more engaging"
```
