# Trust-Based Auto-Merge Pattern

Automatically enable GitHub's native auto-merge for PRs that meet configurable trust criteria: trusted contributor + verified commits.

## Overview

Trust-based auto-merge reduces manual review overhead for trusted contributors while maintaining security. It uses a separate workflow triggered by `workflow_run` to evaluate PRs after CI passes, checking:

1. **Trusted Author**: Either dependabot or a CODEOWNERS member
2. **Verified Commits**: All commits are cryptographically signed (GPG/SSH)
3. **CI Passed**: Triggered only after validation workflow succeeds

If all criteria pass, GitHub's native auto-merge is enabled (respecting all branch protections).

## When to Use This Pattern

- Repositories with trusted contributors who maintain code quality
- Dependabot PR automation (dependency updates)
- High-velocity repositories where review latency is a bottleneck
- Teams that trust GPG/SSH commit signing as identity verification

## Architecture

```
PR Created → W1 Validation ──► workflow_run trigger
                                     │
                        ┌────────────┴────────────┐
                        │   Auto-Merge Workflow   │
                        ├─────────────────────────┤
                        │ 1. Find PR from run     │
                        │ 2. Check target branch  │
                        │ 3. Check author trust   │
                        │ 4. Verify commit sigs   │
                        │ 5. Enable auto-merge    │
                        └─────────────────────────┘
```

### Why workflow_run?

Using `workflow_run` instead of embedding in the validation workflow:

- **Runs from default branch**: Workflow code comes from `main`, not PR branch
- **No sync needed**: Doesn't require syncing workflow files to staging branch
- **Security**: PR authors cannot modify the auto-merge logic
- **Clean separation**: Validation and merge-eligibility are separate concerns

## Core Components

### 1. workflow_run Trigger

```yaml
name: Auto-Merge Integration PRs

on:
  workflow_run:
    workflows: ["Validate Contribution PR"]  # Name of your CI workflow
    types:
      - completed
    # Note: branches filter matches HEAD, not BASE
    # Check target branch inside the workflow instead

permissions:
  contents: write
  pull-requests: write
```

### 2. Find PR from Workflow Run

```yaml
- name: Get PR Information
  id: pr
  env:
    GH_TOKEN: ${{ github.token }}
    ALLOWED_BASE_BRANCHES: ${{ vars.AUTO_MERGE_ALLOWED_BRANCHES || 'integration' }}
  run: |
    HEAD_SHA="${{ github.event.workflow_run.head_sha }}"

    # Convert allowed branches to array
    IFS=',' read -ra ALLOWED_BRANCHES <<< "$ALLOWED_BASE_BRANCHES"

    PR_DATA=""
    for BASE_BRANCH in "${ALLOWED_BRANCHES[@]}"; do
      BASE_BRANCH=$(echo "$BASE_BRANCH" | xargs)  # trim

      FOUND=$(gh pr list \
        --repo "${{ github.repository }}" \
        --state open \
        --base "$BASE_BRANCH" \
        --json number,headRefOid,author,baseRefName \
        --jq ".[] | select(.headRefOid == \"$HEAD_SHA\")")

      if [[ -n "$FOUND" ]]; then
        PR_DATA="$FOUND"
        break
      fi
    done

    if [[ -z "$PR_DATA" ]]; then
      echo "found=false" >> "$GITHUB_OUTPUT"
      exit 0
    fi

    PR_NUMBER=$(echo "$PR_DATA" | jq -r '.number')
    PR_AUTHOR=$(echo "$PR_DATA" | jq -r '.author.login')

    echo "found=true" >> "$GITHUB_OUTPUT"
    echo "number=$PR_NUMBER" >> "$GITHUB_OUTPUT"
    echo "author=$PR_AUTHOR" >> "$GITHUB_OUTPUT"
```

### 3. Detect PR Type

```yaml
- name: Detect PR Type
  id: detect
  env:
    PR_AUTHOR: ${{ steps.pr.outputs.author }}
  run: |
    if [[ "$PR_AUTHOR" == "dependabot[bot]" ]]; then
      echo "pr_type=dependabot" >> "$GITHUB_OUTPUT"
      echo "::notice::Dependabot PR - using automation trust path"
    else
      echo "pr_type=contributor" >> "$GITHUB_OUTPUT"
      echo "::notice::Contributor PR - using CODEOWNERS trust path"
    fi
```

### 4. Check Contributor Trust

```yaml
- name: Check Contributor Trust
  id: trust
  env:
    GH_TOKEN: ${{ github.token }}
    PR_AUTHOR: ${{ steps.pr.outputs.author }}
    PR_TYPE: ${{ steps.detect.outputs.pr_type }}
  run: |
    TRUSTED=false

    if [[ "$PR_TYPE" == "dependabot" ]]; then
      # Dependabot is trusted by virtue of being the GitHub app
      TRUSTED=true
    else
      # Check CODEOWNERS for human contributors
      for CODEOWNERS_FILE in "CODEOWNERS" ".github/CODEOWNERS" "docs/CODEOWNERS"; do
        if [[ -f "$CODEOWNERS_FILE" ]]; then
          if grep -q "@$PR_AUTHOR" "$CODEOWNERS_FILE" 2>/dev/null; then
            echo "::notice::Author @$PR_AUTHOR found in $CODEOWNERS_FILE"
            TRUSTED=true
            break
          fi
        fi
      done
    fi

    echo "trusted=$TRUSTED" >> "$GITHUB_OUTPUT"
```

