# Phase 5: Post Commands

## Objective

Write a single post from a phase plan. Each phase file becomes one post with its own spec, outline, and draft.

## Architecture Note

Post commands follow the established pattern:

- **`spec`** — Create post specification from phase file
- **`plan`** — Create structural outline from spec
- **`draft`** — Write full post from outline
- **`review`** — Evaluate draft quality (auto-detects artifact type)
- **`refine`** — Update artifacts based on review feedback

```
post/
├── spec.md    → Phase file → post specification
├── plan.md    → Spec → structural outline
├── draft.md   → Outline → full draft
├── refine.md  → Update any post artifact
└── review.md  → Evaluate spec, outline, or draft
```

## Post Artifact Storage

Post artifacts are organized under `post/<phase-slug>/`:

```text
content/_projects/<slug>/
├── phase/
│   ├── 0-tutorial-ebpf.md         # Phase file
│   └── 1-deep-dive-state.md       # Phase file
└── post/
    ├── tutorial-ebpf/
    │   ├── spec.md                # Post specification
    │   └── outline.md             # Structural outline
    └── deep-dive-state/
        ├── spec.md
        └── outline.md
```

**Single-post projects** use the same structure with one subdirectory:

```text
post/
└── main/
    ├── spec.md
    └── outline.md
```

**Drafts** are stored separately in the shared drafts directory:

```text
content/_drafts/
└── tutorial-ebpf.md               # AstroPaper-compatible draft
```

## Deliverables

### 1. Post Commands

Create under `context/plugins/blog-workflow/commands/post/`:

| Command | Purpose | Output | Self-review |
|---------|---------|--------|-------------|
| `spec.md` | Phase → post spec | `post/<slug>/spec.md` | Yes - completeness check |
| `plan.md` | Spec → outline | `post/<slug>/outline.md` | Yes - structure check |
| `draft.md` | Outline → draft | `content/_drafts/<slug>.md` | Yes - style/voice check |
| `refine.md` | Update post artifacts | Updated artifact | Yes - re-checks review items |
| `review.md` | Evaluate any post artifact | Checklist evaluation | N/A - is the review |

**Command frontmatter pattern**:

```yaml
---
name: blog:post:spec
description: Create post specification from phase file
arguments:
  - name: path
    description: Path to the phase file
    required: true
---
```

### 2. Artifact Templates

Create under `context/plugins/blog-workflow/.templates/`:

#### post-spec.md

```markdown
---
type: post-spec
id: "{{UUIDv4}}"
status: draft
parent: "{{relative path to phase file}}"
persona: "{{persona slug}}"
template: "{{outline template slug}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

# Post Spec: {{title}}

## Target Audience

**Who is this for?**
{{description of target reader}}

**Skill level**: {{beginner | intermediate | advanced}}

**What they'll gain**:
{{specific value proposition}}

## Key Takeaways

1. {{concrete, actionable takeaway}}
2. {{concrete, actionable takeaway}}
3. {{concrete, actionable takeaway}}
4. {{concrete, actionable takeaway}}
5. {{concrete, actionable takeaway}}

## Prerequisites

### Required Knowledge

- {{what reader must already know}}
- {{what reader must already know}}

### Recommended Reading

- [{{related post title}}]({{path or URL}})

## Scope

### What This Post Covers

- {{topic included}}
- {{topic included}}

### What This Post Does NOT Cover

- {{explicit exclusion}}
- {{explicit exclusion}}

## Code Examples Needed

| Example | Purpose | Language | Complexity |
|---------|---------|----------|------------|
| {{description}} | {{what it demonstrates}} | {{lang}} | {{simple/moderate/complex}} |

## Estimated Length

**Target**: {{X,XXX}} words
**Reading time**: {{N}} minutes

## Related Posts

| Post | Relationship |
|------|--------------|
| {{title}} | Prerequisite |
| {{title}} | Follow-up |
| {{title}} | Alternative approach |
```

#### post-outline.md

