---
module: CommandShared  
scope: context
triggers: []
conflicts: []
dependencies:
  - meta/slash-command-principles.md
  - processes/meta/determine-prompt-reusability.md
priority: high
---

# CommandShared - Common Utilities and Patterns

## Purpose
Shared utilities and validation for command management, ensuring consistency across all command subcommands.

## Overview
This module provides common functionality used by init, update, and review subcommands.

## Command Entry Point

The main `/project:command` entry handles routing to subcommands:

```
/project:command [init|update|review]
```

## Common Patterns and Best Practices

### For All Subcommands

1. **Always Check Reusability First**:
   ```
   !load processes/meta/determine-prompt-reusability.md
   ```

2. **Document Everything**:
   - Why decisions were made
   - What was reused
   - What was custom-built

3. **Think Modular**:
   - Small, composable pieces
   - Clear interfaces
   - Minimal dependencies

4. **Follow the Principles**:
   ```
   !load meta/slash-command-principles.md
   ```

## Success Metrics

A well-implemented command should:
- Reuse 60-80% functionality from existing prompts
- Have clear documentation of all dependencies
- Use conditional extensions for command-specific features
- Score 8+ on review analysis

## Common Validation Functions

### Command Name Validation
- Must start with letter
- Can contain letters, numbers, hyphens
- No spaces or special characters
- Maximum 30 characters

### Version Format Validation
- Follow semantic versioning (x.y.z)
- Major.Minor.Patch format
- Valid examples: 1.0.0, 2.1.3, 0.1.0

### Dependency Validation
- Check if referenced processes exist
- Verify version compatibility
- Detect circular dependencies

## Error Message Templates

### User-Friendly Errors
```
Error: [What went wrong]
Why: [Brief explanation]
Fix: [How to resolve]
```

### Examples
```
Error: Command name contains spaces
Why: Command names cannot have spaces
Fix: Use hyphens instead (e.g., "my-command")
```

## Process Reference Patterns

### Unconditional Process Usage
```yaml
processes:
  - name: process-name
    version: ">=1.0.0"
    usage: "Description of how it's used"
```

### Conditional Process Usage
```yaml
processes:
  - name: process-name
    version: ">=1.0.0"
    condition: "flag or condition"
    usage: "Used when condition is met"
```

### Process with Overrides
```yaml
processes:
  - name: process-name
    version: ">=1.0.0"
    overrides:
      - feature: "specific-feature"
        implementation: "Custom behavior"
```

## Integration Points

All command subcommands should:
1. Import this module for shared functionality
2. Use common validation functions
3. Follow error message templates
4. Apply consistent patterns

## Remember

The goal is to build a coherent, maintainable ecosystem where improvements to shared prompts benefit all commands that use them.

## Module Dependencies

This shared module is used by:
- `init.md` - Command creation
- `update.md` - Command enhancement
- `review.md` - Command analysis
- `.meta.md` - Directory routing