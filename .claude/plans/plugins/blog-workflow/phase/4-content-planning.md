# Phase 4: Content Planning Commands

## Objective

Turn research output into planned work items (phases). This is where idea decomposition happens — a single research effort can produce multiple tutorials, deep-dives, experiments, or explainers.

## Architecture Note

Content planning bridges research and post creation:

- **`draft`** — Brainstorm what content pieces could come from research
- **`plan`** — Decompose brainstorm into numbered `phase/` files
- **`review`** — Evaluate brainstorm or phase files (auto-detects type)
- **`refine`** — Update artifacts based on review feedback

```
content/
├── draft.md    → Research report → content-brainstorm.md
├── plan.md     → Brainstorm → numbered phase/ files
├── refine.md   → Update any content artifact
└── review.md   → Evaluate brainstorm or phases
```

## Deliverables

### 1. Content Planning Commands

Create under `context/plugins/blog-workflow/commands/content/`:

| Command | Purpose | Output | Self-review |
|---------|---------|--------|-------------|
| `draft.md` | Research report → content brainstorm | `content-brainstorm.md` | Yes - feasibility check |
| `plan.md` | Brainstorm → phase files | `phase/0-<slug>.md`, etc. | Yes - dependency check |
| `refine.md` | Update content artifacts | Updated artifact | Yes - re-checks review items |
| `review.md` | Evaluate brainstorm or phases | Checklist evaluation | N/A - is the review |

**Command frontmatter pattern**:

```yaml
---
name: blog:content:draft
description: Create content brainstorm from research report
arguments:
  - name: path
    description: Path to the research report
    required: true
---
```

### 2. Artifact Templates

Create under `context/plugins/blog-workflow/.templates/`:

#### content-brainstorm.md

```markdown
---
type: content-brainstorm
id: "{{UUIDv4}}"
status: draft
parent: "{{relative path to research report}}"
persona: "{{persona slug if set}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

# Content Brainstorm: {{title}}

## Research Summary

{{Brief summary of key findings from research report}}

## Content Opportunities

### Tutorials

| Idea | Target Audience | Complexity | Priority |
|------|-----------------|------------|----------|
| {{tutorial idea}} | {{audience}} | {{beginner/intermediate/advanced}} | {{high/medium/low}} |

### Deep Dives

| Idea | Focus Area | Prerequisites | Priority |
|------|------------|---------------|----------|
| {{deep dive idea}} | {{area}} | {{prereqs}} | {{high/medium/low}} |

### Experiments

| Idea | Hypothesis | Effort | Priority |
|------|------------|--------|----------|
| {{experiment idea}} | {{what to test}} | {{estimate}} | {{high/medium/low}} |

### Explainers

| Idea | Core Concept | Audience | Priority |
|------|--------------|----------|----------|
| {{explainer idea}} | {{concept}} | {{audience}} | {{high/medium/low}} |

## Recommended Sequence

1. {{first piece — why start here}}
2. {{second piece — builds on first}}
3. {{third piece — etc.}}

## Dependencies

{{Note any pieces that require others to be completed first}}

## Scope Considerations

### Standalone Posts

{{Which ideas can be single posts}}

### Multi-Part Series

{{Which ideas need multiple posts or spawn child projects}}

## Feasibility Notes

{{Any concerns about effort, expertise gaps, or resource needs}}
```

#### phase.md

