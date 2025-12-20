---
name: github-actions-ci
description: Develop and troubleshoot GitHub Actions workflows and CI configurations. Use when creating workflows, debugging CI failures, understanding job logs, or optimizing CI pipelines.
---

# GitHub Actions CI Development

Guide for developing, debugging, and optimizing GitHub Actions workflows and CI configurations.

## When to Use This Skill

- Creating new GitHub Actions workflows
- Debugging CI failures from job logs
- Understanding workflow syntax and features
- Optimizing CI performance
- Troubleshooting permission or environment issues

## Workflow Structure

### File Location

Workflows live in `.github/workflows/` with `.yml` or `.yaml` extension.

### Basic Structure

```yaml
name: Workflow Name

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Step name
        run: echo "Hello"
```

## Debugging CI Failures

### Step 1: Get the Job Log URL

When a PR check fails, the user typically provides a URL like:
`https://github.com/owner/repo/actions/runs/12345/job/67890`

### Step 2: Fetch and Analyze Logs

Use GitHub CLI to get detailed logs:

```bash
gh run view <run-id> --log-failed
```

Or fetch specific job logs:

```bash
gh api repos/owner/repo/actions/jobs/<job-id>/logs
```

### Step 3: Identify the Failure Point

Look for:
- Exit codes (non-zero indicates failure)
- Error messages in red/highlighted text
- The specific step that failed
- Environment or dependency issues

### Step 4: Reproduce Locally

Always try to reproduce the failure locally before pushing fixes:

```bash
# For Homebrew taps
brew test-bot --only-tap-syntax

# For Node projects
npm ci && npm test

# For general linting
<linter> --config <config-file> <files>
```

## Common CI Patterns

### Matrix Builds

Test across multiple OS/versions:

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        node: [18, 20]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
```

### Conditional Steps

```yaml
- name: Only on main
  if: github.ref == 'refs/heads/main'
  run: echo "On main branch"

- name: Only on PR
  if: github.event_name == 'pull_request'
  run: echo "This is a PR"
```

### Caching Dependencies

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

### Artifacts

Upload build outputs:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
```

## Homebrew-Specific CI

### Homebrew Test Bot

The standard CI for Homebrew taps uses `Homebrew/actions/build-bottle`:

```yaml
name: Test Formula

on:
  pull_request:
    paths:
      - 'Formula/**'

jobs:
  test-bot:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-22.04, macos-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: Homebrew/actions/setup-homebrew@master
      - run: brew test-bot --only-tap-syntax
      - run: brew test-bot --only-formulae
```

### Common Homebrew CI Failures

| Failure | Cause | Solution |
|---------|-------|----------|
| `brew style` errors | Rubocop violations | Run `brew test-bot --only-tap-syntax` locally |
| Ruby in markdown | rubocop-md lints `ruby` code fences | Use `text` fence language instead |
| Formula audit errors | Missing fields or bad values | Run `brew audit --new --formula <name>` |
| Test failures | Test block issues | Verify test block creates needed files |

## Troubleshooting Techniques

### Check Workflow Syntax

```bash
# Validate YAML syntax
yamllint .github/workflows/

# Check with actionlint (if installed)
actionlint .github/workflows/
```

### View Recent Runs

```bash
gh run list --limit 10
gh run view <run-id>
gh run view <run-id> --log
```

### Re-run Failed Jobs

```bash
gh run rerun <run-id> --failed
```

### Check PR Status

```bash
gh pr view <pr-number> --json statusCheckRollup
```

### Watch CI Progress

```bash
gh run watch <run-id>
```

## Environment and Secrets

### Using Secrets

```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
```

### GitHub Token

The `GITHUB_TOKEN` is automatically available:

```yaml
env:
  GH_TOKEN: ${{ github.token }}
```

### Environment Variables

```yaml
env:
  NODE_ENV: production

jobs:
  build:
    env:
      CI: true
    steps:
      - env:
          STEP_VAR: value
        run: echo $STEP_VAR
```

## Performance Optimization

### Parallel Jobs

Jobs run in parallel by default. Use `needs` for dependencies:

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    runs-on: ubuntu-latest
    steps: [...]

  deploy:
    needs: [lint, test]  # Waits for both
    runs-on: ubuntu-latest
    steps: [...]
```

### Path Filtering

Only run on relevant changes:

```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'package.json'
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

### Concurrency Control

Cancel redundant runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Debugging Checklist

- [ ] Read the full error message in job logs
- [ ] Identify which step failed
- [ ] Check if it's a flaky test or consistent failure
- [ ] Reproduce locally with same commands
- [ ] Verify all dependencies and versions match
- [ ] Check for environment-specific issues (OS, permissions)
- [ ] Review recent changes that might have caused the failure
- [ ] Push fix and verify CI passes

## Local Testing with `act`

