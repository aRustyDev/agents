---
name: Test-Driven Development Pattern
module_type: pattern
scope: persistent
priority: critical
triggers: ["TDD", "test-driven", "red-green-refactor", "test first"]
dependencies: ["processes/testing/tdd.md"]
conflicts: 
  - "patterns/development/cdd-pattern.md"
  - "patterns/development/bdd-pattern.md"
version: 1.0.0
---

# Test-Driven Development Pattern

## Purpose
This pattern defines the Test-Driven Development methodology as the default approach for all development work. It enforces quality through a disciplined cycle of writing tests before code.

## Pattern Overview

```
┌─────────────┐
│   Red       │ Write a failing test
│  (Failing)  │ that defines desired behavior
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Green     │ Write minimal code
│  (Passing)  │ to make the test pass
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Refactor   │ Improve code structure
│ (Improving) │ while keeping tests green
└─────┬───────┘
      │
      ▼
   Commit & Push
      │
      └──────── Return to Red
```

## Core Principles

### 1. Test First
- Never write production code without a failing test
- Tests document the intended behavior
- Tests drive the design

### 2. Minimal Implementation
- Write only enough code to pass the test
- Resist adding untested functionality
- YAGNI (You Aren't Gonna Need It)

### 3. Continuous Refactoring
- Clean code with confidence
- Tests provide safety net
- Improve design iteratively

### 4. Atomic Commits
- Each cycle results in a commit
- Commits include both test and implementation
- Push frequently to share progress

## Implementation Rules

### Red Phase Rules
1. Write one test at a time
2. Test must fail for the right reason
3. Test must be clear about intent
4. Commit the failing test

### Green Phase Rules
1. Make the test pass quickly
2. Don't worry about perfection
3. All tests must remain green
4. Focus on working code

### Refactor Phase Rules
1. Only refactor with green tests
2. Run tests after each change
3. Improve without changing behavior
4. Keep refactoring scope small

## When to Apply
- All new feature development
- Bug fixes (test reproduces bug first)
- Refactoring (tests ensure behavior preserved)
- Spike solutions (explore with tests)

## Example: Adding Email Validation

### Step 1: Red - Write Failing Test
```python
def test_email_validation_accepts_valid_emails():
    # Test: Should accept standard email formats
    assert is_valid_email("user@example.com") == True
    assert is_valid_email("user.name+tag@example.co.uk") == True
```
Commit: `test(validation): add failing test for email validation`

### Step 2: Green - Minimal Implementation
```python
def is_valid_email(email):
    return "@" in email and "." in email.split("@")[1]
```
Commit: `feat(validation): implement basic email validation`

### Step 3: Refactor - Improve Implementation
```python
import re

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
```
Commit: `refactor(validation): improve email regex pattern`

## Anti-Patterns to Avoid

### Writing Implementation First
❌ Writing code then adding tests later  
✅ Always write the test first - it defines the interface

### Giant Test Steps
❌ Writing tests for entire features at once  
✅ One small test for one small behavior

### Skipping the Refactor Step
❌ Moving to next feature immediately after green  
✅ Always consider: "Can this be clearer?"

### Delayed Commits
❌ Waiting until "done" to commit  
✅ Commit after every red-green-refactor cycle

### Working in Isolation
❌ Not pushing until feature complete  
✅ Push frequently for continuous integration

## Benefits
- **Confidence**: Comprehensive test coverage
- **Design**: Tests drive better design
- **Documentation**: Tests document behavior
- **Refactoring**: Safe to improve code
- **Debugging**: Failures pinpoint issues

## Integration with Processes
This pattern is implemented through:
- Process: `processes/testing/tdd.md` - Detailed implementation steps
- Workflows: Referenced in all development workflows
- Enforcement: Pre-commit hooks and CI/CD

## Success Metrics
- 100% of new code has tests written first
- All tests pass before commit
- Commits show test-first approach
- Coverage increases over time
- Refactoring happens regularly

## Troubleshooting

### Tests Won't Fail Properly
- Ensure test actually tests new behavior
- Check test isn't accidentally passing
- Verify assertions are correct

### Can't Write Minimal Code
- Break down the test further
- Focus on making just this test pass
- Ignore edge cases until tested

### Too Many Tests Failing
- Check for unintended side effects
- Review recent changes
- Consider rolling back and smaller steps

---
*TDD is not just a testing strategy, it's a design methodology that results in better, more maintainable code.*