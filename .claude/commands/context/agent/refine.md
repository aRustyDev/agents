---
description: Refine an agent definition based on review feedback
argument-hint: <agent-path>
allowed-tools: Read, Write, Edit, AskUserQuestion
---

# Refine Agent

Improve an agent definition based on review findings or user feedback.

## Arguments

- `$1` - Path to agent file (required)

## Workflow

### Step 1: Load and Analyze

1. Read agent file
2. Run quick review to identify issues
3. Present findings to user

### Step 2: Gather Feedback

Use AskUserQuestion:

1. Which issues to address?
2. Any additional changes needed?

### Step 3: Apply Refinements

Common refinements:

- Add missing sections
- Adjust model assignments
- Reduce tool scope
- Clarify workflow steps
- Add error handling
- Include examples

### Step 4: Validate

1. Re-run review checks
2. Verify structure is valid
3. Confirm no regressions

### Step 5: Report

```text
## Agent Refined

| Field | Value |
|-------|-------|
| Agent | <name> |
| Changes | N |

**Modifications:**
- <change 1>
- <change 2>

Run `/context:agent:review` to verify.
```

## Examples

```bash
/context:agent:refine .claude/agents/code-reviewer.md
```

## Related Commands

- `/context:agent:review` - Review agent quality
- `/context:agent:create` - Create new agent
