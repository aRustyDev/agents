---
name: report
description: Create GitHub issues for bugs, features, and improvements across multiple repositories
author: Claude
version: 3.0.0
modules:
  - report/bug.md
  - report/feature.md
  - report/improvement.md
  - report/security.md
  - report/audit.md
  - report/_templates.md
  - report/_interactive.md
---

# Command: /report

Create GitHub issues to report bugs, request features, or suggest improvements across your repositories. Supports multiple repositories with customizable templates. Issues are previewed before submission for review and editing.

## Usage
```
/report <subcommand> [options]
```

## Architecture

This command is implemented as a modular system with specialized modules for each report type:

### Report Type Modules

1. **`bug.md`** - Bug Report Creation
   - Execution errors and unexpected behavior
   - Comprehensive bug templates with reproduction steps
   - Enhanced context gathering options

2. **`feature.md`** - Feature Request Creation
   - New functionality requests
   - User stories and acceptance criteria
   - Use case documentation

3. **`improvement.md`** - Enhancement Suggestions
   - Performance, usability, and code quality improvements
   - Data-driven improvement proposals
   - Impact assessment

4. **`security.md`** - Security Issue Reporting
   - Responsible disclosure workflows
   - CVSS scoring and severity assessment
   - Private security advisories

5. **`audit.md`** - Audit Findings and Recommendations
   - Repository audit reports
   - Architecture compliance findings
   - Progress tracking

### Shared Modules

6. **`_templates.md`** - Issue Templates
   - Reusable issue templates
   - Template generation utilities
   - Formatting helpers

7. **`_interactive.md`** - Interactive Prompts
   - User interaction flows
   - Input validation
   - Repository selection

## Module Loading Strategy

The report command loads modules based on the subcommand:

```yaml
subcommand_modules:
  bug: report/bug.md
  feature: report/feature.md
  improvement: report/improvement.md
  security: report/security.md
  audit: report/audit.md
  shared:
    - report/_templates.md
    - report/_interactive.md
```

## Process Dependencies
```yaml
processes:
  - name: issue-tracking/github-issues
    version: ">=1.0.0"
    usage: "Core issue creation and management"
    
  - name: data-sanitization
    version: ">=1.0.0" 
    usage: "Sanitize conversation context before including in issues"
    
  - name: ui/interactive-selection
    version: ">=1.0.0"
    usage: "Repository selection and preview formatting"
    
  - name: meta/context-analysis
    version: ">=1.0.0"
    usage: "Enhanced context gathering from various sources"
    conditional: true
    condition: "Used when --enhanced-context flag is set"
```

## Repository Selection

When any subcommand is invoked, Claude will:

1. **Load Repository Configuration**
   ```bash
   # Load from config/repositories.yaml
   REPOS=$(yq eval '.core + .custom' ~/.claude/config/repositories.yaml)
   ```

2. **Interactive Repository Selection**
   ```
   Which repository is this issue for?
   
   Core Repositories:
   1) prompts - Slash command system and Claude configuration
   2) dotfiles - Personal dotfiles and system configuration  
   3) pre-commit-hooks - Custom pre-commit hooks collection
   
   Custom Repositories:
   4) my-project - My awesome project
   
   Select repository [1-4]: 
   ```

3. **Template Resolution**
   - Core repos use `templates/issues-{repo}/` templates
   - Custom repos use `templates/issues-custom/` templates
   - Falls back to generic templates if repo-specific not found

## Subcommand: bug

Report issues with Claude's behavior when using slash-commands.

### Usage
```
/report bug [--quick] [--type <bug-type>] [--command <command-name>]
```

### Options
- `--quick` - Skip interactive prompts, use defaults where possible
- `--type` - Specify bug type (execution-error, unexpected-behavior, missing-behavior, performance, documentation, logic-order, other)
- `--command` - Specify the command that exhibited the bug
- `--no-preview` - Skip issue preview and submit directly (use with caution)
- `--enhanced-context` - Gather additional diagnostic data (logs, system info, etc.)
- `--repo` - Specify repository directly (skips interactive selection)

