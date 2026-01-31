---
module: ReportBug  
scope: context
triggers: 
  - "/report bug"
  - "bug report"
  - "report issue"
conflicts: []
dependencies:
  - _templates.md
  - _interactive.md
  - _bug_templates.md
priority: high
---

# ReportBug - Bug Report Creation

## Purpose
Report issues with system behavior, including execution errors, unexpected behavior, and performance problems.

## Overview
Create comprehensive bug reports with reproduction steps, environment details, and diagnostic information.

## Usage
```
/report bug [--quick] [--type <bug-type>] [--command <command-name>]
```

## Options
- `--quick` - Skip interactive prompts, use defaults where possible
- `--type` - Specify bug type (execution-error, unexpected-behavior, missing-behavior, performance, documentation, logic-order, other)
- `--command` - Specify the command that exhibited the bug
- `--no-preview` - Skip issue preview and submit directly (use with caution)
- `--enhanced-context` - Gather additional diagnostic data (logs, system info, etc.)
- `--repo` - Specify repository directly (skips interactive selection)

## Interactive Mode Workflow

### Step 1: Context Collection
```bash
# Auto-detect current command context
CURRENT_COMMAND=$(echo "$CONVERSATION_CONTEXT" | grep -E "^/[a-zA-Z]+" | tail -1)

# Capture environment
CLAUDE_VERSION="${CLAUDE_MODEL:-unknown}"
PROMPTS_VERSION=$(cd ~/.claude && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
```

### Step 2: Bug Type Selection
```
What type of bug are you reporting?

1) execution-error - Command failed to execute or threw an error
2) unexpected-behavior - Command executed but produced wrong results  
3) missing-behavior - Command is missing expected functionality
4) performance - Command is too slow or resource-intensive
5) documentation - Documentation is wrong or misleading
6) logic-order - Command executes steps in wrong order
7) other - Something else

Select bug type [1-7]: 
```

### Step 3: Command Identification
If not provided via `--command`:
```
Which command exhibited this bug?
(Leave blank if not command-specific)

Command: /
```

### Step 4: Bug Description
```
Please describe the bug in detail:
- What were you trying to do?
- What did you expect to happen?
- What actually happened?

Description: 
```

### Step 5: Reproduction Steps
```
How can this bug be reproduced?
Please provide step-by-step instructions:

1. 
2. 
3. 
```

### Step 6: Environment Details
```bash
# Auto-collect if --enhanced-context
SYSTEM_INFO=$(uname -a)
SHELL_INFO=$SHELL
GIT_VERSION=$(git --version)
GH_VERSION=$(gh --version | head -1)
```

### Step 7: Additional Context
```
Any additional context? (error messages, logs, screenshots)
You can paste multiple lines. Type 'done' on a new line when finished.

> 
```

### Step 8: Severity Assessment
```
How severe is this bug?

1) critical - Prevents all usage, data loss, security issue
2) high - Major functionality broken, no workaround
3) medium - Functionality impaired but has workaround
4) low - Minor issue, cosmetic, or edge case

Select severity [1-4]: 
```

## Quick Mode Workflow

When `--quick` flag is used:
- Skip interactive prompts where possible
- Use command context to auto-fill fields
- Use smart defaults for severity and type
- Still show preview before submission

```bash
# Quick mode example
/report bug --quick --type execution-error --command plan

# Auto-fills:
# - Repository: prompts (detected from command)
# - Bug type: execution-error (provided)
# - Command: /plan (provided)
# - Context: Last error from conversation
# - Severity: medium (default)
```

## Bug Report Templates

**See**: `_bug_templates.md` for complete templates

Available templates:
- Execution Error Template - Command fails with error
- Unexpected Behavior Template - Wrong output or results
- Missing Behavior Template - Expected functionality is missing
- Performance Issue Template - Slow execution or high resource usage
- Documentation Bug Template - Incorrect or missing documentation
- Logic Order Bug Template - Steps execute in wrong order
- General Bug Template - Other types of bugs

Select template based on bug type and replace placeholders with actual values.

## Context Enhancement

When `--enhanced-context` is used:
1. Capture last 10 commands from history
2. Include relevant log files
3. Check for known issues
4. Run diagnostic commands
5. Include system resource usage

## Integration

This module:
- Uses `_templates.md` for issue formatting
- Uses `_interactive.md` for user prompts
- Integrates with GitHub CLI for submission

## Best Practices

1. **Be specific**: Include exact error messages
2. **Be reproducible**: Clear steps to recreate
3. **Include context**: Environment and versions matter
4. **Check existing**: Search for duplicates first
5. **Follow up**: Respond to maintainer questions