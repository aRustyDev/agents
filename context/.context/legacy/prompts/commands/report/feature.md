---
module: ReportFeature  
scope: context
triggers: 
  - "/report feature"
  - "feature request"
  - "request feature"
conflicts: []
dependencies:
  - _templates.md
  - _interactive.md
  - _feature_templates.md
priority: high
---

# ReportFeature - Feature Request Creation

## Purpose
Request new functionality or capabilities for commands, modules, or the system.

## Overview
Create comprehensive feature requests with user stories, requirements, and implementation suggestions.

## Usage
```
/report feature [--type <feature-type>] [--command <command-name>]
```

## Options
- `--type` - Feature type (command, pattern, role, guide, process, workflow, tool, module, integration)
- `--command` - Related command (if applicable)
- `--priority` - Set priority (critical, high, medium, low)
- `--repo` - Specify repository directly
- `--template` - Use specific template

## Interactive Mode Workflow

### Step 1: Feature Type Selection
```
What type of feature are you requesting?

1) command - New slash command
2) pattern - Development or design pattern
3) role - Expert role or persona
4) guide - How-to documentation
5) process - Reusable process/procedure
6) workflow - Multi-step workflow
7) tool - External tool integration
8) module - New module for existing command
9) integration - Third-party integration

Select feature type [1-9]: 
```

### Step 2: Feature Context

#### For Commands
```
Command name (e.g., 'analyze', 'deploy'): 
Primary purpose (one sentence): 
Target users (who will use this): 
```

#### For Patterns
```
Pattern name: 
Problem it solves: 
When to use it: 
```

#### For Roles
```
Role name: 
Expertise area: 
Key responsibilities: 
```

### Step 3: User Story
```
Please provide a user story:
As a [type of user]
I want [feature/capability]
So that [benefit/value]

User story: 
```

### Step 4: Requirements Gathering

#### Functional Requirements
```
What specific functionality is needed?
List key features (one per line, blank line to finish):

1. 
2. 
3. 
```

#### Acceptance Criteria
```
How will we know this feature is complete?
List acceptance criteria:

- [ ] 
- [ ] 
- [ ] 
```

### Step 5: Use Cases
```
Describe 2-3 specific use cases:

Use case 1: 
Use case 2: 
Use case 3: 
```

### Step 6: Technical Considerations
```
Any technical requirements or constraints?
(APIs, dependencies, performance needs, etc.)

Technical notes: 
```

### Step 7: Priority and Impact
```
What's the priority of this feature?

1) critical - Blocks important work
2) high - Significant value, needed soon
3) medium - Important but not urgent
4) low - Nice to have

Priority [1-4]: 

Who benefits from this feature?
How many users would this impact?
```

## Feature Templates

**See**: `_feature_templates.md` for complete templates

Available templates:
- Command Feature Template - For new slash commands
- Integration Feature Template - For external service integrations
- Module Feature Template - For new system modules
- UI Feature Template - For user interface enhancements
- API Feature Template - For new API endpoints
- Workflow Feature Template - For process automation

Select template based on feature type and replace placeholders with specifics.

## Creating New Feature Types

To add support for new feature types:

1. Add to feature type selection menu
2. Create context gathering questions
3. Design feature template
4. Update validation logic

Example for adding "automation" type:
```yaml
automation:
  questions:
    - "What manual process will this automate?"
    - "How often is this task performed?"
    - "What triggers the automation?"
  template: automation-feature.md
  required_fields:
    - trigger_description
    - frequency
    - time_savings
```

## Smart Defaults

Based on feature type, apply smart defaults:
- **Commands**: High priority, requires documentation
- **Integrations**: Medium priority, requires security review
- **Patterns**: Low priority, requires examples
- **Tools**: Medium priority, requires compatibility check

## Integration

This module:
- Uses `_templates.md` for issue formatting
- Uses `_interactive.md` for user interaction
- Can reference existing commands/modules
- Integrates with project planning tools

## Best Practices

1. **Clear user story**: Focus on the why
2. **Specific requirements**: Avoid vague requests
3. **Real use cases**: Provide concrete examples
4. **Consider alternatives**: Show you've thought it through
5. **Estimate impact**: Help prioritize the work