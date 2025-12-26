# GitHub Actions Debugging Guide

Systematic approach to debugging failed GitHub Actions.

## Quick Diagnosis

### Step 1: Identify the Failure Type

```bash
# Get failed run details
gh run view <run-id> --log-failed
```

Parse the output to identify:

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| `Resource not accessible by integration` | Permission issue | Check `permissions:` block |
| `Error: Process completed with exit code 1` | Command failed | Check the specific command |
| `npm ERR!` / `cargo error` | Dependency issue | Check lock files, versions |
| `RequestError [HttpError]` | API rate limit or auth | Check token, add retry |
| `No space left on device` | Runner disk full | Clean up or use larger runner |
| `Timeout` | Long-running step | Increase timeout or optimize |

### Step 2: Get Full Context

```bash
# Full logs (verbose)
gh run view <run-id> --log

# Download logs for offline analysis
gh run download <run-id> --dir ./logs

# Get workflow file
gh api repos/<owner>/<repo>/contents/.github/workflows/<workflow>.yml | jq -r '.content' | base64 -d
```

### Step 3: Check Recent Changes

```bash
# Commits since last success
gh run list --status success --limit 1  # Get last success
gh log --oneline <last-success-sha>..HEAD

# Workflow file changes
git log -p -- .github/workflows/
```

## Common Issues and Fixes

### Permission Errors

**Symptom:** `Resource not accessible by integration` (403)

**Diagnosis:**
```bash
# Check what permissions are needed
gh run view <run-id> --log | grep -i "x-accepted-github-permissions"
```

**Fix:** Add explicit permissions
```yaml
permissions:
  contents: read
  issues: write
  pull-requests: write
```

**Common permission needs:**
| Operation | Permission |
|-----------|------------|
| Read code | `contents: read` |
| Push code | `contents: write` |
| Create issues | `issues: write` |
| Comment on PRs | `pull-requests: write` |
| Create releases | `contents: write` |
| Upload packages | `packages: write` |

### Dependabot PR Restrictions

**Symptom:** Workflow triggered by Dependabot fails with permission errors

**Cause:** Dependabot PRs run with restricted `GITHUB_TOKEN`

**Fix options:**
1. Use `pull_request_target` instead of `pull_request`
2. Don't try to modify Dependabot PRs
3. Use a PAT for operations requiring more permissions

```yaml
# Safe pattern for Dependabot
on:
  pull_request_target:
    types: [opened]

jobs:
  safe-job:
    if: github.actor == 'dependabot[bot]'
    permissions:
      issues: write  # Can create issues
      pull-requests: read  # Can read, but NOT write to Dependabot PRs
```

### Rate Limiting

**Symptom:** `API rate limit exceeded` or 403 with rate limit headers

**Diagnosis:**
```bash
gh api rate_limit
```

**Fix options:**
1. Cache API responses
2. Reduce API calls
3. Use GraphQL for batch queries
4. Add retry with backoff

```yaml
- uses: actions/github-script@v7
  with:
    retries: 3
    retry-exempt-status-codes: 400,401,403,404,422
```

### Dependency Failures

**Symptom:** `npm ci` or `cargo build` fails

**Diagnosis:**
```bash
# Check lock file freshness
git log -1 -- package-lock.json Cargo.lock

# Check if local build works
npm ci && npm test
cargo build --locked
```

**Common fixes:**
1. Regenerate lock file
2. Pin problematic dependency version
3. Clear cache in workflow

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      target
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
```

### Flaky Tests

**Symptom:** Tests pass locally but fail intermittently in CI

**Diagnosis:**
```bash
# Run multiple times locally
for i in {1..10}; do npm test || echo "Failed on run $i"; done
```

**Common causes:**
1. Race conditions
2. Time-dependent tests
3. Order-dependent tests
4. Network dependencies

**Fix options:**
1. Add retry to flaky step
2. Fix the underlying flakiness
3. Mark as flaky and track

```yaml
- name: Run tests
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: npm test
```

### Runner Environment Issues

**Symptom:** Works on one runner OS, fails on another

**Diagnosis:**
```bash
# Check runner info
gh run view <run-id> --log | grep -E "(runs-on|RUNNER_OS|ImageVersion)"
```

**Common fixes:**
1. Use consistent runner images
2. Add OS-specific steps
3. Use Docker for consistency

```yaml
runs-on: ubuntu-22.04  # Pin specific version, not ubuntu-latest
```

## Debugging Techniques

### Enable Debug Logging

Re-run with debug enabled:
```bash
gh run rerun <run-id> --debug
```

Or add to workflow:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

### Add Diagnostic Steps

```yaml
- name: Debug info
  if: failure()
  run: |
    echo "=== Environment ==="
    env | sort
    echo "=== Disk Space ==="
    df -h
    echo "=== Memory ==="
    free -m
    echo "=== Processes ==="
    ps aux | head -20
```

### SSH Debug Session

For persistent issues, use tmate for SSH access:

```yaml
- name: Debug via SSH
  if: failure()
  uses: mxschmitt/action-tmate@v3
  timeout-minutes: 15
```

### Local Reproduction with act

```bash
# Run workflow locally
act push -j <job-name>

# With secrets
act -s GITHUB_TOKEN="$(gh auth token)"

# With specific event
act pull_request -e event.json
```

## Debugging Checklist

- [ ] Read the full error message
- [ ] Identify which step failed
- [ ] Check if it's consistent or flaky
- [ ] Check recent changes to workflow or code
- [ ] Verify permissions are correct
- [ ] Check for environment differences
- [ ] Try reproducing locally
- [ ] Check action versions and changelogs
- [ ] Search for known issues in action repo
- [ ] Add debug logging if needed