```markdown
---
type: post-outline
id: "{{UUIDv4}}"
status: draft
parent: "{{relative path to spec.md}}"
created: "{{ISO 8601}}"
updated: "{{ISO 8601}}"
---

# Post Outline: {{title}}

## Structure Overview

| Section | Words | Purpose |
|---------|-------|---------|
| Introduction | {{N}} | Hook and context |
| {{Section 1}} | {{N}} | {{purpose}} |
| {{Section 2}} | {{N}} | {{purpose}} |
| {{Section 3}} | {{N}} | {{purpose}} |
| Conclusion | {{N}} | Summary and next steps |
| **Total** | **{{N}}** | |

## Introduction (~{{N}} words)

### Hook

{{opening line or question that grabs attention}}

### Context

{{why this matters now, brief background}}

### What You'll Learn

{{preview of key takeaways}}

## {{Section 1 Title}} (~{{N}} words)

### Key Points

- {{point 1}}
- {{point 2}}

### Code Example

**Location**: After {{point}}
**Purpose**: {{what it demonstrates}}
**Type**: {{snippet | full example | interactive}}

### Transition

{{how this connects to next section}}

## {{Section 2 Title}} (~{{N}} words)

### Key Points

- {{point 1}}
- {{point 2}}

### Diagram/Visual

**Location**: {{where in section}}
**Type**: {{diagram | screenshot | flowchart}}
**Shows**: {{what it illustrates}}

### Transition

{{how this connects to next section}}

## {{Section 3 Title}} (~{{N}} words)

### Key Points

- {{point 1}}
- {{point 2}}

## Conclusion (~{{N}} words)

### Summary

{{recap of key insights}}

### Call to Action

{{what reader should do next}}

### Related Resources

{{links to further reading}}
```

### 3. Outline Templates

Create under `context/plugins/blog-workflow/.templates/outlines/`:

#### tutorial.md

```markdown
---
type: template
name: Tutorial
applies_to: post-outline
content_type: tutorial
---

## Structure

### 1. Introduction (150-250 words)

- What we're building
- Why it matters
- Prerequisites check

### 2. Setup (200-400 words)

- Environment requirements
- Installation steps
- Verification that setup works

### 3. Step-by-Step Guide (1000-2000 words)

- 3-7 distinct steps
- Each step: explanation → code → verification
- Progressive complexity

### 4. Testing/Verification (200-400 words)

- How to verify it works
- Common issues and fixes

### 5. Next Steps (100-200 words)

- What to explore next
- Related tutorials
- Production considerations
```

#### deep-dive.md

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

#### experiment.md

```markdown
---
type: template
name: Experiment
applies_to: post-outline
content_type: experiment
---

## Structure

### 1. Hypothesis (150-250 words)

- What we're testing
- Why it matters
- Expected outcome

### 2. Methodology (300-500 words)

- Setup and environment
- Variables and controls
- Measurement approach

### 3. Experiment (800-1500 words)

- Step-by-step execution
- Observations during
- Raw results

### 4. Analysis (400-600 words)

- What the results mean
- Unexpected findings
- Limitations

### 5. Conclusions (200-300 words)

- Was hypothesis confirmed?
- Practical implications
- Future experiments
```

#### explainer.md

```markdown
---
type: template
name: Explainer
applies_to: post-outline
content_type: explainer
---

## Structure

### 1. The Question (100-200 words)

- What we're explaining
- Why it's confusing or misunderstood

### 2. The Simple Answer (200-300 words)

- ELI5 version
- Core concept in plain language

### 3. Going Deeper (800-1200 words)

- 2-4 layers of increasing detail
- Analogies and examples
- Visual aids where helpful

### 4. Common Misconceptions (200-400 words)

- What people get wrong
- Why they get it wrong
- The correct understanding

### 5. Summary (100-200 words)

- Key points to remember
- When this knowledge applies
```

### 4. Review Checklists

Create under `context/plugins/blog-workflow/.templates/review-checklists/`:

