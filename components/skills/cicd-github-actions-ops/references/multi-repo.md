# Multi-Repository Review

Guide for batch reviewing GitHub Actions across multiple repositories.

## Quick Start

```bash
# List all repos with workflows
for repo in $(gh repo list aRustyDev --limit 100 --json name -q '.[].name'); do
  count=$(gh api "repos/aRustyDev/$repo/contents/.github/workflows" 2>/dev/null | jq length 2>/dev/null || echo 0)
  [ "$count" -gt 0 ] && echo "$repo: $count workflows"
done

# List all failed runs across repos
gh search prs --author @me --state open --limit 50 --json repository,number,title
```

## Review Strategies

### Strategy 1: Priority-Based (Recommended)

Review repositories by failure impact:

```bash
# Get repos with most failures
for repo in $(gh repo list aRustyDev --limit 50 --json name -q '.[].name'); do
  failures=$(gh run list --repo "aRustyDev/$repo" --status failure --limit 100 --json conclusion -q 'length' 2>/dev/null || echo 0)
  [ "$failures" -gt 0 ] && echo "$failures $repo"
done | sort -rn | head -20
```

### Strategy 2: Template-Based

Group repos by type and apply consistent fixes:

| Template | Repos | Common Issues |
|----------|-------|---------------|
| `tmpl-mdbook-plugin` | mdbook-* | Missing concurrency, old mdbook version |
| `tmpl-rust-lib` | *-rs | Missing Swatinem/rust-cache |
| `tmpl-nix` | nix-* | Cachix setup issues |

### Strategy 3: Fork Audit

Special handling for forked repositories requires checking for upstream-specific patterns:

```bash
# List all forks
gh repo list aRustyDev --fork --limit 100 --json name,parent -q '.[] | "\(.name) <- \(.parent.nameWithOwner)"'
```

## Fork-Specific Issues Detection

### Phase 0: Fork Detection & Complexity Assessment

Before reviewing any repository, check if it's a fork and assess complexity:

```bash
# Check if repo is a fork and get upstream info
gh repo view --json isFork,parent -q '{fork: .isFork, parent: .parent.nameWithOwner}'

# Count workflows and complexity
echo "=== Workflow Complexity ==="
ls -1 .github/workflows/*.yml 2>/dev/null | wc -l | xargs echo "Workflow count:"
wc -l .github/workflows/*.yml 2>/dev/null | tail -1 | awk '{print "Total lines:", $1}'

# Count action dependencies
echo "=== Action Dependencies ==="
grep -h "uses:" .github/workflows/*.yml 2>/dev/null | wc -l | xargs echo "Action references:"
grep -h "uses:" .github/workflows/*.yml 2>/dev/null | grep -oE '[^/]+/[^@]+' | sort -u | wc -l | xargs echo "Unique actions:"
```

### Fork Pattern Detection

**Identify upstream-specific patterns that commonly break in forks:**

| Pattern | Detection Command | Common Issues |
|---------|-------------------|---------------|
| External deploy target | `grep -r "external_repository:" .github/workflows/` | Deploys to upstream's gh-pages |
| Deploy keys | `grep -r "secrets.DEPLOY_KEY" .github/workflows/` | Secret doesn't exist in fork |
| Hardcoded org | `grep -r "google/timesketch" .github/workflows/` | Wrong target org |
| Upstream branches | `grep -r "branches: \[main\]" .github/workflows/` | Branch mismatch |
| Upstream composite actions | `grep -rE "uses: <upstream>/.github/actions/" .github/workflows/` | Action path doesn't exist in fork |
| Hardcoded Docker namespace | `grep -rE "docker.*<upstream-org>/" .github/workflows/` | Pushes to wrong Docker Hub namespace |
| External registries | `grep -rE "hub\.infinyon\.cloud" .github/workflows/` | Upstream-specific package registry |
| Upstream secrets | `grep -rE "secrets\.(ORG_|DOCKER_|SLACK_|AWS_)" .github/workflows/` | Organization secrets not available |