```markdown
---
type: phase
id: "{{UUIDv4}}"
status: draft
parent: "{{relative path to content-brainstorm.md}}"
children: []
phase_number: {{0, 1, 2, ...}}
title: "{{Phase Title}}"
content_type: tutorial | deep-dive | experiment | explainer
template: "{{template slug}}"
persona: "{{persona slug}}"
estimated_effort: "{{X-Y hours}}"
prerequisites:
  - "{{prerequisite knowledge}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

# Phase {{N}}: {{Title}}

## Summary

{{What this phase will cover and why it matters}}

## Target Audience

{{Who this content is for, what they should already know}}

## Key Points

1. {{Main point one}}
2. {{Main point two}}
3. {{Main point three}}

## Code Examples Needed

| Example | Purpose | Complexity |
|---------|---------|------------|
| {{example description}} | {{what it demonstrates}} | {{simple/moderate/complex}} |

## Related Research

| Finding | From Report Section | How It Applies |
|---------|---------------------|----------------|
| {{finding}} | {{section ref}} | {{application}} |

## Dependencies

### Requires (blocks this phase)

- {{other phase or external dependency}}

### Enables (this phase blocks)

- {{phases that depend on this one}}

## Child Project

{{If this phase spawns a child project, note it here}}

- Child project: `content/_projects/{{child-slug}}/`
- Reason: {{why this needs its own project}}
```

### 3. Review Checklists

Create under `context/plugins/blog-workflow/.templates/review-checklists/`:

#### content-brainstorm.md

```markdown
---
type: review-checklist
name: Content Brainstorm Review
applies_to: content-brainstorm
---

## Research Coverage

- [ ] All major research themes addressed
- [ ] Key findings translated into content ideas
- [ ] No significant gaps in coverage

## Feasibility

- [ ] Content ideas are achievable with available resources
- [ ] Effort estimates are realistic
- [ ] Expertise gaps identified (if any)

## Audience Clarity

- [ ] Target audience defined for each piece
- [ ] Complexity levels appropriate for audiences
- [ ] Prerequisites clearly stated

## Prioritization

- [ ] Priorities assigned to all ideas
- [ ] Recommended sequence is logical
- [ ] Dependencies between pieces identified

## Scope

- [ ] Standalone vs. series pieces identified
- [ ] No overlapping content between ideas
- [ ] Each idea is focused (not too broad)
```

#### phase.md

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

## Traceability

- [ ] Links back to content brainstorm
- [ ] Research findings referenced
- [ ] Child project linked (if applicable)
```

## Command Behaviors

### draft.md

**Input**: Path to research report

**Output**: `content/_projects/<slug>/content-brainstorm.md`

**Tools Used**:
- `Read` — load research report and project index
- `Write` — create content brainstorm

**Logic**:

1. **Load research report** at `{{path}}`
2. **Verify report status** is `complete`
3. **Persona verification**: Check for configured persona in project
   - If set, load from `context/plugins/blog-workflow/.templates/personas/<slug>.md`
   - Display: "This project uses persona: **{{name}}**. Use this persona? (yes / no / change)"
4. **Extract content opportunities** from report:
   - Identify potential tutorials from "how-to" findings
   - Identify deep-dives from complex technical findings
   - Identify experiments from open questions
   - Identify explainers from conceptual findings
5. **Assess feasibility** for each opportunity
6. **Generate content brainstorm** using `.templates/content-brainstorm.md`
7. **Create bidirectional links**:
   - Set `parent` in brainstorm to relative path to report
   - Add brainstorm to `children` in report frontmatter
8. **Update project status** → `content-planning` in `index.md`
9. **Add to Artifacts table** in `index.md`
10. **Self-review** (feasibility check):
    - Are effort estimates realistic?
    - Are there expertise gaps?
    - Is scope manageable?

**Example output**:

```text
Created content brainstorm: content/_projects/kubernetes-migration/content-brainstorm.md

Content opportunities identified:
- Tutorials: 2
- Deep dives: 1
- Experiments: 1
- Explainers: 1

Total pieces: 5
Recommended sequence: 5 ordered items

Self-review: passed

Next: Run `blog:content:plan {{path}}` to decompose into phases
      Or: Run `blog:content:review {{path}}` to evaluate brainstorm first
