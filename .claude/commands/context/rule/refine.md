---
description: Refine a rule based on review feedback
argument-hint: <rule-path>
allowed-tools: Read, Write, Edit, AskUserQuestion
---

# Refine Rule

Improve a rule file based on review findings or user feedback.

## Arguments

- `$1` - Path to rule file (required)

## Workflow

### Step 1: Load and Analyze

1. Read rule file
2. Run quick review to identify issues
3. Present findings to user

### Step 2: Gather Feedback

Use AskUserQuestion:

1. Which issues to address?
2. Any clarifications needed?
3. Should scope be adjusted?

### Step 3: Apply Refinements

Common refinements:

- Clarify ambiguous language
- Add missing examples
- Define scope more precisely
- Add rationale section
- Remove redundancy

### Step 4: Validate

1. Re-run review checks
2. Verify rule is still coherent
3. Check for conflicts with other rules

### Step 5: Report

```text
## Rule Refined

| Field | Value |
|-------|-------|
| Rule | <name> |
| Changes | N |

**Modifications:**
- <change 1>
- <change 2>

Run `/context:rule:review` to verify.
```

## Examples

```bash
/context:rule:refine .claude/rules/commit-conventions.md
```

## Related Commands

- `/context:rule:review` - Review rule quality
- `/context:rule:create` - Create new rule