### Interactive Mode Workflow

1. **Context Collection**
   ```bash
   # Auto-detect current command context
   CURRENT_COMMAND=$(echo "$CONVERSATION_CONTEXT" | grep -E "^/[a-zA-Z]+" | tail -1)
   
   # Capture environment
   CLAUDE_VERSION="${CLAUDE_MODEL:-unknown}"
   PROMPTS_VERSION=$(cd ~/.claude && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
   ```

2. **Bug Type Selection**
   ```
   What type of bug are you reporting?
   1) Command execution error
   2) Unexpected behavior
   3) Missing expected behavior
   4) Performance issue
   5) Documentation mismatch
   6) Logical order issue
   7) Other
   ```

3. **Information Gathering**
   Based on bug type, load appropriate template:
   - First check repo-specific: `templates/issues-{repo}/{bug-type}.md`
   - Fallback to generic: `templates/issues/bugs/{bug-type}.md`
   
   Template types:
   - `execution-error.md`
   - `unexpected-behavior.md`
   - `missing-behavior.md`
   - `performance-issue.md`
   - `documentation-mismatch.md`
   - `logic-order.md`
   - `other-bug.md`

4. **Enhanced Context Gathering** (if --enhanced-context)
   ```bash
   # Gather diagnostic data
   gather_enhanced_context() {
     echo "## Additional Context"
     
     # Last command output
     if [ -f "$LAST_COMMAND_OUTPUT" ]; then
       echo "### Last Command Output"
       tail -n 50 "$LAST_COMMAND_OUTPUT"
     fi
     
     # Check common log locations
     for log_dir in ~/logs /tmp ./.claude/logs ./logs; do
       if [ -d "$log_dir" ]; then
         echo "### Recent Logs from $log_dir"
         find "$log_dir" -name "*.log" -mtime -1 -exec tail -n 20 {} \;
       fi
     done
     
     # Git status and recent changes
     echo "### Git Status"
     git status --short
     echo "### Recent Git Changes"
     git diff --stat HEAD~5..HEAD
     
     # System information
     echo "### System Info"
     uname -a
     echo "Memory: $(free -h | grep Mem | awk '{print $3"/"$2}')"
     echo "Disk: $(df -h . | tail -1 | awk '{print $3"/"$2" ("$5" used)"}')"
     
     # Recent shell history (last 10 relevant commands)
     echo "### Recent Commands"
     history | grep -E "(${CURRENT_COMMAND}|error|fail)" | tail -10
   }
   ```

5. **Context Sanitization**
   ```bash
   # Sanitize all gathered context
   FULL_CONTEXT="$CONVERSATION_CONTEXT"
   if [[ "$ENHANCED_CONTEXT" == "true" ]]; then
     FULL_CONTEXT="$FULL_CONTEXT\n\n$(gather_enhanced_context)"
   fi
   
   SANITIZED_CONTEXT=$(echo "$FULL_CONTEXT" | \
     ~/.claude/processes/data-sanitization.sh --remove-pii --truncate 2000)
   ```

5. **Issue Preview & Submission**
   ```bash
   # Show preview unless --no-preview flag is used
   if [[ "$NO_PREVIEW" != "true" ]]; then
     show_issue_preview "$ISSUE_TITLE" "$ISSUE_BODY" "bug,$BUG_TYPE_LABEL"
     
     # Get user confirmation
     read -p "Choose action: [S]ubmit, [E]dit, [C]ancel, [D]ry-run: " ACTION
     
     case "$ACTION" in
       [Ss]* )
         # Proceed to create issue
         ;;
       [Ee]* )
         # Allow editing (implementation depends on environment)
         ISSUE_BODY=$(edit_in_editor "$ISSUE_BODY")
         # Recursively show preview again
         ;;
       [Dd]* )
         # Show what would be submitted without creating
         echo "Dry run - issue would be created with:"
         echo "Repo: $REPO_OWNER/$REPO_NAME"
         echo "Title: $ISSUE_TITLE"
         echo "Labels: bug,$BUG_TYPE_LABEL"
         exit 0
         ;;
       * )
         echo "Cancelled."
         exit 0
         ;;
     esac
   fi
   
   # Create issue using gh CLI
   gh issue create \
     --repo "$REPO_OWNER/$REPO_NAME" \
     --title "$ISSUE_TITLE" \
     --body "$ISSUE_BODY" \
     --label "bug,$BUG_TYPE_LABEL" \
     --assignee "$REPO_ASSIGNEE"
   ```

