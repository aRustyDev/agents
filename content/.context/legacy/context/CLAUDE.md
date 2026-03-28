rev# Configuration

## Tool Defaults
```yaml
version_control: git
issue_tracker: github
project_management: github_projects
search_tool: grep
branch_prefix: feature/
commit_style: conventional
test_framework: auto-detect

# Sanitization Tools (in order of preference)
sanitization_tools:
  text:
    - tool: sed
      available: check
      complexity: simple
    - tool: awk
      available: check
      complexity: medium
    - tool: perl
      available: check
      complexity: complex
    - tool: python
      available: assume
      complexity: any

  json:
    - tool: jq
      available: check
      complexity: any
    - tool: python
      available: assume
      complexity: any

  structured_logs:
    - tool: awk
      available: check
      complexity: medium
    - tool: python
      available: assume
      complexity: any

# Sanitization Patterns
sanitization_patterns:
  # Pattern format: name -> [regex, replacement, tool_hint]
  email: ['[\w\.-]+@[\w\.-]+\.\w+', '<email>', 'simple']
  ipv4: ['\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<ip-address>', 'simple']
  uuid: ['[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '<uuid>', 'simple']
  ssh_key: ['-----BEGIN [\w\s]+ KEY-----[\s\S]+?-----END [\w\s]+ KEY-----', '<ssh-key-REDACTED>', 'medium']
  api_key: ['(api[_-]?key|token|bearer)[\s:=]+["\'`]?[\w\-]{20,}["\'`]?', '\1=<api-key-REDACTED>', 'medium']
  path_username: ['/home/([^/]+)/', '/home/<username>/', 'simple']
  path_users: ['/Users/([^/]+)/', '/Users/<username>/', 'simple']
```

## Development Patterns
```yaml
available_patterns:
  - TestDrivenDevelopment (TDD)
  - CoverageDrivenDevelopment (CDD)
  - BehaviorDrivenDevelopment (BDD)

active_pattern: TestDrivenDevelopment
```

# Core Principles

## ALWAYS
- Write atomic code following Single Responsibility Principle
- Ask for clarification on ambiguous requirements
- State understanding before proceeding
- Record all work in issue tracker
- Follow the active development pattern
- Verify repository context before using CLI tools

## NEVER
- Edit .pre-commit-config.yaml without confirmation
- Skip issue tracking updates
- Assume requirements without verification
- Proceed without a clear plan
- Mix multiple responsibilities in a single function/module

# Workflows

## Workflow: FeatureDevelopment
```
Trigger: New feature request
Pattern: Uses ${active_pattern} from configuration
Steps:
1. Process: WorkspaceSetup
2. Process: CodebaseReview (Feature Focus)
3. Process: FeaturePlanning
4. Process: DevelopmentExecution → ${active_pattern}
5. Process: CodeQualityReview
6. Process: WorkspaceCleanup
7. Process: SubmitWork
```

## Workflow: BugFix
```
Trigger: Bug report or error identification
Steps:
1. Process: WorkspaceSetup
2. Process: CodebaseReview (Bug Focus)
3. Process: BugAnalysis
4. Process: FixPlanning
5. Process: DevelopmentExecution → TestDrivenDevelopment
6. Process: RegressionPrevention
7. Process: WorkspaceCleanup
8. Process: SubmitWork
```

## Workflow: Refactoring
```
Trigger: Code improvement need
Steps:
1. Process: WorkspaceSetup
2. Process: CodebaseReview (Refactor Focus)
3. Process: RefactorPlanning
4. Process: SafetyNetCreation
5. Process: RefactorExecution
6. Process: CodeQualityReview
7. Process: WorkspaceCleanup
8. Process: SubmitWork
```

# Process Definitions

## Process: WorkspaceSetup
### Purpose
Initialize a clean, tracked workspace for development

### Trigger
Start of any development workflow

### Steps
```
1. Verify Repository
   1.1 Run: `${version_control} config remote.origin.url | cat`
   1.2 Confirm correct repository
   1.3 Check current branch: `${version_control} branch --show-current`

2. Pre-commit Configuration Check
   2.1 Execute: Process: PreCommitConfiguration
   2.2 Wait for user approval if changes needed
   2.3 Install hooks if approved

3. Create Working Branch
   3.1 Determine branch type (feature/fix/refactor)
   3.2 Generate branch name: ${branch_prefix}${issue_number}-${brief_description}
   3.3 Create and checkout: `${version_control} checkout -b ${branch_name}`

4. Push Branch
   4.1 Push to remote: `${version_control} push -u origin ${branch_name}`
   4.2 Verify push successful

5. Initialize Issue Tracking
   5.1 Execute: Process: IssueCreation
   5.2 Link branch to issue if supported
```

### Output
- Working branch created and pushed
- Issue tracker initialized
- Pre-commit hooks configured
- Workspace ready for development

---

## Process: IssueCreation
### Purpose
Create or update issue tracking for current work

### Steps
```
1. Search Existing Issues
   1.1 Query: `${issue_tracker} issue list --search "${keywords}"`
   1.2 Review results for related issues

2. Determine Issue Strategy
   IF existing_issue_found:
      2.1 Assess if work is directly related
      2.2 If subset of existing work → Create child issue
      2.3 If directly related → Use existing issue
   ELSE:
      2.4 Create new issue

3. Create/Update Issue
   3.1 Title: Clear, actionable description
   3.2 Body must include:
       - Problem Statement
       - Acceptance Criteria
       - Technical Approach (high-level)
       - Related Issues (if any)
   3.3 Labels: Apply relevant labels (${label_strategy})
   3.4 Assign to self

4. Link to Project/Milestone
   4.1 Check for related project: `${issue_tracker} project list`
   4.2 If exists → Link issue to project
   4.3 Check for related milestone
   4.4 If exists → Assign milestone

5. Record Issue Number
   5.1 Store issue number for commit messages
   5.2 Add issue link to working notes
```

### Output
- Issue created/updated with number
- Issue linked to project/milestone if applicable

---

## Process: FeaturePlanning
### Purpose
Create comprehensive plan for feature implementation

### Prerequisites
- CodebaseReview completed
- Issue created

### Steps
```
1. Requirements Analysis
   1.1 State understanding of requirements
   1.2 Identify ambiguities
   1.3 Ask clarification questions
   1.4 Wait for responses
   1.5 Document final requirements

2. Technical Design
   2.1 Based on CodebaseReview findings:
       - Identify integration points
       - List required new components
       - Note patterns to follow
   2.2 Create component diagram if complex
   2.3 Define interfaces/contracts

3. Risk Assessment
   3.1 Identify technical risks
   3.2 Note security considerations
   3.3 Performance implications
   3.4 Breaking change potential

4. Implementation Breakdown
   4.1 Decompose into atomic tasks
   4.2 Order by dependencies
   4.3 Estimate complexity per task
   4.4 Identify parallelizable work

5. Test Strategy
   5.1 Define test scenarios
   5.2 Identify edge cases
   5.3 Plan integration tests
   5.4 Note performance benchmarks

6. Plan Documentation
   6.1 Format as structured markdown
   6.2 Include all sections above
   6.3 Add success criteria

7. Seek Approval
   7.1 Present plan summary
   7.2 Ask: "Should this be tracked as a Project or Milestone?"
   7.3 Wait for approval/feedback

8. Record Plan
   IF project_needed:
      8.1 Create GitHub Project
      8.2 Add tasks as cards
      8.3 Set up automation
   ELIF milestone_needed:
      8.1 Create milestone
      8.2 Link related issues

   ALWAYS:
      8.4 Update issue with plan
      8.5 Link to project/milestone
```

### Output
- Approved implementation plan
- Project/Milestone created if needed
- Clear task breakdown

---

## Process: TestDrivenDevelopment
### Purpose
Implement code using red-green-refactor cycle with continuous integration

### Trigger
Selected as active_pattern for development

### Steps
```
1. Select Next Task
   1.1 From plan, identify next atomic task
   1.2 Confirm task is truly atomic
   1.3 Create task-specific branch if needed:
       `${version_control} checkout -b ${current_branch}-${task_id}`

2. Write Failing Test
   2.1 Create test file if needed
   2.2 Write test that describes desired behavior
   2.3 Test should fail for the right reason
   2.4 Document test purpose: "// Test: ${what_and_why}"
   2.5 Run test, confirm failure
   2.6 Commit the failing test:
       - Message: "test(${scope}): add failing test for ${behavior}"
       - This documents our intention before implementation

3. Minimal Implementation
   3.1 Write ONLY enough code to pass test
   3.2 Avoid premature optimization
   3.3 Run test, confirm passes
   3.4 Run ALL tests, confirm no regression

4. Commit Working Code
   4.1 Stage test and implementation together
   4.2 Execute: Process: CommitWork
       Message: "feat(${scope}): implement ${behavior}"
   4.3 IF commit_succeeds:
       - Continue to step 5
   4.4 ELSE handle_commit_failure:
       - Create or update issue for failure pattern
       - Fix issues identified by pre-commit
       - Document solution in issue
       - Retry commit until success
       - Ensure issue is linked to current work

5. Push Changes
   5.1 Push to remote: `${version_control} push`
   5.2 IF push_fails:
       - Execute: Process: PushFailureResolution
       - Document resolution in issue tracker
       - Retry push until success
   5.3 Verify CI/CD pipeline triggered
   5.4 Monitor for any CI/CD failures

6. Document Progress
   6.1 Execute: Process: IssueUpdate
       Context: "TDD Cycle completed for ${task}"
       Include:
       - Test written and what it validates
       - Implementation approach
       - Any pre-commit issues encountered
       - CI/CD status

7. Refactor (if needed)
   7.1 Improve code structure
   7.2 Extract common patterns
   7.3 Enhance readability
   7.4 Add implementation comments
   7.5 Run all tests after each change
   7.6 IF refactoring_done:
       Execute: Process: CommitWork
       Message: "refactor(${scope}): ${improvement_description}"
       Then: Push changes

8. Task Completion Check
   8.1 IF atomic_task_complete:
       - Update issue with task completion
       - Check for any open sub-issues
       - Close any resolved pre-commit issues
   8.2 ELSE:
       - Return to Step 1 for next test

9. Issue Hygiene
   9.1 Review all issues created during this task
   9.2 Ensure all are either:
       - Closed with resolution documented
       - Linked to parent issue for tracking
       - Assigned for follow-up if still open
   9.3 No orphaned issues allowed
```

### Output
- Tested, documented code
- All changes pushed to remote
- Updated issue tracking
- No orphaned issues
- Ready for next task

### Integration Points
- Links to: Process: CommitWork (handles pre-commit)
- Links to: Process: PushFailureResolution (handles push issues)
- Links to: Process: IssueUpdate (maintains tracking)

---

## Process: PushFailureResolution
### Purpose
Resolve issues preventing push to remote and ensure they're tracked

### Trigger
Push to remote repository fails

### Steps
```
1. Diagnose Push Failure
   1.1 Capture full error message
   1.2 Common patterns:
       - Authentication failure
       - Remote has diverged
       - Protected branch
       - Network issues
       - Hook rejections

2. Create/Update Tracking Issue
   2.1 Search for existing push failure issues
   2.2 If pattern exists, update it
   2.3 Otherwise create new issue:
       Title: "Push Failure: ${error_type}"
       Labels: ['infrastructure', 'blocking']
   2.4 Document:
       - Full error message (sanitized)
       - Context when it occurred
       - Branch and commits affected

3. Resolution by Type
   3.1 IF remote_diverged:
       - Fetch latest: `${version_control} fetch origin`
       - Rebase or merge based on project standards
       - Resolve any conflicts
       - Re-run all tests

   3.2 IF authentication_issue:
       - Verify credentials
       - Check SSH keys/tokens
       - Update auth method if needed

   3.3 IF protected_branch:
       - Verify correct branch
       - Create PR if needed
       - Or switch to feature branch

   3.4 IF hook_rejection:
       - Read hook output carefully
       - Fix identified issues
       - Document hook requirements

4. Retry Push
   4.1 Attempt push again
   4.2 If still fails, return to step 1
   4.3 If succeeds, continue to step 5

5. Document Resolution
   5.1 Update issue with:
       - Root cause analysis
       - Steps taken to resolve
       - Time spent on resolution
       - Preventive measures
   5.2 If issue can be automated:
       Execute: Process: RecurringProblemIdentification
   5.3 Close issue with resolution

6. Update Local Documentation
   6.1 If new pattern discovered:
       - Add to team knowledge base
       - Update troubleshooting guide
   6.2 Consider pre-push hook to prevent
```

### Output
- Changes successfully pushed
- Issue tracked and resolved
- Knowledge captured for future

---

## Process: CoverageDrivenDevelopment
### Purpose
Alternative to TDD, focusing on coverage metrics

### Trigger
Selected as active_pattern for development

### Steps
```
1. Analyze Coverage
   1.1 Run coverage tool
   1.2 Identify uncovered code paths
   1.3 Prioritize by risk/importance

2. Write Implementation
   2.1 Implement feature/fix
   2.2 Focus on main path first
   2.3 Document with comments

3. Measure Coverage
   3.1 Run coverage analysis
   3.2 Identify gaps

4. Write Tests for Gaps
   4.1 Target uncovered lines
   4.2 Test edge cases
   4.3 Verify coverage improves

5. Refactor if Needed
   5.1 Improve testability
   5.2 Simplify complex paths

6. Document and Commit
   6.1 Same as TDD steps 4-7
```

---

## Process: IssueUpdate
### Purpose
Record development progress and learnings

### Parameters
- Context: What phase/task
- Include: Specific information to record

### Steps
```
1. Prepare Content
   1.1 Gather all information to include
   1.2 Execute: Process: DataSanitization
       Input: All content to be posted
   1.3 Review sanitized output for completeness

2. Format Update
   2.1 Title: "Progress Update: ${context}"
   2.2 Sections:
       ### Work Completed
       - ${list_of_completed_items}

       ### Challenges Encountered
       - ${challenge}: ${description}
         - Attempted: ${solutions_tried}
         - Root Cause: ${analysis}

       ### Solution Implemented
       - ${final_solution}
       - Why it worked: ${explanation}

       ### Lessons Learned
       - ${lesson}: ${how_to_apply_future}

       ### Next Steps
       - ${upcoming_tasks}

3. Add Technical Details
   3.1 Include sanitized debug output
   3.2 Add code snippets if relevant
   3.3 Link to commits/branches

4. Post Update
   4.1 Post to issue: `${issue_tracker} issue comment ${issue_number}`
   4.2 Update labels if status changed
   4.3 Move project card if applicable
```

---

## Process: DataSanitization
### Purpose
Remove or mask sensitive information before posting to any public or semi-public location

### Trigger
- Before any IssueUpdate
- Before creating PRs or issues
- Before posting error messages or logs
- Before sharing debug output

### Input
Raw text that may contain sensitive information

### Steps
```
1. Determine Content Type
   1.1 Identify input format:
       - Plain text → use 'text' tools
       - JSON data → use 'json' tools
       - Log files → use 'structured_logs' tools
   1.2 Assess complexity level:
       - Single-line replacements → simple
       - Multi-line patterns → medium
       - Context-aware replacements → complex

2. Select Sanitization Tool
   2.1 Execute: Process: ToolSelection
       Parameters:
       - tool_category: ${content_type}
       - complexity: ${assessed_complexity}
   2.2 Verify tool availability
   2.3 Prepare tool-specific commands

3. Apply Sanitization Patterns
   3.1 For each pattern in ${sanitization_patterns}:
       IF pattern.complexity <= tool.complexity:
          Apply pattern using selected tool

   3.2 Tool-specific implementation:
       FOR sed (simple patterns):
           echo "${content}" | sed -E 's/${pattern.regex}/${pattern.replacement}/g'

       FOR awk (medium patterns):
           echo "${content}" | awk '{
               gsub(/${pattern.regex}/, "${pattern.replacement}")
               print
           }'

       FOR python (any complexity):
           python3 -c "
           import re, sys
           content = sys.stdin.read()
           # Apply all patterns
           for pattern in patterns:
               content = re.sub(pattern['regex'], pattern['replacement'], content)
           print(content)
           "

       FOR jq (JSON data):
           cat "${file}" | jq 'walk(if type == "string" then
               gsub("${pattern.regex}"; "${pattern.replacement}")
           else . end)'

