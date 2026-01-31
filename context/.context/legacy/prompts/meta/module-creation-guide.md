---
name: Module Creation Guide
module_type: meta
scope: persistent
priority: high
triggers: ["create module", "new module", "module template", "how to create module"]
dependencies: ["core/principles.md", "manifest.md"]
conflicts: []
version: 1.0.0
---

# Module Creation Guide

## Purpose
This meta-module provides templates and guidelines for creating new modules in the Claude modular system. It ensures consistency, completeness, and proper integration of new modules.

## Module Types

### 1. Process Module
For step-by-step procedures that accomplish specific tasks.

### 2. Workflow Module
For orchestrating multiple processes to achieve larger goals.

### 3. Pattern Module
For defining development methodologies and approaches.

### 4. Guide Module
For reference documentation and tool usage instructions.

### 5. Meta Module
For system management and module administration.

## Module Structure Requirements

### Required YAML Frontmatter
```yaml
---
name: [Descriptive Module Name]
module_type: [process|workflow|pattern|guide|meta]
scope: [persistent|context|temporary|locked]
priority: [critical|highest|high|medium|low]
triggers: ["keyword1", "keyword2", "phrase trigger"]
dependencies: ["path/to/dependency1.md", "path/to/dependency2.md"]
conflicts: ["path/to/conflicting-module.md"]
version: 1.0.0
---
```

### Field Definitions

#### name
- Full descriptive name of the module
- Use title case
- Be specific but concise

#### module_type
- **process**: Step-by-step procedures
- **workflow**: Multi-process orchestration
- **pattern**: Development methodology
- **guide**: Reference documentation
- **meta**: System management

#### scope
- **persistent**: Always loaded, never unloaded automatically
- **context**: Loaded based on conversation context
- **temporary**: Loaded for specific task then unloaded
- **locked**: Never unloaded unless explicitly unlocked

#### priority
- **critical**: Core functionality (1000)
- **highest**: Override modules (900)
- **high**: Important features (700)
- **medium**: Standard modules (500)
- **low**: Optional features (300)

#### triggers
- Keywords or phrases that cause automatic loading
- Use lowercase
- Include variations and common phrases
- More specific triggers take precedence

#### dependencies
- List of modules that must be loaded first
- Use relative paths from .claude/
- Check for circular dependencies

#### conflicts
- Modules that cannot be loaded simultaneously
- Usually alternative approaches to same problem
- Exception: comparison mode

## Module Content Structure

### Process Module Template
```markdown
# [Process Name]

## Purpose
[Clear, single-sentence description of what this process accomplishes]

## Trigger
[When this process should be executed]

## Prerequisites
- [Required condition 1]
- [Required condition 2]

## Process Steps

### 1. [Step Name]
**Goal**: [What this step achieves]

**Actions**:
1. [Specific action]
2. [Specific action]

**Checks**:
- [ ] [Verification point]
- [ ] [Verification point]

### 2. [Next Step]
[Continue pattern...]

## Output
[What the process produces]

## Integration Points
- Uses: [Process/Module this depends on]
- Used by: [Process/Module that uses this]
- May trigger: [Conditional processes]

## Best Practices
### DO
- ✅ [Positive practice]

### DON'T
- ❌ [Anti-pattern]

## Troubleshooting
[Common issues and solutions]
```

### Workflow Module Template
```markdown
# [Workflow Name]

## Purpose
[High-level goal this workflow achieves]

## Trigger
[What initiates this workflow]

## Workflow Steps

### 1. Process: [ProcessName]
**Purpose**: [Why this process]
**Focus**: [Specific aspects]
**Output**: [What it produces]

### 2. Decision Point: [Decision Name]
```
[Condition]
├─ Option A → [Action]
├─ Option B → [Action]
└─ Default → [Action]
```

### 3. Process: [NextProcess]
[Continue pattern...]

## Integration Points
### Required Processes
- [List of mandatory processes]

### Optional Processes
- [Conditional processes]

### May Trigger
- [Other workflows]

## Success Criteria
- [ ] [Measurable outcome]
- [ ] [Quality metric]

## Variations
### [Variation Name]
[When to use this variation]
[How it differs]
```

