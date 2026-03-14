# Phase 4: Content Planning Commands

## Objective

Decompose research into planned work items (phases). This is where idea decomposition happens.

## Deliverables

### 1. Content Planning Commands

Create under `.claude/commands/blog/content/`:

| Command | Purpose |
|---------|---------|
| `draft.md` | Research report → content brainstorm |
| `plan.md` | Brainstorm → numbered `phase/` files |
| `refine.md` | Update content plan or phase files |
| `review.md` | Validate decomposition |

### 2. Review Checklists

Create `content/_templates/review-checklists/content-plan.md`:

```markdown
---
type: review-checklist
name: Content Plan Review
applies_to: content-plan
---

## Completeness

- [ ] All research insights addressed
- [ ] No significant gaps in coverage
- [ ] Prerequisites identified for each piece

## Scope

- [ ] Each phase has clear boundaries
- [ ] No overlapping content between phases
- [ ] Phase sizes are manageable (not too large)

## Ordering

- [ ] Dependencies between phases identified
- [ ] Logical progression for readers
- [ ] Early phases don't assume later knowledge

## Feasibility

- [ ] Each phase can stand alone as a post
- [ ] Child projects identified where needed
- [ ] Estimated effort reasonable for each
```

Create `content/_templates/review-checklists/phase.md`:

```markdown
---
type: review-checklist
name: Phase File Review
applies_to: phase
---

## Scope

- [ ] Phase boundaries clearly defined
- [ ] Single coherent topic/theme
- [ ] Not too broad (achievable in one post)

## Prerequisites

- [ ] Required knowledge listed
- [ ] Dependencies on other phases noted
- [ ] No circular dependencies

## Feasibility

- [ ] Estimated effort realistic
- [ ] Code examples specified are doable
- [ ] Research backing is sufficient

## Structure

- [ ] Key points identified
- [ ] Code example needs clear
- [ ] Related research linked
```

## Command Behaviors

### draft.md

**Input**: Research report path

**Output**: `content/_projects/<slug>/content-plan.md` (`type: content-plan`)

**Logic**:

1. Load research report
2. Identify potential content pieces:
   - Tutorials
   - Deep-dives
   - Experiments
   - Explainers
3. Note dependencies and prerequisites
4. Create content-plan artifact
5. Update project status → `content-planning` in `index.md`
6. Add content-plan to Artifacts table

### plan.md

**Input**: Content brainstorm path

**Output**: Numbered `phase/` files

**Logic**:

1. Load content brainstorm
2. Decompose into phases:
   - `phase/0-<slug>.md`
   - `phase/1-<slug>.md`
   - etc.
3. For phases requiring own project:
   - Create child project at `content/_projects/<child-slug>/`
   - Link via `children` in phase frontmatter
   - Link via `parent` in child `index.md`
4. Update parent project `index.md`:
   - Add to Phases table
   - Add to Related Projects table (if children)

### review.md

**Input**: Content plan + phase files

**Output**: Decomposition validation

**Logic**:

1. Load all phase files
2. Check for gaps (topics in research not covered)
3. Check for overlaps (duplicate coverage)
4. Verify ordering (dependencies satisfied)
5. Validate scope (each phase achievable)
6. Update artifact status → `in-review`
7. Update `index.md` with status change

### refine.md

**Input**: Content plan or phase file + feedback

**Output**: Updated artifact(s)

**Logic**:

1. Apply feedback
2. Rebalance phases if needed
3. Update cross-references
4. Run self-review
5. Update `index.md` with status change

## Phase File Structure

```yaml
---
id: <UUIDv4>
type: phase
status: draft | in-review | approved | complete
parent: ../plan.md
children:
  - content/_projects/<child-slug>/index.md  # if spawns sub-project
phase_number: 0
title: "eBPF Tutorial"
content_type: tutorial | deep-dive | experiment | explainer
template: tutorial  # references outline template
persona: practitioner
estimated_effort: "4-6 hours"
prerequisites:
  - Basic Linux knowledge
  - Familiarity with syscalls
created: <ISO 8601>
updated: <ISO 8601>
---

## Summary

What this phase will cover...

## Key Points

1. Point one
2. Point two
3. Point three

## Code Examples Needed

- Example 1: ...
- Example 2: ...

## Related Research

- From report section X: ...
```

## Project Structure After Content Planning

```text
content/_projects/<slug>/
├── index.md
├── idea.md
├── plan.md
├── research/
│   └── ...
└── phase/
    ├── 0-tutorial-ebpf.md
    ├── 1-deep-dive-openllmetry.md
    └── 2-experiment-tracing.md

content/_projects/tutorial-ebpf/     # Child project (if created)
├── index.md                         # parent: ../llm-observability/phase/0-tutorial-ebpf.md
└── ...
```

## Tasks

- [ ] Create `.claude/commands/blog/content/` directory
- [ ] Write `content/draft.md` command
- [ ] Write `content/plan.md` command
- [ ] Write `content/refine.md` command
- [ ] Write `content/review.md` command
- [ ] Create `content/_templates/review-checklists/content-plan.md`
- [ ] Create `content/_templates/review-checklists/phase.md`
- [ ] Test single-post decomposition (one phase)
- [ ] Test multi-post decomposition (multiple phases)
- [ ] Test child project creation flow

## Acceptance Tests

- [ ] `/blog/content/draft` reads report → produces `type: content-plan`
- [ ] `/blog/content/plan` decomposes into numbered `phase/` files
- [ ] Phase files have `type: phase` in frontmatter
- [ ] Child projects created flat at `content/_projects/<child-slug>/`
- [ ] Phase `children` links to child `index.md`
- [ ] Child `parent` links back to phase file
- [ ] `/blog/content/review` validates: no gaps, no overlaps, correct ordering
- [ ] `index.md` Phases table populated
- [ ] `index.md` Related Projects table populated for child projects
- [ ] `/blog/content/refine` updates phase files based on feedback
- [ ] Single-post idea produces exactly one phase file

## Entry Points

Per SPEC, content planning can be entered:

- **From research**: After research report is complete (normal flow)
- **Directly**: With `/blog/content/draft` if research is already done elsewhere

When entering directly:

1. Accept external research document path or inline summary
2. Create project structure if needed
3. Set project status to `content-planning`

## Dependencies

- Phase 0 (Foundation) — required
- Phase 3 (Research) — optional (can use existing research)

## Estimated Effort

3-4 hours
