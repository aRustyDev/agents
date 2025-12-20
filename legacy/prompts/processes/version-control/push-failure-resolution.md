---
module: PushFailureResolution
scope: context
triggers: ["push failed", "push rejected", "cannot push", "push error"]
conflicts: []
dependencies: ["IssueTracking", "RecurringProblemIdentification"]
priority: high
---

# Push Failure Resolution Process

## Purpose
Systematically resolve issues preventing code from being pushed to remote repositories while capturing patterns that could be automated or prevented, ensuring development flow continues smoothly.

## Trigger
Executes when attempting to push commits results in failure, regardless of the underlying cause.

## Prerequisites
- Local commits ready to push
- Remote repository access (normally)
- Understanding of intended changes

## Steps

### Step 1: Capture Failure Details
```
1.1 Record complete error message:
    Capture full output from:
    ${version_control} push

    Include:
    - Exact error message
    - Remote repository URL
    - Branch names (local and remote)
    - Any hints provided by git

1.2 Identify failure category:
    Parse error for common patterns:
    - "rejected - non-fast-forward" → Remote has diverged
    - "Permission denied" → Authentication issue
    - "protected branch" → Branch protection
    - "pre-receive hook declined" → Server-side hook
    - "Connection refused" → Network issue
    - "does not appear to be a git repository" → Configuration issue

1.3 Document context:
    - What changes were being pushed
    - How long since last successful push
    - Any recent configuration changes
    - Team members who might have pushed
```

### Step 2: Issue Tracking Creation
```
2.1 Check for existing patterns:
    Query: ${issue_tracker} issue list --search "push ${error_keywords}"

    Look for:
    - Same error message
    - Similar failure patterns
    - Previous resolutions
    - Frequency of occurrence

2.2 Create or update tracking issue:
    IF pattern_exists:
        Update existing issue with new occurrence
    ELSE:
        Create new issue:

    Title: "Push Failure: ${error_category}"
    Labels: ['infrastructure', 'blocking', 'version-control']

    Body:
    """
    ## Push Failure Details

    ### Error Message
    ```
    ${full_error_output}
    ```

    ### Context
    - Repository: ${repo_url}
    - Branch: ${local_branch} → ${remote_branch}
    - Commits attempting to push: ${count}
    - Last successful push: ${timestamp_or_unknown}

    ### Initial Assessment
    ${likely_cause_based_on_error}

    ### Impact
    - Work blocked: ${description}
    - Team members affected: ${who}
    - Urgency: ${critical/high/medium}
    """
```

### Step 3: Resolution by Category

#### 3.1 Remote Divergence (non-fast-forward)
```
3.1.1 Fetch latest changes:
    ${version_control} fetch origin

3.1.2 Examine divergence:
    ${version_control} log HEAD..origin/${branch} --oneline
    ${version_control} log origin/${branch}..HEAD --oneline

3.1.3 Choose integration strategy:
    Option A - Rebase (preferred for linear history):
        ${version_control} rebase origin/${branch}

        If conflicts:
        - Resolve each conflict carefully
        - Test after each resolution
        - Continue rebase: ${version_control} rebase --continue

    Option B - Merge (when rebase inappropriate):
        ${version_control} merge origin/${branch}

        If conflicts:
        - Resolve conflicts
        - Test thoroughly
        - Commit merge

3.1.4 Verify changes preserved:
    - Run test suite
    - Check your changes still present
    - Ensure no functionality lost

3.1.5 Retry push:
    ${version_control} push origin ${branch}
```

#### 3.2 Authentication Failure
```
3.2.1 Verify credentials:
    For HTTPS:
    - Check stored credentials
    - Update personal access token if expired
    - Verify username correct

    For SSH:
    - Test connection: ssh -T git@github.com
    - Check SSH key: ssh-add -l
    - Verify key added to remote service

3.2.2 Fix authentication:
    HTTPS token update:
    - Generate new token on service
    - Update credential manager
    - Test with: ${version_control} fetch

    SSH key issues:
    - Add key: ssh-add ~/.ssh/id_rsa
    - Or generate new: ssh-keygen -t ed25519
    - Add public key to service

3.2.3 Update team documentation:
    If process unclear:
    - Document steps taken
    - Update onboarding guide
    - Share with team
```

#### 3.3 Protected Branch
```
3.3.1 Understand protection:
    - Check branch protection rules
    - Verify you're on correct branch
    - Confirm workflow expectations

3.3.2 Follow proper workflow:
    Typically:
    - Create feature branch
    - Push feature branch
    - Open pull request
    - Get reviews
    - Merge via PR

3.3.3 If emergency override needed:
    - Document justification
    - Get approval from admin
    - Temporarily adjust rules
    - Push changes
    - Restore protection
```

