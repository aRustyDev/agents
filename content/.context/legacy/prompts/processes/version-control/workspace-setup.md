---
module: WorkspaceSetup
scope: context
triggers: ["setup workspace", "start work", "new feature", "new task", "begin development"]
conflicts: []
dependencies: ["PreCommitConfiguration", "IssueTracking"]
priority: high
---

# Workspace Setup Process

## Purpose
Initialize a clean, properly configured workspace before starting any development work, ensuring version control, issue tracking, and development tools are properly configured.

## Trigger
Execute before starting work on any new feature, fix, or refactor.

## Prerequisites
- Repository access confirmed
- Development environment ready
- Issue or task identified

## Steps

### Step 1: Repository Verification
```
1.1 Verify correct repository:
    Run: ${version_control} config remote.origin.url | cat

1.2 Confirm repository matches task:
    - Check URL matches expected project
    - Verify access permissions
    - Ensure latest version

1.3 Check repository status:
    ${version_control} status
    ${version_control} branch --show-current

1.4 Ensure clean working directory:
    IF uncommitted_changes:
        - Stash or commit existing work
        - Document why changes exist
        - Decide if new branch needed
```

### Step 2: Pre-commit Configuration
```
2.1 Execute: Process: PreCommitConfiguration
    - Checks for .pre-commit-config.yaml
    - Proposes configuration if missing
    - Updates hooks if needed
    - Installs git hooks

2.2 Wait for approval if changes proposed:
    - Review suggested hooks
    - Confirm additions appropriate
    - Allow customization

2.3 Verify installation:
    pre-commit --version
    pre-commit run --all-files (test run)
```

### Step 3: Branch Creation
```
3.1 Determine branch type:
    - feature/ for new functionality
    - fix/ for bug fixes
    - refactor/ for code improvement
    - chore/ for maintenance tasks

3.2 Generate branch name:
    Format: ${branch_prefix}${issue_number}-${brief-description}
    Example: feature/234-user-avatar-upload

    Rules:
    - Use issue number if available
    - Keep description brief (3-5 words)
    - Use kebab-case
    - Be specific but concise

3.3 Create and checkout branch:
    ${version_control} checkout -b ${branch_name}

3.4 Set upstream tracking:
    ${version_control} branch --set-upstream-to=origin/main
```

### Step 4: Push Branch to Remote
```
4.1 Push branch to establish remote:
    ${version_control} push -u origin ${branch_name}

4.2 Verify push succeeded:
    - Check remote repository
    - Confirm branch visible
    - Note branch protection rules

4.3 Document branch creation:
    - Add branch name to issue
    - Link in project board
    - Notify team if needed
```

### Step 5: Issue Tracking Initialization
```
5.1 Execute: Process: IssueTracking
    Purpose: Create or link work to issue

5.2 Ensure issue contains:
    - Clear description of work
    - Acceptance criteria
    - Branch name reference
    - Assigned to self

5.3 Update issue with startup:
    "Started work on branch: ${branch_name}
     Setup completed: ${timestamp}
     Estimated completion: ${estimate}"
```

### Step 6: Environment Validation
```
6.1 Verify development tools:
    - Language version correct
    - Dependencies installed
    - IDE configured

6.2 Run initial test suite:
    - Ensure all tests passing
    - Note baseline coverage
    - Check performance benchmarks

6.3 Document environment:
    IF special_requirements:
        - Note in issue
        - Update README if needed
        - Share with team
```

## Output
- Clean workspace on new branch
- Issue tracking initialized
- Pre-commit hooks installed
- Remote branch established
- Ready for development

## Decision Points

### Existing Work in Progress
```
IF uncommitted_changes_exist:
    Options:
    1. Stash changes: ${version_control} stash save "WIP: ${description}"
    2. Commit to current branch before switching
    3. Create new worktree for parallel work

    Recommend based on:
    - Changes related to new work?
    - Current branch mergeable?
    - Need to preserve state?
```

### Branch Naming Conflicts
```
IF branch_already_exists:
    Options:
    1. Use existing branch (if same work)
    2. Add suffix: -v2, -retry, -new
    3. Delete old branch if obsolete

    Check:
    - Is old work complete?
    - Was it merged?
    - Different approach needed?
```

## Integration Points

- **Executes**: Process: PreCommitConfiguration
- **Executes**: Process: IssueTracking
- **Triggers**: Development workflow readiness
- **Updates**: Issue with branch information
- **Enables**: Clean commit history

## Common Patterns

### Feature Branch Setup
```bash
# For feature #234: Add user avatars
git checkout main
git pull origin main
git checkout -b feature/234-user-avatars
git push -u origin feature/234-user-avatars
# Update issue #234 with branch name
```

### Hotfix Branch Setup
```bash
# For critical bug #567
git checkout production
git pull origin production
git checkout -b fix/567-critical-auth-bug
git push -u origin fix/567-critical-auth-bug
# Mark issue #567 as in-progress
```

### Parallel Work Setup
```bash
# When needing to work on multiple features
git worktree add ../project-feature-a feature/234-avatars
git worktree add ../project-feature-b feature/235-notifications
# Each worktree is independent
```

## Best Practices

### Do's
- ✅ Always verify repository before starting
- ✅ Keep branch names descriptive but short
- ✅ Push immediately after branch creation
- ✅ Link all work to issues
- ✅ Configure pre-commit hooks early

### Don'ts
- ❌ Work directly on main/master
- ❌ Create branches without issues
- ❌ Skip pre-commit configuration
- ❌ Use generic branch names
- ❌ Forget to push new branches

## Troubleshooting

### Can't Create Branch
```
Error: "A branch named 'feature/x' already exists"
Solutions:
1. Check if you're resuming work: git checkout feature/x
2. Delete old branch: git branch -D feature/x
3. Use different name: feature/x-v2
```

### Pre-commit Installation Fails
```
Error: "pre-commit not found"
Solutions:
1. Install pre-commit: pip install pre-commit
2. Use brew/apt: brew install pre-commit
3. Check Python environment activated
```

### Push Rejected
```
Error: "rejected - non-fast-forward"
Solutions:
1. You're not up to date: git pull origin main
2. Branch protection active - check rules
3. Wrong base branch - verify upstream
```

Remember: A properly configured workspace prevents problems later. The few minutes spent on setup save hours of debugging and merge conflicts.
