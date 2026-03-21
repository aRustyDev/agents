# Command Feedback

Submit feedback about a slash command. Supports bug reports, feature requests, and success stories.

## Arguments

`$ARGUMENTS` can be:

- `bug` - Report a command bug with auto-gathered context
- `feature` - Request a command feature or enhancement
- `success` - Share a command success story (opens GitHub Discussions)
- (empty) - Interactive menu to choose type

## Subcommands

### /context:command:feedback bug

Report a command bug with automatically gathered context.

1. **Gather Context** (automatic):

   ```bash
   # Current directory
   CWD=$(pwd)

   # Available commands
   COMMANDS=$(find context/commands -name '*.md' -not -name 'feedback.md' | sed 's|context/commands/||; s|\.md$||' | sort | tr '\n' ', ' | sed 's/,$//')

   # OS info
   OS_INFO="$(uname -s) $(uname -r)"

   # Claude Code version
   CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
   ```

2. **Ask for Bug Details** using AskUserQuestion:
   - Command name (e.g. `/context:skill:create`, `/beads:ready`)
   - Command namespace (context, beads, homebrew, github, etc.)
   - What arguments were passed
   - What happened vs what was expected
   - Steps to reproduce

3. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the bug report.

4. **Generate GitHub Issue URL**:

   ```text
   https://github.com/aRustyDev/agents/issues/new?template=bug-report.yml&title=[BUG][command:<namespace>:<name>]%20<title>&labels=bug,triage,command
   ```

5. **Present to User**:
   - Show the formatted bug report with command context
   - Provide the pre-filled issue URL
   - Offer to open in browser: `open "<url>"`

### /context:command:feedback feature

Request a command feature or enhancement.

1. **Ask for Feature Details** using AskUserQuestion:
   - Command name (existing or "New Command")
   - Command namespace (existing or new)
   - Feature scope (New Subcommand, Argument Handling, Output Format, Integration, Other)
   - Use case / problem to solve
   - Proposed solution

2. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the feature request.

3. **Generate GitHub Issue URL**:

   ```text
   https://github.com/aRustyDev/agents/issues/new?template=feature-request.yml&title=[FEATURE][command:<namespace>:<name>]%20<title>&labels=enhancement,command
   ```

4. **Present to User**:
   - Show the formatted feature request
   - Provide the pre-filled issue URL
   - Offer to open in browser

### /context:command:feedback success

Share a success story about how a command helped you.

1. **Ask for Success Story Details** using AskUserQuestion:
   - Command name
   - What task you accomplished
   - How the command improved your workflow
   - Tips for other command users

2. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the success story.

3. **Generate GitHub Discussions URL**:

   ```text
   https://github.com/aRustyDev/agents/discussions/new?category=show-and-tell&title=[Command]%20<title>
   ```

4. **Present to User**:
   - Show the formatted success story
   - Provide the pre-filled discussion URL
   - Offer to open in browser

### /context:command:feedback (no argument)

Interactive menu to choose feedback type.

Use AskUserQuestion with options:

| Option | Description |
|--------|-------------|
| Report a Bug | A command isn't working correctly |
| Request a Feature | Suggest a new command or improvement |
| Share Success Story | Tell us how a command helped you |

Then route to the appropriate subcommand.

## Context Gathering

The following context is gathered automatically for command bug reports:

| Context | Source | Required |
|---------|--------|----------|
| Working Directory | `pwd` | Yes |
| Command Name | User input | Yes |
| Command Namespace | Derived from path | Yes |
| Arguments Passed | User input | No |
| OS/Platform | `uname -s` | Yes |
| Claude Code Version | `claude --version` | No |

**Privacy**: Context is shown to the user before submission. No automatic submission occurs.

## Output

After gathering information, present:

```text
## Command Feedback Ready

### Command
**Name**: <command name>
**Namespace**: <namespace>
**Arguments**: <args passed>

### Summary
<formatted feedback using output style>

### Submit
**URL**: <pre-filled GitHub URL>

Would you like me to open this in your browser?
```

## Examples

```text
/context:command:feedback bug
/context:command:feedback feature
/context:command:feedback success
/context:command:feedback
```

## Related

- Output Style: `context/output-styles/feedback-submission.md`
- Command Structure: `context/commands/<namespace>/<name>.md`
- Bug Template: `.github/ISSUE_TEMPLATE/bug-report.yml`
- Feature Template: `.github/ISSUE_TEMPLATE/feature-request.yml`
- Success Stories: GitHub Discussions > Show and Tell