#### post-spec.md

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

#### post-outline.md

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

#### post-draft.md

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

## Command Behaviors

### spec.md

**Input**: Path to phase file

**Output**: `post/<phase-slug>/spec.md`

**Tools Used**:
- `Read` — load phase file and research
- `Write` — create spec

**Logic**:

1. **Load phase file** at `{{path}}`
2. **Verify phase status** is `draft` or `approved`
3. **Persona verification**:
   - Check for configured persona in phase or project
   - If set, load from `context/plugins/blog-workflow/.templates/personas/<slug>.md`
   - Display: "This post uses persona: **{{name}}**. Use this persona? (yes / no / change)"
4. **Extract post requirements** from phase:
   - Title and summary
   - Key points
   - Code example needs
   - Related research
5. **Generate spec** using `.templates/post-spec.md`:
   - Define target audience
   - List 3-5 key takeaways
   - Identify prerequisites
   - Specify code examples needed
   - Estimate word count
6. **Create post directory**: `post/<phase-slug>/`
7. **Write spec**: `post/<phase-slug>/spec.md`
8. **Create bidirectional links**:
   - Set `parent` in spec to relative path to phase file
   - Add spec to `children` in phase file
9. **Update project status** → `post` in `index.md`
10. **Add to Artifacts table** in `index.md`
11. **Self-review** (completeness check):
    - Are takeaways concrete?
    - Are prerequisites clear?
    - Is scope achievable?

**Example output**:

```text
Created post spec: content/_projects/kubernetes-migration/post/tutorial-basics/spec.md

Post: Tutorial Basics
Persona: technical-educator
Template: tutorial
Target: ~2,500 words (~10 min read)

Takeaways: 5
Prerequisites: 2
Code examples: 3

Self-review: passed

Next: Run `blog:post:plan {{path}}` to create outline
```

### plan.md

**Input**: Path to post spec

**Output**: `post/<phase-slug>/outline.md`

**Tools Used**:
- `Read` — load spec and template
- `Write` — create outline

**Logic**:

1. **Load post spec** at `{{path}}`
2. **Load outline template**:
   - From `template` field in spec frontmatter
   - Or default based on `content_type` from phase
   - Path: `context/plugins/blog-workflow/.templates/outlines/<template>.md`
3. **Generate outline** following template structure:
   - Create sections with word estimates
   - Mark code example locations
   - Note diagram/visual placements
   - Plan transitions between sections
4. **Verify word estimates** sum to target length
5. **Write outline**: `post/<phase-slug>/outline.md`
6. **Create bidirectional links**:
   - Set `parent` in outline to `./spec.md`
   - Add outline to `children` in spec
7. **Update Artifacts table** in `index.md`
8. **Self-review** (structure check):
   - Does structure follow template?
   - Are word estimates balanced?
   - Are all takeaways covered?

**Example output**:

```text
Created post outline: content/_projects/kubernetes-migration/post/tutorial-basics/outline.md

Template: tutorial
Sections: 5
Total words: ~2,500

Section breakdown:
- Introduction: 200 words
- Setup: 350 words
- Step-by-Step Guide: 1,500 words (5 steps)
- Testing: 300 words
- Next Steps: 150 words

Code examples: 3 locations marked
Diagrams: 1 location marked

Self-review: passed

Next: Run `blog:post:draft {{path}}` to write full post
```

### draft.md

**Input**: Path to post outline

**Output**: `content/_drafts/<slug>.md`

**Tools Used**:
- `Read` — load outline, spec, persona
- `Write` — create draft

**Logic**:

1. **Load outline** at `{{path}}`
2. **Load spec** from outline's `parent`
3. **Load persona** from spec frontmatter
4. **Generate full draft** following:
   - Outline structure and sections
   - Persona voice and tone
   - Word estimates per section
