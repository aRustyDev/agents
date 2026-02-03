# MCP Server Test Coverage Assessment

This document describes how test coverage is assessed for MCP servers, including unit tests, integration tests, end-to-end tests, and overall test robustness.

## Overview

The assessment schema tracks testing quality across multiple dimensions:

```sql
-- Fields in mcp_server_assessments
has_unit_tests INTEGER DEFAULT 0,      -- Boolean: 0 or 1
has_integration_tests INTEGER DEFAULT 0,
has_e2e_tests INTEGER DEFAULT 0,
test_coverage_pct REAL,                -- 0.0 to 100.0
test_robustness TEXT                   -- 'minimal', 'adequate', 'comprehensive'
```

## Test Type Definitions

### Unit Tests

Tests for individual functions, classes, or modules in isolation.

**Detection signals:**
- Files matching: `*_test.py`, `*.test.ts`, `*_spec.rb`, `*Test.java`
- Directories: `tests/unit/`, `__tests__/`, `spec/unit/`
- Frameworks: pytest, jest, mocha, rspec, junit

**Example patterns:**
```bash
# Python
tests/test_*.py
**/test_*.py

# JavaScript/TypeScript
**/*.test.ts
**/*.spec.js
__tests__/**/*.ts

# Go
**/*_test.go
```

### Integration Tests

Tests for interactions between components or external services.

**Detection signals:**
- Directories: `tests/integration/`, `integration_tests/`
- Files with "integration" in name
- Test fixtures for databases, APIs, or message queues
- Docker Compose test configurations

**Indicators:**
- Database fixtures or migrations in test setup
- Mock server configurations
- Network-dependent test utilities

### End-to-End Tests

Tests for complete workflows from user input to final output.

**Detection signals:**
- Directories: `tests/e2e/`, `e2e/`, `tests/functional/`
- Playwright, Cypress, Selenium configurations
- MCP client test harnesses
- Full server startup/shutdown in tests

**Indicators:**
- Browser automation configs
- Full MCP protocol test sequences
- Scenario-based test files

## Coverage Calculation

### Source-Based Coverage

If the repository includes coverage reports or CI badges:

1. **Parse coverage badges** from README:
   ```regex
   coverage[:\s]*(\d+(?:\.\d+)?)\s*%
   codecov.*?(\d+(?:\.\d+)?)%
   ```

2. **Check CI artifacts** for coverage reports:
   - `.coverage`, `coverage.xml`, `lcov.info`
   - `coverage/` directory with HTML reports

3. **Parse CI configs** for coverage thresholds:
   ```yaml
   # .github/workflows/test.yml
   - name: Check coverage
     run: pytest --cov=src --cov-fail-under=80
   ```

### Heuristic Coverage Estimation

When explicit coverage data is unavailable:

| Indicator | Estimated Coverage |
|-----------|-------------------|
| No test files found | 0% |
| Test files exist, no CI | 10-30% |
| CI runs tests, no coverage | 30-50% |
| CI with coverage, no threshold | 50-70% |
| CI with coverage threshold | Use threshold as estimate |
| Coverage badge present | Use badge value |

## Test Robustness Rating

The `test_robustness` field rates overall testing quality:

### Minimal

- Few or no tests
- No CI integration
- Manual testing only

**Criteria:**
- `has_unit_tests = 0` OR
- `test_coverage_pct < 20%` OR
- No CI configuration

### Adequate

- Unit tests present
- CI runs tests on PR
- Basic coverage

**Criteria:**
- `has_unit_tests = 1` AND
- `test_coverage_pct >= 40%` AND
- CI configuration exists

### Comprehensive

- Multi-level testing (unit + integration + e2e)
- High coverage with thresholds
- Mutation testing or property-based tests

**Criteria:**
- `has_unit_tests = 1` AND
- `has_integration_tests = 1` AND
- `test_coverage_pct >= 70%` AND
- Coverage thresholds enforced in CI

## Assessment Workflow

The profiler agent assesses test coverage by:

### Step 1: Scan Repository Structure

```bash
# Check for test directories
gh api repos/<owner>/<repo>/contents \
  --jq '.[] | select(.name | test("test|spec|__tests__")) | .name'

# Check for CI configs
gh api repos/<owner>/<repo>/contents/.github/workflows \
  --jq '.[].name' 2>/dev/null
```

### Step 2: Analyze Test Files

```bash
# Count test files by type
gh api repos/<owner>/<repo>/git/trees/HEAD?recursive=1 \
  --jq '[.tree[].path | select(test("test.*\\.(py|ts|js|go|rb)$"))] | length'
```

### Step 3: Parse CI Configuration

Look for test commands and coverage settings in:
- `.github/workflows/*.yml`
- `.travis.yml`
- `.circleci/config.yml`
- `Makefile` or `justfile`
- `package.json` scripts

### Step 4: Extract Coverage Data

```bash
# Check for coverage badges in README
gh api repos/<owner>/<repo>/readme --jq '.content' | base64 -d | \
  grep -oE 'coverage[^)]+\d+%'

# Check for codecov.yml
gh api repos/<owner>/<repo>/contents/codecov.yml 2>/dev/null
```

### Step 5: Record Assessment

```sql
UPDATE mcp_server_assessments SET
  has_unit_tests = 1,
  has_integration_tests = 1,
  has_e2e_tests = 0,
  test_coverage_pct = 78.5,
  test_robustness = 'adequate'
WHERE server_id = <entity_id> AND domain = '<need>';
```

## Querying Test Quality

Find well-tested servers:

```sql
SELECT e.name, e.slug,
       a.has_unit_tests, a.has_integration_tests, a.has_e2e_tests,
       a.test_coverage_pct, a.test_robustness
FROM mcp_server_assessments a
JOIN entities e ON a.server_id = e.id
WHERE a.test_robustness = 'comprehensive'
  AND a.test_coverage_pct >= 70
ORDER BY a.test_coverage_pct DESC;
```

## Current Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Schema fields | Implemented | All columns exist |
| Unit test detection | Partial | Via README/CI analysis |
| Integration test detection | Partial | Via directory structure |
| E2E test detection | Partial | Via framework configs |
| Coverage extraction | Planned | Badge parsing only |
| Robustness rating | Planned | Heuristics defined |
| Automated scanning | Planned | Manual assessment only |

## Future Improvements

- [ ] Clone repos locally for deep test analysis
- [ ] Parse AST to count test functions
- [ ] Run coverage tools on cloned repos
- [ ] Track coverage trends over time
- [ ] Integrate with codecov/coveralls APIs
- [ ] Assess test quality (assertions per test, mocking patterns)
