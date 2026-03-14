# Phase 5: Post Commands

## Objective

Write a single post from a phase plan.

## Deliverables

### Post Artifact Storage

Post artifacts (spec, outline) are stored alongside the phase file they derive from:

```text
content/_projects/<slug>/
├── phase/
│   ├── 0-tutorial-ebpf.md              # phase file
│   ├── 0-tutorial-ebpf.spec.md         # post-spec for phase 0
│   └── 0-tutorial-ebpf.outline.md      # post-outline for phase 0
```

Alternative naming pattern (if multiple posts per phase):

```text
content/_projects/<slug>/
├── posts/
│   └── tutorial-ebpf/
│       ├── spec.md
│       └── outline.md
```

**Decision**: Use inline pattern (`<phase>.spec.md`, `<phase>.outline.md`) for simplicity.

### 1. Post Commands

Create under `.claude/commands/blog/post/`:

| Command | Purpose |
|---------|---------|
| `spec.md` | Phase file → post spec |
| `plan.md` | Post spec → structural outline |
| `draft.md` | Outline → full draft |
| `refine.md` | Update any post artifact |
| `review.md` | Evaluate draft quality |

### 2. Review Checklists

Create `content/_templates/review-checklists/post-spec.md`:

```markdown
---
type: review-checklist
name: Post Spec Review
applies_to: post-spec
---

## Audience Definition

- [ ] Target audience clearly described
- [ ] Skill level specified
- [ ] What reader will gain is explicit

## Takeaways

- [ ] 3-5 key takeaways identified
- [ ] Takeaways are concrete and actionable
- [ ] Ordered by importance

## Prerequisites

- [ ] Required knowledge listed
- [ ] Links to prerequisite content (if applicable)
- [ ] Nothing assumed that isn't stated

## Scope

- [ ] Boundaries clear (what's NOT covered)
- [ ] Achievable in estimated word count
- [ ] Aligns with phase file
```

Create `content/_templates/review-checklists/post-outline.md`:

```markdown
---
type: review-checklist
name: Post Outline Review
applies_to: post-outline
---

## Structure

- [ ] Sections follow template structure
- [ ] Logical flow from start to end
- [ ] Each section has clear purpose

## Balance

- [ ] Word estimates total to target length
- [ ] No section dominates disproportionately
- [ ] Introduction and conclusion appropriately sized

## Completeness

- [ ] All spec takeaways covered
- [ ] Code example locations marked
- [ ] Diagram/image placements noted

## Readability

- [ ] Headers are descriptive
- [ ] Transitions between sections planned
- [ ] Complexity builds progressively
```

Create `content/_templates/review-checklists/post-draft.md`:

```markdown
---
type: review-checklist
name: Post Draft Review
applies_to: draft
---

## Clarity

- [ ] Opening hooks the reader
- [ ] Each section has clear purpose
- [ ] Transitions between sections smooth
- [ ] Conclusion provides clear takeaway

## Technical Accuracy

- [ ] Code examples tested/verified
- [ ] Technical claims accurate
- [ ] Edge cases acknowledged

## Voice Consistency

- [ ] Matches configured persona
- [ ] Consistent throughout post
- [ ] No jarring tone shifts

## Structure

- [ ] Follows outline template
- [ ] Section lengths balanced
- [ ] Headers accurately describe content

## Completeness

- [ ] All outline points addressed
- [ ] Prerequisites satisfied
- [ ] Links to related content included
```

### 3. Additional Outline Template

Create `content/_templates/outlines/deep-dive.md` (if not already seeded):

```markdown
---
type: template
name: Deep Dive
applies_to: post-outline
content_type: deep-dive
---

## Structure

### 1. Hook (100-200 words)

- Start with the "aha" moment
- Why this matters now

### 2. Context (200-300 words)

- What you need to know first
- Brief history/background

### 3. Deep Dive Sections (1500-2500 words total)

- 3-5 sections exploring the topic
- Each section builds on previous
- Include diagrams/code where helpful

### 4. Practical Applications (300-500 words)

- Real-world usage
- When to use/not use

### 5. Conclusion (100-200 words)

- Key insights
- What to explore next
```

## Command Behaviors

### spec.md

**Input**: Phase file path

**Output**: Post spec at `phase/<N>-<slug>.spec.md` (`type: post-spec`)

**Logic**:

1. Load phase file
2. Check for persona (prompt if not set)
3. Generate spec with:
   - Target audience
   - Key takeaways (3-5)
   - Prerequisites
   - Related posts
   - Code examples needed
4. Create post-spec artifact at `phase/<N>-<slug>.spec.md`
5. Update project status → `post` in `index.md`
6. Add post-spec to Artifacts table