5. **Write code examples** at marked locations
6. **Generate AstroPaper frontmatter**:

   ```yaml
   ---
   id: "{{UUIDv4}}"
   title: "{{title}}"
   description: "{{max 160 chars}}"
   pubDatetime: {{ISO 8601}}
   modDatetime: null
   author: "aRustyDev"
   featured: false
   draft: true
   tags:
     - {{tag}}
   ogImage: ""
   canonicalURL: ""
   hideEditPost: false
   timezone: "America/New_York"
   ---
   ```

7. **Generate slug** from title (lowercase, hyphenated)
8. **Write draft**: `content/_drafts/<slug>.md`
9. **Update Artifacts table** in `index.md`
10. **Self-review** (style/voice check):
    - Does voice match persona?
    - Is tone consistent throughout?
    - Are transitions smooth?

> **Note**: AstroPaper frontmatter schema is documented in `context/plugins/blog-workflow/rules/blog-frontmatter.md`

**Example output**:

```text
Created draft: content/_drafts/building-ebpf-tracing-tools.md

Title: Building eBPF Tracing Tools: A Practical Guide
Words: 2,487
Reading time: ~10 minutes

Sections written: 5
Code examples: 3
Voice: technical-educator (verified)

Self-review: passed

Next: Run `blog:post:review {{path}}` to evaluate
```

### review.md

**Input**: Path to any post artifact (spec, outline, or draft)

**Output**: Checklist evaluation with `## Review` section appended

**Arguments**:
- `path` (required): Path to the artifact
- `approve` (optional): Auto-approve if only warnings remain
- `no-approve` (optional): Never approve, evaluation only

**Tools Used**:
- `Read` — load artifact, persona, checklist
- `Edit` — append review section

**Logic**:

1. **Load artifact** at `{{path}}`
2. **Detect artifact type** from frontmatter (`post-spec`, `post-outline`, or `draft`)
3. **Load appropriate checklist**:
   - `post-spec` → `.templates/review-checklists/post-spec.md`
   - `post-outline` → `.templates/review-checklists/post-outline.md`
   - `draft` → `.templates/review-checklists/post-draft.md`
4. **Load persona** (for voice consistency check on drafts)
5. **Evaluate each criterion** (pass/warn/fail)
6. **For drafts**: Check voice against persona
7. **Remove existing `## Review` section** if present
8. **Append new `## Review` section**:

```markdown
## Review

**Reviewed**: {{ISO 8601 timestamp}}
**Result**: {{pass|warn|fail}}

### Audience Definition (for spec) / Clarity (for draft)
- [x] Criterion — pass
- [~] Criterion — warn: {{reason}}
- [ ] Criterion — fail: {{reason}}

...

**Summary**: {{pass_count}} pass, {{warn_count}} warn, {{fail_count}} fail

{{If warnings or fails}}

### Action Items
1. {{specific action}}
2. {{specific action}}
{{/If}}
```

9. **Determine approval**:

| Condition | `--approve` flag | `--no-approve` flag | Default |
|-----------|------------------|---------------------|---------|
| All pass | approved | in-review | Prompt user |
| Warns only | approved | in-review | Prompt user |
| Any fail | in-review | in-review | in-review |

10. **Update status** in frontmatter
11. **Update `index.md`** with status change

**Example output (draft)**:

```text
## Post Draft Review: building-ebpf-tracing-tools.md

### Clarity
- [x] Opening hooks reader — pass
- [x] Sections have clear purpose — pass
- [x] Transitions smooth — pass
- [x] Conclusion provides takeaway — pass

### Technical Accuracy
- [x] Code examples verified — pass
- [x] Technical claims accurate — pass
- [~] Edge cases acknowledged — warn: consider mentioning kernel version requirements

### Voice Consistency
- [x] Matches persona — pass
- [x] Consistent throughout — pass
- [x] No tone shifts — pass

### Structure
- [x] Follows outline — pass
- [x] Sections balanced — pass
- [x] Headers accurate — pass

### Completeness
- [x] All outline points addressed — pass
- [x] Prerequisites satisfied — pass
- [x] Related links included — pass

Summary: 14 pass, 1 warn, 0 fail
Status: approved

Next: Run `blog:publish:seo-review {{path}}` to prepare for publication
```

