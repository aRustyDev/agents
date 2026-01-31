---
module: CommitOperations
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - ../error-handling/base-error-handler.md
  - ../error-handling/git-errors.md
  - ../validation/input-validator.md
---

# Commit Operations

## Purpose
Provides standardized git commit operations with message formatting, staging control, and commit management.

## Overview
This module encapsulates commit-related operations with validation, conventional commit support, and proper error handling.

## Staging Operations

### stage_files
Stages files for commit with validation.

```bash
stage_files() {
    local -a files=("$@")
    
    if [ ${#files[@]} -eq 0 ]; then
        handle_error "1002" "files" "No files specified to stage"
        return 1
    fi
    
    # Validate each file exists
    local valid_files=()
    for file in "${files[@]}"; do
        if [ -e "$file" ]; then
            valid_files+=("$file")
        else
            echo "Warning: File not found: $file"
        fi
    done
    
    if [ ${#valid_files[@]} -eq 0 ]; then
        handle_error "2001" "files" "No valid files to stage"
        return 1
    fi
    
    # Stage files
    echo "Staging ${#valid_files[@]} file(s)..."
    if ! git add "${valid_files[@]}" 2>&1; then
        handle_error "3005" "git add" "${valid_files[*]}"
        return 1
    fi
    
    # Show staged files
    echo "Staged files:"
    git diff --name-only --cached
    
    return 0
}
```

### stage_interactive
Interactive staging with user prompts.

```bash
stage_interactive() {
    local pattern="${1:-}"
    
    # Get modified files
    local files
    if [ -n "$pattern" ]; then
        files=$(git ls-files -m | grep -E "$pattern")
    else
        files=$(git ls-files -m)
    fi
    
    if [ -z "$files" ]; then
        echo "No modified files to stage"
        return 0
    fi
    
    # Interactive selection
    echo "Modified files:"
    echo "$files" | nl -w2 -s') '
    echo ""
    echo "Enter file numbers to stage (space-separated), 'all', or 'none':"
    read -r selection
    
    case "$selection" in
        "all")
            git add -A
            echo "All files staged"
            ;;
        "none"|"")
            echo "No files staged"
            ;;
        *)
            # Process selected numbers
            local selected_files=()
            for num in $selection; do
                if [[ "$num" =~ ^[0-9]+$ ]]; then
                    local file=$(echo "$files" | sed -n "${num}p")
                    [ -n "$file" ] && selected_files+=("$file")
                fi
            done
            
            if [ ${#selected_files[@]} -gt 0 ]; then
                stage_files "${selected_files[@]}"
            else
                echo "No valid selections"
            fi
            ;;
    esac
}
```

### unstage_files
Unstages files from the index.

```bash
unstage_files() {
    local -a files=("$@")
    
    if [ ${#files[@]} -eq 0 ]; then
        # Unstage all
        echo "Unstaging all files..."
        git reset HEAD
    else
        # Unstage specific files
        echo "Unstaging ${#files[@]} file(s)..."
        git reset HEAD "${files[@]}"
    fi
    
    # Show remaining staged files
    local staged_count=$(git diff --name-only --cached | wc -l)
    if [ "$staged_count" -gt 0 ]; then
        echo "Still staged:"
        git diff --name-only --cached
    else
        echo "No files staged"
    fi
}
```

## Commit Creation

### create_commit
Creates a commit with message validation.

```bash
create_commit() {
    local message="$1"
    local description="${2:-}"
    local no_verify="${3:-false}"
    local amend="${4:-false}"
    
    # Check for staged changes
    if ! git diff --cached --quiet; then
        :  # Has staged changes
    elif [ "$amend" = "true" ]; then
        :  # Amending is ok without staged changes
    else
        handle_error "3002" "No staged changes" "Stage files before committing"
        return 1
    fi
    
    # Validate commit message
    if ! validate_commit_message "$message"; then
        return 1
    fi
    
    # Build commit command
    local commit_cmd="git commit"
    [ "$no_verify" = "true" ] && commit_cmd="$commit_cmd --no-verify"
    [ "$amend" = "true" ] && commit_cmd="$commit_cmd --amend"
    
    # Execute commit
    if [ -n "$description" ]; then
        # Multi-line commit
        echo "Creating commit..."
        if ! $commit_cmd -m "$message" -m "$description" 2>&1; then
            handle_error "3005" "git commit" "Failed to create commit"
            return 1
        fi
    else
        # Single line commit
        if ! $commit_cmd -m "$message" 2>&1; then
            handle_error "3005" "git commit" "Failed to create commit"
            return 1
        fi
    fi
    
    # Show commit info
    echo "Commit created:"
    git log --oneline -n 1
    
    return 0
}
```