### plan.md

**Input**: Post spec path

**Output**: Structural outline at `phase/<N>-<slug>.outline.md` (`type: post-outline`)

**Logic**:

1. Load post spec
2. Load outline template (from `template` frontmatter or default)
3. Generate detailed outline:
   - Sections with word estimates
   - Code example placements
   - Diagram locations
4. Create post-outline artifact at `phase/<N>-<slug>.outline.md`
5. Run self-review for structure
6. Update `index.md` Artifacts table

### draft.md

**Input**: Post outline path

**Output**: Full draft at `content/_drafts/<slug>.md`

**Logic**:

1. Load outline
2. Load persona
3. Generate full draft following:
   - Outline structure
   - Persona voice
   - Word estimates
4. Generate AstroPaper frontmatter:
   - `id: <UUIDv4>`
   - `title`
   - `description` (max 160 chars)
   - `pubDatetime` (ISO 8601)
   - `draft: true`
   - `tags`
   - `author: "aRustyDev"`
5. Run self-review for voice/style
6. Update `index.md`

### review.md

**Input**: Draft path

**Output**: Quality evaluation

**Logic**:

1. Load draft
2. Load persona
3. Load `post-draft.md` checklist
4. Evaluate each criterion
5. Check voice against persona
6. Update status → `in-review`

### refine.md

**Input**: Any post artifact + feedback

**Output**: Updated artifact

**Logic**:

1. Load artifact and feedback
2. Apply improvements
3. Maintain persona voice
4. Run self-review
5. Update status → `draft`
6. Update `index.md` with status change

## Draft Frontmatter (AstroPaper)

```yaml
---
id: "550e8400-e29b-41d4-a716-446655440000"
title: "Building eBPF Tracing Tools: A Practical Guide"
description: "Learn to build powerful Linux tracing tools using eBPF with step-by-step examples."
pubDatetime: 2026-03-14T00:00:00Z
modDatetime: null
author: "aRustyDev"
featured: false
draft: true
tags:
  - ebpf
  - linux
  - tracing
ogImage: ""
canonicalURL: ""
hideEditPost: false
timezone: "America/New_York"
---
```

## Tasks

- [ ] Create `.claude/commands/blog/post/` directory
- [ ] Write `post/spec.md` command
- [ ] Write `post/plan.md` command
- [ ] Write `post/draft.md` command
- [ ] Write `post/refine.md` command
- [ ] Write `post/review.md` command
- [ ] Create `content/_templates/review-checklists/post-spec.md`
- [ ] Create `content/_templates/review-checklists/post-outline.md`
- [ ] Create `content/_templates/review-checklists/post-draft.md`
- [ ] Create `content/_templates/outlines/deep-dive.md` (if needed)
- [ ] Test full post writing flow
- [ ] Verify AstroPaper frontmatter compliance

## Acceptance Tests

- [ ] `/blog/post/spec` reads phase file → produces `type: post-spec`
- [ ] Post spec stored at `phase/<N>-<slug>.spec.md`
- [ ] Post spec includes: audience, takeaways, prerequisites
- [ ] `/blog/post/plan` produces `type: post-outline` with sections
- [ ] Post outline stored at `phase/<N>-<slug>.outline.md`
- [ ] Outline includes word estimates and code locations
- [ ] `/blog/post/draft` produces draft at `content/_drafts/<slug>.md`
- [ ] Draft has valid AstroPaper frontmatter
- [ ] Draft includes: `id` (UUIDv4), `pubDatetime`, `draft: true`, `tags`, `title`, `description`
- [ ] Draft does NOT use: `date`, `image`, `canonical`, `type`
- [ ] `/blog/post/review` evaluates clarity, accuracy, voice
- [ ] Voice consistency checked against configured persona
- [ ] `/blog/post/refine` updates draft based on feedback
- [ ] Persona verification fires at `spec` start
- [ ] Outline template applied when specified in frontmatter
- [ ] All post artifacts tracked in `index.md`

## Entry Points

Per SPEC, post phase can be entered:

- **From content planning**: After phase files are created (normal flow)
- **Directly**: With `/blog/post/spec` if you know exactly what to write

When entering directly without a phase file:

1. Accept topic/outline as input
2. Create minimal project structure if needed
3. Create a synthetic phase file or work without one
4. Set project status to `post`

## Dependencies

- Phase 0 (Foundation) — required
- Phase 2 (Persona/Template) — required for personas and outline templates
- Phase 4 (Content Planning) — optional (can create post directly)

## Estimated Effort

4-5 hours
