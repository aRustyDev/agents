# Plugin Build System

Content-addressed build system for plugin component management.

## Problem

- Component duplication across plugins
- Version drift with no tracking
- Painful updates to shared components

## Solution

Extend `plugin.sources.json` with content hashes, add build-time validation, and auto-detect when sources change.

## Phases

| Phase | Name | Goal | Status |
|-------|------|------|--------|
| 0 | Research | Brainstorm and document approach | Complete |
| 1 | PoC | Hash generation and validation | Planned |
| 2 | MVP | Stale detection + one plugin migration | Planned |
| 3 | Full Build | Complete build-plugin rewrite | Planned |
| 4 | Migration | Migrate all plugins | Planned |

## Documents

| Document | Location |
|----------|----------|
| Research Findings | `docs/src/plugin-build-system-research.md` |
| Architecture Decision | `docs/src/adr/0003-plugin-build-system.md` |
| Phase Plans | `phase/*.md` |
| Tracking Issue | ai-aj5 |

## Quick Links

- [Phase 1: PoC](phase/1-poc.md)
- [Phase 2: MVP](phase/2-mvp.md)
- [Phase 3: Full Build](phase/3-full-build.md)
- [Phase 4: Migration](phase/4-migration.md)
