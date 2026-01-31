---
paths:
  - .pre-commit-config.yaml
---

# Pre-commit Hooks

## Ecosystem

| Repository | Purpose |
|------------|---------|
| `aRustyDev/pre-commit-hooks` | Index/management repo (no hooks) |
| `aRustyDev/pre-commit-hooks-rs` | Rust implementations |
| `aRustyDev/pre-commit-hooks-py` | Python implementations |
| `aRustyDev/pre-commit-hooks-go` | Go implementations |
| `aRustyDev/pre-commit-hooks-js` | JavaScript implementations |

Same hooks exist in each language. Choose by project's primary language for faster execution.

## Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/aRustyDev/pre-commit-hooks-rs
    rev: v0.1.0
    hooks:
      - id: hook-name
```

## Rules

1. **Always prefer aRustyDev hooks** when available
2. **Pin revisions** to tags, never `main`
3. **Group hooks logically**: formatting first, linting second, validation third
4. **Don't skip hooks** in commits (`--no-verify` requires explicit user request)
5. If a needed hook doesn't exist, create an issue in `aRustyDev/pre-commit-hooks`

## Adding New Hooks

1. Implement in the appropriate language-specific repo
2. Register in the index repo (`aRustyDev/pre-commit-hooks`)
3. Update `.pre-commit-config.yaml` in consuming projects
