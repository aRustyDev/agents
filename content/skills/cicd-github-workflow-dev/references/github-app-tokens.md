# GitHub App Token Pattern

Using GitHub App tokens for elevated permissions in workflows that need to bypass branch protection, trigger other workflows, or perform privileged operations.

## Overview

The default `GITHUB_TOKEN` has limitations that prevent certain automation scenarios. A GitHub App token acts as a first-class GitHub App with configurable permissions, enabling:

- **Bypass branch protection**: Push to protected branches via ruleset bypass
- **Trigger workflows**: PRs/commits trigger `on: push` and `on: pull_request`
- **Cross-repo operations**: Access multiple repositories (when configured)
- **Custom identity**: Actions attributed to the app, not `github-actions[bot]`

## When to Use This Pattern

| Operation | GITHUB_TOKEN | App Token |
|-----------|--------------|-----------|
| Read repository contents | Yes | Yes |
| Create PRs | Yes | Yes |
| Push to protected branches | No | Yes |
| Bypass ruleset rules | No | Yes |
| Trigger other workflows | No | Yes |
| Force push (when needed) | No | Yes |
| Cross-repo access | No | Yes |

## Secret Management Options

### Option A: 1Password Integration (Recommended)

Centralized secret management with automatic rotation support:

```yaml
jobs:
  generate-token:
    runs-on: ubuntu-latest
    outputs:
      token: ${{ steps.app-token.outputs.token }}
    steps:
      - name: Load secrets from 1Password
        id: op-secrets
        uses: 1password/load-secrets-action@v2
        with:
          export-env: false
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
```

**Benefits:**
- Centralized across repositories
- Audit trail for secret access
- No need to duplicate secrets per repo
- Supports secret rotation

### Option B: GitHub Secrets

Direct storage in repository secrets:

```yaml
jobs:
  generate-token:
    runs-on: ubuntu-latest
    outputs:
      token: ${{ steps.app-token.outputs.token }}
    steps:
      - name: Generate GitHub App Token
        id: app-token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
```

## Consuming the Token

### In Dependent Jobs

```yaml
my-job:
  needs: [generate-token]
  runs-on: ubuntu-latest
  steps:
    - name: Checkout with App Token
      uses: actions/checkout@v4
      with:
        token: ${{ needs.generate-token.outputs.token }}

    - name: Use gh CLI
      env:
        GH_TOKEN: ${{ needs.generate-token.outputs.token }}
      run: |
        gh pr create --title "Automated PR" --body "Created with app token"
```

### For Git Push Operations

```yaml
- name: Push to Protected Branch
  env:
    GH_TOKEN: ${{ needs.generate-token.outputs.token }}
  run: |
    git remote set-url origin "https://x-access-token:${GH_TOKEN}@github.com/${{ github.repository }}.git"
    git push origin my-branch --force-with-lease
```

### Within Same Job

```yaml
- name: Load secrets from 1Password
  id: op-secrets
  uses: 1password/load-secrets-action@v2
  # ...

- name: Generate GitHub App Token
  id: app-token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ steps.op-secrets.outputs.X_REPO_AUTH_APP_ID }}
    private-key: ${{ steps.op-secrets.outputs.X_REPO_AUTH_PRIVATE_KEY }}

- name: Checkout with Token
  uses: actions/checkout@v4
  with:
    token: ${{ steps.app-token.outputs.token }}
```

## GitHub App Configuration

### Required Permissions

Configure in your GitHub App settings:

| Permission | Access | Use Case |
|------------|--------|----------|
| Contents | Read & Write | Push commits, create branches |
| Pull requests | Read & Write | Create/update PRs |
| Issues | Read & Write | Create issues |
| Metadata | Read | Required for all apps |

### Ruleset Bypass Configuration

To allow the app to bypass branch protection:

1. Navigate to: **Settings > Rules > Rulesets > [Your Ruleset]**
2. Scroll to **Bypass list**
3. Click **Add bypass**
4. Select your GitHub App
5. Set bypass mode to **Always**

## Token Scoping

By default, tokens are scoped to the current repository only:

```yaml
# Default: current repository only
- uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
```

For cross-repository access (use sparingly):

```yaml
# Explicit multi-repo scope
- uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
    repositories: "repo1,repo2"
```

## Complete Example

Version bump workflow that pushes to a PR branch:

```yaml
name: Version Bump

on:
  pull_request:
    branches: [main]

permissions:
  contents: read  # Minimal for GITHUB_TOKEN

jobs:
  version-bump:
    runs-on: ubuntu-latest
    steps:
      - name: Load secrets from 1Password
        id: op-secrets
        uses: 1password/load-secrets-action@v3
        with:
          export-env: false
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

      - name: Checkout PR Branch
        uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
          fetch-depth: 0
          token: ${{ steps.app-token.outputs.token }}

      - name: Configure Git
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

      - name: Bump Version
        run: |
          # Your version bump logic
          ./scripts/bump-version.sh

      - name: Commit and Push
        run: |
          git add .
          git commit -m "chore: bump version"
          git push origin HEAD:${{ github.head_ref }}
```

## Security Considerations

1. **Principle of least privilege**: Only request permissions the app needs
2. **Repository scoping**: Keep default single-repo scope unless cross-repo required
3. **Secret management**: Use 1Password or similar for centralized management
4. **Audit trail**: All actions with app token are attributed to the app
5. **Token lifetime**: Tokens are short-lived (1 hour by default)

## Common Use Cases

### Pushing Version Bumps to PR Branches

```yaml
- name: Commit Version Bump
  if: steps.bump.outputs.bumped == 'true'
  run: |
    git add Chart.yaml CHANGELOG.md
    git commit -m "chore(release): bump version"
    git push origin HEAD:${{ github.head_ref }}
```

### Creating PRs That Trigger Other Workflows

```yaml
- name: Create PR
  env:
    GH_TOKEN: ${{ needs.generate-token.outputs.token }}
  run: |
    gh pr create \
      --title "chore: automated update" \
      --body "This PR will trigger validation workflows"
```

### Deleting Protected Branches

```yaml
- name: Delete Source Branch
  env:
    GH_TOKEN: ${{ steps.app-token.outputs.token }}
  run: |
    git push origin --delete "${{ github.event.pull_request.head.ref }}"
```

### Force Push to Reset Branches

```yaml
- name: Reset Integration to Main
  env:
    GH_TOKEN: ${{ steps.app-token.outputs.token }}
  run: |
    git fetch origin main
    git checkout integration
    git reset --hard origin/main
    git push origin integration --force
```

## Production Example

See [arustydev/helm-charts](https://github.com/arustydev/helm-charts) for a complete implementation:

- `.github/workflows/validate-atomic-chart-pr.yaml` - Version bump with app token
- `docs/src/ci/github-app-auth.md` - Full authentication guide
- `docs/src/adr/012-github-app-token-pattern.md` - Architecture decision record

## Related

- [../SKILL.md](../SKILL.md) - Main skill file
- [trust-based-auto-merge.md](trust-based-auto-merge.md) - Auto-merge pattern
- [linear-history.md](linear-history.md) - Branch protection that requires app tokens
- [actions/create-github-app-token](https://github.com/actions/create-github-app-token)
- [1password/load-secrets-action](https://github.com/1password/load-secrets-action)
