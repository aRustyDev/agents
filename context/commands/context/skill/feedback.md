# Skill Feedback

Submit feedback about a skill. Supports bug reports, feature requests, and success stories.

## Arguments

`$ARGUMENTS` can be:

- `bug` - Report a skill bug with auto-gathered context
- `feature` - Request a skill feature or enhancement
- `success` - Share a skill success story (opens GitHub Discussions)
- (empty) - Interactive menu to choose type

## Subcommands

### /context:skill:feedback bug

Report a skill bug with automatically gathered context.

1. **Gather Context** (automatic):

   ```bash
   # Current directory
   CWD=$(pwd)

   # Skill detection
   SKILL_DIR=$(find context/skills -maxdepth 1 -type d -name '*' | fzf --prompt "Select skill: " 2>/dev/null)
   SKILL_FILE="$SKILL_DIR/SKILL.md"
   SKILL_NAME=$(basename "$SKILL_DIR")

   # Skill metadata from frontmatter
   SKILL_TITLE=$(head -20 "$SKILL_FILE" | grep '^title:' | sed 's/title: //')
   SKILL_VERSION=$(head -20 "$SKILL_FILE" | grep '^version:' | sed 's/version: //')

   # Skill assets
   ASSETS=$(ls "$SKILL_DIR/assets/" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')

   # OS info
   OS_INFO="$(uname -s) $(uname -r)"

   # Claude Code version
   CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
   ```

2. **Ask for Bug Details** using AskUserQuestion:
   - Skill name (pre-filled if detected)
   - What task were you performing when the issue occurred
   - What happened vs what was expected
   - Steps to reproduce
   - Was the skill loaded correctly (check with `/find-skills`)

3. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the bug report.

4. **Generate GitHub Issue URL**:

   ```text
   https://github.com/aRustyDev/agents/issues/new?template=bug-report.yml&title=[BUG][skill:<name>]%20<title>&labels=bug,triage,skills
   ```

5. **Present to User**:
   - Show the formatted bug report with skill context
   - Provide the pre-filled issue URL
   - Offer to open in browser: `open "<url>"`

### /context:skill:feedback feature

Request a skill feature or enhancement.

1. **Ask for Feature Details** using AskUserQuestion:
   - Skill name (existing or "New Skill")
   - Feature scope (New Section, Pattern Coverage, Asset Addition, Trigger Improvement, Other)
   - Use case / problem to solve
   - Proposed solution

2. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the feature request.

3. **Generate GitHub Issue URL**:

   ```text
   https://github.com/aRustyDev/agents/issues/new?template=feature-request.yml&title=[FEATURE][skill:<name>]%20<title>&labels=enhancement,skills
   ```

4. **Present to User**:
   - Show the formatted feature request
   - Provide the pre-filled issue URL
   - Offer to open in browser

### /context:skill:feedback success

Share a success story about how a skill helped you.

1. **Ask for Success Story Details** using AskUserQuestion:
   - Skill name
   - What task you accomplished
   - How the skill improved your workflow
   - Quality of the output (accuracy, completeness)
   - Tips for other skill users

2. **Format Using Output Style**:
   Use the `feedback-submission` output style to format the success story.

3. **Generate GitHub Discussions URL**:

   ```text
   https://github.com/aRustyDev/agents/discussions/new?category=show-and-tell&title=[Skill]%20<title>
   ```

4. **Present to User**:
   - Show the formatted success story
   - Provide the pre-filled discussion URL
   - Offer to open in browser

### /context:skill:feedback (no argument)

Interactive menu to choose feedback type.

Use AskUserQuestion with options:

| Option | Description |
|--------|-------------|
| Report a Bug | Something in a skill isn't working correctly |
| Request a Feature | Suggest a skill improvement or new coverage |
| Share Success Story | Tell us how a skill helped you |

Then route to the appropriate subcommand.

## Context Gathering

The following context is gathered automatically for skill bug reports:

| Context | Source | Required |
|---------|--------|----------|
| Working Directory | `pwd` | Yes |
| Skill Name | Directory name | Yes |
| Skill Version | SKILL.md frontmatter | No |
| Skill Assets | `ls assets/` | No |
| OS/Platform | `uname -s` | Yes |
| Claude Code Version | `claude --version` | No |

**Privacy**: Context is shown to the user before submission. No automatic submission occurs.

## Output

After gathering information, present:

```text
## Skill Feedback Ready

### Skill
**Name**: <skill name>
**Version**: <version>
**Assets**: <asset list>

### Summary
<formatted feedback using output style>

### Submit
**URL**: <pre-filled GitHub URL>

Would you like me to open this in your browser?
```

## Examples

```text
/context:skill:feedback bug
/context:skill:feedback feature
/context:skill:feedback success
/context:skill:feedback
```

## Related

- Output Style: `context/output-styles/feedback-submission.md`
- Skill Structure: `context/skills/<name>/SKILL.md`
- Skill Validation: `/context:skill:review`
- Bug Template: `.github/ISSUE_TEMPLATE/bug-report.yml`
- Feature Template: `.github/ISSUE_TEMPLATE/feature-request.yml`
- Success Stories: GitHub Discussions > Show and Tell
