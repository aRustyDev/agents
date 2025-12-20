---
module: GitErrorHandler
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - base-error-handler.md
  - error-categories.yaml
---

# Git Error Handler

## Purpose
Specialized error handling for git operations with git-specific context and recovery suggestions.

## Overview
Extends the base error handler with git-specific functionality, including repository state checks and git-aware recovery suggestions.

## Git-Specific Functions

### check_git_repo
Validates that we're in a git repository before attempting git operations.

```bash
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        handle_error "3001" "$(pwd)"
    fi
}
```

### check_clean_working_tree
Ensures working tree is clean before operations that require it.

```bash
check_clean_working_tree() {
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        local changes=$(git status --porcelain | wc -l)
        handle_error "3002" "Working tree has uncommitted changes" "$changes files modified"
    fi
}
```

### check_branch_exists
Verifies a branch exists before attempting to switch or merge.

```bash
check_branch_exists() {
    local branch="$1"
    local remote="${2:-origin}"
    
    if ! git show-ref --verify --quiet "refs/heads/$branch"; then
        if ! git show-ref --verify --quiet "refs/remotes/$remote/$branch"; then
            handle_error "3003" "Branch not found" "Neither local nor remote branch '$branch' exists"
        fi
    fi
}
```

### handle_merge_conflict
Provides detailed information when merge conflicts occur.

```bash
handle_merge_conflict() {
    local conflicted_files=$(git diff --name-only --diff-filter=U)
    local conflict_count=$(echo "$conflicted_files" | wc -l)
    
    handle_error "3004" "Merge conflict in $conflict_count files" "$conflicted_files"
}
```

### safe_git_operation
Wraps git operations with appropriate error handling.

```bash
safe_git_operation() {
    local operation="$1"
    shift
    local args="$@"
    
    case "$operation" in
        "push")
            if ! git push $args 2>&1; then
                if git remote -v | grep -q origin; then
                    handle_error "3005" "git push $args"
                else
                    handle_error "3006" "No remote repository configured"
                fi
            fi
            ;;
        "pull")
            if ! git pull $args 2>&1; then
                handle_error "3005" "git pull $args"
            fi
            ;;
        "checkout")
            if ! git checkout $args 2>&1; then
                handle_error "3003" "git checkout $args"
            fi
            ;;
        "merge")
            if ! git merge $args 2>&1; then
                if git status | grep -q "You have unmerged paths"; then
                    handle_merge_conflict
                else
                    handle_error "3005" "git merge $args"
                fi
            fi
            ;;
        *)
            if ! git $operation $args 2>&1; then
                handle_error "3005" "git $operation $args"
            fi
            ;;
    esac
}
```

### ensure_upstream_set
Ensures current branch has upstream tracking configured.

```bash
ensure_upstream_set() {
    local branch=$(git branch --show-current)
    local upstream=$(git for-each-ref --format='%(upstream:short)' "refs/heads/$branch")
    
    if [ -z "$upstream" ]; then
        handle_error "3006" "Branch '$branch' has no upstream"
    fi
}
```

## Usage Examples

### Pre-operation Checks
```bash
# Before any git operation
check_git_repo

# Before operations requiring clean tree
check_clean_working_tree

# Before switching branches
check_branch_exists "feature/new-feature"
```

### Safe Git Operations
```bash
# Safe push with automatic error handling
safe_git_operation push origin main

# Safe checkout
safe_git_operation checkout -b feature/new-feature

# Safe merge
safe_git_operation merge origin/main
```

### Complex Git Workflows
```bash
# Example: Safe feature branch workflow
create_feature_branch() {
    local branch_name="$1"
    
    check_git_repo
    check_clean_working_tree
    
    # Create and checkout branch
    safe_git_operation checkout -b "$branch_name"
    
    # Push and set upstream
    safe_git_operation push -u origin "$branch_name"
}
```

## Integration with CI/CD

The git error handler can be particularly useful in CI/CD pipelines:

```bash
# CI/CD safe deployment
deploy_to_production() {
    check_git_repo
    check_clean_working_tree
    ensure_upstream_set
    
    # Ensure we're on main branch
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        handle_error "3003" "Not on main branch" "Current branch: $current_branch"
    fi
    
    # Safe deployment
    safe_git_operation pull origin main
    safe_git_operation tag -a "v$VERSION" -m "Release version $VERSION"
    safe_git_operation push origin "v$VERSION"
}
```

## Best Practices

1. **Always check repository state** before git operations
2. **Use safe wrappers** for all git commands in scripts
3. **Provide context** about what was being attempted
4. **Include branch/file information** in error messages
5. **Test error scenarios** to ensure proper handling