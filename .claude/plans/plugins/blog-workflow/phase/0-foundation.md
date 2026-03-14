# Phase 0: Foundation

## Objective

Establish storage layout, schemas, and rules — no workflow logic yet.

## Deliverables

### 1. Directory Structure

Create directories with `.gitkeep` files for git tracking:

```text
content/
├── _projects/          # All content projects
└── _drafts/            # Post drafts (shared across projects)

context/plugins/blog-workflow/
├── commands/           # Workflow command files
│   ├── idea/
│   ├── research/
│   ├── content/
│   ├── post/
│   ├── publish/
│   ├── persona/
│   └── template/
├── hooks/              # Hook scripts
├── rules/              # Rules files
└── .templates/         # Reusable assets
    ├── personas/       # Authorial voice definitions
    ├── outlines/       # Post structure templates
    ├── research-plans/ # Research methodology templates
    ├── review-checklists/ # Review criteria
    ├── brainstorm-plans/  # Brainstorming templates
    └── schemas/        # Frontmatter schema documentation
```

**Creation script**:

```bash
# Content directories
mkdir -p content/{_projects,_drafts}
touch content/{_projects,_drafts}/.gitkeep

# Plugin directories
mkdir -p context/plugins/blog-workflow/{commands/{idea,research,content,post,publish,persona,template},hooks,rules}
mkdir -p context/plugins/blog-workflow/.templates/{personas,outlines,research-plans,review-checklists,brainstorm-plans,schemas}
touch context/plugins/blog-workflow/{hooks,rules}/.gitkeep
touch context/plugins/blog-workflow/.templates/{personas,outlines,research-plans,review-checklists,brainstorm-plans,schemas}/.gitkeep
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

### 3. Blog Frontmatter Rules

Create `context/plugins/blog-workflow/rules/blog-frontmatter.md`:

```markdown
# Blog Frontmatter Rules

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUIDv4 | Stable artifact identifier (auto-generated) |
| `title` | string | Post title (max 60 chars for SEO) |
| `description` | string | Summary (150-160 chars for SEO) |
| `pubDatetime` | ISO 8601 | Publication datetime with timezone |
| `tags` | string[] | At least one tag required |

## Optional Fields with Defaults

| Field | Default | Description |
|-------|---------|-------------|
| `modDatetime` | null | Last modification datetime |
| `author` | "aRustyDev" | Author name (configurable per-project) |
| `featured` | false | Show on homepage |
| `draft` | true | Exclude from build until promoted |
| `ogImage` | "" | Open Graph image path |
| `canonicalURL` | "" | Canonical URL if cross-posted |
| `hideEditPost` | false | Hide edit link |
| `timezone` | "America/New_York" | Timezone for datetime display |

## Common Mistakes

| Wrong | Correct | Notes |
|-------|---------|-------|
| `date:` | `pubDatetime:` | AstroPaper uses pubDatetime |
| `image:` | `ogImage:` | AstroPaper naming convention |
| `canonical:` | `canonicalURL:` | AstroPaper naming convention |
| `type:` | (remove) | Not in AstroPaper schema |

## Field Validation

- `id` must be valid UUIDv4 (generate with `crypto.randomUUID()`)
- `pubDatetime` must be ISO 8601 with timezone (e.g., `2026-03-14T12:00:00Z`)
- `description` should not exceed 160 characters
- `title` should not exceed 60 characters for SEO optimization

## Configuration

### Author

Default: `aRustyDev` — can be overridden in project frontmatter or future config.

### Timezone

Default: `America/New_York` — hardcoded for consistency across all posts.
```

### 4. Index Update Rules

Create `context/plugins/blog-workflow/rules/blog-index-updates.md`:

```markdown
# Index.md Update Rules

**Every command that creates or modifies an artifact MUST update `index.md`.**

## Required Updates

| Action | Update |
|--------|--------|
| Create artifact | Add row to Artifacts table |
| Change artifact status | Update status column in Artifacts table |
| Create phase | Add row to Phases table |
| Create child project | Add row to Related Projects table |
| Change project phase | Update `status` in frontmatter |

## Read-Modify-Write Pattern

Commands must:

1. Read `index.md` at start to understand project state
2. Perform work and create/modify artifacts
3. Write back `index.md` with all updates at end

Never skip the index update — it's the project's source of truth.

## Table Formats

### Artifacts Table

| Artifact | Status | Path |
|----------|--------|------|
| Idea | approved | ./idea.md |
| Plan | draft | ./plan.md |

### Phases Table