### Quick Mode Workflow

```bash
# Example usage
/report bug --quick --type execution-error --command "/test"

# Automatically:
# 1. Uses execution-error template
# 2. Captures last 500 lines of context
# 3. Creates issue with minimal prompts
```

## Subcommand: feature

Request new functionality for the slash-command system.

### Usage
```
/report feature [--quick] [--type <feature-type>] [--title <title>]
```

### Options
- `--quick` - Skip interactive prompts where possible
- `--type` - Feature type (command, pattern, role, guide, process, workflow, helper, template, meta, other)
- `--title` - Feature title for quick mode
- `--no-preview` - Skip issue preview and submit directly (use with caution)

### Interactive Mode Workflow

1. **Feature Type Selection**
   ```
   What type of feature are you requesting?
   1) command - New slash command
   2) pattern - Development or design pattern
   3) role - Expert role or persona
   4) guide - How-to documentation
   5) process - Reusable process/procedure
   6) workflow - Multi-step workflow
   7) helper - Utility or helper function
   8) template - Reusable template
   9) meta - Meta-level improvement
   10) other - Create new type
   ```

2. **Type-Specific Templates**
   Load template from `templates/issues/features/`:
   - `command-request.md`
   - `pattern-request.md`
   - `role-request.md`
   - `guide-request.md`
   - `process-request.md`
   - `workflow-request.md`
   - `helper-request.md`
   - `template-request.md`
   - `meta-request.md`
   - `other-feature.md`

3. **Context Enhancement**
   ```bash
   # Detect related commands/processes
   RELATED_ITEMS=$(find ~/.claude -name "*.md" | xargs grep -l "$FEATURE_KEYWORDS" | head -5)
   ```

4. **Label Assignment**
   ```bash
   # Auto-apply labels based on type
   LABELS="enhancement,$FEATURE_TYPE"
   
   # Add additional context labels
   if [[ "$FEATURE_TYPE" == "command" ]]; then
     LABELS="$LABELS,slash-command"
   fi
   ```

5. **Issue Preview & Submission**
   ```bash
   # Show preview unless --no-preview flag is used
   if [[ "$NO_PREVIEW" != "true" ]]; then
     show_issue_preview "$FEATURE_TITLE" "$ISSUE_BODY" "$LABELS"
     
     # Get user confirmation
     read -p "Choose action: [S]ubmit, [E]dit, [C]ancel, [D]ry-run: " ACTION
     
     case "$ACTION" in
       [Ss]* )
         # Proceed to create issue
         ;;
       [Ee]* )
         # Allow editing
         ISSUE_BODY=$(edit_in_editor "$ISSUE_BODY")
         # Recursively show preview again
         ;;
       [Dd]* )
         # Show what would be submitted without creating
         echo "Dry run - issue would be created with:"
         echo "Repo: $REPO_OWNER/$REPO_NAME"
         echo "Title: $FEATURE_TITLE"
         echo "Labels: $LABELS"
         exit 0
         ;;
       * )
         echo "Cancelled."
         exit 0
         ;;
     esac
   fi
   
   # Create issue using gh CLI
   gh issue create \
     --repo "aRustyDev/prompts" \
     --title "$FEATURE_TITLE" \
     --body "$ISSUE_BODY" \
     --label "$LABELS"
   ```

### Creating New Types

When "other" is selected:
```bash
read -p "Enter the new type name: " NEW_TYPE
read -p "Describe this type: " TYPE_DESCRIPTION

# Create new directory if needed
mkdir -p "~/.claude/$NEW_TYPE"

# Create template
cat > "~/.claude/templates/issues/features/${NEW_TYPE}-request.md" << EOF
# ${NEW_TYPE^} Request Template

## Description
$TYPE_DESCRIPTION

## Details
[Provide specific details about the $NEW_TYPE]

## Use Cases
[When and why would this be used?]

## Examples
[Provide examples if applicable]
EOF
```

