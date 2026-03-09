---
name: artifacts
description: expire_in, expose_as, access levels, cross-pipeline sharing, and artifact dependencies
---

# Artifacts

> **Scope:** expire_in, expose_as, access levels, cross-pipeline sharing, and artifact dependencies
> **GitLab version:** 9.0+
> **Source cards:** JB-4
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Passing build outputs between jobs and stages
- Uploading test reports (JUnit, coverage, code quality) for MR widgets
- Configuring artifact expiration to control storage costs
- Sharing artifacts across pipelines or projects
- Exposing build outputs as links in merge requests

## Key Concepts

### Artifact Configuration

| Keyword | Purpose |
|---|---|
| `artifacts:paths:` | Glob patterns for files to upload |
| `artifacts:exclude:` | Patterns to exclude from upload |
| `artifacts:untracked: true` | Include gitignored files |
| `artifacts:expire_in:` | Duration: `30 days`, `1 week`, `never` |
| `artifacts:when:` | `on_success` (default), `on_failure`, `always` |
| `artifacts:name:` | Custom archive name (supports variables) |
| `artifacts:expose_as:` | Display name in MR widget (single file/directory) |
| `artifacts:access:` | `all`, `developer`, `maintainer`, `none` (17.1+) |

### Report Artifacts

Artifacts under `artifacts:reports:` are processed by GitLab for MR widgets:

| Report | MR Widget |
|---|---|
| `junit:` | Test summary tab |
| `coverage_report:` | Diff coverage visualization |
| `codequality:` | Code quality changes |
| `sast:` | Security vulnerability report |
| `dependency_scanning:` | Dependency vulnerabilities |
| `container_scanning:` | Container image vulnerabilities |
| `license_scanning:` | License compliance |
| `dotenv:` | Variable export to downstream jobs |

### Artifact Download Control

| Keyword | Purpose |
|---|---|
| `dependencies: [job-a]` | Only download artifacts from listed jobs |
| `dependencies: []` | Download **no** artifacts (speed optimization) |
| `needs: [job-a]` | Download artifacts from `job-a` + create DAG edge |
| `needs:artifacts: false` | DAG edge without artifact download |

### Cross-Pipeline Artifacts

```yaml
# Download artifacts from another pipeline/project
consume:
  needs:
    - project: group/other-project
      job: build
      ref: main
      artifacts: true
```

> **64K+ views on Stack Overflow** — cross-pipeline artifact sharing is a top pain point.

### Keep Latest Artifacts

**Settings > CI/CD > Artifacts > Keep artifacts from most recent successful jobs** — prevents expiration of the latest good build artifacts. Affects all jobs equally (project-level setting).

### Variable Expansion in Paths

Artifact paths support variable expansion: `artifacts:paths: ["dist/$CI_COMMIT_REF_SLUG/"]`

## Examples

### Standard Build Artifacts

```yaml
build:
  stage: build
  script: make build
  artifacts:
    paths:
      - dist/
    exclude:
      - dist/**/*.map
    expire_in: 1 week
    name: "$CI_PROJECT_NAME-$CI_COMMIT_SHORT_SHA"
```

### Test Reports with Always-Upload

```yaml
test:
  stage: test
  script: pytest --junitxml=report.xml --cov=app --cov-report=xml
  artifacts:
    when: always
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
    expire_in: 30 days
```

### Expose Build in MR

```yaml
build-docs:
  stage: build
  script: mkdocs build -d public
  artifacts:
    paths:
      - public/
    expose_as: Documentation Preview
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

## Common Patterns

- **`artifacts:when: always`** for test reports — essential for failure debugging
- **`artifacts:expire_in: 1 week`** on non-critical builds to control storage
- **`artifacts:expose_as:`** for MR-visible links to built documentation/previews
- **`dependencies: []`** to skip artifact downloads in jobs that don't need them
- **`artifacts:access: developer`** to restrict access to sensitive outputs
- **`artifacts:reports:dotenv`** to export variables to downstream jobs

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| No `expire_in:` | Artifacts persist forever, storage costs grow | Set appropriate `expire_in:` |
| Broad `paths:` without `exclude:` | Upload unnecessary files | Use `exclude:` to trim |
| Missing `when: always` on test reports | Reports lost on failure | Add `when: always` |
| Large artifacts between every stage | Slow upload/download | Use `dependencies: []` where unneeded |
| `needs:` when only DAG is wanted | Unwanted artifact download | Use `needs:artifacts: false` |

## Practitioner Pain Points

1. **Cross-pipeline artifact sharing** (64K+ SO views) — requires `needs:project:` with exact `job:`, `ref:`, and `artifacts: true`.
2. **`dependencies:` vs `needs:` confusion** — `dependencies:` controls artifact download; `needs:` creates DAG edge AND downloads artifacts.
3. **Storage costs grow without `expire_in:`** — artifacts never expire by default. Set `expire_in:` on every job.
4. **Keep latest artifacts is project-wide** — cannot selectively keep artifacts for specific jobs.
<!-- TODO: Expand with deeper research on artifact attestation and access control patterns -->

## Related Topics

- [caching.md](caching.md) — Cache for dependencies, artifacts for outputs
- [testing.md](testing.md) — Test report artifacts
- [execution-flow.md](execution-flow.md) — `needs:` and `dependencies:` interaction
- [../pipelines/downstream.md](../pipelines/downstream.md) — Cross-pipeline artifacts

## Sources

- [Job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [Artifact reports](https://docs.gitlab.com/ci/yaml/artifacts_reports/)

