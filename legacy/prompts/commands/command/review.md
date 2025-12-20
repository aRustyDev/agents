---
module: CommandReview  
scope: context
triggers: 
  - "/command review"
  - "review command"
  - "analyze command"
conflicts: []
dependencies:
  - _shared.md
  - meta/slash-command-principles.md
priority: medium
---

# CommandReview - Analyze Command Quality

## Purpose
Analyze command quality and suggest improvements based on slash command principles and reusability standards.

## Overview
When you use `/project:command review`, I'll analyze a command's implementation quality, focusing on reusability, consistency, and alignment with principles.

## Phase 1: Command Loading 📂

1. **Identify the command**: "Which command would you like me to review?"
2. **Load implementation**: Read the complete command file
3. **Load dependencies**: Identify all referenced processes

### Initial Assessment
- Command structure and organization
- Metadata completeness
- Dependency declarations
- Version information

## Phase 2: Principles Alignment Check ✅

Evaluate against slash command principles:

### 1. Reusability First
- Does it search for existing processes?
- Are common patterns properly reused?
- Is there unnecessary duplication?

### 2. Composition Over Duplication
- Are processes properly composed?
- Is there monolithic code that could be modularized?

### 3. Documentation Standards
- Are all dependencies documented?
- Are modifications clearly explained?
- Is the purpose well-defined?

## Phase 3: Implementation Analysis 🔬

### Process Reuse Assessment
```
Reusability Score: X%
- Reused processes: [list]
- Custom implementations: [list]
- Opportunities for reuse: [list]
```

### Anti-Pattern Detection
- ❌ Hidden duplication
- ❌ Over-specialization
- ❌ Unclear dependencies
- ❌ Breaking composition

### Extension Pattern Review
- Are conditional extensions used appropriately?
- Are unconditional extensions justified?
- Is the modification decision tree followed?

## Phase 4: Logical Analysis 🧩

### Completeness Check
- Are all promised features implemented?
- Is error handling comprehensive?
- Are edge cases considered?

### Consistency Review
- Does the command follow established patterns?
- Is the code style consistent?
- Are naming conventions followed?

### Flow Analysis
- Is the workflow logical?
- Are there unnecessary steps?
- Could the process be optimized?

## Phase 5: Improvement Recommendations 💡

### Critical Issues (Must Fix)
- Security vulnerabilities
- Breaking changes
- Logic errors

### Major Improvements (Should Fix)
- Reusability opportunities
- Performance optimizations
- Better error handling

### Minor Enhancements (Could Fix)
- Documentation improvements
- Code style adjustments
- Nice-to-have features

## Phase 6: Reusability Opportunities 🔄

Identify code that could be:
1. **Extracted to shared processes**
2. **Replaced with existing processes**
3. **Composed from multiple processes**
4. **Parameterized for broader use**

## Review Report Format

```markdown
# Command Review: [command-name]

## Summary
- Overall Score: X/10
- Reusability: X%
- Principles Alignment: [Excellent/Good/Needs Work]

## Strengths
- [What the command does well]

## Critical Issues
- [Must-fix problems]

## Improvement Opportunities
1. [Specific recommendation]
2. [Another recommendation]

## Reusability Analysis
- Current reuse: X%
- Potential reuse: Y%
- Recommended extractions: [list]

## Next Steps
[Prioritized action items]
```

## Scoring Rubric

### Overall Score (out of 10)
- **Reusability** (3 points)
  - 3: >80% reused
  - 2: 60-80% reused
  - 1: 40-60% reused
  - 0: <40% reused

- **Documentation** (2 points)
  - 2: Comprehensive
  - 1: Adequate
  - 0: Insufficient

- **Code Quality** (2 points)
  - 2: Clean and consistent
  - 1: Minor issues
  - 0: Major issues

- **Error Handling** (2 points)
  - 2: Robust
  - 1: Basic
  - 0: Inadequate

- **Performance** (1 point)
  - 1: Optimized
  - 0: Needs work

## Best Practices for High Scores

1. **Maximize reuse**: Use existing processes wherever possible
2. **Document thoroughly**: Explain all decisions
3. **Handle errors gracefully**: Consider all failure modes
4. **Follow patterns**: Consistency is key
5. **Think modular**: Small, composable pieces

## Integration Guide

This module references:
- `_shared.md` for review criteria
- `meta/slash-command-principles.md` for standards
- Command files for analysis

## Related Modules
- `init.md` - For creating well-designed commands
- `update.md` - For implementing review recommendations
- `process-detection.md` - For finding reuse opportunities