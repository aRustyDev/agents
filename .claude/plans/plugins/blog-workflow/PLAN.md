# Blog Workflow Redesign: Implementation Plan

## Overview

Redesign the blog-workflow plugin from a linear skill pipeline into a multi-phase system with iterative review loops, project-based organization, and persona-driven voice control.

**SPEC**: `2026-03-13-blog-workflow-redesign-design.md`

## Summary

| Aspect | Description |
|--------|-------------|
| Phases | 8 (0-7) |
| Commands | 30+ across 7 command groups |
| Templates | 18 outline templates + checklists + personas |
| Hooks | 3 (frontmatter validator, index staleness, promote safety) |
| Storage | `content/_projects/`, `content/_drafts/`, `content/_templates/` |

## Phase Dependencies

```text
Phase 0: Foundation (required by all)
    │
    ├── Phase 1: Ideation Commands
    │       │
    │       └── Phase 2: Persona & Template Meta Commands
    │               │
    │               ├── Phase 3: Research Commands
    │               │       │
    │               │       └── Phase 4: Content Planning Commands
    │               │               │
    │               │               └── Phase 5: Post Commands
    │               │                       │
    │               │                       └── Phase 6: Publish Commands & Hooks
    │               │                               │
    │               │                               └── Phase 7: Plugin Packaging
```

## Phase Overview

| Phase | Name | Key Deliverables | Est. Effort |
|-------|------|------------------|-------------|
| 0 | Foundation | Directory structure, schemas, rules | 1-2h |
| 1 | Ideation | brainstorm, review, refine, draft-plan commands | 3-4h |
| 2 | Persona & Template | Meta commands, seed personas/templates | 2-3h |
| 3 | Research | spec/draft, draft, plan, review commands | 4-5h |
| 4 | Content Planning | Decomposition commands, phase files | 3-4h |
| 5 | Post | spec, plan, draft, refine, review commands | 4-5h |
| 6 | Publish & Hooks | seo-review, pre-check, promote, validate + hooks | 3-4h |
| 7 | Plugin Packaging | Marketplace plugin structure | 2-3h |

**Total estimated effort**: 22-30 hours

## Default Templates (From `/templates/`)

These 18 outline templates will be seeded into `content/_templates/outlines/`:

### Engineering & Development

- `tutorial.outline.md` - Step-by-step tutorials
- `dev-blog.outline.md` - Development blog posts
- `debug-error.outline.md` - Debugging/error resolution
- `staff-eng.outline.md` - Staff engineer perspective
- `principal-eng.outline.md` - Principal engineer perspective
- `research-eng.outline.md` - Research engineering

### Hardware & Architecture

- `computer-arch.outline.md` - Computer architecture
- `isa-design.outline.md` - ISA design
- `vlsi-eng.outline.md` - VLSI engineering
- `elec-eng.outline.md` - Electrical engineering
- `photonics.outline.md` - Photonics
- `neuromorphic.outline.md` - Neuromorphic computing
- `novel-computing.outline.md` - Novel computing paradigms

### Academic & Research

- `conference-paper-blog.outline.md` - Conference paper summaries
- `literature-review.outline.md` - Literature reviews
- `simulation-study.outline.md` - Simulation studies
- `thesis-blog.outline.md` - Thesis chapter adaptations
- `reverse-eng.outline.md` - Reverse engineering

## Individual Phase Plans

Detailed implementation plans are in `./phase/`:

- `phase/0-foundation.md`
- `phase/1-ideation.md`
- `phase/2-persona-template.md`
- `phase/3-research.md`
- `phase/4-content-planning.md`
- `phase/5-post.md`
- `phase/6-publish-hooks.md`
- `phase/7-plugin-packaging.md`

## Implementation Notes

### Incremental Value

Each phase is independently useful:

- After Phase 0: Directory structure ready for manual use
- After Phase 1: Can brainstorm and plan ideas
- After Phase 2: Personas and templates functional
- After Phase 3: Full research workflow
- After Phase 4: Content decomposition
- After Phase 5: Full post writing workflow
- After Phase 6: End-to-end publishing
- After Phase 7: Distributable plugin

### Key Design Decisions

1. **Flat project structure** - All projects at `content/_projects/<slug>/`, never nested
2. **UUIDv4 IDs** - Stable references across renames/moves
3. **Bidirectional links** - `parent`/`children` always kept in sync
4. **Human gating** - Ideation requires explicit approval before planning
5. **Self-review** - Non-review commands run light validation before output

### Migration Strategy

- Existing `posts/_research/` files remain (migration is separate task)
- Existing `content/.todo/` backlog remains as lightweight storage
- New commands are additive, do not break existing workflow