**Comprehensive fork detection script:**
```bash
#!/bin/bash
# fork-patterns.sh - Detect upstream-specific patterns

echo "=== Fork Pattern Detection ==="

# External repositories and deploy keys
echo "--- Deploy Patterns ---"
grep -rE "external_repository:|DEPLOY_KEY|\.github/actions/" .github/workflows/ 2>/dev/null || echo "None found"

# Organization and service secrets
echo "--- Secret Patterns ---"
grep -rE "secrets\.(ORG_|DOCKER_|SLACK_|AWS_)" .github/workflows/ 2>/dev/null || echo "None found"

# External services and registries
echo "--- External Service Patterns ---"
grep -rE "https?://[a-z-]+\.[a-z]+\.(cloud|io)/" .github/workflows/ 2>/dev/null | grep -v github || echo "None found"

# Hardcoded organization references
echo "--- Organization References ---"
repo_parent=$(gh repo view --json parent -q '.parent.nameWithOwner' 2>/dev/null)
if [ -n "$repo_parent" ]; then
    parent_org=$(echo "$repo_parent" | cut -d'/' -f1)
    echo "Searching for hardcoded references to upstream org: $parent_org"
    grep -r "$parent_org" .github/workflows/ 2>/dev/null || echo "None found"
fi
```

### Fork Handling Options

For each detected pattern, choose appropriate handling:

| Option | When to Use | Implementation |
|--------|-------------|----------------|
| **Disable** | Deploy workflows, upstream-specific CI | `mv .github/workflows/deploy.yml .github/workflows/deploy.yml.disabled` |
| **Adapt** | Can be modified for your fork | Edit workflow to use your org/secrets |
| **Remove** | Not needed in fork | `rm .github/workflows/upstream-specific.yml` |
| **Keep** | Works as-is (rare) | No changes needed |

**Quick disable script:**
```bash
#!/bin/bash
# disable-upstream-workflows.sh - Disable problematic workflows

# Disable deploy workflows (most common)
for workflow in deploy publish release; do
    for file in .github/workflows/${workflow}*.yml; do
        if [ -f "$file" ]; then
            echo "Disabling: $file"
            mv "$file" "${file}.disabled"
        fi
    done
done

# Find and suggest other workflows to disable
echo "=== Suggested Workflows to Review ==="
grep -l "external_repository\|DEPLOY_KEY\|ORG_" .github/workflows/*.yml 2>/dev/null | \
    while read file; do
        echo "⚠️  Review: $file (contains upstream patterns)"
    done
```

### Complexity Assessment

**Complexity tiers guide decision making:**

| Tier | Workflows | Lines | Approach |
|------|-----------|-------|----------|
| Simple | 1-5 | <500 | Fix all in one PR |
| Medium | 6-10 | 500-1500 | Fix by priority, 1-2 PRs |
| Complex | 11+ | 1500+ | Incremental fixes, multiple PRs |
| Massive | 15+ | 3000+ | Consider disable-first strategy |

**For High/Massive complexity in forks:**

1. Start with disabling non-essential workflows (quick win)
2. Focus on basic fixes (concurrency, path filters) for essential workflows
3. Address failures incrementally
4. Document known limitations that won't be fixed

**Assessment script:**
```bash
#!/bin/bash
# assess-complexity.sh - Determine review approach

workflows=$(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)
lines=$(wc -l .github/workflows/*.yml 2>/dev/null | tail -1 | awk '{print $1}' || echo 0)

echo "Workflows: $workflows"
echo "Total lines: $lines"

if [ "$workflows" -le 5 ] && [ "$lines" -le 500 ]; then
    echo "Complexity: SIMPLE - Fix all in one PR"
elif [ "$workflows" -le 10 ] && [ "$lines" -le 1500 ]; then
    echo "Complexity: MEDIUM - Fix by priority, 1-2 PRs"
elif [ "$workflows" -le 15 ] && [ "$lines" -le 3000 ]; then
    echo "Complexity: COMPLEX - Incremental fixes, multiple PRs"
else
    echo "Complexity: MASSIVE - Consider disable-first strategy"
fi

# Check if it's a fork
if gh repo view --json isFork -q '.isFork' 2>/dev/null | grep -q true; then
    echo "⚠️ FORK DETECTED - Apply fork-specific patterns first"
fi
```

## Batch Commands

### Audit All Repos

```bash
# Create audit report
echo "# GHA Audit Report - $(date +%Y-%m-%d)" > audit.md
echo "" >> audit.md

for repo in $(gh repo list aRustyDev --limit 100 --json name -q '.[].name'); do
  echo "## $repo" >> audit.md

  # Get workflow count
  workflows=$(gh api "repos/aRustyDev/$repo/contents/.github/workflows" 2>/dev/null | jq -r '.[].name' 2>/dev/null || echo "none")
  echo "Workflows: $workflows" >> audit.md

  # Get recent failures
  failures=$(gh run list --repo "aRustyDev/$repo" --status failure --limit 5 --json name,conclusion,createdAt 2>/dev/null)
  echo "Recent failures: $(echo "$failures" | jq length)" >> audit.md
  echo "" >> audit.md
done
```

