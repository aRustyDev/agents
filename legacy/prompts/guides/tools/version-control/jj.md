---
name: Jujutsu (jj) Version Control Guide
module_type: guide
scope: temporary
priority: low
triggers: ["jj", "jujutsu", "jj vcs", "git alternative", "jujutsu version control"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Jujutsu (jj) Version Control Guide

## Purpose
Master Jujutsu (jj), a Git-compatible VCS that reimagines version control with automatic commits, powerful history editing, and conflict-free rebasing.

## What is Jujutsu?

Jujutsu is a Git-compatible VCS that provides:
- **Automatic working copy commits**: Every change is automatically committed
- **First-class conflicts**: Conflicts are recorded in commits, not working copy
- **Powerful history editing**: Easy undo, evolution, and rewriting
- **No staging area**: Simplifies the commit process
- **Git compatibility**: Works with existing Git repos

## Installation and Setup

### Installation
```bash
# macOS with Homebrew
brew install jj

# Install from source
cargo install --git https://github.com/martinvonz/jj.git --bin jj jujutsu

# Verify installation
jj --version
```

### Initial Configuration
```bash
# Set user name and email
jj config set --user user.name "Your Name"
jj config set --user user.email "you@example.com"

# Set default editor
jj config set --user ui.editor "code --wait"

# Enable color output
jj config set --user ui.color "always"

# Set up Git integration
jj config set --user git.auto-local-bookmark true
```

### Repository Setup
```bash
# Initialize new jj repo
jj init

# Clone existing Git repo
jj git clone https://github.com/user/repo.git

# Convert existing Git repo
cd existing-git-repo
jj git init --colocate
```

## Core Concepts

### Working Copy Commit
- Jujutsu automatically creates a commit for your working copy
- No staging area - all changes are in the working copy commit
- The working copy commit has a special symbol: `@`

### Change IDs vs Commit IDs
- **Change ID**: Stable identifier that survives rebasing (e.g., `qpvuntsm`)
- **Commit ID**: Git-compatible SHA (e.g., `65b1ef43`)
- Change IDs are what you typically work with

### Revisions and Revsets
```bash
# Current working copy
@

# Parent of working copy
@-

# All descendants of main
main..

# All ancestors of @
..@

# Commits by author
author(martinvonz)

# Commits with description matching pattern
description(glob:"fix*")
```

## Basic Operations

### Viewing Status
```bash
# Show current status
jj status

# Show log (graph view)
jj log

# Show log with more detail
jj log -r 'all()'

# Show specific revision
jj show abc123
```

### Making Changes
```bash
# Edit files (changes auto-committed to working copy)
echo "Hello" > file.txt

# Check status
jj status

# Describe the working copy commit
jj describe -m "Add hello file"

# Create a new change (commit) and start working on it
jj new
jj new -m "Start new feature"

# Insert a new change after a specific commit
jj new abc123 -m "Fix issue"
```

### Navigating History
```bash
# Move to a different commit
jj edit abc123

# Go back to previous location
jj edit @-

# Create new commit on top of specific revision
jj new main
```

## Advanced Workflows

### Branching Without Branches
```bash
# Jujutsu doesn't require branches for parallel work
# Start feature 1
jj new main -m "Feature 1"
echo "feature1" > feature1.txt

# Start feature 2 (parallel to feature 1)
jj new main -m "Feature 2"
echo "feature2" > feature2.txt

# See parallel changes
jj log

# Merge features
jj new feature1 feature2 -m "Merge features"
```

### History Editing
```bash
# Squash current change into parent
jj squash

# Squash specific changes
jj squash -r xyz789

# Move changes from one commit to another
jj squash --from abc123 --into def456

# Split a commit
jj split -r abc123

# Reorder commits
jj rebase -r abc123 -d xyz789

# Abandon a change
jj abandon abc123
```

### Undo Operations
```bash
# Undo last operation
jj undo

# Undo multiple operations
jj undo -n 3

# See operation history
jj op log

# Restore to specific operation
jj op restore abc123
```

## Git Integration

### Working with Git Remotes
```bash
# Add Git remote
jj git remote add origin https://github.com/user/repo.git

# Fetch from remote
jj git fetch

# Push to remote
jj git push

# Push specific change
jj git push -r abc123

# Create Git branch for a change
jj bookmark create -r abc123 my-feature

# Push bookmark to Git branch
jj git push --bookmark my-feature
```

### Git Interoperability
```bash
# Import Git refs
jj git import

# Export to Git
jj git export

# Show Git refs
jj log -r 'bookmarks()'

# Track Git branch
jj bookmark track main@origin
```

## Conflict Resolution

### Working with Conflicts
```bash
# Conflicts are stored in commits, not working copy
# Create a conflict
jj new main feature -m "Merge with conflict"

# See conflict markers in files
cat conflicted.txt

# Resolve conflict by editing
vim conflicted.txt

# Check resolution
jj status

# Conflicts auto-resolve when fixed
```

### Conflict Tools
```bash
# Use merge tool
jj resolve

# List conflicts
jj resolve --list

# Use specific tool
jj resolve --tool vimdiff
```

## Advanced Features

### Revsets (Query Language)
```bash
# Complex queries
# All commits not merged to main
jj log -r 'all() ~ ancestors(main)'

# Commits in the last week
jj log -r 'committer_date(after:"1 week ago")'

# My commits that touch specific file
jj log -r 'author(me) & file(path/to/file)'

# Commits between two revisions
jj log -r 'x..y'

# All merge commits
jj log -r 'merge()'
```

### Templates
```bash
# Custom log format
jj log --template '
commit_id.short() ++ " " ++ 
description.first_line() ++ 
" (" ++ author.name() ++ ")"
'

# Set default template
jj config set --user template.log_node '
if(current_working_copy, "@", "○")
'
```

### Workspaces
```bash
# Create new workspace
jj workspace add ../jj-feature

# List workspaces
jj workspace list

# Update workspace
cd ../jj-feature
jj workspace update-stale
```

## Practical Examples

### Feature Development Flow
```bash
# Start from main
jj new main -m "feat: add user authentication"

# Work on feature
echo "auth code" > auth.py
jj describe -m "feat: implement login functionality"

# Realize you need a fix first
jj new main -m "fix: update dependencies"
echo "updated" > requirements.txt

# Continue feature on top of fix
jj rebase -r @-- -d @  # Rebase feature onto fix
jj edit @--  # Go back to feature

# Squash when ready
jj squash  # Squash working copy into feature commit
```

### Code Review Workflow
```bash
# Create changes for review
jj new main -m "feat: new feature"

# Make changes based on review
jj describe  # Update description
vim file.py  # Make requested changes

# Split for easier review
jj split  # Split current changes
jj describe -m "refactor: extract helper function"
jj new -m "feat: use helper in feature"

# Push for review
jj git push --bookmark feature-branch
```

### Experimentation
```bash
# Save current state
jj describe -m "WIP: current approach"

# Try different approach
jj new @- -m "experiment: alternative approach"
# Make experimental changes

# Compare approaches
jj diff -r @- -r @

# Keep experiment
jj abandon @--  # Remove WIP
# Or abandon experiment
jj abandon @
jj edit @-
```

## Configuration

### Config File (~/.jjconfig.toml)
```toml
[user]
name = "Your Name"
email = "you@example.com"

[ui]
editor = "code --wait"
diff-editor = "meld"
color = "always"
default-command = "log"

[git]
auto-local-bookmark = true

[revset-aliases]
"mine" = "author(me)"
"recent" = 'committer_date(after:"2 weeks ago")'

[template-aliases]
'format_short_id(id)' = 'id.shortest(8)'
```

## Tips and Tricks

### Aliases
```bash
# Shell aliases for common operations
alias js='jj status'
alias jl='jj log'
alias jn='jj new'
alias jd='jj describe'
alias je='jj edit'

# Revset aliases
jj config set --user revset-aliases.mine 'author(exact:"me")'
jj log -r 'mine'
```

### Integration with Editors
```bash
# VS Code
jj config set --user ui.editor "code --wait"

# Vim with fugitive-like experience
jj config set --user ui.editor "vim -c 'set ft=gitcommit'"

# IntelliJ IDEA
jj config set --user ui.editor "idea --wait"
```

## Comparison with Git

### Advantages
- No staging area complexity
- Automatic commits prevent work loss
- First-class conflicts
- Powerful history editing
- Simpler mental model

### Different Concepts
| Git | Jujutsu |
|-----|---------|
| Staging area | Automatic commits |
| Branches | Anonymous branches + bookmarks |
| HEAD | @ (working copy) |
| Detached HEAD | Normal state |
| Merge conflicts | Conflict commits |

## Troubleshooting

### Common Issues
```bash
# Recover from mistakes
jj op log  # See what happened
jj undo    # Undo last operation

# Fix divergent changes
jj evolve  # Automatically evolve orphaned changes

# Resolve Git integration issues
jj git import  # Re-import Git refs
jj git export  # Re-export to Git

# Debug revsets
jj log -r 'abc123' --debug
```

### Getting Help
```bash
# General help
jj help

# Command help
jj help new

# Revset help
jj help revsets

# Template help
jj help templates
```

---
*Jujutsu reimagines version control with a focus on simplicity and power, making complex workflows feel natural while maintaining Git compatibility.*