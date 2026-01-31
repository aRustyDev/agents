# Performance Optimization Reference

Comprehensive strategies for optimizing GitHub Actions workflow performance and reducing build times.

## Overview

Performance optimization focuses on reducing workflow execution time, resource usage, and runner costs while maintaining reliability.

## Performance Analysis Framework

### Baseline Measurement

```bash
#!/bin/bash
# measure-performance.sh - Establish performance baseline

repo=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}

echo "=== Performance Baseline: $repo ==="

# Average build times by workflow
gh run list --repo "$repo" --limit 100 --json workflowName,runStartedAt,updatedAt | \
    jq -r '.[] |
    select(.runStartedAt != null and .updatedAt != null) |
    [.workflowName,
     ((.updatedAt | fromdateiso8601) - (.runStartedAt | fromdateiso8601))] |
    @csv' | \
    awk -F',' '
    {
        workflow=substr($1, 2, length($1)-2)  # Remove quotes
        time=$2
        sum[workflow] += time
        count[workflow]++
    }
    END {
        for (w in sum) {
            avg = sum[w] / count[w]
            printf "%-30s %3dm %2ds (%d runs)\n", w, int(avg/60), int(avg%60), count[w]
        }
    }' | sort -k2,2nr
```

### Performance Metrics

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Total workflow time | <15 min | >30 min | >60 min |
| Queue time | <30 sec | >2 min | >5 min |
| Setup time (checkout, cache) | <1 min | >3 min | >5 min |
| Test execution | <10 min | >20 min | >45 min |
| Artifact upload/download | <1 min | >5 min | >10 min |

## Caching Strategies

### Language-Specific Caching

#### Rust/Cargo

```yaml
- name: Cache Cargo dependencies
  uses: actions/cache@v4.1.2
  with:
    path: |
      ~/.cargo/bin/
      ~/.cargo/registry/index/
      ~/.cargo/registry/cache/
      ~/.cargo/git/db/
      target/
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-cargo-
```

#### Node.js/npm

```yaml
- name: Cache Node dependencies
  uses: actions/cache@v4.1.2
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

- name: Cache Next.js build
  uses: actions/cache@v4.1.2
  with:
    path: |
      ~/.npm
      ${{ github.workspace }}/.next/cache
    key: ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-${{ hashFiles('**.[jt]s', '**.[jt]sx') }}
```

#### Python/pip

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v4.1.2
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

#### Go

```yaml
- name: Cache Go modules
  uses: actions/cache@v4.1.2
  with:
    path: |
      ~/go/pkg/mod
      ~/.cache/go-build
    key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}
    restore-keys: |
      ${{ runner.os }}-go-
```

### Advanced Caching Patterns

#### Multi-Layer Caching

```yaml
# Cache both dependencies and build artifacts with fallbacks
- name: Cache dependencies
  uses: actions/cache@v4.1.2
  with:
    path: ~/.cargo
    key: ${{ runner.os }}-deps-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-deps-
      ${{ runner.os }}-

- name: Cache build artifacts
  uses: actions/cache@v4.1.2
  with:
    path: target/
    key: ${{ runner.os }}-build-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-build-${{ github.head_ref }}-
      ${{ runner.os }}-build-main-
      ${{ runner.os }}-build-
```

#### Conditional Caching

```yaml
- name: Cache when not dependabot
  if: github.actor != 'dependabot[bot]'
  uses: actions/cache@v4.1.2
  with:
    path: ~/.cargo
    key: cargo-${{ hashFiles('Cargo.lock') }}
```

## Parallelization Strategies

### Job-Level Parallelization

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linter
        run: cargo clippy

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - name: "unit-tests"
            command: "cargo test --lib"
          - name: "integration-tests"
            command: "cargo test --test '*'"
          - name: "doc-tests"
            command: "cargo test --doc"
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: ${{ matrix.command }}

  build:
    needs: [lint, test]  # Only run after lint/test pass
    runs-on: ubuntu-latest
    steps:
      - name: Build release
        run: cargo build --release
```

### Step-Level Parallelization

```yaml
- name: Run parallel tasks
  run: |
    # Run independent tasks in background
    npm run lint &
    npm run type-check &
    npm run security-audit &

    # Wait for all to complete
    wait

    echo "All parallel tasks completed"
```

### Matrix Optimization

```yaml
strategy:
  fail-fast: false  # Don't cancel other matrix jobs on first failure
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    rust-version: [stable, beta]
    include:
      # Add extra combinations
      - os: ubuntu-latest
        rust-version: nightly
        experimental: true
    exclude:
      # Remove expensive combinations
      - os: windows-latest
        rust-version: beta
