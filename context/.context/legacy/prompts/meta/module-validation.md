---
name: Module Validation Guide
module_type: meta
scope: context
priority: high
triggers: ["validate module", "check module", "module validation", "!validate"]
dependencies: ["meta/module-creation-guide.md", "core/loader.md"]
conflicts: []
version: 1.0.0
---

# Module Validation Guide

## Purpose
Define the 4-level validation process for ensuring module quality, correctness, and integration. This guide is used when creating new modules or reviewing existing ones.

## Validation Levels

### Level 1: Syntax Validation
Basic structural correctness

### Level 2: Semantic Validation
Logical consistency and completeness

### Level 3: Integration Validation
Proper system integration

### Level 4: Quality Validation
Best practices and maintainability

## Level 1: Syntax Validation

### YAML Frontmatter
```yaml
# Check for valid YAML syntax
---
name: [Required: non-empty string]
module_type: [Required: enum]
scope: [Required: enum]
priority: [Required: enum]
triggers: [Required: array of strings]
dependencies: [Required: array, can be empty]
conflicts: [Required: array, can be empty]
version: [Required: semver format]
---
```

### Validation Checks
- [ ] YAML parses without errors
- [ ] All required fields present
- [ ] Field types correct
- [ ] No unknown fields

### Common Syntax Errors
```yaml
# ❌ Invalid: Missing quotes in triggers
triggers: [test, TDD, coverage]

# ✅ Valid: Properly quoted
triggers: ["test", "TDD", "coverage"]

# ❌ Invalid: Wrong field type
dependencies: "core/principles.md"

# ✅ Valid: Array format
dependencies: ["core/principles.md"]
```

## Level 2: Semantic Validation

### Field Value Validation

#### module_type
Valid values:
- `process` - Step-by-step procedures
- `workflow` - Process orchestration
- `pattern` - Development methodology
- `guide` - Reference documentation
- `meta` - System management

#### scope
Valid values:
- `persistent` - Always loaded
- `context` - Context-based loading
- `temporary` - Task-specific loading
- `locked` - Manual control only

#### priority
Valid values:
- `critical` (1000)
- `highest` (900)
- `high` (700)
- `medium` (500)
- `low` (300)

### Logical Consistency Checks
- [ ] Module type matches content structure
- [ ] Scope appropriate for module purpose
- [ ] Priority aligns with importance
- [ ] Triggers relevant to module function

### Content Structure Validation

#### For Process Modules
Required sections:
- [ ] Purpose
- [ ] Trigger
- [ ] Process Steps
- [ ] Output
- [ ] Integration Points

#### For Workflow Modules
Required sections:
- [ ] Purpose
- [ ] Trigger
- [ ] Workflow Steps
- [ ] Decision Points
- [ ] Success Criteria

#### For Pattern Modules
Required sections:
- [ ] Purpose
- [ ] Core Principles
- [ ] Implementation Rules
- [ ] When to Apply
- [ ] Anti-Patterns

## Level 3: Integration Validation

### Dependency Validation
```python
# Pseudo-code for dependency checking
for dep in module.dependencies:
    if not exists(dep):
        error(f"Dependency not found: {dep}")
    if creates_circular_dependency(module, dep):
        error(f"Circular dependency detected: {dep}")
```

Checks:
- [ ] All dependencies exist
- [ ] No circular dependencies
- [ ] Dependencies loaded before module
- [ ] Dependency scopes compatible

### Conflict Validation
```python
# Pseudo-code for conflict checking
for conflict in module.conflicts:
    if not exists(conflict):
        warning(f"Conflicting module not found: {conflict}")
    if conflict in module.dependencies:
        error("Module conflicts with its dependency")
```

Checks:
- [ ] Conflicting modules exist
- [ ] No dependency-conflict overlap
- [ ] Conflict resolution documented
- [ ] Mutual conflicts declared

### Trigger Validation
- [ ] No duplicate triggers across persistent modules
- [ ] Triggers don't overlap with commands
- [ ] Context triggers properly categorized
- [ ] Trigger specificity appropriate

### Path Validation
- [ ] File path matches module location
- [ ] Category directory appropriate
- [ ] Naming conventions followed

## Level 4: Quality Validation

### Documentation Quality
- [ ] Purpose clear and concise
- [ ] All sections complete
- [ ] Examples provided
- [ ] Troubleshooting included

