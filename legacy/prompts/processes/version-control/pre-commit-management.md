---
module: PreCommitConfiguration
scope: context
triggers: ["pre-commit", "setup hooks", "configure pre-commit", ".pre-commit-config.yaml"]
conflicts: []
dependencies: ["IssueTracking"]
priority: high
---

# Pre-commit Configuration Process

## Purpose
Ensure pre-commit hooks are properly configured for each repository, automatically catching issues before they enter version control and maintaining consistent code quality across the team.

## Trigger
- During WorkspaceSetup process
- When .pre-commit-config.yaml is missing
- When joining a new repository
- When hooks need updating

## Prerequisites
- Repository access
- Python/pip available (for pre-commit installation)
- Understanding of project languages and tools

## Steps

### Step 1: Pre-commit Detection
```
1.1 Check for existing configuration:
    Look for: .pre-commit-config.yaml
    Also check: .pre-commit-config.yml

1.2 Check for pre-commit installation:
    Run: pre-commit --version

    IF not_installed:
        Suggest: pip install pre-commit
        Or: brew install pre-commit
        Or: apt install pre-commit

1.3 Examine git hooks directory:
    Check: .git/hooks/pre-commit
    Note: Any existing custom hooks
```

### Step 2: Repository Analysis (if no config)
```
2.1 Identify languages present:
    - Check file extensions
    - Look for package files:
        * package.json → JavaScript/Node
        * requirements.txt/Pipfile → Python
        * go.mod → Go
        * Gemfile → Ruby
        * pom.xml → Java

2.2 Detect existing tools:
    - Linting configs: .eslintrc, .pylintrc
    - Formatting: .prettierrc, .black
    - Testing frameworks
    - Security tools

2.3 Review CI/CD configuration:
    - What checks run in CI?
    - Replicate locally via pre-commit
    - Ensure consistency

2.4 Check code patterns:
    - Comment style
    - Import organization
    - File structure
```

### Step 3: Configuration Proposal
```
3.1 Generate configuration based on analysis:

    For Python project:
    """
    repos:
      - repo: https://github.com/pre-commit/pre-commit-hooks
        rev: v4.5.0
        hooks:
          - id: trailing-whitespace
          - id: end-of-file-fixer
          - id: check-yaml
          - id: check-added-large-files
          - id: check-merge-conflict

      - repo: https://github.com/psf/black
        rev: 23.12.0
        hooks:
          - id: black

      - repo: https://github.com/pycqa/isort
        rev: 5.13.0
        hooks:
          - id: isort

      - repo: https://github.com/pycqa/flake8
        rev: 7.0.0
        hooks:
          - id: flake8
    """

    For JavaScript project:
    """
    repos:
      - repo: https://github.com/pre-commit/pre-commit-hooks
        rev: v4.5.0
        hooks:
          - id: trailing-whitespace
          - id: end-of-file-fixer
          - id: check-json
          - id: check-merge-conflict

      - repo: https://github.com/pre-commit/mirrors-eslint
        rev: v8.56.0
        hooks:
          - id: eslint

      - repo: https://github.com/pre-commit/mirrors-prettier
        rev: v3.1.0
        hooks:
          - id: prettier
    """

3.2 Include security hooks:
    - detect-secrets for credential scanning
    - bandit for Python security
    - safety for dependency checks

3.3 Add custom repository hooks:
    IF .pre-commit-hooks.yaml exists:
        Include local repository hooks
```

### Step 4: User Approval
```
4.1 Present configuration:
    "I've analyzed this repository and recommend the following
     pre-commit configuration:

     [Show proposed .pre-commit-config.yaml]

     This will:
     - Ensure consistent code formatting
     - Catch common errors before commit
     - Run security checks
     - Match your CI/CD pipeline

     Would you like me to set this up?"

4.2 Allow customization:
    - User can modify proposal
    - Add/remove specific hooks
    - Adjust hook configurations
    - Set custom parameters

4.3 Get explicit approval:
    - Never modify without permission
    - Explain each hook's purpose
    - Note performance impact
```

