---
name: testing-strategies
description: JUnit report integration, coverage regex, quality reports, and test result visualization
---

# Testing Strategies

> **Scope:** JUnit report integration, coverage regex, quality reports, and test result visualization
> **GitLab version:** 11.0+
> **Source cards:** JB-1
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Configuring test jobs with JUnit/Cobertura/code quality reports
- Integrating test results into MR widgets
- Setting up parallel test execution and test splitting
- Implementing fail-fast strategies and flaky test detection
- Extracting code coverage percentages

## Key Concepts

### Test Report Types

| Report Type | Keyword | MR Widget | Format |
|---|---|---|---|
| **JUnit** | `artifacts:reports:junit:` | Test summary tab | JUnit XML |
| **Code coverage** | `coverage:` regex | Coverage badge | Regex on stdout |
| **Cobertura** | `artifacts:reports:coverage_report:` | Diff coverage viz | Cobertura XML |
| **Code quality** | `artifacts:reports:codequality:` | Code quality tab | CodeClimate JSON |
| **Accessibility** | `artifacts:reports:accessibility:` | Accessibility tab | pa11y JSON |
| **Browser perf** | `artifacts:reports:browser_performance:` | Performance tab | Sitespeed.io |
| **Custom metrics** | `artifacts:reports:metrics:` | Metrics report | `key value` text |

### Coverage Regex

Extract coverage from job output with language-specific patterns:

| Language | Regex |
|---|---|
| Python (pytest-cov) | `TOTAL\s+\d+\s+\d+\s+(\d+)%` |
| JavaScript (Jest) | `All files[^|]*\|\s*([\d.]+)` |
| Go | `coverage:\s*([\d.]+)%` |
| Ruby (SimpleCov) | `\(\d+.\d+%\) covered` |

### Always Upload Reports

```yaml
artifacts:
  when: always  # Upload reports even when tests fail
  reports:
    junit: report.xml
```

> **Critical:** Without `when: always`, test reports are lost when the job fails — exactly when you need them most.

### Test Failure Tracking

GitLab detects flaky tests by comparing JUnit results across pipelines:
- **Test suite** tab in MR shows new failures vs. existing failures
- Tests that alternate pass/fail are flagged as flaky (Premium+)

## Examples

### Parallel Test with JUnit

```yaml
test:
  stage: test
  parallel: 4
  script:
    - bundle exec rspec $(scripts/split-tests.sh $CI_NODE_INDEX $CI_NODE_TOTAL)
  artifacts:
    when: always
    reports:
      junit: rspec-*.xml
    paths:
      - coverage/
  coverage: '/\(\d+.\d+%\) covered/'
```

### Multi-Framework Test Matrix

```yaml
test:
  stage: test
  parallel:
    matrix:
      - SUITE: [unit, integration, e2e]
  script:
    - make test-$SUITE
  artifacts:
    when: always
    reports:
      junit: reports/$SUITE-junit.xml
      coverage_report:
        coverage_format: cobertura
        path: reports/coverage.xml
```

### Code Quality Report

```yaml
code-quality:
  stage: test
  image: registry.gitlab.com/gitlab-org/ci-cd/codequality:latest
  script:
    - /analyzer run
  artifacts:
    reports:
      codequality: gl-code-quality-report.json
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

## Common Patterns

- **`artifacts:reports:junit`** for MR test summaries — most impactful single addition
- **`artifacts:when: always`** to upload reports even on failure
- **`parallel:` + test splitting** for large test suites
- **`coverage:` regex** for MR coverage badge
- **`fail_fast`** (RSpec) or equivalent for quick feedback on obvioius failures
- **`allow_failure: exit_codes: [42]`** for flaky test tolerance

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| All tests in one job | Slow, no parallelism | Use `parallel:` with test splitting |
| Missing `artifacts:when: always` | Reports lost on failure | Always set `when: always` for reports |
| Missing `artifacts:reports:junit` | No MR test summary | Add JUnit report to `artifacts:reports:` |
| Duplicate test names in JUnit XML | Parsing issues, inaccurate counts | Ensure unique test names |
| No coverage extraction | No coverage tracking over time | Add `coverage:` regex |

## Practitioner Pain Points

1. **`artifacts:when: always` is essential** — without it, test reports vanish on failure. Most common omission in test job config.
2. **Test splitting requires custom scripts** — GitLab provides `$CI_NODE_INDEX` and `$CI_NODE_TOTAL` but not a built-in test splitter.
3. **Flaky test detection requires Premium+** — free tier only sees pass/fail per run, no cross-pipeline comparison.
<!-- TODO: Expand with deeper research on load balancing test splitting and fail-fast patterns -->

## Related Topics

- [artifacts.md](artifacts.md) — Artifact configuration and expiration
- [caching.md](caching.md) — Caching test dependencies
- [../pipelines/optimization.md](../pipelines/optimization.md) — Test parallelism strategies

## Sources

- [Unit test reports](https://docs.gitlab.com/ci/testing/unit_test_reports/)
- [Code coverage](https://docs.gitlab.com/ci/testing/code_coverage/)
- [Test failure tracking](https://docs.gitlab.com/ci/testing/test_failure_tracking/)
