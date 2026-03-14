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

```text
post/
├── spec.md    → Phase file → post specification
├── plan.md    → Spec → structural outline
├── draft.md   → Outline → full draft
├── refine.md  → Update any post artifact
└── review.md  → Evaluate spec, outline, or draft
```

---

## Command Summary

| Command | Purpose | Output | Self-review |
|---------|---------|--------|-------------|
| `/blog/post/spec` | Phase → post spec | `post/<slug>/spec.md` | Yes - completeness check |
| `/blog/post/plan` | Spec → outline | `post/<slug>/outline.md` | Yes - structure check |
| `/blog/post/draft` | Outline → draft | `content/_drafts/<slug>.md` | Yes - style/voice check |
| `/blog/post/refine` | Update post artifacts | Updated artifact | Yes - re-checks review items |
| `/blog/post/review` | Evaluate any post artifact | Checklist evaluation | N/A - is the review |

---

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
└── kubernetes-migration-tutorial-ebpf.md    # AstroPaper-compatible draft
```

---

## Deliverables

### 1. Post Commands

Create under `context/plugins/blog-workflow/commands/post/`:

#### spec.md

```yaml
---
name: blog/post/spec
description: Create post specification from phase file
arguments:
  - name: path
    description: Path to the phase file
    required: true
  - name: force
    description: Overwrite existing spec
    required: false
---
```

#### plan.md

```yaml
---
name: blog/post/plan
description: Create structural outline from post spec
arguments:
  - name: path
    description: Path to the post spec
    required: true
  - name: force
    description: Overwrite existing outline
    required: false
  - name: template
    description: Override outline template (slug)
    required: false
---
```

#### draft.md

```yaml
---
name: blog/post/draft
description: Write full post draft from outline
arguments:
  - name: path
    description: Path to the post outline
    required: true
  - name: force
    description: Overwrite existing draft
    required: false
  - name: preview
    description: Generate intro + one section only (verify tone)
    required: false
---
```

#### review.md

```yaml
---
name: blog/post/review
description: Evaluate post artifact (spec, outline, or draft)
arguments:
  - name: path
    description: Path to the artifact or post/ directory for batch review
    required: true
  - name: approve
    description: Auto-approve if no fails (skip prompt)
    required: false
  - name: no-approve
    description: Keep in-review status even if passing
    required: false
---
```

#### refine.md

```yaml
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

---

## Template Architecture

### Artifact Templates vs Outline Templates

Two distinct template types serve different purposes:

**Artifact Templates** (`.templates/post-spec.md`, `.templates/post-outline.md`):

- Define the *structure* of artifacts
- Include frontmatter fields and section headers
- Used when creating new artifacts
- One template per artifact type

**Outline Templates** (`.templates/outlines/*.md`):

- Define the *content structure* of a post
- Specify sections, word counts, flow patterns
- Applied to post-outline artifacts during `/blog/post/plan`
- Multiple templates for different content types

### Relationship

```text
Phase file
    ↓
post-spec.md (artifact template) ← persona, target audience
    ↓
post-outline.md (artifact template) + tutorial.outline.md (outline template)
    ↓
Draft (AstroPaper frontmatter) ← persona voice applied
```

### Existing Outline Templates (from Phase 0)

The 18 templates in `.templates/outlines/` include these core types:

| content_type | Primary Template | Alternatives |
|--------------|------------------|--------------|
| `tutorial` | `tutorial.outline.md` | `getting-started.outline.md`, `how-i-built.outline.md` |
| `deep-dive` | `algorithm-deep-dive.outline.md` | `architecture-decision.outline.md`, `performance.outline.md` |
| `experiment` | `experiment.outline.md` | `debug-error.outline.md` |
| `explainer` | `first-look.outline.md` | `comparison.outline.md`, `library-evaluation.outline.md` |

Phase 5 does NOT create duplicate templates. The outline template definitions in this plan document the expected structure for reference. All 18 existing templates from Phase 0 remain valid choices.

---

### 3. Review Checklists

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

## Template Selection

- [ ] Outline template specified
- [ ] Template appropriate for content type
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

## Word Count