```

## Resource Optimization

### Runner Selection

| Use Case | Runner Type | Cost Factor | Performance |
|----------|-------------|-------------|-------------|
| Basic CI (lint, test) | `ubuntu-latest` | 1x | Fast |
| Multi-OS testing | `windows-latest`, `macos-latest` | 2x, 10x | Moderate |
| Large builds | `ubuntu-latest-4-cores` | 2x | Very fast |
| GPU workloads | `gpu-ubuntu-latest` | 50x+ | Specialized |

```yaml
# Choose appropriate runner size
jobs:
  quick-checks:
    runs-on: ubuntu-latest  # 2-core, sufficient for lint/small tests

  heavy-build:
    runs-on: ubuntu-latest-4-cores  # 4-core for compilation-heavy workloads

  cross-platform:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]  # Skip macOS if not needed
```

### Memory and Disk Management

```yaml
- name: Free up disk space
  run: |
    # Remove unnecessary tools to free ~14GB
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /opt/ghc
    sudo rm -rf "/usr/local/share/boost"
    sudo rm -rf "$AGENT_TOOLSDIRECTORY"

    df -h

- name: Optimize memory usage
  run: |
    # Limit parallel jobs based on available memory
    JOBS=$(nproc)
    MEM_GB=$(free -g | awk '/^Mem:/{print $2}')

    # Use fewer jobs if memory is limited (< 2GB per job)
    if [ $MEM_GB -lt $((JOBS * 2)) ]; then
      JOBS=$((MEM_GB / 2))
      JOBS=$([ $JOBS -lt 1 ] && echo 1 || echo $JOBS)
    fi

    echo "Using $JOBS parallel jobs"
    echo "MAKEFLAGS=-j$JOBS" >> $GITHUB_ENV
```

## Build Optimization

### Incremental Builds

```yaml
# Rust incremental compilation
- name: Enable incremental builds
  run: |
    echo "CARGO_INCREMENTAL=1" >> $GITHUB_ENV
    echo "CARGO_NET_RETRY=10" >> $GITHUB_ENV

# Selective building
- name: Build only changed packages
  run: |
    # Get list of changed files
    changed_files=$(git diff --name-only ${{ github.base_ref }}..HEAD)

    if echo "$changed_files" | grep -q "^frontend/"; then
      echo "Frontend changed, building frontend"
      cd frontend && npm run build
    fi

    if echo "$changed_files" | grep -q "^backend/"; then
      echo "Backend changed, building backend"
      cd backend && cargo build --release
    fi
```

### Dependency Optimization

```yaml
# Pin action versions for consistent performance
- uses: actions/checkout@v4.2.2  # Specific version, not @v4
- uses: actions/cache@v4.1.2

# Use faster alternatives
- name: Setup Node
  uses: actions/setup-node@v4.1.0
  with:
    node-version: '20'
    cache: 'npm'  # Built-in caching, faster than separate cache action

# Minimize checkout scope
- uses: actions/checkout@v4
  with:
    fetch-depth: 1  # Shallow clone, much faster
    sparse-checkout: |
      src/
      Cargo.toml
      Cargo.lock
```

## Network Optimization

### Artifact Management

```yaml
# Upload only essential artifacts
- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: |
      target/debug/test-results.xml
      !target/debug/**/*.o  # Exclude large object files
    retention-days: 7  # Shorter retention for non-critical artifacts

# Compress large artifacts
- name: Compress logs
  run: tar -czf logs.tar.gz logs/

- name: Upload compressed logs
  uses: actions/upload-artifact@v4
  with:
    name: logs
    path: logs.tar.gz
```

### Registry Optimization

```yaml
# Use registry mirrors for faster downloads
- name: Configure npm registry
  run: npm config set registry https://registry.npmjs.org/

# Docker layer caching
- name: Build Docker image
  uses: docker/build-push-action@v6
  with:
    context: .
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Performance Testing Workflows

### Benchmark Integration

```yaml
name: Performance Benchmarks
on:
  push:
    branches: [main]
  pull_request:
    paths: ['src/**', 'benches/**']

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run benchmarks
        run: cargo bench --bench=main

      - name: Performance regression check
        run: |
          # Compare with baseline (stored in git notes or artifact)
          current_time=$(cat target/criterion/main/benchmark.json | jq '.mean.estimate')
          baseline_time=$(git notes show HEAD~1:benchmark || echo "0")

          if (( $(echo "$current_time > $baseline_time * 1.1" | bc -l) )); then
            echo "❌ Performance regression detected: ${current_time}s vs ${baseline_time}s"
            exit 1
          fi

          echo "✅ Performance within acceptable range"
          git notes add -m "$current_time" HEAD
```

