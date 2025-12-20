---
module: StatusOperations
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - ../error-handling/base-error-handler.md
  - ../error-handling/git-errors.md
---

# Status Operations

## Purpose
Provides comprehensive git status operations including repository state checks, diff generation, and change detection.

## Overview
This module encapsulates status-related git operations for understanding repository state, tracking changes, and identifying conflicts.

## Status Checks

### get_repository_status
Gets comprehensive repository status information.

```bash
get_repository_status() {
    local format="${1:-text}"
    local verbose="${2:-false}"
    
    # Check if in git repo
    check_git_repo || return 1
    
    # Gather status information
    local branch=$(git branch --show-current)
    local upstream=$(git for-each-ref --format='%(upstream:short)' "refs/heads/$branch")
    local staged=$(git diff --cached --numstat | wc -l)
    local modified=$(git ls-files -m | wc -l)
    local untracked=$(git ls-files -o --exclude-standard | wc -l)
    local stashes=$(git stash list | wc -l)
    
    # Get ahead/behind info
    local ahead=0
    local behind=0
    if [ -n "$upstream" ]; then
        ahead=$(git rev-list --count "$upstream..$branch" 2>/dev/null || echo 0)
        behind=$(git rev-list --count "$branch..$upstream" 2>/dev/null || echo 0)
    fi
    
    case "$format" in
        "text")
            echo "Repository Status:"
            echo "  Branch: ${branch:-'(detached HEAD)'}"
            [ -n "$upstream" ] && echo "  Tracking: $upstream"
            [ $ahead -gt 0 -o $behind -gt 0 ] && echo "  Position: $ahead ahead, $behind behind"
            echo "  Changes:"
            echo "    Staged: $staged"
            echo "    Modified: $modified"
            echo "    Untracked: $untracked"
            [ $stashes -gt 0 ] && echo "  Stashes: $stashes"
            
            if [ "$verbose" = "true" ]; then
                echo ""
                show_detailed_status
            fi
            ;;
        "json")
            cat <<EOF
{
  "branch": "${branch:-null}",
  "upstream": "${upstream:-null}",
  "ahead": $ahead,
  "behind": $behind,
  "changes": {
    "staged": $staged,
    "modified": $modified,
    "untracked": $untracked
  },
  "stashes": $stashes
}
EOF
            ;;
        "short")
            local status_line=""
            [ $staged -gt 0 ] && status_line="${status_line}+$staged "
            [ $modified -gt 0 ] && status_line="${status_line}~$modified "
            [ $untracked -gt 0 ] && status_line="${status_line}?$untracked "
            [ $ahead -gt 0 ] && status_line="${status_line}↑$ahead "
            [ $behind -gt 0 ] && status_line="${status_line}↓$behind "
            
            echo "${branch:-HEAD}: ${status_line:-'clean'}"
            ;;
    esac
}
```

### show_detailed_status
Shows detailed status with file listings.

```bash
show_detailed_status() {
    # Staged files
    local staged_files=$(git diff --cached --name-only)
    if [ -n "$staged_files" ]; then
        echo "Staged files:"
        echo "$staged_files" | sed 's/^/  ✓ /'
        echo ""
    fi
    
    # Modified files
    local modified_files=$(git ls-files -m)
    if [ -n "$modified_files" ]; then
        echo "Modified files:"
        echo "$modified_files" | sed 's/^/  ≈ /'
        echo ""
    fi
    
    # Untracked files
    local untracked_files=$(git ls-files -o --exclude-standard)
    if [ -n "$untracked_files" ]; then
        echo "Untracked files:"
        echo "$untracked_files" | sed 's/^/  ? /'
        echo ""
    fi
    
    # Conflicts
    local conflicted_files=$(git diff --name-only --diff-filter=U)
    if [ -n "$conflicted_files" ]; then
        echo "Conflicted files:"
        echo "$conflicted_files" | sed 's/^/  ⚠ /'
        echo ""
    fi
}
```

### check_working_tree_clean
Checks if working tree is clean.

```bash
check_working_tree_clean() {
    local ignore_untracked="${1:-false}"
    
    # Check for staged changes
    if ! git diff --cached --quiet; then
        return 1  # Has staged changes
    fi
    
    # Check for unstaged changes
    if ! git diff --quiet; then
        return 1  # Has unstaged changes
    fi
    
    # Check for untracked files
    if [ "$ignore_untracked" != "true" ]; then
        if [ -n "$(git ls-files -o --exclude-standard)" ]; then
            return 1  # Has untracked files
        fi
    fi
    
    return 0  # Working tree is clean
}
```

## Diff Operations

### show_diff
Shows differences with various options.

```bash
show_diff() {
    local target="${1:-}"
    local options="${2:-}"
    local filter="${3:-}"
    
    local diff_cmd="git diff"
    
    # Add options
    case "$options" in
        "staged"|"cached")
            diff_cmd="$diff_cmd --cached"
            ;;
        "words")
            diff_cmd="$diff_cmd --word-diff"
            ;;
        "stats")
            diff_cmd="$diff_cmd --stat"
            ;;
        "name-only")
            diff_cmd="$diff_cmd --name-only"
            ;;
        "summary")
            diff_cmd="$diff_cmd --summary"
            ;;
    esac
    
    # Add target
    [ -n "$target" ] && diff_cmd="$diff_cmd $target"
    
    # Add path filter
    [ -n "$filter" ] && diff_cmd="$diff_cmd -- $filter"
    
    # Execute diff
    eval "$diff_cmd"
}
```

### compare_branches
Compares two branches.

```bash
compare_branches() {
    local branch1="$1"
    local branch2="$2"
    local show_commits="${3:-true}"
    local show_files="${4:-true}"
    
    # Validate branches exist
    check_branch_exists "$branch1" || return 1
    check_branch_exists "$branch2" || return 1
    
    echo "Comparing $branch1...$branch2"
    echo "===================="
    
    # Show commit differences
    if [ "$show_commits" = "true" ]; then
        echo ""
        echo "Commits in $branch1 but not in $branch2:"
        git log --oneline "$branch2..$branch1"
        
        echo ""
        echo "Commits in $branch2 but not in $branch1:"
        git log --oneline "$branch1..$branch2"
    fi
    
    # Show file differences
    if [ "$show_files" = "true" ]; then
        echo ""
        echo "File differences:"
        git diff --stat "$branch1...$branch2"
    fi
    
    # Summary
    local ahead=$(git rev-list --count "$branch2..$branch1")
    local behind=$(git rev-list --count "$branch1..$branch2")
    echo ""
    echo "Summary: $branch1 is $ahead commits ahead and $behind commits behind $branch2"
}
```

### show_file_history
Shows history of changes for a specific file.

```bash
show_file_history() {
    local file_path="$1"
    local num_commits="${2:-10}"
    local follow_renames="${3:-true}"
    
    # Validate file
    if [ ! -e "$file_path" ] && ! git ls-files --error-unmatch "$file_path" >/dev/null 2>&1; then
        handle_error "2001" "$file_path" "File not found in repository"
        return 1
    fi
    
    echo "History for: $file_path"
    echo "=================="
    
    # Build log command
    local log_cmd="git log --oneline -n $num_commits"
    [ "$follow_renames" = "true" ] && log_cmd="$log_cmd --follow"
    log_cmd="$log_cmd -- $file_path"
    
    # Show commits
    eval "$log_cmd"
    
    # Show current status
    echo ""
    echo "Current status:"
    if [ -e "$file_path" ]; then
        local size=$(du -h "$file_path" | cut -f1)
        local lines=$(wc -l < "$file_path")
        echo "  Size: $size"
        echo "  Lines: $lines"
    else
        echo "  File deleted"
    fi
}
```

## Change Detection

### detect_changes
Detects various types of changes in the repository.