- [ ] Within 10% of target estimate
- [ ] No section significantly over/under
```

---

## Command Behaviors

### spec.md

**Input**: Path to phase file

**Output**: `post/<phase-slug>/spec.md`

**Tools Used**:

- `Read` — load phase file, research, project index
- `Write` — create spec
- `Bash` — create directories

**Logic**:

1. **Validate input**:
   - Check phase file exists at `{{path}}`
   - Check phase status is `draft` or `approved`
   - Check spec doesn't exist (unless `--force`)

2. **Persona verification**:
   - Check for configured persona in phase or project
   - If set, load from `context/plugins/blog-workflow/.templates/personas/<slug>.md`
   - Display dialog (see Persona Verification Dialog below)

3. **Extract post requirements** from phase:
   - Title and summary
   - Key points
   - Code example needs
   - Related research
   - Template preference

4. **Generate spec** using `.templates/post-spec.md`:
   - Define target audience from phase
   - List 3-5 key takeaways
   - Identify prerequisites
   - Specify code examples needed
   - Estimate word count based on content type

5. **Create post directory**: `post/<phase-slug>/`

6. **Write spec**: `post/<phase-slug>/spec.md`

7. **Create bidirectional links**:
   - Set `parent` in spec to relative path to phase file
   - Add spec to `children` in phase file

8. **Update project status** → `post` in `index.md`

9. **Add to Post Artifacts table** in `index.md`

10. **Self-review** (completeness check):
    - Are takeaways concrete?
    - Are prerequisites clear?
    - Is scope achievable?

**Example output**:

```text
Created post spec: content/_projects/kubernetes-migration/post/tutorial-basics/spec.md

Post: Tutorial Basics
Persona: practitioner
Template: tutorial.outline.md
Target: ~2,500 words (~10 min read)

Takeaways: 5
Prerequisites: 2
Code examples: 3

Self-review: passed

Next: Run `/blog/post/plan content/_projects/kubernetes-migration/post/tutorial-basics/spec.md`
```

### plan.md

**Input**: Path to post spec

**Output**: `post/<phase-slug>/outline.md`

**Tools Used**:

- `Read` — load spec and template
- `Write` — create outline

**Logic**:

1. **Validate input**:
   - Check spec exists at `{{path}}`
   - Check spec status (can be `draft` or `approved`)
   - Check outline doesn't exist (unless `--force`)

2. **Load outline template**:
   - If `--template` flag provided, use that
   - Otherwise, from `template` field in spec frontmatter
   - Or default based on `content_type` from phase
   - Path: `context/plugins/blog-workflow/.templates/outlines/<template>.md`

3. **Template preview** (optional):
   - Show template structure: "Using template: tutorial.outline.md"
   - Display section count and typical word distribution

4. **Generate outline** following template structure:
   - Create sections with word estimates
   - Mark code example locations
   - Note diagram/visual placements
   - Plan transitions between sections

5. **Verify word estimates** sum to target length (±10%)

6. **Write outline**: `post/<phase-slug>/outline.md`

7. **Create bidirectional links**:
   - Set `parent` in outline to `./spec.md`
   - Add outline to `children` in spec

8. **Update Post Artifacts table** in `index.md`

9. **Self-review** (structure check):
   - Does structure follow template?
   - Are word estimates balanced?
   - Are all takeaways covered?

**Example output**:

```text
Created post outline: content/_projects/kubernetes-migration/post/tutorial-basics/outline.md

Template: tutorial.outline.md
Sections: 5
Total words: ~2,500 (target: 2,500)

Section breakdown:
- Introduction: 200 words
- Setup: 350 words
- Step-by-Step Guide: 1,500 words (5 steps)
- Testing: 300 words
- Next Steps: 150 words

Code examples: 3 locations marked
Diagrams: 1 location marked

Self-review: passed

