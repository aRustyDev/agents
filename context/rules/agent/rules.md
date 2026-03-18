---
paths:
  - "**/.claude/rules/**.md"
---

# Rules Loading Mechanics

## How Rules Work

- ALL `.md` files in `.claude/rules/` are loaded into context at session start
- Loading is unconditional; application is conditional
- Rules **with** `globs:` or `paths:` frontmatter: loaded always, applied only when working with matching files
- Rules **without** frontmatter: apply unconditionally to all contexts

## Directory Organization

- Rules in `context/rules/` are organized into category subdirectories (e.g., `pre-commit/`, `agent/`, `github/`)
- Subdirectory nesting does not affect loading — all `.md` files under `context/rules/` are discovered recursively

## Implications

- Every rule file consumes context tokens regardless of relevance
- Keep rules **concise** - verbose rules waste tokens when not applicable
- Use `globs:` frontmatter to scope rules to relevant files
- Prefer fewer, well-scoped rules over many broad ones

## Writing Good Rules

1. **Add frontmatter** with `globs:` whenever the rule is file-type-specific
2. **Be concise** - tables over prose, examples over explanations
3. **No duplication** - don't repeat content from CLAUDE.md or other rules
4. **Actionable** - rules should tell the agent what to do, not background info
5. **Test scope** - verify glob patterns match intended files only
