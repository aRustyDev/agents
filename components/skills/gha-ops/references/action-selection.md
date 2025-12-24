# Action Selection Criteria

Guide for choosing between action alternatives.

## Current Stable Versions (December 2024)

**IMPORTANT:** Always verify versions exist before using. Common mistake: using versions that don't exist (e.g., `setup-node@v6`).

### GitHub Official Actions

| Action | Latest Stable | NOT Valid | Check Command |
|--------|---------------|-----------|---------------|
| `actions/checkout` | v4 | v5, v6 | `gh api repos/actions/checkout/releases/latest -q .tag_name` |
| `actions/setup-node` | v4 | v5, v6 | `gh api repos/actions/setup-node/releases/latest -q .tag_name` |
| `actions/setup-python` | v5 | v6 | `gh api repos/actions/setup-python/releases/latest -q .tag_name` |
| `actions/setup-go` | v5 | v6 | `gh api repos/actions/setup-go/releases/latest -q .tag_name` |
| `actions/setup-java` | v4 | v5, v6 | `gh api repos/actions/setup-java/releases/latest -q .tag_name` |
| `actions/cache` | v4 | v5 | `gh api repos/actions/cache/releases/latest -q .tag_name` |
| `actions/upload-artifact` | v4 | v5 | `gh api repos/actions/upload-artifact/releases/latest -q .tag_name` |
| `actions/download-artifact` | v4 | v5 | `gh api repos/actions/download-artifact/releases/latest -q .tag_name` |
| `actions/github-script` | v7 | v8 | `gh api repos/actions/github-script/releases/latest -q .tag_name` |

### Third-Party Actions

| Action | Latest Stable | Notes |
|--------|---------------|-------|
| `dtolnay/rust-toolchain` | `@stable` / `@nightly` | Uses channel names, not versions |
| `Swatinem/rust-cache` | v2 | |
| `codecov/codecov-action` | v4 | v5 in beta |
| `nick-fields/retry` | v3 | v2 still works |
| `peaceiris/actions-gh-pages` | v4 | |

### Quick Version Check

```bash
# Check if a specific version exists
gh api repos/actions/setup-node/git/refs/tags/v4 --silent && echo "v4 exists" || echo "v4 NOT FOUND"

# Get latest version for any action
gh api repos/<owner>/<action>/releases/latest -q .tag_name

# Bulk check all actions in a workflow
grep -oE 'uses: [^@]+@v[0-9]+' .github/workflows/*.yml | while read line; do
  action=$(echo "$line" | sed 's/uses: //' | cut -d@ -f1)
  version=$(echo "$line" | cut -d@ -f2)
  gh api "repos/$action/git/refs/tags/$version" --silent && echo "$action@$version: OK" || echo "$action@$version: NOT FOUND"
done
```

## Decision Framework

### Question 1: Does arustydev/gha have this?

```bash
# Check if action exists in arustydev/gha
gh api repos/aRustyDev/gha/contents/actions 2>/dev/null | jq -r '.[].name'
```

If **yes**: Use `arustydev/gha/<action>@v1`
If **no**: Continue to Question 2

### Question 2: Is this new development or existing usage?

**Existing usage** (action already in workflow):
- Keep current action if working
- Only change if broken or deprecated

**New development** (adding new action):
- Continue to Question 3

### Question 3: Are there multiple options?

If multiple third-party options exist:

| Criterion | Weight | How to Check |
|-----------|--------|--------------|
| Maintenance | High | Last commit date, response to issues |
| Adoption | High | Stars, used by count |
| Simplicity | Medium | Config complexity, edge cases |
| Features | Low | Only if features are needed |

```bash
# Check action health
gh api repos/<owner>/<action> --jq '{
  stars: .stargazers_count,
  updated: .pushed_at,
  open_issues: .open_issues_count,
  archived: .archived
}'

# Check used by count (if visible)
gh api repos/<owner>/<action> --jq '.network_count'
```

### Question 4: Reliable vs Fancy?

