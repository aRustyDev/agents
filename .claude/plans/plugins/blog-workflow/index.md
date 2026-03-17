---
id: af74ab61-56fa-4cec-b1d6-2da98aa5ce6b
project:
  id: 6233cf65-b369-4afe-8fd9-b934b1dc8716
title: Platform Extensibility Refactoring
status: draft
tags: [plan, plugin, blog-workflow, platform-extensibility]
---

# Platform Extensibility Refactoring

**Created:** 2026-03-16
**Updated:** 2026-03-17
**Owner:** aRustyDev

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Extract Astro-specific content into platform skill | Yes | 0 Astro-specific references in core plugin commands/rules |
| 2 | Define platform interface contract | Yes | `_interface.md` exists with all required fields documented |
| 3 | Enable platform extensibility | Yes | New platform can be added by creating skill directory only |
| 4 | Maintain backward compatibility | Yes | All existing Astro workflows pass validation unchanged |
| 5 | Reduce default token usage via progressive disclosure | Yes | SKILL.md < 200 lines; reference files loaded on demand |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Platform-agnostic commands | ~85% | 100% | 7 files contain Astro-specific content |
| Platform skills | 0 | 1 (Astro) | No platform abstraction exists |
| Platform interface contract | None | Defined | No contract for new platforms |
| Platform detection | None | Auto-detect | No detection logic |
| Supported platforms | 1 (implicit Astro) | 1 (explicit Astro) | Platform is hardcoded, not configurable |

## Phases

| ID | Name | Status | Dependencies | Success Criteria |
|----|------|--------|--------------|------------------|
| phase-1 | Platform Interface & Astro Skill | pending | - | Interface contract defined; Astro skill created with progressive disclosure |
| phase-2 | Abstract Core Commands | pending | phase-1 | Commands use platform config values; Astro users see no change |
| phase-3 | Abstract Rules & Documentation | pending | phase-1 | Rules/docs are platform-neutral with platform skill references |
| phase-4 | Platform Detection & Config | pending | phase-2, phase-3 | Auto-detection works; config stored in `.blog-workflow.yaml` |
| phase-5 | Validation & Testing | pending | phase-4 | All existing workflows pass; migration guide documented |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing Astro workflows | Medium | High | Phase 5 regression testing; maintain backward compat throughout |
| Platform config file not read by agent | Medium | High | Use YAML frontmatter in skill files (agent-native); `.blog-workflow.yaml` as secondary |
| Platform detection false positives | Low | Low | Allow manual override via `--platform` flag and config file |
| Skill loading overhead | Low | Low | Progressive disclosure: SKILL.md is minimal, reference files on demand |
| Scope creep into multi-platform support | Medium | Medium | Phase 1-5 covers Astro extraction only; other platforms are future work |

## Rollback Strategy

Each phase is independently revertible:

1. **Phase 1** (skill creation): Delete `skills/platforms/` directory. No core files modified.
2. **Phase 2** (command abstraction): Revert command files to pre-refactor versions via git. Platform config values are read from skill files, so removing the abstraction just means restoring hardcoded values.
3. **Phase 3** (rules/docs): Revert rule and doc files via git.
4. **Phase 4** (detection/config): Remove detection logic from `init.md`; delete `.blog-workflow.yaml` template.
5. **Full rollback**: `git revert` the merge commit for the feature branch.

All changes are file-level modifications within the plugin directory, so rollback has no side effects on other plugins.

## Platform Config Approach

**Decision:** Platform configuration uses two complementary mechanisms:

1. **Platform skill YAML frontmatter** — The platform skill's `SKILL.md` contains all platform-specific values in its frontmatter (paths, commands, field mappings). The agent reads these when the skill is loaded.

2. **Project config file** (`.blog-workflow.yaml`) — Stores the user's platform choice and any project-level overrides. Created by `/blog/init`.

```yaml
# .blog-workflow.yaml (project root)
platform: astro
overrides:
  paths:
    published: src/content/blog/  # Override default if needed
```

**Why not `{{variable}}` substitution:** Claude Code has no template engine. Variables like `{{platform.paths.published}}` would require a preprocessing step that doesn't exist. Instead, commands reference "the active platform skill's configured path" in natural language, and the agent resolves values from the loaded skill's frontmatter at runtime.

## GAP Review Notes

### Gaps

- **No multi-platform testing**: Plan only validates Astro. Future platforms (Hugo, Next.js) need their own validation phases.
- **No CI integration**: No automated checks that commands remain platform-neutral after refactoring.
- **Edge case: no platform detected**: What happens when neither detection nor config file identifies a platform? Commands should fail with a clear message.

### Areas for Refinement

- Phase 2 task granularity: Each command file modification should be its own subtask with specific before/after examples.
- The "platform interface contract" needs concrete field validation rules, not just field names.
- Success criteria for Phase 4 ("auto-detection works") needs specific test scenarios.

### Potential Extensions

- Platform skill marketplace: Community-contributed platform skills for Hugo, Jekyll, etc.
- Platform migration command: `/blog/migrate --from astro --to hugo` using both platform skills.
- Shared test fixtures: Golden-file tests for each platform's frontmatter output.

## Notes

This plan was reviewed on 2026-03-17 and restructured from a single-file format to schema-compliant `index.md` + `phase/*.md` structure. The original file is archived at `platform-extensibility.md` in this directory.