### Code Quality
```markdown
# Check for:
- [ ] Consistent formatting
- [ ] Clear variable placeholders (${var})
- [ ] Proper command syntax
- [ ] Error handling documented
```

### Best Practices
- [ ] Single Responsibility Principle
- [ ] No redundant functionality
- [ ] Clear integration points
- [ ] Appropriate granularity

### Maintainability
- [ ] Self-contained documentation
- [ ] Version appropriate
- [ ] Update implications clear
- [ ] Migration path for deprecation

## Validation Process

### Manual Validation
```bash
# 1. Syntax check
cat module.md | head -20  # Check frontmatter

# 2. Load test
!load path/to/module.md
!list-modules  # Verify loaded

# 3. Trigger test
[use trigger phrase]  # Verify auto-load

# 4. Integration test
!load dependencies  # Should auto-load
!load conflicts  # Should warn
```

### Automated Validation Script
```python
#!/usr/bin/env python3
"""Module validation script"""

import yaml
import os
import sys

def validate_module(filepath):
    """Validate a module file"""
    errors = []
    warnings = []
    
    # Level 1: Syntax
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            # Extract frontmatter
            if content.startswith('---'):
                fm_end = content.find('---', 3)
                frontmatter = yaml.safe_load(content[3:fm_end])
            else:
                errors.append("No frontmatter found")
                return errors, warnings
    except Exception as e:
        errors.append(f"YAML parse error: {e}")
        return errors, warnings
    
    # Level 2: Semantic
    required_fields = ['name', 'module_type', 'scope', 
                      'priority', 'triggers', 'dependencies', 
                      'conflicts', 'version']
    
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")
    
    # Level 3: Integration
    if 'dependencies' in frontmatter:
        for dep in frontmatter['dependencies']:
            if not os.path.exists(dep):
                warnings.append(f"Dependency not found: {dep}")
    
    # Level 4: Quality
    if len(content) < 500:
        warnings.append("Module seems too short")
    
    return errors, warnings

# Run validation
if __name__ == "__main__":
    errors, warnings = validate_module(sys.argv[1])
    
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ❌ {e}")
    
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ⚠️  {w}")
    
    if not errors and not warnings:
        print("✅ Module validation passed!")
```

## Validation Report Template

```markdown
### Module Validation Report

**Module**: [module path]
**Date**: [timestamp]
**Validator**: [human/automated]

#### Level 1: Syntax ✅/❌
- [ ] YAML valid
- [ ] Required fields present
- [ ] Field types correct

#### Level 2: Semantic ✅/❌
- [ ] Values valid
- [ ] Structure appropriate
- [ ] Content complete

#### Level 3: Integration ✅/❌
- [ ] Dependencies valid
- [ ] No circular dependencies
- [ ] Conflicts documented
- [ ] Triggers unique

#### Level 4: Quality ✅/❌
- [ ] Well documented
- [ ] Examples included
- [ ] Maintainable
- [ ] Follows best practices

**Issues Found**:
1. [Issue description]
2. [Issue description]

**Recommendations**:
- [Improvement suggestion]
- [Improvement suggestion]

**Status**: PASSED/FAILED
```

## Common Validation Failures

### Syntax Failures
1. **Invalid YAML**
   - Missing quotes
   - Wrong indentation
   - Invalid characters

2. **Missing Fields**
   - Forgot version
   - Empty triggers
   - No dependencies field

### Semantic Failures
1. **Type Mismatches**
   - Process module with workflow content
   - Guide module with process steps

2. **Scope Issues**
   - Temporary module with critical priority
   - Context module that should be persistent

### Integration Failures
1. **Dependency Issues**
   - Non-existent dependencies
   - Circular dependency chains
   - Version conflicts

2. **Trigger Conflicts**
   - Duplicate triggers
   - Too generic triggers
   - Command conflicts

### Quality Failures
1. **Poor Documentation**
   - Vague purpose
   - Missing examples
   - No troubleshooting

2. **Maintainability**
   - Too complex
   - Unclear integration
   - No update path

## Validation Enforcement

### Pre-Commit Validation
- Run syntax validation
- Check basic semantic rules
- Prevent invalid modules

### Load-Time Validation
- Full validation before loading
- Warning for quality issues
- Error for critical issues

### Periodic Review
- Monthly quality reviews
- Usage analysis
- Deprecation planning

---
*Rigorous validation ensures the module system remains reliable, maintainable, and effective.*