**Choose Reliable when:**
- Core CI functionality (checkout, setup-*, cache)
- Security-sensitive operations
- Simple use case that doesn't need extra features
- Fancy option is < 6 months old

**Consider Fancy when:**
- Significant time savings
- Features genuinely needed
- Well-maintained (> 1 year, active development)
- Used by major projects

**Always track the decision:**
```bash
# If chose reliable over fancy
gh issue create --repo arustydev/gha \
  --title "[REVIEW] <fancy-action> vs <reliable-action>" \
  --label "action-review"
```

## Recommended Actions by Category

### Core Actions (GitHub Official)

Always prefer these for basic operations:

| Purpose | Action | Notes |
|---------|--------|-------|
| Checkout | `actions/checkout@v4` | Standard |
| Cache | `actions/cache@v4` | Standard |
| Upload artifact | `actions/upload-artifact@v4` | Standard |
| Download artifact | `actions/download-artifact@v4` | Standard |
| GitHub Script | `actions/github-script@v7` | For custom API calls |

### Language Setup

| Language | Recommended | Alternative |
|----------|-------------|-------------|
| Node.js | `actions/setup-node@v4` | - |
| Python | `actions/setup-python@v5` | - |
| Go | `actions/setup-go@v5` | - |
| Rust | `dtolnay/rust-toolchain@stable` | `actions-rs/toolchain` (deprecated) |
| Java | `actions/setup-java@v4` | - |

### Rust-Specific

| Purpose | Recommended | Why |
|---------|-------------|-----|
| Toolchain | `dtolnay/rust-toolchain@stable` | Simple, maintained |
| Caching | `Swatinem/rust-cache@v2` | Rust-optimized |
| Clippy | `giraffate/clippy-action@v1` | PR annotations |
| Audit | `rustsec/audit-check@v1` | Security |

### Testing

| Purpose | Recommended | Notes |
|---------|-------------|-------|
| Retry flaky | `nick-fields/retry@v2` | Simple retry logic |
| Test reporter | `dorny/test-reporter@v1` | Multi-format support |
| Coverage | `codecov/codecov-action@v4` | Industry standard |

### PR/Issue Automation

| Purpose | Recommended | Notes |
|---------|-------------|-------|
| Auto-assign | Custom script | See gha-ops main doc |
| Label sync | `EndBug/label-sync@v2` | YAML config |
| Auto-merge | `pascalgn/automerge-action@v0.16` | Dependabot friendly |

### Security

| Purpose | Recommended | Notes |
|---------|-------------|-------|
| Dependency review | `actions/dependency-review-action@v4` | GitHub official |
| CodeQL | `github/codeql-action@v3` | GitHub official |
| Secrets scan | `trufflesecurity/trufflehog@main` | Comprehensive |

## Anti-Patterns

### Actions to Avoid

| Action | Problem | Alternative |
|--------|---------|-------------|
| `actions-rs/*` | Unmaintained | `dtolnay/rust-toolchain` |
| Ancient versions | Security risk | Update to latest major |
| Forks of official | Drift, security | Use official |
| Over-featured | Complexity | Simpler alternative |

### Red Flags

- No commits in > 6 months
- Many open security issues
- No response to issues
- Deprecated warnings in readme
- Fork with minimal changes

## Version Pinning

### Recommended Practice

```yaml
# Good: Pin to major version
- uses: actions/checkout@v4

# Better for security: Pin to SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

# Bad: Unpinned
- uses: actions/checkout@main
```

### When to Use SHA Pinning

- Security-sensitive workflows
- Production deployments
- Compliance requirements

### Dependabot for Updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Tracking Template

When making a non-obvious choice, document it:

```markdown
## Action Selection: <purpose>

**Chosen:** `<owner>/<action>@<version>`

**Considered:**
| Action | Stars | Updated | Why Not |
|--------|-------|---------|---------|
| <alt1> | X | YYYY-MM | <reason> |
| <alt2> | Y | YYYY-MM | <reason> |

**Decision Factors:**
- <factor 1>
- <factor 2>

**Tracking Issue:** <link if created>
```
