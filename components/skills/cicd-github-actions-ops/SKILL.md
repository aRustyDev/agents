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

### Phase 0: Fork Detection

Before reviewing, check if the repository is a fork:

```bash
# Check if repo is a fork
gh repo view --json isFork,parent -q '{fork: .isFork, parent: .parent.nameWithOwner}'
```

**If forked, identify upstream-specific patterns:**

| Pattern | Detection | Common Issues |
|---------|-----------|---------------|
| External deploy target | `external_repository:` in workflow | Deploys to upstream's gh-pages |
| Deploy keys | `secrets.DEPLOY_KEY` | Secret doesn't exist in fork |
| Hardcoded org | `google/timesketch` in workflow | Wrong target org |
| Upstream branches | `branches: [main]` when fork uses `master` | Branch mismatch |
| Upstream composite actions | `uses: <upstream>/.github/actions/` | Action path doesn't exist in fork |
| Hardcoded Docker namespace | `docker.*<upstream-org>/` | Pushes to wrong Docker Hub namespace |
| External registries | `hub.infinyon.cloud` or similar | Upstream-specific package registry |
| Upstream secrets | `secrets.ORG_*` or `secrets.DOCKER_*` | Organization secrets not available |

```bash
# Comprehensive fork detection
grep -rE "external_repository:|DEPLOY_KEY|\.github/actions/" .github/workflows/
grep -rE "secrets\.(ORG_|DOCKER_|SLACK_|AWS_)" .github/workflows/
grep -rE "https?://[a-z-]+\.[a-z]+\.(cloud|io)/" .github/workflows/ | grep -v github
```

**Fork handling options:**

1. **Disable** - Rename to `.yml.disabled` (recommended for deploy workflows)
2. **Adapt** - Modify to work with your fork
3. **Remove** - Delete if not needed
4. **Keep** - Leave as-is if it will work (rare)

```bash
# Disable a workflow
mv .github/workflows/deploy.yml .github/workflows/deploy.yml.disabled

# Find upstream-specific patterns
grep -r "external_repository\|DEPLOY_KEY\|google/" .github/workflows/
```

### Phase 0.5: Complexity Assessment

Before diving into fixes, assess the scope of work:

```bash
# Count workflows and total lines
echo "=== Workflow Complexity ==="
ls -1 .github/workflows/*.yml 2>/dev/null | wc -l | xargs echo "Workflow count:"
wc -l .github/workflows/*.yml 2>/dev/null | tail -1 | awk '{print "Total lines:", $1}'

# Count action dependencies
echo "=== Action Dependencies ==="
grep -h "uses:" .github/workflows/*.yml 2>/dev/null | wc -l | xargs echo "Action references:"
grep -h "uses:" .github/workflows/*.yml 2>/dev/null | grep -oE '[^/]+/[^@]+' | sort -u | wc -l | xargs echo "Unique actions:"

# Count job dependencies (complexity indicator)
echo "=== Job Dependencies ==="
grep -c "needs:" .github/workflows/*.yml 2>/dev/null | awk -F: '{sum+=$2} END {print "Total needs: clauses:", sum}'

# Matrix sprawl check
echo "=== Matrix Size ==="
grep -A20 "matrix:" .github/workflows/*.yml 2>/dev/null | grep -E "^\s+-\s" | wc -l | xargs echo "Matrix entries:"
```

**Complexity tiers:**

| Tier | Workflows | Lines | Approach |
|------|-----------|-------|----------|
| Simple | 1-5 | <500 | Fix all in one PR |
| Medium | 6-10 | 500-1500 | Fix by priority, 1-2 PRs |
| Complex | 11+ | 1500+ | Incremental fixes, multiple PRs |
| Massive | 15+ | 3000+ | Consider disable-first strategy |

**If complexity is High/Massive:**

1. Start with disabling non-essential workflows
2. Focus on Priority 2 fixes (concurrency, path filters) first
3. Address failures incrementally
4. Document known limitations that won't be fixed

### Phase 1: Gather Information

```bash
# List all open PRs across your repos
gh search prs --author aRustyDev --state open --limit 100

# List failed workflow runs
gh run list --repo <owner>/<repo> --status failure --limit 20

# Get workflow files for a repo
gh api repos/<owner>/<repo>/contents/.github/workflows | jq -r '.[].name'
```

