# Quick Reference

Essential commands, patterns, and troubleshooting for GitHub Actions operations.

## Essential Commands

### Repository Analysis
```bash
# Check if repo is fork and assess complexity
gh repo view --json isFork,parent -q '{fork: .isFork, parent: .parent.nameWithOwner}'
ls -1 .github/workflows/*.yml 2>/dev/null | wc -l

# List failed runs
gh run list --status failure --limit 10

# Get logs for failed run
gh run view <run-id> --log-failed

# Re-run failed jobs only
gh run rerun <run-id> --failed
```

### Workflow Validation
```bash
# Check YAML syntax and common issues
actionlint .github/workflows/*.yml

# Find deprecated patterns
grep -r "actions-rs/\|set-output\|save-state" .github/workflows/

# Find unpinned actions (security risk)
grep -r "uses:.*@v[0-9]" .github/workflows/
```

### Multi-Repository Operations
```bash
# List repos with workflows
for repo in $(gh repo list aRustyDev --limit 100 --json name -q '.[].name'); do
  count=$(gh api "repos/aRustyDev/$repo/contents/.github/workflows" 2>/dev/null | jq length 2>/dev/null || echo 0)
  [ "$count" -gt 0 ] && echo "$repo: $count workflows"
done

# Find repos with most failures
for repo in $(gh repo list aRustyDev --limit 50 --json name -q '.[].name'); do
  failures=$(gh run list --repo "aRustyDev/$repo" --status failure --limit 100 --json conclusion -q 'length' 2>/dev/null || echo 0)
  [ "$failures" -gt 0 ] && echo "$failures $repo"
done | sort -rn
```

## Common Patterns

### Security & Permissions
```yaml
# Minimal permissions template
permissions:
  contents: read       # Default for all jobs

jobs:
  deploy:
    permissions:
      contents: read         # Clone repo
      deployments: write     # Deploy
      id-token: write       # OIDC authentication
```

### Performance & Efficiency
```yaml
# Concurrency control
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}

# Path filters
on:
  push:
    paths: ['src/**', 'Cargo.toml']
    paths-ignore: ['**.md', 'docs/**']

# Caching template
- uses: actions/cache@v4.1.2
  with:
    path: ~/.cargo
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: ${{ runner.os }}-cargo-
```

### Matrix Optimization
```yaml
strategy:
  fail-fast: false
  matrix:
    os: [ubuntu-latest, windows-latest]
    include:
      - os: ubuntu-latest
        experimental: true
    exclude:
      - os: windows-latest
        experimental: true
```

## Quick Fixes

### Fork Issues
| Issue | Quick Fix |
|-------|-----------|
| External deployment | `mv .github/workflows/deploy.yml .github/workflows/deploy.yml.disabled` |
| Wrong Docker namespace | Edit workflow: `s/upstream-org/your-org/g` |
| Missing secrets | Remove secret references or create tracking issue |
| Upstream composite actions | Replace with standard actions or disable |

### Performance Issues
| Issue | Quick Fix |
|-------|-----------|
| No concurrency control | Add concurrency block to workflow |
| Broad triggers | Add path filters to `on:` section |
| No caching | Add language-specific cache action |
| Inefficient matrix | Remove unnecessary OS/version combinations |

### Security Issues
| Issue | Quick Fix |
|-------|-----------|
| `permissions: write-all` | Replace with specific minimal permissions |
| Unpinned actions | Pin to specific version: `@v4.1.0` |
| Exposed secrets | Use environment variables, add masking |
| Injection risks | Validate inputs, use environment variables |

## Troubleshooting Checklist

### Pre-Review
- [ ] Check GitHub Status for service issues
- [ ] Identify if repository is a fork
- [ ] Assess workflow complexity (count workflows/lines)
- [ ] Look for recent changes to workflow files

### During Review
- [ ] **Priority 1**: Ensure workflows are actually working (not just passing)
- [ ] **Priority 2**: Check for reasonable resource usage
- [ ] **Priority 3**: Debug and fix failing workflows
- [ ] **Priority 4**: Choose reliable over fancy actions
- [ ] **Priority 5**: Prefer third-party over self-hosted for new development
- [ ] **Priority 6**: Standardize patterns across repositories

