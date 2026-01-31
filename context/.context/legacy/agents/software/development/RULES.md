# Software Development Team Rules

These rules govern all development activities within the software development team. All team members must adhere to these standards without exception.

## Code Requirements

### Documentation Standards
- All code must have 2 kinds of comments: inline and block comments.
  - Inline comments are for explaining specific lines of code.
  - Block comments are for explaining larger sections of code.
  - Block comments should include DEVNOTES, which describe the functionality of the code from the developer's perspective, so that test-engineers and technical writers can understand the code.
  - Block comments should include BUSINESSCASE, which describe the functionality of the code from the business logic perspective, so that test-engineers and technical writers can understand the code.
  - Code that will be Public Facing should be tagged with the inline comment `PUBLICFACING`.

### Testing Requirements
- All code should be tested following Test-Driven Development (TDD) principles.
  - Functions defined in the code should be 100% covered.
  - Branches defined in the code should be 60% covered.
  - Statements defined in the code should be 60% covered.
  - Code that you believe qualifies as untestable should have an inline comment added with the tag `UNTESTABLE`.
  - Code that you believe qualifies as needing a mock should have an inline comment added with the tag `MOCKTHIS`.

### Version Control Standards
- All code should be branch separated.
  - When starting new work, create a branch following BRANCH_PATTERN.
  - Then checkout the branch.
  - Commits must be atomic (one logical change per commit).
  - Follow conventional commit standards for all commit messages.
  - Include detailed commit body with learning notes and challenges.

### Function Development Process
Creating a new function should follow the following steps:
  1. Define the function signature.
  2. Write a static function body, that includes the DEVNOTES and BUSINESSCASE as block comments, and statically returns what its signature says it will.
  3. Write unit tests for the function that covers the simplest possible implementation beyond a statically returned value, which should cause the test to fail.
  4. Iteratively write the smallest and simplest implementation for the function, until it succeeds.
  5. Git Add the changes to the branch, commit the changes with a descriptive incremental message, aligning with conventional-commit standards, the header should include the minimal changes made, and including a body describing challenges discovered since last commit.
  6. Update the unit test for the function to cover more business case logic, until it fails.
  7. If all business cases are covered by the unit tests, then move on to the next step, otherwise return to step 4.
  8. Update the function until it passes all unit tests.

### Code Maintenance
- Regularly review and try to simplify the codebase.
  - Deduplicate code wherever possible.
  - Remove dead code that is not marked as `NOTDEAD`.
  - Remove unnecessary specifications.
  - Look for opportunities to improve code readability and maintainability.
  - Refactor code to adhere to SOLID principles.
  - Look for opportunities to improve code performance.
  - Refactor code to adhere to the Single Responsibility Principle.

## Team Interaction Protocols

### Communication Standards
1. **Clarity First**: All technical communication must be clear and unambiguous.
2. **Document Decisions**: Important decisions must be recorded in TEAM_MEMORY.md.
3. **Proactive Updates**: Blockers and risks must be communicated immediately.
4. **Knowledge Sharing**: Learnings and insights must be shared with the team.
5. **Respectful Collaboration**: All interactions must be professional and constructive.

### Code Review Process
1. **Submitter Responsibilities**:
   - Ensure all tests pass before submitting.
   - Self-review code for obvious issues.
   - Provide context in pull request description.
   - Respond to feedback promptly.

2. **Reviewer Responsibilities**:
   - Review within 4 hours of submission.
   - Provide constructive, actionable feedback.
   - Focus on correctness, then quality.
   - Explain the reasoning behind suggestions.

### Task Management
1. **Task Assignment**:
   - Engineer assigns tasks to Agent.
   - Tasks must have clear requirements.
   - Acceptance criteria must be specific.
   - Timeline expectations must be set.

2. **Progress Tracking**:
   - Update task status regularly.
   - Communicate blockers immediately.
   - Document progress in commits.
   - Update CHANGELOG.md with changes.

### Shared Memory Updates
1. **TEAM_MEMORY.md Updates**:
   - Update after significant decisions.
   - Record architectural changes.
   - Document lessons learned.
   - Maintain current sprint status.

2. **Documentation Maintenance**:
   - Keep all documentation current.
   - Update when implementation changes.
   - Remove outdated information.
   - Version significant changes.

## Commit Message Standards

### Format
```
type(scope): brief description

[Body - Required for all commits]
DEVNOTES:
- Technical implementation details
- Challenges faced and solutions
- Design decisions made

LESSONS LEARNED:
- Key insights gained
- Mistakes to avoid
- Better approaches discovered

REFERENCES:
- Documentation consulted
- Stack Overflow links
- Blog posts or tutorials
```

### Types
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Test additions/changes
- chore: Build/tool changes

### Scope
Use module name, component name, or feature area.

## Quality Gates

### Pre-Commit Checklist
- [ ] All tests pass
- [ ] Coverage requirements met
- [ ] Linter reports no errors
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit message follows format

### Pre-Merge Requirements
- [ ] Code review approved
- [ ] All quality gates passed
- [ ] No merge conflicts
- [ ] CI/CD pipeline green
- [ ] QA sign-off received

## Branch Naming Conventions

### BRANCH_PATTERN
```
<type>/<ticket-number>-<brief-description>
```

### Examples
- feature/PROJ-123-user-authentication
- fix/PROJ-456-login-error
- refactor/PROJ-789-optimize-queries
- docs/PROJ-321-api-documentation

## Cross-Agent Communication

### Escalation Path
1. Agent → Engineer (technical guidance)
2. Engineer → Architect (design decisions)
3. Engineer → Manager (blockers/risks)
4. QA → Manager (quality concerns)
5. Manager → External teams (dependencies)

### Meeting Protocols
1. **Daily Sync**: Brief status updates
2. **Technical Reviews**: Deep dives on complex topics
3. **Retrospectives**: Team improvement discussions
4. **Planning Sessions**: Sprint/iteration planning

## Exception Handling

### When Rules Can Be Bypassed
1. **Emergency Fixes**: Document in commit why rules were bypassed
2. **Legacy Code**: Apply rules to modified portions only
3. **Third-Party Code**: Exclude from coverage requirements
4. **Prototypes**: Mark clearly as non-production code

### Documentation of Exceptions
All exceptions must be:
- Documented in TEAM_MEMORY.md
- Justified with clear reasoning
- Time-boxed with remediation plan
- Approved by Manager or Architect
