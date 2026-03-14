---
name: blog:idea:refine
description: Update an idea or plan artifact based on review feedback
arguments:
  - name: path
    description: Path to the artifact to refine
    required: true
  - name: feedback
    description: Review feedback or specific improvements to make
    required: true
---

# Idea/Plan Refine

Update an idea or plan artifact based on review feedback, then run self-review.

## Behavior

1. **Load artifact** from provided path

2. **Load feedback** from argument or conversation context

3. **Apply improvements**:
   - Address each piece of feedback
   - Update relevant sections of the artifact
   - Maintain consistent voice and structure
   - Update `updated` timestamp in frontmatter

4. **Run self-review** per `rules/blog-self-review.md`:
   - Check against appropriate checklist (`.templates/review-checklists/idea.md` or `plan.md`)
   - Only check **fail** items (warn items left for explicit review)
   - Report any issues found

5. **Set status → `draft`**:
   - Artifact returns to draft state after refinement
   - Requires re-review before approval

6. **Update `index.md`** with status change

## Output Format

```text
## Refinement Applied

### Changes Made
1. <change description>
2. <change description>

### Self-Review
- [x] <criterion> — pass
- [ ] <criterion> — fail: <reason>

Status: <previous> → draft

Next: Run `blog:idea:review <path>` to evaluate changes
```

## Workflow Note

After refinement, the artifact returns to `draft` status. This ensures all changes go through the review process before approval. The typical flow is:

```text
refine → draft → review → [approve | refine again]
```

## Example

**Input**: `blog:idea:refine content/_projects/ebpf-tracing/idea.md "Narrow scope to exclude XDP, add specific tool examples"`

**Output**:

```text
## Refinement Applied

### Changes Made
1. Updated Scope section to explicitly exclude XDP networking use cases
2. Added specific tool examples: bpftrace, libbpf, BCC
3. Clarified target audience skill level

### Self-Review
- [x] Target audience defined — pass
- [x] Core message identifiable — pass
- [x] Scope is achievable — pass
- [x] Unique angle or perspective — pass
- [x] Research requirements clear — pass
- [x] Expertise available — pass
- [x] Time estimate reasonable — pass

Status: in-review → draft

Next: Run `blog:idea:review content/_projects/ebpf-tracing/idea.md` to evaluate changes
```
