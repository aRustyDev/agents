# Markdown Linting Rules (rumdl)

Configuration: `.github/pre-commit/rumdl.toml` (symlinked to `rumdl.toml`)

## When to Modify

Modify the rumdl configuration when:
- Adding new markdown patterns that trigger false positives
- Changing line length limits
- Enabling/disabling specific markdown rules
- Excluding new directories from linting

## Key Rules Configured

| Rule | Status | Reason |
|------|--------|--------|
| MD013 | Disabled | Line length varies in documentation |
| MD041 | Disabled | Files often start with frontmatter |
| MD033 | Disabled | Inline HTML needed for formatting |
| MD057 | Disabled | Links to planned files are common |

## Pre-commit Hooks

- `rumdl-check`: Validates markdown (runs on commit)
- `rumdl-fix`: Auto-fixes issues (manual stage)

## Running Manually

```bash
# Check all markdown files
rumdl check

# Auto-fix issues
rumdl fmt

# Check specific file
rumdl check path/to/file.md
```

## Adding Exclusions

Edit `.github/pre-commit/rumdl.toml`:

```toml
[files]
exclude = [
    "existing/**",
    "new-pattern/**"
]
```
