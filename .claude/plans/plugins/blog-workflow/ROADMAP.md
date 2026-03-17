---
id: 17fe9006-e681-471a-98bd-2a734c36d871
project:
  id: 6233cf65-b369-4afe-8fd9-b934b1dc8716
title: Platform Extensibility Roadmap
status: draft
related:
  references: [af74ab61-56fa-4cec-b1d6-2da98aa5ce6b]
---

# Platform Extensibility Roadmap

## Issues

| Phase | Issue | Milestone | Status |
|-------|-------|-----------|--------|
| - | Parent: Platform Extensibility Refactoring | v3.0.0 | Not created |
| 1 | Platform Interface & Astro Skill | v3.0.0 | Not created |
| 2 | Abstract Core Commands | v3.0.0 | Not created |
| 3 | Abstract Rules & Documentation | v3.0.0 | Not created |
| 4 | Platform Detection & Config | v3.0.0 | Not created |
| 5 | Validation & Testing | v3.0.0 | Not created |

## Version Bumps

| Version | Scope | Reason |
|---------|-------|--------|
| v3.0.0 | Major | Breaking: commands now require platform skill; config file format added |

Major version bump because:
- Commands change from hardcoded Astro to platform-skill-dependent
- New `.blog-workflow.yaml` config file required
- Existing users must run `/blog/init` after upgrade

## MVP Timeline

1. **Phase 1** — Can be done independently. Creates new files only.
2. **Phase 2 + 3** — Can run in parallel after Phase 1. These modify existing files.
3. **Phase 4** — Depends on Phase 2 + 3 completing.
4. **Phase 5** — Final validation before release.

## Future Work (Post v3.0.0)

- Hugo platform skill (v3.1.0)
- Next.js MDX platform skill (v3.1.0)
- Platform migration command (v3.2.0)
- Community platform skill contributions (v4.0.0)
