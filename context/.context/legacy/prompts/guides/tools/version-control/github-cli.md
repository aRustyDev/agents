---
name: GitHub CLI (gh) Guide
module_type: guide
scope: temporary
priority: low
triggers: ["gh", "github cli", "gh command", "github api", "create pr", "github issue"]
dependencies: []
conflicts: []
version: 1.0.0
---

# GitHub CLI (gh) Guide

## Purpose
The GitHub CLI brings GitHub functionality to your terminal, enabling issue management, PR creation, repository operations, and API access without leaving the command line.

## Installation Check
```bash
# Check if installed
command -v gh || echo "GitHub CLI not installed"

# Install commands
# macOS: brew install gh
# Ubuntu: sudo apt install gh
# Windows: winget install GitHub.cli

# Authenticate
gh auth login
gh auth status
```

## Basic Usage

### Repository Operations
```bash
# Clone repository
gh repo clone owner/repo

# Create repository
gh repo create my-project --public --clone

# Fork repository
gh repo fork owner/repo --clone

# View repository
gh repo view owner/repo --web
```

### Issue Management
```bash
# List issues
gh issue list
gh issue list --assignee @me
gh issue list --label bug
gh issue list --state closed

# View issue details
gh issue view 123
gh issue view 123 --comments

# Create issue
gh issue create --title "Bug: Application crashes" --body "Details here"

# Create with template
gh issue create --template bug_report.md

# Update issue
gh issue edit 123 --add-label priority:high
gh issue edit 123 --add-assignee @me
gh issue close 123
gh issue reopen 123
```

### Pull Request Operations
```bash
# List PRs
gh pr list
gh pr list --state merged
gh pr list --author @me

# Create PR
gh pr create --title "Feature: Add login" --body "Description"

# Create with template
gh pr create --template feature_pr.md

# Create as draft
gh pr create --draft

# View PR
gh pr view 123
gh pr view 123 --comments

# Check out PR
gh pr checkout 123

# Review PR
gh pr review 123 --approve
gh pr review 123 --request-changes --body "See comments"
gh pr review 123 --comment --body "Looks good"

# Merge PR
gh pr merge 123 --merge
gh pr merge 123 --squash
gh pr merge 123 --rebase
```

## Advanced Features

### Working with Workflows
```bash
# List workflow runs
gh run list

# View run details
gh run view 12345

# Watch run progress
gh run watch 12345

# Rerun failed jobs
gh run rerun 12345 --failed

# Download artifacts
gh run download 12345
```

### API Access
```bash
# Direct API calls
gh api repos/:owner/:repo/issues
gh api graphql -f query='{ viewer { login } }'

# With pagination
gh api repos/:owner/:repo/issues --paginate

# POST requests
gh api repos/:owner/:repo/issues \
  --method POST \
  --field title="New Issue" \
  --field body="Issue description"
```

### Alias Creation
```bash
# Create custom commands
gh alias set prs 'pr list --author @me'
gh alias set bugs 'issue list --label bug'
gh alias set review 'pr review --approve'

# List aliases
gh alias list

# Delete alias
gh alias delete prs
```

## Common Workflows

### Feature Development
```bash
# 1. Create issue
gh issue create --title "Feature: User authentication"

# 2. Create branch and start work
git checkout -b feature/auth

# 3. Create PR when ready
gh pr create --title "Add user authentication" \
  --body "Implements login/logout functionality\n\nFixes #123"

# 4. Request review
gh pr edit --add-reviewer teammate1,teammate2

# 5. Check status
gh pr checks

# 6. Merge when approved
gh pr merge --squash --delete-branch
```

### Bug Fixing
```bash
# 1. Find bug issue
gh issue list --label bug --limit 10

# 2. Assign to yourself
gh issue edit 456 --add-assignee @me

# 3. Create fix branch
git checkout -b fix/456-crash-on-login

# 4. Create PR linking to issue
gh pr create --title "Fix: Crash on login" \
  --body "Fixes null pointer exception\n\nFixes #456"
```

### Code Review
```bash
# 1. List PRs needing review
gh pr list --search "review:required"

# 2. Check out PR
gh pr checkout 789

# 3. Run tests locally
make test

# 4. Add review comments
gh pr review 789 --comment \
  --body "Consider extracting this to a method"

# 5. Approve or request changes
gh pr review 789 --approve \
  --body "LGTM! Nice work"
```

## Configuration

### Set Default Editor
```bash
gh config set editor vim
gh config set editor "code --wait"
```

### Set Default Browser
```bash
gh config set browser firefox
```

### Configure PR Creation
```bash
# Always create draft PRs
gh config set prompt disabled

# Set default base branch
git config --global init.defaultBranch main
```

### GitHub Actions Integration
```bash
# Trigger workflow manually
gh workflow run deploy.yml --ref main

# With inputs
gh workflow run test.yml \
  -f environment=staging \
  -f version=1.2.3
```

## Tips and Tricks

### Filtering and Formatting
```bash
# JSON output
gh issue list --json number,title,author

# Format with template
gh issue list --json number,title \
  --template '{{range .}}{{.number}}: {{.title}}{{"\n"}}{{end}}'

# Export to CSV
gh issue list --json number,title,state \
  --jq '.[] | [.number, .title, .state] | @csv'
```

### Batch Operations
```bash
# Close multiple issues
gh issue list --label wontfix --json number \
  --jq '.[].number' | xargs -I {} gh issue close {}

# Add label to multiple PRs
gh pr list --author @me --json number \
  --jq '.[].number' | xargs -I {} gh pr edit {} --add-label needs-review
```

### Search Examples
```bash
# Complex issue search
gh issue list --search "label:bug state:open created:>2024-01-01"

# PR search
gh pr list --search "review:approved base:main"

# Cross-repository search
gh search issues "org:myorg label:help-wanted"
```

## Best Practices

### DO
- ✅ Use templates for consistency
- ✅ Link PRs to issues
- ✅ Set up aliases for common operations
- ✅ Use `--web` flag when GUI needed
- ✅ Leverage JSON output for scripting

### DON'T
- ❌ Hardcode repository names in scripts
- ❌ Skip PR templates
- ❌ Merge without CI passing
- ❌ Use personal access tokens when gh auth works
- ❌ Ignore rate limits for API calls

## Troubleshooting

### Authentication Issues
```bash
# Re-authenticate
gh auth logout
gh auth login

# Check token scopes
gh auth status

# Use different account
gh auth login --hostname github.com
```

### API Rate Limits
```bash
# Check rate limit
gh api rate_limit

# Use pagination to reduce calls
gh api repos/:owner/:repo/issues \
  --paginate \
  --per-page 100
```

### Common Errors
```bash
# Wrong repository context
gh repo set-default owner/repo

# Missing permissions
gh auth refresh -s read:org,repo

# SSL issues
gh config set git_protocol ssh
```

## Integration Examples

### With Git Hooks
```bash
#!/bin/bash
# pre-push hook that checks PR status
branch=$(git branch --show-current)
pr_number=$(gh pr list --head "$branch" --json number -q '.[0].number')

if [ -n "$pr_number" ]; then
    checks=$(gh pr checks "$pr_number" --json status -q '.[].status')
    if echo "$checks" | grep -q "FAILURE"; then
        echo "PR #$pr_number has failing checks. Push anyway? (y/n)"
        read -r response
        [ "$response" != "y" ] && exit 1
    fi
fi
```

### In Scripts
```bash
#!/bin/bash
# Script to create release notes
latest_tag=$(git describe --tags --abbrev=0)
prs=$(gh pr list --state merged --search "merged:>=$latest_tag" \
  --json number,title --template '{{range .}}- #{{.number}}: {{.title}}{{"\n"}}{{end}}')

gh release create "v$1" --notes "## Changes\n\n$prs"
```

---
*The GitHub CLI transforms GitHub workflows by bringing the full power of GitHub to your terminal, enabling faster and more efficient development cycles.*