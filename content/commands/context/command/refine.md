---
description: Refine a command based on review feedback
argument-hint: <command-path>
allowed-tools: Read, Write, Edit, AskUserQuestion
---

# Refine Command

Improve a slash command based on review findings or user feedback.

## Arguments

- `$1` - Path to command file (required)

## Workflow

### Step 1: Load and Analyze

1. Read command file
2. Run quick review to identify issues
3. Present findings to user

### Step 2: Gather Feedback

Use AskUserQuestion:

1. Which issues to address?
2. Any additional changes needed?

### Step 3: Apply Refinements

Common refinements:

- Improve description clarity
- Add missing sections
- Convert to imperative form
- Add error handling
- Include more examples
- Reduce complexity

### Step 4: Validate

1. Re-run review checks
2. Verify frontmatter is valid YAML
3. Confirm no regressions

### Step 5: Report

```text
## Command Refined

| Field | Value |
|-------|-------|
| Command | <name> |
| Changes | N |

**Modifications:**
- <change 1>
- <change 2>

Run `/context:command:review` to verify.
```

## Examples

```bash
/context:command:refine .claude/commands/deploy-staging.md
```

## Related Commands

- `/context:command:review` - Review command quality
- `/context:command:create` - Create new command