4. Multi-pass Sanitization
   4.1 First pass: Credentials and keys
       - API keys, tokens, passwords
       - SSH keys, certificates
       - Database connection strings

   4.2 Second pass: PII
       - Email addresses
       - Names in common positions
       - Phone numbers, SSNs

   4.3 Third pass: System information
       - IP addresses
       - Usernames in paths
       - Hostnames

   4.4 Final pass: Context-specific
       - UUIDs/GUIDs
       - Temporary paths
       - Session IDs

5. Validate Sanitization
   5.1 Quick scan for missed patterns
   5.2 Check for partial exposures:
       - Key prefixes/suffixes
       - Encoded data (base64, hex)
   5.3 If unsure, apply generic sanitization:
       ${suspicious_string} → <redacted-possible-sensitive-data>

6. Handle Tool Failures
   6.1 If primary tool fails:
       - Log failure reason
       - Try next tool in preference list
       - If all fail, use manual replacement

   6.2 Fallback to manual process:
       - Flag for manual review
       - Provide pattern list for manual application
       - Mark output as "Requires manual sanitization"

7. Document Sanitization
   7.1 Add header to sanitized content:
       "# Note: This content has been sanitized for security
        # Tool used: ${tool_name}
        # Patterns applied: ${pattern_count}
        # Date: ${timestamp}"

   7.2 Keep sanitization log:
       - Patterns matched
       - Replacements made
       - Tool used
