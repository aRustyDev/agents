# Browser Extension Dev Hooks

Claude Code hooks for browser extension development. These hooks validate files automatically when you save them.

## Installation

### Prerequisites

Install the required tools:

```bash
# web-ext for manifest validation
npm install -g web-ext

# ESLint for code linting (or use biome)
npm install -D eslint eslint-plugin-webextensions

# wasm-pack for WASM build verification
cargo install wasm-pack
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

### extension-linter (Active)

**Status:** Active
**Trigger:** PostToolUse on Write|Edit
**Pattern:** `**/entrypoints/**/*.{ts,tsx,js,jsx}`

Lints extension entrypoint code for deprecated APIs, security issues, and best practices.

**Checks for:**

- Deprecated API usage (`browserAction` vs `action`)
- Unsafe `eval()` or `new Function()`
- Missing error handling on API calls
- Sync storage access patterns
- Content script isolation issues

**Example output:**

```text
/path/to/entrypoints/background.ts
  12:5  warning  Prefer 'browser.action' over deprecated 'browser.browserAction'
  45:3  error    Avoid using eval()

✓ extension linted
```

**Graceful degradation:** Falls back to Biome if ESLint not installed. If neither is available, prints a warning.

**Installation:**

```bash
npm install -D eslint eslint-plugin-webextensions
```

### wasm-build-check (Active)

**Status:** Active
**Trigger:** PostToolUse on Write|Edit
**Pattern:** `**/wasm/**/*.rs`

Verifies WASM builds succeed after Rust changes in `wasm/` directories.

**Checks for:**

- Cargo.toml validity
- wasm-bindgen compatibility
- Build errors and warnings
- Missing dependencies

**Example output:**

```text
   Compiling extension-wasm v0.1.0
    Finished dev target in 2.34s
✓ WASM build succeeded
```

**Graceful degradation:** If `wasm-pack` is not installed, prints a warning and skips the build check.

**Installation:**

```bash
cargo install wasm-pack
```

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
