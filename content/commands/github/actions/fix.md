---
description: Systematically review and fix GitHub Actions in a repository
argument-hint: "[owner/repo] [--dry-run]"
---

# Fix GitHub Actions

Systematically review all PRs and failed action logs in a repository, applying fixes based on priority order.

## Arguments

- `$1` - Repository in `owner/repo` format (optional, defaults to current repo)
- `--dry-run` - Preview mode: identify and report issues without making changes

## Skills Required

Read and apply guidance from: `~/.claude/skills/gha-ops/`

## Priority Order

Fix issues in this order:

1. **Working** - Ensure actions actually work, not just pass
2. **Reasonable** - Ensure workflows trigger appropriately
3. **Passing** - Fix failing actions
4. **Reliable > Fancy** - Prefer proven actions over feature-rich
5. **Reliable > Self-hosted** - Prefer third-party over building new
6. **Standardized** - Use consistent patterns

## Workflow

### Step 1: Determine Target Repository

```bash
# If $1 provided, use it; otherwise detect from git remote
REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
```

Parse `$1` if provided, otherwise use the current repository.

### Step 1b: Check for Dry-Run Mode

If `--dry-run` is specified:

- **DO NOT** make any changes to files
- **DO NOT** create branches, commits, or PRs
- **DO NOT** create tracking issues
- **DO** analyze and report all issues found
- **DO** categorize issues by priority
- **DO** suggest fixes without applying them
- **DO** generate the summary report with "Would fix" status

In dry-run mode, prefix all actions with `[DRY-RUN]` in output.

### Step 1c: Assess Complexity

Before diving into fixes, assess the scope:

```bash
# Quick complexity check
echo "Workflows: $(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)"
echo "Total lines: $(wc -l .github/workflows/*.yml 2>/dev/null | tail -1 | awk '{print $1}')"
echo "Action refs: $(grep -h 'uses:' .github/workflows/*.yml 2>/dev/null | wc -l)"
```

| Tier | Workflows | Lines | Strategy |
|------|-----------|-------|----------|
| Simple | 1-5 | <500 | Fix all in one PR |
| Medium | 6-10 | 500-1500 | Fix by priority, 1-2 PRs |
| Complex | 11+ | 1500+ | Incremental PRs |
| Massive | 15+ | 3000+ | Disable-first, then incremental |

For **Complex/Massive** repos, use incremental approach:

1. PR 1: Disable non-essential workflows
2. PR 2: Add concurrency/path filters
3. PR 3+: Fix specific failures

### Step 2: Gather Information

Run these commands in parallel to understand the current state:

```bash
# List open PRs with workflow changes
gh pr list --repo "$REPO" --state open --json number,title,files --jq '.[] | select(.files[].path | startswith(".github/workflows/"))'

# List failed workflow runs (last 20)
gh run list --repo "$REPO" --status failure --limit 20

# List all workflow files
gh api "repos/$REPO/contents/.github/workflows" --jq '.[].name'

# Check for open Dependabot PRs
gh pr list --repo "$REPO" --author "app/dependabot" --state open
```

### Step 3: Categorize Issues

For each PR and failed run, categorize by priority:

| Priority | Category | Examples |
|----------|----------|----------|
| 1 | Not working | Empty tests, swallowed errors, `continue-on-error: true` hiding failures |
| 2 | Unreasonable | No path filters, fuzzing on every push, no concurrency control |
| 3 | Failing | Actual test/build failures, permission errors, dependency issues |
| 4 | Fancy action | Feature-rich action chosen over reliable alternative |
| 5 | Self-hosted gap | Third-party used where arustydev/gha could have an action |
| 6 | Non-standard | Inconsistent patterns, outdated action versions |

### Step 4: Fix Priority 1 - Working

Check workflows for:

- Jobs that pass with no assertions
- `continue-on-error: true` masking real failures
- Conditional steps that always skip
- Empty or placeholder test suites

**Fix pattern**: Add meaningful assertions or remove misleading success signals.

### Step 5: Fix Priority 2 - Reasonable

Check workflows for anti-patterns:

| Anti-pattern | Fix |
|--------------|-----|
| No path filters | Add `paths:` and `paths-ignore:` |
| No concurrency | Add `concurrency:` block |
| Expensive jobs on every push | Move to schedule or manual trigger |
| Full matrix without need | Reduce matrix or make conditional |

**Standard concurrency block**:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

### Step 6: Fix Priority 3 - Passing

Debug failing actions using the gha-ops skill guidance:

1. Get failed run logs: `gh run view <run-id> --log-failed`
2. Identify failure type (permission, dependency, flaky, environment)
3. Apply appropriate fix from debugging reference

### Step 7: Fix Priority 4 - Reliable > Fancy

When encountering action choices:

1. Check if a simpler/more reliable alternative exists
2. If choosing reliable over fancy, create tracking issue:

```bash
gh issue create --repo arustydev/gha \
  --title "[REVIEW] Evaluate <fancy-action>" \
  --label "action-review" \
  --body "## Context
Chose \`<reliable-action>\` over \`<fancy-action>\` in \`$REPO\`.

## Fancy Action
- **Repository:** \`<owner>/<fancy-action>\`
- **Version:** \`<version>\`
- **Features:** <list attractive features>
- **Concerns:** <why not chosen - stability, maintenance, complexity>

## Reliable Alternative
- **Repository:** \`<owner>/<reliable-action>\`
- **Why chosen:** <stability, simplicity, proven track record>

## Used In
- \`$REPO\` - \`<workflow-file>\`

## Review Criteria
- [ ] 6+ months stable releases
- [ ] Active maintenance
- [ ] Features become necessary"
```

