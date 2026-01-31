---
module: ReportSecurityTemplates
scope: context
triggers: []
conflicts: []
dependencies: []
priority: medium
---

# ReportSecurityTemplates - Security Report Templates

## Purpose
Reusable templates for security vulnerability reporting.

## Critical Vulnerability Template
```markdown
# SECURITY ADVISORY - CONFIDENTIAL

## Summary
{{vulnerability_summary}}

## Severity
**CRITICAL** - CVSS 9.8 ({{cvss_vector}})

## Description
{{detailed_description}}

## Affected Versions
{{affected_versions}}

## Proof of Concept
{{poc_steps}}

## Impact
{{impact_analysis}}

## Mitigation
### Immediate Actions
{{immediate_mitigation}}

### Patches
{{patch_information}}

## Timeline
- Discovery: {{discovery_date}}
- Reported: {{report_date}}
- Fixed: {{fix_date}}
- Disclosed: {{disclosure_date}}

## Credit
{{reporter_credit}}
```

## Dependency Vulnerability Template
```markdown
## Summary
Vulnerable dependency: {{dependency_name}}

## Details
- Package: {{package_name}}
- Version: {{current_version}}
- Vulnerability: {{cve_id}}
- Severity: {{severity}}

## Affected Components
{{affected_components}}

## Remediation
Update to version {{fixed_version}} or later

## Workaround
{{workaround_if_any}}
```

## Security Issue Template
```markdown
## Summary
{{issue_summary}}

## Vulnerability Type
{{vulnerability_type}}

## Severity
{{severity_level}} - {{cvss_score}} ({{cvss_vector}})

## Description
{{detailed_description}}

## Steps to Reproduce
1. {{step_1}}
2. {{step_2}}
3. {{step_3}}

## Impact
- Confidentiality: {{confidentiality_impact}}
- Integrity: {{integrity_impact}}
- Availability: {{availability_impact}}

## Recommended Fix
{{fix_recommendation}}

## References
- {{reference_1}}
- {{reference_2}}
```

## Security Advisory Template
```markdown
# Security Advisory: {{advisory_title}}

## Overview
{{advisory_overview}}

## Affected Products
{{affected_products}}

## Vulnerability Details
- **CVE ID**: {{cve_id}}
- **Type**: {{vulnerability_type}}
- **Severity**: {{severity}}
- **CVSS Score**: {{cvss_score}}

## Technical Details
{{technical_details}}

## Mitigations
{{mitigation_steps}}

## Detection
{{detection_guidance}}

## Timeline
{{disclosure_timeline}}

## Acknowledgments
{{acknowledgments}}
```

## Incident Report Template
```markdown
## Incident Summary
{{incident_summary}}

## Timeline
- Detection: {{detection_time}}
- Containment: {{containment_time}}
- Resolution: {{resolution_time}}

## Root Cause
{{root_cause_analysis}}

## Impact Assessment
{{impact_details}}

## Lessons Learned
{{lessons_learned}}

## Action Items
- [ ] {{action_1}}
- [ ] {{action_2}}
- [ ] {{action_3}}
```