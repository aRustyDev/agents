---
description: Systematically review and fix GitHub Actions in a repository
argument-hint: [owner/repo]
---

# Fix GitHub Actions

Systematically review all PRs and failed action logs in a repository, applying fixes based on priority order.

## Arguments

- `$1` - Repository in `owner/repo` format (optional, defaults to current repo)

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
  --label "action-review,deferred" \
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
  --label "new-action,deferred" \
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

For each fix:

1. Create a feature branch if not already on one
2. Make the change
3. Test locally if possible (`actionlint .github/workflows/*.yml`)
4. Commit with conventional commit message
5. Push and create PR if needed

### Step 12: Report Summary

Provide a summary table:

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
```

## Notes

- Always read the gha-ops skill for detailed debugging and selection guidance
- Create tracking issues with full context - future you will thank present you
- Prefer updating existing gists/templates over creating new ones
- When in doubt about action selection, choose the more boring option