### Pattern Module Template
```markdown
# [Pattern Name]

## Purpose
[Philosophy and goal of this pattern]

## Core Principles
1. **[Principle Name]**: [Description]
2. **[Principle Name]**: [Description]

## Implementation
### Overview
[High-level description]

### Rules
#### [Phase Name] Rules
1. [Specific rule]
2. [Specific rule]

## When to Apply
- [Scenario 1]
- [Scenario 2]

## Benefits
- **[Benefit]**: [Explanation]

## Anti-Patterns
### [Anti-pattern Name]
❌ [What not to do]
✅ [What to do instead]

## Integration
- Implemented by: [Process modules]
- Used in: [Workflows]
```

## Module Creation Process

### 1. Identify Need
- Gap in current modules
- Repeated manual process
- New methodology

### 2. Determine Type
- Is it a step-by-step process?
- Does it orchestrate other processes?
- Is it a methodology or approach?
- Is it reference material?

### 3. Design Module
- Define clear purpose
- Identify triggers
- List dependencies
- Check for conflicts

### 4. Write Content
- Use appropriate template
- Follow structure guidelines
- Include examples
- Add troubleshooting

### 5. Validate Module
- Check YAML syntax
- Verify dependencies exist
- Test triggers
- Ensure no circular dependencies

### 6. Register Module
- Add to manifest.md
- Update category metadata
- Test loading/unloading

## Module Naming Conventions

### File Names
- Use kebab-case: `module-name.md`
- Be descriptive but concise
- Match module purpose

### Directory Structure
```
.claude/
├── processes/      # Step-by-step procedures
├── workflows/      # Multi-process orchestrations
├── patterns/       # Development methodologies
├── guides/         # Reference documentation
└── meta/          # System management
```

### Category Organization
- Group related modules
- Create `_meta.md` for categories
- Maximum 3 levels deep

## Module Quality Checklist

### Structure
- [ ] Valid YAML frontmatter
- [ ] All required fields present
- [ ] Appropriate module type
- [ ] Clear purpose statement

### Content
- [ ] Follows template structure
- [ ] Includes examples
- [ ] Has troubleshooting section
- [ ] Lists integration points

### Integration
- [ ] Dependencies valid
- [ ] No circular dependencies
- [ ] Conflicts documented
- [ ] Triggers appropriate

### Documentation
- [ ] Clear, concise writing
- [ ] Consistent formatting
- [ ] Practical examples
- [ ] Best practices included

## Common Mistakes

### Frontmatter Issues
- ❌ Missing required fields
- ❌ Invalid YAML syntax
- ❌ Wrong module type
- ✅ Validate before saving

### Scope Problems
- ❌ Context module marked persistent
- ❌ Critical module marked temporary
- ✅ Match scope to purpose

### Dependency Errors
- ❌ Circular dependencies
- ❌ Non-existent dependencies
- ❌ Missing dependencies
- ✅ Test load order

### Content Issues
- ❌ Vague purpose
- ❌ Missing integration points
- ❌ No examples
- ✅ Complete all sections

## Module Testing

### Load Testing
```bash
!load [module-path]
!list-modules  # Verify loaded
```

### Trigger Testing
- Use trigger keywords in conversation
- Verify automatic loading
- Check context switching

### Conflict Testing
```bash
!load [module1]
!load [conflicting-module]  # Should prompt
```

### Integration Testing
- Verify dependencies load
- Test in workflows
- Check process calls

## Maintenance

### Updates
- Increment version on changes
- Document changes
- Test thoroughly
- Update dependencies

### Deprecation
- Mark as deprecated
- Provide migration path
- Update dependents
- Schedule removal

### Review
- Regular quality checks
- Usage statistics
- Performance impact
- User feedback

---
*Creating well-structured modules ensures the system remains maintainable, discoverable, and effective.*