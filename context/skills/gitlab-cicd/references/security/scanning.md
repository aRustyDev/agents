---
name: security-scanning
description: SAST, DAST, container scanning, dependency scanning, and license compliance templates
---

# Security Scanning

> **Scope:** SAST, DAST, container scanning, dependency scanning, and license compliance templates
> **GitLab version:** 11.0+
> **Source cards:** NEW-13
> **Tier:** B
> **Last verified:** 2026-03

## When to Use

- Integrating SAST, DAST, container scanning, or dependency scanning into pipelines
- Adding security report artifacts to merge request widgets
- Setting up scheduled security scans for continuous monitoring
- Understanding which scanner types apply to your project

## Key Concepts

### Scanner Types

| Scanner | What It Checks | Stage | Report Keyword |
|---|---|---|---|
| **SAST** | Source code vulnerabilities | `test` | `artifacts:reports:sast:` |
| **DAST** | Running application vulnerabilities | `dast` | `artifacts:reports:dast:` |
| **Dependency Scanning** | Known library vulnerabilities | `test` | `artifacts:reports:dependency_scanning:` |
| **Container Scanning** | Docker image vulnerabilities | `test` | `artifacts:reports:container_scanning:` |
| **License Scanning** | Open source license compliance | `test` | `artifacts:reports:license_scanning:` |
| **Secret Detection** | Leaked credentials in code | `test` | `artifacts:reports:secret_detection:` |

### Integration via Templates

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
```

Templates define jobs with appropriate images, scripts, and report artifacts.

### MR Widget Integration

Security scan results appear in the MR widget:
- **New vulnerabilities** introduced by the MR are highlighted
- **Existing vulnerabilities** shown for context
- **Approval rules** can require zero new critical/high vulnerabilities (Ultimate)

### Vulnerability Management (Ultimate)

- **Vulnerability report** at project/group level
- **Vulnerability tracking** across pipelines
- **Auto-remediation** for known dependency vulnerabilities
- **Security policies** to enforce scanning requirements

## Examples

### Enable SAST and Dependency Scanning

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml

variables:
  SAST_EXCLUDED_PATHS: "spec,test,docs"
```

### Container Scanning

```yaml
include:
  - template: Security/Container-Scanning.gitlab-ci.yml

variables:
  CS_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### Scheduled Security Scan

```yaml
nightly-security:
  stage: test
  script: run-all-scanners
  artifacts:
    reports:
      sast: gl-sast-report.json
      dependency_scanning: gl-dependency-scanning-report.json
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

## Common Patterns

- **Include GitLab security templates** for one-line scanner integration
- **`artifacts:reports:`** for MR widget integration
- **Schedule-based scans** for continuous monitoring (not just on commits)
- **`SAST_EXCLUDED_PATHS`** to skip test/doc directories
- **Container scanning** after `docker build` with `CS_IMAGE` variable

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Enabling all scanners without evaluating relevance | Wasted CI minutes, noise | Enable only relevant scanners for your stack |
| Not reviewing findings in MR widget | Vulnerabilities slip through | Make security review part of MR process |
| Security scan only on default branch | Late detection | Scan on MR pipelines for early feedback |
| Ignoring scanner configuration variables | Missing customization | Set `SAST_EXCLUDED_PATHS`, `CS_IMAGE`, etc. |

## Practitioner Pain Points

1. **Scanner output volume** — SAST can produce many false positives. Tune with exclude paths and custom rulesets.
2. **Container scanning requires built image** — `CS_IMAGE` must reference the image built earlier in the pipeline.
3. **Vulnerability management requires Ultimate** — Free/Premium get MR widget reports but not tracking/remediation.
<!-- TODO: Expand with deeper research on custom SAST rulesets and DAST API scanning -->

## Related Topics

- [secrets-management.md](secrets-management.md) — Secret detection and management
- [compliance.md](compliance.md) — Compliance frameworks and security policies
- [../pipelines/security.md](../pipelines/security.md) — Pipeline-level security controls

## Sources

- [Security scanning](https://docs.gitlab.com/user/application_security/)
- [SAST](https://docs.gitlab.com/user/application_security/sast/)
- [Container scanning](https://docs.gitlab.com/user/application_security/container_scanning/)
