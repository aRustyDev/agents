---
description: Promote a local GitHub Action to aRustyDev/gha via Issue+PR, optionally publish to Marketplace
argument-hint: <action-name> [--marketplace] [--skip-validation]
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Bash(npm:*), Bash(ls:*), Bash(cat:*), Bash(cp:*), Bash(cd:*), Glob, Grep, AskUserQuestion, TodoWrite
---

# Promote GitHub Action

Promote a locally developed GitHub Action to the central `aRustyDev/gha` repository via Issue+PR. Optionally publish to the GitHub Marketplace.

## Arguments

- `$1` - Action name (must exist in `.github/actions/<action-name>/`)
- `--marketplace` - Also publish to GitHub Marketplace after PR is merged
- `--skip-validation` - Skip pre-promotion validation checks

## Prerequisites

- Action exists locally in `.github/actions/<action-name>/`
- Action has been tested and works
- `gh` CLI is authenticated
- Access to `aRustyDev/gha` repository

## Workflow

### Phase 1: Locate and Validate Action

**Use TodoWrite to track progress.**

1. **Locate action**:
   ```bash
   ACTION_PATH=".github/actions/$1"
   if [ ! -d "$ACTION_PATH" ]; then
     echo "Action not found at $ACTION_PATH"
     exit 1
   fi
   ```

2. **Validate action structure** (unless `--skip-validation`):

   | Check | Requirement |
   |-------|-------------|
   | action.yml exists | Required |
   | action.yml has name | Required |
   | action.yml has description | Required |
   | action.yml has branding | Required for Marketplace |
   | README.md exists | Recommended |
   | dist/ is built (TypeScript) | Required |
   | Tests pass | Recommended |

3. **Extract action metadata**:
   ```bash
   ACTION_NAME=$(yq '.name' "$ACTION_PATH/action.yml")
   ACTION_DESC=$(yq '.description' "$ACTION_PATH/action.yml")
   ACTION_TYPE=$(yq '.runs.using' "$ACTION_PATH/action.yml")
   ```

4. **Check for existing action in gha repo**:
   ```bash
   gh api repos/aRustyDev/gha/contents/$1 2>/dev/null && echo "EXISTS" || echo "NEW"
   ```

### Phase 2: Pre-Promotion Checklist

Present checklist to user for confirmation:

```
## Pre-Promotion Checklist

| Check | Status |
|-------|--------|
| Action tested locally | ⬜ Confirm |
| Tests pass | ⬜ Confirm |
| Documentation complete | ⬜ Confirm |
| No secrets/sensitive data | ⬜ Confirm |
| Branding configured | ✅ / ❌ |

Ready to promote? [Yes / No]
```

If user confirms, proceed. Otherwise, list what needs to be fixed.

### Phase 3: Create Issue in aRustyDev/gha

```bash
ISSUE_BODY=$(cat <<'EOF'
## New Action: $ACTION_NAME

**Description**: $ACTION_DESC

**Type**: $ACTION_TYPE

**Source Repository**: $CURRENT_REPO

**Checklist**:
- [ ] Action tested locally
- [ ] Tests pass
- [ ] Documentation complete
- [ ] action.yml has branding
- [ ] No secrets or sensitive data included

**Files to add**:
```
$1/
├── action.yml
├── dist/          # For TypeScript actions
├── README.md
└── ...
```

**Usage after merge**:
```yaml
- uses: aRustyDev/gha/$1@v1
```
EOF
)

gh issue create \
  --repo aRustyDev/gha \
  --title "feat: add $1 action" \
  --body "$ISSUE_BODY"
```

Store the issue number for the PR.

### Phase 4: Create Branch and Copy Files

1. **Determine gha repo location**:
   ```bash
   GHA_REPO="${GHA_REPO_PATH:-$HOME/repos/gha}"

   if [ ! -d "$GHA_REPO" ]; then
     echo "aRustyDev/gha repo not found at $GHA_REPO"
     echo "Clone it or set GHA_REPO_PATH environment variable"

     # Offer to clone
     gh repo clone aRustyDev/gha "$GHA_REPO"
   fi
   ```

2. **Create feature branch**:
   ```bash
   cd "$GHA_REPO"
   git fetch origin
   git checkout main
   git pull origin main
   git checkout -b "feat/add-$1"
   ```

3. **Copy action files**:
   ```bash
   # Copy entire action directory
   cp -r "$ORIGINAL_REPO/.github/actions/$1" "./$1"

   # For TypeScript actions, ensure dist/ is included
   # For Docker actions, ensure Dockerfile is included
   ```

4. **Update README if action has usage examples**:
   - Update `uses:` references from `./.github/actions/<name>` to `aRustyDev/gha/<name>@v1`

### Phase 5: Commit and Create PR

1. **Stage and commit**:
   ```bash
   git add "$1/"
   git commit -m "feat: add $1 action

   ### Added
   - $1 action: $ACTION_DESC

   Closes #$ISSUE_NUMBER

   🤖 Generated with Claude Code"
   ```

