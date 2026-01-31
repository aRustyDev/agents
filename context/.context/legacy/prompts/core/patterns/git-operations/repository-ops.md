---
module: RepositoryOperations
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - ../error-handling/base-error-handler.md
  - ../error-handling/git-errors.md
  - ../validation/input-validator.md
---

# Repository Operations

## Purpose
Provides standardized git repository operations including initialization, cloning, remote management, and configuration.

## Overview
This module encapsulates common repository-level git operations with proper error handling, validation, and safety checks.

## Repository Initialization

### init_repository
Initializes a new git repository with standard configuration.

```bash
init_repository() {
    local repo_path="${1:-.}"
    local branch_name="${2:-main}"
    local initial_commit="${3:-true}"
    
    # Validate path
    validate_directory_path "repo_path" "$repo_path" false true || return 1
    
    # Check if already a git repo
    if [ -d "$repo_path/.git" ]; then
        handle_error "3001" "$repo_path" "Already a git repository"
        return 1
    fi
    
    # Initialize repository
    (
        cd "$repo_path" || exit 1
        
        # Initialize
        if ! git init --initial-branch="$branch_name" 2>&1; then
            # Fallback for older git versions
            git init || handle_error "3001" "git init"
            git checkout -b "$branch_name" || handle_error "3003" "$branch_name"
        fi
        
        # Set up standard configuration
        setup_repository_config
        
        # Create initial commit if requested
        if [ "$initial_commit" = "true" ]; then
            create_initial_commit
        fi
    ) || return 1
    
    echo "Repository initialized at: $repo_path"
    return 0
}
```

### clone_repository
Clones a repository with validation and configuration.

```bash
clone_repository() {
    local repo_url="$1"
    local target_dir="${2:-}"
    local branch="${3:-}"
    local depth="${4:-}"
    
    # Validate URL
    validate_git_url "$repo_url" || return 1
    
    # Determine target directory
    if [ -z "$target_dir" ]; then
        target_dir=$(basename "$repo_url" .git)
    fi
    
    # Check if target exists
    if [ -e "$target_dir" ]; then
        handle_error "2003" "$target_dir" "Target directory already exists"
        return 1
    fi
    
    # Build clone command
    local clone_cmd="git clone"
    [ -n "$branch" ] && clone_cmd="$clone_cmd --branch $branch"
    [ -n "$depth" ] && clone_cmd="$clone_cmd --depth $depth"
    clone_cmd="$clone_cmd $repo_url $target_dir"
    
    # Execute clone
    echo "Cloning repository: $repo_url"
    if ! $clone_cmd 2>&1; then
        handle_error "3005" "git clone" "$repo_url"
        return 1
    fi
    
    # Set up repository configuration
    (
        cd "$target_dir" || exit 1
        setup_repository_config
    )
    
    echo "Repository cloned to: $target_dir"
    return 0
}
```

### setup_repository_config
Sets up standard repository configuration.

```bash
setup_repository_config() {
    # Core settings
    git config core.autocrlf input
    git config core.whitespace trailing-space,space-before-tab
    
    # Branch settings
    git config branch.autosetupmerge always
    git config branch.autosetuprebase always
    
    # Pull settings
    git config pull.rebase true
    
    # Push settings
    git config push.default current
    
    # Diff settings
    git config diff.algorithm histogram
    git config diff.colorMoved zebra
    
    # Merge settings
    git config merge.conflictstyle diff3
    
    echo "Repository configuration applied"
}
```

## Remote Management

### add_remote
Adds a remote with validation.

```bash
add_remote() {
    local remote_name="$1"
    local remote_url="$2"
    local set_upstream="${3:-false}"
    
    # Validate inputs
    validate_required "remote_name" "$remote_name" || return 1
    validate_git_url "$remote_url" || return 1
    
    # Check if remote exists
    if git remote get-url "$remote_name" >/dev/null 2>&1; then
        handle_error "3005" "Remote already exists" "$remote_name"
        return 1
    fi
    
    # Add remote
    if ! git remote add "$remote_name" "$remote_url" 2>&1; then
        handle_error "3005" "git remote add" "$remote_name"
        return 1
    fi
    
    # Fetch remote
    echo "Fetching from remote: $remote_name"
    if ! git fetch "$remote_name" 2>&1; then
        echo "Warning: Failed to fetch from remote"
    fi
    
    # Set as upstream if requested
    if [ "$set_upstream" = "true" ]; then
        local current_branch=$(git branch --show-current)
        if [ -n "$current_branch" ]; then
            git branch --set-upstream-to="$remote_name/$current_branch" "$current_branch"
        fi
    fi
    
    echo "Remote added: $remote_name -> $remote_url"
    return 0
}
```

