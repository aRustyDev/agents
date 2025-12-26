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

Special handling for forked repositories:

```bash
# List all forks
gh repo list aRustyDev --fork --limit 100 --json name,parent -q '.[] | "\(.name) <- \(.parent.nameWithOwner)"'
```

For each fork:
1. Check for upstream-specific workflows
2. Disable or adapt as needed
3. Consider if fork is still needed

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