### refine.md

**Input**: Path to any post artifact (spec, outline, or draft)

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
4. **Load persona** (for voice consistency on drafts)
5. **Apply improvements**:

   **For post-spec**:
   - Clarify audience definition
   - Refine takeaways
   - Update prerequisites
   - Adjust scope

   **For post-outline**:
   - Rebalance section lengths
   - Improve transitions
   - Add missing code/diagram markers
   - Fix structure issues

   **For draft**:
   - Improve clarity
   - Fix technical issues
   - Adjust voice/tone
   - Complete missing sections
   - Maintain persona voice throughout

6. **Remove `## Review` section**
7. **Reset status** → `draft`
8. **Update `updated` timestamp**
9. **Self-review** (fail items only)
10. **Update `index.md`** with status change

**Example output**:

```text
Refined: content/_drafts/building-ebpf-tracing-tools.md

Changes applied:
- Added kernel version requirements to Prerequisites section
- Expanded edge case discussion in Step 3
- Maintained technical-educator voice throughout

Status reset to: draft

Next: Run `blog:post:review {{path}}` to re-evaluate
```

## Draft Frontmatter (AstroPaper)

All drafts use AstroPaper-compatible frontmatter:

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

> **Reference**: Full schema documented in `context/plugins/blog-workflow/rules/blog-frontmatter.md`

## Project Structure After Post Phase

```text
content/_projects/<slug>/
├── index.md                    # status: post
├── idea.md                     # status: complete
├── plan.md                     # status: complete
├── research/
│   └── ...                     # all complete
├── content-brainstorm.md       # status: complete
├── phase/
│   ├── 0-tutorial-basics.md    # status: complete
│   └── 1-deep-dive-state.md    # status: in-progress
└── post/
    ├── tutorial-basics/
    │   ├── spec.md             # status: complete
    │   └── outline.md          # status: complete
    └── deep-dive-state/
        ├── spec.md             # status: draft
        └── outline.md          # (not yet created)

content/_drafts/
├── kubernetes-migration-tutorial-basics.md    # draft: true
└── ...
```

## Entry Points

Per SPEC, post phase can be entered at:

| Scenario | Start At | Notes |
|----------|----------|-------|
| From content planning | `blog:post:spec` | Normal flow after phase files |
| Know exactly what to write | `blog:post:spec` | Create minimal phase first |
| Post already outlined | `blog:post:draft` | With existing outline |

### Direct Entry Without Phase File

When entering `blog:post:spec` without a phase file:

1. Prompt for post topic and type
2. Create minimal project structure if needed
3. Create synthetic phase file with provided details
4. Continue with spec creation

This maintains project structure consistency while allowing flexible entry.

## Single-Post Projects

For simple ideas that don't need decomposition:

1. Content brainstorm identifies one piece
2. `blog:content:plan` creates single `phase/0-main.md`
3. `blog:post:spec` creates `post/main/spec.md`
4. Normal post flow continues

The phase file is still created for consistency and traceability.

## Alignment with SPEC

This phase implements SPEC sections:

- **Phase 4: Post** (lines 140-158) — command structure and flow
- **Project Structure** (lines 222-224) — post/ subdirectory
- **Artifact Types** (lines 264-266) — post-spec, post-outline, draft
- **AstroPaper Frontmatter** (lines 519-540) — required fields

Key SPEC quotes implemented:

> "spec | Phase file | post/spec.md (type: post-spec): audience, takeaways, examples needed, prerequisites, related posts"
>
> "plan | post/spec.md | post/outline.md (type: post-outline): sections, word estimates, code example locations"
>
> "draft | Post outline | Full draft at content/_drafts/<slug>.md with AstroPaper frontmatter"
>
> "Persona verification: At spec start, check for configured persona and confirm with user in conversation."

