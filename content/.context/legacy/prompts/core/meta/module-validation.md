---
module: ModuleValidation
scope: persistent
triggers: ["validate module", "check module", "module validation", "test module"]
conflicts: []
dependencies: ["module-interface"]
priority: high
---

# Module Validation Process

## Purpose
Ensure modules are correctly structured, internally consistent, and integrate properly with the modular system before deployment.

## When to Validate
Execute validation:
- After creating a new module
- Before committing module changes
- When debugging module loading issues
- During periodic system health checks
- When modules interact unexpectedly

## Validation Levels

### Level 1: Structural Validation (Syntax)
Verifies the module follows required format and contains necessary elements.

### Level 2: Semantic Validation (Meaning)
Ensures content makes sense and is internally consistent.

### Level 3: Integration Validation (System)
Confirms module works correctly with other modules.

### Level 4: Behavioral Validation (Runtime)
Tests module performs as expected when loaded and used.

## Validation Process

### Step 1: Structural Validation
```
1.1 Verify YAML frontmatter:
    - Exists at start of file
    - Valid YAML syntax
    - Contains all required fields:
      * module (PascalCase string)
      * scope (valid scope value)
      * triggers (array of strings)
      * conflicts (array, can be empty)
      * dependencies (array, can be empty)
      * priority (low|medium|high)

1.2 Check markdown structure:
    - Has # Title matching module name
    - Contains ## Purpose section
    - Includes required sections for module type
    - Uses consistent heading hierarchy

1.3 Validate formatting:
    - Code blocks properly fenced
    - Lists consistently formatted
    - Variables use ${variable} syntax
    - Cross-references use correct format
```

### Step 2: Semantic Validation
```
2.1 Validate scope appropriateness:
    - Tool guides → temporary
    - Core processes → persistent
    - Workflows → context or persistent
    - Security rules → locked

2.2 Check trigger quality:
    - Triggers are specific enough
    - No overly broad triggers
    - Triggers match module purpose
    - No duplicate triggers across modules

2.3 Verify content completeness:
    - All steps are actionable
    - Examples are practical
    - No placeholder content
    - No broken references

2.4 Assess clarity:
    - Purpose is clear in 1-2 sentences
    - Steps follow logical order
    - Technical terms explained
    - Ambiguity eliminated
```

### Step 3: Integration Validation
```
3.1 Dependency check:
    - All dependencies exist
    - No circular dependencies
    - Dependencies load in correct order
    - Dependency scopes compatible

3.2 Conflict analysis:
    - Declared conflicts are bidirectional
    - Conflicting modules truly incompatible
    - No hidden conflicts (same triggers)

3.3 Cross-reference validation:
    - All referenced modules exist
    - References use correct syntax
    - Referenced sections exist
    - No orphaned references

3.4 Scope compatibility:
    - Module scope matches usage patterns
    - Dependencies have compatible scopes
    - No temporary module depends on context
```

### Step 4: Behavioral Validation
```
4.1 Load testing:
    - Module loads without errors
    - Triggers activate module correctly
    - Module unloads cleanly
    - Scope rules respected

4.2 Interaction testing:
    - Works with dependent modules
    - Conflicts prevent dual loading
    - Handoffs between modules smooth
    - No memory leaks

4.3 Edge case testing:
    - Handles missing dependencies gracefully
    - Works with partial loading
    - Recovers from errors
    - Maintains state correctly
```

## Automated Validation Checks

### YAML Frontmatter Validator
```python
# Pseudocode for validation logic
def validate_frontmatter(content):
    checks = {
        "has_frontmatter": "---" at start and end,
        "valid_yaml": parseable YAML syntax,
        "required_fields": all fields present,
        "valid_scope": scope in allowed values,
        "triggers_array": triggers is list,
        "priority_valid": priority in [low, medium, high]
    }
    return all(checks)
```

### Common Validation Errors

#### Error: Missing Required Field
```
❌ Problem: Frontmatter missing 'scope' field
✅ Solution: Add scope: persistent|context|temporary
```

#### Error: Circular Dependency
```
❌ Problem: Module A requires B, B requires A
✅ Solution: Extract shared functionality to Module C
```

#### Error: Overly Broad Trigger
```
❌ Problem: Trigger "code" matches too many contexts
✅ Solution: Use specific triggers like "review code"
```

#### Error: Scope Mismatch
```
❌ Problem: Temporary module depends on context module
✅ Solution: Adjust scopes or restructure dependencies
```

## Validation Report Format

After validation, generate a report:

```markdown
## Module Validation Report: [Module Name]

### Summary
- Status: PASS|FAIL|WARNING
- Date: [timestamp]
- Validator: ModuleValidation v1.0

### Level 1: Structure ✅|❌
- [ ] Valid YAML frontmatter
- [ ] Required fields present
- [ ] Proper markdown structure
- [ ] Consistent formatting

### Level 2: Semantics ✅|❌
- [ ] Appropriate scope
- [ ] Quality triggers
- [ ] Complete content
- [ ] Clear writing

### Level 3: Integration ✅|❌
- [ ] Dependencies exist
- [ ] No circular deps
- [ ] Valid references
- [ ] Compatible scopes

### Level 4: Behavior ✅|❌
- [ ] Loads correctly
- [ ] Interacts properly
- [ ] Handles errors
- [ ] Maintains state

### Issues Found
1. [Issue description and severity]
2. [Recommended fix]

### Recommendations
- [Improvement suggestion 1]
- [Improvement suggestion 2]
```

## Validation Workflow Integration

### Pre-commit Validation
Add to version control workflow:
```bash
# Run before committing modules
!validate ~/.claude/modules/new-module.md
```

### Batch Validation
Validate all modules periodically:
```bash
# Validate entire module directory
!validate ~/.claude/ --recursive
```

### Continuous Validation
During development:
```bash
# Watch mode for active development
!validate ~/.claude/modules/working.md --watch
```

## Quality Gates

Modules must pass these gates:

### Gate 1: Loadable
- Module can be loaded without errors
- Basic syntax is correct

### Gate 2: Functional
- Module performs its stated purpose
- All features work as documented

### Gate 3: Integrable
- Works with existing modules
- Doesn't break other functionality

### Gate 4: Maintainable
- Clear documentation
- Follows conventions
- Easy to modify

## Validation Best Practices

### Do's
- ✅ Validate early and often
- ✅ Fix issues immediately
- ✅ Test with real scenarios
- ✅ Document validation results
- ✅ Automate repeated checks

### Don'ts
- ❌ Skip validation for "simple" modules
- ❌ Ignore warnings
- ❌ Validate only structure
- ❌ Test in isolation only
- ❌ Assume dependencies exist

## Troubleshooting Validation Failures

### Module Won't Load
1. Check YAML syntax with online validator
2. Verify file encoding is UTF-8
3. Ensure no hidden characters
4. Validate markdown structure

### Dependencies Fail
1. List all module dependencies
2. Check each exists and loads
3. Verify scope compatibility
4. Test load order

### Triggers Don't Work
1. Check for typos in triggers
2. Verify no duplicate triggers
3. Test trigger in context
4. Review trigger specificity

### Integration Issues
1. Load modules individually first
2. Check for naming conflicts
3. Review cross-references
4. Test interaction scenarios

## Evolution and Feedback

The validation process should evolve based on:
- Common validation failures
- New module types
- System complexity growth
- User feedback

Track validation metrics to improve:
- Most common errors
- Time to validate
- False positive rate
- Module quality trends

Remember: Validation is not just about catching errors—it's about ensuring modules provide consistent, reliable functionality that enhances Claude's capabilities without introducing complexity or conflicts.