#### 3.4 Hook Rejection
```
3.4.1 Parse hook output:
    Identify:
    - Which hook failed
    - Specific violations
    - Required fixes

3.4.2 Common hook issues:
    Commit message format:
    - Fix message format
    - Amend commit: ${version_control} commit --amend

    Code quality:
    - Run linters locally
    - Fix identified issues
    - Update commits

    Security scanning:
    - Remove sensitive data
    - Update to secure methods
    - Clean git history if needed

3.4.3 Rewrite history if needed:
    If multiple commits need fixing:
    ${version_control} rebase -i origin/${branch}
    - Edit problematic commits
    - Fix issues
    - Continue rebase
```

#### 3.5 Network/Connection Issues
```
3.5.1 Diagnose connectivity:
    - Ping remote host
    - Check VPN if required
    - Verify proxy settings
    - Test alternative network

3.5.2 Common fixes:
    Proxy configuration:
    ${version_control} config --global http.proxy http://proxy:port

    DNS issues:
    - Try IP instead of hostname
    - Flush DNS cache
    - Use alternative DNS

    Firewall blocking:
    - Check corporate firewall
    - Try different port
    - Use HTTPS instead of SSH

3.5.3 Workarounds:
    - Push from different network
    - Use personal hotspot
    - Ask colleague to push
    - Wait for network fix
```

### Step 4: Verify Resolution
```
4.1 Confirm push succeeded:
    - Check remote repository
    - Verify all commits present
    - Ensure branch updated
    - Check CI/CD triggered

4.2 Test functionality:
    - Pull on another machine
    - Run test suite
    - Verify nothing broken
    - Check with teammates
```

### Step 5: Document Resolution
```
5.1 Update tracking issue:
    Execute: Process: IssueUpdate

    Include:
    """
    ## Resolution Summary

    ### Root Cause
    ${identified_root_cause}

    ### Solution Applied
    Steps taken:
    1. ${step_1}
    2. ${step_2}

    ### Time to Resolve
    ${duration} minutes

    ### Lessons Learned
    - ${lesson_1}
    - ${lesson_2}

    ### Preventive Measures
    ${how_to_prevent_recurrence}
    """

5.2 Check for automation opportunity:
    IF resolution_could_be_automated:
        Execute: Process: RecurringProblemIdentification
        Context: Push failure pattern

5.3 Close issue:
    - Mark as resolved
    - Add resolution label
    - Link any automation issues
```

### Step 6: Prevention Planning
```
6.1 Identify prevention opportunities:
    Could this be prevented by:
    - Pre-push hooks?
    - Better documentation?
    - Workflow changes?
    - Tool configuration?
    - Team communication?

6.2 Implement preventions:
    Pre-push hook example:
    """
    #!/bin/bash
    # Prevent push if remote has diverged

    UPSTREAM=${1:-'@{u}'}
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse "$UPSTREAM")
    BASE=$(git merge-base @ "$UPSTREAM")

    if [ $LOCAL = $REMOTE ]; then
        echo "Branch is up to date"
    elif [ $LOCAL = $BASE ]; then
        echo "Error: Need to pull first"
        echo "Run: git pull --rebase"
        exit 1
    fi
    """

6.3 Share knowledge:
    - Update team playbook
    - Add to troubleshooting guide
    - Share in team channel
    - Consider automation
```

## Common Patterns and Quick Fixes

### Pattern: Forgot to Pull
```bash
# Quick fix
git pull --rebase origin main
git push

# Prevention
Add to pre-push hook or create habit
```

### Pattern: Pushed to Wrong Branch
```bash
# Quick fix
git push origin HEAD:correct-branch-name

# Prevention
Use push.default = current
Check branch before pushing
```

### Pattern: Large Files Rejected
```bash
# Quick fix
git rm --cached large-file
git commit --amend
git push

# Long-term fix
Add .gitignore rules
Use Git LFS for large files
```

## Integration Points

- **Called by**: Process: CommitWork (step 5)
- **Called by**: Process: TestDrivenDevelopment (step 5)
- **Creates**: Issues for tracking patterns
- **May trigger**: Process: RecurringProblemIdentification
- **Updates**: Team documentation

## Escalation Path

If standard resolution fails:
1. Check with team lead
2. Consult platform documentation
3. Contact repository admin
4. Open support ticket
5. Find alternative solution

## Best Practices

### Do's
- ✅ Always capture full error messages
- ✅ Document resolution steps
- ✅ Check for patterns
- ✅ Share solutions with team
- ✅ Automate where possible

### Don'ts
- ❌ Force push without understanding
- ❌ Ignore recurring patterns
- ❌ Skip documentation
- ❌ Work around without fixing
- ❌ Blame tools first

Remember: Push failures often indicate process issues rather than technical problems. Each resolution is an opportunity to improve team workflows and prevent future occurrences.
