# Linear History with GitHub Rulesets

Enforcing linear git history using GitHub Rulesets combined with rebase workflows and automated sync mechanisms.

## Overview

Linear history ensures a clean, auditable git log without merge commits. This requires:

1. **Rulesets**: Enforce linear history, block force pushes, require PRs
2. **Rebase workflow**: Contributors use rebase instead of merge
3. **Sync automation**: Prevent branch divergence
4. **GitHub App bypass**: Allow automation to perform privileged operations

## When to Use This Pattern

- Projects prioritizing clean, bisectable git history
- Repositories using conventional commits for changelog generation
- Teams that want clear audit trails for compliance
- Environments where each commit should be independently deployable

## Ruleset Configuration

### Protected Branches Ruleset

```json
{
  "name": "protected-branches-linear",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main", "refs/heads/integration", "refs/heads/release"]
    }
  },
  "rules": [
    {
      "type": "required_linear_history"
    },
    {
      "type": "deletion",
      "parameters": {
        "enabled": true
      }
    },
    {
      "type": "non_fast_forward",
      "parameters": {
        "enabled": true
      }
    }
  ],
  "bypass_actors": [
    {
      "actor_type": "Integration",
      "actor_id": "<your-github-app-id>",
      "bypass_mode": "always"
    }
  ]
}
```

### Main Branch Strict Ruleset

```json
{
  "name": "main-strict",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"]
    }
  },
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_last_push_approval": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          {"context": "lint"},
          {"context": "test"},
          {"context": "k8s-test (v1.32)"}
        ]
      }
    }
  ]
}
```

## Rebase Workflow for Contributors

### When PR Has Conflicts

```bash
# Fetch latest changes
git fetch origin

# Rebase your branch onto target
git rebase origin/integration

# If conflicts occur, resolve them
# ... fix conflicts in files ...
git add <resolved-files>
git rebase --continue

# Force push the rebased branch
git push --force-with-lease
```

### Documentation for Contributors

Include in CONTRIBUTING.md:

```markdown
## Keeping Your Branch Up to Date

This repository enforces linear history. To update your branch:

1. **Never use `git merge`** - this creates merge commits that are rejected
2. **Always use `git rebase`**:

   ```bash
   git fetch origin
   git rebase origin/integration
   git push --force-with-lease
   ```

3. If you encounter conflicts, resolve them and continue:

   ```bash
   git add <resolved-files>
   git rebase --continue
   git push --force-with-lease
   ```

### Why Rebase?

- Keeps history linear and easy to bisect
- Each commit is independently testable
- Changelogs are cleaner
- Simplifies rollbacks
```

## Sync Automation

Prevent divergence between branches:

### Sync Main to Integration

```yaml
name: Sync Main to Integration

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

permissions:
  contents: read

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Load secrets from 1Password
        id: op-secrets
        uses: 1password/load-secrets-action@v2
        env:
          OP_SERVICE_ACCOUNT_TOKEN: ${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}
          X_REPO_AUTH_APP_ID: op://gh-shared/xauth/app/id
          X_REPO_AUTH_PRIVATE_KEY: op://gh-shared/xauth/app/private-key.pem

      - name: Generate GitHub App Token
        id: app-token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ steps.op-secrets.outputs.X_REPO_AUTH_APP_ID }}
          private-key: ${{ steps.op-secrets.outputs.X_REPO_AUTH_PRIVATE_KEY }}

      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ steps.app-token.outputs.token }}

      - name: Configure Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Check Divergence
        id: check
        run: |
          git fetch origin main integration

          # Check if integration is behind main
          BEHIND=$(git rev-list --count origin/integration..origin/main)
          AHEAD=$(git rev-list --count origin/main..origin/integration)

          echo "behind=$BEHIND" >> "$GITHUB_OUTPUT"
          echo "ahead=$AHEAD" >> "$GITHUB_OUTPUT"

          if [[ "$BEHIND" -gt 0 && "$AHEAD" -gt 0 ]]; then
            echo "status=diverged" >> "$GITHUB_OUTPUT"
          elif [[ "$BEHIND" -gt 0 ]]; then
            echo "status=behind" >> "$GITHUB_OUTPUT"
          else
            echo "status=up-to-date" >> "$GITHUB_OUTPUT"
          fi

      - name: Fast-Forward Integration
        if: steps.check.outputs.status == 'behind'
        run: |
          git checkout integration
          git merge --ff-only origin/main
          git push origin integration

      - name: Handle Divergence
        if: steps.check.outputs.status == 'diverged'
        run: |
          echo "::warning::Integration has diverged from main"
          echo "Behind: ${{ steps.check.outputs.behind }} commits"
          echo "Ahead: ${{ steps.check.outputs.ahead }} commits"
          # Could create an issue, send alert, etc.
```

