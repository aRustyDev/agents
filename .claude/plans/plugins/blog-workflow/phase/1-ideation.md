# Phase 1: Ideation Commands

## Objective

Create the entry point for all content — brainstorm, review, refine, and plan ideas.

## Deliverables

### 1. Command Files

Create under `.claude/commands/blog/idea/`:

| Command | Purpose |
|---------|---------|
| `brainstorm.md` | Take raw concept → `idea.md` + `index.md` |
| `review.md` | Evaluate idea or plan with checklist |
| `refine.md` | Update artifact based on review feedback |
| `draft-plan.md` | Approved idea → `plan.md` |

### 2. Review Checklists

Create `content/_templates/review-checklists/idea.md`:

```markdown
---
type: review-checklist
name: Idea Review
applies_to: idea
---

## Scope Clarity

- [ ] Target audience defined
- [ ] Core message identifiable
- [ ] Scope is achievable (not too broad)

## Differentiation

- [ ] Unique angle or perspective
- [ ] Not rehashing existing content

## Research Needs

- [ ] Research requirements clear
- [ ] Sources/experts identified

## Feasibility

- [ ] Expertise available to write this
- [ ] Time estimate reasonable
```

Create `content/_templates/review-checklists/plan.md`:

```markdown
---
type: review-checklist
name: Project Plan Review
applies_to: plan
---

## Structure

- [ ] Research section defined
- [ ] Content deliverables identified
- [ ] Timeline/milestones outlined

## Scope

- [ ] Achievable within stated timeframe
- [ ] Dependencies identified
- [ ] Risks acknowledged

## Alignment

- [ ] Aligns with original idea
- [ ] Addresses target audience needs
- [ ] Clear success criteria

## Completeness

- [ ] All sections filled
- [ ] No placeholder content remaining
- [ ] Links to idea artifact present
```

### 3. Command Behaviors

#### brainstorm.md

**Input**: Raw concept (conversational text)

**Output**:

- `content/_projects/<slug>/idea.md` (artifact)
- `content/_projects/<slug>/index.md` (manifest)

**Logic**:

1. Generate slug from concept
2. Create project directory
3. Generate `idea.md` with artifact frontmatter
4. Create `index.md` with project frontmatter (status: `ideation`)
5. Create `README.md` from `project-readme.md` template
6. Run self-review (fail items only)

> **Note**: Persona verification is added in Phase 2. Until then, brainstorm works without persona.

#### review.md

**Input**: Artifact path (auto-detects idea vs plan)

**Output**: Checklist evaluation with pass/warn/fail

**Logic**:

1. Load artifact
2. Detect type (idea or plan)
3. Load appropriate checklist
4. Evaluate each criterion
5. Update artifact status → `in-review`
6. Update `index.md`

#### refine.md

**Input**: Artifact path + review feedback

**Output**: Updated artifact

**Logic**:

1. Load artifact and feedback
2. Apply improvements
3. Run self-review checklist
4. Set status → `draft`
5. Update `index.md`

#### draft-plan.md

**Input**: Approved `idea.md` path

**Output**: `content/_projects/<slug>/plan.md`

**Logic**:

1. Verify idea is approved
2. Generate project plan structure
3. Create `plan.md` with artifact frontmatter
4. Link plan to idea (parent/children)
5. Update `index.md`
6. Run self-review

## Tasks

- [ ] Create `.claude/commands/blog/idea/` directory
- [ ] Write `brainstorm.md` command
- [ ] Write `review.md` command (auto-detects idea vs plan)
- [ ] Write `refine.md` command
- [ ] Write `draft-plan.md` command
- [ ] Create `content/_templates/review-checklists/idea.md`
- [ ] Create `content/_templates/review-checklists/plan.md`
- [ ] Test brainstorm → review → refine loop
- [ ] Test plan review flow

## Acceptance Tests

- [ ] `/blog/idea/brainstorm "test topic"` creates `idea.md`, `index.md`, and `README.md`
- [ ] `README.md` created from `project-readme.md` template
- [ ] `idea.md` has valid frontmatter (id, type, status, created, updated)
- [ ] `index.md` has valid project frontmatter (type: project, status: ideation)
- [ ] `index.md` lists the idea artifact
- [ ] `/blog/idea/review <path>/idea.md` produces checklist evaluation
- [ ] After review, `idea.md` status is `in-review`
- [ ] `/blog/idea/refine <path>/idea.md` updates artifact, status → `draft`
- [ ] `/blog/idea/draft-plan <path>/idea.md` creates `plan.md`
- [ ] `/blog/idea/review <path>/plan.md` auto-detects and reviews plan
- [ ] Multiple brainstorm → review → refine iterations work correctly

## Dependencies

- Phase 0 (Foundation) must be complete

## Estimated Effort

3-4 hours
