---
paths:
  - justfile
  - "*.just"
---

# Justfile Conventions

> **Skill**: Load `justfile-dev` for authoring, reviewing, planning, converting, or upgrading justfiles.

## Structure

```just
set shell := ["bash", "-cu"]

# Variables and configuration at top

# =============================================================================
# Section Name
# =============================================================================

# Recipe description (this becomes the doc comment)
[group('section')]
recipe-name *args:
    command {{args}}
```

## Rules

1. **Group all recipes** using `[group('name')]` - no ungrouped recipes except `default`
2. **Document every recipe** with a comment above it
3. **Use `set shell := ["bash", "-cu"]`** for safety (`-c` = command string, `-u` = error on undefined vars)
4. **Prefer parameters over env vars** for recipe inputs
5. **Keep recipes focused** - single responsibility, compose with dependencies
6. **Private helpers** start with `_` (e.g., `_ensure-tool`)
7. **Use `[confirm]`** for destructive operations

## Standard Groups

| Group | Purpose |
|-------|---------|
| `dev` | Development workflows (setup, build, fmt, check) |
| `test` | Testing commands |
| `lint` | Linting and formatting checks |
| `docs` | Documentation generation and serving |
| `docker` | Container operations |
| `release` | Release and CI workflows |
| `util` | Maintenance utilities (clean, update) |

## Modules and Imports

- Use `import? "just/<module>.just"` for optional local modules
- CDN modules: `mod name "https://just.arusty.dev/modules/<name>.just"`
- Module library lives at `aRustyDev/just` → `just.arusty.dev`

## Key Features Reference

| Feature | Syntax | Use When |
|---------|--------|----------|
| Parameters | `recipe name:` | Recipe needs input |
| Variadic | `recipe *args:` | Pass-through arguments |
| Default values | `recipe name='default':` | Optional parameters |
| Dependencies | `recipe: dep1 dep2` | Recipe requires others first |
| Conditional | `if os() == "macos" { ... }` | Platform-specific logic |
| Shebang | `#!/usr/bin/env python3` | Multi-line scripts in other languages |
| `[script]` | `[script('python3')]` | Cleaner alternative to shebang |
| `[confirm]` | `[confirm('Delete all?')]` | Destructive operations |

## Anti-Patterns

- Don't chain commands with `&&` in recipes (use separate lines or dependencies)
- Don't use `cd` (use `[working-directory]` attribute instead)
- Don't put secrets in justfiles (use env vars or `op://` URLs)
- Don't create monolithic recipes (compose from focused ones)
