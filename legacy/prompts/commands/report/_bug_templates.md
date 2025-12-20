---
module: ReportBugTemplates
scope: context
triggers: []
conflicts: []
dependencies: []
priority: medium
---

# ReportBugTemplates - Bug Report Templates

## Purpose
Reusable templates for different types of bug reports.

## Execution Error Template
```markdown
## Summary
Command execution failed with error

## Command
`/{{command}}`

## Error Message
```
{{error_message}}
```

## Steps to Reproduce
{{reproduction_steps}}

## Expected Behavior
Command should execute successfully

## Actual Behavior
{{actual_behavior}}

## Environment
- Claude Version: {{claude_version}}
- Prompts Version: {{prompts_version}}
- System: {{system_info}}

## Additional Context
{{additional_context}}
```

## Unexpected Behavior Template
```markdown
## Summary
{{brief_description}}

## Command
`/{{command}}`

## Expected Behavior
{{expected_behavior}}

## Actual Behavior
{{actual_behavior}}

## Steps to Reproduce
{{reproduction_steps}}

## Impact
{{impact_description}}

## Environment
- Claude Version: {{claude_version}}
- Prompts Version: {{prompts_version}}

## Possible Cause
{{analysis}}
```

## Missing Behavior Template
```markdown
## Summary
Expected functionality is missing from {{command}}

## Command
`/{{command}}`

## Missing Functionality
{{missing_feature_description}}

## Use Case
{{use_case_description}}

## Expected Behavior
{{expected_behavior}}

## Current Behavior
{{current_behavior}}

## Workaround
{{workaround_if_any}}
```

## Performance Issue Template
```markdown
## Summary
Performance issue with {{command}}

## Command
`/{{command}}`

## Performance Metrics
- Execution time: {{execution_time}}
- Resource usage: {{resource_usage}}
- Expected time: {{expected_time}}

## Steps to Reproduce
{{reproduction_steps}}

## Test Data
{{test_data_description}}

## Environment
{{environment_details}}

## Analysis
{{performance_analysis}}
```

## Documentation Bug Template
```markdown
## Summary
Documentation issue in {{location}}

## Location
{{documentation_path}}

## Issue Type
{{issue_type}} (incorrect, missing, outdated, unclear)

## Current Documentation
{{current_text}}

## Suggested Fix
{{suggested_text}}

## Impact
{{impact_on_users}}
```

## Logic Order Bug Template
```markdown
## Summary
{{command}} executes steps in wrong order

## Command
`/{{command}}`

## Current Order
1. {{current_step_1}}
2. {{current_step_2}}
3. {{current_step_3}}

## Expected Order
1. {{expected_step_1}}
2. {{expected_step_2}}
3. {{expected_step_3}}

## Impact
{{impact_description}}

## Steps to Reproduce
{{reproduction_steps}}
```

## General Bug Template
```markdown
## Summary
{{bug_summary}}

## Description
{{detailed_description}}

## Steps to Reproduce
{{reproduction_steps}}

## Expected Result
{{expected_result}}

## Actual Result
{{actual_result}}

## Environment
{{environment_info}}

## Additional Information
{{additional_info}}
```

## Template Selection
- Command errors → Execution Error Template
- Wrong output → Unexpected Behavior Template  
- Missing features → Missing Behavior Template
- Performance → Performance Issue Template
- Documentation → Documentation Bug Template
- Wrong order → Logic Order Bug Template
- Other → General Bug Template