```bash
detect_changes() {
    local change_type="${1:-all}"
    
    case "$change_type" in
        "staged")
            git diff --cached --name-status
            ;;
        "unstaged")
            git diff --name-status
            ;;
        "untracked")
            git ls-files -o --exclude-standard
            ;;
        "deleted")
            git ls-files -d
            ;;
        "modified")
            git ls-files -m
            ;;
        "conflicts")
            git diff --name-only --diff-filter=U
            ;;
        "all")
            echo "=== Staged Changes ==="
            git diff --cached --name-status
            echo ""
            echo "=== Unstaged Changes ==="
            git diff --name-status
            echo ""
            echo "=== Untracked Files ==="
            git ls-files -o --exclude-standard
            ;;
        *)
            handle_error "1003" "change_type" "Unknown change type: $change_type"
            return 1
            ;;
    esac
}
```

### find_large_files
Finds large files in the repository.

```bash
find_large_files() {
    local size_limit="${1:-1M}"
    local show_history="${2:-false}"
    
    echo "Finding files larger than $size_limit..."
    
    if [ "$show_history" = "true" ]; then
        # Search entire history
        git rev-list --all | while read commit; do
            git ls-tree -r -l $commit | while read mode type hash size path; do
                if [ "$type" = "blob" ]; then
                    # Convert size limit to bytes
                    local limit_bytes=$(numfmt --from=iec $size_limit 2>/dev/null || echo 1048576)
                    if [ "$size" -gt "$limit_bytes" ]; then
                        echo "$commit: $path ($size bytes)"
                    fi
                fi
            done
        done | sort -u
    else
        # Search current tree only
        find . -type f -size +$size_limit | grep -v "^./.git/" | while read file; do
            local size=$(du -h "$file" | cut -f1)
            echo "$size $file"
        done | sort -hr
    fi
}
```

### detect_merge_conflicts
Detects and analyzes merge conflicts.

```bash
detect_merge_conflicts() {
    local show_markers="${1:-true}"
    
    # Get conflicted files
    local conflicts=$(git diff --name-only --diff-filter=U)
    
    if [ -z "$conflicts" ]; then
        echo "No merge conflicts detected"
        return 0
    fi
    
    echo "Merge conflicts found in:"
    echo "$conflicts" | nl -w2 -s') '
    
    if [ "$show_markers" = "true" ]; then
        echo ""
        echo "Conflict details:"
        echo "$conflicts" | while read file; do
            echo ""
            echo "File: $file"
            echo "Conflict markers:"
            grep -n "^<<<<<<< \|^=======$\|^>>>>>>> " "$file" || echo "  No standard markers found"
        done
    fi
    
    # Show resolution hints
    echo ""
    echo "To resolve conflicts:"
    echo "  1. Edit the conflicted files"
    echo "  2. Remove conflict markers"
    echo "  3. Stage resolved files: git add <file>"
    echo "  4. Complete merge: git commit"
    
    return 1
}
```

## Stash Operations

### show_stash_info
Shows information about stashes.

```bash
show_stash_info() {
    local stash_ref="${1:-}"
    local verbose="${2:-false}"
    
    if [ -z "$stash_ref" ]; then
        # Show all stashes
        local stash_count=$(git stash list | wc -l)
        
        if [ $stash_count -eq 0 ]; then
            echo "No stashes found"
            return 0
        fi
        
        echo "Stashes ($stash_count total):"
        git stash list | while IFS=: read stash_id message; do
            echo "  $stash_id: $message"
            if [ "$verbose" = "true" ]; then
                echo "    Files:"
                git stash show --name-only "$stash_id" | sed 's/^/      /'
                echo ""
            fi
        done
    else
        # Show specific stash
        if ! git stash show "$stash_ref" >/dev/null 2>&1; then
            handle_error "3005" "Invalid stash reference" "$stash_ref"
            return 1
        fi
        
        echo "Stash: $stash_ref"
        git stash show --stat "$stash_ref"
        
        if [ "$verbose" = "true" ]; then
            echo ""
            echo "Full diff:"
            git stash show -p "$stash_ref"
        fi
    fi
}
```