```

### plan.md

**Input**: Path to content brainstorm

**Output**: Numbered `phase/` files

**Tools Used**:
- `Read` — load content brainstorm
- `Write` — create phase files

**Logic**:

1. **Load content brainstorm** at `{{path}}`
2. **Verify brainstorm status** (can be `draft` or `approved`)
3. **Create `phase/` directory** if needed
4. **For each content piece** in recommended sequence:
   - Generate slug from title (lowercase, hyphenated, max 50 chars)
   - Create phase file: `phase/{{N}}-{{slug}}.md`
   - Set `phase_number` in frontmatter
   - Set `parent` to relative path to content-brainstorm.md
   - Populate from brainstorm data
5. **Identify child projects**:
   - If phase scope is too large (multiple posts needed)
   - If phase topic diverges significantly from parent
   - Create child project at `content/_projects/<child-slug>/`
   - Link via `children` in phase frontmatter
   - Link via `parent` in child `index.md`
6. **Update content brainstorm**:
   - Add all phase paths to `children` array
7. **Update parent project `index.md`**:
   - Add to Phases table
   - Add to Related Projects table (if children created)
8. **Self-review** (dependency check):
   - Are dependencies between phases explicit?
   - Is ordering logical for readers?
   - Do early phases avoid assuming later knowledge?

**Child project criteria**:

| Criterion | Create Child Project |
|-----------|---------------------|
| Estimated effort > 8 hours | Yes |
| Multiple posts needed | Yes |
| Different target audience | Yes |
| Standalone value | Yes |
| Tightly coupled to parent | No - keep as phase |

**Example output**:

```text
Decomposed into phases: content/_projects/kubernetes-migration/phase/

Phases created:
- phase/0-tutorial-basic-migration.md (tutorial, ~4h)
- phase/1-deep-dive-state-management.md (deep-dive, ~6h)
- phase/2-experiment-canary-releases.md (experiment, ~3h)

Child projects created:
- content/_projects/tutorial-ebpf/ (from phase/0, spawned due to scope)

Self-review: passed

Next: Run `blog:content:review {{path}}` to validate decomposition
```

### review.md

**Input**: Path to content brainstorm OR phase file

**Output**: Checklist evaluation with `## Review` section appended

**Tools Used**:
- `Read` — load artifact and checklist
- `Edit` — append review section

**Logic**:

1. **Load artifact** at `{{path}}`
2. **Detect artifact type** from frontmatter (`content-brainstorm` or `phase`)
3. **Load appropriate checklist**:
   - `content-brainstorm` → `.templates/review-checklists/content-brainstorm.md`
   - `phase` → `.templates/review-checklists/phase.md`
4. **Evaluate each criterion** (pass/warn/fail)
5. **Remove existing `## Review` section** if present
6. **Append new `## Review` section** to artifact:

```markdown
## Review

**Reviewed**: {{ISO 8601 timestamp}}
**Result**: {{pass|warn|fail}}

### Research Coverage (for brainstorm) / Scope (for phase)
- [x] Criterion — pass
- [~] Criterion — warn: {{reason}}
- [ ] Criterion — fail: {{reason}}

...

**Summary**: {{pass_count}} pass, {{warn_count}} warn, {{fail_count}} fail

{{If warnings or fails}}

### Action Items
1. {{specific action to address issue}}
2. {{specific action to address issue}}
{{/If}}
```

7. **Determine approval**:

| Condition | `--approve` flag | `--no-approve` flag | Default |
|-----------|------------------|---------------------|---------|
| All pass | approved | in-review | Prompt user |
| Warns only | approved | in-review | Prompt user |
| Any fail | in-review | in-review | in-review |

8. **Update status** in frontmatter
9. **Update `index.md`** with status change

**Example output (brainstorm)**:

```text
## Content Brainstorm Review: content-brainstorm.md

### Research Coverage
- [x] All major themes addressed — pass
- [x] Key findings translated — pass
- [x] No significant gaps — pass

### Feasibility
- [x] Ideas achievable — pass
- [~] Effort estimates realistic — warn: experiment may take longer
- [x] Expertise gaps identified — pass

### Audience Clarity
- [x] Target audience defined — pass
- [x] Complexity appropriate — pass
- [x] Prerequisites stated — pass

### Prioritization
- [x] Priorities assigned — pass
- [x] Sequence logical — pass
- [x] Dependencies identified — pass

### Scope
- [x] Standalone vs series identified — pass
- [x] No overlapping content — pass
- [x] Ideas focused — pass

Summary: 14 pass, 1 warn, 0 fail
Status: approved

Next: Run `blog:content:plan {{path}}` to decompose into phases
```

### refine.md

**Input**: Path to content artifact (brainstorm or phase)

**Output**: Updated artifact with `## Review` section removed

**Arguments**:
- `path` (required): Path to the artifact
- `feedback` (optional): Direct feedback (if not using `## Review` section)

**Tools Used**:
- `Read` — load artifact and review
- `Edit` — apply changes

**Logic**:

1. **Load artifact** at `{{path}}`
2. **Detect artifact type** from frontmatter
3. **Load feedback**:
   - If `--feedback` provided, use that
   - Otherwise, read `## Review` section from artifact
   - If neither, error: "No feedback found"
4. **Load corresponding checklist** for reference
5. **Apply improvements**:

   **For content-brainstorm**:
   - Add missing content opportunities
   - Adjust priorities based on feedback
   - Clarify audience definitions
   - Fix effort estimates
   - Resolve scope issues

   **For phase**:
   - Clarify scope boundaries
   - Add missing prerequisites
   - Fix dependency issues
   - Update code example specifications
   - Link additional research

6. **Remove `## Review` section** (will be regenerated on next review)
7. **Reset status** → `draft`
8. **Update `updated` timestamp**
9. **Self-review** (fail items only)
10. **Update `index.md`** with status change

**Example output**:

```text
Refined: content/_projects/kubernetes-migration/content-brainstorm.md

Changes applied:
- Updated effort estimate for experiment (3h → 5h)
- Added prerequisite for deep-dive
- Clarified audience for tutorial

Status reset to: draft

Next: Run `blog:content:review {{path}}` to re-evaluate
```

## Project Structure After Content Planning

```text
content/_projects/<slug>/
├── index.md                    # status: content-planning
├── idea.md                     # status: complete
├── plan.md                     # status: complete
├── research/
│   ├── plans/
│   │   └── <slug>.md           # status: complete
│   ├── findings/
│   │   └── <slug>.md           # status: complete
│   ├── analysis/
│   │   └── <slug>.md           # status: complete
│   └── reports/
│       └── <slug>.md           # status: complete
├── content-brainstorm.md       # status: approved
└── phase/
    ├── 0-tutorial-basics.md    # status: draft
    ├── 1-deep-dive-advanced.md # status: draft
    └── 2-experiment-testing.md # status: draft

content/_projects/<child-slug>/     # Child project (if created)
├── index.md                        # parent: content/_projects/<parent>/phase/0-*.md
└── ...
```

## Entry Points

Per SPEC, content planning can be entered at:

| Scenario | Start At | Notes |
|----------|----------|-------|
| From research | `blog:content:draft` | Normal flow after research report |
| Research done elsewhere | `blog:content:draft` | Accept external research path |
| Skip to post | `blog:post:spec` | If content planning not needed |

### Direct Entry Without Research Report

When entering `blog:content:draft` with external research:

1. Accept research document path (can be outside project)
2. Create project structure if needed
3. Create minimal `index.md` and `plan.md` as stubs
4. Set project status to `content-planning`
5. Continue with brainstorm creation

## Single-Post Projects

For simple ideas that don't need decomposition:

1. `blog:content:draft` creates brainstorm with one item
2. `blog:content:plan` creates single `phase/0-<slug>.md`
3. Proceed directly to `blog:post:spec` with that phase

The phase file is still created for consistency — it serves as the specification for the post.