| # | Title | Type | Status | Link |
|---|-------|------|--------|------|
| 0 | eBPF Tutorial | tutorial | draft | ./phase/0-tutorial-ebpf.md |
| 1 | Tracing Deep-Dive | deep-dive | pending | ./phase/1-tracing-deep-dive.md |

### Related Projects Table

| Project | Relationship | Path |
|---------|-------------|------|
| tutorial-ebpf | child | content/_projects/tutorial-ebpf/index.md |
| llm-observability | parent | content/_projects/llm-observability/index.md |
```

### 5. Self-Review Standard

Create `context/plugins/blog-workflow/rules/blog-self-review.md`:

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

After `brainstorm.md` creates an idea:

1. Load `idea.md` checklist
2. Check each criterion
3. If "Scope is achievable" fails → report and set status: `draft`
4. If "Unique angle" is warning-level → ignore (human will check in review)
```

### 6. Index.md Template

Create `context/plugins/blog-workflow/.templates/project-index.md`:

```markdown
---
type: project
title: "{{project title}}"
status: ideation
persona: null
created: {{ISO 8601}}
updated: {{ISO 8601}}
---

<!-- Template placeholders like {{title}} are filled by Claude during artifact creation -->

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

**Project Status Values**:

| Status | Description |
|--------|-------------|
| `ideation` | Idea phase active |
| `research` | Research phase active |
| `content-planning` | Content decomposition active |
| `post` | Post writing active |
| `publish` | Publish phase active |
| `complete` | All phases done, all posts published |
| `paused` | Work suspended (add note in README) |

**Note**: `persona` is optional — can be set during brainstorm or later phases.

### 7. Project README Template

Create `context/plugins/blog-workflow/.templates/project-readme.md`:

```markdown
# {{title}}

> {{one-line description}}

<!-- Template placeholders like {{title}} are filled by Claude during artifact creation -->

## Status

**Phase**: {{status}}
**Persona**: {{persona or "not set"}}

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

### 8. Brainstorm Plan Template

Create `context/plugins/blog-workflow/.templates/brainstorm-plans/standard.md`:

```markdown
---
type: template
name: Standard Brainstorm Plan
applies_to: brainstorm
---

<!-- Template placeholders like {{topic}} are filled by Claude during artifact creation -->

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

### 9. Artifact Frontmatter Schema

Create `context/plugins/blog-workflow/.templates/schemas/artifact-schema.md`:

````markdown
# Artifact Frontmatter Schema

This documents the frontmatter structure for all blog workflow artifacts.
Commands reference this for consistency — it's documentation, not machine-parseable.

## Artifact Frontmatter

```yaml
---
id: <UUIDv4>                    # Required - stable identifier, never changes
type: <artifact type>           # Required - see types below
status: draft | in-review | approved | complete
parent: <relative path>         # Optional - link to parent artifact
children:                       # Optional - links to child artifacts
  - <relative path>
persona: <persona slug>         # Optional - authorial voice
template: <template slug>       # Optional - structural template used
created: <ISO 8601>             # Required - creation timestamp
updated: <ISO 8601>             # Required - last modification timestamp
---
```

## Artifact Types

| Type | Description | Created By |
|------|-------------|------------|
| `idea` | Brainstormed concept | `idea/brainstorm` |
| `plan` | Project plan | `idea/draft-plan` |
| `research-plan` | Research specification | `research/spec/draft` |
| `research-findings` | Raw research output | `research/draft` |
| `analysis` | Synthesized analysis | `research/plan` |
| `report` | Final research report | `research/review` |
| `content-brainstorm` | Content phase brainstorm output | `content/draft` |
| `phase` | Single content piece plan | `content/plan` |
| `post-spec` | Post specification | `post/spec` |
| `post-outline` | Structural outline | `post/plan` |
| `draft` | Full post draft | `post/draft` |

## Status Values

| Status | Description |
|--------|-------------|
| `draft` | Initial state, being worked on |
| `in-review` | Review command has been run |
| `approved` | Review passed, ready for next phase |
| `complete` | Finalized, no further changes expected |
````

### 10. Linking Rules

Create `context/plugins/blog-workflow/.templates/schemas/linking-rules.md`:

```markdown
# Linking Rules

## Bidirectional Links

- `parent` and `children` are ALWAYS bidirectional
- When adding a parent link, update the parent's children array
- When adding a child link, update the child's parent field

## Cross-Project Links

| From | To | Link Format |
|------|-----|-------------|
| Phase file | Child project | `children: [content/_projects/<child-slug>/index.md]` |
| Child index | Parent phase | `parent: content/_projects/<parent-slug>/phase/<N>-<slug>.md` |

## Path Conventions

- **Within project**: Use relative paths (`./idea.md`, `./phase/0-tutorial.md`)
- **Cross-project**: Use paths from `content/` root (`content/_projects/<slug>/index.md`)