## Subcommand: improvement

Suggest improvements to existing functionality.

### Usage
```
/report improvement [--quick] [--area <improvement-area>] [--title <title>]
```

### Options
- `--quick` - Skip interactive prompts where possible
- `--area` - Improvement area (performance, usability, documentation, testing, refactoring, other)
- `--title` - Improvement title for quick mode
- `--no-preview` - Skip issue preview and submit directly
- `--enhanced-context` - Include performance metrics and usage data
- `--repo` - Specify repository directly

### Interactive Mode Workflow

1. **Improvement Area Selection**
   ```
   What area does this improvement target?
   1) performance - Speed, efficiency, resource usage
   2) usability - User experience, interface, workflow
   3) documentation - Clarity, completeness, examples
   4) testing - Test coverage, quality, automation
   5) refactoring - Code structure, maintainability
   6) other - Other improvements
   ```

2. **Current State Analysis**
   - Describe current behavior/state
   - Identify specific pain points
   - Quantify impact if possible

3. **Proposed Improvement**
   - Detailed description of changes
   - Expected benefits
   - Implementation approach
   - Potential risks or trade-offs

4. **Template Loading**
   Load template from:
   - Repo-specific: `templates/issues-{repo}/improvement-{area}.md`
   - Generic: `templates/issues/improvements/{area}.md`

5. **Issue Creation**
   ```bash
   # Create improvement issue
   gh issue create \
     --repo "$REPO_OWNER/$REPO_NAME" \
     --title "$IMPROVEMENT_TITLE" \
     --body "$ISSUE_BODY" \
     --label "improvement,$AREA_LABEL" \
     --assignee "$REPO_ASSIGNEE"
   ```

## Implementation Details

### Environment Detection
```bash
# Function to gather environment info
gather_environment() {
  echo "## Environment"
  echo "- Claude Model: ${CLAUDE_MODEL:-unknown}"
  echo "- Claude Version: ${CLAUDE_VERSION:-unknown}"
  echo "- Prompts Version: $(cd ~/.claude && git describe --tags --always 2>/dev/null || echo 'unknown')"
  echo "- Platform: $(uname -s)"
  echo "- Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
  echo "- Session ID: ${CLAUDE_SESSION_ID:-unknown}"
}
```

### Context Capture
```bash
# Function to capture and sanitize context
capture_context() {
  local LINES="${1:-500}"
  
  # Get recent conversation context
  if [ -n "$CLAUDE_CONVERSATION_FILE" ]; then
    tail -n "$LINES" "$CLAUDE_CONVERSATION_FILE" | \
      ~/.claude/processes/data-sanitization.sh --remove-pii
  else
    echo "[No conversation context available]"
  fi
}
```

### Issue Preview Display
```bash
# Function to display issue preview
show_issue_preview() {
  local TITLE="$1"
  local BODY="$2"
  local LABELS="$3"
  
  # Draw preview box using box-drawing characters
  echo "╭─────────────────────────────────────────────╮"
  echo "│ GitHub Issue Preview                        │"
  echo "├─────────────────────────────────────────────┤"
  echo "│ Repository: $REPO_OWNER/$REPO_NAME          │"
  echo "│ Type: ${LABELS}                             │"
  echo "├─────────────────────────────────────────────┤"
  echo "│ Title: ${TITLE}                             │"
  echo "├─────────────────────────────────────────────┤"
  echo "│ Body:                                       │"
  echo "╰─────────────────────────────────────────────╯"
  echo ""
  echo "$BODY"
  echo ""
  echo "─────────────────────────────────────────────"
}

# Function to edit in user's preferred editor
edit_in_editor() {
  local CONTENT="$1"
  local TMPFILE=$(mktemp)
  
  echo "$CONTENT" > "$TMPFILE"
  ${EDITOR:-vi} "$TMPFILE"
  cat "$TMPFILE"
  rm "$TMPFILE"
}
```