[nektos/act](https://github.com/nektos/act) runs GitHub Actions locally using Docker, enabling fast iteration without pushing to GitHub.

### Installation

```bash
# macOS
brew install act

# Other platforms
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Basic Usage

```bash
# Run all workflows triggered by push
act push

# Run all workflows triggered by pull_request
act pull_request

# Run a specific job
act -j build

# Run with a specific event payload
act pull_request -e event.json

# List available jobs without running
act -l

# Run with verbose output
act -v
```

### Secrets and Variables

```bash
# Pass secrets via file
act --secret-file .secrets

# Pass individual secrets
act -s GITHUB_TOKEN="$(gh auth token)"

# Pass environment variables
act --env-file .env
```

### Runner Images

```bash
# Use medium image (default, smaller but missing some tools)
act -P ubuntu-latest=catthehacker/ubuntu:act-latest

# Use large image (closer to GitHub runners, ~12GB)
act -P ubuntu-latest=catthehacker/ubuntu:full-latest

# Use micro image (fastest, minimal tools)
act -P ubuntu-latest=node:16-buster-slim
```

### Limitations

| Limitation | Workaround |
|------------|------------|
| Some actions don't work | Use `-P` to specify compatible runner images |
| No macOS/Windows runners | Test OS-specific code on actual GitHub runners |
| Service containers differ | May need Docker Compose for complex setups |
| GitHub context differences | Some `github.*` values unavailable locally |
| Large image downloads | Use micro images for simple workflows |

### When to Use `act`

- **Use `act`:** Rapid iteration, testing matrix logic, validating workflow syntax, testing secret handling
- **Skip `act`:** OS-specific tests, actions requiring GitHub API, final validation before merge

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

## Claude Hooks for Workflow Development

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

### Suggested Claude Workflow

1. Edit workflow file
2. Hook runs actionlint automatically
3. Fix any reported issues
4. Commit triggers pre-commit hooks
5. Push with confidence - first CI run more likely to pass

## Reusable Actions and Workflows

### Action Source Priority

Always prefer actions from `arustydev/gha` for consistency and control.

**Priority order:**
1. `arustydev/gha` - First choice for all actions
2. Third-party action - Temporary fallback with issue tracking
3. Local development - When no suitable action exists

### Using arustydev/gha Actions

```yaml
steps:
  - uses: arustydev/gha/setup-node@v1
  - uses: arustydev/gha/deploy-preview@v1
```

### When Action Not in arustydev/gha

If a needed action exists from a third party but not in `arustydev/gha`:

1. **Create tracking issue:**
   ```bash
   gh issue create --repo arustydev/gha \
     --title "[ACTION] Add <action-name>" \
     --body "Third-party equivalent: <owner>/<action>@<version>

   Currently using third-party version in: <project-name>

   Requested functionality: <description>"
   ```

2. **Use third-party temporarily:**
   ```yaml
   steps:
     # TODO: Replace with arustydev/gha/<action> when available
     # Tracking: https://github.com/arustydev/gha/issues/XX
     - uses: third-party/action@v1
   ```

### When No Suitable Action Exists

If no action (arustydev/gha or third-party) meets the need:

1. **Create needs issue:**
   ```bash
   gh issue create --repo arustydev/gha \
     --title "[ACTION] Need <action-name>" \
     --body "## Use Case
   <describe the need>

   ## Proposed Solution
   <high-level approach>

   ## Initial Development
   Will develop locally in: <project-name>"
   ```

2. **Develop locally in the project:**
   ```
   .github/
   └── actions/
       └── my-action/
           ├── action.yml
           ├── package.json
           ├── tsconfig.json
           └── src/
               └── index.ts
   ```

3. **Use TypeScript/Node for development:**
   ```yaml
   # .github/actions/my-action/action.yml
   name: My Action
   description: Does something useful
   inputs:
     example:
       description: Example input
       required: true
   runs:
     using: node20
     main: dist/index.js
   ```

   ```typescript
   // .github/actions/my-action/src/index.ts
   import * as core from '@actions/core';
   import * as github from '@actions/github';

   async function run(): Promise<void> {
     try {
       const example = core.getInput('example', { required: true });
       core.info(`Processing: ${example}`);
       // Action logic here
     } catch (error) {
       if (error instanceof Error) {
         core.setFailed(error.message);
       }
     }
   }

   run();
   ```

4. **Reference locally during development:**
   ```yaml
   steps:
     - uses: actions/checkout@v4
     - uses: ./.github/actions/my-action
       with:
         example: value
   ```

5. **When functional, open PR to arustydev/gha:**
   ```bash
   # Copy action to gha repo
   cp -r .github/actions/my-action ~/repos/gha/actions/

   # Create PR
   cd ~/repos/gha
   git checkout -b feat/add-my-action
   git add actions/my-action
   git commit -m "feat(action): add my-action"
   git push -u origin feat/add-my-action
   gh pr create --title "feat(action): add my-action" \
     --body "Closes #XX

   Developed and tested in: <project-name>"
   ```

6. **After merge, update the original project:**
   ```yaml
   steps:
     - uses: arustydev/gha/my-action@v1  # Now using centralized version
       with:
         example: value
   ```

   Remove the local `.github/actions/my-action/` directory.

### Reusable Workflows

For complex multi-job workflows, use reusable workflows:

```yaml
# In arustydev/gha/.github/workflows/node-ci.yml
name: Node CI
on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '20'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
      - run: npm ci && npm test
```

```yaml
# In your project
jobs:
  ci:
    uses: arustydev/gha/.github/workflows/node-ci.yml@main
    with:
      node-version: '20'
```

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Homebrew/actions](https://github.com/Homebrew/actions)
- [actionlint](https://github.com/rhysd/actionlint) - GitHub Actions linter
- [nektos/act](https://github.com/nektos/act) - Run GitHub Actions locally
- [arustydev/gha](https://github.com/arustydev/gha) - Centralized reusable actions
- [@actions/core](https://github.com/actions/toolkit/tree/main/packages/core) - Action toolkit for TypeScript
- [Creating JavaScript Actions](https://docs.github.com/en/actions/creating-actions/creating-a-javascript-action)