### Dry-Run All Repos

Use the `/fix-gha` command with `--dry-run` to preview issues without making changes:

```bash
# Run dry-run analysis for each repo (manual process)
# For each repo, run: /fix-gha aRustyDev/<repo> --dry-run
```

### Apply Standard Fixes

Common fixes that can be applied broadly:

```bash
# Update action versions across all repos (use with caution)
# This is a template - customize per repo
for repo in timesketch mdbook-doc-graph; do
  gh workflow list --repo "aRustyDev/$repo" -q '.[].name'
done
```

## Progress Tracking

### Tracking Table Template

```markdown
## Multi-Repo GHA Review Progress

| Repository | Workflows | Status | Issues | PR | Notes |
|------------|-----------|--------|--------|-----|-------|
| repo-1 | 3 | Reviewed | #9 | #3 | Fork - disabled upstream |
| repo-2 | 5 | Pending | - | - | - |
| repo-3 | 2 | Fixed | - | #12 | Updated versions |
```

### Status Values

| Status | Meaning |
|--------|---------|
| Pending | Not yet reviewed |
| Reviewed | Analyzed, issues identified |
| In Progress | Fixes being applied |
| Fixed | All issues resolved |
| Skipped | No action needed (e.g., archived) |

## Prioritization Matrix

| Priority | Criteria | Action |
|----------|----------|--------|
| Critical | Main project, CI blocking | Fix immediately |
| High | Active development, flaky tests | Fix this sprint |
| Medium | Stable, minor issues | Fix when convenient |
| Low | Archived/inactive | Skip or minimal fix |

### Determining Priority

```bash
# Check repo activity
gh api "repos/aRustyDev/<repo>" --jq '{
  pushed: .pushed_at,
  updated: .updated_at,
  open_issues: .open_issues_count,
  archived: .archived
}'
```

## Common Patterns

### Pattern 1: Version Update Wave

When GitHub releases new action versions, update all repos:

```bash
# Find repos using old version
for repo in $(gh repo list aRustyDev --limit 100 --json name -q '.[].name'); do
  old=$(gh api "repos/aRustyDev/$repo/contents/.github/workflows" 2>/dev/null | \
    jq -r '.[].download_url' 2>/dev/null | \
    xargs -I{} curl -s {} 2>/dev/null | \
    grep -l "actions/checkout@v3" 2>/dev/null && echo "$repo")
  [ -n "$old" ] && echo "Needs update: $repo"
done
```

### Pattern 2: Concurrency Rollout

Add concurrency blocks to all repos missing them:

```bash
# Check for missing concurrency
for repo in $(gh repo list aRustyDev --limit 50 --json name -q '.[].name'); do
  missing=$(gh api "repos/aRustyDev/$repo/contents/.github/workflows" 2>/dev/null | \
    jq -r '.[].download_url' 2>/dev/null | head -1 | \
    xargs -I{} curl -s {} 2>/dev/null | \
    grep -L "concurrency:" 2>/dev/null && echo "$repo")
  [ -n "$missing" ] && echo "Missing concurrency: $repo"
done
```

### Pattern 3: Fork Cleanup

Handle upstream-specific workflows in forks:

```bash
# List forks with deploy workflows
for repo in $(gh repo list aRustyDev --fork --limit 50 --json name -q '.[].name'); do
  has_deploy=$(gh api "repos/aRustyDev/$repo/contents/.github/workflows" 2>/dev/null | \
    jq -r '.[].name' 2>/dev/null | grep -E "(deploy|publish|release)" && echo "yes")
  [ -n "$has_deploy" ] && echo "Check: $repo"
done
```

## Session Management

For large-scale reviews spanning multiple sessions:

1. **Start of session**: Note repos to review
2. **During session**: Update tracking table after each repo
3. **End of session**: Summarize progress, note next steps

### Resume Template

```markdown
## GHA Review Session - [DATE]

### Completed This Session
- [ ] repo-1: Fixed concurrency, PR #X
- [ ] repo-2: Disabled upstream workflows

### Deferred
- repo-3: Needs upstream issue resolved first

### Next Session
- Start with repo-4
- Check if upstream fix for repo-3 is merged
```