### Template Population
```bash
# Function to populate template variables
populate_template() {
  local TEMPLATE="$1"
  
  # Replace all template variables
  sed -e "s/\${COMMAND}/$CURRENT_COMMAND/g" \
      -e "s/\${CLAUDE_VERSION}/$CLAUDE_VERSION/g" \
      -e "s/\${PROMPTS_VERSION}/$PROMPTS_VERSION/g" \
      -e "s/\${TIMESTAMP}/$(date -u)/g" \
      -e "s/\${USER}/${USER:-unknown}/g" \
      "$TEMPLATE"
}
```

## Error Handling

- Check for `gh` CLI installation
- Verify GitHub authentication
- Validate repository access
- Handle network failures gracefully
- Provide fallback to clipboard copy if issue creation fails

## Success Metrics

- Issue creation time < 30 seconds
- All required context captured automatically
- 90%+ of issues have sufficient detail for action
- Proper categorization and labeling

## Implementation

When this command is invoked, Claude will:

1. **Parse Arguments**: Determine subcommand and options
2. **Gather Context**: Automatically collect environment and conversation data
3. **Interactive Flow**: Guide through appropriate template selection
4. **Populate Template**: Fill in all variables with gathered information
5. **Preview Issue**: Display formatted preview (unless --no-preview is set)
6. **Handle User Choice**: Submit, edit, cancel, or dry-run based on selection
7. **Create Issue**: Use GitHub CLI to create the issue after approval

### Example Execution Flow

For bug reporting:
```
User: /report bug
Claude: I'll help you report a bug. Let me gather some context first...

Auto-detected command: /cicd
Environment: Claude Opus 4, Prompts v1.2.3

What type of bug are you reporting?
1) Command execution error
2) Unexpected behavior
3) Missing expected behavior
4) Performance issue
5) Documentation mismatch
6) Logical order issue
7) Other

User: 2
Claude: I'll use the unexpected behavior template. Please describe what unexpected behavior you encountered...

[Claude guides through template completion]

╭─────────────────────────────────────────────╮
│ GitHub Issue Preview                        │
├─────────────────────────────────────────────┤
│ Repository: $REPO_OWNER/$REPO_NAME          │
│ Type: bug, unexpected-behavior              │
├─────────────────────────────────────────────┤
│ Title: /cicd command produces wrong output  │
├─────────────────────────────────────────────┤
│ Body:                                       │
╰─────────────────────────────────────────────╯

[Issue body content displayed here...]

─────────────────────────────────────────────

Choose action: [S]ubmit, [E]dit, [C]ancel, [D]ry-run: s

Creating issue on GitHub...
✅ Issue created: https://github.com/aRustyDev/prompts/issues/123
```

For feature requests:
```
User: /report feature --quick --type command --title "Add /analyze command"
Claude: Creating feature request for new command...
✅ Issue created: https://github.com/aRustyDev/prompts/issues/124
```

## Changelog

### Version 2.0.0
- **Breaking Change**: Now prompts for repository selection (previously hardcoded to prompts repo)
- **New Feature**: Multi-repository support with configurable repositories
- **New Feature**: Added `improvement` subcommand for suggesting enhancements
- **New Feature**: Enhanced context gathering with `--enhanced-context` flag
- **New Feature**: Repository-specific templates (e.g., `templates/issues-prompts/`)
- **New Feature**: Custom repository support via `config/repositories.yaml`
- **Enhancement**: Added `--repo` flag to skip interactive repository selection
- **Enhancement**: Improved template resolution with repo-specific fallback
- **Enhancement**: Added diagnostic data collection (logs, git info, system metrics)
- **Process Integration**: Added `meta/context-analysis` for enhanced context
- **Configuration**: Added `.gitignore` for custom templates

### Version 1.1.0
- Added issue preview functionality before submission
- Added `--no-preview` flag option
- Added edit capability in preview mode
- Added dry-run option

### Version 1.0.0
- Initial release with bug and feature reporting
- GitHub CLI integration
- Interactive and quick modes
- Template-based issue creation