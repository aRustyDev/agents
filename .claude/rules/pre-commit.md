# Pre-commit Configuration

Main configuration: `.pre-commit-config.yaml`
Tool configs: `.github/pre-commit/`

## Overview

Pre-commit hooks run automatically on `git commit`. Each hook has a single responsibility (SRP design).

## Configuration Structure

```
.pre-commit-config.yaml          # Hook definitions
.github/pre-commit/
├── biome.json                   # JS/TS linting
├── cspell.json                  # Spell checking
├── ruff.toml                    # Python linting
├── rumdl.toml                   # Markdown linting
└── sqlfluff.cfg                 # SQL linting

# Symlinks in root (tools that require root config)
biome.json -> .github/pre-commit/biome.json
.cspell.json -> .github/pre-commit/cspell.json
ruff.toml -> .github/pre-commit/ruff.toml
rumdl.toml -> .github/pre-commit/rumdl.toml
.sqlfluff -> .github/pre-commit/sqlfluff.cfg
```

## Hook Categories

### File Safety
- `check-added-large-files`: Prevents files >50MB (LFS prevention)
- `detect-private-key`: Blocks accidental secret commits

### Markdown
- `rumdl-check`: Lint markdown files
- `rumdl-fix`: Auto-fix markdown (manual)
- `lychee`: Check links in markdown

### Code Quality
- `ruff-check`: Python linting
- `ruff-format-check`: Python formatting
- `biome-check`: JS/TS linting
- `shellcheck`: Bash bug detection
- `shfmt-check`: Bash formatting
- `shellharden`: Bash security

### Data Formats
- `json-validate`: JSON syntax
- `yamllint`: YAML validation
- `sqlfluff-lint`: SQL linting
- `check-json`: JSON via pre-commit-hooks
- `check-yaml`: YAML via pre-commit-hooks

### Spelling & Docs
- `cspell`: Spell checking
- `cclint`: Claude context validation

### Build Files
- `brewfile-lint`: Brewfile syntax
- `justfile-check`: Justfile syntax

### Whitespace
- `trailing-whitespace`: Remove trailing spaces
- `end-of-file-fixer`: Ensure final newline

## Running Hooks

```bash
# Install hooks
pre-commit install

# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-check --all-files

# Run manual stage hooks
pre-commit run --hook-stage manual --all-files

# Skip hooks on commit
git commit --no-verify -m "message"
```

## Adding New Hooks

Edit `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: my-hook
      name: "category: description"
      entry: command
      language: system
      types: [filetype]  # or files: 'pattern'
```

## Stages

| Stage | When Runs | Use Case |
|-------|-----------|----------|
| `pre-commit` | On commit | Default checks |
| `manual` | Explicitly only | Fix/format commands |
| `pre-push` | On push | Slower checks |

## Troubleshooting

```bash
# Clear cache
pre-commit clean

# Update hooks
pre-commit autoupdate

# Verbose output
pre-commit run --verbose
```

## Related Rules

- `pre-commit-bash.md`: Shellcheck, shfmt, shellharden
- `pre-commit-javascript.md`: Biome configuration
- `pre-commit-markdown.md`: Rumdl configuration
- `pre-commit-python.md`: Ruff configuration
- `pre-commit-spelling.md`: CSpell configuration
- `pre-commit-sql.md`: SQLFluff configuration
- `pre-commit-yaml.md`: Yamllint configuration
