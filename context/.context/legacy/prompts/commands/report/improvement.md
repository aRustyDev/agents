---
module: ReportImprovement  
scope: context
triggers: 
  - "/report improvement"
  - "suggest improvement"
  - "enhancement request"
conflicts: []
dependencies:
  - _templates.md
  - _interactive.md
  - _improvement_templates.md
priority: high
---

# ReportImprovement - Enhancement Suggestions

## Purpose
Suggest improvements to existing functionality, including performance, usability, and code quality enhancements.

## Overview
Create improvement suggestions that enhance existing features without changing core functionality.

## Usage
```
/report improvement [--type <improvement-type>] [--target <target-area>]
```

## Options
- `--type` - Improvement type (performance, usability, maintainability, documentation, testing, accessibility)
- `--target` - Target area (command, module, process, workflow)
- `--data` - Include metrics/data to support suggestion
- `--priority` - Set priority level
- `--repo` - Specify repository directly

## Interactive Mode Workflow

### Step 1: Improvement Type Selection
```
What type of improvement are you suggesting?

1) performance - Speed, efficiency, resource usage
2) usability - User experience, interface, clarity
3) maintainability - Code quality, organization, readability
4) documentation - Better docs, examples, guides
5) testing - Test coverage, quality, automation
6) accessibility - Inclusivity, compatibility
7) error-handling - Better error messages, recovery
8) integration - Better tool/service integration

Select improvement type [1-8]: 
```

### Step 2: Target Identification
```
What are you suggesting to improve?

1) Specific command (e.g., /plan, /report)
2) Module or component
3) Process or workflow
4) Documentation section
5) System-wide improvement
6) Configuration or setup

Select target [1-6]: 
```

### Step 3: Current State Description
```
Describe the current state:
- What exists today?
- What are the pain points?
- How does it impact users?

Current state: 
```

### Step 4: Proposed Improvement
```
Describe your proposed improvement:
- What should change?
- How would it work better?
- What's the expected benefit?

Proposed improvement: 
```

### Step 5: Data and Evidence
```
Do you have data to support this improvement?
(metrics, benchmarks, user feedback, etc.)

Type 'none' if no data, or provide details:

Supporting data: 
```

### Step 6: Impact Assessment
```
Who would benefit from this improvement?

1) All users
2) Power users
3) New users
4) Developers/contributors
5) Specific user group: ________

Select beneficiaries [1-5]: 

Estimated improvement:
- Performance gain: ____%
- Time saved: ____
- Other benefits: ____
```

### Step 7: Implementation Complexity
```
How complex is this improvement?

1) trivial - Simple change, < 1 hour
2) small - Straightforward, < 4 hours
3) medium - Some complexity, 1-2 days
4) large - Significant work, 3-5 days
5) very large - Major effort, > 1 week

Complexity [1-5]: 
```

## Improvement Templates

**See**: `_improvement_templates.md` for complete templates

Available templates:
- Performance Improvement Template
- Usability Improvement Template
- Code Quality Improvement Template
- Documentation Improvement Template
- Process Improvement Template
- Integration Improvement Template

Each template provides structured format for specific improvement types.

## Data-Driven Improvements

When `--data` flag is used, include:
1. Current metrics/benchmarks
2. Comparative analysis
3. User feedback surveys
4. Performance profiles
5. Usage analytics

Example:
```bash
/report improvement --type performance --data <<EOF
Current: 5.2s average execution time
Benchmark: Similar tools achieve 1.8s
Profiling: 60% time in network calls
Proposal: Implement caching layer
Expected: 2.1s execution time (60% improvement)
EOF
```

## Improvement Categories

### Quick Wins
- Low effort, high impact
- Can be done immediately
- No breaking changes
- Clear benefits

### Strategic Improvements
- Higher effort, long-term value
- May require planning
- Significant benefits
- Worth the investment

### Technical Debt
- Cleanup and refactoring
- Improves maintainability
- Prevents future issues
- Enables new features

## Integration

This module:
- Uses `_templates.md` for formatting
- Uses `_interactive.md` for prompts
- Can include metrics and data
- Links to related issues/PRs

## Best Practices

1. **Be specific**: Vague suggestions rarely get implemented
2. **Show impact**: Quantify benefits when possible
3. **Consider trade-offs**: Acknowledge any downsides
4. **Provide examples**: Show before/after states
5. **Start small**: Incremental improvements are easier to adopt