# Feature Request: File-Path Scoped Hook Matchers

**Target:** [anthropics/claude-code](https://github.com/anthropics/claude-code/issues)
**Status:** Draft
**Date:** 2026-03-23

## Summary

Add a `files` field (glob pattern) to hook configuration so hooks can be scoped to specific file paths, avoiding the need for bash `case` filtering inside every hook command.

## Problem

Currently, the `matcher` field in `.claude/settings.json` hooks only matches **tool names** (`Write|Edit|MultiEdit`), not file paths. To scope a hook to specific files, every hook command must:

1. Accept `$TOOL_INPUT_FILE_PATH` as an environment variable
2. Parse the path inside bash
3. Short-circuit via `case` if the file doesn't match

This means every hook runs on every file edit and does its own path filtering:

```json
{
  "matcher": "Write|Edit|MultiEdit",
  "hooks": [{
    "type": "command",
    "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in *.py) ruff check \"$FILE\";; esac; true'"
  }]
}
```

**Consequences:**
- N hooks fire on every Write/Edit, even when N-1 are irrelevant to the file being edited
- Each hook spawns a bash process just to check a `case` pattern and exit
- Hook configuration is harder to read — the file-scope logic is buried in bash
- No way to express file scoping declaratively

## Proposed Solution

Add a `files` field (glob or regex pattern) to hook configuration:

```json
{
  "matcher": "Write|Edit|MultiEdit",
  "files": "context/plugins/**/*.json",
  "hooks": [{
    "type": "command",
    "command": "cd cli && bun run bin/agents.ts plugin validate-all --quiet"
  }]
}
```

The hook only fires when the edited file matches `files`. If `files` is omitted, the hook fires for all files (current behavior).

## Research Findings

### How We Searched

1. Searched `anthropics/claude-code` GitHub issues for: "hook matcher file path", "hook files pattern", "hook glob", "PostToolUse file filter", "hook scope file"
2. Read the official hooks documentation: [hooks.md](https://code.claude.com/docs/en/hooks.md), [hook-development SKILL.md](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/hook-development/SKILL.md), [patterns reference](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/hook-development/references/patterns.md)
3. Checked all hook-related issues (open and closed) for any discussion of file-path scoping
4. Examined the `matcher` field documentation for any undocumented features

### Undocumented `ToolName:RegexPattern` Syntax

[Issue #5314](https://github.com/anthropics/claude-code/issues/5314) reveals that a compound `ToolName:RegexPattern` syntax exists:

```json
"matcher": "Edit:.*\\.cs"
```

This format appears to filter by both tool name and file path. However:
- **Not in official documentation** — discovered through user experimentation
- **Reported as unreliable** — the issue author found hooks still didn't fire consistently
- **Issue closed as "Completed"** despite the user indicating it wasn't fully working
- **Unknown stability** — may be an internal/experimental feature not intended for public use

### No Dedicated `files`/`glob` Field

The hook configuration schema supports exactly these fields:
- `matcher` (string) — tool name pattern
- `hooks` (array) — hook definitions with `type`, `command`, `timeout`

There is no `files`, `glob`, `pattern`, `pathPattern`, `include`, `exclude`, or similar field.

### No Prior Feature Request

No one has filed a feature request specifically proposing a `files` glob field in hook configuration. This would be a **new request**.

### Related Issues (Tangential)

#### Directly Related

| Issue | Title | Status | Relevance |
|-------|-------|--------|-----------|
| [#5314](https://github.com/anthropics/claude-code/issues/5314) | PostToolUse hooks not triggering for Edit operations on .cs files | Closed (Completed) | Reveals undocumented `Edit:.*\\.cs` matcher syntax; user reports unreliable behavior |
| [#20334](https://github.com/anthropics/claude-code/issues/20334) | PostToolUse hook with tool-specific matcher runs for all tools | Closed (Not Planned) | Matcher filtering by tool name itself is buggy — hooks fire for unmatched tools |
| [#23478](https://github.com/anthropics/claude-code/issues/23478) | Path-based rules not loaded on Write tool — only on Read | Open | Demonstrates need for path-based filtering; workaround uses hooks with manual `$TOOL_INPUT_FILE_PATH` checking |

#### Indirectly Related

| Issue | Title | Status | Relevance |
|-------|-------|--------|-----------|
| [#4446](https://github.com/anthropics/claude-code/issues/4446) | Support Sequential, Conditional, and Chainable Hooks | Closed (Not Planned) | Proposes `conditions.file_exists` but not file-path matchers |
| [#9550](https://github.com/anthropics/claude-code/issues/9550) | Include Modified Files in Hook Input | Closed (Not Planned) | Requests `modified_files` array in hook input JSON |
| [#4904](https://github.com/anthropics/claude-code/issues/4904) | Centralize and Expose File Filtering Configuration | Open | Proposes `fileFiltering` in settings.json for general file discovery |
| [#30736](https://github.com/anthropics/claude-code/issues/30736) | allowedTools glob patterns never match Windows backslash paths | Open | Shows glob pattern issues in permission matchers — analogous problem space |
| [#9567](https://github.com/anthropics/claude-code/issues/9567) | Hook environment variables and $CLAUDE_TOOL_INPUT are always empty | Closed | Without working env vars, in-script file-path filtering is impossible |
| [#30810](https://github.com/anthropics/claude-code/issues/30810) | .claude-ignore — exclude files/directories from Claude's file access | Open | Related file-scope concept but for access control, not hooks |

## Recommended Configuration Schemas

### Option A: `files` glob field (Recommended)

```json
{
  "matcher": "Write|Edit|MultiEdit",
  "files": "context/plugins/**/*.json",
  "hooks": [{ "type": "command", "command": "validate-plugins.sh" }]
}
```

**Pros:**
- Familiar pattern — matches pre-commit's `files` field exactly
- Declarative — scope is visible in config, not buried in bash
- Performance — hook process is never spawned for non-matching files
- Composable — can have separate hooks for `*.py`, `*.ts`, `*.json` without shared `case` blocks

**Cons:**
- New schema field — requires Claude Code core changes
- Glob engine choice matters (minimatch, micromatch, fast-glob) — needs consistency with existing glob support
- Backwards compatibility — existing hooks without `files` must continue working (default to match-all)

### Option B: `files` regex field

```json
{
  "matcher": "Write|Edit|MultiEdit",
  "files": "context/plugins/.*\\.json$",
  "hooks": [{ "type": "command", "command": "validate-plugins.sh" }]
}
```

**Pros:**
- More powerful than glob for complex patterns
- Aligns with `matcher`'s existing regex support for tool names

**Cons:**
- Harder to read than globs for simple cases
- Easy to get wrong (regex escaping in JSON strings)
- Less familiar to most users

### Option C: Formalize `ToolName:PathRegex` compound matcher `[needs-research]`

```json
{
  "matcher": "Edit:context/plugins/.*\\.json$"
}
```

**Pros:**
- No new field — extends existing `matcher` semantics
- Already partially implemented (per #5314, though unreliable)
- Single field to express both tool and file scope

**Cons:**
- **`[needs-research]`** Current implementation is undocumented and reported as unreliable
- Harder to read — tool name and file pattern are concatenated
- Can't express "any tool on this file" without duplicating patterns (`Write:*.py|Edit:*.py|MultiEdit:*.py`)
- Doesn't support glob syntax (regex only)

### Option D: `include`/`exclude` arrays `[needs-research]`

```json
{
  "matcher": "Write|Edit|MultiEdit",
  "include": ["context/plugins/**/*.json", ".claude-plugin/**"],
  "exclude": ["**/node_modules/**"],
  "hooks": [{ "type": "command", "command": "validate-plugins.sh" }]
}
```

**Pros:**
- Most expressive — can both include and exclude
- Matches eslint/prettier configuration patterns
- Handles monorepo patterns well

**Cons:**
- **`[needs-research]`** More complex schema — may be over-engineered for most use cases
- Requires defining precedence (does exclude override include? vice versa?)
- Unclear if this complexity is warranted for hooks (vs. just `files`)

## Our Recommendation

**Option A (`files` glob field)** — simplest, most familiar, solves 95% of use cases. Falls back cleanly (no `files` = match all). Mirrors pre-commit's proven design.

If Option A is too simple for advanced cases, Option D adds include/exclude but at a complexity cost that may not be justified.

## Experiment Results (2026-03-23)

### `ToolName:PathRegex` syntax does NOT work

Tested `"matcher": "Write:.*plugin\\.json|Edit:.*plugin\\.json"` — the hook never fired. The undocumented syntax from #5314 does not work in Claude Code 2.1.78.

### `$TOOL_INPUT_FILE_PATH` env var does NOT exist

Despite being referenced in hook documentation examples, this environment variable is not set. The only Claude-related env vars available to hooks are:
- `CLAUDE_PROJECT_DIR` — project root path
- `CLAUDE_CODE_ENTRYPOINT` — how Claude Code was invoked (`cli`)

### File path IS available via stdin JSON

Hooks receive a JSON payload on stdin containing the full tool input:

```json
{
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/edited/file.txt",
    "content": "..."
  },
  "tool_response": { ... }
}
```

The file path is at `.tool_input.file_path` and must be extracted with `jq` or similar JSON parsing.

### Implication

All inline hooks using `$TOOL_INPUT_FILE_PATH` are silently broken — the variable is empty, so `case` patterns never match, and hooks never run. Only `lint-context.sh` works correctly because it reads stdin JSON.

This reinforces the need for a `files` field in hook config — the current approach of parsing stdin JSON in every hook command is fragile and verbose.

## Use Case: Our Plugin Validation Hooks

Currently we have this (12 hooks in one `case` block):

```json
{
  "matcher": "Write|Edit|MultiEdit",
  "hooks": [{
    "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in *.sh) shellcheck...;; *.py) ruff...;; *.md) rumdl...;; */plugins/*/plugin.json) validate-plugin...;; esac; true'"
  }]
}
```

With Option A, each concern gets its own scoped hook:

```json
{
  "matcher": "Write|Edit|MultiEdit",
  "files": "*.sh",
  "hooks": [{ "command": "shellcheck \"$TOOL_INPUT_FILE_PATH\"" }]
},
{
  "matcher": "Write|Edit|MultiEdit",
  "files": "context/plugins/**/*.json",
  "hooks": [{ "command": "cli/bin/validate-plugin.sh" }]
}
```

Cleaner, faster, and each hook's scope is self-documenting.
