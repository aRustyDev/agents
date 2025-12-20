---
module: BranchOperations
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - ../error-handling/base-error-handler.md
  - ../error-handling/git-errors.md
  - ../validation/input-validator.md
---

# Branch Operations

## Purpose
Provides standardized git branch operations including creation, switching, merging, and branch management.

## Overview
This module encapsulates branch-related git operations with validation, protection checks, and proper error handling.

## Branch Creation

### create_branch
Creates a new branch with validation.

```bash
create_branch() {
    local branch_name="$1"
    local start_point="${2:-HEAD}"
    local switch="${3:-true}"
    
    # Validate branch name
    validate_branch_name "branch_name" "$branch_name" || return 1
    
    # Check if branch already exists
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        handle_error "3003" "$branch_name" "Branch already exists"
        return 1
    fi
    
    # Create branch
    echo "Creating branch: $branch_name"
    if ! git branch "$branch_name" "$start_point" 2>&1; then
        handle_error "3003" "git branch" "$branch_name"
        return 1
    fi
    
    # Switch to branch if requested
    if [ "$switch" = "true" ]; then
        switch_branch "$branch_name"
    fi
    
    echo "Branch created: $branch_name"
    return 0
}
```

### create_feature_branch
Creates a feature branch with naming convention.

```bash
create_feature_branch() {
    local feature_name="$1"
    local prefix="${2:-feature}"
    
    # Validate feature name
    validate_required "feature_name" "$feature_name" || return 1
    
    # Sanitize feature name
    local safe_name=$(echo "$feature_name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')
    local branch_name="$prefix/$safe_name"
    
    # Ensure we're on the default branch
    local default_branch=$(get_default_branch)
    if ! switch_branch "$default_branch"; then
        return 1
    fi
    
    # Pull latest changes
    echo "Updating $default_branch..."
    if ! git pull origin "$default_branch" 2>&1; then
        echo "Warning: Failed to pull latest changes"
    fi
    
    # Create and switch to feature branch
    create_branch "$branch_name" "$default_branch" true
}
```

### create_release_branch
Creates a release branch with version.

```bash
create_release_branch() {
    local version="$1"
    local prefix="${2:-release}"
    
    # Validate version format
    validate_format "version" "$version" "semver" || return 1
    
    # Check for uncommitted changes
    check_clean_working_tree || return 1
    
    local branch_name="$prefix/$version"
    
    # Create from main/master
    local default_branch=$(get_default_branch)
    create_branch "$branch_name" "$default_branch" true
    
    # Tag the branch point
    git tag -a "v$version-start" -m "Start of release $version"
    
    echo "Release branch created: $branch_name"
}
```

## Branch Switching

### switch_branch
Switches to a branch with safety checks.

```bash
switch_branch() {
    local branch_name="$1"
    local force="${2:-false}"
    
    # Check if already on target branch
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" = "$branch_name" ]; then
        echo "Already on branch: $branch_name"
        return 0
    fi
    
    # Check for uncommitted changes
    if [ "$force" != "true" ] && ! git diff-index --quiet HEAD -- 2>/dev/null; then
        handle_error "3002" "Uncommitted changes" "Use stash or commit before switching"
        return 1
    fi
    
    # Check if branch exists
    check_branch_exists "$branch_name" || return 1
    
    # Switch branch
    echo "Switching to branch: $branch_name"
    if ! git checkout "$branch_name" 2>&1; then
        handle_error "3003" "git checkout" "$branch_name"
        return 1
    fi
    
    # Show branch info
    echo "Switched to branch: $branch_name"
    git log --oneline -n 1
    
    return 0
}
```

### checkout_remote_branch
Checks out a remote branch as a local branch.

```bash
checkout_remote_branch() {
    local branch_name="$1"
    local remote="${2:-origin}"
    
    # Check if local branch exists
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        echo "Local branch already exists: $branch_name"
        switch_branch "$branch_name"
        return $?
    fi
    
    # Check if remote branch exists
    if ! git show-ref --verify --quiet "refs/remotes/$remote/$branch_name"; then
        handle_error "3003" "Remote branch not found" "$remote/$branch_name"
        return 1
    fi
    
    # Create and switch to local branch tracking remote
    echo "Checking out remote branch: $remote/$branch_name"
    if ! git checkout -b "$branch_name" "$remote/$branch_name" 2>&1; then
        handle_error "3003" "git checkout" "$branch_name"
        return 1
    fi
    
    echo "Tracking remote branch: $remote/$branch_name"
    return 0
}
```

## Branch Merging

### merge_branch
Merges a branch with conflict handling.

