# Context Component Build System

**Created:** 2025-02-20
**Updated:** 2025-03-16
**Owner:** Claude Code AI

Content-addressed build system for context component management with tiered distribution.

## Problem

- Component duplication across plugins
- Version drift with no tracking
- No standardized distribution for non-plugin components
- Unclear relationships between plugins, skills, commands, agents

## Solution

Implement a tiered build and distribution system:

1. **Justfile modules** for building each component type
2. **Content-addressed hashing** for tracking source changes
3. **Tiered distribution** via appropriate tools per component type
4. **Validation gates** appropriate to each tier

## Component Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: PLUGINS (Primary)                                  │
│  Distribution: plugin-marketplace                           │
│  Build: just plugin:build <name>                            │
│  Validation: Full marketplace validation, versioning        │
│  Contains: Skills, Commands, Agents, Rules, MCP configs     │
├─────────────────────────────────────────────────────────────┤
│  TIER 2: SKILLS (Secondary)                                 │
│  Distribution: npx skills (Vercel Labs) ✓                   │
│  Build: just skill:build <name>                             │
│  Validation: SKILL.md structure, allowed-tools              │
│  Contains: Commands, Agents, Rules (bundled)                │
├─────────────────────────────────────────────────────────────┤
│  TIER 3: COMMANDS & AGENTS (Tertiary)                       │
│  Distribution: Bundle into skills (no dedicated CLI exists) │
│  Build: just command:build, just agent:build                │
│  Validation: Frontmatter, markdown lint                     │
│  Contains: Self-contained                                   │
├─────────────────────────────────────────────────────────────┤
│  TIER 4: SUPPORTING COMPONENTS                              │
│  Distribution: Bundled into higher tiers                    │
│  Build: just rule:build, just mcp:build, just hook:build    │
│  Validation: Format-specific                                │
│  Types: Rules, Output Styles, MCP Configs, Hooks            │
└─────────────────────────────────────────────────────────────┘
```

> **Note:** Prompts are NOT a separate component type. Commands are "prompts with slash triggers", rules are "headless prompts", and skills are "prompts with infrastructure". Use SKILL.md `type` metadata for distinctions.

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Promotion path | None | Components are distinct, refactor not promote |
| Plugin skills | All referenced | Extract to context/skills/ first |
| Build system | Justfile modules | `just plugin:build`, `just skill:build`, etc. |
| Plugin distribution | plugin-marketplace | Established, works |
| Skill distribution | **`npx skills` (Vercel)** | 547K/week downloads, 42 agents, skills.sh registry |
| Command/Agent distribution | Bundle into skills | No dedicated CLI exists |
| Source tracking | Extend plugin.sources.json | Track skill composition |
| Prompts as component | **No** | Subsumed by skills/commands/rules |
| Skill spec | SKILL.md (agentskills.io) | Industry standard (Anthropic, OpenAI, Microsoft, Google) |

## Phases

| Phase | Name | Goal | Status |
|-------|------|------|--------|
| 0 | Research | Document approach, audit components | ✅ Complete |
| 0.5 | CLI Research | Evaluate distribution CLI options | ✅ Complete |
| 1 | PoC | Hash generation and validation | ✅ Complete |
| 2 | MVP | Stale detection + one plugin migration | ✅ Complete |
| 3 | Full Build | Complete build system with justfile modules | ✅ Complete |
| 4 | Migration | Migrate all plugins, implement skill tracking | ✅ Complete |
| 5 | Distribution Gaps | Hook distribution, cross-agent rules (optional) | Proposed |

## Documents

| Document | Location |
|----------|----------|
| Component Audit | `analysis/plugin-component-audit.md` |
| CLI Research Report | `analysis/research-report.md` |
| Architecture Decision | `docs/src/adr/0003-plugin-build-system.md` |
| Phase Plans | `phase/*.md` |

## Research Questions (Resolved)

| Question | Answer |
|----------|--------|
| Skills CLI? | **`npx skills`** (add-skill deprecated, openskills has 200x less adoption) |
| Commands/Agents/Rules CLI? | **None exists** - bundle into skills |
| Prompts as component? | **No** - subsumed by skills/commands/rules |

## Distribution Gaps (Phase 5 Candidates)

Ecosystem gaps with no existing tools:

| Gap | Impact | Build Opportunity |
|-----|--------|-------------------|
| **Hook distribution** | No way to share hook configs | High - largest ecosystem gap |
| **Cross-agent rule translation** | Different formats per agent | Medium - multi-agent teams |
| **Skill dependency resolution** | No formal dependency graph | Medium - contribute to spec |
| **AGENTS.md for Claude Code** | 3K+ GitHub upvotes, no response | Low - wait for Anthropic |

See `analysis/research-report.md` for full details.

## Quick Links

- [Phase 0: Research](phase/0-research.md) ✓
- [Phase 0.5: CLI Research](phase/0.5-cli-research.md)
- [Phase 1: PoC](phase/1-poc.md)
- [Phase 2: MVP](phase/2-mvp.md)
- [Phase 3: Full Build](phase/3-full-build.md)
- [Phase 4: Migration](phase/4-migration.md)