### create_conventional_commit
Creates a conventional commit with type, scope, and description.

```bash
create_conventional_commit() {
    local type="$1"
    local scope="$2"
    local description="$3"
    local body="${4:-}"
    local breaking="${5:-false}"
    
    # Validate type
    local valid_types=("feat" "fix" "docs" "style" "refactor" "perf" "test" "build" "ci" "chore" "revert")
    validate_enum "type" "$type" "${valid_types[@]}" || return 1
    
    # Build commit message
    local message="$type"
    [ -n "$scope" ] && message="$message($scope)"
    message="$message: $description"
    
    # Add breaking change indicator
    [ "$breaking" = "true" ] && message="$message!"
    
    # Create commit
    create_commit "$message" "$body"
}
```

### commit_with_template
Creates a commit using a template.

```bash
commit_with_template() {
    local template_name="${1:-default}"
    local values_file="${2:-}"
    
    # Get template path
    local template_file="$HOME/.claude/templates/commit-$template_name.txt"
    if [ ! -f "$template_file" ]; then
        handle_error "2001" "$template_file" "Commit template not found"
        return 1
    fi
    
    # Create temp file for message
    local temp_msg=$(mktemp)
    cp "$template_file" "$temp_msg"
    
    # Replace variables if values provided
    if [ -n "$values_file" ] && [ -f "$values_file" ]; then
        source "$values_file"
        # Replace template variables
        for var in $(grep -oE '\{\{[A-Z_]+\}\}' "$temp_msg" | tr -d '{}' | sort -u); do
            local value="${!var:-}"
            sed -i "s/{{$var}}/$value/g" "$temp_msg"
        done
    fi
    
    # Open editor for user to complete
    ${EDITOR:-vi} "$temp_msg"
    
    # Check if user saved changes
    if [ ! -s "$temp_msg" ]; then
        echo "Commit cancelled"
        rm -f "$temp_msg"
        return 1
    fi
    
    # Create commit with the message
    git commit -F "$temp_msg"
    local result=$?
    
    rm -f "$temp_msg"
    return $result
}
```

## Commit Management

### amend_commit
Amends the last commit.

```bash
amend_commit() {
    local new_message="${1:-}"
    local add_files="${2:-false}"
    
    # Check if there's a commit to amend
    if ! git rev-parse HEAD >/dev/null 2>&1; then
        handle_error "3005" "No commits" "Cannot amend without commits"
        return 1
    fi
    
    # Add files if requested
    if [ "$add_files" = "true" ]; then
        echo "Adding modified files to amendment..."
        git add -u
    fi
    
    # Amend commit
    if [ -n "$new_message" ]; then
        echo "Amending commit with new message..."
        create_commit "$new_message" "" false true
    else
        echo "Amending commit (edit message in editor)..."
        git commit --amend
    fi
}
```

### revert_commit
Reverts a commit safely.

```bash
revert_commit() {
    local commit_ref="${1:-HEAD}"
    local no_commit="${2:-false}"
    
    # Validate commit exists
    if ! git rev-parse "$commit_ref" >/dev/null 2>&1; then
        handle_error "3005" "Invalid commit reference" "$commit_ref"
        return 1
    fi
    
    # Get commit info
    local commit_hash=$(git rev-parse "$commit_ref")
    local commit_msg=$(git log -1 --pretty=%s "$commit_hash")
    
    echo "Reverting commit: $commit_hash"
    echo "Original message: $commit_msg"
    
    # Build revert command
    local revert_cmd="git revert"
    [ "$no_commit" = "true" ] && revert_cmd="$revert_cmd --no-commit"
    revert_cmd="$revert_cmd $commit_hash"
    
    # Execute revert
    if ! $revert_cmd 2>&1; then
        handle_error "3005" "git revert" "Failed to revert commit"
        return 1
    fi
    
    if [ "$no_commit" = "true" ]; then
        echo "Changes staged for revert. Commit when ready."
    else
        echo "Revert commit created"
        git log --oneline -n 1
    fi
}
```

