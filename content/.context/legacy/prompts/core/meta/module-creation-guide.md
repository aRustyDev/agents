---
module: ModuleCreationGuide
scope: persistent
triggers: ["create module", "new module", "module template", "how to write module"]
conflicts: []
dependencies: ["module-interface"]
priority: high
---

# Module Creation Guide

## Purpose
Ensure all modules follow consistent patterns and integrate seamlessly with the modular CLAUDE system.

## Module Anatomy
Every module MUST contain these sections in order:

### 1. YAML Frontmatter (Required)
```yaml
---
module: ModuleName                    # PascalCase, descriptive
scope: persistent|context|temporary   # When should this stay loaded?
triggers: ["keyword1", "keyword2"]    # What words/phrases load this module?
conflicts: ["conflicting-module"]     # Modules that can't coexist
dependencies: ["required-module"]     # Modules that must load together
priority: low|medium|high            # Resolution precedence
author: YourName                     # Optional: who created this
created: 2024-01-15                  # Optional: creation date
---
```

### 2. Module Title and Purpose
```markdown
# [Module Name]

## Purpose
[1-2 sentence clear description of what this module does and why it exists]
```

### 3. Content Sections
Structure depends on module type:

#### For Process Modules:
```markdown
## Trigger
[When this process should be executed]

## Prerequisites
[What must be true/available before this process can run]

## Steps
[Numbered steps with sub-steps using consistent formatting]

## Output
[What this process produces/accomplishes]

## Integration Points
[How this connects to other modules]
```

#### For Pattern Modules:
```markdown
## When to Use
[Specific scenarios where this pattern applies]

## Implementation
[How to apply this pattern]

## Examples
[Concrete examples of the pattern in use]

## Anti-patterns
[What to avoid when using this pattern]
```

#### For Guide Modules:
```markdown
## Overview
[What this guide covers]

## Basic Usage
[Simple examples for common cases]

## Advanced Usage
[Complex scenarios and edge cases]

## Command Reference
[Complete list of commands/options]

## Troubleshooting
[Common problems and solutions]
```

#### For Workflow Modules:
```markdown
## Workflow Trigger
[What initiates this workflow]

## Workflow Steps
[High-level steps that reference specific processes]

## Decision Points
[Where the workflow might branch]

## Completion Criteria
[How to know the workflow is done]
```

## Module Creation Process

### Step 1: Identify Module Need
```
1.1 Document the gap the module fills
1.2 Search existing modules for overlap
1.3 Determine appropriate module type
1.4 Choose correct directory location
```

### Step 2: Define Module Metadata
```
2.1 Choose descriptive module name (PascalCase)
2.2 Determine appropriate scope:
    - locked: Critical security/compliance rules
    - persistent: Core methodologies (like TDD)
    - context: Domain-specific processes
    - temporary: Tool guides and one-off references
2.3 List trigger keywords (think what users might say)
2.4 Identify conflicts and dependencies
2.5 Set priority level
```

### Step 3: Write Module Content
```
3.1 Start with the template for your module type
3.2 Write clear, actionable content
3.3 Use consistent formatting:
    - Backticks for code/commands
    - ${variables} for placeholders
    - Bold for emphasis
    - Numbered lists for sequential steps
3.4 Include examples where helpful
3.5 Cross-reference other modules properly
```

### Step 4: Validate Module
```
4.1 Execute: !validate <module-path>
4.2 Fix any structural issues
4.3 Test trigger words make sense
4.4 Verify no circular dependencies
```

### Step 5: Integration Test
```
5.1 Place module in appropriate directory
5.2 Run: !reload-manifest
5.3 Test module loads correctly
5.4 Verify interactions with dependent modules
5.5 Check for conflicts
```

## Module Naming Conventions

### File Names
- Use kebab-case: `module-name.md`
- Be descriptive but concise
- Include category prefix if helpful: `git-workflow.md`

### Module Names (in frontmatter)
- Use PascalCase: `ModuleName`
- Match the concept: `TestDrivenDevelopment` not `TDDProcess`
- Avoid redundant suffixes like "Module" or "Process"

## Cross-Module References

### Linking to Other Modules
```markdown
Execute: Process: ModuleName
See: Pattern: PatternName
Requires: Guide: GuideName
```

### Conditional Loading
```markdown
IF condition:
    Load: workflows/specific-workflow.md
ELSE:
    Load: workflows/alternative-workflow.md
```

## Quality Checklist
Before finalizing any module, verify:

- [ ] Frontmatter is complete and valid
- [ ] Purpose is clear and concise
- [ ] All required sections are present
- [ ] Formatting is consistent
- [ ] Examples are practical and tested
- [ ] Cross-references use correct syntax
- [ ] No sensitive information included
- [ ] Module adds unique value (no duplication)
- [ ] Trigger words are intuitive
- [ ] Scope is appropriate for use case

## Common Pitfalls to Avoid

### 1. Scope Confusion
❌ Making a tool guide persistent
✅ Tool guides should be temporary

### 2. Over-broad Triggers
❌ Triggers: ["code", "work", "do"]
✅ Triggers: ["refactor safely", "refactoring process"]

### 3. Missing Dependencies
❌ Assuming version control is loaded
✅ Explicitly list in dependencies

### 4. Circular Dependencies
❌ Module A requires B, B requires A
✅ Extract shared content to Module C

### 5. Monolithic Modules
❌ One giant module for all testing
✅ Separate modules for TDD, CDD, BDD

## Module Templates

### Process Module Template
```markdown
---
module: ProcessName
scope: context
triggers: ["trigger phrase"]
conflicts: []
dependencies: []
priority: medium
---

# Process: [Process Name]

## Purpose
[What this process accomplishes]

## Trigger
[When to execute this process]

## Prerequisites
- [Prerequisite 1]
- [Prerequisite 2]

## Steps
\`\`\`
1. First Step
   1.1 Substep with detail
   1.2 Another substep

2. Second Step
   2.1 Execute: Process: OtherProcess
   2.2 Continue with results
\`\`\`

## Output
- [Output 1]
- [Output 2]

## Error Handling
IF [error condition]:
    [Resolution steps]
```

### Guide Module Template
```markdown
---
module: ToolGuide
scope: temporary
triggers: ["tool name", "how to use tool"]
conflicts: []
dependencies: []
priority: low
---

# [Tool Name] Guide

## Purpose
Quick reference for using [tool] effectively

## Basic Usage
\`\`\`bash
# Simple example
tool --basic-flag input
\`\`\`

## Common Patterns
### Pattern 1: [Description]
\`\`\`bash
tool --flag1 --flag2 input
\`\`\`

### Pattern 2: [Description]
\`\`\`bash
tool --complex-usage
\`\`\`

## Advanced Features
[Describe advanced usage]

## Troubleshooting
| Problem | Solution |
|---------|----------|
| Error X | Try solution Y |
```

## Module Evolution
Modules should evolve based on usage:

1. Track common questions about the module
2. Add clarifications for confusing parts
3. Update examples based on real usage
4. Add new triggers as language evolves
5. Split large modules when they become unwieldy

Remember: A well-crafted module is a reusable piece of knowledge that makes Claude more capable while keeping memory usage efficient.
