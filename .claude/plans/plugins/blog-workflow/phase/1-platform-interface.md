---
id: 09b45d7f-1ac5-4be3-8748-20da81378c2e
project:
  id: 6233cf65-b369-4afe-8fd9-b934b1dc8716
title: "Phase 1: Platform Interface & Astro Skill"
status: draft
related:
  depends-on: []
---

# Phase 1: Platform Interface & Astro Skill

**ID:** `phase-1`
**Dependencies:** None
**Status:** pending
**Effort:** 4-6 hours

## Objective

Extract Astro-specific knowledge into a platform skill and define the interface contract that all future platform skills must follow. This phase creates new files only — no existing files are modified.

## Success Criteria

- [ ] `skills/platforms/_interface.md` defines all required platform fields with types and descriptions
- [ ] `skills/platforms/astro/SKILL.md` exists with frontmatter containing all Astro-specific values
- [ ] `skills/platforms/astro/reference/` contains frontmatter, publishing, and paths documentation
- [ ] SKILL.md is under 200 lines (progressive disclosure)
- [ ] Astro skill can be manually loaded and provides correct AstroPaper information

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Platform interface contract | `skills/platforms/_interface.md` | Markdown with YAML schema |
| Astro platform skill | `skills/platforms/astro/SKILL.md` | Skill file with frontmatter |
| Frontmatter reference | `skills/platforms/astro/reference/frontmatter.md` | Reference doc |
| Publishing reference | `skills/platforms/astro/reference/publishing.md` | Reference doc |
| Paths reference | `skills/platforms/astro/reference/paths.md` | Reference doc |

## Tasks

- [ ] Define platform interface contract in `_interface.md` with:
  - Required fields: `name`, `display_name`, `paths.published`, `paths.build_output`, `frontmatter.*`, `commands.build`, `commands.dev`, `detection.files`
  - Field types, descriptions, and example values
  - Validation rules (e.g., paths must end with `/`)
- [ ] Create `astro/SKILL.md` with YAML frontmatter containing all Astro/AstroPaper values from the interface
- [ ] Extract AstroPaper frontmatter schema from `rules/blog-frontmatter.md` into `astro/reference/frontmatter.md`
- [ ] Extract build/deploy details from `commands/publish/validate.md` into `astro/reference/publishing.md`
- [ ] Extract directory conventions from `commands/publish/promote.md` into `astro/reference/paths.md`

## Files

**Create:**

- `content/plugins/blog-workflow/skills/platforms/_interface.md`
- `content/plugins/blog-workflow/skills/platforms/astro/SKILL.md`
- `content/plugins/blog-workflow/skills/platforms/astro/reference/frontmatter.md`
- `content/plugins/blog-workflow/skills/platforms/astro/reference/publishing.md`
- `content/plugins/blog-workflow/skills/platforms/astro/reference/paths.md`

**Modify:**

- None (this phase is additive only)