### update_remote
Updates a remote URL.

```bash
update_remote() {
    local remote_name="$1"
    local new_url="$2"
    
    # Validate inputs
    validate_required "remote_name" "$remote_name" || return 1
    validate_git_url "$new_url" || return 1
    
    # Check if remote exists
    if ! git remote get-url "$remote_name" >/dev/null 2>&1; then
        handle_error "3005" "Remote not found" "$remote_name"
        return 1
    fi
    
    # Get old URL for confirmation
    local old_url=$(git remote get-url "$remote_name")
    
    # Update remote
    if ! git remote set-url "$remote_name" "$new_url" 2>&1; then
        handle_error "3005" "git remote set-url" "$remote_name"
        return 1
    fi
    
    echo "Remote updated: $remote_name"
    echo "  Old URL: $old_url"
    echo "  New URL: $new_url"
    
    # Test connection
    echo "Testing connection..."
    if git ls-remote "$remote_name" >/dev/null 2>&1; then
        echo "Connection successful"
    else
        echo "Warning: Failed to connect to remote"
    fi
    
    return 0
}
```

### list_remotes
Lists all configured remotes with details.

```bash
list_remotes() {
    local verbose="${1:-false}"
    
    if [ "$verbose" = "true" ]; then
        # Detailed listing
        git remote -v | while read -r remote url type; do
            echo "$remote:"
            echo "  URL: $url ($type)"
            
            # Get HEAD branch
            local head_branch=$(git ls-remote --symref "$remote" HEAD 2>/dev/null | grep "^ref:" | cut -f2 | cut -d'/' -f3)
            [ -n "$head_branch" ] && echo "  HEAD: $head_branch"
            
            # List branches
            echo "  Branches:"
            git ls-remote --heads "$remote" 2>/dev/null | while read -r sha ref; do
                echo "    - ${ref#refs/heads/}"
            done
            echo
        done
    else
        # Simple listing
        git remote -v
    fi
}
```

## Repository Information

### get_repository_info
Gets comprehensive repository information.

```bash
get_repository_info() {
    local format="${1:-text}"
    
    # Check if in git repo
    check_git_repo || return 1
    
    # Gather information
    local repo_root=$(git rev-parse --show-toplevel)
    local current_branch=$(git branch --show-current)
    local head_commit=$(git rev-parse HEAD)
    local head_commit_short=$(git rev-parse --short HEAD)
    local remote_count=$(git remote | wc -l)
    local branch_count=$(git branch -a | wc -l)
    local tag_count=$(git tag | wc -l)
    local stash_count=$(git stash list | wc -l)
    
    case "$format" in
        "text")
            echo "Repository Information:"
            echo "  Path: $repo_root"
            echo "  Current branch: ${current_branch:-'(detached HEAD)'}"
            echo "  HEAD commit: $head_commit_short"
            echo "  Remotes: $remote_count"
            echo "  Branches: $branch_count"
            echo "  Tags: $tag_count"
            echo "  Stashes: $stash_count"
            ;;
        "json")
            cat <<EOF
{
  "path": "$repo_root",
  "current_branch": "${current_branch:-null}",
  "head_commit": "$head_commit",
  "head_commit_short": "$head_commit_short",
  "remotes": $remote_count,
  "branches": $branch_count,
  "tags": $tag_count,
  "stashes": $stash_count
}
EOF
            ;;
    esac
}
```

### check_repository_health
Performs health checks on the repository.

```bash
check_repository_health() {
    local fix_issues="${1:-false}"
    local issues_found=0
    
    echo "Performing repository health check..."
    
    # Check if in git repo
    if ! check_git_repo 2>/dev/null; then
        echo "✗ Not a git repository"
        return 1
    fi
    
    # Check for corrupted objects
    echo -n "Checking object integrity... "
    if git fsck --no-dangling >/dev/null 2>&1; then
        echo "✓"
    else
        echo "✗ Corrupted objects found"
        ((issues_found++))
        if [ "$fix_issues" = "true" ]; then
            echo "  Attempting to fix..."
            git fsck --full
        fi
    fi
    
    # Check index
    echo -n "Checking index... "
    if git status >/dev/null 2>&1; then
        echo "✓"
    else
        echo "✗ Index corrupted"
        ((issues_found++))
        if [ "$fix_issues" = "true" ]; then
            echo "  Attempting to fix..."
            rm -f .git/index
            git reset
        fi
    fi
    
    # Check for large files
    echo -n "Checking for large files... "
    local large_files=$(git ls-files | xargs -I {} du -s {} 2>/dev/null | awk '$1 > 50000' | wc -l)
    if [ "$large_files" -eq 0 ]; then
        echo "✓"
    else
        echo "✗ Found $large_files large files (>50MB)"
        ((issues_found++))
    fi
    
    # Check remote connectivity
    echo -n "Checking remote connectivity... "
    local remotes_ok=true
    for remote in $(git remote); do
        if ! git ls-remote "$remote" >/dev/null 2>&1; then
            remotes_ok=false
            break
        fi
    done
    
    if [ "$remotes_ok" = "true" ]; then
        echo "✓"
    else
        echo "✗ Some remotes unreachable"
        ((issues_found++))
    fi
    
    # Summary
    echo
    if [ $issues_found -eq 0 ]; then
        echo "Repository health check passed ✓"
        return 0
    else
        echo "Repository health check found $issues_found issue(s)"
        return 1
    fi
}
```