2. **Push branch**:
   ```bash
   git push -u origin "feat/add-$1"
   ```

3. **Create PR**:
   ```bash
   gh pr create \
     --repo aRustyDev/gha \
     --title "feat: add $1 action" \
     --body "$(cat <<EOF
   Closes #$ISSUE_NUMBER

   ## Summary
   Adds the \`$1\` action to the central repository.

   **Description**: $ACTION_DESC

   ## Usage
   \`\`\`yaml
   - uses: aRustyDev/gha/$1@v1
     with:
       token: \${{ secrets.GITHUB_TOKEN }}
   \`\`\`

   ## Checklist
   - [x] Action tested in source repository
   - [x] Documentation included
   - [x] Branding configured

   🤖 Generated with Claude Code
   EOF
   )"
   ```

### Phase 6: Marketplace Publishing (if --marketplace)

**Only run if `--marketplace` flag is set.**

#### 6.1 Marketplace Requirements

Verify action meets Marketplace requirements:

| Requirement | Check |
|-------------|-------|
| Public repository | ✅ aRustyDev/gha is public |
| action.yml in repo root or action directory | ✅ |
| Unique action name | Verify |
| Branding (icon + color) | Required |
| README.md | Required |
| LICENSE file | Required (in repo) |

#### 6.2 Post-Merge Marketplace Steps

After PR is merged:

1. **Create a release**:
   ```bash
   cd "$GHA_REPO"
   git checkout main
   git pull origin main

   # Tag the release
   gh release create "$1-v1.0.0" \
     --title "$ACTION_NAME v1.0.0" \
     --notes "Initial release of $1 action.

   ## Usage
   \`\`\`yaml
   - uses: aRustyDev/gha/$1@v1
   \`\`\`
   " \
     --target main
   ```

2. **Create major version tag**:
   ```bash
   git tag -fa "$1-v1" -m "Update $1-v1 tag"
   git push origin "$1-v1" --force
   ```

3. **Publish to Marketplace**:
   - Go to the release on GitHub
   - Click "Edit"
   - Check "Publish this Action to the GitHub Marketplace"
   - Select categories
   - Save

#### 6.3 Marketplace Notes

- For monorepo actions (multiple actions in one repo), each action can be published separately
- Users reference as `uses: aRustyDev/gha/<action-name>@v1`
- Major version tags (`v1`) should be updated with each release for easy upgrades

### Phase 7: Report

```
## Action Promoted

| Field | Value |
|-------|-------|
| Action | `$1` |
| Issue | aRustyDev/gha#$ISSUE_NUMBER |
| PR | aRustyDev/gha#$PR_NUMBER |
| Branch | `feat/add-$1` |

**Usage (after PR merge)**:
\`\`\`yaml
- uses: aRustyDev/gha/$1@v1
\`\`\`

**Next steps**:
1. Review and merge the PR
2. Create a release tag (if not using --marketplace)
3. Update consuming workflows to use the published action
4. (If --marketplace) Publish to GitHub Marketplace via release page
```

## Updating an Existing Action

If the action already exists in aRustyDev/gha:

1. **Create update branch**:
   ```bash
   git checkout -b "feat/update-$1"
   ```

2. **Copy updated files**:
   ```bash
   rm -rf "./$1"
   cp -r "$ORIGINAL_REPO/.github/actions/$1" "./$1"
   ```

3. **Bump version in action.yml** (if applicable)

4. **Create PR with update notes**

5. **After merge, update version tags**

## Examples

**Promote action to central repo:**
```
/promote-gha setup-rust
```

**Promote and publish to Marketplace:**
```
/promote-gha label-pr --marketplace
```

**Skip validation (use with caution):**
```
/promote-gha my-action --skip-validation
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GHA_REPO_PATH` | `$HOME/repos/gha` | Path to local aRustyDev/gha clone |

## Troubleshooting

**"aRustyDev/gha repo not found":**
- Clone the repo: `gh repo clone aRustyDev/gha ~/repos/gha`
- Or set `GHA_REPO_PATH` to your clone location

**"Action not found":**
- Ensure action exists at `.github/actions/<action-name>/`
- Run `/create-gha <action-name>` first

**"gh: permission denied":**
- Authenticate gh CLI: `gh auth login`
- Ensure you have write access to aRustyDev/gha

**PR creation fails:**
- Check if branch already exists: `git branch -a | grep feat/add-<name>`
- Delete old branch if needed: `git push origin --delete feat/add-<name>`

## Related Commands

- `/create-gha` - Create a new GitHub Action locally for development

## Notes

- Always test actions locally before promoting
- Use semantic versioning for releases (v1.0.0, v1.1.0, v2.0.0)
- Keep major version tags updated for easy consumer upgrades
- Marketplace publishing requires manual steps after PR merge
