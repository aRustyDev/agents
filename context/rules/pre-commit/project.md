# Pre-commit Configuration

Main configuration: `.pre-commit-config.yaml`
Tool configs: `.github/pre-commit/`

## Design Principles

1. **Use public hooks where available** - Pin versions with `rev` key
2. **Explicit config paths** - Use `--config` flags to reference `.github/pre-commit/`
3. **Local hooks only when necessary** - For tools without public pre-commit repos
4. **Single Responsibility** - Each hook does one thing

## Configuration Structure

```
.pre-commit-config.yaml          # Hook definitions (pinned versions)
.github/pre-commit/
├── biome.json                   # JS/TS linting
├── cspell.json                  # Spell checking
├── ruff.toml                    # Python linting
├── rumdl.toml                   # Markdown linting
├── sqlfluff.cfg                 # SQL linting
├── yamllint.yaml                # YAML linting
└── words/                       # CSpell dictionaries
    ├── project.txt              # Project-specific terms
    └── tools.txt                # Tool/library names

.data/cache/                     # Tool caches (gitignored)
├── lychee/                      # Link checker cache
├── ruff/                        # Python linter cache
└── rumdl/                       # Markdown linter cache
```

## Hook Sources

### Public Repositories (Preferred)

| Repo | Rev | Hooks |
|------|-----|-------|
| `pre-commit/pre-commit-hooks` | v5.0.0 | check-added-large-files, trailing-whitespace, end-of-file-fixer, check-merge-conflict, check-case-conflict, detect-private-key, check-symlinks, check-executables-have-shebangs, check-json, check-yaml |
| `astral-sh/ruff-pre-commit` | v0.9.6 | ruff, ruff-format |
| `biomejs/pre-commit` | v0.6.1 | biome-check, biome-format |
| `shellcheck-py/shellcheck-py` | v0.10.0.1 | shellcheck |
| `scop/pre-commit-shfmt` | v3.10.0-1 | shfmt |
| `adrienverge/yamllint` | v1.38.0 | yamllint |
| `sqlfluff/sqlfluff` | 4.0.0 | sqlfluff-lint, sqlfluff-fix |
| `lycheeverse/lychee` | lychee-v0.18.0 | lychee |
| `rvben/rumdl-pre-commit` | v0.1.11 | rumdl |
| `aRustyDev/shellharden` | v0.1.0 | shellharden (fork with pre-commit hooks) |

### Local Hooks (Project-Specific)

| Hook | Tool | Reason |
|------|------|--------|
| cspell | cspell | Custom dictionaries in `.github/pre-commit/words/` |
| cclint | `agents plugin lint` (cclint SDK) | Claude context validation |
| brewfile-lint | ruby -c | Project-specific build file |
| justfile-check/format | just | Project-specific build file |
| json-validate | python3 | Explicit validation beyond check-json |

## Explicit Config Paths

All hooks use explicit `--config` flags where supported:

```yaml
# Ruff
args: ['--config=.github/pre-commit/ruff.toml']

# Biome
args: ['--config-path=.github/pre-commit/biome.json']

# Yamllint
args: ['--config-file=.github/pre-commit/yamllint.yaml']

# SQLFluff
args: ['--config=.github/pre-commit/sqlfluff.cfg']

# CSpell
entry: cspell lint --config .github/pre-commit/cspell.json

# Rumdl
entry: rumdl check --config .github/pre-commit/rumdl.toml
```

## Version Pinning

Always pin versions to ensure reproducible builds:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.9.6  # Pin specific version
  hooks:
    - id: ruff
```

Update versions with:

```bash
pre-commit autoupdate
```

## Running Hooks

```bash
# Install hooks
pre-commit install

# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Run manual stage hooks
pre-commit run --hook-stage manual --all-files

# Skip hooks on commit
git commit --no-verify -m "message"
```

## Stages

| Stage | When Runs | Use Case |
|-------|-----------|----------|
| `pre-commit` | On commit | Default checks |
| `manual` | Explicitly only | Fix/format commands |
| `pre-push` | On push | Slower checks |

## Adding New Hooks

1. **Check for public hook repo first** - Search GitHub for `<tool>-pre-commit` or check tool's repo for `.pre-commit-hooks.yaml`
2. **Pin the version** - Use latest stable release tag
3. **Use explicit config path** - Reference `.github/pre-commit/<config>`
4. **Fall back to local** - Only if no public repo exists

Example adding a new public hook:

```yaml
- repo: https://github.com/example/tool-pre-commit
  rev: v1.2.3
  hooks:
    - id: tool-check
      name: "category: tool check"
      args:
        - '--config=.github/pre-commit/tool.config'
```

Example adding a local hook:

```yaml
- repo: local
  hooks:
    - id: my-hook
      name: "category: description"
      entry: tool --config .github/pre-commit/tool.config
      language: system
      types: [filetype]
```

## Troubleshooting

```bash
# Clear cache
pre-commit clean

# Update hooks to latest versions
pre-commit autoupdate

# Verbose output
pre-commit run --verbose

# Run with specific files
pre-commit run --files path/to/file.py
```

## Related Rules

- `pre-commit-bash.md`: Shellcheck, shfmt, shellharden
- `pre-commit-javascript.md`: Biome configuration
- `pre-commit-markdown.md`: Rumdl configuration
- `pre-commit-python.md`: Ruff configuration
- `pre-commit-spelling.md`: CSpell configuration
- `pre-commit-sql.md`: SQLFluff configuration
- `pre-commit-yaml.md`: Yamllint configuration
- `claude-hooks.md`: Real-time Claude Code linting hooks
