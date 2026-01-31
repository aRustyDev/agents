# Hooks

Hooks are a new mechanic introduced to Claude Code to allow deterministic responses based on a given event such as tool executions, file changes, or deployment activities.

## Real-World Implementation

I have been experimenting with simple use cases for how they can be used to improve the reliability of my existing workflows such as running various pre/post deploy related activities before deploying the ClaudeLog website live.

When you update a website online there are various SEO related activities which must be performed such as:

- Deploying your sitemap to various web master tools.
- Checking build process has not generated invalid JSON schemas (different web masters are surprisingly sensitive).
- Validating URLs are all live and well formed.

These were simple low hanging fruit which Claude suggested for me to explore implementing into my workflow based on my existing deployment pipeline.

## The Scoping Challenge

Interestingly I found the fiddliest bit was scoping the activation requirements such that they do not activate too early.

### Badly Scoped Hook Example

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/expensive-validation.sh"
          }
        ]
      }
    ]
  }
}
```

This fires on ANY bash command, running expensive validation even for simple ls or pwd commands

### Better Scoped Hook Example - Smart Dispatcher Pattern

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/smart-hook-dispatcher.sh"
          }
        ]
      }
    ]
  }
}
```

#### Smart Dispatcher Script:

```bash
#!/bin/bash

# Read JSON input from Claude Code

json_input=$(cat)
command=$(echo "$json_input" | jq -r '.tool_input.command // empty')

# Exit early if no command

if [ -z "$command" ]; then
exit 0
fi

# Scope to specific commands only

if echo "$command" | grep -q "npm run deploy"; then
  echo "🚀 Running pre-deployment validation..."
  ./scripts/pre-deployment-checks.sh <<< "$json_input"
fi

if echo "$command" | grep -q "npm run build"; then
  echo "🔧 Running build validation..."
  ./scripts/build-validator.sh <<< "$json_input"
fi
```

This intelligently routes commands based on content analysis, only running expensive operations when needed

### Finding Hook Opportunities

To find suggestions for where hooks could be useful within your setup be sure to ask Claude to review your current systems and suggest the benefit of Hooks.

Just beware that if they're unnecessarily firing you will have an extremely slowed down Agent (thankfully it is not costing you tokens though).

### Modifying Tool Inputs with PreToolUse

Starting in v2.0.10, PreToolUse hooks can modify tool inputs before execution. Instead of blocking Claude's actions and forcing retries, hooks intercept tool calls, modify the JSON input, and let execution proceed with corrected parameters. This enables transparent sandboxing, automatic security enforcement (dry-run flags, secret redaction), team convention adherence (commit message formatting, linter configuration), and developer experience improvements (path correction, dependency auto-installation). The modifications are invisible to Claude.

This enables dynamic parameter adjustment, input validation, and automatic correction of tool arguments based on project-specific requirements.

### Use Cases for Tool Input Modification:

- **Environment Variables** - Automatically inject required environment variables before commands.
- **Path Normalization** - Convert relative paths to absolute paths based on project structure.
- **Security Wrappers** - Wrap commands with security constraints or sandboxing.
- **Parameter Validation** - Check and correct parameter formats before execution.
- **Logging Enhancement** - Add verbose flags or logging parameters automatically.

The hook script receives the tool input JSON via stdin and outputs the modified JSON to stdout. Claude Code uses the modified input for tool execution.

### Available Triggers

- **PreToolUse** - Before tool execution.
- **PostToolUse** - After tool completion.
- **UserPromptSubmit** - When user submits a prompt.
- **Stop** - When Claude Code agent finishes responding.
- **SessionEnd** - When Claude Code session terminates.

### Common JSON Fields

All hook types can include these optional fields for controlling execution behavior:

```json
{
  "continue": true, // Whether Claude should continue after hook execution (default: true)
  "stopReason": "string", // Message shown when continue is false
  "suppressOutput": true, // Hide stdout from transcript mode (default: false)
  "systemMessage": "string" // Optional warning message shown to the user
}
```

### Best Practices

- **Smart dispatching** - Use single entry point with intelligent command routing to avoid performance penalties.
- **Exit code checking** - Validate successful command execution in PostToolUse hooks (.tool_response.exit_code only available after execution).
- **Parallel execution** - Run independent validations concurrently with & and wait for faster processing.
- **JSON input parsing** - Extract command details with jq -r '.tool_input.command // empty' (fallback handles missing fields gracefully).
- **Performance monitoring** - Track hook execution time and cache results to identify bottlenecks.
- **Error handling** - Graceful failure for non-critical hooks prevents workflow interruption.
- **Scope precisely** - Target specific commands rather than broad tool categories to maintain responsiveness.
- **Tool input modification** - When modifying tool inputs in PreToolUse hooks, ensure output is valid JSON and preserve all required fields.

### Workflow Automation

Hooks transform reactive development into proactive automation. Well-scoped hooks eliminate manual deployment steps and catch issues before they reach production. The key is precise trigger patterns.