### Step 5: Installation
```
5.1 Create/update configuration file:
    Write .pre-commit-config.yaml
    Add to version control

5.2 Install pre-commit hooks:
    Run: pre-commit install

    This creates:
    - .git/hooks/pre-commit
    - Runs automatically on commit

5.3 Install hook environments:
    Run: pre-commit install --install-hooks

    This:
    - Downloads hook repositories
    - Sets up virtual environments
    - Prepares all tools

5.4 Run initial test:
    Run: pre-commit run --all-files

    This:
    - Tests all hooks work
    - Identifies existing issues
    - Validates configuration
```

### Step 6: Existing Configuration Review
```
IF configuration_exists:
    6.1 Review current hooks:
        - Check versions are recent
        - Identify missing hooks for languages
        - Look for deprecated hooks

    6.2 Analyze repository fit:
        - Do hooks match current code?
        - Any new languages added?
        - Unused hooks to remove?

    6.3 Check for updates:
        Run: pre-commit autoupdate

        This updates all hooks to latest versions

    6.4 IF improvements_found:
        Present suggestions:
        "Your pre-commit configuration could be enhanced:
         - Add X for better Python linting
         - Update Y to latest version
         - Remove Z (no Ruby files found)

         Would you like me to update it?"
```

### Step 7: Documentation
```
7.1 Update README if needed:
    Add section on pre-commit:
    """
    ## Development Setup

    This project uses pre-commit hooks. Install them with:
    ```bash
    pip install pre-commit
    pre-commit install
    ```

    Run manually with:
    ```bash
    pre-commit run --all-files
    ```
    """

7.2 Document custom hooks:
    - Explain any project-specific hooks
    - Note configuration choices
    - Link to hook documentation

7.3 Team communication:
    - Note in PR if adding hooks
    - Explain in team channel
    - Offer to help with issues
```

## Common Hook Configurations

### Universal Hooks (all projects)
```yaml
- id: trailing-whitespace
- id: end-of-file-fixer
- id: check-merge-conflict
- id: check-added-large-files
  args: ['--maxkb=1000']
- id: detect-private-key
```

### Language-Specific Hooks

#### Python
```yaml
- id: black  # Formatting
- id: isort  # Import sorting
- id: flake8  # Linting
- id: mypy  # Type checking
- id: bandit  # Security
- id: pytest  # Run tests
```

#### JavaScript/TypeScript
```yaml
- id: eslint  # Linting
- id: prettier  # Formatting
- id: tsc  # TypeScript checking
```

#### Security Hooks
```yaml
- id: detect-secrets  # Credential scanning
- id: gitguardian  # Secret detection
- id: safety  # Dependency vulnerabilities
```

## Troubleshooting

### Hook Failures
```
Problem: "Hook X failed"
Approach:
1. Run hook directly for details
2. Check hook configuration
3. Verify tool installed
4. Check file encoding
```

### Performance Issues
```
Problem: "Pre-commit takes too long"
Solutions:
1. Limit hooks to changed files
2. Skip expensive hooks for WIP commits
3. Run some hooks only in CI
4. Use --no-verify for emergencies
```

### Environment Issues
```
Problem: "Command not found"
Solutions:
1. Install in virtual environment
2. Check PATH configuration
3. Use pre-commit's environment
4. Specify full tool path
```

## Integration Points

- **Called by**: Process: WorkspaceSetup
- **Updates**: README documentation
- **Configures**: Git hooks
- **Triggers**: Process: RecurringProblemIdentification (on failures)
- **Creates**: Issues for hook problems

## Best Practices

### Do's
- ✅ Keep hooks fast (< 10 seconds total)
- ✅ Match CI/CD checks locally
- ✅ Update hooks regularly
- ✅ Document custom configurations
- ✅ Test hooks before committing config

### Don'ts
- ❌ Add slow hooks without warning
- ❌ Skip hooks habitually
- ❌ Ignore hook failures
- ❌ Commit hook config without testing
- ❌ Use overly strict configurations

Remember: Pre-commit hooks are your first line of defense against bad code. They catch issues early when they're cheapest to fix, and ensure consistent quality across your team.
