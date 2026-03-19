---
name: blog:idea:draft-plan
description: Create a project plan from an approved idea
argument-hint: <path>
arguments:
  - name: path
    description: Path to the approved idea.md
    required: true
---

# Draft Plan

Create a project plan from an approved idea, establishing the research scope, content deliverables, and timeline.

## Behavior

1. **Load idea** from provided path

2. **Verify approval**:
   - Check `status` field in frontmatter
   - If not `approved`: Error and exit
   - Error message: "Error: idea.md must be approved before creating a plan. Run `blog:idea:review <path>` first."

3. **Generate plan** from `.templates/plan.md`:
   - `id`: Generate new UUIDv4
   - `type`: "plan"
   - `status`: "draft"
   - `parent`: Relative path to idea (e.g., `./idea.md`)
   - `created`/`updated`: Current ISO 8601 timestamp
   - Fill sections based on idea content:
     - Overview from idea's Concept
     - Research Phase from idea's Research Needs
     - Content Deliverables (initial estimate)
     - Timeline (based on Estimated Effort)
     - Dependencies and Risks

4. **Create bidirectional link**:
   - Add `children: [./plan.md]` to idea.md frontmatter
   - Plan already has `parent: ./idea.md`

5. **Update `index.md`**:
   - Add plan to Artifacts table
   - Keep project status as `ideation` (changes to `research` when research starts)

6. **Run self-review** per `rules/blog-self-review.md`:
   - Check against `.templates/review-checklists/plan.md`
   - Only report **fail** items

## Output Format

```text
## Plan Created

Path: content/_projects/<slug>/plan.md
Status: draft

### Links
- Parent: ./idea.md (bidirectional link added)

### Self-Review
[pass | X issues found]

Next steps:
1. Review the plan: blog:idea:review <path>/plan.md
2. Refine if needed: blog:idea:refine <path>/plan.md "feedback"
3. Start research when approved: blog:research:spec:draft <path>/plan.md
```

## Error Handling

**Idea not approved**:

```text
Error: idea.md must be approved before creating a plan.

Current status: draft
Required status: approved

Run `blog:idea:review content/_projects/<slug>/idea.md` to review and approve.
```

**Plan already exists**:

```text
Warning: plan.md already exists at content/_projects/<slug>/plan.md

Options:
1. Review existing plan: blog:idea:review <path>/plan.md
2. Delete and recreate (manual action required)
```

## Example

**Input**: `blog:idea:draft-plan content/_projects/ebpf-tracing/idea.md`

**Output**:

```text
## Plan Created

Path: content/_projects/ebpf-tracing/plan.md
Status: draft

### Links
- Parent: ./idea.md (bidirectional link added)

### Self-Review
- [x] Research section defined — pass
- [x] Content deliverables identified — pass
- [~] Timeline/milestones outlined — warn: consider adding specific dates
- [x] Achievable within stated timeframe — pass
- [x] Dependencies identified — pass
- [x] Risks acknowledged — pass
- [x] Aligns with original idea — pass
- [x] Clear success criteria — pass

Self-review: passed (1 warn item for manual review)

Next steps:
1. Review the plan: blog:idea:review content/_projects/ebpf-tracing/plan.md
2. Refine if needed: blog:idea:refine content/_projects/ebpf-tracing/plan.md "feedback"
3. Start research when approved: blog:research:spec:draft content/_projects/ebpf-tracing/plan.md
```
