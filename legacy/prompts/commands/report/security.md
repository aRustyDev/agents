---
module: ReportSecurity  
scope: context
triggers: 
  - "/report security"
  - "security issue"
  - "vulnerability report"
conflicts: []
dependencies:
  - _templates.md
  - _interactive.md
  - _security_templates.md
  - cvss-scoring.md
priority: high
---

# ReportSecurity - Security Issue Reporting

## Purpose
Report security vulnerabilities, concerns, and risks in a responsible manner.

## Overview
Create security reports following responsible disclosure practices with appropriate severity assessment and mitigation suggestions.

## Usage
```
/report security [--severity <level>] [--private]
```

## Options
- `--severity` - Severity level (critical, high, medium, low, info)
- `--private` - Create as private security advisory
- `--cve` - Include CVE reference if known
- `--cvss` - Calculate CVSS score
- `--repo` - Specify repository

## Security Reporting Workflow

### Step 1: Initial Assessment
```
⚠️  SECURITY REPORT - CONFIDENTIAL ⚠️

This appears to be a security issue. 
Would you like to:

1) Create private security advisory (recommended)
2) Create public issue with redacted details
3) Contact security team directly
4) Cancel and seek guidance

Select option [1-4]: 
```

### Step 2: Vulnerability Type
```
What type of security issue is this?

1) authentication - Auth bypass, credential exposure
2) authorization - Privilege escalation, access control
3) injection - Code/command injection, XSS, SQLi
4) data-exposure - Information disclosure, data leak
5) cryptography - Weak crypto, insecure random
6) dos - Denial of service, resource exhaustion
7) configuration - Insecure defaults, misconfig
8) dependency - Vulnerable dependency
9) other - Other security issue

Select type [1-9]: 
```

### Step 3: Severity Assessment
```
Rate the severity based on:
- Exploitability
- Impact
- Scope

1) critical - Remote code execution, data breach
2) high - Privilege escalation, significant impact
3) medium - Limited impact, requires conditions
4) low - Minor issue, minimal impact
5) info - Best practice, defense in depth

Severity [1-5]: 
```

### Step 4: Vulnerability Details
```
Describe the vulnerability:
(Be specific but avoid exploit code)

Description: 

Affected components: 

Prerequisites/conditions: 
```

### Step 5: Proof of Concept
```
Can you provide a proof of concept?
(Demonstrate the issue without causing harm)

NOTE: Do not include actual exploit code
Provide steps to reproduce safely:

1. 
2. 
3. 
```

### Step 6: Impact Analysis
```
What is the potential impact?

- Confidentiality impact: [none/low/high]
- Integrity impact: [none/low/high]
- Availability impact: [none/low/high]
- Scope: [unchanged/changed]

Who could be affected?
What data/systems are at risk?
```

### Step 7: Mitigation
```
Suggested mitigation:

Immediate mitigation: 

Long-term fix: 

Workarounds: 
```

## CVSS Scoring

When `--cvss` is used, see `cvss-scoring.md` for:
- Complete CVSS v3.1 base score calculator
- Attack vector definitions and scores
- Impact metrics and calculations
- Example vectors for common vulnerabilities

## Security Templates

**See**: `_security_templates.md` for complete templates

Available templates:
- Critical Vulnerability Template - For critical security issues
- Dependency Vulnerability Template - For vulnerable dependencies
- Security Issue Template - General security issues
- Security Advisory Template - Formal security advisories
- Incident Report Template - Post-incident documentation

## Responsible Disclosure

1. **Private First**: Always start with private disclosure
2. **Coordinate**: Work with maintainers on fix
3. **Timeline**: Allow reasonable time for patching
4. **Credit**: Acknowledge researchers appropriately
5. **Transparency**: Disclose after fix is available

## Security Contacts

Maintain list of security contacts:
```yaml
security_contacts:
  prompts:
    email: security@example.com
    github: @security-team
  custom-repo:
    email: maintainer@example.com
```

## Integration

This module:
- Creates private security advisories
- Uses encrypted communication when needed
- Follows coordinated disclosure
- Integrates with GitHub Security features

## Best Practices

1. **No exploit code**: Never include working exploits
2. **Private first**: Start with private disclosure
3. **Be responsible**: Consider impact on users
4. **Document clearly**: Help maintainers understand
5. **Follow up**: Ensure issues are addressed