### squash_commits
Squashes multiple commits into one.

```bash
squash_commits() {
    local num_commits="$1"
    local new_message="${2:-}"
    
    # Validate number
    validate_type "num_commits" "$num_commits" "integer" || return 1
    
    if [ "$num_commits" -lt 2 ]; then
        handle_error "1004" "num_commits" "Must squash at least 2 commits"
        return 1
    fi
    
    # Check if we have enough commits
    local total_commits=$(git rev-list --count HEAD)
    if [ "$num_commits" -gt "$total_commits" ]; then
        handle_error "1004" "num_commits" "Only $total_commits commits available"
        return 1
    fi
    
    # Start interactive rebase
    echo "Squashing last $num_commits commits..."
    
    if [ -n "$new_message" ]; then
        # Non-interactive squash
        git reset --soft HEAD~$num_commits
        create_commit "$new_message"
    else
        # Interactive rebase
        GIT_SEQUENCE_EDITOR="sed -i '2,${s/^pick/squash/}'" git rebase -i HEAD~$num_commits
    fi
}
```

### fixup_commit
Creates a fixup commit for a previous commit.

```bash
fixup_commit() {
    local target_commit="$1"
    local auto_squash="${2:-true}"
    
    # Find target commit
    local commit_hash
    if [[ "$target_commit" =~ ^[0-9a-f]{7,40}$ ]]; then
        # Already a hash
        commit_hash="$target_commit"
    else
        # Search by message
        commit_hash=$(git log --grep="$target_commit" --pretty=format:"%h" -n 1)
        if [ -z "$commit_hash" ]; then
            handle_error "3005" "Commit not found" "$target_commit"
            return 1
        fi
    fi
    
    # Validate commit exists
    if ! git rev-parse "$commit_hash" >/dev/null 2>&1; then
        handle_error "3005" "Invalid commit" "$commit_hash"
        return 1
    fi
    
    # Create fixup commit
    echo "Creating fixup for: $(git log -1 --oneline $commit_hash)"
    git commit --fixup="$commit_hash"
    
    # Auto-squash if requested
    if [ "$auto_squash" = "true" ]; then
        echo "Auto-squashing fixup commits..."
        git rebase -i --autosquash "$commit_hash^"
    fi
}
```

## Commit History

### show_commit_log
Shows formatted commit log.

```bash
show_commit_log() {
    local num_commits="${1:-10}"
    local format="${2:-oneline}"
    local filter="${3:-}"
    
    local log_cmd="git log"
    
    # Add format
    case "$format" in
        "oneline")
            log_cmd="$log_cmd --oneline"
            ;;
        "short")
            log_cmd="$log_cmd --pretty=format:'%h %s (%an, %ar)'"
            ;;
        "full")
            log_cmd="$log_cmd --pretty=full"
            ;;
        "custom")
            log_cmd="$log_cmd --pretty=format:'%C(yellow)%h%Creset %C(blue)%an%Creset %C(green)%ar%Creset%n  %s%n'"
            ;;
    esac
    
    # Add filter
    [ -n "$filter" ] && log_cmd="$log_cmd --grep='$filter'"
    
    # Add count
    log_cmd="$log_cmd -n $num_commits"
    
    # Execute
    eval "$log_cmd"
}
```

### find_commits
Searches for commits by various criteria.

```bash
find_commits() {
    local search_type="$1"
    local search_value="$2"
    local max_results="${3:-20}"
    
    local log_cmd="git log --oneline -n $max_results"
    
    case "$search_type" in
        "author")
            log_cmd="$log_cmd --author='$search_value'"
            ;;
        "message")
            log_cmd="$log_cmd --grep='$search_value'"
            ;;
        "file")
            log_cmd="$log_cmd -- '$search_value'"
            ;;
        "date")
            log_cmd="$log_cmd --since='$search_value'"
            ;;
        *)
            handle_error "1003" "search_type" "Unknown search type: $search_type"
            return 1
            ;;
    esac
    
    echo "Searching commits..."
    eval "$log_cmd"
}
```

