# Validation Hooks Reference

Comprehensive guide for setting up pre-commit hooks and Claude Code hooks to validate GitHub Actions workflows before commit.

## Pre-commit Hooks for Workflows

Catch workflow errors before commit to reduce failed CI runs.

### actionlint Hook

The most important hook - catches syntax errors, type mismatches, and common mistakes.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/rhysd/actionlint
    rev: v1.7.4
    hooks:
      - id: actionlint
        files: ^\.github/workflows/
```

### yamllint Hook

Validates YAML structure and formatting.

```yaml
repos:
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
        files: ^\.github/workflows/
        args: [--config-file, .yamllint.yml]
```

Recommended `.yamllint.yml` for GitHub Actions:

```yaml
extends: default
rules:
  line-length:
    max: 120
  truthy:
    check-keys: false  # Allows 'on:' without quotes
  comments:
    min-spaces-from-content: 1
```

### check-yaml Hook

Basic YAML validity check.

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-yaml
        files: ^\.github/workflows/
        args: [--unsafe]  # Required for GitHub Actions syntax
```

### Complete Pre-commit Config

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-yaml
        files: ^\.github/workflows/
        args: [--unsafe]

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
        files: ^\.github/workflows/
        args: [-c, .yamllint.yml]

  - repo: https://github.com/rhysd/actionlint
    rev: v1.7.4
    hooks:
      - id: actionlint
```

### Manual Validation

```bash
# Run actionlint on all workflows
actionlint

# Run on specific file
actionlint .github/workflows/ci.yml

# With shellcheck integration (recommended)
actionlint -shellcheck=$(which shellcheck)
```

### Advanced Hook Configuration

#### Custom actionlint Configuration

Create `.actionlint.yml` for project-specific rules:

```yaml
self-hosted-runner:
  # Define custom runner labels
  labels:
    - linux-large
    - windows-gpu
    - macos-arm64

config-variables:
  # Define organization/repository config variables
  - API_URL
  - DEPLOY_ENVIRONMENT
  - NOTIFICATION_WEBHOOK

# Disable specific checks
format:
  # Disable color output in CI
  color: false
  logLevel: info

# Shellcheck configuration
shellcheck:
  # External sources are allowed
  external-sources: true
```

#### Language-Specific Validation

```yaml
# Additional hooks for different workflow types
repos:
  # Docker workflow validation
  - repo: https://github.com/hadolint/hadolint
    rev: v2.12.0
    hooks:
      - id: hadolint-docker
        files: Dockerfile

  # Helm chart validation (for deploy workflows)
  - repo: https://github.com/gruntwork-io/pre-commit
    rev: v0.1.22
    hooks:
      - id: helmlint
        files: ^charts/.*\.yaml$

  # Kubernetes manifest validation
  - repo: https://github.com/syntaqx/kube-score
    rev: v1.16.1
    hooks:
      - id: kube-score
        files: ^k8s/.*\.ya?ml$
