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

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Homebrew/actions](https://github.com/Homebrew/actions)
- [actionlint](https://github.com/rhysd/actionlint) - GitHub Actions linter
