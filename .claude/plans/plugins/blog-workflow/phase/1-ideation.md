# Phase 1: Ideation Commands

## Objective

Create the entry point for all content — brainstorm, review, refine, and plan ideas.

## Deliverables

### 1. Command Files

Create under `context/plugins/blog-workflow/commands/idea/`:

| Command | Purpose |
|---------|---------|
| `brainstorm.md` | Take raw concept → `idea.md` + `index.md` |
| `review.md` | Evaluate idea or plan with checklist |
| `refine.md` | Update artifact based on review feedback |
| `draft-plan.md` | Approved idea → `plan.md` |

**Command frontmatter pattern**:

```yaml
---
name: blog:idea:brainstorm
description: Transform a raw concept into a structured idea artifact
arguments:
  - name: concept
    description: The topic or concept to brainstorm
    required: true
---
```

### 2. Artifact Templates

Create `context/plugins/blog-workflow/.templates/idea.md`:

```markdown
---
id: {{UUIDv4}}
type: idea
status: draft
created: {{ISO 8601}}
updated: {{ISO 8601}}
---

## Concept

{{core concept in 1-2 sentences}}

## Target Audience

{{who is this for? skill level, role, interests}}

## Problem/Need

{{what problem does this solve or need does it address?}}

## Unique Angle

{{what makes this different from existing content?}}

## Scope

{{what's included and explicitly excluded}}

## Research Needs

{{what needs to be researched? sources to consult?}}

## Estimated Effort

{{rough time estimate}}
```

Create `context/plugins/blog-workflow/.templates/plan.md`:

```markdown
---
id: {{UUIDv4}}
type: plan
status: draft
parent: ./idea.md
created: {{ISO 8601}}
updated: {{ISO 8601}}
---

## Overview

{{1-2 paragraph summary of the project}}

## Research Phase

- **Scope**: {{what to research}}
- **Sources**: {{where to look}}
- **Deliverable**: Research report

## Content Deliverables

| # | Type | Title | Est. Words |
|---|------|-------|------------|

## Timeline

| Phase | Duration | Notes |
|-------|----------|-------|

## Dependencies

{{external dependencies, prerequisites}}

## Risks

{{potential blockers, mitigation strategies}}

## Success Criteria

{{how to know this project is complete}}
```

### 3. Review Checklists

Create `context/plugins/blog-workflow/.templates/review-checklists/idea.md`:

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

Create `context/plugins/blog-workflow/.templates/review-checklists/plan.md`:

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

### 4. Skill Behaviors

#### brainstorm.md

**Input**: Raw concept (conversational text)

**Output**:

- `content/_projects/<slug>/idea.md` (artifact)
- `content/_projects/<slug>/index.md` (manifest)
- `content/_projects/<slug>/README.md` (human-readable overview)

**Slug generation**:

1. Lowercase the concept
2. Replace spaces and special characters with hyphens
3. Remove consecutive hyphens
4. Truncate to 50 characters
5. If `content/_projects/<slug>/` exists, append `-2`, `-3`, etc.

**Logic**:

1. Generate slug from concept (see rules above)
2. Check for collision, increment suffix if needed
3. Create project directory
4. Generate `idea.md` from `.templates/idea.md` with artifact frontmatter
5. Create `index.md` from `.templates/project-index.md` (status: `ideation`)
6. Create `README.md` from `.templates/project-readme.md`
7. Run self-review per `rules/blog-self-review.md` (fail items only)

> **Persona awareness**: At brainstorm start, check if a persona is configured in the project.
> If not, inform user that no persona is set and content will use default voice.
> Persona *creation* commands are in Phase 2, but *awareness check* happens here.

#### review.md

**Input**: Artifact path (auto-detects idea vs plan)

**Output**: Checklist evaluation with pass/warn/fail + `## Review` section appended to artifact

**Logic**:

1. Load artifact
2. Detect type from frontmatter (`type: idea` or `type: plan`)
3. Load appropriate checklist from `.templates/review-checklists/`
4. Evaluate each criterion
5. **Append `## Review` section** to the artifact file (replacing any previous review section)
6. Update artifact status → `in-review`
7. Update `index.md`

> **Review storage**: Review results are appended directly to the reviewed artifact in a `## Review` section at the end of the file. This keeps the review collocated with the content it evaluates. The `refine` command reads this section to know what to fix.

**Approval workflow**:

- If all checklist items pass: prompt user "Approve this artifact? [y/n]"
- If user approves: set status → `approved`, update `index.md`
- If user declines or any items fail: keep status at `in-review`

**Flags**:

- `--approve`: Skip confirmation prompt, auto-approve if all items pass
- `--no-approve`: Evaluate only, never set `approved` status

#### refine.md

**Input**: Artifact path (reads `## Review` section from artifact, or accepts feedback as direct input)

**Output**: Updated artifact with `## Review` section removed

**Logic**:

1. Load artifact
2. Read the `## Review` section from the artifact (or accept feedback as direct input)
3. Apply improvements based on feedback
4. **Remove the `## Review` section** (it will be regenerated on next review)
5. Run self-review per `rules/blog-self-review.md` (fail items only)
6. Set status → `draft` (requires re-review before approval)
7. Update `index.md`

> **Workflow note**: After refinement, the artifact returns to `draft` status and the `## Review` section is removed.
> User should run `review.md` again to evaluate changes and potentially approve.

