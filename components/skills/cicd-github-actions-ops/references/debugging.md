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

## Advanced Debugging Techniques

### Workflow Performance Analysis

```bash
# Analyze slow-running workflows
gh run list --limit 20 --json workflowName,startedAt,updatedAt,displayTitle | \
    jq -r '.[] | [.workflowName, (.updatedAt | fromdateiso8601) - (.startedAt | fromdateiso8601), .displayTitle] | @tsv' | \
    sort -nrk2 | head -10
```

### Job Dependency Analysis

```bash
# Visualize job dependencies in complex workflows
grep -A 20 "needs:" .github/workflows/*.yml | \
    grep -E "(needs:|name:)" | \
    paste - - | \
    column -t
```

### Matrix Job Failure Patterns

```bash
# Find which matrix combinations fail most often
gh run list --status failure --limit 100 --json displayTitle | \
    jq -r '.[].displayTitle' | \
    grep -oE '\([^)]+\)' | \
    sort | uniq -c | sort -nr
```

### Secret and Environment Variable Debug

```yaml
- name: Debug secrets (safely)
  run: |
    echo "Available secrets:"
    env | grep -E '^[A-Z_]+=' | grep -v TOKEN | head -10
    echo "Context info:"
    echo "Repository: ${{ github.repository }}"
    echo "Event: ${{ github.event_name }}"
    echo "Actor: ${{ github.actor }}"
    echo "Ref: ${{ github.ref }}"
```

### Artifact Analysis

```bash
# Download and analyze build artifacts
gh run download <run-id>
find . -name "*.log" -exec echo "=== {} ===" \; -exec head -50 {} \;
```

### Container/Docker Issues

```yaml
- name: Debug Docker environment
  if: failure()
  run: |
    echo "=== Docker Info ==="
    docker --version
    docker system df
    echo "=== Running Containers ==="
    docker ps -a
    echo "=== Images ==="
    docker images
    echo "=== Networks ==="
    docker network ls
```

## Emergency Response Procedures

### Mass Workflow Failures

When multiple workflows fail simultaneously:

```bash
#!/bin/bash
# mass-failure-triage.sh - Quick triage for widespread failures

echo "=== Mass Failure Analysis ==="

# Count failures by time
gh run list --status failure --limit 50 --json createdAt | \
    jq -r '.[].createdAt' | \
    cut -dT -f1 | \
    sort | uniq -c

# Common error patterns
echo "=== Common Error Patterns ==="
for run in $(gh run list --status failure --limit 20 --json id -q '.[].id'); do
    gh run view "$run" --log-failed 2>/dev/null | \
        grep -E "(Error:|ERROR:|FAILED)" | \
        head -5
done | sort | uniq -c | sort -nr | head -10

# Check GitHub Status
echo "=== GitHub Status ==="
curl -s https://www.githubstatus.com/api/v2/status.json | jq -r '.status.description'
```

### Rollback Strategy

```bash
# Quick rollback for broken workflow
git log -1 --format="%H" -- .github/workflows/<workflow>.yml  # Get current commit
git checkout HEAD~1 -- .github/workflows/<workflow>.yml       # Rollback one commit
git add .github/workflows/<workflow>.yml
git commit -m "fix(ci): rollback <workflow> to working state"
```

## Integration with Monitoring

### Automated Failure Detection

```yaml
# .github/workflows/failure-monitor.yml
name: Failure Monitor
on:
  workflow_run:
    workflows: ["CI", "Tests", "Build"]
    types: [completed]

jobs:
  notify-on-failure:
    if: github.event.workflow_run.conclusion == 'failure'
    runs-on: ubuntu-latest
    steps:
      - name: Analyze failure
        run: |
          echo "Failed workflow: ${{ github.event.workflow_run.name }}"
          echo "Run ID: ${{ github.event.workflow_run.id }}"

          # Fetch failure details
          gh run view ${{ github.event.workflow_run.id }} --log-failed | \
            grep -E "(Error:|ERROR:)" | head -10
        env:
          GH_TOKEN: ${{ github.token }}

      - name: Create issue for repeated failures
        uses: actions/github-script@v7
        with:
          script: |
            // Logic to create issue if same workflow fails >3 times
            // Include failure analysis and suggested fixes
```

## Debugging Checklist

### Pre-Debugging
- [ ] Check GitHub Status page for service issues
- [ ] Verify recent changes to workflow files
- [ ] Check if failure is isolated or widespread

### During Debugging
- [ ] Read the full error message
- [ ] Identify which step failed
- [ ] Check if it's consistent or flaky
- [ ] Verify permissions are correct
- [ ] Check for environment differences
- [ ] Try reproducing locally with act

### Post-Debugging
- [ ] Document the fix in commit message
- [ ] Update workflow if needed to prevent recurrence
- [ ] Check action versions and changelogs
- [ ] Create tracking issue if it's a recurring problem
- [ ] Add monitoring if it's a critical workflow

## Cross-References

- [monitoring.md](monitoring.md) - Set up proactive monitoring to catch issues early
- [security.md](security.md) - Security-related debugging (permissions, secrets)
- [performance.md](performance.md) - Performance-related failures and optimization