## Alignment with SPEC

This phase implements SPEC sections:

- **Phase 3: Content Planning** (lines 122-138) — command structure and flow
- **Project Structure** (lines 209-230) — content-brainstorm.md and phase/ locations
- **Artifact Types** (lines 256-267) — content-brainstorm, phase types
- **Entry Points** (lines 636-638) — "Research already done" entry

Key SPEC quotes implemented:

> "draft | Research report | content-brainstorm.md (type: content-brainstorm): what posts, experiments, tutorials could come from this"
>
> "plan | content-brainstorm.md | Numbered phase/ files (type: phase) with decomposition. Creates child project links where needed"
>
> "The brainstorm output (content-brainstorm.md) can optionally be reviewed before proceeding to plan."

## Tasks

### Commands (4 files)

- [ ] Create `context/plugins/blog-workflow/commands/content/` directory
- [ ] Write `commands/content/draft.md` with command frontmatter
- [ ] Write `commands/content/plan.md` with command frontmatter
- [ ] Write `commands/content/refine.md` with command frontmatter
- [ ] Write `commands/content/review.md` with command frontmatter

### Templates (2 artifact templates)

- [ ] Create `.templates/content-brainstorm.md` artifact template
- [ ] Create `.templates/phase.md` artifact template

### Review Checklists (2 files)

- [ ] Create `.templates/review-checklists/content-brainstorm.md`
- [ ] Create `.templates/review-checklists/phase.md`

### Plugin Updates

- [ ] Update `plugin.json` with 4 new commands
- [ ] Update `marketplace.json` version (1.3.0 → 1.4.0)

### Testing

- [ ] Test draft: research report → content-brainstorm.md
- [ ] Test plan: brainstorm → phase/ files
- [ ] Test review on content-brainstorm (optional pre-plan review)
- [ ] Test review on phase files
- [ ] Test refine on both artifact types
- [ ] Test single-post decomposition (one phase)
- [ ] Test multi-post decomposition (multiple phases)
- [ ] Test child project creation flow
- [ ] Test direct entry without prior research report
- [ ] Verify persona verification fires at draft
- [ ] Verify `## Review` section appended/removed correctly
- [ ] Verify bidirectional links maintained
- [ ] Verify index.md tracking through all stages

## Acceptance Tests

(From SPEC lines 1044-1055, updated)

- [ ] `/blog/content/draft` reads report → produces `content-brainstorm.md` with `type: content-brainstorm`
- [ ] `/blog/content/plan` decomposes brainstorm into numbered `phase/` files
- [ ] Phase files have `type: phase` in frontmatter
- [ ] Phase files have `parent` pointing to `content-brainstorm.md`
- [ ] Content brainstorm has `children` array with phase paths
- [ ] Child projects created flat at `content/_projects/<child-slug>/`
- [ ] Phase `children` links to child `index.md`
- [ ] Child `parent` links back to phase file
- [ ] `/blog/content/review` auto-detects artifact type
- [ ] `/blog/content/review` validates: no gaps, no overlaps, correct ordering
- [ ] `/blog/content/review` appends `## Review` section to artifact
- [ ] `/blog/content/refine` removes `## Review` section after applying fixes
- [ ] `index.md` Phases table populated
- [ ] `index.md` Related Projects table populated for child projects
- [ ] Persona verification fires at `draft` start
- [ ] Single-post idea produces exactly one phase file
- [ ] The full content planning flow completes end-to-end

## Dependencies

- Phase 0 (Foundation) — required for templates, rules, schemas
- Phase 3 (Research) — optional (can use existing research)
- Phase 2 (Persona/Template) — for persona verification at draft

## Estimated Effort

4-5 hours

- Commands (4 files): 2 hours
- Artifact templates (2 files): 45 min
- Review checklists (2 files): 30 min
- Plugin manifest updates: 15 min
- Testing all workflows: 1 hour
