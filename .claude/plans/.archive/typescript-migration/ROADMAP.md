---
id: d90dbc2d-d7de-470f-9db2-1faa038d531f
project:
  id: 00000000-0000-0000-0000-000000000000
title: TypeScript Migration Roadmap
status: draft
tags: [roadmap, migration, typescript]
related:
  depends-on: [bcb4f31b-e0a1-4bf5-af73-d36426442250]
---

# TypeScript Migration Roadmap

## Issues

Epic: `ai-ki5`

| Phase | Issue | Milestone | Status |
|-------|-------|-----------|--------|
| phase-0 | `ai-gwm` | v0.1.0 | open |
| phase-1 | `ai-kqu` | v0.1.0 | open |
| phase-2 | `ai-ajy` | v0.1.0 | open |
| phase-3 | `ai-y5i` | v0.2.0 | open |
| phase-4a | `ai-dxg` | v0.2.0 | open |
| phase-4b | `ai-7q0` | v0.3.0 | open |
| phase-5 | `ai-5yq` | v0.3.0 | open |
| phase-6 | `ai-mpl` | v0.4.0 | open |
| phase-7 | `ai-9lh` | v1.0.0 | open |

## Milestones

| Milestone | Description | Version Bump |
|-----------|-------------|--------------|
| v0.1.0 | Foundation: scaffold + core lib + schema layer | minor |
| v0.2.0 | Plugin + skill commands migrated | minor |
| v0.3.0 | External skill tracking + registry crawler | minor |
| v0.4.0 | Knowledge graph migrated (or fallback confirmed) | minor |
| v1.0.0 | Python removed, single-runtime achieved | major |

## MVP Timeline

- **v0.1.0** — Foundation phases (0, 1, 2) must complete before any command migration
- **v0.2.0** — First user-facing value: plugin and skill commands work in TS
- **v0.3.0** — New capability: external skill tracking with drift detection
- **v0.4.0** — Highest-risk phase: KG migration or fallback decision
- **v1.0.0** — Cleanup: Python removed, brewfile/justfile/CLAUDE.md updated

## Dependencies

```
phase-0 ──→ phase-1 ──→ phase-2 ──┬──→ phase-3 ──────────────┐
                                   ├──→ phase-4a → phase-4b ──┤
                                   └──→ phase-5 ──────────────┤
                         phase-1 ──→ phase-6 ─────────────────┤
                                                               └──→ phase-7
```

Phases 3, 4a, 5 can run in parallel after Phase 2. Phase 4b depends on 4a. Phase 6 runs independently after Phase 1. Phase 7 runs after all others.
