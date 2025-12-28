---
name: cicd-gitea-actions-dev
description: Develop and troubleshoot Gitea Actions workflows. Use when creating workflows, debugging CI failures, understanding Gitea-specific syntax differences from GitHub Actions, or migrating workflows between platforms.
---

# Gitea Actions Development

Guide for developing, debugging, and optimizing Gitea Actions workflows. Gitea Actions is largely compatible with GitHub Actions syntax but has platform-specific differences.

## When to Use This Skill

- Creating new Gitea Actions workflows
- Debugging CI failures in Gitea
- Migrating workflows from GitHub Actions to Gitea
- Understanding Gitea-specific features and limitations
- Troubleshooting runner or environment issues

## Key Differences from GitHub Actions

| Feature | GitHub Actions | Gitea Actions |
|---------|---------------|---------------|
| Workflow location | `.github/workflows/` | `.gitea/workflows/` |
| Default runner | `ubuntu-latest` | Self-hosted or `ubuntu-latest` (if configured) |
| Secrets syntax | `${{ secrets.NAME }}` | `${{ secrets.NAME }}` (same) |
| Context variables | Full `github.*` context | `gitea.*` context with some differences |
| Marketplace | actions/* available | Limited - use full URLs or self-host |

## Workflow Structure

### File Location

Workflows live in `.gitea/workflows/` with `.yml` or `.yaml` extension.

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
        run: echo "Hello from Gitea"
```

### Using GitHub Actions in Gitea

Most GitHub Actions work in Gitea. Reference them by full URL or short form:

```yaml
steps:
  # Short form (requires Gitea to be configured for GitHub)
  - uses: actions/checkout@v4

  # Full URL form (always works)
  - uses: https://github.com/actions/checkout@v4

  # Gitea-hosted action
  - uses: https://gitea.example.com/owner/action@v1
```

## Gitea-Specific Context

### Available Context Variables

```yaml
# Gitea context (similar to github.*)
${{ gitea.event_name }}        # push, pull_request, etc.
${{ gitea.ref }}               # refs/heads/main
${{ gitea.sha }}               # commit SHA
${{ gitea.repository }}        # owner/repo
${{ gitea.actor }}             # username triggering the workflow
${{ gitea.run_id }}            # workflow run ID
${{ gitea.run_number }}        # workflow run number
${{ gitea.server_url }}        # https://gitea.example.com
${{ gitea.api_url }}           # https://gitea.example.com/api/v1
```

### Secrets

```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
  # Gitea token (like GITHUB_TOKEN)
  GITEA_TOKEN: ${{ secrets.GITEA_TOKEN }}
```

## Common CI Patterns

### Matrix Builds

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest]
        go: ['1.21', '1.22']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: ${{ matrix.go }}
      - run: go test ./...
```

### Conditional Steps

```yaml
- name: Only on main
  if: gitea.ref == 'refs/heads/main'
  run: echo "On main branch"

- name: Only on PR
  if: gitea.event_name == 'pull_request'
  run: echo "This is a PR"
```

### Caching

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/go-build
      ~/go/pkg/mod
    key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}
    restore-keys: |
      ${{ runner.os }}-go-
```

### Artifacts

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
```

## Runner Configuration

### Self-Hosted Runners

Gitea primarily uses self-hosted runners via `act_runner`:

```bash
# Install act_runner
wget https://gitea.com/gitea/act_runner/releases/latest/download/act_runner-linux-amd64
chmod +x act_runner-linux-amd64

# Register runner
./act_runner-linux-amd64 register \
  --instance https://gitea.example.com \
  --token <registration-token>

# Start runner
./act_runner-linux-amd64 daemon
```

### Runner Labels

```yaml
jobs:
  build:
    runs-on: ubuntu-latest  # or custom label
    # runs-on: self-hosted   # for self-hosted runners
    # runs-on: [self-hosted, linux, x64]  # with labels
```

## Debugging CI Failures

### View Workflow Logs

In Gitea web UI:
1. Navigate to repository
2. Click "Actions" tab
3. Select the workflow run
4. Click on failed job to see logs

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Action not found | GitHub action not accessible | Use full URL or mirror action |
| Runner offline | Self-hosted runner not running | Check `act_runner` service |
| Permission denied | Missing secrets or permissions | Configure secrets in repo settings |
| Context undefined | Using `github.*` instead of `gitea.*` | Use `gitea.*` context variables |

### Reproduce Locally with act

```bash
# Install act
brew install act

# Run workflow locally
act -W .gitea/workflows/

# With specific event
act push -W .gitea/workflows/
```

## Migrating from GitHub Actions

### Step 1: Move Workflow Files

```bash
mkdir -p .gitea/workflows
cp .github/workflows/*.yml .gitea/workflows/
```

### Step 2: Update Context References

```yaml
# Before (GitHub)
if: github.ref == 'refs/heads/main'

# After (Gitea)
if: gitea.ref == 'refs/heads/main'
```

### Step 3: Update Action References

```yaml
# If Gitea can't reach GitHub actions
steps:
  # Mirror to your Gitea instance
  - uses: https://gitea.example.com/mirrors/checkout@v4

  # Or use full GitHub URL
  - uses: https://github.com/actions/checkout@v4
```

### Step 4: Configure Secrets

Re-create secrets in Gitea:
- Repository Settings > Actions > Secrets

## Environment Variables

```yaml
env:
  GLOBAL_VAR: value

jobs:
  build:
    env:
      JOB_VAR: value
    runs-on: ubuntu-latest
    steps:
      - env:
          STEP_VAR: value
        run: echo $STEP_VAR
```

## Performance Optimization

### Parallel Jobs

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    runs-on: ubuntu-latest
    steps: [...]

  deploy:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps: [...]
```

### Path Filtering

```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'go.mod'
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

### Concurrency Control

```yaml
concurrency:
  group: ${{ gitea.workflow }}-${{ gitea.ref }}
  cancel-in-progress: true
```

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
        files: ^\.gitea/workflows/
        args: [-c, .yamllint.yml]
```

## Debugging Checklist

- [ ] Check workflow is in `.gitea/workflows/` (not `.github/workflows/`)
- [ ] Verify runner is online and registered
- [ ] Check action URLs are accessible from runner
- [ ] Verify secrets are configured in Gitea
- [ ] Use `gitea.*` context instead of `github.*`
- [ ] Check runner labels match `runs-on` specification
- [ ] Review Gitea Actions logs in web UI

## References

- [Gitea Actions Documentation](https://docs.gitea.com/usage/actions/overview)
- [Gitea Actions Quickstart](https://docs.gitea.com/usage/actions/quickstart)
- [act_runner Documentation](https://gitea.com/gitea/act_runner)
- [Comparison with GitHub Actions](https://docs.gitea.com/usage/actions/comparison)
- [Migrating from GitHub](https://docs.gitea.com/usage/actions/faq#how-to-migrate-from-github-actions)