#### draft-plan.md

**Input**: Approved `idea.md` path

**Output**: `content/_projects/<slug>/plan.md`

**Logic**:

1. Verify idea status is `approved` (error if not)
2. Generate project plan from `.templates/plan.md`
3. Create `plan.md` with artifact frontmatter
4. Set `parent: ./idea.md` in plan frontmatter
5. Add `children: [./plan.md]` to idea frontmatter (bidirectional link)
6. Update `index.md` Artifacts table
7. Run self-review per `rules/blog-self-review.md`

**Error handling**:

- If idea is not approved: "Error: idea.md must be approved before creating a plan. Run `blog:idea:review` first."

### 5. Example Output

After running `blog:idea:brainstorm "Building eBPF tracing tools"`:

**`content/_projects/building-ebpf-tracing-tools/idea.md`**:

```markdown
---
id: "550e8400-e29b-41d4-a716-446655440000"
type: idea
status: draft
created: 2026-03-14T12:00:00Z
updated: 2026-03-14T12:00:00Z
---

## Concept

A practical guide to building custom tracing tools using eBPF, covering the fundamentals and real-world applications.

## Target Audience

Mid-to-senior Linux developers and SREs who want to understand eBPF beyond surface-level tutorials. Should have basic C knowledge and Linux systems experience.

## Problem/Need

Most eBPF tutorials stop at "hello world" examples. Engineers need guidance on building production-quality tracing tools.

## Unique Angle

Hands-on, practitioner perspective with real debugging scenarios from production systems.

## Scope

**Included**: eBPF basics, BPF CO-RE, libbpf, tracepoints, kprobes, practical examples
**Excluded**: XDP networking, security use cases, kernel internals deep-dive

## Research Needs

- Current state of libbpf and BPF CO-RE tooling
- Common pitfalls and gotchas
- Performance considerations

## Estimated Effort

2-3 weeks for research + writing
```

## Tasks

### Commands

- [ ] Create `context/plugins/blog-workflow/commands/idea/` directory
- [ ] Write `commands/idea/brainstorm.md` with proper command frontmatter
- [ ] Write `commands/idea/review.md` with approval workflow
- [ ] Write `commands/idea/refine.md` with self-review integration
- [ ] Write `commands/idea/draft-plan.md` with bidirectional linking

### Templates

- [ ] Create `.templates/idea.md` artifact template
- [ ] Create `.templates/plan.md` artifact template
- [ ] Create `.templates/review-checklists/idea.md`
- [ ] Create `.templates/review-checklists/plan.md`

### Testing

- [ ] Test brainstorm → review → approve flow
- [ ] Test brainstorm → review → refine → review loop
- [ ] Test draft-plan with approved idea
- [ ] Test draft-plan error on unapproved idea
- [ ] Test slug collision handling (create same concept twice)
- [ ] Test persona awareness message when no persona configured

## Acceptance Tests

### Artifact Creation

- [ ] `blog:idea:brainstorm "test topic"` creates `idea.md`, `index.md`, and `README.md`
- [ ] `idea.md` follows `.templates/idea.md` structure
- [ ] `idea.md` has valid frontmatter (id, type: idea, status: draft, created, updated)
- [ ] `index.md` has valid project frontmatter (type: project, status: ideation)
- [ ] `index.md` Artifacts table lists the idea artifact
- [ ] `README.md` created from `.templates/project-readme.md`

### Slug Generation

- [ ] Concept "My Great Idea!" generates slug `my-great-idea`
- [ ] Existing project causes suffix increment (`my-great-idea-2`)
- [ ] Long concepts are truncated to 50 characters

### Review Workflow

- [ ] `blog:idea:review <path>/idea.md` produces checklist evaluation
- [ ] After review, `idea.md` status is `in-review`
- [ ] If all items pass, user is prompted to approve
- [ ] Approval sets status → `approved`
- [ ] `--approve` flag auto-approves without prompt
- [ ] `--no-approve` flag evaluates only, never approves

### Refine Workflow

- [ ] `blog:idea:refine <path>/idea.md` updates artifact based on feedback
- [ ] After refine, status returns to `draft`
- [ ] Self-review runs automatically (per `rules/blog-self-review.md`)

### Plan Creation

- [ ] `blog:idea:draft-plan <path>/idea.md` creates `plan.md` when idea is approved
- [ ] `plan.md` follows `.templates/plan.md` structure
- [ ] `plan.md` has `parent: ./idea.md` in frontmatter
- [ ] `idea.md` has `children: [./plan.md]` added (bidirectional)
- [ ] Error if idea is not approved

### Review Plan

- [ ] `blog:idea:review <path>/plan.md` auto-detects plan type
- [ ] Uses `.templates/review-checklists/plan.md` checklist
- [ ] Approval workflow works same as idea review

### Persona Awareness

- [ ] When no persona configured, brainstorm shows info message
- [ ] Message indicates default voice will be used

## Dependencies

- Phase 0 (Foundation) must be complete
- Plugin directory structure exists at `context/plugins/blog-workflow/`
- Base templates exist in `.templates/` (project-index.md, project-readme.md)
- Rules exist in `rules/` (blog-self-review.md)

## Estimated Effort

4-5 hours

- Skills (4 files): 2 hours
- Artifact templates (2 files): 30 min
- Review checklists (2 files): 30 min
- Testing all workflows: 1.5 hours