```

### Output
Sanitized text safe for public posting

### Tool-Specific Examples

#### Using sed (simple):
```bash
# Sanitize email addresses
echo "Contact: john.doe@example.com" | sed -E 's/[\w\.-]+@[\w\.-]+\.\w+/<email>/g'
# Output: Contact: <email>
```

#### Using awk (medium):
```bash
# Sanitize paths with usernames
echo "/home/johndoe/project/src" | awk '{
    gsub(/\/home\/[^\/]+\//, "/home/<username>/")
    gsub(/\/Users\/[^\/]+\//, "/Users/<username>/")
    print
}'
# Output: /home/<username>/project/src
```

#### Using python (complex):
```bash
# Multiple pattern sanitization
cat debug.log | python3 -c "
import re, sys
content = sys.stdin.read()
# Define patterns
patterns = [
    (r'Bearer\s+[\w\-\.]+', 'Bearer <token-REDACTED>'),
    (r'password[\"\']\s*:\s*[\"\''][^\"\']+[\"\'']', 'password: \"<password>\"'),
    (r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '<uuid>')
]
# Apply all patterns
for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
print(content)
"
```

#### Using jq (JSON):
```bash
# Sanitize JSON data
cat config.json | jq 'walk(if type == "string" then
    gsub("(?<key>api_key\"?\\s*:\\s*\"?)[^\"]+"; "\(.key)<api-key-REDACTED>") |
    gsub("[\\w\\.-]+@[\\w\\.-]+\\.\\w+"; "<email>")
else . end)'
```

---

## Process: ToolSelection
### Purpose
Select the most appropriate tool from configured options based on availability and requirements

### Parameters
- tool_category: Category of tools needed (text/json/structured_logs)
- complexity: Required complexity level (simple/medium/complex/any)

### Steps
```
1. Load Tool Configuration
   1.1 Read tool list for ${tool_category}
   1.2 Filter by complexity requirements
   1.3 Order by preference (list order)

2. Check Tool Availability
   2.1 For each tool in filtered list:
       IF tool.available == "check":
          Run: command -v ${tool.name} >/dev/null 2>&1
          IF exit_code == 0:
             Mark as available
       ELIF tool.available == "assume":
          Mark as available

   2.2 Build available tools list

3. Select Primary Tool
   3.1 Choose first available tool from list
   3.2 If no tools available:
       - Alert user
       - Suggest installing tools
       - Offer manual sanitization

4. Prepare Fallback Chain
   4.1 Create ordered list of alternatives
   4.2 Document fallback reasons
   4.3 Set complexity limits per tool

5. Return Tool Configuration
   5.1 Primary tool with command syntax
   5.2 Fallback tools in order
   5.3 Complexity limitations
   5.4 Special flags or options
```

### Output
- Selected tool configuration
- Fallback chain
- Usage instructions

---

## Process: CommitWork
### Purpose
Create atomic, well-documented commits

### Steps
```
1. Stage Changes
   1.1 Review changes: `${version_control} diff`
   1.2 Stage atomic changes: `${version_control} add ${files}`
   1.3 Verify staged: `${version_control} status`

2. Determine Commit Type
   2.1 Check if commit closes issue
   2.2 Identify commit type (feat/fix/refactor/docs/test)

3. Write Commit Message
   3.1 Prepare message content
   3.2 Execute: Process: DataSanitization
       Input: Commit message body
   3.3 Format: "${type}(${scope}): ${description}"

   IF closes_issue:
      Add: "Fixes #${issue_number}"

   Body:
   - What changed (sanitized)
   - Why it changed
   - Side effects

4. Run Pre-commit Hooks
   4.1 Commit with hooks: `${version_control} commit`
   4.2 IF hooks_fail:
       - Record failure type and pattern
       - Execute: Process: RecurringProblemIdentification
           Context: Hook failure details
       - Fix immediate issues
       - Document solution in issue
       - Retry commit

5. Push Changes
   5.1 Push to remote: `${version_control} push`
   5.2 IF push_fails:
       - Diagnose issue
       - Execute: Process: RecurringProblemIdentification
           Context: Push failure pattern
       - Resolve conflicts if needed
       - Document in issue tracker
       - Retry push

6. Verify Success
   6.1 Check remote repository
   6.2 Ensure CI/CD triggered
```

---

## Process: CodeQualityReview
### Purpose
Ensure code meets quality standards

### Steps
```
1. Automated Checks
   1.1 Run linter
   1.2 Run formatter
   1.3 Run type checker (if applicable)
   1.4 Check test coverage

2. Manual Review
   2.1 Verify follows identified patterns
   2.2 Check error handling
   2.3 Review documentation completeness
   2.4 Assess code clarity

3. Security Review
   3.1 No hardcoded secrets
   3.2 Input validation present
   3.3 No SQL injection risks
   3.4 Dependencies up to date

4. Performance Check
   4.1 No obvious inefficiencies
   4.2 Appropriate data structures
   4.3 Caching where beneficial

5. Document Findings
   5.1 Create review checklist
   5.2 Note any concerns
   5.3 Suggest improvements
```

---

## Process: WorkspaceCleanup
### Purpose
Prepare workspace for merge and next task

### Steps
```
1. Ensure All Work Committed
   1.1 Check status: `${version_control} status`
   1.2 Commit any remaining changes
   1.3 Push all commits

2. Update Documentation
   2.1 Update README if needed
   2.2 Update API docs if applicable
   2.3 Add/update examples

3. Final Issue Update
   3.1 Summary of all work completed
   3.2 Link to all related commits
   3.3 Confirm acceptance criteria met

4. Prepare for Review
   4.1 Self-review all changes
   4.2 Add review checklist to PR/MR
   4.3 Tag relevant reviewers
```

---

## Process: SubmitWork
### Purpose
Create pull/merge request for review

### Steps
```
1. Create Pull Request
   1.1 Prepare all content for PR
   1.2 Execute: Process: DataSanitization
       Input: PR title and body content
   1.3 Title: Clear description of changes
   1.4 Body template:
       ## Summary
       ${what_changed_and_why}

       ## Related Issue
       Fixes #${issue_number}

       ## Changes Made
       - ${change_1}
       - ${change_2}

       ## Testing
       - ${how_tested}
       - Coverage: ${coverage_percent}%

       ## Checklist
       - [ ] Tests pass
       - [ ] Documentation updated
       - [ ] No security issues
       - [ ] Follows patterns

2. Configure PR
   2.1 Set base branch correctly
   2.2 Assign reviewers
   2.3 Add labels
   2.4 Link to project/milestone

3. Monitor and Respond
   3.1 Watch for CI/CD results
   3.2 Respond to review feedback
   3.3 Make requested changes
   3.4 Update issue with status
```

# Development Patterns

## Pattern: TestDrivenDevelopment
See Process: TestDrivenDevelopment

## Pattern: CoverageDrivenDevelopment
See Process: CoverageDrivenDevelopment

## Pattern: BehaviorDrivenDevelopment
```
1. Write Scenario
   Given: ${initial_context}
   When: ${action_taken}
   Then: ${expected_outcome}

2. Implement Steps
3. Make Scenario Pass
4. Refactor
```

# Pre-commit Hook Management

## Hook Problem Tracking
The system automatically identifies recurring problems that could be solved by pre-commit hooks by tracking:
- Repeated CI/CD failures
- Common code review feedback
- Frequent manual fixes
- Pre-commit hook failures

## Hook Resolution Flow
```
Problem Detected → RecurringProblemIdentification
                  ↓
                  Analyze if automatable
                  ↓
        ┌─────────┴─────────┐
        ↓                   ↓
Find Existing Hook    Create Custom Hook
        ↓                   ↓
        └─────────┬─────────┘
                  ↓
            Test & Apply
                  ↓
         If custom & valuable
                  ↓
      PreCommitHookContribution
```

# Quick Reference

## Process Chains
- New Feature: CodebaseReview → FeaturePlanning → TDD → QualityReview → Submit
- Bug Fix: CodebaseReview → BugAnalysis → TDD → RegressionTest → Submit
- Refactor: CodebaseReview → RefactorPlanning → SafetyNet → Refactor → Submit
- Hook Creation: RecurringProblemIdentification → PreCommitHookResolution → PreCommitHookContribution

## Pre-commit Integration Points
- Repository Setup: WorkspaceSetup → PreCommitConfiguration
- Problem Detection: CommitWork failures → RecurringProblemIdentification
- Hook Development: Create → Test → Contribute to aRustyDev/pre-commit-hooks

## Issue Updates Required At
- After each TDD cycle
- When encountering challenges
- When finding solutions
- When identifying recurring problems
- At milestone completion
- Before submitting PR
- After creating new pre-commit hooks

## Label Strategy
- `needs:tests` - Missing test coverage
- `needs:review` - Ready for code review
- `needs:docs` - Documentation needed
- `needs:hook` - Could benefit from pre-commit hook
- `type:bug` - Bug fix
- `type:feature` - New feature
- `type:refactor` - Code improvement
- `type:tooling` - Development tool improvement
- `priority:high` - Urgent
- `blocked` - Waiting on external factor
- `help-wanted` - Need assistance
- `recurring-issue` - Pattern identified for automation
