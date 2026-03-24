# Plugin Feedback

Submit feedback about a plugin. Supports bug reports, feature requests, and success stories.

## Arguments

`$ARGUMENTS` can be:

- `bug` - Report a plugin bug with auto-gathered context
- `feature` - Request a plugin feature or enhancement
- `success` - Share a plugin success story (opens GitHub Discussions)
- (empty) - Interactive menu to choose type

## Subcommands

### /context:plugin:feedback bug

Report a plugin bug with automatically gathered context.

1. **Gather Context** (automatic):

   ```bash
   # Current directory
   CWD=$(pwd)

   # Plugin manifest
   PLUGIN_DIR=$(find content/plugins -maxdepth 1 -type d | fzf --prompt "Select plugin: " 2>/dev/null)
   PLUGIN_JSON=$(cat "$PLUGIN_DIR/.claude-plugin/plugin.json" 2>/dev/null)
   PLUGIN_NAME=$(echo "$PLUGIN_JSON" | jq -r '.name')
   PLUGIN_VERSION=$(echo "$PLUGIN_JSON" | jq -r '.version')

   # Plugin components
   SKILLS=$(ls "$PLUGIN_DIR/skills/" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
   AGENTS=$(ls "$PLUGIN_DIR/agents/" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
   COMMANDS=$(ls "$PLUGIN_DIR/commands/" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')

   # OS info
   OS_INFO="$(uname -s) $(uname -r)"

   # Claude Code version
   CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
   ```

2. **Ask for Bug Details** using AskUserQuestion:
   - Plugin name (pre-filled if detected)
   - Affected component (Skill, Command, Agent, Rule, Hook, Settings, Other)
   - What happened vs what was expected
   - Steps to reproduce

3. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the bug report.

4. **Generate GitHub Issue URL**:

   ```text
   https://github.com/aRustyDev/agents/issues/new?template=bug-report.yml&title=[BUG][plugin:<name>]%20<title>&labels=bug,triage,plugin
   ```

5. **Present to User**:
   - Show the formatted bug report with plugin context
   - Provide the pre-filled issue URL
   - Offer to open in browser: `open "<url>"`

### /context:plugin:feedback feature

Request a plugin feature or enhancement.

1. **Ask for Feature Details** using AskUserQuestion:
   - Plugin name (existing or "New Plugin")
   - Feature scope (New Skill, New Command, New Agent, Configuration, Integration, Other)
   - Use case / problem to solve
   - Proposed solution

2. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the feature request.

3. **Generate GitHub Issue URL**:

   ```text
   https://github.com/aRustyDev/agents/issues/new?template=feature-request.yml&title=[FEATURE][plugin:<name>]%20<title>&labels=enhancement,plugin
   ```

4. **Present to User**:
   - Show the formatted feature request
   - Provide the pre-filled issue URL
   - Offer to open in browser

### /context:plugin:feedback success

Share a success story about how a plugin helped you.

1. **Ask for Success Story Details** using AskUserQuestion:
   - Plugin name
   - What you accomplished
   - Which plugin components were most useful
   - Tips for other plugin users

2. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the success story.

3. **Generate GitHub Discussions URL**:

   ```text
   https://github.com/aRustyDev/agents/discussions/new?category=show-and-tell&title=[Plugin]%20<title>
   ```

4. **Present to User**:
   - Show the formatted success story
   - Provide the pre-filled discussion URL
   - Offer to open in browser

### /context:plugin:feedback (no argument)

Interactive menu to choose feedback type.

Use AskUserQuestion with options:

| Option | Description |
|--------|-------------|
| Report a Bug | Something in a plugin isn't working correctly |
| Request a Feature | Suggest a new plugin feature or improvement |
| Share Success Story | Tell us how a plugin helped you |

Then route to the appropriate subcommand.

## Context Gathering

The following context is gathered automatically for plugin bug reports:

| Context | Source | Required |
|---------|--------|----------|
| Working Directory | `pwd` | Yes |
| Plugin Name | `plugin.json → name` | Yes |
| Plugin Version | `plugin.json → version` | Yes |
| Plugin Components | `ls skills/ agents/ commands/` | No |
| OS/Platform | `uname -s` | Yes |
| Claude Code Version | `claude --version` | No |

**Privacy**: Context is shown to the user before submission. No automatic submission occurs.

## Output

After gathering information, present:

```text
## Plugin Feedback Ready

### Plugin
**Name**: <plugin name>
**Version**: <version>
**Components**: <skills, agents, commands>

### Summary
<formatted feedback using output style>

### Submit
**URL**: <pre-filled GitHub URL>

Would you like me to open this in your browser?
```

## Examples

```text
/context:plugin:feedback bug
/context:plugin:feedback feature
/context:plugin:feedback success
/context:plugin:feedback
```

## Related

- Output Style: `content/output-styles/feedback-submission.md`
- Plugin Structure: `content/plugins/<name>/.claude-plugin/plugin.json`
- Bug Template: `.github/ISSUE_TEMPLATE/bug-report.yml`
- Feature Template: `.github/ISSUE_TEMPLATE/feature-request.yml`
- Success Stories: GitHub Discussions > Show and Tell