## Submodule Management

### add_submodule
Adds a submodule to the repository.

```bash
add_submodule() {
    local submodule_url="$1"
    local submodule_path="$2"
    local branch="${3:-}"
    
    # Validate inputs
    validate_git_url "$submodule_url" || return 1
    validate_required "submodule_path" "$submodule_path" || return 1
    
    # Check if path exists
    if [ -e "$submodule_path" ]; then
        handle_error "2003" "$submodule_path" "Path already exists"
        return 1
    fi
    
    # Build command
    local cmd="git submodule add"
    [ -n "$branch" ] && cmd="$cmd -b $branch"
    cmd="$cmd $submodule_url $submodule_path"
    
    # Add submodule
    echo "Adding submodule: $submodule_path"
    if ! $cmd 2>&1; then
        handle_error "3005" "git submodule add" "$submodule_url"
        return 1
    fi
    
    # Initialize and update
    git submodule update --init --recursive "$submodule_path"
    
    echo "Submodule added: $submodule_path"
    return 0
}
```

### update_submodules
Updates all submodules.

```bash
update_submodules() {
    local recursive="${1:-true}"
    local init="${2:-true}"
    
    echo "Updating submodules..."
    
    local cmd="git submodule update"
    [ "$init" = "true" ] && cmd="$cmd --init"
    [ "$recursive" = "true" ] && cmd="$cmd --recursive"
    
    if ! $cmd 2>&1; then
        handle_error "3005" "git submodule update"
        return 1
    fi
    
    # Show status
    git submodule status
    
    echo "Submodules updated"
    return 0
}
```

## Helper Functions

### validate_git_url
Validates a git repository URL.

```bash
validate_git_url() {
    local url="$1"
    
    # Check basic format
    if [[ "$url" =~ ^(https?://|git://|ssh://|git@) ]] || [[ "$url" =~ \.git$ ]] || [ -d "$url" ]; then
        return 0
    else
        handle_error "1006" "repository URL" "$url"
        return 1
    fi
}
```

### create_initial_commit
Creates a standard initial commit.

```bash
create_initial_commit() {
    # Create README if it doesn't exist
    if [ ! -f "README.md" ]; then
        echo "# $(basename "$PWD")" > README.md
        echo "" >> README.md
        echo "Created on $(date +%Y-%m-%d)" >> README.md
    fi
    
    # Create .gitignore if it doesn't exist
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore <<EOF
# OS generated files
.DS_Store
Thumbs.db

# Editor files
*.swp
*.swo
*~
.idea/
.vscode/

# Dependencies
node_modules/
vendor/

# Build output
dist/
build/
*.log
EOF
    fi
    
    # Stage and commit
    git add README.md .gitignore
    git commit -m "Initial commit" -m "Initialize repository with README and .gitignore"
}
```

## Usage Examples

### Repository Setup
```bash
# Initialize new repository
init_repository "./my-project" "main" true

# Clone repository
clone_repository "https://github.com/user/repo.git" "local-repo" "develop" 1

# Clone with validation
if clone_repository "$REPO_URL"; then
    cd "$(basename "$REPO_URL" .git)"
    setup_repository_config
fi
```

### Remote Management
```bash
# Add origin remote
add_remote "origin" "git@github.com:user/repo.git" true

# Update remote URL
update_remote "origin" "https://github.com/user/new-repo.git"

# List all remotes with details
list_remotes true
```

### Health Checks
```bash
# Check repository health
if ! check_repository_health; then
    echo "Repository needs attention"
    check_repository_health true  # Try to fix issues
fi

# Get repository information
get_repository_info "json" > repo-info.json
```

## Best Practices

1. **Always validate inputs**: URLs, paths, and names should be validated
2. **Check repository state**: Ensure you're in a git repo before operations
3. **Handle errors gracefully**: Provide helpful error messages
4. **Test connectivity**: Verify remote connections after changes
5. **Use standard configurations**: Apply consistent settings across repos