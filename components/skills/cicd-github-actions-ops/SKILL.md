---
name: cicd-github-actions-ops
description: Systematic review and debugging of GitHub Actions workflows. Use when reviewing PRs, debugging failed actions, analyzing workflow efficiency, or making decisions about which actions to use.
---

# GitHub Actions Operations

Guide for systematic review, debugging, and optimization of GitHub Actions across repositories.

## When to Use This Skill

- Reviewing open PRs that involve workflow changes
- Debugging failed GitHub Actions runs
- Auditing workflow efficiency and reasonableness
- Making decisions about action selection (reliable vs fancy, self-hosted vs third-party)
- Standardizing workflows across repositories

## Review Priorities

When reviewing workflows and actions, follow these priorities in order:

### Priority 1: Working (Not Just Passing)

Ensure all GitHub Actions are actually working, not just passing by luck or skipping.

**Check for:**
- Jobs that pass because they have no assertions
- Conditional steps that always skip (`if: false` effectively)
- Error handling that swallows failures
- `continue-on-error: true` hiding real issues
- Empty test suites that "pass"

```bash
# Check if a workflow has meaningful steps
gh run view <run-id> --log | grep -E "(Run|Error|Warning|PASS|FAIL)"
```

### Priority 2: Reasonable Workflows

Ensure workflows trigger appropriately and don't waste resources.

**Anti-patterns to fix:**
| Anti-pattern | Problem | Solution |
|--------------|---------|----------|
| Fuzzing on every push | Expensive, slow | Schedule or manual trigger |
| Full rebuild for doc changes | Wasteful | Use path filters |
| No concurrency control | Redundant runs | Add `concurrency:` |
| Matrix without need | Slow CI | Use matrix only when testing compatibility |

**Path filtering template:**
```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'Cargo.toml'
      - '.github/workflows/ci.yml'
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.gitignore'
```

**Concurrency template:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

### Priority 3: Passing

All GitHub Actions should pass. Debug failures systematically.

See: [debugging.md](references/debugging.md)

### Priority 4: Reliable > Fancy

Prefer proven, reliable actions over feature-rich alternatives.

**When choosing reliable over fancy:**
1. Use the reliable action
2. Create tracking issue in `arustydev/gha` for review

```bash
gh issue create --repo arustydev/gha \
  --title "[REVIEW] Evaluate <fancy-action> vs <reliable-action>" \
  --body "## Context
Chose \`<reliable-action>\` over \`<fancy-action>\` for <reason>.

## Fancy Action
- **Name:** \`<owner>/<fancy-action>\`
- **Features:** <list features>
- **Concerns:** <why not chosen>

## Reliable Action
- **Name:** \`<owner>/<reliable-action>\`
- **Why chosen:** <stability, maintenance, simplicity>

## Used In
- \`<repo-name>\` - \`<workflow-file>\`

## Review Request
Evaluate if fancy action is worth adopting once:
- [ ] It has more stability/adoption
- [ ] We need its features
- [ ] It's been maintained for 6+ months"
```

### Priority 5: Reliable > Self-Hosted (New Development)

For NEW action development, prefer third-party reliable actions over building in `arustydev/gha`.

**When using third-party over building self-hosted:**
1. Use the third-party action
2. Create tracking issue in `arustydev/gha` for future consideration

```bash
gh issue create --repo arustydev/gha \
  --title "[CONSIDER] Build alternative to <action>" \
  --body "## Context
Using third-party \`<owner>/<action>\` instead of building custom.

## Third-Party Action
- **Name:** \`<owner>/<action>@<version>\`
- **Purpose:** <what it does>
- **Why chosen:** <reliability, features, maintenance>

## Evaluated Alternatives
| Action | Pros | Cons |
|--------|------|------|
| <action1> | ... | ... |
| <action2> | ... | ... |

## Used In
- \`<repo-name>\` - \`<workflow-file>\`

## Future Consideration
Build custom version if:
- [ ] Third-party becomes unmaintained
- [ ] We need custom features not supported
- [ ] Security/audit requirements demand it"
```

### Priority 6: Standardization

Use consistent patterns across all repositories.

**Standard workflow patterns:**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | push, pull_request | Build, test, lint |
| `release.yml` | release published | Publish artifacts |
| `dependabot.yml` | schedule | Dependency updates |
| `auto-assign.yml` | issues, PRs opened | Assign to owner |

## Systematic Review Workflow