Next: Run `/blog/post/draft content/_projects/kubernetes-migration/post/tutorial-basics/outline.md`
```

### draft.md

**Input**: Path to post outline

**Output**: `content/_drafts/<slug>.md`

**Tools Used**:

- `Read` — load outline, spec, persona
- `Write` — create draft

**Logic**:

1. **Validate input**:
   - Check outline exists at `{{path}}`
   - Check outline status (can be `draft` or `approved`)
   - Generate slug, check for conflicts (unless `--force`)

2. **Preview mode** (if `--preview`):
   - Generate intro + first section only
   - Display for tone/voice verification
   - Exit without creating full draft

3. **Load context**:
   - Load outline at `{{path}}`
   - Load spec from outline's `parent`
   - Load persona from spec frontmatter
   - Load author from project or plugin settings

4. **Generate full draft** following:
   - Outline structure and sections
   - Persona voice and tone
   - Word estimates per section

5. **Write code examples** at marked locations

6. **Track word count** per section vs estimate

7. **Generate AstroPaper frontmatter** (see Author Configuration)

8. **Generate slug** (see Slug Generation Logic)

9. **Write draft**: `content/_drafts/<slug>.md`

10. **Update Post Artifacts table** in `index.md`

11. **Self-review** (style/voice check):
    - Does voice match persona?
    - Is tone consistent throughout?
    - Are transitions smooth?
    - Is word count within 10% of target?

**Example output**:

```text
Created draft: content/_drafts/kubernetes-migration-tutorial-basics.md

Title: Building Your First Kubernetes Migration: A Practical Guide
Words: 2,487 (target: 2,500, within 1%)
Reading time: ~10 minutes

Section word counts:
- Introduction: 195 (target: 200) ✓
- Setup: 362 (target: 350) ✓
- Step-by-Step Guide: 1,512 (target: 1,500) ✓
- Testing: 278 (target: 300) ✓
- Next Steps: 140 (target: 150) ✓

Code examples: 3
Voice: practitioner (verified)

Self-review: passed

Next: Run `/blog/post/review content/_drafts/kubernetes-migration-tutorial-basics.md`
```

### review.md

**Input**: Path to any post artifact (spec, outline, draft) or post/ directory

**Output**: Checklist evaluation with `## Review` section appended

**Tools Used**:

- `Read` — load artifact(s), persona, checklist
- `Edit` — append review section
- `Glob` — find artifacts if directory provided

**Logic**:

1. **Detect input type**:
   - If path is `post/` directory → batch review all specs and outlines
   - If path ends with `.md` → single artifact review
   - If path is `content/_drafts/` directory → batch review all drafts

2. **For each artifact**:

   a. Load artifact at `{{path}}`

   b. Detect artifact type:
   - `type: post-spec` in frontmatter → post-spec
   - `type: post-outline` in frontmatter → post-outline
   - `draft: true` in frontmatter (AstroPaper) → draft

   c. Load appropriate checklist:
   - `post-spec` → `.templates/review-checklists/post-spec.md`
   - `post-outline` → `.templates/review-checklists/post-outline.md`
   - `draft` → `.templates/review-checklists/post-draft.md`

   d. Load persona (for voice consistency check on drafts)

   e. Evaluate each criterion (pass/warn/fail)

   f. For drafts: Check voice against persona, verify word counts

   g. Remove existing `## Review` section if present

   h. Append new `## Review` section

3. **Review section format**:

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

4. **Determine approval**:

   | Condition | `--approve` flag | `--no-approve` flag | Default |
   |-----------|------------------|---------------------|---------|
   | All pass | approved | in-review | Prompt user |
   | Warns only | approved | in-review | Prompt user |
   | Any fail | in-review | in-review | in-review |

5. **Update status** in frontmatter (for spec/outline) or note in draft

6. **Update `index.md`** with status change

**Batch review output**:

```text
## Post Artifacts Review: kubernetes-migration

Reviewed 4 artifacts:

| Artifact | Type | Result | Pass | Warn | Fail |
|----------|------|--------|------|------|------|
| post/tutorial-basics/spec.md | post-spec | pass | 12 | 0 | 0 |
| post/tutorial-basics/outline.md | post-outline | pass | 11 | 0 | 0 |
| post/deep-dive-state/spec.md | post-spec | warn | 10 | 2 | 0 |
| _drafts/kubernetes-migration-tutorial-basics.md | draft | pass | 15 | 0 | 0 |

Overall: 3 pass, 1 warn, 0 fail

Warnings in post/deep-dive-state/spec.md:
- Word count estimate may be too high for scope
- Missing one prerequisite link

Next: Run `/blog/post/refine` on artifacts with warnings
```