## Helper Functions

### validate_commit_message
Validates commit message format.

```bash
validate_commit_message() {
    local message="$1"
    
    # Check length
    local first_line=$(echo "$message" | head -1)
    if [ ${#first_line} -gt 72 ]; then
        echo "Warning: First line exceeds 72 characters"
    fi
    
    # Check format (optional conventional commit check)
    if [ "${ENFORCE_CONVENTIONAL_COMMITS:-false}" = "true" ]; then
        if ! [[ "$first_line" =~ ^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?!?:\ .+ ]]; then
            handle_error "1003" "commit message" "Must follow conventional commit format"
            return 1
        fi
    fi
    
    # Check for empty message
    if [ -z "$(echo "$message" | tr -d '[:space:]')" ]; then
        handle_error "1002" "commit message" "Message cannot be empty"
        return 1
    fi
    
    return 0
}
```

### get_commit_info
Gets detailed information about a commit.

```bash
get_commit_info() {
    local commit_ref="${1:-HEAD}"
    
    if ! git rev-parse "$commit_ref" >/dev/null 2>&1; then
        handle_error "3005" "Invalid commit reference" "$commit_ref"
        return 1
    fi
    
    local commit_hash=$(git rev-parse "$commit_ref")
    
    echo "Commit: $commit_hash"
    echo "Author: $(git log -1 --pretty=%an $commit_hash) <$(git log -1 --pretty=%ae $commit_hash)>"
    echo "Date: $(git log -1 --pretty=%ad $commit_hash)"
    echo "Message:"
    git log -1 --pretty=%B $commit_hash | sed 's/^/  /'
    echo ""
    echo "Files changed:"
    git diff-tree --no-commit-id --name-status -r $commit_hash
}
```

### generate_changelog
Generates a changelog from commit history.

```bash
generate_changelog() {
    local since_tag="${1:-}"
    local output_file="${2:-CHANGELOG.md}"
    local include_types="${3:-feat,fix,perf}"
    
    # Determine range
    local range=""
    if [ -n "$since_tag" ]; then
        range="$since_tag..HEAD"
    else
        # Get last tag
        local last_tag=$(git describe --tags --abbrev=0 2>/dev/null)
        [ -n "$last_tag" ] && range="$last_tag..HEAD"
    fi
    
    # Generate changelog
    {
        echo "# Changelog"
        echo ""
        echo "## [Unreleased]"
        echo ""
        
        # Parse commits by type
        IFS=',' read -ra types <<< "$include_types"
        for type in "${types[@]}"; do
            local commits=$(git log $range --pretty=format:"%s" | grep "^$type" || true)
            if [ -n "$commits" ]; then
                case "$type" in
                    "feat") echo "### Features" ;;
                    "fix") echo "### Bug Fixes" ;;
                    "perf") echo "### Performance Improvements" ;;
                    *) echo "### $type" ;;
                esac
                echo ""
                echo "$commits" | while read -r commit; do
                    echo "- $commit"
                done
                echo ""
            fi
        done
    } > "$output_file"
    
    echo "Changelog generated: $output_file"
}
```

## Usage Examples

### Staging and Committing
```bash
# Stage specific files
stage_files "src/main.js" "src/utils.js"

# Interactive staging
stage_interactive "*.js"

# Create conventional commit
create_conventional_commit "feat" "auth" "add user login functionality"

# Commit with template
commit_with_template "feature" "./commit-values.sh"
```

### Commit Management
```bash
# Amend last commit
amend_commit "fix: correct typo in function name" true

# Revert a commit
revert_commit "abc123"

# Squash last 3 commits
squash_commits 3 "feat: complete authentication system"

# Create fixup commit
fixup_commit "fix: resolve login bug"
```

### History and Search
```bash
# Show custom format log
show_commit_log 20 "custom"

# Find commits by author
find_commits "author" "john@example.com"

# Generate changelog
generate_changelog "v1.0.0" "CHANGELOG.md" "feat,fix,breaking"
```

## Best Practices

1. **Write clear commit messages**: Be descriptive and concise
2. **Use conventional commits**: Follow a consistent format
3. **Commit logical units**: One change per commit
4. **Review before committing**: Check staged changes
5. **Keep history clean**: Use squash and fixup appropriately