```bash
merge_branch() {
    local source_branch="$1"
    local target_branch="${2:-$(git branch --show-current)}"
    local strategy="${3:-}"
    local no_ff="${4:-false}"
    
    # Validate branches exist
    check_branch_exists "$source_branch" || return 1
    check_branch_exists "$target_branch" || return 1
    
    # Switch to target branch
    if ! switch_branch "$target_branch"; then
        return 1
    fi
    
    # Build merge command
    local merge_cmd="git merge"
    [ -n "$strategy" ] && merge_cmd="$merge_cmd --strategy=$strategy"
    [ "$no_ff" = "true" ] && merge_cmd="$merge_cmd --no-ff"
    merge_cmd="$merge_cmd $source_branch"
    
    # Attempt merge
    echo "Merging $source_branch into $target_branch..."
    if ! $merge_cmd 2>&1; then
        # Check for conflicts
        if git status | grep -q "You have unmerged paths"; then
            handle_merge_conflict
            echo ""
            echo "Resolve conflicts and run:"
            echo "  git add <resolved-files>"
            echo "  git commit"
            return 1
        else
            handle_error "3005" "git merge" "$source_branch"
            return 1
        fi
    fi
    
    echo "Successfully merged $source_branch into $target_branch"
    return 0
}
```

### safe_merge
Performs a safe merge with backup.

```bash
safe_merge() {
    local source_branch="$1"
    local backup="${2:-true}"
    
    # Get current branch
    local current_branch=$(git branch --show-current)
    
    # Create backup if requested
    if [ "$backup" = "true" ]; then
        local backup_branch="${current_branch}-backup-$(date +%Y%m%d-%H%M%S)"
        echo "Creating backup branch: $backup_branch"
        create_branch "$backup_branch" "$current_branch" false
    fi
    
    # Perform merge
    if merge_branch "$source_branch"; then
        echo "Merge completed successfully"
        [ "$backup" = "true" ] && echo "Backup branch available: $backup_branch"
        return 0
    else
        echo "Merge failed"
        if [ "$backup" = "true" ]; then
            echo "You can restore from backup with:"
            echo "  git reset --hard $backup_branch"
        fi
        return 1
    fi
}
```

## Branch Management

### delete_branch
Deletes a branch with safety checks.

```bash
delete_branch() {
    local branch_name="$1"
    local force="${2:-false}"
    local delete_remote="${3:-false}"
    
    # Prevent deletion of current branch
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" = "$branch_name" ]; then
        handle_error "3003" "$branch_name" "Cannot delete current branch"
        return 1
    fi
    
    # Prevent deletion of main branches
    if is_protected_branch "$branch_name"; then
        handle_error "3003" "$branch_name" "Cannot delete protected branch"
        return 1
    fi
    
    # Check if branch exists
    if ! git show-ref --verify --quiet "refs/heads/$branch_name"; then
        handle_error "3003" "$branch_name" "Branch does not exist"
        return 1
    fi
    
    # Check if branch is merged (unless force)
    if [ "$force" != "true" ]; then
        local default_branch=$(get_default_branch)
        if ! git branch --merged "$default_branch" | grep -q "^[* ]*$branch_name$"; then
            echo "Warning: Branch '$branch_name' is not merged into $default_branch"
            echo "Use force=true to delete anyway"
            return 1
        fi
    fi
    
    # Delete local branch
    local delete_flag="-d"
    [ "$force" = "true" ] && delete_flag="-D"
    
    echo "Deleting local branch: $branch_name"
    if ! git branch "$delete_flag" "$branch_name" 2>&1; then
        handle_error "3003" "git branch delete" "$branch_name"
        return 1
    fi
    
    # Delete remote branch if requested
    if [ "$delete_remote" = "true" ]; then
        delete_remote_branch "$branch_name"
    fi
    
    echo "Branch deleted: $branch_name"
    return 0
}
```

### delete_remote_branch
Deletes a remote branch.

```bash
delete_remote_branch() {
    local branch_name="$1"
    local remote="${2:-origin}"
    
    # Check if remote branch exists
    if ! git show-ref --verify --quiet "refs/remotes/$remote/$branch_name"; then
        echo "Remote branch does not exist: $remote/$branch_name"
        return 0
    fi
    
    # Delete remote branch
    echo "Deleting remote branch: $remote/$branch_name"
    if ! git push "$remote" --delete "$branch_name" 2>&1; then
        handle_error "3005" "git push --delete" "$branch_name"
        return 1
    fi
    
    echo "Remote branch deleted: $remote/$branch_name"
    return 0
}
```

### list_branches
Lists branches with filtering options.

