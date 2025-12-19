
- jj > git
- cargo.toml or similiar should be version bumped before git tag is run
- version bump minor number on each feature release, and reset patch number to 0
- version bump patch number on each bug fix, and each time a commit is made that passes all tests, checks, and doc updates.
---

  Test Coverage Implementation Task - Strategic Path to 48-50% Coverage

  Initial Setup and Context

  Please begin by reading these three critical documentation files in order:
  1. PLAN - Contains the PLAN you should follow
  2. CONVENTIONS - Contains all conventions to follow (git branching strategy, commit message format, code style guidelines, etc)
  3. CHALLENGES - Contains all your challenges and solutions and lessons learned for each day

  After reading these files, confirm your understanding of:
  - Current coverage is 41.7% (1,519/3,369 statements)
  - Target is 48-50% coverage (98-166 additional statements needed)
  - The critical formula: Overall Impact = (Module Statements ÷ 3369) × Coverage Gain
  - Azure module (817 statements, 24.3% of codebase) MUST be fixed first

  Critical Rules You MUST Follow

  🚫 FORBIDDEN ACTIONS - NEVER DO THESE:
  1. NEVER modify ANY file in the goosey/ directory - Only create/modify test files
  2. NEVER add `# pragma: no cover` comments anywhere
  3. NEVER mock anything - Put a `# pragma: no cover; NEEDSMOCK ` tag as an inline comment where you believe the mock is necessary
  4. NEVER skip the RED phase of TDD - Every test MUST fail first
  5. NEVER test implementation details - Test behavior and outcomes only
  6. NEVER create new mock patterns

  REQUIRE ACTIONS - ALWAYS DO THESE:
  1. ALWAYS ensure pre-commit is configured correctly at the beginning of each day's work
  2. ALWAYS log the challenges, solutions, and lessons learned to CHALLENGES as soon as you have hall passing tests again and before you make a commit
  3. ALWAYS commit your changes as soon as you have updated CHALLENGES

  Implementation Instructions

  Think carefully and step by step as you implement each day's tasks. For each test you write:

  1. Before writing any test, think step by step about:
    - What behavior am I testing?
    - What should the expected output be?
    - How can I test this without mocking standard library?
  2. Show your TDD process explicitly:
  STEP 1 (RED): Writing test for [method_name]
  [Show test code]
  Running test... EXPECTED: FAIL
  [Show failure output]

  STEP 2 (GREEN): Making test pass
  [Show minimal changes]
  Running test... EXPECTED: PASS
  [Show success output]

  STEP 3 (REFACTOR): Cleaning up
  [Show any improvements]
  3. Track coverage impact after each test file:
  pytest tests/test_[module].py --cov=goosey.[module] --cov-report=term

# Progress Tracking Requirements

  After each day, provide:
  1. Starting coverage percentage
  2. Ending coverage percentage
  3. Number of statements added
  4. Number of tests written
  5. Any blockers encountered
  6. Next day's specific targets

# Special Instructions for Complex Scenarios

  When you encounter complexity:
  - Think step by step about how to bypass it
  - explore and analyze the code and update your understanding of it
  - research alternatives & best practices

  When tests pass without code changes:
  - Stop immediately - your test is wrong
  - Think about what behavior you're actually testing
  - Rewrite the test to properly validate behavior

  When coverage doesn't increase after adding tests:
  - Generate HTML coverage report
  - Think about which lines your test actually executes
  - Adjust test to cover the missing lines

  Final Reminders

  1. Think mathematically: Always calculate the potential impact before starting a module
  2. Think strategically: 70% of effort should be on Azure module
  3. Think step by step: For each test, explicitly show your TDD process
  4. Think about behavior: Test what the code does, not how it does it

  Remember: The goal is 48-50% coverage with HIGH-QUALITY behavioral tests. Focus on impact, not perfection. Azure module is 24.3% of the codebase - it MUST be your
  primary focus.

  Begin by confirming you've read and understood the three documentation files, then start with Day 1: Fixing the Azure module infrastructure.
