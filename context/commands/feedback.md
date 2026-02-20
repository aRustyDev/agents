# Feedback

Submit feedback about plugins, skills, commands, or other components. Supports bug reports, feature requests, and success stories.

## Arguments

`$ARGUMENTS` can be:

- `bug` - Report a bug with auto-gathered context
- `feature` - Request a new feature or enhancement
- `success` - Share a success story (opens GitHub Discussions)
- (empty) - Interactive menu to choose type

## Subcommands

### /feedback bug

Report a bug with automatically gathered context.

1. **Gather Context** (automatic):

   ```bash
   # Current directory
   CWD=$(pwd)

   # Installed plugins
   PLUGINS=$(jq -r '.plugins[].name' .claude-plugin/marketplace.json 2>/dev/null | tr '\n' ', ' | sed 's/,$//')

   # OS info
   OS_INFO="$(uname -s) $(uname -r)"

   # Claude Code version (if available)
   CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
   ```

2. **Ask for Bug Details** using AskUserQuestion:
   - Component type (Plugin, Skill, Command, Agent, MCP Server, Other)
   - Component name
   - What happened vs what was expected
   - Steps to reproduce

3. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the bug report.

4. **Generate GitHub Issue URL**:

   ```text
   https://github.com/aRustyDev/ai/issues/new?template=bug-report.yml&title=[BUG]%20<title>&labels=bug,triage
   ```

5. **Present to User**:
   - Show the formatted bug report
   - Provide the pre-filled issue URL
   - Offer to open in browser: `open "<url>"`

### /feedback feature

Request a new feature or enhancement.

1. **Ask for Feature Details** using AskUserQuestion:
   - Component type (Plugin, Skill, Command, Agent, MCP Server, New, Other)
   - Component name (or "New" for new components)
   - Use case / problem to solve
   - Proposed solution

2. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the feature request.

3. **Generate GitHub Issue URL**:

   ```text
   https://github.com/aRustyDev/ai/issues/new?template=feature-request.yml&title=[FEATURE]%20<title>&labels=enhancement
   ```

4. **Present to User**:
   - Show the formatted feature request
   - Provide the pre-filled issue URL
   - Offer to open in browser

### /feedback success

Share a success story about how a component helped you.

1. **Ask for Success Story Details** using AskUserQuestion:
   - Component used (Plugin, Skill, Command, Agent)
   - Component name
   - What you accomplished
   - How it helped
   - Tips for others

2. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the success story.

3. **Generate GitHub Discussions URL**:

   ```text
   https://github.com/aRustyDev/ai/discussions/new?category=show-and-tell&title=<title>
   ```

4. **Present to User**:
   - Show the formatted success story
   - Provide the pre-filled discussion URL
   - Offer to open in browser

### /feedback (no argument)

Interactive menu to choose feedback type.

Use AskUserQuestion with options:

| Option | Description |
|--------|-------------|
| Report a Bug | Something isn't working correctly |
| Request a Feature | Suggest a new feature or improvement |
| Share Success Story | Tell us how a component helped you |

Then route to the appropriate subcommand.

## Context Gathering

The following context is gathered automatically for bug reports:

| Context | Source | Required |
|---------|--------|----------|
| Working Directory | `pwd` | Yes |
| Installed Plugins | `.claude-plugin/marketplace.json` | No |
| OS/Platform | `uname -s` | Yes |
| Claude Code Version | `claude --version` | No |

**Privacy**: Context is shown to the user before submission. No automatic submission occurs.

## Output

After gathering information, present:

```text
## Feedback Ready

### Summary
<formatted feedback using output style>

### Submit
**URL**: <pre-filled GitHub URL>

Would you like me to open this in your browser?
```

## Examples

```text
/feedback bug
/feedback feature
/feedback success
/feedback
```

## Related

- Output Style: `context/output-styles/feedback-submission.md`
- Bug Template: `.github/ISSUE_TEMPLATE/bug-report.yml`
- Feature Template: `.github/ISSUE_TEMPLATE/feature-request.yml`
- Success Stories: GitHub Discussions > Show and Tell