### Post-Review
- [ ] Validate changes with `actionlint`
- [ ] Verify action versions exist
- [ ] Create tracking issues for action decisions
- [ ] Document known limitations if applicable
- [ ] Test critical workflows after changes

## Error Patterns

### Permission Errors
| Error | Cause | Fix |
|-------|-------|-----|
| `Resource not accessible by integration` | Missing permissions | Add `permissions:` block |
| `HttpError: 403` with Dependabot | Dependabot token limitations | Use `pull_request_target` or PAT |

### Dependency Errors
| Error | Cause | Fix |
|-------|-------|-----|
| `npm ci` fails | Outdated lock file | Delete `package-lock.json`, run `npm install` |
| `cargo build` fails | Missing system dependencies | Add setup steps for dependencies |

### Environment Errors
| Error | Cause | Fix |
|-------|-------|-----|
| `No space left on device` | Runner disk full | Clean up or use larger runner |
| Action version not found | Invalid version tag | Check action repository for valid versions |
| Timeout | Long-running process | Increase timeout or optimize process |

## Action Selection Reference

### Reliable Actions (Prefer These)
| Purpose | Action | Version | Notes |
|---------|--------|---------|-------|
| Checkout | `actions/checkout` | `@v4.1.0` | Standard, well-maintained |
| Cache | `actions/cache` | `@v4.1.2` | Official caching |
| Setup Node | `actions/setup-node` | `@v4.1.0` | Built-in npm caching |
| Upload artifact | `actions/upload-artifact` | `@v4` | Official artifact handling |

### Language-Specific
| Language | Setup | Cache | Notes |
|----------|-------|-------|-------|
| Rust | `dtolnay/rust-toolchain` | `Swatinem/rust-cache` | Fast, efficient |
| Node.js | `actions/setup-node` | Built-in | Use `cache: 'npm'` |
| Python | `actions/setup-python` | `actions/cache` | Path: `~/.cache/pip` |
| Go | `actions/setup-go` | `actions/cache` | Path: `~/go/pkg/mod` |

### Security Actions
| Purpose | Action | Notes |
|---------|--------|-------|
| Secret scanning | `trufflesecurity/trufflehog` | Find exposed secrets |
| Dependency audit | Built-in (`npm audit`, `cargo audit`) | Language-specific |
| Container scan | `aquasecurity/trivy-action` | Scan Docker images |

## File Templates

### Basic CI Workflow
```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4.1.0
      - name: Setup
        run: echo "Setup steps here"
      - name: Test
        run: echo "Test commands here"
```

### Minimal Dependabot Config
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

### Basic Auto-assign Workflow
```yaml
# .github/workflows/auto-assign.yml
name: Auto Assign
on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

jobs:
  assign:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: write
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.addAssignees({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              assignees: ['${{ github.repository_owner }}']
            });
```

## Complexity Decision Matrix

| Workflows | Lines | Approach | Estimated Time |
|-----------|-------|----------|----------------|
| 1-5 | <500 | Fix all in one PR | 1-2 hours |
| 6-10 | 500-1500 | Fix by priority, 1-2 PRs | 3-6 hours |
| 11-15 | 1500-3000 | Incremental fixes, multiple PRs | 1-2 days |
| 16+ | 3000+ | Disable-first strategy | 2+ days |

### When to Ask User
- Complete fix requires >2 hours of refactoring
- Fix would change core project behavior
- Multiple equally valid approaches exist
- Fork has diverged significantly from upstream

## Resource Links

### Official Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Security hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

### Tools
- [actionlint](https://github.com/rhymond/actionlint) - Workflow linting
- [act](https://github.com/nektos/act) - Local workflow testing
- [GitHub CLI](https://cli.github.com/) - Command-line operations

### Cross-References
- [debugging.md](debugging.md) - Detailed debugging procedures
- [security.md](security.md) - Comprehensive security hardening
- [performance.md](performance.md) - Performance optimization strategies
- [monitoring.md](monitoring.md) - Monitoring and alerting setup
- [multi-repo.md](multi-repo.md) - Multi-repository review workflows