### Phase 2: Categorize Issues

For each PR/failure, categorize:

1. **Workflow broken** - Action itself has bugs
2. **Workflow inefficient** - Runs unnecessarily
3. **Test failure** - Code issue, not workflow
4. **Permission issue** - Token/access problems
5. **Environment issue** - Runner/dependency problems
6. **Flaky test** - Intermittent failures

### Phase 3: Fix by Category

| Category | Action |
|----------|--------|
| Workflow broken | Fix workflow, update action versions |
| Workflow inefficient | Add path filters, concurrency |
| Test failure | Fix code, not workflow |
| Permission issue | Adjust permissions block |
| Environment issue | Pin versions, add setup steps |
| Flaky test | Add retry or fix root cause |

### Phase 4: Track Decisions

For every non-trivial decision, create appropriate tracking:

- **Chose reliable over fancy** → Issue in `arustydev/gha`
- **Chose third-party over self-hosted** → Issue in `arustydev/gha`
- **Found bug in action** → Issue in action's repo
- **Need new action** → Issue in `arustydev/gha`

### Phase 5: Validate Before Committing

Before committing workflow changes, validate them:

```bash
# 1. Check YAML syntax and common issues
actionlint .github/workflows/*.yml

# 2. Verify action versions exist
for action in $(grep -h "uses:" .github/workflows/*.yml | grep -oE '[^/]+/[^@]+@v[0-9]+' | sort -u); do
  repo=$(echo "$action" | cut -d@ -f1)
  version=$(echo "$action" | cut -d@ -f2)
  echo -n "$action: "
  gh api "repos/$repo/git/refs/tags/$version" --silent && echo "OK" || echo "NOT FOUND"
done

# 3. Check for deprecated actions
grep -r "actions-rs/\|set-output\|save-state" .github/workflows/ && echo "WARNING: Deprecated patterns found"
```

**Common validation failures:**

| Error | Cause | Fix |
|-------|-------|-----|
| `action version not found` | Invalid version (v6 doesn't exist) | Check [action-selection.md](references/action-selection.md) for valid versions |
| `set-output is deprecated` | Old output syntax | Use `echo "name=value" >> $GITHUB_OUTPUT` |
| `save-state is deprecated` | Old state syntax | Use `echo "name=value" >> $GITHUB_STATE` |

### Phase 6: Partial Fixes and Known Limitations

Not every issue can or should be fully fixed. Know when to stop.

**When to accept a partial fix:**

| Situation | Action |
|-----------|--------|
| Fixing requires rewriting >50% of workflow | Disable or document limitation |
| Need to create custom actions for fork | Document as future work |
| External service dependencies can't be removed | Disable affected jobs/workflows |
| Upstream architecture tightly coupled | Accept reduced CI coverage |

**Documenting known limitations:**

When creating a PR with partial fixes, include a "Known Limitations" section:

```markdown
### Known Limitations

The following issues remain after this fix:

| Issue | Reason | Impact |
|-------|--------|--------|
| `cli_smoke` job fails | Uses upstream's Infinyon Hub | Integration tests don't run |
| Docker builds use wrong namespace | Would require forking build scripts | Images not pushed |

These would require significant refactoring to address.
```

**When to ask the user:**

If any of these apply, use AskUserQuestion before proceeding:

- Complete fix requires >2 hours of refactoring
- Fix would change core project behavior
- Multiple equally valid approaches exist
- Fork has diverged significantly from upstream

**Incremental progress strategy:**

For complex repositories, prefer multiple small PRs:

```
PR 1: Disable non-essential workflows (quick win)
   ↓
PR 2: Add concurrency blocks to remaining workflows
   ↓
PR 3: Fix path filters and triggers
   ↓
PR 4: Address specific test failures
   ↓
(Optional) PR 5: Deep refactoring if needed
```

Each PR should be independently mergeable and improve the situation.

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

- Reference: [debugging.md](references/debugging.md) - Detailed debugging guide
- Reference: [action-selection.md](references/action-selection.md) - Action selection criteria
- Reference: [issue-templates.md](references/issue-templates.md) - Issue templates for tracking
- Reference: [multi-repo.md](references/multi-repo.md) - Multi-repository batch review