### Load Testing

```yaml
- name: Performance load test
  run: |
    # Start application in background
    ./target/release/app &
    APP_PID=$!

    # Wait for startup
    sleep 5

    # Run load test
    ab -n 1000 -c 10 http://localhost:8080/health

    # Cleanup
    kill $APP_PID

    # Check if response time is acceptable
    avg_time=$(grep "Time per request:" ab_results.txt | head -1 | awk '{print $4}')
    if (( $(echo "$avg_time > 100" | bc -l) )); then
      echo "❌ Response time too high: ${avg_time}ms"
      exit 1
    fi
```

## Cost Optimization

### Runner Cost Analysis

```bash
#!/bin/bash
# analyze-runner-costs.sh - Estimate workflow costs

repo=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}

echo "=== Runner Cost Analysis: $repo ==="

# Get runner usage by OS
gh run list --repo "$repo" --limit 100 --json runsOn,duration,runStartedAt | \
    jq -r '.[] |
    select(.duration != null) |
    [.runsOn[0], .duration] |
    @csv' | \
    awk -F',' '
    {
        os = substr($1, 2, length($1)-2)  # Remove quotes
        duration = $2

        # GitHub Actions pricing (rough estimates)
        if (os ~ /ubuntu/) cost_per_min = 0.008
        else if (os ~ /windows/) cost_per_min = 0.016
        else if (os ~ /macos/) cost_per_min = 0.08
        else cost_per_min = 0.008

        total_minutes[os] += duration / 60
        total_cost[os] += (duration / 60) * cost_per_min
        runs[os]++
    }
    END {
        print "OS\t\tMinutes\tCost\tRuns\tAvg/Run"
        for (os in total_minutes) {
            printf "%-15s\t%.1f\t$%.2f\t%d\t%.1fm\n",
                os, total_minutes[os], total_cost[os], runs[os],
                total_minutes[os] / runs[os]
        }
    }'
```

### Optimization Recommendations

```yaml
# Use YAML anchors to reduce duplication
.cache_config: &cache_config
  uses: actions/cache@v4.1.2
  with:
    path: ~/.cargo
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - *cache_config  # Reuse cache configuration
      - run: cargo test

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - *cache_config  # Reuse cache configuration
      - run: cargo build
```

## Monitoring Performance

### Performance Alerts

```yaml
# Add to workflow to track performance degradation
- name: Performance monitoring
  run: |
    build_time=$(date +%s -d "${{ steps.build.outputs.start_time }}")
    current_time=$(date +%s)
    duration=$((current_time - build_time))

    # Alert if build takes longer than 20 minutes
    if [ $duration -gt 1200 ]; then
      echo "⚠️ Build time exceeded 20 minutes: ${duration}s"
      echo "performance_alert=true" >> $GITHUB_OUTPUT
    fi
  id: perf_check

- name: Create performance alert issue
  if: steps.perf_check.outputs.performance_alert
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: 'Performance Alert: Build time exceeded threshold',
        body: `Build time exceeded 20 minutes in workflow: ${{ github.workflow }}

        **Run details:**
        - Workflow: ${{ github.workflow }}
        - Duration: ${process.env.duration}s
        - Commit: ${{ github.sha }}
        - Runner: ${{ runner.os }}

        Please investigate and optimize the workflow.`,
        labels: ['performance', 'ci']
      });
```

### Dashboard Integration

```bash
# Generate performance report for dashboard
#!/bin/bash
# performance-report.sh

{
  echo "{"
  echo "  \"timestamp\": \"$(date -I)\","
  echo "  \"repository\": \"$(gh repo view --json nameWithOwner -q .nameWithOwner)\","

  echo "  \"metrics\": {"
  # Average build time last 10 runs
  avg_time=$(gh run list --limit 10 --json duration | jq -r '[.[].duration] | add / length')
  echo "    \"avg_build_time\": $avg_time,"

  # Success rate
  total=$(gh run list --limit 50 --json conclusion | jq length)
  success=$(gh run list --limit 50 --status success --json conclusion | jq length)
  success_rate=$((success * 100 / total))
  echo "    \"success_rate\": $success_rate,"

  # Cache hit rate (if available)
  echo "    \"cache_hit_rate\": 85"
  echo "  }"
  echo "}"
} > performance-metrics.json
```

## Cross-References

- [monitoring.md](monitoring.md) - Set up monitoring for performance metrics
- [debugging.md](debugging.md) - Debug performance-related issues
- [security.md](security.md) - Ensure optimizations don't compromise security