## Tasks

### Commands (5 files)

- [ ] Create `context/plugins/blog-workflow/commands/post/` directory
- [ ] Write `commands/post/spec.md` with command frontmatter
- [ ] Write `commands/post/plan.md` with command frontmatter
- [ ] Write `commands/post/draft.md` with command frontmatter
- [ ] Write `commands/post/refine.md` with command frontmatter
- [ ] Write `commands/post/review.md` with command frontmatter

### Artifact Templates (2 files)

- [ ] Create `.templates/post-spec.md` artifact template
- [ ] Create `.templates/post-outline.md` artifact template

### Outline Templates (4 files)

- [ ] Create `.templates/outlines/tutorial.md`
- [ ] Create `.templates/outlines/deep-dive.md`
- [ ] Create `.templates/outlines/experiment.md`
- [ ] Create `.templates/outlines/explainer.md`

### Review Checklists (3 files)

- [ ] Create `.templates/review-checklists/post-spec.md`
- [ ] Create `.templates/review-checklists/post-outline.md`
- [ ] Create `.templates/review-checklists/post-draft.md`

### Plugin Updates

- [ ] Update `plugin.json` with 5 new commands
- [ ] Update `marketplace.json` version (1.4.0 → 1.5.0)

### Testing

- [ ] Test spec: phase file → post/spec.md
- [ ] Test plan: spec → post/outline.md
- [ ] Test draft: outline → content/_drafts/<slug>.md
- [ ] Test review on spec (auto-detect)
- [ ] Test review on outline (auto-detect)
- [ ] Test review on draft (auto-detect)
- [ ] Test refine on all three artifact types
- [ ] Test persona verification at spec start
- [ ] Test voice consistency check in draft review
- [ ] Test all four outline templates
- [ ] Verify AstroPaper frontmatter compliance
- [ ] Verify `## Review` section appended/removed correctly
- [ ] Verify bidirectional links maintained
- [ ] Verify index.md tracking through all stages

## Acceptance Tests

- [ ] `/blog/post/spec` reads phase file → produces `post/<slug>/spec.md` with `type: post-spec`
- [ ] Post spec includes: audience, takeaways, prerequisites, scope, code examples
- [ ] `/blog/post/plan` produces `post/<slug>/outline.md` with `type: post-outline`
- [ ] Outline includes: sections, word estimates, code locations, transitions
- [ ] Outline template applied when specified in spec frontmatter
- [ ] `/blog/post/draft` produces draft at `content/_drafts/<slug>.md`
- [ ] Draft has valid AstroPaper frontmatter with all required fields
- [ ] Draft includes: `id` (UUIDv4), `pubDatetime`, `draft: true`, `tags`, `title`, `description`
- [ ] `/blog/post/review` auto-detects artifact type (spec, outline, draft)
- [ ] `/blog/post/review` evaluates against appropriate checklist
- [ ] `/blog/post/review` appends `## Review` section to artifact
- [ ] Voice consistency checked against configured persona for drafts
- [ ] `/blog/post/refine` removes `## Review` section after applying fixes
- [ ] `/blog/post/refine` resets status to `draft`
- [ ] Persona verification fires at `spec` start
- [ ] All post artifacts tracked in `index.md`
- [ ] Bidirectional links maintained (phase ↔ spec ↔ outline)
- [ ] Single-post projects work with `post/main/` structure
- [ ] The full post flow (spec → plan → draft → review) completes end-to-end

## Dependencies

- Phase 0 (Foundation) — required for templates, rules, schemas
- Phase 2 (Persona/Template) — required for personas and outline templates
- Phase 4 (Content Planning) — optional (can create post directly from phase)

## Estimated Effort

5-6 hours

- Commands (5 files): 2.5 hours
- Artifact templates (2 files): 30 min
- Outline templates (4 files): 1 hour
- Review checklists (3 files): 30 min
- Plugin manifest updates: 15 min
- Testing all workflows: 1 hour
