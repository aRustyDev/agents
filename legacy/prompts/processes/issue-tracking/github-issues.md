---
module: IssueTracking
scope: persistent
triggers: ["create issue", "track work", "update issue", "issue tracking"]
conflicts: []
dependencies: ["DataSanitization"]
priority: high
---

# Issue Tracking Process

## Purpose
Maintain comprehensive tracking of all development work through issues, ensuring no work is undocumented, no problems are forgotten, and all learnings are captured for future reference.

## Trigger
Execute whenever starting new work, encountering problems, or making progress that should be documented.

## Prerequisites
- Issue tracker access (GitHub by default)
- Understanding of work to be tracked
- Any relevant context or parent issues

## Steps

### Step 1: Issue Discovery
```
1.1 Search for existing issues:
    Query: ${issue_tracker} issue list --search "${keywords}"

    Search strategies:
    - Use multiple keyword combinations
    - Check closed issues too
    - Look for similar problems
    - Review related components

1.2 Analyze search results:
    - Is this exact issue already tracked?
    - Is this part of a larger issue?
    - Are there related issues to link?
    - Has this been solved before?

1.3 Determine issue strategy:
    IF exact_issue_exists:
        - Use existing issue
        - Add new context as comment
    ELIF subset_of_existing:
        - Create child issue
        - Link to parent
    ELSE:
        - Create new issue
```

### Step 2: Issue Creation (if needed)
```
2.1 Craft descriptive title:
    Format: [Type] Clear, actionable description
    Examples:
    - "[Bug] Authentication fails when session expires during 2FA"
    - "[Feature] Add CSV export for user activity reports"
    - "[Refactor] Extract payment processing into service class"

2.2 Write comprehensive body:
    Execute: Process: DataSanitization
    Input: Issue description content

    Then structure as:

    ## Problem Statement
    [Clear description of what needs to be done or fixed]

    ## Current Behavior (for bugs)
    [What happens now]

    ## Expected Behavior
    [What should happen]

    ## Acceptance Criteria
    - [ ] Specific, measurable outcome 1
    - [ ] Specific, measurable outcome 2
    - [ ] Tests written and passing
    - [ ] Documentation updated

    ## Technical Approach (if known)
    [High-level solution approach]

    ## Related Issues
    - Related to #123
    - Blocks #456
    - Child of #789

2.3 Add metadata:
    - Labels: Select all applicable
        * Type: bug/feature/refactor/chore
        * Priority: critical/high/medium/low
        * Component: auth/api/ui/database
        * Status: needs:analysis/ready/in-progress
    - Assignee: Self if working on it
    - Milestone: If part of larger effort
    - Project: If tracked in project board
```

### Step 3: Issue Linking
```
3.1 Establish relationships:
    - Parent/Child: Use "Child of #X" in description
    - Blocking: Use "Blocks #X"
    - Related: Use "Related to #X"
    - Duplicate: Close with "Duplicate of #X"

3.2 Cross-reference in other issues:
    - Add comment in parent about child
    - Note in blocked issues
    - Update related issue descriptions

3.3 Project board management:
    IF project_exists:
        - Add issue to appropriate column
        - Set priority within column
        - Add to sprint if applicable
```

### Step 4: Progress Documentation
```
4.1 Regular updates (execute via IssueUpdate):
    Frequency:
    - After each work session
    - When encountering obstacles
    - Upon finding solutions
    - At milestone completions

4.2 Update format:
    ### Progress Update: ${timestamp}

    #### Work Completed
    - [Specific accomplishment]
    - [Progress percentage: X%]

    #### Challenges Encountered
    - Challenge: [Description]
      - Attempted: [Solutions tried]
      - Result: [What happened]

    #### Next Steps
    - [Immediate next action]
    - [Estimated completion]

4.3 Technical documentation:
    - Include sanitized error messages
    - Add relevant code snippets
    - Link to commits/branches
    - Reference external resources
```

### Step 5: Issue Hygiene
```
5.1 Status management:
    - Update labels as status changes
    - Move in project board
    - Keep assignee current

5.2 Child issue tracking:
    - Ensure all children linked
    - Update parent with child progress
    - Close children before parent

5.3 Prevent orphaned issues:
    - Every issue must be:
        * Assigned to someone, OR
        * In a project/milestone, OR
        * Have a clear next action
    - No issue left in limbo
```

### Step 6: Issue Closure
```
6.1 Completion verification:
    - All acceptance criteria met
    - Tests written and passing
    - Documentation updated
    - Code reviewed and merged

6.2 Final documentation:
    ### Resolution Summary

    #### Solution Implemented
    [Brief description of what was done]

    #### Lessons Learned
    - [Key learning 1]
    - [Key learning 2]

    #### Follow-up Items
    - [Any new issues created]
    - [Future improvements identified]

    Resolved in: PR #X, Commit: abc123

6.3 Close with reference:
    - Use "Fixes #X" in PR/commit
    - Or manually close with comment
    - Ensure automation worked
```

## Issue Templates

### Bug Report Template
```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [See error]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., Ubuntu 20.04]
- Version: [e.g., v2.1.0]
- Browser: [if applicable]

## Additional Context
[Any other relevant information]
```

### Feature Request Template
```markdown
## Problem Statement
[What problem does this solve?]

## Proposed Solution
[How should it work?]

## Alternatives Considered
[Other approaches evaluated]

## Acceptance Criteria
- [ ] User can...
- [ ] System should...
- [ ] Tests cover...

## Technical Considerations
[Implementation notes]
```

## Label Strategy

### Type Labels (mutually exclusive)
- `type:bug` - Something broken
- `type:feature` - New functionality
- `type:refactor` - Code improvement
- `type:chore` - Maintenance task

### Status Labels (progressive)
- `needs:triage` - Requires analysis
- `needs:design` - Solution being planned
- `ready` - Ready for development
- `in-progress` - Being worked on
- `needs:review` - PR submitted
- `done` - Completed

### Priority Labels
- `priority:critical` - Production down
- `priority:high` - Major impact
- `priority:medium` - Normal workflow
- `priority:low` - Nice to have

### Special Labels
- `good-first-issue` - For new contributors
- `help-wanted` - Need assistance
- `blocked` - Waiting on dependency
- `wontfix` - Decided not to fix
- `duplicate` - Already tracked elsewhere

## Integration Points

- **Uses**: Process: DataSanitization (for all content)
- **Feeds**: All development processes
- **Triggers**: Project board automation
- **Links to**: Version control via commits
- **Notifies**: Team members when mentioned

## Best Practices

### Do's
- ✅ One issue per problem/feature
- ✅ Search before creating
- ✅ Update regularly
- ✅ Link related issues
- ✅ Close with resolution summary

### Don'ts
- ❌ Create vague issues
- ❌ Leave issues unassigned
- ❌ Skip documentation
- ❌ Close without explanation
- ❌ Let issues go stale

## Common Patterns

### Epic Breakdown
```
Epic: #100 "User Management System"
├── Feature: #101 "User Registration"
│   ├── Task: #102 "Registration form UI"
│   ├── Task: #103 "Email verification"
│   └── Bug: #104 "Fix validation error"
├── Feature: #105 "User Profile"
└── Feature: #106 "Admin Dashboard"
```

### Bug Triage Flow
```
1. Bug reported → Label: needs:triage
2. Confirmed → Label: type:bug, priority:X
3. Assigned → Label: in-progress
4. PR submitted → Label: needs:review
5. Merged → Close with fix reference
```

Remember: Issues are not just task tracking - they're the permanent record of your project's evolution. Future developers (including future you) will thank you for comprehensive issue documentation.
