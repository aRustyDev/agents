# Python Linting Rules (ruff)

Configuration: `.github/pre-commit/ruff.toml` (symlinked to `ruff.toml`)

## When to Modify

Modify the ruff configuration when:
- Changing Python version target
- Enabling/disabling linting rules
- Adding per-file rule ignores
- Adjusting import sorting behavior

## Key Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `target-version` | py311 | Python 3.11 compatibility |
| `line-length` | 100 | Max line length |
| `lint.select` | Multiple | Enabled rule categories |

## Enabled Rule Categories

- `E`, `W`: pycodestyle (errors, warnings)
- `F`: Pyflakes
- `I`: isort (import sorting)
- `B`: flake8-bugbear
- `UP`: pyupgrade
- `SIM`: simplify
- `PTH`: pathlib usage
- `RUF`: ruff-specific

## Pre-commit Hooks

- `ruff-check`: Lints and auto-fixes (runs on commit)
- `ruff-format-check`: Checks formatting (runs on commit)
- `ruff-format-fix`: Applies formatting (manual stage)

## Running Manually

```bash
# Check and fix
ruff check --fix scripts/

# Format
ruff format scripts/

# Check only
ruff check scripts/ --no-fix
```

## Per-File Ignores

Edit `.github/pre-commit/ruff.toml`:

```toml
[lint.per-file-ignores]
"scripts/**/*.py" = ["T201"]  # Allow print
"tests/**/*.py" = ["S101"]    # Allow assert
```
