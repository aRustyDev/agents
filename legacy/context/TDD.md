
  1. Import Errors (3 failures):
    - ModuleNotFoundError: No module named 'honk' - trying to patch non-existent modules
    - Incorrect import paths like from utils import findkeys instead of from goosey.utils import findkeys
  2. Function Signature Mismatches (5 failures):
    - get_nextlink() called with wrong parameter order: actual signature is (url, outfile, session, logger, auth) but test calls it with (session, url, outfile, endpoint)
    - helper_single_object() expects params tuple but test passes individual arguments
    - parse_file() missing required parameters fields and result_dir
  3. Authentication/Parameter Issues (2 failures):
    - helper_single_object() failing due to missing token_type and access_token in auth structure
    - Functions expecting proper auth tokens but getting incomplete mock data
  4. Data Type Mismatches (2 failures):
    - save_state() function expecting datetime object but getting dictionary
    - write_auth() function signature mismatch with test expectations
  5. Over-Mocking Issues (multiple):
    - Tests are mocking too much, losing track of actual function behavior
    - Mocks don't match real function signatures and requirements

---

```Markdown

# Test Coverage Implementation Instructions for Goosey Project

  ## Overview
  You are tasked with improving test coverage for the "goosey" Python project from the current 30.3% to 45%. All planning has been completed and documented in three key files that you MUST read and
   follow:

  1. **CLAUDE.md** - Contains the comprehensive review, current coverage status, and critical authorization requirements
  2. **PLAN.md** - Contains the detailed step-by-step implementation plan with code examples
  3. **TODO.md** - Contains the prioritized task list with specific coverage targets

  ## CRITICAL: Start By Reading These Files
  ```bash
  # Read these files IN THIS ORDER before doing anything else:
  cat CLAUDE.md    # Read the "TEST COVERAGE - Comprehensive Review and Plan to 45%" section
  cat PLAN.md      # Read the entire implementation plan
  cat TODO.md      # Read the task list and authorization requirements

  Your Primary Objectives

  1. Achieve 45% Test Coverage (Currently at 30.3%)

  - Need to add 376 additional lines of covered code
  - Focus on HIGH-PRIORITY untested areas identified in the plan
  - Follow the 4-phase approach documented in PLAN.md

  2. Follow Test-Driven Development (TDD) Strictly

  For EVERY test you write:
  1. RED: Write a failing test FIRST
  pytest tests/test_new.py::test_feature -xvs  # MUST FAIL
  2. GREEN: Write MINIMAL code to make it pass
  pytest tests/test_new.py::test_feature -xvs  # MUST PASS
  3. REFACTOR: Clean up while keeping tests passing

  3. Use Existing Infrastructure

  - MUST USE the mock factories in tests/mocks/ directory:
    - M365SDKMockFactory (gold standard)
    - AzureSDKMockFactory (enhanced with M365 patterns)
    - HonkMockFactory (orchestration standard)
  - FOLLOW patterns from tests/test_m365_datadumper.py (31/31 tests passing)
  - DO NOT create new mocking patterns

  Phase-by-Phase Implementation

  Phase 1: Utils Async Functions (HIGHEST PRIORITY)

  Target: Add 120 lines coverage to utils.py (39.8% → 55%)

  Create tests/test_utils_async.py:
  # Focus on these critical untested functions:
  # - get_nextlink() (lines 276-328) - pagination, rate limiting
  # - run_kql_query() (lines 330-419) - KQL execution
  # - helper_single_object() (lines 486-568) - API retrieval

  # Use M365 pagination patterns as reference:
  grep -n "@odata.nextLink" tests/test_m365_datadumper.py

  Phase 2: Honk Orchestration

  Target: Add 80 lines coverage to honk.py (50.5% → 65%)

  Enhance tests/test_honk.py:
  - Test parse_config() with various configurations
  - Use existing HonkMockFactory from tests/mocks/honk_mocks.py
  - Test multi-service orchestration and error aggregation

  Phase 3: Dumper Behavioral Tests

  Target: Add 150 lines coverage across dumpers

  Priority order:
  1. Azure (4.3% → 15%): Test PCAP download, multi-subscription
  2. EntraID (10% → 20%): Test sign-in logs, pagination
  3. MDE (14.9% → 25%): Test KQL queries, state management

  Phase 4: Integration Tests

  Target: Add 50 lines coverage with end-to-end tests

  Create tests/integration/ directory for workflow testing.

  CRITICAL RULES - MUST FOLLOW

  ⚠️ AUTHORIZATION REQUIRED

  YOU MUST GET EXPLICIT AUTHORIZATION BEFORE:
  1. Making ANY changes to files in the goosey/ directory
  2. Adding # pragma: no cover comments anywhere
  3. Modifying .coveragerc or pyproject.toml
  4. Adding any coverage exclusion decorators

  YOU CAN DO WITHOUT AUTHORIZATION:
  - Create/modify ANY files in tests/ directory
  - Create new test files
  - Update documentation (*.md files)

  ❌ What NOT to Test (IMPORTANT)

  DO NOT write tests for:
  - Print statements or logging calls
  - if __name__ == "__main__" blocks
  - Interactive prompts (getpass, input)
  - Simple getters/setters
  - OS-specific code or external tool calls

  These are already excluded in .coveragerc - check the file to see current exclusions.

  ❌ Testing Anti-Patterns to AVOID

  Based on the review in CLAUDE.md, avoid these mistakes:
  1. DON'T mock Python standard library (json, csv, open)
    - Use temp files instead
  2. DON'T test implementation details
    - Test behavior, not how code works internally
  3. DON'T verify mock call counts
    - Test actual outcomes instead
  4. DON'T skip async tests
    - Use AsyncMock and follow M365 patterns

  Helpful Commands and Debugging

  Check Current Coverage

  # Before starting work
  pytest --cov=goosey --cov-report=term --cov-report=html

  # Check specific module coverage
  pytest tests/test_utils.py --cov=goosey.utils --cov-report=term

  Find Patterns in Existing Tests

  # Find async test patterns
  grep -n "pytest.mark.asyncio" tests/test_m365_datadumper.py

  # Find mock factory usage
  grep -r "MockFactory" tests/mocks/

  # Find pagination examples
  grep -r "nextLink" tests/

  Run Tests with Debugging

  # See print statements
  pytest -s tests/test_file.py::test_name

  # Stop on first failure
  pytest -x tests/

  # Verbose output
  pytest -vvv tests/test_file.py

  Expected Deliverables

  1. New test files created:
    - tests/test_utils_async.py (Phase 1)
    - tests/integration/test_*.py files (Phase 4)
  2. Enhanced test files:
    - tests/test_honk.py (Phase 2)
    - tests/test_azure_dumper.py (Phase 3)
    - tests/test_entra_id_datadumper.py (Phase 3)
    - tests/test_mde_datadumper.py (Phase 3)
  3. Coverage improvement:
    - From 30.3% to 45% overall
    - Each phase should show measurable improvement
    - Run coverage after each module completion
  4. Documentation updates:
    - Update TODO.md with completed tasks
    - Note any blockers or authorization needs

  If You Encounter Untestable Code

  1. STOP - Don't modify the source code
  2. DOCUMENT the issue:
  File: goosey/utils.py
  Lines: 575-598
  Reason: Platform-specific file locking
  Impact: ~24 lines
  Suggested: # pragma: no cover
  3. REQUEST authorization with documentation
  4. WAIT for approval before proceeding

  Success Criteria

  ✅ Your implementation is successful when:
  - Overall coverage reaches 45% or higher
  - All tests pass (maintain 100% pass rate)
  - Tests follow behavioral patterns, not structural
  - Existing mock factories are used consistently
  - TDD process was followed (commits show test-first approach)
  - No unauthorized changes to goosey/ directory
  - All work is properly documented

  Remember

  1. Read CLAUDE.md, PLAN.md, and TODO.md FIRST - They contain all the details
  2. Use existing patterns - Don't reinvent the wheel
  3. Test behavior, not implementation - Focus on what code does
  4. Follow TDD strictly - Red, Green, Refactor
  5. Ask for authorization - When touching source code
  6. Quality over quantity - Better to have fewer, high-quality tests

  Start by reading the three planning documents, then begin with Phase 3: Dumper Behavioral Tests
```
