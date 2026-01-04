# GitHub Actions Debugging Reference

Comprehensive debugging guide for GitHub Actions workflows, covering advanced troubleshooting techniques and common failure patterns.

## Advanced Log Analysis

### Understanding Exit Codes

| Exit Code | Meaning | Common Causes |
|-----------|---------|---------------|
| 0 | Success | Normal completion |
| 1 | General errors | Script errors, command not found |
| 2 | Misuse of shell builtins | Invalid command usage |
| 126 | Command invoked cannot execute | Permission problems, not executable |
| 127 | Command not found | PATH issues, missing dependencies |
| 128+n | Fatal error signal "n" | Signal termination (SIGINT=130, SIGKILL=137) |

### Job Context Analysis

**Example job log analysis:**
```
2024-01-03T10:15:32.1234567Z ##[group]Run npm test
2024-01-03T10:15:32.1234568Z npm test
2024-01-03T10:15:32.1234569Z shell: /usr/bin/bash -e {0}
2024-01-03T10:15:32.1234570Z env:
2024-01-03T10:15:32.1234571Z   CI: true
2024-01-03T10:15:32.1234572Z   NODE_ENV: test
```

**Key indicators:**
- `shell: /usr/bin/bash -e {0}` - Shell exits on first error (`-e` flag)
- `env:` section shows available environment variables
- Timestamps help identify slow operations

### Log Pattern Matching

```bash
# Extract error lines from logs
gh run view 12345 --log | grep -E "(ERROR|FAIL|✗)"

# Find timeout issues
gh run view 12345 --log | grep -i timeout

# Check for permission issues
gh run view 12345 --log | grep -E "(permission|denied|403)"

# Find dependency conflicts
gh run view 12345 --log | grep -E "(conflict|version|dependency)"
```

## Environment Debugging

### Runner Information

```yaml
- name: Debug runner info
  run: |
    echo "Runner OS: $RUNNER_OS"
    echo "Runner Arch: $RUNNER_ARCH"
    echo "Runner Tool Cache: $RUNNER_TOOL_CACHE"
    echo "GitHub Workspace: $GITHUB_WORKSPACE"
    echo "GitHub Action: $GITHUB_ACTION"
    echo "GitHub Actor: $GITHUB_ACTOR"
    echo "GitHub Repository: $GITHUB_REPOSITORY"
    echo "GitHub Event Name: $GITHUB_EVENT_NAME"
    echo "GitHub SHA: $GITHUB_SHA"
    echo "GitHub Ref: $GITHUB_REF"
    echo "GitHub Head Ref: $GITHUB_HEAD_REF"
    echo "GitHub Base Ref: $GITHUB_BASE_REF"
```

### Path and Environment Issues

```yaml
- name: Debug PATH and environment
  run: |
    echo "PATH: $PATH"
    echo "NODE_VERSION: $(node --version 2>/dev/null || echo 'not found')"
    echo "NPM_VERSION: $(npm --version 2>/dev/null || echo 'not found')"
    echo "PYTHON_VERSION: $(python --version 2>/dev/null || echo 'not found')"
    which node || echo "node not in PATH"
    which npm || echo "npm not in PATH"
    ls -la $HOME/.cache/
```

### Step-by-Step Debugging

```yaml
- name: Step 1 - Checkout (debug)
  uses: actions/checkout@v4
  with:
    fetch-depth: 0

- name: Debug - List workspace contents
  run: |
    pwd
    ls -la
    git status
    git log --oneline -n 5

- name: Step 2 - Setup Node (debug)
  uses: actions/setup-node@v4
  with:
    node-version: '20'

- name: Debug - Verify Node installation
  run: |
    node --version
    npm --version
    which node
    which npm

- name: Step 3 - Install dependencies
  run: npm ci

- name: Debug - List node_modules
  run: |
    ls -la node_modules/ | head -20
    cat package-lock.json | jq '.lockfileVersion'
```

## Common Failure Patterns

### Node.js/NPM Issues

**Pattern 1: NPM Install Failures**
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

**Debugging steps:**
```yaml
- name: Debug dependency conflicts
  run: |
    npm ls --depth=0
    npm outdated
    cat package.json | jq '.dependencies + .devDependencies'
```

**Pattern 2: Node Version Mismatches**
```
Error: The engine "node" is incompatible with this module
```

**Solution:**
```yaml
- uses: actions/setup-node@v4
  with:
    node-version-file: '.nvmrc'  # Use project's Node version
    cache: 'npm'
```

### Python Issues

**Pattern 1: Package Installation Failures**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Debugging:**
```yaml
- name: Debug Python environment
  run: |
    python --version
    pip --version
    pip list
    which python
    which pip
    python -m site
```

### Docker/Container Issues

**Pattern 1: Permission Issues**
```
docker: permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```yaml
- name: Fix Docker permissions
  run: |
    sudo usermod -aG docker $USER
    newgrp docker
```

**Pattern 2: Image Pull Failures**
```
Error response from daemon: pull access denied
```

**Debugging:**
```yaml
- name: Debug Docker setup
  run: |
    docker info
    docker system df
    docker images
```

## Performance Debugging

### Identifying Slow Steps

```bash
# Analyze step durations from logs
gh run view 12345 --log | grep -E "##\[.*\]" | awk '{print $1, $2}'
```

### Memory and CPU Issues

```yaml
- name: Monitor resource usage
  run: |
    echo "Memory usage:"
    free -h
    echo "CPU info:"
    nproc
    lscpu | grep "CPU(s)"
    echo "Disk usage:"
    df -h
    echo "Running processes:"
    ps aux --sort=-%cpu | head -10
```

### Cache Debugging

```yaml
- name: Debug cache
  uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

- name: Verify cache contents
  run: |
    ls -la ~/.npm
    du -sh ~/.npm
```

## Test Debugging

### Flaky Test Detection

```yaml
- name: Run tests with retries
  run: |
    for i in {1..3}; do
      echo "Test run $i"
      npm test && break || {
        echo "Test run $i failed"
        if [ $i -eq 3 ]; then
          echo "All test runs failed"
          exit 1
        fi
      }
    done
```

### Test Output Formatting

```yaml
- name: Run tests with detailed output
  run: |
    npm test -- --verbose --reporter=json > test-results.json
    npm test -- --verbose --reporter=tap > test-results.tap

- name: Upload test results
  uses: actions/upload-artifact@v4
  if: always()
  with:
    name: test-results
    path: |
      test-results.json
      test-results.tap
```

## Integration Testing

### Multi-Service Dependencies

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: testdb
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

- name: Debug service connectivity
  run: |
    nc -zv localhost 5432
    psql -h localhost -U postgres -d testdb -c "SELECT version();"
```

## Cross-References

- [GitHub Actions Troubleshooting Guide](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows)
- [Runner Environment Reference](https://docs.github.com/en/actions/learn-github-actions/environment-variables)
- [Workflow Commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions)