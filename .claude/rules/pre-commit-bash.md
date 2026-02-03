# Bash Linting Rules

Tools: shellcheck, shfmt, shellharden

## When to Modify Pre-commit Config

Modify `.pre-commit-config.yaml` bash hooks when:
- Changing shellcheck severity level
- Adjusting shfmt indentation or style
- Disabling shellharden security checks

## Tools Overview

| Tool | Purpose | Fix Mode |
|------|---------|----------|
| shellcheck | Bug detection, best practices | Manual fixes |
| shfmt | Formatting, consistent style | Auto-fix available |
| shellharden | Security hardening, quoting | Auto-fix available |

## Shellcheck Configuration

Current settings in `.pre-commit-config.yaml`:

```yaml
args:
  - '--severity=warning'  # error, warning, info, style
  - '--shell=bash'
```

### Common Exclusions

Add to scripts via comments:

```bash
# shellcheck disable=SC2086  # Word splitting intended
# shellcheck disable=SC2016  # Single quotes intended
```

## Shfmt Configuration

Current settings:

```yaml
args:
  - '-d'   # Diff mode (check) or '-w' (write)
  - '-i=2' # 2 space indent
  - '-ci'  # Indent switch cases
```

### Style Options

| Flag | Meaning |
|------|---------|
| `-i=N` | N spaces for indent |
| `-ci` | Indent switch cases |
| `-bn` | Binary ops at line start |
| `-sr` | Redirect ops with space |

## Shellharden Configuration

Current settings:

```yaml
args:
  - '--check'  # Check mode, no modifications
```

### Running with Fixes

```bash
# Preview changes
shellharden --suggest script.sh

# Apply changes
shellharden --replace script.sh
```

## Running Manually

```bash
# Check with shellcheck
shellcheck scripts/*.sh

# Format with shfmt
shfmt -d -i=2 -ci scripts/*.sh

# Check with shellharden
shellharden --check scripts/*.sh
```

## Pre-commit Hooks

- `shellcheck`: Bug detection (runs on commit)
- `shfmt-check`: Format check (runs on commit)
- `shfmt-fix`: Auto-format (manual stage)
- `shellharden`: Security check (runs on commit)