### Step 8: Fix Priority 5 - Reliable > Self-hosted

When using third-party instead of building in arustydev/gha:

```bash
gh issue create --repo arustydev/gha \
  --title "[CONSIDER] Build alternative to <action-purpose>" \
  --label "new-action" \
  --body "## Context
Using third-party \`<owner>/<action>\` in \`$REPO\` instead of building custom.

## Third-Party Action
- **Repository:** \`<owner>/<action>@<version>\`
- **Purpose:** <what it does>
- **Why chosen:** <reliability, features, maintenance>

## Alternatives Evaluated
| Action | Pros | Cons |
|--------|------|------|
| <action1> | ... | ... |
| <action2> | ... | ... |

## Used In
- \`$REPO\` - \`<workflow-file>\`

## Build Custom If
- [ ] Third-party becomes unmaintained
- [ ] Need unsupported features
- [ ] Security/compliance requires it"
```

### Step 9: Fix Priority 6 - Standardization

Ensure workflows follow standard patterns:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | push, pull_request | Build, test, lint |
| `release.yml` | release published | Publish artifacts |
| `dependabot.yml` | schedule | Dependency updates |

**Prefer newer versions**: When updating dependencies, always use the latest stable version.

### Step 10: Template Prevention

After identifying each problem, evaluate:

1. **Could a gist template prevent this?**
   - Check existing gists: `gh gist list --filter templates`
   - If template exists but is outdated, note for update
   - If no template exists, note for creation

2. **Could a tmpl-* repo change prevent this?**
   - Check if pattern belongs in project templates
   - Note improvements for tmpl-mdbook-plugin, tmpl-nix, etc.

Document prevention opportunities in the fix summary.

### Step 11: Apply Fixes

**In dry-run mode**: Skip this step entirely. Report what would be done instead.

**In normal mode**, for each fix:

1. Create a feature branch if not already on one
2. Make the change
3. Validate changes before committing:

   ```bash
   # Check YAML syntax
   actionlint .github/workflows/*.yml

   # Verify action versions exist
   for action in $(grep -h "uses:" .github/workflows/*.yml | grep -oE '[^/]+/[^@]+@v[0-9]+' | sort -u); do
     repo=$(echo "$action" | cut -d@ -f1)
     version=$(echo "$action" | cut -d@ -f2)
     gh api "repos/$repo/git/refs/tags/$version" --silent || echo "WARNING: $action not found"
   done
   ```

4. Commit with conventional commit message
5. Push and create PR if needed

### Step 12: Report Summary

Provide a summary table.

**Dry-run mode format:**

```markdown
## [DRY-RUN] Analysis for $REPO

| Priority | Issue | Would Fix | Prevention |
|----------|-------|-----------|------------|
| 1 | <issue> | <proposed fix> | <gist/template opportunity> |
| 2 | <issue> | <proposed fix> | <gist/template opportunity> |

### Issues That Would Be Created

- [REVIEW] <title> - <reason>
- [CONSIDER] <title> - <reason>

### Template Opportunities

- [ ] Update gist: `templates.hbs(github/workflows)` - <reason>

### To Apply These Fixes

Run without --dry-run: `/fix-gha $REPO`
```

**Normal mode format:**

```markdown
## Fix Summary for $REPO

| Priority | Issue | Status | Prevention |
|----------|-------|--------|------------|
| 1 | <issue> | Fixed/Pending | <gist/template opportunity> |
| 2 | <issue> | Fixed/Pending | <gist/template opportunity> |
| ... | ... | ... | ... |

### Issues Created

- arustydev/gha#XX - [REVIEW] <title>
- arustydev/gha#XX - [CONSIDER] <title>

### Known Limitations
<!-- Include if any issues couldn't be fully fixed -->

| Issue | Reason | Impact |
|-------|--------|--------|
| <issue> | <why not fixed> | <what doesn't work> |

### Template Opportunities

- [ ] Update gist: `templates.hbs(github/workflows)` - <reason>
- [ ] Update tmpl-*: <repo> - <reason>

### Next Steps

1. <action item>
2. <action item>
```

## Examples

```bash
# Fix current repository
/fix-gha

# Fix specific repository
/fix-gha aRustyDev/mdbook-doc-graph

# Preview issues without making changes (dry-run)
/fix-gha --dry-run

# Dry-run on specific repository
/fix-gha aRustyDev/timesketch --dry-run
```

## Notes

- Always read the gha-ops skill for detailed debugging and selection guidance
- Create tracking issues with full context - future you will thank present you
- Prefer updating existing gists/templates over creating new ones
- When in doubt about action selection, choose the more boring option

## When to Accept Partial Fixes

Not everything can be fixed. Accept partial progress when:

| Situation | Action |
|-----------|--------|
| Fix requires >50% workflow rewrite | Disable or document limitation |
| External service dependencies (upstream hubs, registries) | Disable affected jobs |
| Upstream composite actions referenced | Document as limitation |
| Fork architecture tightly coupled | Accept reduced CI coverage |

**For forked repos with extensive upstream dependencies:**

1. Disable non-essential workflows (deploy, publish, scheduled)
2. Keep core CI (build, test, lint) even if some jobs fail
3. Document known limitations in PR description
4. Don't try to fix everything - progress over perfection