### refine.md

**Input**: Path to any post artifact (spec, outline, or draft)

**Output**: Updated artifact with `## Review` section removed

**Tools Used**:

- `Read` — load artifact and review
- `Edit` — apply changes

**Logic**:

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

7. **Reset status** → `draft` (for spec/outline)

8. **Update `updated` timestamp**

9. **Self-review** (fail items only)

10. **Update `index.md`** with status change

**Example output**:

```text
Refined: content/_drafts/kubernetes-migration-tutorial-basics.md

Changes applied:
- Added kernel version requirements to Prerequisites section
- Expanded edge case discussion in Step 3
- Adjusted Setup section (-50 words, was over estimate)
- Maintained practitioner voice throughout

Word count: 2,437 (was 2,487)
Status reset to: draft

Next: Run `/blog/post/review content/_drafts/kubernetes-migration-tutorial-basics.md`
```

---

## Slug Generation Logic

### Slug Format

For multi-phase projects: `<project-slug>-<phase-slug>.md`

Example: `kubernetes-migration-tutorial-basics.md`

### Single-Post Projects

For projects with one phase (`phase/0-main.md`): `<project-slug>.md`

Example: `ebpf-intro.md`

### Generation Rules

1. Take title from spec
2. Convert to lowercase
3. Replace spaces with hyphens
4. Remove special characters except hyphens
5. Truncate to 60 characters max
6. Prepend project slug for uniqueness

### Collision Handling

1. Generate candidate slug
2. Check if `content/_drafts/<slug>.md` exists
3. If exists and `--force` not set:
   - Error: "Draft 'kubernetes-migration-tutorial-basics.md' already exists"
   - Suggest: "Use --force to overwrite, or change the post title"
4. If `--force` set: overwrite existing draft

---

## Author Configuration

The `author` field in AstroPaper frontmatter comes from (in priority order):

1. **Project-level**: `index.md` frontmatter `author` field
2. **Plugin-level**: `.claude-plugin/plugin.json` → `author.name`
3. **Default**: `"aRustyDev"`

### Per-Project Override

```yaml
# content/_projects/<slug>/index.md
---
type: project
author: "Different Author"
---
```

### AstroPaper Frontmatter

All drafts use this structure:

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

---

## Persona Verification Dialog

When persona verification fires at `spec` start:

1. **Display current persona**:

   ```text
   This post uses persona: **Practitioner**
   (Senior engineer sharing field experience with pragmatic, battle-tested advice)
   ```

2. **Prompt options**:

   ```text
   Use this persona for the post?
   - yes: Continue with Practitioner
   - no: Proceed without persona
   - change: Select different persona
   ```

3. **Change flow** (if selected):

   ```text
   Available personas:
   1. practitioner - Senior engineer sharing field experience
   2. educator - Teacher explaining concepts clearly
   3. researcher - Academic exploring new territory

   Select persona (1-3 or slug):
   ```

4. **Update spec frontmatter** with selected persona

---

## Index.md Table Formats

### Post Artifacts Table (added by spec.md, updated by plan.md/draft.md)

```markdown
## Post Artifacts

| Phase | Spec | Outline | Draft | Status |
|-------|------|---------|-------|--------|
| [tutorial-basics](./phase/0-tutorial-basics.md) | [spec](./post/tutorial-basics/spec.md) | [outline](./post/tutorial-basics/outline.md) | [draft](../../../_drafts/kubernetes-migration-tutorial-basics.md) | approved |
| [deep-dive-state](./phase/1-deep-dive-state.md) | [spec](./post/deep-dive-state/spec.md) | - | - | spec-draft |
```

### Status Values

| Status | Meaning |
|--------|---------|
| `spec-draft` | Spec created, not yet reviewed |
| `spec-approved` | Spec approved, outline not started |
| `outline-draft` | Outline created, not yet reviewed |
| `outline-approved` | Outline approved, draft not started |
| `draft-wip` | Draft in progress |
| `in-review` | Draft under review |
| `approved` | Draft approved, ready for publish phase |

---

## Error Handling

