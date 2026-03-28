---
module: RecurringProblemIdentification
scope: context
triggers: ["recurring problem", "pattern detected", "repeated issue", "automation opportunity"]
conflicts: []
dependencies: ["IssueTracking", "PreCommitHookResolution"]
priority: high
---

# Recurring Problem Identification Process

## Purpose
Identify patterns in development issues that could be prevented through automation, creating a learning system that continuously improves the development workflow by converting repeated manual fixes into automated checks.

## Trigger
Execute when:
- Same type of error occurs multiple times
- Pre-commit hooks fail repeatedly for similar reasons
- Code review feedback shows patterns
- Manual fixes are applied more than twice
- CI/CD failures show patterns
- Team members report repetitive tasks

## Prerequisites
- Access to issue tracking history
- Understanding of the problem encountered
- Ability to query past occurrences

## Steps

### Step 1: Problem Documentation
```
1.1 Record current instance:
    Create detailed record of:
    - Error type and exact message
    - Context when it occurred
    - File types affected
    - Time spent fixing
    - Solution applied

1.2 Capture technical details:
    - Full error output (sanitized)
    - Code diff of the fix
    - Commands used to resolve
    - Dependencies involved

1.3 Note impact:
    - Development time lost
    - Potential production impact
    - Team members affected
    - Frustration level (honest assessment)
```

### Step 2: Pattern Analysis
```
2.1 Search for similar occurrences:
    Query issue tracker:
    - ${issue_tracker} issue list --search "${error_keywords}"
    - Check closed issues too
    - Search commit messages for fixes
    - Review PR comments

2.2 Analyze frequency:
    Count occurrences:
    - How many times this month?
    - How many different people hit it?
    - Is frequency increasing?
    - Any correlation with events?

2.3 Calculate automation value:
    Value = (Frequency × Time_per_fix × Team_size) - Automation_cost

    If Value > threshold:
        Proceed with automation
    Else:
        Document for future reference
```

### Step 3: Problem Categorization
```
3.1 Identify problem type:

    Syntax/Formatting Issues:
    - Inconsistent indentation
    - Missing semicolons
    - Import ordering
    - Trailing whitespace
    → Solution: Formatting hooks

    Code Quality Issues:
    - Unused variables
    - Complex functions
    - Missing documentation
    - Poor naming
    → Solution: Linting hooks

    Security Issues:
    - Hardcoded credentials
    - Insecure functions
    - Missing validation
    - SQL injection risks
    → Solution: Security scanning hooks

    Project Conventions:
    - Custom naming rules
    - File organization
    - Commit message format
    - API patterns
    → Solution: Custom hooks

    Dependency Issues:
    - Outdated packages
    - Security vulnerabilities
    - License conflicts
    - Version mismatches
    → Solution: Dependency checking hooks

3.2 Assess automation feasibility:
    Can this be:
    - Automatically detected? (Static analysis)
    - Automatically fixed? (Safe transforms)
    - Partially automated? (Assisted fixes)
    - Only warned about? (Human judgment needed)
```

### Step 4: Historical Pattern Documentation
```
4.1 Create pattern record:
    Document in issue tracker:

    Title: "[Pattern] ${problem_type} occurring ${frequency}/month"

    Body:
    ## Pattern Description
    ${detailed_description}

    ## Occurrences
    - Issue #123: ${date} - ${person} - ${time_spent}
    - Issue #456: ${date} - ${person} - ${time_spent}
    - Commit abc123: Fixed same issue

    ## Impact Analysis
    - Total time lost: ${total_hours} hours
    - People affected: ${count}
    - Trending: ${up/down/stable}

    ## Proposed Solution
    Automate via pre-commit hook that ${solution_description}

    ## Implementation Priority
    ${high/medium/low} based on ${reasoning}

4.2 Link related issues:
    - Tag all instances with pattern label
    - Create relationships in tracker
    - Note in each issue
```

