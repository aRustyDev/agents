---

  Test Coverage Implementation Task - Strategic Path to 48-50% Coverage

  Initial Setup and Context

  Please begin by reading these critical sources of information in order:
  1. COVERAGE_REQUIREMENTS - Read the "TEST COVERAGE - Organization Requirements"
  2. RULES - Read the "FORBIDDEN_PATHS" section

  After reading these files, confirm your understanding of:
  - Current coverage statistics
  - Coverage Target percentage
  - The critical formula: Overall Impact = (Module Statements ÷ Total Statements) × Coverage Gain

  Critical Rules You MUST Follow

  🚫 FORBIDDEN ACTIONS - NEVER DO THESE:
  1. NEVER modify ANY file listed in the FORBIDDEN_PATHS section of RULES
  2. NEVER add # pragma: no cover comments anywhere
  3. NEVER mock Python standard library (json, csv, open, etc.) - use real operations with tempfile
  4. NEVER skip the RED phase of TDD - Every test MUST fail first
  5. NEVER test implementation details - Test behavior and outcomes only
  6. NEVER create new mock patterns - Use existing factories in tests/mocks/
  7. NEVER try to fix failing tests by changing source code - Work around issues in tests
  8. NEVER waste time on small modules (<300 statements) - Focus on Azure, Entra ID, M365 only


  Special Instructions

  1. in order to add `# pragma: no cover` comments anywhere, you must ask for permission from the team lead, and the target MUST meet the EXCLUDABLE_REQUIREMENTS definition in COVERAGE_REQUIREMENTS

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

  Day 1: Fix Azure Module Infrastructure (MANDATORY FIRST STEP)

  Morning Tasks:
  1. Run pytest tests/test_azure_dumper.py -xvs and document each of the 7 failures
  2. Think step by step about why each test is failing
  3. Identify patterns in failures (missing methods, config issues, etc.)

  Afternoon Tasks:
  1. Create a create_azure_dumper_for_testing() helper function that bypasses complex initialization
  2. Fix each failing test one by one using the helper function
  3. Ensure all 11 Azure tests pass before proceeding

  Critical: If Azure tests aren't fixed, the entire plan fails. Think carefully about each fix.

  Day 2: Azure Module Coverage Blitz

  Target simple Azure methods that use delegation pattern:
  - dump_storage_accounts(), dump_network_security_groups(), dump_virtual_machines(), etc.

  For each method:
  1. Think about what the method does
  2. Write a failing test using the delegation pattern
  3. Make it pass using the mock factory
  4. Verify coverage increased

  Day 3: High-Impact Module Combination

  Morning: Entra ID simple methods
  Afternoon: M365 error paths

  Think strategically about which methods give the most coverage for the least complexity.

  Day 4: Final Push to 48-50%

  Based on Days 1-3 progress, choose the most efficient path:
  - Option A: More Azure methods if going well
  - Option B: MDE advanced hunting if Azure is difficult
  - Option C: Utils error paths for guaranteed small gains

  Progress Tracking Requirements

  After each day, provide:
  1. Starting coverage percentage
  2. Ending coverage percentage
  3. Number of statements added
  4. Number of tests written
  5. Any blockers encountered
  6. Next day's specific targets

  Special Instructions for Complex Scenarios

  When you encounter Azure initialization complexity:
  - Think step by step about how to bypass it
  - Use object.new() to create instances without calling init
  - Set required attributes manually
  - Use the AzureSDKMockFactory for client mocks

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