### spec.md Errors

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Phase file doesn't exist | "Phase file not found at {{path}}" | Verify path or run content planning |
| Phase status is complete | "Phase '{{slug}}' already has a complete post" | Check post/ directory |
| Spec already exists | "Spec already exists at post/{{slug}}/spec.md. Use --force to overwrite" | Use --force flag |
| Persona not found | "Persona '{{slug}}' not found in .templates/personas/" | Create persona or select different |
| Template not found | "Outline template '{{slug}}' not found in .templates/outlines/" | Check available templates |
| Project index missing | "Project index.md not found" | Verify project structure |

### plan.md Errors

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Spec doesn't exist | "Post spec not found at {{path}}" | Run /blog/post/spec first |
| Spec not approved | "Spec status is '{{status}}'. Review and approve first, or proceed anyway?" | Approve or confirm |
| Outline already exists | "Outline exists at {{path}}. Use --force to overwrite" | Use --force flag |
| Template not found | "Template '{{slug}}' not found in .templates/outlines/" | Verify template exists |
| Word estimate mismatch | "Outline total ({{N}}) differs from spec target ({{M}}) by >10%" | Adjust estimates |

### draft.md Errors

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Outline doesn't exist | "Outline not found at {{path}}" | Run /blog/post/plan first |
| Outline not approved | "Outline status is '{{status}}'. Review first?" | Approve or confirm |
| Draft slug conflict | "Draft '{{slug}}.md' already exists. Use --force to overwrite" | Use --force or change title |
| Persona not found | "Persona '{{slug}}' not found for voice styling" | Verify persona exists |
| Drafts directory missing | "content/_drafts/ directory not found" | Run /blog/init |

### review.md Errors

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Artifact not found | "Artifact not found at {{path}}" | Verify path |
| Unknown artifact type | "Cannot determine artifact type. Expected post-spec, post-outline, or draft" | Check frontmatter |
| Checklist not found | "Review checklist not found for type '{{type}}'" | Verify checklist exists |
| Empty directory | "No post artifacts found in {{path}}" | Run /blog/post/spec first |
| Persona missing for draft | "Draft references persona '{{slug}}' but it wasn't found" | Verify persona |

### refine.md Errors

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| No feedback found | "No feedback found. Provide --feedback or run review first" | Run review or provide feedback |
| Artifact not found | "Artifact not found at {{path}}" | Verify path |
| Persona missing | "Cannot verify voice without persona '{{slug}}'" | Create or update persona reference |

---

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

---

## Entry Points

Per SPEC, post phase can be entered at:

| Scenario | Start At | Notes |
|----------|----------|-------|
| From content planning | `/blog/post/spec` | Normal flow after phase files |
| Know exactly what to write | `/blog/post/spec` | Create minimal phase first |
| Post already outlined | `/blog/post/draft` | With existing outline |

### Direct Entry Without Phase File

When entering `/blog/post/spec` without a phase file:

1. Prompt for post topic and type
2. Create minimal project structure if needed
3. Create synthetic phase file with provided details
4. Continue with spec creation

This maintains project structure consistency while allowing flexible entry.

---

## Single-Post Projects

For simple ideas that don't need decomposition:

1. Content brainstorm identifies one piece
2. `/blog/content/plan` creates single `phase/0-main.md`
3. `/blog/post/spec` creates `post/main/spec.md`
4. Normal post flow continues

The phase file is still created for consistency and traceability.

---

## Optional Extensions

### Preview Mode

`/blog/post/draft --preview` generates partial draft:

- Introduction section only
- First content section
- Displays for tone/voice verification
- User confirms before full generation

### Word Count Tracking

During draft generation, track actual vs estimated:

```text
Section word counts:
- Introduction: 195 (target: 200) ✓
- Setup: 362 (target: 350) ⚠ +3%
- Guide: 1,512 (target: 1,500) ✓
```

Warn if any section exceeds ±15% of estimate.

### Code Example Validation

After draft, optionally validate code blocks:

```text
/blog/post/draft --validate-code

Code validation:
- Example 1 (Python): ✓ syntax valid
- Example 2 (Bash): ✓ syntax valid
- Example 3 (Go): ⚠ unused import on line 3
```

---

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

---

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

### Review Checklists (3 files)

- [ ] Create `.templates/review-checklists/post-spec.md`
- [ ] Create `.templates/review-checklists/post-outline.md`
- [ ] Create `.templates/review-checklists/post-draft.md`