## Rules

1. Projects are ALWAYS flat at `content/_projects/` — never nested in each other
2. Child projects are peers, not subdirectories
3. Graph relationships live in frontmatter, not directory structure
```

### 11. Validation Script (Optional)

Create `.scripts/validate-blog-structure.sh`:

```bash
#!/bin/bash
# Validates blog workflow directory structure exists

DIRS=(
  "content/_projects"
  "content/_drafts"
  "context/plugins/blog-workflow/commands"
  "context/plugins/blog-workflow/hooks"
  "context/plugins/blog-workflow/rules"
  "context/plugins/blog-workflow/.templates/personas"
  "context/plugins/blog-workflow/.templates/outlines"
  "context/plugins/blog-workflow/.templates/research-plans"
  "context/plugins/blog-workflow/.templates/review-checklists"
  "context/plugins/blog-workflow/.templates/brainstorm-plans"
  "context/plugins/blog-workflow/.templates/schemas"
)

MISSING=0
for dir in "${DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "Missing: $dir"
    MISSING=$((MISSING + 1))
  fi
done

if [ $MISSING -eq 0 ]; then
  echo "All directories present"
  exit 0
else
  echo "Missing $MISSING directories"
  exit 1
fi
```

## Tasks

### Directory Setup

- [ ] Run directory creation script (creates all directories + .gitkeep files)

### Schema Update

- [ ] Update `src/content.config.ts` with optional `id` field
- [ ] Verify `astro build` succeeds

### Rules Files

- [ ] Create `context/plugins/blog-workflow/rules/blog-frontmatter.md`
- [ ] Create `context/plugins/blog-workflow/rules/blog-index-updates.md`
- [ ] Create `context/plugins/blog-workflow/rules/blog-self-review.md`

### Templates

- [ ] Create `context/plugins/blog-workflow/.templates/project-index.md`
- [ ] Create `context/plugins/blog-workflow/.templates/project-readme.md`
- [ ] Create `context/plugins/blog-workflow/.templates/brainstorm-plans/standard.md`

### Schema Documentation

- [ ] Create `context/plugins/blog-workflow/.templates/schemas/artifact-schema.md`
- [ ] Create `context/plugins/blog-workflow/.templates/schemas/linking-rules.md`

### Validation (Optional)

- [ ] Create `.scripts/validate-blog-structure.sh`
- [ ] Make script executable (`chmod +x`)

## Acceptance Tests

### Directory Structure

- [ ] All directories exist under `content/` and `context/plugins/blog-workflow/`
- [ ] Each directory contains `.gitkeep` file where needed
- [ ] Validation script passes (if created)

### Schema Update

- [ ] `astro build` succeeds with schema change
- [ ] Existing blog post with added `id: "<valid-uuid>"` passes validation
- [ ] Existing blog post without `id` field still passes (field is optional)

### Rules Files

- [ ] `context/plugins/blog-workflow/rules/blog-frontmatter.md` loads in Claude Code rules context
- [ ] `context/plugins/blog-workflow/rules/blog-index-updates.md` loads in Claude Code rules context
- [ ] `context/plugins/blog-workflow/rules/blog-self-review.md` loads in Claude Code rules context
- [ ] Frontmatter rules document all required and optional fields
- [ ] Index update rules document all table formats

### Templates

- [ ] `project-index.md` includes all 7 project status values
- [ ] `project-readme.md` has all placeholder sections
- [ ] `brainstorm-plans/standard.md` has valid frontmatter
- [ ] Templates include placeholder documentation comment

### Schema Documentation

- [ ] `artifact-schema.md` documents all 11 artifact types
- [ ] `artifact-schema.md` documents all 4 status values
- [ ] `linking-rules.md` documents bidirectional linking requirement

### Integration Test

- [ ] Create test project at `content/_projects/_test/`
- [ ] Test project has valid `index.md` using template
- [ ] Test project has minimal `idea.md` with valid frontmatter
- [ ] Delete test project after validation

## Migration Notes

Existing content locations (NOT migrated in this phase):

| Current | Future | Notes |
|---------|--------|-------|
| `posts/_research/` | `content/_projects/<slug>/research/` | Migration tracked separately |
| `content/.todo/` | Remains as lightweight backlog | Ideas become projects when actively worked |

## Dependencies

None (this is the foundation phase).

## Estimated Effort

2-3 hours

- Directory creation + .gitkeep: 15 min
- Schema update + testing: 30 min
- 3 rules files with full content: 45 min
- 4 template files: 30 min
- 2 schema documentation files: 20 min
- Acceptance testing: 30 min
