---
module: ReportFeatureTemplates
scope: context
triggers: []
conflicts: []
dependencies: []
priority: medium
---

# ReportFeatureTemplates - Feature Request Templates

## Purpose
Reusable templates for different types of feature requests.

## Command Feature Template
```markdown
## Summary
{{feature_summary}}

## User Story
As a {{user_type}}
I want {{feature_description}}
So that {{benefit}}

## Description
{{detailed_description}}

## Requirements
### Functional Requirements
{{functional_requirements}}

### Non-Functional Requirements
- Performance: {{performance_needs}}
- Security: {{security_needs}}
- Usability: {{usability_needs}}

## Acceptance Criteria
{{acceptance_criteria}}

## Use Cases
### Use Case 1: {{use_case_1_title}}
{{use_case_1_description}}

### Use Case 2: {{use_case_2_title}}
{{use_case_2_description}}

## Technical Design
### Proposed Implementation
{{implementation_approach}}

### Dependencies
{{dependencies}}

### API Design (if applicable)
{{api_design}}

## Impact Analysis
- Users affected: {{user_impact}}
- Backward compatibility: {{compatibility}}
- Documentation needs: {{doc_needs}}

## Alternatives Considered
{{alternatives}}
```

## Integration Feature Template
```markdown
## Summary
Integration with {{service_name}}

## Motivation
{{why_needed}}

## Integration Points
{{integration_details}}

## Authentication
{{auth_requirements}}

## Data Flow
{{data_flow_description}}

## Security Considerations
{{security_notes}}

## Implementation Phases
1. {{phase_1}}
2. {{phase_2}}
3. {{phase_3}}
```

## Module Feature Template
```markdown
## Summary
New module: {{module_name}}

## Purpose
{{module_purpose}}

## Module Structure
- Scope: {{scope}}
- Triggers: {{triggers}}
- Dependencies: {{dependencies}}

## Key Functions
{{key_functions}}

## Integration Points
{{integration_with_existing}}

## Testing Strategy
{{testing_approach}}
```

## UI Feature Template
```markdown
## Summary
{{ui_feature_summary}}

## Current State
{{current_ui_state}}

## Proposed Enhancement
{{proposed_ui_change}}

## Mockups/Wireframes
{{mockup_references}}

## User Flow
1. {{step_1}}
2. {{step_2}}
3. {{step_3}}

## Accessibility Considerations
{{accessibility_requirements}}

## Browser/Platform Support
{{support_matrix}}
```

## API Feature Template
```markdown
## Summary
New API endpoint: {{endpoint_name}}

## Endpoint Details
- Method: {{http_method}}
- Path: {{api_path}}
- Authentication: {{auth_type}}

## Request Format
{{request_schema}}

## Response Format
{{response_schema}}

## Error Handling
{{error_responses}}

## Rate Limiting
{{rate_limit_details}}

## Examples
{{usage_examples}}
```

## Workflow Feature Template
```markdown
## Summary
New workflow: {{workflow_name}}

## Workflow Steps
1. {{step_1}}
2. {{step_2}}
3. {{step_3}}

## Triggers
{{workflow_triggers}}

## Automation Points
{{automation_opportunities}}

## Error Handling
{{error_scenarios}}

## Success Metrics
{{success_indicators}}
```

## Template Selection Guide

Choose template based on feature type:
- New commands → Command Feature Template
- External services → Integration Feature Template
- New modules → Module Feature Template
- UI changes → UI Feature Template
- API endpoints → API Feature Template
- Process automation → Workflow Feature Template

For complex features, combine multiple templates as needed.