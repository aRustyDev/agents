---
module: ProcessDetection  
scope: context
triggers: 
  - "process detection"
  - "reusability check"
  - "find existing process"
conflicts: []
dependencies:
  - processes/meta/determine-prompt-reusability.md
priority: high
---

# ProcessDetection - Reusable Process Discovery

## Purpose
Detect and suggest reusable processes from existing modules before creating custom implementations.

## Overview
This module implements the process detection and analysis phase for command creation, ensuring maximum reusability by finding and adapting existing processes.

## Process Scanning

1. **Analyze description keywords** to identify potential process matches
2. **Search ~/.claude/** for relevant modules:
   - **processes/** - Step-by-step procedures
   - **patterns/** - Development patterns
   - **workflows/** - Complex workflows
   - **templates/** - Reusable structures
   - **guides/** - How-to documentation

## Process Matching Algorithm

For each potential match:

1. Calculate relevance score based on:
   - Keyword overlap
   - Workflow similarity
   - Input/output compatibility
   - Tool requirements alignment

2. Present high-confidence matches:
   ```
   Found potential process match:
   - Process: [process-name]
   - Relevance: [score]%
   - Description: [what it does]
   - Key features: [list]
   ```

3. Ask for confirmation:
   "Would you like to use the existing [process-name] process for [specific functionality]?
   
   Benefits of reusing:
   - Consistent behavior across commands
   - Well-tested implementation
   - Automatic updates when process improves
   
   [View process details] [Use this process] [Create custom instead]"

## Conflict Detection

If choosing to use existing process:

1. **Identify conflicts** between desired behavior and existing process
2. **Present each conflict** for resolution:
   ```
   Conflict detected:
   - You described: [user's description]
   - Process does: [existing behavior]
   
   How would you like to resolve this?
   1. Use existing behavior
   2. Create command-specific override
   3. Propose change to shared process
   ```

## Missing Feature Detection

Identify features you want that aren't in the shared process:

1. **List missing capabilities**
2. **For each missing feature, ask**:
   ```
   The [process-name] process doesn't include [feature].
   
   Would you like to:
   1. Add this to the shared process (benefits all commands)
   2. Create a conditional extension (only your command uses it)
   3. Implement separately in your command
   4. Skip this feature
   
   If adding to shared process:
   - Should this be always active?
   - Or activated by a flag/condition?
   ```

## Reusability Scoring

Calculate and track reusability metrics:
- Percentage of functionality from existing processes
- Number of custom implementations avoided
- Consistency score across commands

## Integration with Command Creation

This module integrates with the command creation workflow:
1. Called after goal discovery
2. Before requirements gathering
3. Influences solution design
4. Documented in final implementation

## Best Practices

1. **Always search thoroughly** - Cast a wide net for potential matches
2. **Prefer adaptation over duplication** - Modify existing processes when possible
3. **Document decisions** - Record why processes were or weren't reused
4. **Think long-term** - Consider future commands that might benefit

## Process Extension Patterns

### Unconditional Extension
When a feature benefits all users of a process:
```yaml
extends: processes/testing/unit-test-runner
additions:
  - feature: parallel-execution
    always_active: true
    implementation: "Use pytest-xdist by default"
```

### Conditional Extension
When a feature is context-specific:
```yaml
extends: processes/testing/unit-test-runner
additions:
  - feature: coverage-report
    condition: "--coverage flag provided"
    implementation: "Generate HTML coverage report"
```

## Related Modules
- `init.md` - Uses this for command creation
- `update.md` - Uses this for enhancement checks
- `processes/meta/determine-prompt-reusability.md` - Core reusability logic