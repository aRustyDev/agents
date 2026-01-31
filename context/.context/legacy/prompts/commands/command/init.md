---
module: CommandInit  
scope: context
triggers: 
  - "/command init"
  - "create command"
  - "new slash command"
conflicts: []
dependencies:
  - _shared.md
  - process-detection.md
  - meta/slash-command-principles.md
  - processes/meta/determine-prompt-reusability.md
priority: high
---

# CommandInit - Interactive Command Creation

## Purpose
Interactive command creation with comprehensive requirements analysis and process detection.

## Overview
When you use `/project:command init`, I'll guide you through creating a new slash command with a focus on reusability and alignment with command principles.

## Phase 1: Goal Discovery 🎯

First, I need to understand what you want to accomplish:

1. **Ask the primary question**: "What would you like your new command to accomplish?"
2. **Listen actively** to the response
3. **Ask follow-up questions** to understand:
   - The specific problem being solved
   - Who will use this command
   - How often it will be used
   - The expected outcome

### Clarifying Questions:
- Can you give me a specific example of when you'd use this command?
- What currently takes too much time or is error-prone?
- What would success look like for this command?

## Phase 2: Process Detection & Analysis 🔍

Before gathering new requirements, I'll analyze if any existing processes match your needs. This phase is handled by the `process-detection.md` module.

## Phase 3: Requirements Gathering 📋

Based on the goal and process analysis, I'll generate comprehensive requirements:

### Functional Requirements
- What specific actions must the command perform?
- What are the core features vs nice-to-haves?
- What's the expected workflow from start to finish?

### Input/Output Requirements
- What information does the command need from the user?
- What format should inputs be in?
- What outputs will be generated?
- How should results be presented?

### Integration Requirements
- What existing tools or systems will this interact with?
- Are there API dependencies?
- What file formats need support?

### Error Handling Requirements
- What could go wrong?
- How should errors be communicated?
- What recovery options exist?

### Performance Requirements
- Expected response time?
- Data volume considerations?
- Concurrent usage needs?

### Security Requirements
- Authentication needs?
- Data sensitivity?
- Access control requirements?

## Phase 4: Deep Analysis 🔬

### Step-by-Step Workflow Analysis
I'll think through the entire process:
1. Map each step from invocation to completion
2. Identify decision points
3. Consider alternative paths
4. Plan error recovery

### Edge Case Identification
- What happens with empty inputs?
- How to handle very large datasets?
- What about network failures?
- How to manage partial completions?

### Exceeding Expectations
Ways to make the command exceptional:
- **Automation**: What repetitive tasks can be eliminated?
- **Intelligence**: Can the command learn or adapt?
- **Performance**: How to make it fast and efficient?
- **User Experience**: How to make it delightful to use?
- **Robustness**: How to handle edge cases gracefully?

## Phase 5: Solution Design 📐

### Process Integration Design
```yaml
name: [command-name]
description: [clear, concise description]
author: [your name]
version: 1.0.0

# Process Dependencies
processes:
  - name: version-control/commit-standards
    version: ">=1.0.0"
    usage: "For creating standardized commits"
    overrides:
      - feature: "commit-message-format"
        condition: "when flag --custom-format is used"
        implementation: "Use user-provided format"
  
  - name: testing/tdd-pattern
    version: ">=1.0.0"
    usage: "For test-driven implementation"
    extensions:
      - feature: "parallel-test-execution"
        condition: "when flag --parallel is used"
        implementation: "Run tests in parallel using pytest-xdist"
```

## Phase 6: Implementation

The final command will be created with:
- Clear documentation of all reused processes
- Proper conditional gates for extensions
- Comprehensive error handling
- Alignment with slash command principles

## Integration Guide

This module works closely with:
- `process-detection.md` for finding reusable processes
- `_shared.md` for common utilities and principles
- `meta/slash-command-principles.md` for alignment checks

## Best Practices

1. Always prioritize reusability over custom implementation
2. Document all design decisions
3. Consider future extensibility
4. Follow the established command patterns

## Related Modules
- `update.md` - For enhancing existing commands
- `review.md` - For analyzing command quality
- `process-detection.md` - For process reuse analysis