```bash
list_branches() {
    local filter="${1:-all}"  # all, local, remote, merged, unmerged
    local pattern="${2:-}"
    
    case "$filter" in
        "local")
            git branch | grep -E "$pattern"
            ;;
        "remote")
            git branch -r | grep -E "$pattern"
            ;;
        "merged")
            local default_branch=$(get_default_branch)
            git branch --merged "$default_branch" | grep -E "$pattern"
            ;;
        "unmerged")
            local default_branch=$(get_default_branch)
            git branch --no-merged "$default_branch" | grep -E "$pattern"
            ;;
        "all"|*)
            git branch -a | grep -E "$pattern"
            ;;
    esac
}
```

### cleanup_branches
Cleans up merged branches.

```bash
cleanup_branches() {
    local dry_run="${1:-true}"
    local protect_pattern="${2:-^(main|master|develop|release/)}"
    
    echo "Finding merged branches..."
    local default_branch=$(get_default_branch)
    
    # Get merged branches
    local branches=$(git branch --merged "$default_branch" | grep -v "^[* ]*$default_branch$" | grep -vE "$protect_pattern")
    
    if [ -z "$branches" ]; then
        echo "No branches to clean up"
        return 0
    fi
    
    echo "Branches to delete:"
    echo "$branches"
    
    if [ "$dry_run" = "true" ]; then
        echo ""
        echo "This is a dry run. To actually delete, run with dry_run=false"
        return 0
    fi
    
    # Confirm deletion
    echo ""
    read -p "Delete these branches? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled"
        return 0
    fi
    
    # Delete branches
    echo "$branches" | while read -r branch; do
        branch=$(echo "$branch" | xargs)  # Trim whitespace
        delete_branch "$branch" false false
    done
    
    echo "Cleanup completed"
}
```

## Helper Functions

### get_default_branch
Gets the default branch name.

```bash
get_default_branch() {
    # Try to get from remote
    local default_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
    
    if [ -z "$default_branch" ]; then
        # Fallback to common names
        if git show-ref --verify --quiet refs/heads/main; then
            default_branch="main"
        elif git show-ref --verify --quiet refs/heads/master; then
            default_branch="master"
        else
            # Get first branch
            default_branch=$(git branch | head -1 | sed 's/^[* ]*//')
        fi
    fi
    
    echo "$default_branch"
}
```

### is_protected_branch
Checks if a branch is protected.

```bash
is_protected_branch() {
    local branch_name="$1"
    local protected_branches=("main" "master" "develop" "production" "staging")
    
    for protected in "${protected_branches[@]}"; do
        if [ "$branch_name" = "$protected" ]; then
            return 0
        fi
    done
    
    # Check if it's a release branch
    if [[ "$branch_name" =~ ^release/ ]]; then
        return 0
    fi
    
    return 1
}
```

### get_branch_info
Gets detailed information about a branch.

```bash
get_branch_info() {
    local branch_name="$1"
    
    check_branch_exists "$branch_name" || return 1
    
    echo "Branch: $branch_name"
    
    # Get tracking info
    local upstream=$(git for-each-ref --format='%(upstream:short)' "refs/heads/$branch_name")
    [ -n "$upstream" ] && echo "Tracking: $upstream"
    
    # Get last commit
    echo "Last commit:"
    git log -1 --oneline "$branch_name"
    
    # Get ahead/behind info
    if [ -n "$upstream" ]; then
        local ahead=$(git rev-list --count "$upstream..$branch_name")
        local behind=$(git rev-list --count "$branch_name..$upstream")
        echo "Status: $ahead ahead, $behind behind $upstream"
    fi
    
    # Get merge status
    local default_branch=$(get_default_branch)
    if git branch --merged "$default_branch" | grep -q "^[* ]*$branch_name$"; then
        echo "Merged into $default_branch: Yes"
    else
        echo "Merged into $default_branch: No"
    fi
}
```

## Usage Examples

### Branch Creation
```bash
# Create feature branch
create_feature_branch "add-user-auth"

# Create release branch
create_release_branch "2.0.0"

# Create branch from specific commit
create_branch "hotfix/security-patch" "abc123" true
```

### Branch Operations
```bash
# Switch branches safely
switch_branch "develop"

# Checkout remote branch
checkout_remote_branch "feature/remote-feature"

# Merge with conflict handling
merge_branch "feature/new-feature" "develop"

# Safe merge with backup
safe_merge "feature/risky-change"
```

### Branch Management
```bash
# Delete merged branch
delete_branch "feature/completed-feature"

# Force delete with remote
delete_branch "feature/abandoned" true true

# Clean up old branches
cleanup_branches false "^(main|master|develop|release/|hotfix/)"

# Get branch information
get_branch_info "feature/current-work"
```

## Best Practices

1. **Use descriptive branch names**: Follow naming conventions
2. **Keep branches focused**: One feature/fix per branch
3. **Delete merged branches**: Keep repository clean
4. **Protect important branches**: Prevent accidental deletion
5. **Update before branching**: Always branch from latest code