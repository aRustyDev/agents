---
name: Git Advanced Guide
module_type: guide
scope: temporary
priority: low
triggers: ["git rebase", "git bisect", "git cherry-pick", "interactive rebase", "git reflog", "advanced git"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Git Advanced Guide

## Purpose
Master advanced Git techniques including rebasing, bisecting, cherry-picking, and history manipulation for efficient version control and debugging.

## Interactive Rebase

### Basic Interactive Rebase
```bash
# Rebase last 5 commits
git rebase -i HEAD~5

# Rebase onto another branch
git rebase -i main

# Rebase from specific commit
git rebase -i abc1234^
```

### Rebase Commands
```
# In the editor, you'll see:
pick abc1234 Add feature X
pick def5678 Fix typo
pick ghi9012 Update tests

# Commands available:
# p, pick = use commit
# r, reword = use commit, but edit message
# e, edit = use commit, but stop for amending
# s, squash = use commit, but meld into previous
# f, fixup = like squash, but discard message
# x, exec = run command
# d, drop = remove commit
```

### Common Rebase Workflows

#### Squashing Commits
```bash
# Squash last 3 commits
git rebase -i HEAD~3

# Change to:
pick abc1234 Feature: Add authentication
squash def5678 Fix: Handle edge case
squash ghi9012 Tests: Add auth tests

# Result: One commit with combined changes
```

#### Reordering Commits
```bash
# Original order:
pick abc1234 Add database migration
pick def5678 Add API endpoint
pick ghi9012 Update documentation

# Reorder to:
pick ghi9012 Update documentation
pick abc1234 Add database migration
pick def5678 Add API endpoint
```

#### Editing Past Commits
```bash
# Mark commit for editing
edit abc1234 Add feature with bug

# Git will stop at that commit
# Make your changes
git add .
git commit --amend
git rebase --continue
```

### Resolving Rebase Conflicts
```bash
# During rebase, if conflicts occur:
git status  # See conflicted files

# Fix conflicts in files
git add <resolved-files>
git rebase --continue

# Or abort the rebase
git rebase --abort

# Skip a problematic commit
git rebase --skip
```

## Cherry-Picking

### Basic Cherry-Pick
```bash
# Apply single commit from another branch
git cherry-pick abc1234

# Cherry-pick multiple commits
git cherry-pick abc1234 def5678

# Cherry-pick a range
git cherry-pick abc1234..ghi9012

# Cherry-pick without committing
git cherry-pick -n abc1234
```

### Advanced Cherry-Pick
```bash
# Cherry-pick with edit
git cherry-pick -e abc1234

# Cherry-pick merge commit
git cherry-pick -m 1 merge_commit_sha

# Cherry-pick and track origin
git cherry-pick -x abc1234  # Adds "cherry picked from" to message

# Continue after conflict
git cherry-pick --continue
git cherry-pick --abort
```

## Git Bisect (Binary Search for Bugs)

### Basic Bisect Workflow
```bash
# Start bisect
git bisect start

# Mark current commit as bad
git bisect bad

# Mark known good commit
git bisect good v1.0

# Git checks out middle commit
# Test and mark as good or bad
git bisect good  # or git bisect bad

# Continue until bug commit found
# When done:
git bisect reset
```

### Automated Bisect
```bash
# Create test script (exit 0 for good, 1 for bad)
cat > test.sh << 'EOF'
#!/bin/bash
make test || exit 1
./app | grep -q "ERROR" && exit 1
exit 0
EOF

chmod +x test.sh

# Run automated bisect
git bisect start HEAD v1.0
git bisect run ./test.sh

# Git finds the bad commit automatically
```

### Advanced Bisect Options
```bash
# Skip broken commits
git bisect skip

# Visualize bisect progress
git bisect visualize

# See bisect log
git bisect log

# Replay bisect from log
git bisect replay bisect.log

# Bisect with terms other than good/bad
git bisect start --term-old=fast --term-new=slow
git bisect fast v1.0
git bisect slow HEAD
```

## Reflog (Reference Log)

### Viewing Reflog
```bash
# Show reflog for HEAD
git reflog

# Show reflog for specific branch
git reflog show main

# Detailed reflog with dates
git reflog --date=iso

# Reflog for all references
git reflog --all
```

### Recovering Lost Commits
```bash
# Find lost commit in reflog
git reflog | grep "commit message"

# Recover lost commit
git checkout abc1234
git checkout -b recovered-branch

# Or cherry-pick it
git cherry-pick abc1234

# Recover after bad rebase
git reflog
git reset --hard HEAD@{2}  # Go back 2 reflog entries
```

## Advanced Reset and Checkout

### Reset Modes
```bash
# Soft reset - keep changes staged
git reset --soft HEAD~1

# Mixed reset (default) - keep changes unstaged
git reset HEAD~1

# Hard reset - discard all changes
git reset --hard HEAD~1

# Reset single file
git reset HEAD~1 -- path/to/file
```

### Checkout Advanced
```bash
# Checkout file from another branch
git checkout main -- path/to/file

# Checkout file from specific commit
git checkout abc1234 -- path/to/file

# Create branch from remote
git checkout -b feature origin/feature

# Checkout previous branch
git checkout -
```

## Stash Advanced

### Named and Multiple Stashes
```bash
# Stash with message
git stash save "WIP: feature X"

# Stash including untracked files
git stash -u

# Stash including ignored files
git stash -a

# List stashes with descriptions
git stash list
```

### Stash Operations
```bash
# Apply specific stash
git stash apply stash@{2}

# Apply and drop
git stash pop stash@{1}

# Create branch from stash
git stash branch feature-branch stash@{0}

# Show stash contents
git stash show -p stash@{0}

# Drop specific stash
git stash drop stash@{1}
```

## Submodules

### Working with Submodules
```bash
# Add submodule
git submodule add https://github.com/user/repo libs/repo

# Clone with submodules
git clone --recursive <url>

# Initialize after regular clone
git submodule update --init --recursive

# Update all submodules
git submodule update --remote

# Remove submodule
git rm libs/repo
rm -rf .git/modules/libs/repo
```

## Advanced Merge Strategies

### Merge Strategies
```bash
# Ours strategy - keep our version
git merge -s ours feature-branch

# Recursive with options
git merge -X theirs feature-branch  # Prefer their changes
git merge -X ours feature-branch    # Prefer our changes
git merge -X patience feature-branch # Better diff algorithm

# Octopus merge (multiple branches)
git merge branch1 branch2 branch3
```

### Rerere (Reuse Recorded Resolution)
```bash
# Enable rerere
git config rerere.enabled true

# After resolving conflict once, Git remembers
# Next time same conflict appears, auto-resolved

# See rerere status
git rerere status

# Forget specific resolution
git rerere forget path/to/file
```

## Filter-branch and BFG

### Rewriting History
```bash
# Remove file from entire history
git filter-branch --tree-filter \
  'rm -f passwords.txt' HEAD

# Change author for all commits
git filter-branch --env-filter '
if [ "$GIT_AUTHOR_EMAIL" = "old@email.com" ]; then
    export GIT_AUTHOR_EMAIL="new@email.com"
    export GIT_AUTHOR_NAME="New Name"
fi' HEAD

# Using BFG (faster alternative)
bfg --delete-files passwords.txt
bfg --replace-text passwords.txt
```

## Git Hooks Advanced

### Client-side Hooks
```bash
# pre-commit hook example
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run tests before commit
npm test || exit 1

# Check for console.log
if git diff --cached | grep -q "console.log"; then
    echo "Error: console.log found in staged files"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

### Commit Message Hook
```bash
# commit-msg hook
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
# Check commit message format
pattern="^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}"
if ! grep -qE "$pattern" "$1"; then
    echo "Commit message must follow conventional format"
    exit 1
fi
EOF
```

## Performance Optimization

### Large Repository Handling
```bash
# Shallow clone
git clone --depth 1 <url>

# Partial clone
git clone --filter=blob:none <url>

# Sparse checkout
git sparse-checkout init
git sparse-checkout set src/ docs/

# Garbage collection
git gc --aggressive

# Prune old objects
git prune --expire=now
```

## Debugging Commands

### Blame and Log Analysis
```bash
# Blame with specific range
git blame -L 10,20 file.py

# Blame ignoring whitespace
git blame -w file.py

# Blame showing movement
git blame -M file.py

# Log with graph and decorations
git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit

# Find commits by content
git log -S "function_name" --source --all
```

## Best Practices

### DO
- ✅ Use feature branches for rebasing
- ✅ Backup before dangerous operations
- ✅ Communicate when rewriting shared history
- ✅ Use descriptive commit messages
- ✅ Test after history manipulation

### DON'T
- ❌ Rebase published commits
- ❌ Force push to main/master
- ❌ Ignore reflog for recovery
- ❌ Use filter-branch on shared repos
- ❌ Skip conflict resolution testing

## Emergency Recovery

### Common Recovery Scenarios
```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Recover deleted branch
git reflog | grep "branch_name"
git checkout -b branch_name abc1234

# Fix detached HEAD
git checkout -b temp-branch
# or
git checkout main

# Undo accidental git add
git reset HEAD

# Recover from bad merge
git reflog
git reset --hard HEAD@{n}  # n = steps back
```

---
*Advanced Git techniques provide powerful tools for managing complex development workflows, but use them wisely and always backup important work.*