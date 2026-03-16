---
description: Refine an MCP server configuration based on review
argument-hint: <config-path>
allowed-tools: Read, Write, Edit, AskUserQuestion
---

# Refine MCP Config

Improve an MCP server configuration based on review findings.

## Arguments

- `$1` - Path to MCP config file (required)

## Workflow

### Step 1: Load and Analyze

1. Read config file
2. Run quick review to identify issues
3. Present findings to user

### Step 2: Gather Feedback

Use AskUserQuestion:

1. Which issues to address?
2. Any env vars to externalize?
3. Should security warnings be fixed?

### Step 3: Apply Refinements

Common refinements:

- Move hardcoded values to env vars
- Add missing documentation comments
- Fix YAML formatting
- Add server descriptions

### Step 4: Validate

1. Re-run review checks
2. Verify YAML is valid
3. Test command still works

### Step 5: Report

```text
## MCP Config Refined

| Field | Value |
|-------|-------|
| Config | <name> |
| Changes | N |

**Modifications:**
- <change 1>
- <change 2>

Run `/context:mcp:review` to verify.
```

## Examples

```bash
/context:mcp:refine settings/mcp/github-tools.yaml
```

## Related Commands

- `/context:mcp:review` - Review config quality
- `/context:mcp:create` - Create new config
