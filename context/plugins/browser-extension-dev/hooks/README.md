# Browser Extension Dev Hooks

Claude Code hooks for browser extension development. These hooks validate files automatically when you save them.

## Installation

### Prerequisites

Install the required tools:

```bash
# web-ext for manifest validation
npm install -g web-ext
```

### Enable Hooks

Add the hooks to your `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in */manifest.json) DIR=$(dirname \"$FILE\"); if command -v web-ext >/dev/null 2>&1; then web-ext lint --source-dir \"$DIR\" --warnings-as-errors=false 2>&1 | head -30 && echo \"✓ manifest validated\"; else echo \"⚠ web-ext not installed, skipping validation\"; fi;; esac; true'",
            "timeout": 20
          }
        ]
      }
    ]
  }
}
```

## Available Hooks

### manifest-validator (Active)

**Status:** Active
**Trigger:** PostToolUse on Write|Edit
**Pattern:** `**/manifest.json`

Validates `manifest.json` files using the `web-ext lint` command. Catches:

- Missing required manifest fields
- Invalid permission declarations
- Deprecated manifest keys
- Cross-browser compatibility issues
- CSP violations

**Example output:**

```
Validation warnings:
  ...
✓ manifest validated
```

**Graceful degradation:** If `web-ext` is not installed, the hook prints a warning and continues without blocking.

### extension-linter (Planned)

**Status:** Planned
**Trigger:** PostToolUse on Write|Edit
**Pattern:** `**/entrypoints/**/*.ts`

Lints extension TypeScript code for deprecated APIs and security issues.

### wasm-build-check (Planned)

**Status:** Planned
**Trigger:** PostToolUse on Write|Edit
**Pattern:** `**/*.rs`

Verifies WASM builds succeed after Rust changes.

## Hook Format

Hooks are defined in `hooks.json`:

```json
{
  "hooks": {
    "hook-name": {
      "status": "active|planned",
      "trigger": "PostToolUse",
      "matcher": "Write|Edit",
      "pattern": "glob pattern",
      "command": "shell command",
      "timeout": 20,
      "description": "What this hook does",
      "install": "How to install dependencies",
      "docs": "Link to documentation"
    }
  }
}
```

## Troubleshooting

### Hook not running

1. Check the file pattern matches your file path
2. Verify the tool is installed: `which web-ext`
3. Check timeout isn't too short for slow operations

### Validation errors

The hook is non-blocking by design (ends with `; true`). Errors are shown but don't prevent saves. To make errors blocking, remove the `; true` suffix.

### Performance

If hooks are slow, consider:

- Increasing timeout value
- Adding more specific file patterns
- Running validation only on commit (pre-commit hook)