### Detect and Alert on Divergence

```yaml
- name: Create Divergence Issue
  if: steps.check.outputs.status == 'diverged'
  env:
    GH_TOKEN: ${{ steps.app-token.outputs.token }}
  run: |
    # Check if issue already exists
    EXISTING=$(gh issue list --label "divergence" --state open --json number --jq '.[0].number')

    if [[ -z "$EXISTING" ]]; then
      gh issue create \
        --title "Branch Divergence: integration vs main" \
        --label "divergence,urgent" \
        --body "## Branch Divergence Detected

    - **Integration behind main**: ${{ steps.check.outputs.behind }} commits
    - **Integration ahead of main**: ${{ steps.check.outputs.ahead }} commits

    ### Resolution

    1. Identify commits on integration that haven't been atomized
    2. Create atomic PRs for those commits
    3. Reset integration to main after all commits are processed

    \`\`\`bash
    git checkout integration
    git reset --hard origin/main
    git push origin integration --force
    \`\`\`

    *This requires GitHub App bypass permissions.*"
    fi
```

## Integration Branch Reset

When atomization is complete, reset integration to main:

```yaml
- name: Reset Integration to Main
  if: needs.process.outputs.all_atomized == 'true'
  env:
    GH_TOKEN: ${{ steps.app-token.outputs.token }}
  run: |
    git fetch origin main integration
    git checkout integration
    git reset --hard origin/main
    git push origin integration --force
```

This requires:
- GitHub App with bypass permissions
- Ruleset configured to allow the app to force push

## Hotfix Workflow

Emergency fixes that bypass the normal flow:

```yaml
name: Hotfix

on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number for the hotfix'
        required: true

jobs:
  create-hotfix:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout main
        uses: actions/checkout@v4
        with:
          ref: main
          token: ${{ secrets.APP_TOKEN }}

      - name: Create hotfix branch
        run: |
          git checkout -b "hotfix/${{ inputs.issue_number }}"
          git push origin "hotfix/${{ inputs.issue_number }}"
          echo "::notice::Created hotfix/${{ inputs.issue_number }}"

      - name: Create PR template
        env:
          GH_TOKEN: ${{ secrets.APP_TOKEN }}
        run: |
          gh pr create \
            --base main \
            --head "hotfix/${{ inputs.issue_number }}" \
            --title "fix: hotfix for #${{ inputs.issue_number }}" \
            --body "## Hotfix

    Fixes #${{ inputs.issue_number }}

    ### Checklist
    - [ ] Emergency fix implemented
    - [ ] Tests pass
    - [ ] Ready for expedited review" \
            --draft
```

## Ruleset UI vs API

### Create via UI

1. Settings > Rules > Rulesets > New ruleset
2. Name: `protected-branches-linear`
3. Enforcement: Active
4. Target branches: Add `main`, `integration`, `release`
5. Rules:
   - Require linear history
   - Block deletions
   - Block force pushes
6. Bypass list: Add your GitHub App

### Create via API

```bash
gh api "repos/$OWNER/$REPO/rulesets" \
  --method POST \
  --input ruleset.json
```

## Adapting for Different Branching Models

### GitFlow-Style

```json
{
  "conditions": {
    "ref_name": {
      "include": [
        "refs/heads/main",
        "refs/heads/develop",
        "refs/heads/release/*"
      ]
    }
  }
}
```

### Trunk-Based Development

```json
{
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"]
    }
  }
}
```

### Multi-Environment

```json
{
  "conditions": {
    "ref_name": {
      "include": [
        "refs/heads/main",
        "refs/heads/staging",
        "refs/heads/production"
      ]
    }
  }
}
```

## Production Example

See [arustydev/helm-charts](https://github.com/arustydev/helm-charts) for a complete implementation:

- `docs/src/adr/010-linear-history-rebase.md` - Architecture decision record
- `.github/workflows/sync-main-to-branches.yaml` - Sync automation
- `CONTRIBUTING.md` - Contributor rebase instructions

## Related

- [../SKILL.md](../SKILL.md) - Main skill file
- [github-app-tokens.md](github-app-tokens.md) - Required for bypass operations
- [atomic-releases.md](atomic-releases.md) - Works with linear history
- [multi-stage-pipelines.md](multi-stage-pipelines.md) - Pipeline architecture
