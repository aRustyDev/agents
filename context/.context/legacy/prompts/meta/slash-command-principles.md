---
name: slash-command-principles
type: meta
description: Core principles and patterns for implementing, refactoring, extending, or fixing slash commands
author: Claude Code
version: 1.0.0
dependencies:
  - processes/meta/determine-prompt-reusability.md
scope: persistent
priority: high
triggers:
  - "implement slash command"
  - "create command"
  - "refactor command"
  - "extend command"
  - "fix command"
---

# Slash Command Implementation Principles

This meta module defines the core principles and patterns to follow when implementing, refactoring, extending, or fixing slash commands. The primary goal is to maximize reusability of existing prompts and maintain consistency across the command ecosystem.

## Core Principle: Prompt Reusability First

Before creating new functionality, ALWAYS search for and evaluate existing prompts that may satisfy the requirements. This promotes consistency, reduces duplication, and leverages tested solutions.

### Search Order for Reusable Prompts

1. **patterns/** - Development and architecture patterns
2. **processes/** - Step-by-step procedures and workflows
3. **templates/** - Reusable document and code templates
4. **workflows/** - Complex multi-step workflows
5. **guides/** - How-to guides and best practices
6. **roles/** - Role-based expertise modules (when available)

## Process Integration

Load the shared process for evaluating prompt reusability:
```
!load processes/meta/determine-prompt-reusability.md
```

This process provides detailed criteria for:
- Determining if a prompt is fully reusable
- Identifying prompts that need modification
- Deciding between conditional vs unconditional extensions

## Implementation Principles

### 1. Discovery Before Creation
- **ALWAYS** search existing modules before implementing new functionality
- Use keyword matching and semantic analysis
- Consider partial matches that could be extended

### 2. Composition Over Duplication
- Prefer composing multiple existing prompts over creating monolithic new ones
- Use process chaining and module dependencies
- Document integration points clearly

### 3. Extension Patterns

#### Unconditional Extensions
Use when the enhancement benefits ALL users of the prompt:
```yaml
extends: processes/version-control/commit-standards.md
additions:
  - feature: "emoji-prefix"
    rationale: "Improves readability for all users"
    implementation: "Add emoji based on commit type"
```

#### Conditional Extensions
Use when the enhancement is specific to certain contexts:
```yaml
extends: processes/testing/tdd-pattern.md
conditional_additions:
  - feature: "parallel-execution"
    condition: "flag:--parallel OR env:CI=true"
    rationale: "Only beneficial in CI or when explicitly requested"
    implementation: "Use pytest-xdist for parallel test execution"
```

### 4. Conflict Resolution
When existing prompts conflict with requirements:

1. **Evaluate criticality** - Is the conflict fundamental or cosmetic?
2. **Consider alternatives**:
   - Can the requirement be adjusted?
   - Can the prompt be parameterized?
   - Is a conditional branch appropriate?
3. **Document decisions** - Record why conflicts were resolved as they were

### 5. Documentation Standards

Every slash command MUST include:

#### Reusability Declaration
```yaml
# Process Dependencies
reuses:
  - module: patterns/development/tdd-pattern.md
    usage: "Core development workflow"
    modifications: none
    
  - module: processes/version-control/commit-standards.md
    usage: "Standardized commit creation"
    modifications:
      - type: conditional
        feature: "custom-format"
        condition: "when --format flag provided"
```

#### Extension Documentation
```markdown
## Extensions to Shared Processes

### TDD Pattern Extensions
This command extends the standard TDD pattern with:
- **Parallel test execution** (conditional: --parallel flag)
- **Coverage reporting** (unconditional: always enabled)

See: ~/.claude/processes/testing/tdd-pattern.md
```

### 6. Search Strategies

#### Keyword-Based Search
```bash
# Search for relevant patterns
grep -r "commit\|version\|git" ~/.claude/patterns/
grep -r "test\|tdd\|coverage" ~/.claude/processes/

# Search for specific functionality
rg "parallel.*test" ~/.claude/
```

#### Semantic Search
Consider semantic relationships:
- "create PR" → search for "pull request", "merge request", "code review"
- "run checks" → search for "validation", "testing", "quality", "lint"

### 7. Modification Decision Tree

```
Found relevant prompt?
├─ Yes
│  ├─ Covers all requirements?
│  │  ├─ Yes → Reuse as-is
│  │  └─ No
│  │     ├─ Missing features benefit everyone?
│  │     │  ├─ Yes → Unconditional extension
│  │     │  └─ No → Conditional extension
│  │     └─ Conflicts with requirements?
│  │        ├─ Minor → Document override
│  │        └─ Major → Create new with composition
└─ No → Search related terms
   └─ Still no? → Create new (last resort)
```

## Best Practices

### 1. Prompt Discovery Documentation
Always document your search process:
```markdown
## Reusability Analysis
Searched for: "git commit", "version control", "conventional commits"
Found: processes/version-control/commit-standards.md
Coverage: 85% of requirements
Missing: Custom emoji prefixes
Decision: Conditional extension for emoji feature
```

### 2. Extension Impact Analysis
Before extending a shared prompt:
- Count how many commands use it
- Evaluate if the extension helps or hinders other uses
- Consider creating a variant instead of modifying

### 3. Deprecation Handling
When refactoring:
- Check all commands that depend on the prompt
- Provide migration path for breaking changes
- Use semantic versioning for prompts

### 4. Testing Reused Prompts
- Test the command with the base prompt
- Test with your extensions
- Test interaction between multiple reused prompts
- Verify conditional logic works correctly

## Anti-Patterns to Avoid

### 1. Hidden Duplication
❌ Copying prompt content instead of referencing
✅ Using `!load` or proper module dependencies

### 2. Over-Specialization
❌ Creating command-specific versions of general processes
✅ Using conditional extensions for specific needs

### 3. Unclear Dependencies
❌ Using prompts without documenting the dependency
✅ Explicitly listing all reused modules with versions

### 4. Breaking Composition
❌ Modifying shared prompts in ways that break other users
✅ Using extensions that preserve backward compatibility

## Integration with command management

The `/project:command` slash command (v3.0.0) implements these principles through:
- `init` subcommand: Process Detection & Analysis during command creation
- `update` subcommand: Reusability check when enhancing commands
- `review` subcommand: Principles alignment analysis
- Automatic search of ~/.claude/ directories
- Interactive conflict resolution
- Clear documentation of reused processes

## Metrics for Success

A well-implemented command should:
- Reuse 60-80% of functionality from existing prompts
- Have clear documentation of all dependencies
- Use conditional extensions for command-specific features
- Maintain compatibility with shared prompt updates

## Module Evolution

As the system grows:
1. Extract common patterns into shared processes
2. Promote successful extensions to core features
3. Deprecate redundant command-specific implementations
4. Maintain a balance between reusability and specificity

---

Remember: The goal is not just to make commands work, but to build a coherent, maintainable ecosystem where improvements to shared prompts benefit all commands that use them.