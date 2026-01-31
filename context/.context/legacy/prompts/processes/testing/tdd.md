---
name: Test-Driven Development Process
module_type: process
scope: persistent
priority: critical
triggers: ["test", "TDD", "red-green-refactor", "test first", "failing test"]
dependencies: 
  - "processes/version-control/commit-standards.md"
  - "processes/issue-tracking/issue-management.md"
  - "processes/tooling/push-failure-resolution.md"
conflicts: 
  - "processes/testing/cdd.md"
  - "processes/testing/bdd.md"
version: 1.0.0
---

# Test-Driven Development Process

## Purpose
Implement code using red-green-refactor cycle with continuous integration, ensuring all code is tested, commits are atomic, and changes are continuously pushed to remote.

## Trigger
Selected as active_pattern for development or when implementing any new functionality.

## Process Flow

### 1. Select Next Task
**Goal**: Identify truly atomic unit of work

Steps:
1. From plan, identify next atomic task
2. Confirm task is truly atomic by asking:
   - Can this be broken down further?
   - Does this represent a single behavior?
   - Can I write one focused test for this?
3. Create task-specific branch if needed:
   ```bash
   ${version_control} checkout -b ${current_branch}-${task_id}
   ```

**Integration Points**:
- References task breakdown from planning phase
- May trigger issue update if task needs decomposition

### 2. Write Failing Test
**Goal**: Document intended behavior before implementation

Steps:
1. Create test file if needed
2. Write test that describes desired behavior
3. Test should fail for the right reason
4. Document test purpose: `// Test: ${what_and_why}`
5. Run test, confirm failure
6. **COMMIT the failing test**:
   - Message: `test(${scope}): add failing test for ${behavior}`
   - This documents our intention before implementation
   - Creates checkpoint for rollback if needed

**Critical**: The failing test MUST be committed to document intent

### 3. Minimal Implementation
**Goal**: Pass test with simplest possible code

Steps:
1. Write ONLY enough code to pass test
2. Avoid premature optimization
3. Run test, confirm passes
4. Run ALL tests, confirm no regression

**Principles**:
- YAGNI (You Aren't Gonna Need It)
- Make it work, then make it right
- Resist urge to add untested functionality

### 4. Commit Working Code
**Goal**: Create atomic commit with test and implementation

Steps:
1. Stage test and implementation together
2. Execute commit with conventional format:
   ```
   feat(${scope}): implement ${behavior}
   
   - Add implementation for ${specific_functionality}
   - Include test coverage
   - No regression in existing tests
   ```
3. **IF commit succeeds**:
   - Continue to step 5
4. **ELSE handle commit failure**:
   - Create or update issue for failure pattern
   - Fix issues identified by pre-commit
   - Document solution in issue
   - Retry commit until success
   - Ensure issue is linked to current work

**Integration**: Links to Process: CommitWork for pre-commit handling

### 5. Push Changes
**Goal**: Ensure changes are in remote repository

Steps:
1. Push to remote: `${version_control} push`
2. **IF push fails**:
   - Execute: Process: PushFailureResolution
   - Document resolution in issue tracker
   - Retry push until success
3. Verify CI/CD pipeline triggered
4. Monitor for any CI/CD failures
5. **IF CI/CD fails**:
   - Create issue for failure
   - Fix locally
   - Amend commit if needed
   - Push fixes

**Critical**: Changes MUST be pushed after each TDD cycle

### 6. Document Progress
**Goal**: Maintain comprehensive issue tracking

Execute: Process: IssueUpdate with:
- Context: "TDD Cycle completed for ${task}"
- Include:
  - Test written and what it validates
  - Implementation approach
  - Any pre-commit issues encountered
  - CI/CD status
  - Link to commit

### 7. Refactor (if needed)
**Goal**: Improve code structure without changing behavior

Steps:
1. Improve code structure
2. Extract common patterns
3. Enhance readability
4. Add implementation comments
5. **Run all tests after each change**
6. If refactoring done:
   - Commit: `refactor(${scope}): ${improvement_description}`
   - Push changes immediately

**Rule**: Refactoring ONLY with passing tests

### 8. Task Completion Check

Evaluate:
1. **IF atomic task complete**:
   - Update issue with task completion
   - Check for any open sub-issues
   - Close any resolved pre-commit issues
2. **ELSE**:
   - Return to Step 1 for next test

### 9. Issue Hygiene
**Goal**: No orphaned issues

Review all issues created during this task:
1. Ensure all are either:
   - Closed with resolution documented
   - Linked to parent issue for tracking
   - Assigned for follow-up if still open
2. No orphaned issues allowed
3. Update parent issue with summary

## Output
- Tested, documented code
- All changes pushed to remote
- Updated issue tracking
- No orphaned issues
- Ready for next task

## Integration Points
- Links to: Process: CommitWork (handles pre-commit)
- Links to: Process: PushFailureResolution (handles push issues)
- Links to: Process: IssueUpdate (maintains tracking)
- Triggers: CI/CD pipeline on each push

## Common Patterns

### Multiple Related Tests
When task requires multiple tests:
1. Write first failing test
2. Implement
3. Commit
4. Write second failing test
5. Implement
6. Commit
7. Push after each commit

### Test Discovery
If implementation reveals need for more tests:
1. Note in issue
2. Create failing test
3. Follow full cycle
4. Update original task issue

### Regression Found
If existing test fails:
1. Stop current work
2. Create bug issue
3. Fix regression first
4. Link fix to both issues
5. Resume original work

## Anti-Patterns to Avoid
- Writing multiple tests before any implementation
- Implementing features without tests
- Batching commits instead of atomic commits
- Delaying pushes until "ready"
- Skipping documentation in issues

## Enforcement
- Pre-commit hooks enforce test presence
- CI/CD enforces all tests pass
- Issue tracking enforces documentation
- Code review enforces TDD evidence

---
*TDD is the default development pattern ensuring quality through continuous testing and integration.*