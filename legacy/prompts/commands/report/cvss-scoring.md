---
module: ReportCVSSScoring
scope: context
triggers: []
conflicts: []
dependencies: []
priority: medium
---

# ReportCVSSScoring - CVSS Score Calculation

## Purpose
Guide for calculating CVSS v3.1 scores for security vulnerabilities.

## CVSS v3.1 Base Score Calculator

### Attack Vector (AV)
- **Network (N)**: Remotely exploitable (score: 0.85)
- **Adjacent Network (A)**: Same network segment (score: 0.62)
- **Local (L)**: Local access required (score: 0.55)
- **Physical (P)**: Physical access required (score: 0.2)

### Attack Complexity (AC)
- **Low (L)**: No special conditions (score: 0.77)
- **High (H)**: Special conditions required (score: 0.44)

### Privileges Required (PR)
Impact depends on Scope:
- **None (N)**: No privileges (score: 0.85)
- **Low (L)**: Basic privileges (score: 0.62/0.68)
- **High (H)**: Admin privileges (score: 0.27/0.5)

### User Interaction (UI)
- **None (N)**: No user action (score: 0.85)
- **Required (R)**: User must act (score: 0.62)

### Scope (S)
- **Unchanged (U)**: Impact limited to vulnerable component
- **Changed (C)**: Impact beyond vulnerable component

### Impact Metrics

#### Confidentiality Impact (C)
- **None (N)**: No impact (score: 0)
- **Low (L)**: Limited disclosure (score: 0.22)
- **High (H)**: Total disclosure (score: 0.56)

#### Integrity Impact (I)
- **None (N)**: No impact (score: 0)
- **Low (L)**: Limited modification (score: 0.22)
- **High (H)**: Total modification (score: 0.56)

#### Availability Impact (A)
- **None (N)**: No impact (score: 0)
- **Low (L)**: Reduced performance (score: 0.22)
- **High (H)**: Total unavailability (score: 0.56)

## Score Calculation

Base Score = roundup(min[(Impact + Exploitability), 10])

Where:
- Impact = 6.42 × ISC (if Scope Unchanged)
- Impact = 7.52 × (ISC - 0.029) - 3.25 × (ISC - 0.02)^15 (if Scope Changed)
- ISC = 1 - [(1 - C) × (1 - I) × (1 - A)]
- Exploitability = 8.22 × AV × AC × PR × UI

## Severity Ratings
- **None**: 0.0
- **Low**: 0.1 - 3.9
- **Medium**: 4.0 - 6.9
- **High**: 7.0 - 8.9
- **Critical**: 9.0 - 10.0

## Example Vectors

### Remote Code Execution
`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`
Base Score: 9.8 (Critical)

### SQL Injection
`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`
Base Score: 9.1 (Critical)

### XSS (Reflected)
`CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`
Base Score: 6.1 (Medium)

### Local Privilege Escalation
`CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H`
Base Score: 7.8 (High)

## Usage in Reports

Include CVSS score and vector in security reports:
```markdown
## Severity
**HIGH** - CVSS 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
```