### Plugin Updates

- [ ] Update `plugin.json` with 5 new commands
- [ ] Update `marketplace.json` version (1.4.0 → 1.5.0)

### Testing

- [ ] Test spec: phase file → post/spec.md
- [ ] Test spec with --force overwrites existing
- [ ] Test plan: spec → post/outline.md
- [ ] Test plan with --template override
- [ ] Test plan with --force overwrites existing
- [ ] Test draft: outline → content/_drafts/<slug>.md
- [ ] Test draft with --preview generates partial
- [ ] Test draft with --force overwrites existing
- [ ] Test review on spec (auto-detect type)
- [ ] Test review on outline (auto-detect type)
- [ ] Test review on draft (auto-detect AstroPaper frontmatter)
- [ ] Test review on post/ directory (batch mode)
- [ ] Test refine on all three artifact types
- [ ] Test refine with --feedback flag
- [ ] Test persona verification dialog at spec start
- [ ] Test persona change flow
- [ ] Test voice consistency check in draft review
- [ ] Test word count tracking in draft
- [ ] Verify AstroPaper frontmatter compliance
- [ ] Verify slug generation and collision handling
- [ ] Verify author configuration hierarchy
- [ ] Verify `## Review` section appended/removed correctly
- [ ] Verify bidirectional links maintained
- [ ] Verify index.md Post Artifacts table updated
- [ ] Test all error conditions return helpful messages

---

## Acceptance Tests

- [ ] `/blog/post/spec` reads phase file → produces `post/<slug>/spec.md` with `type: post-spec`
- [ ] `/blog/post/spec --force` overwrites existing spec
- [ ] Post spec includes: audience, takeaways, prerequisites, scope, code examples
- [ ] `/blog/post/plan` produces `post/<slug>/outline.md` with `type: post-outline`
- [ ] `/blog/post/plan --template` overrides default template
- [ ] `/blog/post/plan --force` overwrites existing outline
- [ ] Outline includes: sections, word estimates, code locations, transitions
- [ ] Outline template applied correctly from spec or flag
- [ ] `/blog/post/draft` produces draft at `content/_drafts/<slug>.md`
- [ ] `/blog/post/draft --preview` generates intro + one section only
- [ ] `/blog/post/draft --force` overwrites existing draft
- [ ] Draft has valid AstroPaper frontmatter with all required fields
- [ ] Draft includes: `id` (UUIDv4), `pubDatetime`, `draft: true`, `tags`, `title`, `description`
- [ ] Draft slug follows `<project>-<phase>` format
- [ ] Draft slug collision detected and reported
- [ ] Author field populated from project, plugin, or default
- [ ] `/blog/post/review` auto-detects artifact type (spec, outline, draft)
- [ ] `/blog/post/review` on directory reviews all artifacts (batch mode)
- [ ] `/blog/post/review` evaluates against appropriate checklist
- [ ] `/blog/post/review` appends `## Review` section to artifact
- [ ] Voice consistency checked against configured persona for drafts
- [ ] Word count checked against estimates for drafts
- [ ] `/blog/post/refine` removes `## Review` section after applying fixes
- [ ] `/blog/post/refine --feedback` uses provided feedback
- [ ] `/blog/post/refine` resets status to `draft`
- [ ] Persona verification dialog fires at `spec` start
- [ ] Persona change flow works correctly
- [ ] All post artifacts tracked in `index.md` Post Artifacts table
- [ ] Bidirectional links maintained (phase ↔ spec ↔ outline)
- [ ] Single-post projects work with `post/main/` structure
- [ ] All error conditions produce helpful messages
- [ ] The full post flow (spec → plan → draft → review) completes end-to-end

---

## Dependencies

- Phase 0 (Foundation) — required for templates, rules, schemas
- Phase 2 (Persona/Template) — required for personas and outline templates
- Phase 4 (Content Planning) — optional (can create post directly from phase)

## Estimated Effort

6-7 hours

- Commands (5 files): 3 hours
- Artifact templates (2 files): 30 min
- Review checklists (3 files): 30 min
- Plugin manifest updates: 15 min
- Testing all workflows: 2 hours