### create_work_snapshot
Creates a snapshot of current work state.

```bash
create_work_snapshot() {
    local description="${1:-Work in progress}"
    local include_untracked="${2:-true}"
    
    # Check if there are changes to stash
    if check_working_tree_clean; then
        echo "No changes to snapshot"
        return 0
    fi
    
    # Build stash command
    local stash_cmd="git stash push"
    [ "$include_untracked" = "true" ] && stash_cmd="$stash_cmd -u"
    stash_cmd="$stash_cmd -m '$description'"
    
    # Create stash
    echo "Creating work snapshot..."
    if eval "$stash_cmd"; then
        echo "Snapshot created: $description"
        
        # Show stash reference
        local latest_stash=$(git stash list -n 1 | cut -d: -f1)
        echo "Reference: $latest_stash"
        
        # Option to restore immediately
        echo ""
        echo "To restore this snapshot later:"
        echo "  git stash apply $latest_stash"
    else
        handle_error "3005" "git stash" "Failed to create snapshot"
        return 1
    fi
}
```

## Summary Reports

### generate_status_report
Generates a comprehensive status report.

```bash
generate_status_report() {
    local output_file="${1:-}"
    local include_diffs="${2:-false}"
    
    # Function to output or append
    output() {
        if [ -n "$output_file" ]; then
            echo "$@" >> "$output_file"
        else
            echo "$@"
        fi
    }
    
    # Clear output file if specified
    [ -n "$output_file" ] && : > "$output_file"
    
    output "Git Repository Status Report"
    output "Generated: $(date)"
    output "========================================"
    output ""
    
    # Repository info
    output "## Repository Information"
    get_repository_info | while read line; do
        output "$line"
    done
    output ""
    
    # Current status
    output "## Current Status"
    get_repository_status "text" | while read line; do
        output "$line"
    done
    output ""
    
    # Recent activity
    output "## Recent Activity"
    output "Last 5 commits:"
    git log --oneline -n 5 | while read line; do
        output "  $line"
    done
    output ""
    
    # Branch information
    output "## Branches"
    output "Local branches:"
    git branch | while read line; do
        output "  $line"
    done
    output ""
    
    # File statistics
    output "## File Statistics"
    output "Total files: $(git ls-files | wc -l)"
    output "Total size: $(git ls-files | xargs du -ch | tail -1 | cut -f1)"
    output ""
    
    # Include diffs if requested
    if [ "$include_diffs" = "true" ]; then
        output "## Current Changes"
        output "### Staged Changes"
        git diff --cached | while read line; do
            output "$line"
        done
        output ""
        output "### Unstaged Changes"
        git diff | while read line; do
            output "$line"
        done
    fi
    
    [ -n "$output_file" ] && echo "Report saved to: $output_file"
}
```

## Usage Examples

### Status Checks
```bash
# Get repository status
get_repository_status "json" > status.json

# Check if working tree is clean
if check_working_tree_clean; then
    echo "Ready to switch branches"
fi

# Show detailed status
show_detailed_status
```

### Diff Operations
```bash
# Show staged changes
show_diff "" "staged"

# Compare branches
compare_branches "feature/new" "develop"

# Show file history
show_file_history "src/main.js" 20
```

### Change Detection
```bash
# Detect all changes
detect_changes "all"

# Find large files
find_large_files "10M" true

# Check for conflicts
detect_merge_conflicts
```

### Reports and Snapshots
```bash
# Create work snapshot
create_work_snapshot "WIP: implementing auth"

# Generate status report
generate_status_report "status-report.txt" true

# Show stash information
show_stash_info "" true
```

## Best Practices

1. **Check status before operations**: Always know repository state
2. **Use appropriate diff options**: Choose the right view for your needs
3. **Monitor file sizes**: Prevent large files from entering history
4. **Resolve conflicts promptly**: Don't let conflicts linger
5. **Create snapshots regularly**: Save work in progress safely