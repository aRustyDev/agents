---
paths:
  - .claude/**
  - CLAUDE.md
  - CLAUDE.local.md
  - AGENT.md
  - AGENTS.md
---

# AI Context Files

## Source of Truth

`aRustyDev/ai` is the central repository for all AI context files.

Structure: `components/<type>/<name>/` where type is one of:
- `skills/` - Domain expertise and methodology
- `rules/` - Behavioral constraints and patterns
- `commands/` - Slash command definitions
- `agents/` - Agent configurations
- `hooks/` - Event-driven automations

## Local → Central Flow

1. **Develop locally** in `.claude/` during project work
2. **Stabilize** through use across sessions
3. **Generalize** by removing project-specific details
4. **PR to `aRustyDev/ai`** targeting `components/<type>/<name>/`
5. **Reference centrally** once merged

## When to Upstream

- Rule/skill is useful beyond this single project
- Content has been validated across multiple sessions
- No project-specific secrets or paths remain

## When to Keep Local

- Project-specific configuration
- Experimental rules still being refined
- Overrides of central content for this repo only