### Step 5: Solution Strategy
```
5.1 Determine implementation approach:

    IF existing_tool_available:
        Research existing solutions:
        - Search pre-commit hook registry
        - Check awesome-pre-commit lists
        - Look for language-specific tools
        - Evaluate and test options
        → Execute: Process: PreCommitHookResolution
           Type: "find_existing"

    ELIF simple_pattern_matching:
        Create basic hook:
        - Regex-based detection
        - Clear error messages
        - Optional auto-fix
        → Execute: Process: PreCommitHookResolution
           Type: "create_custom"
           Complexity: "simple"

    ELIF complex_logic_required:
        Develop advanced hook:
        - AST parsing
        - Multi-file analysis
        - Context awareness
        → Execute: Process: PreCommitHookResolution
           Type: "create_custom"
           Complexity: "complex"

    ELSE:
        Document best practices:
        - Create team guidelines
        - Add to onboarding docs
        - Regular reminder in reviews
```

### Step 6: Tracking and Validation
```
6.1 Set up monitoring:
    - Track if pattern continues after fix
    - Measure time saved
    - Count prevented occurrences
    - Gather team feedback

6.2 Create success metrics:
    - Pattern occurrences should drop to near zero
    - No false positives causing friction
    - Team satisfaction with solution
    - Measurable time savings

6.3 Schedule review:
    - One month: Is it working?
    - Three months: Still valuable?
    - Six months: Needs adjustment?
```

## Pattern Examples

### Example 1: Import Sorting Issues
```
Pattern Detected:
- 15 PR comments about import order this month
- 3 different developers affected
- ~10 minutes per fix

Analysis:
- Python imports not following PEP8
- No automated checking in place
- Easy to automate with isort

Solution:
- Add isort pre-commit hook
- Configure for project style
- Auto-fix on commit
```

### Example 2: Trailing Comma in JSON
```
Pattern Detected:
- CI fails 2-3 times/week on JSON syntax
- Always trailing comma issue
- 15-20 minutes to fix and re-run

Analysis:
- Developers adding commas from habit
- JSON doesn't allow trailing commas
- Simple to detect and fix

Solution:
- Add JSON syntax checking hook
- Auto-remove trailing commas
- Warn about invalid JSON
```

### Example 3: Hardcoded Development URLs
```
Pattern Detected:
- Production incidents from localhost URLs
- Happened 3 times in 6 months
- Major impact each time

Analysis:
- Developers forgetting to use config
- No automated checking
- Critical to prevent

Solution:
- Custom hook to scan for localhost/127.0.0.1
- Block commits with hardcoded dev URLs
- Suggest config usage
```

## Decision Matrix

| Frequency | Impact | Action |
|-----------|---------|---------|
| Daily | Any | Automate immediately |
| Weekly | High | Automate soon |
| Weekly | Low | Consider automation |
| Monthly | High | Automate if easy |
| Monthly | Low | Document pattern |
| Rare | High | Add to checklist |
| Rare | Low | Note for future |

## Integration Points

- **Triggered by**: CommitWork failures, PR reviews, CI/CD failures
- **Executes**: Process: PreCommitHookResolution
- **Updates**: Issue tracker with patterns
- **May trigger**: Process: PreCommitHookContribution
- **Feeds into**: Architecture review metrics

## Automation ROI Calculation

```
Time_saved_per_month = Occurrences × Average_fix_time × Team_size
Implementation_cost = Development_hours × Hourly_rate
Maintenance_cost = Monthly_hours × Hourly_rate
Break_even_months = Implementation_cost / (Time_saved_per_month - Maintenance_cost)

If Break_even_months < 6:
    Strong candidate for automation
```

## Best Practices

### Do's
- ✅ Track all occurrences, even minor ones
- ✅ Quantify impact in time and frustration
- ✅ Consider team-wide impact
- ✅ Start with simple automations
- ✅ Measure success after implementation

### Don'ts
- ❌ Automate rare edge cases
- ❌ Create brittle solutions
- ❌ Over-engineer simple fixes
- ❌ Ignore false positive impact
- ❌ Forget to document patterns

## Common Anti-patterns

### Over-automation
Creating complex hooks for rare problems causes more friction than value. Always weigh frequency against complexity.

### Under-documentation
Finding the same pattern six months later because nobody documented it the first time. Always create pattern issues.

### Ignoring Feedback
Implementing automation that technically works but frustrates developers. Always gather and act on team feedback.

Remember: The goal is to free developers from repetitive tasks so they can focus on creative problem-solving. Every automated check is a gift to your future self and your team.
