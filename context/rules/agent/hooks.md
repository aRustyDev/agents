# Claude Code Hooks

Configuration: `.claude/settings.json`

## Overview

Claude hooks run automatically after file operations (Write, Edit, MultiEdit). Each hook validates the modified file based on its extension.

## Active Hooks

| Hook | File Types | Tool | Purpose |
|------|------------|------|---------|
| shellcheck | `*.sh` | shellcheck | Bash bug detection |
| shfmt | `*.sh` | shfmt | Bash formatting check |
| shellharden | `*.sh` | shellharden | Bash security hardening |
| rumdl | `*.md` | rumdl | Markdown linting |
| sql-size | `*.sql` | stat | Prevent SQL files >50MB |
| brewfile | `brewfile` | ruby -c | Brewfile syntax |
| justfile | `justfile` | just --check | Justfile syntax |
| ruff | `*.py` | ruff | Python linting |
| biome | `*.js,*.ts,*.jsx,*.tsx` | biome | JS/TS linting |
| yamllint | `*.yaml,*.yml` | yamllint | YAML validation |
| json | `*.json` | python3 | JSON syntax |
| cclint | `context/*.md,.claude/*.md` | scripts/lint-context.sh | Claude context validation |

## Hook Behavior

- Hooks run on `PostToolUse` for Write/Edit/MultiEdit operations
- Each hook uses `case` pattern matching to check file extensions
- Hooks always exit successfully (`; true`) to avoid blocking edits
- Timeout: 5-30 seconds depending on tool complexity

## Modifying Hooks

Edit `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in *.ext) tool \"$FILE\";; esac; true'",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `$TOOL_INPUT_FILE_PATH` | Path to the modified file |
| `$TOOL_INPUT_*` | Other tool input parameters |

## Disabling Hooks

To temporarily disable all hooks, rename the settings file:

```bash
mv .claude/settings.json .claude/settings.json.bak
```

## Relationship to Pre-commit

| Aspect | Claude Hooks | Pre-commit |
|--------|--------------|------------|
| When | After each file edit | Before git commit |
| Scope | Single file | All staged files |
| Blocking | Non-blocking (always succeeds) | Blocks commit on failure |
| Purpose | Immediate feedback | Gate before commit |

Both use the same underlying tools (shellcheck, ruff, etc.) from the brewfile.

## Troubleshooting

If a hook times out:
1. Check the timeout value in settings.json
2. Test the command manually with `TOOL_INPUT_FILE_PATH=<file> bash -c '<command>'`
3. Increase timeout if the tool is legitimately slow

If a hook fails silently:
1. Remove the `; true` suffix temporarily to see errors
2. Check that the tool is installed (`which <tool>`)
3. Verify the file extension pattern matches
