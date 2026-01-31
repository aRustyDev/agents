---
name: command
description: Comprehensive slash command management tool for creating, updating, and reviewing commands
author: Claude Code
version: 3.1.0
dependencies:
  - meta/slash-command-principles.md
  - processes/meta/determine-prompt-reusability.md
modules:
  - command/init.md
  - command/update.md
  - command/review.md
  - command/process-detection.md
  - command/_shared.md
---

# Command - Slash Command Management Suite

I'll help you create, update, or review slash commands with a focus on reusability, consistency, and alignment with command principles.

## Usage

```
/project:command [init|update|review]
```

## Architecture

This command is implemented as a modular system with specialized modules for each subcommand:

### Core Modules

1. **`init.md`** - Create New Command
   - Interactive command creation with comprehensive requirements analysis
   - Process detection and template generation
   - Handles `/project:command init`

2. **`update.md`** - Enhance Existing Command  
   - Add features or modify functionality while maintaining consistency
   - Preserves backward compatibility
   - Handles `/project:command update`

3. **`review.md`** - Analyze Command Quality
   - Critical analysis of command implementation
   - Reusability assessment and principle alignment
   - Handles `/project:command review`

### Shared Modules

4. **`process-detection.md`** - Process Discovery
   - Reusable process detection logic
   - Maps user goals to existing processes
   - Used by multiple subcommands

5. **`_shared.md`** - Common Utilities
   - Shared patterns and utilities
   - Validation functions
   - Template helpers

## Module Loading

Based on the subcommand used, the appropriate module is loaded:

```yaml
subcommand_mapping:
  init: command/init.md
  update: command/update.md
  review: command/review.md
  default: command/init.md
```

All modules have access to shared utilities via `_shared.md`.

---

## Subcommand: init

When you use `/project:command init`, I'll guide you through creating a new slash command.

### Phase 1: Goal Discovery 🎯

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

### Phase 2: Process Detection & Analysis 🔍

Before gathering new requirements, I'll analyze if any existing processes match your needs:

#### Process Scanning
1. **Analyze description keywords** to identify potential process matches
2. **Search ~/.claude/** for relevant modules:
   - **processes/** - Step-by-step procedures
   - **patterns/** - Development patterns
   - **workflows/** - Complex workflows
   - **templates/** - Reusable structures
   - **guides/** - How-to documentation

#### Process Matching Algorithm
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

#### Conflict Detection
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

#### Missing Feature Detection
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

### Phase 3: Requirements Gathering 📋

Based on the goal and process analysis, I'll generate comprehensive requirements:

#### Functional Requirements
- What specific actions must the command perform?
- What are the core features vs nice-to-haves?
- What's the expected workflow from start to finish?

#### Input/Output Requirements
- What information does the command need from the user?
- What format should inputs be in?
- What outputs will be generated?
- How should results be presented?

#### Integration Requirements
- What existing tools or systems will this interact with?
- Are there API dependencies?
- What file formats need support?

#### Error Handling Requirements
- What could go wrong?
- How should errors be communicated?
- What recovery options exist?

#### Performance Requirements
- Expected response time?
- Data volume considerations?
- Concurrent usage needs?

#### Security Requirements
- Authentication needs?
- Data sensitivity?
- Access control requirements?

### Phase 4: Deep Analysis 🔬

#### Step-by-Step Workflow Analysis
I'll think through the entire process:
1. Map each step from invocation to completion
2. Identify decision points
3. Consider alternative paths
4. Plan error recovery

#### Edge Case Identification
- What happens with empty inputs?
- How to handle very large datasets?
- What about network failures?
- How to manage partial completions?

#### Exceeding Expectations
Ways to make the command exceptional:
- **Automation**: What repetitive tasks can be eliminated?
- **Intelligence**: Can the command learn or adapt?
- **Performance**: How to make it fast and efficient?
- **User Experience**: How to make it delightful to use?
- **Robustness**: How to handle edge cases gracefully?

### Phase 5: Solution Design 📐

#### Process Integration Design
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

### Phase 6: Implementation

The final command will be created with:
- Clear documentation of all reused processes
- Proper conditional gates for extensions
- Comprehensive error handling
- Alignment with slash command principles

---

## Subcommand: update

When you use `/project:command update`, I'll help you enhance an existing command.

### Phase 1: Command Analysis 📊

1. **Identify the command**: "Which command would you like to update?"
2. **Read current implementation**: Load and analyze the existing command
3. **Understand current functionality**: Map what it currently does

### Phase 2: Enhancement Discovery 🔍

1. **Understand the need**: "What feature or change would you like to add?"
2. **Clarify requirements**:
   - Is this fixing a problem or adding new capability?
   - Who needs this enhancement?
   - What's the expected behavior?

### Phase 3: Reusability Check ♻️

Following the slash command principles:

1. **Search for existing solutions**:
   ```
   !load processes/meta/determine-prompt-reusability.md
   ```
   - Can any existing process provide this feature?
   - Are there patterns we can compose?

2. **Evaluate extension options**:
   - **Unconditional**: If the feature benefits all users
   - **Conditional**: If it's context-specific

### Phase 4: Impact Analysis 📈

1. **Backward compatibility**: Will existing users be affected?
2. **Performance impact**: Does this add overhead?
3. **Dependency changes**: New requirements or tools?
4. **Documentation needs**: What needs updating?

### Phase 5: Implementation Plan 📝

1. **Minimal changes approach**: Modify only what's necessary
2. **Preserve existing patterns**: Maintain consistency
3. **Add proper gates**: For conditional features
4. **Update documentation**: Reflect all changes

### Phase 6: Update Execution 🛠️

I'll help you:
1. Add the new functionality
2. Update process dependencies
3. Document the enhancement
4. Ensure backward compatibility
5. Update version number

---

## Subcommand: review

When you use `/project:command review`, I'll analyze a command's implementation quality.

### Phase 1: Command Loading 📂

1. **Identify the command**: "Which command would you like me to review?"
2. **Load implementation**: Read the complete command file
3. **Load dependencies**: Identify all referenced processes

### Phase 2: Principles Alignment Check ✅

Evaluate against slash command principles:

1. **Reusability First**:
   - Does it search for existing processes?
   - Are common patterns properly reused?
   - Is there unnecessary duplication?

2. **Composition Over Duplication**:
   - Are processes properly composed?
   - Is there monolithic code that could be modularized?

3. **Documentation Standards**:
   - Are all dependencies documented?
   - Are modifications clearly explained?
   - Is the purpose well-defined?

### Phase 3: Implementation Analysis 🔬

1. **Process Reuse Assessment**:
   ```
   Reusability Score: X%
   - Reused processes: [list]
   - Custom implementations: [list]
   - Opportunities for reuse: [list]
   ```

2. **Anti-Pattern Detection**:
   - ❌ Hidden duplication
   - ❌ Over-specialization
   - ❌ Unclear dependencies
   - ❌ Breaking composition

3. **Extension Pattern Review**:
   - Are conditional extensions used appropriately?
   - Are unconditional extensions justified?
   - Is the modification decision tree followed?

### Phase 4: Logical Analysis 🧩

1. **Completeness Check**:
   - Are all promised features implemented?
   - Is error handling comprehensive?
   - Are edge cases considered?

2. **Consistency Review**:
   - Does the command follow established patterns?
   - Is the code style consistent?
   - Are naming conventions followed?

3. **Flow Analysis**:
   - Is the workflow logical?
   - Are there unnecessary steps?
   - Could the process be optimized?

### Phase 5: Improvement Recommendations 💡

I'll provide:

1. **Critical Issues** (Must Fix):
   - Security vulnerabilities
   - Breaking changes
   - Logic errors

2. **Major Improvements** (Should Fix):
   - Reusability opportunities
   - Performance optimizations
   - Better error handling

3. **Minor Enhancements** (Could Fix):
   - Documentation improvements
   - Code style adjustments
   - Nice-to-have features

### Phase 6: Reusability Opportunities 🔄

Identify code that could be:
1. **Extracted to shared processes**
2. **Replaced with existing processes**
3. **Composed from multiple processes**
4. **Parameterized for broader use**

### Review Report Format

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

---

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

### Success Metrics

A well-implemented command should:
- Reuse 60-80% functionality from existing prompts
- Have clear documentation of all dependencies
- Use conditional extensions for command-specific features
- Score 8+ on review analysis

---

Remember: The goal is to build a coherent, maintainable ecosystem where improvements to shared prompts benefit all commands that use them.