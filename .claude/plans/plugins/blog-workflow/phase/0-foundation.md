# Phase 0: Foundation

## Objective

Establish storage layout, schemas, and rules — no workflow logic yet.

## Deliverables

### 1. Directory Structure

Create the following directories:

```text
content/
├── _projects/          # All content projects
├── _drafts/            # Post drafts (shared across projects)
└── _templates/         # Reusable assets
    ├── personas/       # Authorial voice definitions
    ├── outlines/       # Post structure templates
    ├── research-plans/ # Research methodology templates
    ├── review-checklists/ # Review criteria
    └── brainstorm-plans/  # Brainstorming templates
```

### 2. AstroPaper Schema Update

Add optional `id` field to `src/content.config.ts`:

```typescript
schema: ({ image }) =>
  z.object({
    id: z.string().uuid().optional(),
    // ... existing fields
  }),
```

### 3. Rules File

Create `.claude/rules/blog-frontmatter.md` documenting:

- Required fields (id, title, description, pubDatetime, tags)
- Optional fields with defaults
- Common mistakes to avoid
- AstroPaper-specific mappings

### 4. Index.md Template

Create `content/_templates/project-index.md` with manifest structure:

```yaml
---
type: project
title: "<project title>"
status: ideation | research | content-planning | post | publish | complete | paused
persona: <persona slug>
created: <ISO 8601>
updated: <ISO 8601>
---

## Artifacts

| Artifact | Status | Path |
|----------|--------|------|

## Phases

| # | Title | Type | Status | Link |
|---|-------|------|--------|------|

## Related Projects

| Project | Relationship | Path |
|---------|-------------|------|
```

### 5. Project README Template

Create `content/_templates/project-readme.md`:

```markdown
# {{title}}

> {{one-line description}}

## Status

**Phase**: {{status}}
**Persona**: {{persona}}

## Overview

{{2-3 sentence summary of the project}}

## Artifacts

- [Idea](./idea.md)
- [Plan](./plan.md)
- [Research Report](./research/reports/main.md)

## Posts

| Post | Status | Link |
|------|--------|------|

## Notes

{{any relevant notes}}
```

### 6. Brainstorm Plan Template

Create `content/_templates/brainstorm-plans/standard.md`:

```markdown
---
type: template
name: Standard Brainstorm Plan
applies_to: brainstorm
---

## Topic

{{topic or concept to brainstorm}}

## Constraints

- Time: {{timeframe}}
- Scope: {{boundaries}}
- Audience: {{target readers}}

## Exploration Areas

### What exists?

- Current solutions
- Related work
- Prior art

### What's missing?

- Gaps in coverage
- Unexplored angles
- Unmet needs

### What's unique?

- Your perspective
- Your experience
- Your insights

## Output Goals

- [ ] Clear problem statement
- [ ] Defined audience
- [ ] Unique angle identified
- [ ] Research needs outlined
```

### 7. Self-Review Standard

Document self-review behavior in `.claude/rules/blog-self-review.md`:

```markdown
# Self-Review Standard

Self-review is an automated quality check that runs after artifact creation or modification.

## How It Works

1. Self-review uses the **same checklist** as the dedicated review command
2. Only **fail** items are flagged (items that would block approval)
3. **Warn** items are left for dedicated review (human gating point)

## When It Runs

Self-review runs automatically at the end of:

- `brainstorm.md` — checks idea against `idea.md` checklist
- `draft-plan.md` — checks plan against `plan.md` checklist
- `refine.md` — checks artifact against its type checklist
- All `draft.md` commands — checks output against relevant checklist

## Outcome Handling

| Result | Behavior |
|--------|----------|
| All pass | Continue silently |
| Fail items | Report issues, set status to `draft` |
| Warn items | Ignored (left for `/review`) |

## Example

After `draft.md` creates an idea:

1. Load `idea.md` checklist
2. Check each criterion
3. If "Scope is achievable" fails → report and set status: `draft`
4. If "Unique angle" is warning-level → ignore (human will check in review)
```

### 8. Artifact Frontmatter Schema

Document in `content/_templates/schemas/artifact-schema.md`:

```yaml
---
id: <UUIDv4>
type: idea | plan | research-plan | research-findings | analysis | report | phase | content-plan | post-spec | post-outline | draft
status: draft | in-review | approved | complete
parent: <relative path>
children:
  - <relative path>
persona: <persona slug>
template: <template slug>
created: <ISO 8601>
updated: <ISO 8601>
---
```

## Tasks

- [ ] Create `content/_projects/` directory
- [ ] Create `content/_drafts/` directory
- [ ] Create `content/_templates/personas/` directory
- [ ] Create `content/_templates/outlines/` directory
- [ ] Create `content/_templates/research-plans/` directory
- [ ] Create `content/_templates/review-checklists/` directory
- [ ] Create `content/_templates/brainstorm-plans/` directory
- [ ] Create `content/_templates/schemas/` directory
- [ ] Update `src/content.config.ts` with optional `id` field
- [ ] Create `.claude/rules/blog-frontmatter.md`
- [ ] Create `.claude/rules/blog-self-review.md`
- [ ] Create `content/_templates/project-index.md` template
- [ ] Create `content/_templates/project-readme.md` template
- [ ] Create `content/_templates/brainstorm-plans/standard.md` template
- [ ] Create `content/_templates/schemas/artifact-schema.md` documentation

## Acceptance Tests

- [ ] All directories exist under `content/` including `_templates/schemas/` and `_templates/brainstorm-plans/`
- [ ] `astro build` succeeds with schema change
- [ ] Existing blog post with added `id: "<valid-uuid>"` passes validation
- [ ] Existing blog post without `id` field still passes (optional)
- [ ] `.claude/rules/blog-frontmatter.md` loads in Claude Code rules context
- [ ] Manual `content/_projects/test/index.md` with manifest template has valid YAML
- [ ] `project-readme.md` template has all placeholder sections
- [ ] `brainstorm-plans/standard.md` template has valid frontmatter

## Dependencies

None (this is the foundation phase).

## Estimated Effort

1-2 hours
