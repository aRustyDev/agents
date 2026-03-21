---
id: b8d3e1f7-a2c4-4b9e-8c5d-6f0a1e3b7d2c
project:
  id: 00000000-0000-0000-0000-000000000000
title: Universal Component Registry Roadmap
status: active
---

# Universal Component Registry — Roadmap

## Milestones

| Milestone | Phase | Target | Actual | Version Bump |
|-----------|-------|--------|--------|-------------|
| Foundation interfaces + local provider | phase-1 | - | 2026-03-20 | minor (0.2.0) |
| Smithery MCP search + client config I/O | phase-2 | - | 2026-03-20 | minor (0.3.0) |
| Agent + plugin providers | phase-3a, 3b | - | 2026-03-20 | minor (0.4.0) |
| Rule + command + output_style providers | phase-3c, 3d | - | 2026-03-20 | minor (0.5.0) |
| Publish to Smithery | phase-4a | - | 2026-03-20 | minor (0.6.0) |
| Self-hosted registry | phase-4b | TBD | deferred (AD-3) | minor (0.7.0) |
| Migration + CLI wiring | phase-5 | - | 2026-03-20 | minor (0.8.0) |

## Issues

Epic: `ai-fl4` — Universal Component Registry

| ID | Phase | Status |
|----|-------|--------|
| ai-fl4.1 | Phase 1 | closed |
| ai-fl4.7 | Phase 2 | closed |
| ai-fl4.13 | Phase 3 | sub-tasks closed (ai-fl4.16-19) |
| ai-fl4.14 | Phase 4a | sub-tasks closed (ai-fl4.20-23); 4b deferred |
| ai-fl4.15 | Phase 5 | sub-tasks closed (ai-fl4.24-28) |

## MVP (Complete)

Phase 1 + Phase 2 delivered:
- Universal `Component` type covers 9 entity types
- `ComponentManager` aggregates search across providers
- `LocalProvider` works for skills
- `SmitheryProvider` searches MCP servers
- Client config I/O supports 19 AI clients (JSON/JSONC/YAML)
- Page-based pagination on all search backends
- `smithery://` URI scheme in source parser
- 281 tests, 0 failures

## Links

- Plan: `.claude/plans/universal-component-registry/PLAN.md`
- Related: Skill Management Enhancements (commit 9f8d9c0)
- Smithery CLI research: conducted 2026-03-20 via repomix analysis
- Worktree: `/private/tmp/worktrees/component-registry` on `feat/universal-component-registry`
