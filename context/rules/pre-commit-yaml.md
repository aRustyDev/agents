# YAML Linting Rules (yamllint)

Configuration: `.github/pre-commit/yamllint.yaml`
Public hook: `https://github.com/adrienverge/yamllint` (v1.38.0)

## When to Modify

Modify `.github/pre-commit/yamllint.yaml` when:
- Changing line length limits
- Enabling/disabling specific rules
- Adding custom rule configurations

## Current Configuration

```yaml
extends: default

rules:
  line-length:
    max: 120
    level: warning
  truthy: disable
  comments:
    min-spaces-from-content: 1
  indentation:
    spaces: 2
    indent-sequences: true
  document-start: disable
```

## Key Rules

| Rule | Status | Reason |
|------|--------|--------|
| line-length | max: 120 | Allow longer lines |
| truthy | disabled | Allows `yes`, `no`, `on`, `off` |

## Pre-commit Hook

- `yamllint`: Validates YAML syntax and style (runs on commit)

## Running Manually

```bash
# Lint all YAML files
yamllint .

# Lint specific file
yamllint path/to/file.yaml

# With custom config
yamllint -d '{extends: default, rules: {line-length: disable}}' file.yaml
```

## Creating Config File

For more complex configurations, create `.yamllint.yaml`:

```yaml
extends: default

rules:
  line-length:
    max: 120
    level: warning
  truthy: disable
  comments:
    min-spaces-from-content: 1
  indentation:
    spaces: 2
    indent-sequences: true
```

Then update pre-commit hook:

```yaml
- id: yamllint
  name: "yaml: yamllint validate"
  entry: yamllint
  language: system
  types: [yaml]
  args: ['-c', '.yamllint.yaml']
```

## Common Rules to Customize

| Rule | Description |
|------|-------------|
| `document-start` | Require `---` at start |
| `document-end` | Require `...` at end |
| `key-duplicates` | Forbid duplicate keys |
| `empty-lines` | Control blank lines |
| `trailing-spaces` | Forbid trailing spaces |
