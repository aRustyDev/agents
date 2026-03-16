---
description: Review a command for quality, structure, and best practices
argument-hint: <command-path>
allowed-tools: Read, Glob, Grep, Bash(wc:*)
---

# Review Command

Analyze a slash command for quality, structure, and adherence to best practices.

## Arguments

- `$1` - Path to command file (required)

## Workflow

### Step 1: Load Command

1. Read command file at `$1`
2. Parse YAML frontmatter
3. Parse markdown content

### Step 2: Frontmatter Analysis

| Field | Required | Status |
|-------|----------|--------|
| description | Yes | |
| argument-hint | If args | |
| allowed-tools | Optional | |
| model | Optional | |

Check:

- [ ] Description under 100 characters
- [ ] Description is actionable (starts with verb)
- [ ] argument-hint matches documented arguments
- [ ] allowed-tools list is minimal

### Step 3: Content Analysis

Check:

- [ ] Has Arguments section (if applicable)
- [ ] Has Workflow section with numbered steps
- [ ] Has Examples section
- [ ] Steps use imperative form ("Read the file", not "Reading the file")
- [ ] No placeholder text (TODO, TBD, FIXME)
- [ ] Error handling documented

### Step 4: Complexity Check

| Metric | Threshold | Status |
|--------|-----------|--------|
| Lines | < 300 | |
| Steps | < 10 | |
| Arguments | < 5 | |

Flag if too complex — may need to split into multiple commands.

### Step 5: Generate Report

```markdown
# Command Review: <command-name>

## Summary

| Metric | Status |
|--------|--------|
| Frontmatter | ✅/⚠️/❌ |
| Structure | ✅/⚠️/❌ |
| Clarity | ✅/⚠️/❌ |
| Complexity | ✅/⚠️/❌ |

## Findings

### Critical

- <issues>

### Warnings

- <issues>

### Suggestions

- <improvements>

## Recommendation

<Ready | Needs Revision>
```

## Examples

```bash
/context:command:review .claude/commands/deploy-staging.md
/context:command:review context/commands/create-formula.md
```

## Related Commands

- `/context:command:create` - Create new command
- `/context:command:refine` - Apply improvements