### 5. Verify Commit Signatures

```yaml
- name: Check Commit Signatures
  if: steps.trust.outputs.trusted == 'true'
  id: verify
  env:
    GH_TOKEN: ${{ github.token }}
    PR_NUMBER: ${{ steps.pr.outputs.number }}
  run: |
    # Get all commits in the PR
    COMMITS=$(gh pr view "$PR_NUMBER" \
      --repo "${{ github.repository }}" \
      --json commits \
      --jq '.commits[].oid')

    ALL_VERIFIED=true
    for SHA in $COMMITS; do
      VERIFIED=$(gh api "repos/${{ github.repository }}/commits/$SHA" \
        --jq '.commit.verification.verified')

      if [[ "$VERIFIED" != "true" ]]; then
        echo "::warning::Commit $SHA is not verified"
        ALL_VERIFIED=false
        break
      fi
    done

    echo "all_verified=$ALL_VERIFIED" >> "$GITHUB_OUTPUT"
```

### 6. Enable Auto-Merge

```yaml
- name: Enable Auto-Merge
  if: >-
    steps.pr.outputs.found == 'true' &&
    steps.trust.outputs.trusted == 'true' &&
    steps.verify.outputs.all_verified == 'true'
  uses: peter-evans/enable-pull-request-automerge@v3
  with:
    token: ${{ github.token }}
    pull-request-number: ${{ steps.pr.outputs.number }}
    merge-method: squash  # or 'merge', 'rebase'
```

## Trust Matrix

| Author Type | CODEOWNERS | Verified Commits | Auto-Merge? |
|-------------|------------|------------------|-------------|
| dependabot[bot] | N/A | Yes | Yes |
| dependabot[bot] | N/A | No | No |
| Contributor | Listed | Yes | Yes |
| Contributor | Listed | No | No |
| Contributor | Not listed | Yes | No |
| Contributor | Not listed | No | No |

## Complete Workflow

```yaml
name: Auto-Merge Integration PRs

on:
  workflow_run:
    workflows: ["Validate Contribution PR"]
    types: [completed]

permissions:
  contents: write
  pull-requests: write

jobs:
  enable-automerge:
    if: >-
      github.event.workflow_run.conclusion == 'success' &&
      github.event.workflow_run.event == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Get PR Information
        id: pr
        # ... (see above)

      - name: Detect PR Type
        if: steps.pr.outputs.found == 'true'
        id: detect
        # ... (see above)

      - name: Check Contributor Trust
        if: steps.pr.outputs.found == 'true'
        id: trust
        # ... (see above)

      - name: Check Commit Signatures
        if: steps.pr.outputs.found == 'true' && steps.trust.outputs.trusted == 'true'
        id: verify
        # ... (see above)

      - name: Enable Auto-Merge
        if: >-
          steps.pr.outputs.found == 'true' &&
          steps.trust.outputs.trusted == 'true' &&
          steps.verify.outputs.all_verified == 'true'
        uses: peter-evans/enable-pull-request-automerge@v3
        with:
          token: ${{ github.token }}
          pull-request-number: ${{ steps.pr.outputs.number }}
          merge-method: squash

      - name: Summary
        if: steps.pr.outputs.found == 'true'
        run: |
          # Generate job summary with pass/fail for each check
          echo "## Auto-Merge Status for PR #${{ steps.pr.outputs.number }}" >> "$GITHUB_STEP_SUMMARY"
          # ...
```

## Configuration

### Repository Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AUTO_MERGE_ALLOWED_BRANCHES` | Comma-separated base branches | `integration` |

### CODEOWNERS Format

```
# .github/CODEOWNERS
* @maintainer1 @maintainer2
/charts/ @chart-maintainer
/docs/ @docs-team
```

Contributors listed in CODEOWNERS are trusted for auto-merge.

## Adapting for Different Scenarios

### Multi-Branch Support

```yaml
ALLOWED_BASE_BRANCHES: "integration,staging,develop"
```

### Team-Based Trust

Instead of CODEOWNERS, check team membership:

```yaml
- name: Check Team Membership
  run: |
    TEAM_MEMBERS=$(gh api "orgs/$ORG/teams/$TEAM/members" --jq '.[].login')
    if echo "$TEAM_MEMBERS" | grep -q "^$PR_AUTHOR$"; then
      TRUSTED=true
    fi
```

### Skip for Draft PRs

```yaml
- name: Check Draft Status
  id: draft
  run: |
    IS_DRAFT=$(gh pr view "$PR_NUMBER" --json isDraft --jq '.isDraft')
    echo "is_draft=$IS_DRAFT" >> "$GITHUB_OUTPUT"

- name: Enable Auto-Merge
  if: steps.draft.outputs.is_draft != 'true'
  # ...
```

## Production Example

See [arustydev/helm-charts](https://github.com/arustydev/helm-charts) for a complete implementation:

- `.github/workflows/auto-merge-integration.yaml` - Full workflow
- `docs/src/adr/009-integration-auto-merge.md` - Architecture decision record

## Related

- [../SKILL.md](../SKILL.md) - Main skill file
- [github-app-tokens.md](github-app-tokens.md) - Elevated permissions when needed
- [linear-history.md](linear-history.md) - Branch protection strategy
- [peter-evans/enable-pull-request-automerge](https://github.com/peter-evans/enable-pull-request-automerge)
