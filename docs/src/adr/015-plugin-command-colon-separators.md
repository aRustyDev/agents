# ADR-015: Plugin Command Colon Separators

**Status**: Accepted
**Date**: 2026-03-19
**Context**: Plugin command naming convention
**Deciders**: Project maintainers

## Context

Plugin commands in Claude Code use a `name` field in their YAML frontmatter to define how the command appears in slash-command discovery. During blog-workflow plugin v3.0.0 development, commands were created with `/` as the path separator (e.g., `name: blog/idea/brainstorm`). This caused 17 of 32 commands to be invisible in command discovery on the consumer side, despite loading without errors.

Investigation revealed that Claude Code uses `:` as the canonical namespace separator for plugin commands. Commands using `/` either fail to register or register inconsistently in the command discovery system.

## Decision

All plugin command `name` fields MUST use colons (`:`) as separators.

```yaml
# Required format
name: blog:idea:brainstorm

# Not allowed
name: blog/idea/brainstorm
```

### Format

```
<plugin-short-name>:<category>:<action>
```

Nested categories add additional colons: `blog:research:spec:draft`.

## Rationale

- Claude Code's internal command registry uses `:` as the namespace separator
- `/` in command names causes silent registration failures — no errors, commands just don't appear
- The `:` convention is consistent with how other plugins (homebrew, beads, context) register their commands
- Fixing blog-workflow from `/` to `:` resolved all 17 missing commands

## Consequences

- All existing plugin commands must use `:` separators in their `name` field
- Rule `plugin-command-naming.md` documents this requirement
- Plugin scaffolding templates updated to use `:` format
- blog-workflow v3.0.3 updated all 32 commands from `/` to `:`
