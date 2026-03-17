---
id: a2284908-5c82-452f-b578-62f952ed3c25
project:
  id: 6233cf65-b369-4afe-8fd9-b934b1dc8716
title: "Phase 2: Abstract Core Commands"
status: draft
related:
  depends-on: [09b45d7f-1ac5-4be3-8748-20da81378c2e]
---

# Phase 2: Abstract Core Commands

**ID:** `phase-2`
**Dependencies:** phase-1
**Status:** pending
**Effort:** 3-4 hours

## Objective

Make publish commands platform-agnostic by replacing hardcoded Astro values with references to the active platform skill's configuration. Commands will instruct the agent to read platform-specific values from the loaded skill.

**Note on `init.md`:** This phase adds the `--platform <name>` argument and basic config file generation to `commands/init.md`. Phase 4 extends these same changes with auto-detection logic. Phase 4 builds incrementally on this phase's init.md modifications — it does not replace them.

## Success Criteria

- [ ] No Astro-specific paths, commands, or field names remain in core command files
- [ ] Each modified command includes a "Requires: Active platform skill" prerequisite
- [ ] Existing Astro users see identical behavior (agent resolves values from Astro skill)
- [ ] Commands fail with a clear message when no platform skill is active

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Updated promote command | `commands/publish/promote.md` | Command file |
| Updated validate command | `commands/publish/validate.md` | Command file |
| Updated pre-check command | `commands/publish/pre-check.md` | Command file |
| Updated draft command | `commands/post/draft.md` | Command file |
| Updated init command | `commands/init.md` | Command file |

## Tasks

- [ ] Update `commands/publish/promote.md`: Replace `src/data/blog/` with instruction to read `paths.published` from platform skill
- [ ] Update `commands/publish/validate.md`: Replace `astro build`/`astro dev`/`dist/` with platform skill references
- [ ] Update `commands/publish/pre-check.md`: Replace AstroPaper field names (`pubDatetime`, `modDatetime`, etc.) with platform skill frontmatter field references
- [ ] Update `commands/post/draft.md`: Remove "AstroPaper-compatible" wording; reference platform skill for frontmatter generation
- [ ] Update `commands/init.md`: Add `--platform <name>` argument; add platform detection logic; generate `.blog-workflow.yaml`
- [ ] Add graceful failure message to each command when no platform skill is loaded

## Files

**Create:**

- None

**Modify:**

- `context/plugins/blog-workflow/commands/publish/promote.md`
- `context/plugins/blog-workflow/commands/publish/validate.md`
- `context/plugins/blog-workflow/commands/publish/pre-check.md`
- `context/plugins/blog-workflow/commands/post/draft.md`
- `context/plugins/blog-workflow/commands/init.md`
