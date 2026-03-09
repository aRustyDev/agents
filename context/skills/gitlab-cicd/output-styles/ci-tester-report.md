---
name: ci-tester-report-output
description: Behavioral spec for test result summaries — JUnit summary, coverage, failure analysis
---

# CI Tester Report Output

> **Scope:** Behavioral spec for test result summaries — JUnit summary, coverage, failure analysis
> **Source cards:** OS-3
> **Tier:** D
> **Last verified:** 2026-03

## When to Use

Use this output format when analyzing CI test results —
JUnit summaries, coverage reports, and failure analysis.

## Key Concepts

### Report Structure

1. **Test Summary** — pass/fail/skip counts, duration
2. **Coverage** — line/branch coverage percentage, trends
3. **Failure Analysis** — grouped by failure type with root cause
4. **Recommendations** — test improvements and coverage gaps

### Test Configuration

- **JUnit XML** — standard format for most test frameworks
- **`artifacts:reports:junit`** — path configuration for MR widget display
- **`artifacts:when: always`** — upload reports even on failure (critical!)
- **Coverage regex** — varies by language/framework
- Multiple JUnit report files are merged automatically
- Cannot have duplicate test names in JUnit XML

### MR Integration

- Test results appear in MR widget with pass/fail summary
- **Test failure tracking** (Premium+) tracks flaky tests over time
- Code coverage visualization highlights covered/uncovered lines

<!-- TODO: Expand with full behavioral spec for test report output -->

## Examples

```yaml
# Test job with JUnit and coverage reporting
test:
  script:
    - pytest --junitxml=report.xml --cov=src --cov-report=term
  artifacts:
    when: always
    reports:
      junit: report.xml
    paths:
      - htmlcov/
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

<!-- TODO: Expand with example test report output format -->

## Common Patterns

- `artifacts:reports:junit: report.xml` for MR test visualization
- Combined `artifacts:reports` + `artifacts:paths` for browsable HTML reports
- Coverage regex at job or project level
- `when: always` on test artifacts — reports even on failure

## Anti-Patterns

- Not uploading test reports — no MR visibility
- Duplicate test names in JUnit output — parsing errors
- Not using `artifacts:when: always` — reports lost when tests fail

## Practitioner Pain Points

- Each framework produces slightly different JUnit XML dialect
- Large JUnit files can slow MR widget rendering
- Coverage regex varies by language/framework (common source of confusion)

## Version Notes

<!-- TODO: Expand with deeper research -->

## Decision Guide

<!-- TODO: Expand with deeper research -->

## Related Topics

- [../references/jobs/testing.md](../references/jobs/testing.md) — test job configuration
- [../references/jobs/artifacts.md](../references/jobs/artifacts.md) — artifact configuration
- [troubleshooting-report.md](troubleshooting-report.md) — debugging test failures

## Sources

- [GitLab CI testing](https://docs.gitlab.com/ci/testing/)
- Context card: OS-3

