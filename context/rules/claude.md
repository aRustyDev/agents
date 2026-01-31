---
paths:
  - "**/CLAUDE.md"
  - "**/.claude/CLAUDE.md"
  - "**/CLAUDE.local.md"
---

# CLAUDE.md Context Layering

## Problem

Multiple CLAUDE.md files exist at different levels. Duplicating content wastes context tokens and creates drift.

## Priority Order (highest to lowest)

| Priority | Location | Purpose |
|----------|----------|---------|
| 1 | `/Library/Application Support/ClaudeCode/CLAUDE.md` | Enterprise policy (immutable) |
| 2 | `./.claude/CLAUDE.md` or `./CLAUDE.md` | Project conventions |
| 3 | `./.claude/rules/*.md` | Domain-specific rules |
| 4 | `~/.claude/CLAUDE.md` | User preferences |
| 5 | `./CLAUDE.local.md` | Local overrides (gitignored) |

Files layer additively. Lower priority files extend, not replace, higher ones.

## What Goes Where

| Content | File |
|---------|------|
| Cross-project preferences (editor style, commit style) | `~/.claude/CLAUDE.md` |
| Project structure, conventions, workflows | `.claude/CLAUDE.md` |
| Domain rules (how to write justfiles, handle docs) | `.claude/rules/*.md` |
| Personal API keys, local paths, experiments | `CLAUDE.local.md` |

## Rules

- **Never duplicate** content that exists at a higher layer
- **Always extend** rather than repeat
- Use `@import` in project CLAUDE.md to reference shared content
- If content applies to ALL projects, it belongs in `~/.claude/CLAUDE.md`
- If content applies to matching files only, it belongs in `.claude/rules/` with `globs:` frontmatter
