---
name: Pre-commit Configuration Process
module_type: process
scope: context
priority: high
triggers: ["pre-commit", "setup hooks", "pre-commit config", ".pre-commit-config.yaml", "configure hooks"]
dependencies: ["core/principles.md", "processes/version-control/commit-standards.md"]
conflicts: []
version: 1.0.0
---

# Pre-commit Configuration Process

## Purpose
Configure and maintain pre-commit hooks for a repository to enforce code quality standards automatically before commits. This process ensures consistent code quality and prevents common issues from entering the codebase.

## Trigger
- Repository initialization
- First time setup on a project
- When `.pre-commit-config.yaml` is missing
- When hooks need updating

## Prerequisites
- Git repository initialized
- Python/pip available (for pre-commit framework)
- Understanding of project's code quality requirements

## Process Steps

### 1. Check Current Configuration
```bash
# Check if pre-commit is installed
command -v pre-commit || echo "pre-commit not installed"

# Check for existing config
ls -la .pre-commit-config.yaml

# Check if hooks are installed
ls -la .git/hooks/pre-commit
```

**Decision Point**:
```
Does .pre-commit-config.yaml exist?
├─ Yes → Review and update existing config
├─ No → Create new configuration
└─ Invalid → Fix or recreate
```

### 2. Install Pre-commit Framework
```bash
# Install pre-commit
pip install pre-commit

# Or with pipx (recommended)
pipx install pre-commit

# Verify installation
pre-commit --version
```

### 3. Create/Update Configuration

#### Basic Template
```yaml
# .pre-commit-config.yaml
repos:
  # Standard hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  # Language-specific hooks added based on project
```

#### Language-Specific Additions

**Python Projects**:
```yaml
  # Python formatting
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  # Import sorting
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort

  # Linting
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

**JavaScript/TypeScript Projects**:
```yaml
  # ESLint
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.(js|jsx|ts|tsx)$

  # Prettier
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
```

**Go Projects**:
```yaml
  # Go formatting
  - repo: https://github.com/golangci/golangci-lint
    rev: v1.55.2
    hooks:
      - id: golangci-lint

  # Go imports
  - repo: https://github.com/incu6us/goimports-reviser
    rev: v3.6.4
    hooks:
      - id: goimports-reviser
```

### 4. Configure Hook-Specific Settings

#### Custom Configurations
```yaml
# Example: Configure file size limit
- id: check-added-large-files
  args: ['--maxkb=1000']

# Example: Exclude files from hooks
- id: trailing-whitespace
  exclude: \.md$

# Example: Run only on specific files
- id: black
  files: ^src/
```

### 5. Install Git Hooks
```bash
# Install the git hook scripts
pre-commit install

# Install hooks for other stages (optional)
pre-commit install --hook-type pre-push
pre-commit install --hook-type pre-merge-commit
pre-commit install --hook-type commit-msg

# Verify installation
cat .git/hooks/pre-commit
```

### 6. Test Configuration
```bash
# Run against all files
pre-commit run --all-files

# Run specific hook
pre-commit run trailing-whitespace --all-files

# Test with staged files
git add .
pre-commit run
```

### 7. Handle Common Issues

#### Hook Failures
```bash
# See detailed output
pre-commit run --all-files --verbose

# Skip hooks temporarily (emergency only)
git commit --no-verify -m "Emergency fix"

# Update hooks to latest versions
pre-commit autoupdate
```

#### Performance Issues
```yaml
# Limit concurrent jobs
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: pytest
      language: system
      pass_filenames: false
      args: ["-n", "2"]  # Limit parallel execution
```

### 8. Document Configuration

Create `.pre-commit-config.yaml.md`:
```markdown
# Pre-commit Configuration

This project uses pre-commit hooks to ensure code quality.

## Setup
\`\`\`bash
pip install pre-commit
pre-commit install
\`\`\`

## Hooks Configured
- **trailing-whitespace**: Removes trailing whitespace
- **black**: Python code formatting
- **isort**: Python import sorting
- **flake8**: Python linting

## Running Manually
\`\`\`bash
pre-commit run --all-files
\`\`\`
```

## CRITICAL: Never Edit Without Permission

**IMPORTANT**: As per core principles, NEVER edit `.pre-commit-config.yaml` without explicit user confirmation. Always:

1. **Explain proposed changes**
2. **Show exact modifications**
3. **Wait for approval**
4. **Document reasoning**

Example interaction:
```
Claude: I notice the project could benefit from adding black formatter to pre-commit.
This would require adding to .pre-commit-config.yaml:

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

May I proceed with this addition?
```

## Integration Points
- Integrates with: CI/CD pipelines
- Enforces: Commit standards
- Prevents: Common code issues
- Triggers: Before each commit

## Custom Hooks

### Creating Local Hooks
```yaml
- repo: local
  hooks:
    - id: no-debug-statements
      name: Check for debug statements
      entry: bash -c 'grep -r "console.log\|debugger\|print(" --include="*.js" --include="*.py" . && exit 1 || exit 0'
      language: system
      pass_filenames: false

    - id: run-tests
      name: Run unit tests
      entry: pytest tests/unit
      language: system
      pass_filenames: false
      stages: [push]
```

### Contributing Hooks
When creating valuable custom hooks:
1. Test thoroughly
2. Generalize for reuse
3. Document usage
4. Contribute to: github.com/aRustyDev/pre-commit-hooks

## Best Practices

### DO
- ✅ Keep hooks fast (< 10 seconds total)
- ✅ Use specific file patterns
- ✅ Document each hook's purpose
- ✅ Test changes with `--all-files`
- ✅ Keep hooks updated

### DON'T
- ❌ Add slow hooks without optimization
- ❌ Skip hooks without good reason
- ❌ Modify without team agreement
- ❌ Ignore repeated failures
- ❌ Commit hook config without testing

## Troubleshooting

### Installation Issues
```bash
# Clear and reinstall
pre-commit uninstall
pre-commit clean
pre-commit install

# Check Python environment
which python
which pre-commit
```

### Hook Failures
```bash
# Debug specific hook
pre-commit run <hook-id> --verbose --all-files

# Check hook environment
pre-commit run <hook-id> --show-diff-on-failure
```

### Performance Problems
```bash
# Profile hook execution time
time pre-commit run --all-files

# Run hooks in parallel
pre-commit run --all-files -j 4
```

---
*Pre-commit hooks are the first line of defense for code quality. Configure thoughtfully and maintain rigorously.*