```

## Claude Code Hooks

Configure Claude Code hooks to automatically validate workflows during development.

### Post-Edit Hook: actionlint

Run actionlint after editing workflow files.

```json
// .claude/settings.json
{
  "hooks": {
    "post_edit": [
      {
        "pattern": "^\\.github/workflows/.*\\.ya?ml$",
        "command": "actionlint",
        "description": "Lint GitHub Actions workflow"
      }
    ]
  }
}
```

### Pre-Commit Hook: Full Validation

Validate before committing workflow changes.

```json
{
  "hooks": {
    "pre_commit": [
      {
        "pattern": "^\\.github/workflows/.*\\.ya?ml$",
        "command": "actionlint && yamllint .github/workflows/",
        "description": "Validate GitHub Actions workflows"
      }
    ]
  }
}
```

### Advanced Claude Hook Configurations

#### Multi-Step Validation Hook

```json
{
  "hooks": {
    "post_edit": [
      {
        "pattern": "^\\.github/workflows/.*\\.ya?ml$",
        "command": "bash -c 'actionlint \"$1\" && yamllint \"$1\" && echo \"Workflow validation passed\"' --",
        "description": "Comprehensive workflow validation"
      }
    ]
  }
}
```

#### Conditional Hook Based on File Content

```json
{
  "hooks": {
    "post_edit": [
      {
        "pattern": "^\\.github/workflows/.*\\.ya?ml$",
        "command": "bash -c 'if grep -q \"docker\" \"$1\"; then hadolint $(find . -name Dockerfile); fi && actionlint \"$1\"' --",
        "description": "Validate workflows and Dockerfiles if Docker is used"
      }
    ]
  }
}
```

#### Hook with Custom Output Formatting

```json
{
  "hooks": {
    "post_edit": [
      {
        "pattern": "^\\.github/workflows/.*\\.ya?ml$",
        "command": "bash -c 'echo \"🔍 Validating workflow: $1\" && actionlint \"$1\" && echo \"✅ Validation complete\"' --",
        "description": "Pretty workflow validation"
      }
    ]
  }
}
```

### Suggested Claude Workflow

1. Edit workflow file
2. Hook runs actionlint automatically
3. Fix any reported issues
4. Commit triggers pre-commit hooks
5. Push with confidence - first CI run more likely to pass

### Hook Troubleshooting

#### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `actionlint: command not found` | actionlint not installed | Install: `brew install actionlint` or `go install github.com/rhysd/actionlint/cmd/actionlint@latest` |
| `yamllint: command not found` | yamllint not installed | Install: `pip install yamllint` |
| Hook fails on valid YAML | Wrong yamllint config | Use `--unsafe` flag for check-yaml hook |
| False positives from actionlint | Missing context | Create `.actionlint.yml` with project config |
| Slow hook execution | Heavy validation | Use `--fast` flag or reduce validation scope |

#### Debugging Hook Execution

```bash
# Test hooks manually
pre-commit run actionlint --files .github/workflows/ci.yml

# Verbose output
pre-commit run --verbose actionlint

# Run all hooks on all files
pre-commit run --all-files

# Skip specific hooks temporarily
SKIP=actionlint git commit -m "Skip actionlint for this commit"
```

## Integration with IDEs

### VS Code Integration

**.vscode/settings.json:**
```json
{
  "yaml.schemas": {
    "https://json.schemastore.org/github-workflow.json": [
      ".github/workflows/*.yml",
      ".github/workflows/*.yaml"
    ]
  },
  "yaml.validate": true,
  "files.associations": {
    "*.yml": "yaml",
    "*.yaml": "yaml"
  }
}
```

**.vscode/tasks.json:**
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Lint GitHub Actions",
      "type": "shell",
      "command": "actionlint",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always"
      }
    }
  ]
}
```

### Vim/Neovim Integration

**Using ALE (Asynchronous Lint Engine):**
```vim
" Add to .vimrc or init.vim
let g:ale_linters = {
\   'yaml': ['actionlint', 'yamllint'],
\}

let g:ale_fixers = {
\   'yaml': ['prettier'],
\}

" Enable fixing on save
let g:ale_fix_on_save = 1
```

### GitHub Codespaces/GitPod

**.devcontainer/devcontainer.json:**
```json
{
  "extensions": [
    "redhat.vscode-yaml",
    "github.vscode-github-actions"
  ],
  "postCreateCommand": "sudo apt-get update && curl -sSfL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash | bash"
}
```

## Continuous Integration for Hooks

### Validate Hook Configuration

```yaml
name: Validate Hooks

on: [push, pull_request]

jobs:
  validate-hooks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Install actionlint
        run: |
          curl -sSfL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash | bash
          sudo mv ./actionlint /usr/local/bin/

      - name: Run pre-commit hooks
        run: pre-commit run --all-files
```

### Hook Performance Monitoring

```yaml
- name: Benchmark hook performance
  run: |
    time pre-commit run actionlint --all-files
    time pre-commit run yamllint --all-files
```

## Cross-References

- [Pre-commit Framework Documentation](https://pre-commit.com/)
- [actionlint Documentation](https://github.com/rhysd/actionlint)
- [yamllint Documentation](https://yamllint.readthedocs.io/)
- [Claude Code Hooks Guide](https://docs.claude.ai/claude-code)