### Quick Assessment

Before detailed review, assess complexity and identify fork-specific issues:

```bash
# Check if repo is a fork and assess complexity
gh repo view --json isFork,parent -q '{fork: .isFork, parent: .parent.nameWithOwner}'
echo "=== Workflow Count ===" && ls -1 .github/workflows/*.yml 2>/dev/null | wc -l
```

**Workflow complexity tiers:**

| Tier | Workflows | Approach |
|------|-----------|----------|
| Simple | 1-5 | Fix all in one PR |
| Medium | 6-10 | Fix by priority, 1-2 PRs |
| Complex | 11+ | Incremental fixes, multiple PRs |

**Fork-specific patterns to detect:**
- `external_repository:` or `secrets.DEPLOY_KEY` → Upstream deployment
- `secrets.(ORG_|DOCKER_|AWS_)` → Organization secrets not available
- `uses: <upstream>/.github/actions/` → Composite actions missing in fork

See: [multi-repo.md](references/multi-repo.md) for detailed fork handling and complexity assessment.

### Review Process

1. **Categorize Issues**: Working vs. reasonable vs. passing vs. efficient
2. **Fix by Priority**: Follow Priority 1-6 order (see above)
3. **Track Decisions**: Create tracking issues for action choices
4. **Validate Changes**: Use `actionlint` and version checks
5. **Document Limitations**: When partial fixes are acceptable

See: [debugging.md](references/debugging.md) for detailed systematic debugging process.

## Security & Hardening

Essential security practices for production workflows:

### Token Permissions
```yaml
permissions:
  contents: read    # Default, restrict further if possible
  pull-requests: write  # Only for PR workflows
  id-token: write   # Only for OIDC authentication
```

### Common Security Issues

| Issue | Risk | Fix |
|-------|------|-----|
| `permissions: write-all` | Full repo access | Use minimal permissions |
| Secrets in logs | Credential exposure | Use `::add-mask::` for outputs |
| Untrusted input in scripts | Code injection | Sanitize `${{ github.event.* }}` |
| Third-party actions without pinning | Supply chain attacks | Pin to commit SHA: `@abc123...` |

### Security Validation
```bash
# Check for overprivileged workflows
grep -r "permissions:" .github/workflows/ | grep -E "(write-all|write.*write)"

# Find unpinned actions (security risk)
grep -r "uses:.*@v[0-9]" .github/workflows/

# Check for potential injection points
grep -r "github\.event\." .github/workflows/
```

See: [security.md](references/security.md) for comprehensive security hardening guide.

## Performance Optimization

Key areas for workflow performance improvement:

### Concurrency Control
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

### Efficient Triggers
- Use `paths:` filters to avoid unnecessary runs
- Prefer `pull_request` over `push` for PR validation
- Use `workflow_dispatch` for manual triggers instead of broad automation

### Caching Strategies
```yaml
- uses: actions/cache@v4.1.2
  with:
    path: ~/.cargo
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
```

See: [performance.md](references/performance.md) for optimization strategies and monitoring.

## Quick Commands

### View failed runs
```bash
gh run list --status failure --limit 10
```

### Get logs for failed run
```bash
gh run view <run-id> --log-failed
```

### Re-run failed jobs
```bash
gh run rerun <run-id> --failed
```

### List PRs needing review
```bash
gh pr list --search "is:open draft:false review:required"
```

### Check workflow syntax
```bash
actionlint .github/workflows/*.yml
```

### List all workflows in org
```bash
for repo in $(gh repo list aRustyDev --limit 100 --json name -q '.[].name'); do
  echo "=== $repo ==="
  gh api "repos/aRustyDev/$repo/contents/.github/workflows" 2>/dev/null | jq -r '.[].name' || echo "No workflows"
done
```

## See Also

- **Quick Reference**: [quick-reference.md](references/quick-reference.md) - Essential commands and patterns
- **Deep Dive References**:
  - [debugging.md](references/debugging.md) - Systematic debugging procedures
  - [security.md](references/security.md) - Security hardening and best practices
  - [performance.md](references/performance.md) - Performance optimization strategies
  - [monitoring.md](references/monitoring.md) - Monitoring and alerting setup
  - [multi-repo.md](references/multi-repo.md) - Multi-repository review workflows
  - [action-selection.md](references/action-selection.md) - Action selection criteria
  - [issue-templates.md](references/issue-templates.md) - Issue templates for tracking
