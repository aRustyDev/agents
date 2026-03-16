---
description: Refine a plugin based on review feedback
argument-hint: <plugin-path>
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion
---

# Refine Plugin

Improve a plugin based on review findings or user feedback.

## Arguments

- `$1` - Path to plugin directory (required)

## Workflow

### Step 1: Load and Analyze

1. Read plugin manifest
2. Run quick review to identify issues
3. Present findings to user

### Step 2: Gather Feedback

Use AskUserQuestion:

1. Which issues to address?
2. Priority order for fixes?
3. Any additional improvements?

### Step 3: Apply Refinements

Common refinements:

- Update manifest fields
- Add missing documentation
- Fix component issues
- Improve examples
- Update version

### Step 4: Validate

1. Re-run plugin review
2. Verify all components load
3. Check no regressions

### Step 5: Update Version

If significant changes, bump version:

- Patch (0.0.x): Bug fixes
- Minor (0.x.0): New features
- Major (x.0.0): Breaking changes

### Step 6: Report

```text
## Plugin Refined

| Field | Value |
|-------|-------|
| Plugin | <name> |
| Version | <old> → <new> |
| Changes | N |

**Modifications:**
- <change 1>
- <change 2>

Run `/context:plugin:review` to verify.
```

## Examples

```bash
/context:plugin:refine context/plugins/blog-workflow
```

## Related Commands

- `/context:plugin:review` - Review plugin quality
- `/context:plugin:create` - Create new plugin
