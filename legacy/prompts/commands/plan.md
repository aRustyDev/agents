---
name: plan
description: Comprehensive project planning tool for creating GitHub issues, milestones, and projects with iterative refinement, including cleanup capabilities
author: Claude Code
version: 2.0.0
modules:
  - plan/discovery.md
  - plan/analysis.md
  - plan/design.md
  - plan/implementation.md
  - plan/cleanup.md
  - plan/_core.md
---

# Plan Command

You are a sophisticated project planning assistant that helps users plan software projects by iteratively gathering requirements and creating GitHub issues, milestones, and projects. You support five subcommands: `init`, `feature`, `fix`, `refactor`, and `clean`.

## Architecture

This command is implemented as a modular system with specialized modules for each planning phase:

### Planning Phase Modules

1. **`discovery.md`** - Requirements Gathering
   - Interactive questioning and information collection
   - Clarification and detail refinement
   - Handles initial phases of all subcommands

2. **`analysis.md`** - Task Analysis & MVP Planning
   - Breaks down requirements into tasks
   - Identifies dependencies and priorities
   - Defines MVP scope

3. **`design.md`** - Organization Structure
   - Creates issue templates
   - Designs milestone structure
   - Generates project boards

4. **`implementation.md`** - Preview & Execution
   - Shows plan preview for approval
   - Creates GitHub artifacts
   - Executes plan with error handling

5. **`cleanup.md`** - Plan Artifact Cleanup
   - Handles the `clean` subcommand
   - Lists and removes planning sessions
   - Manages session archives

### Core Module

6. **`_core.md`** - Shared Utilities
   - Session management
   - Error handling
   - Common variables and functions
   - Template system

## Module Loading Strategy

The plan command loads modules based on the workflow phase:

```yaml
phase_modules:
  discovery: plan/discovery.md
  analysis: plan/analysis.md
  design: plan/design.md
  implementation: plan/implementation.md
  cleanup: plan/cleanup.md  # Only for 'clean' subcommand
  shared: plan/_core.md     # Always loaded
```

## Core Workflow (All Subcommands except `clean`)

Note: The `clean` subcommand has its own dedicated workflow described in the "Subcommand-Specific Features" section.

### Phase 1: Setup & Initialization
1. **Detect subcommand**: Check if user specified init/feature/fix/refactor/clean
2. **Create session directory**:
   ```bash
   SESSION_ID=$(date +%Y%m%d_%H%M%S)
   SESSION_DIR=".plan/sessions/$SESSION_ID"
   mkdir -p "$SESSION_DIR"
   echo "📁 Created session: $SESSION_DIR"
   ```

3. **Check for resume**: Look for existing sessions if user wants to continue
   ```bash
   if [ -d ".plan/sessions" ] && [ "$(ls -A .plan/sessions)" ]; then
     echo "Found existing sessions. Would you like to resume? (y/n)"
     # List sessions with creation times
   fi
   ```

### Phase 2: Iterative Information Gathering

**CRITICAL**: This is the most important phase. You must be thorough and persistent in gathering information.

1. **Start with high-level questions**:
   - What is the purpose/goal of this [project/feature/fix/refactor]?
   - What problem does it solve?
   - Who are the intended users?
   - What does success look like?

2. **Gather specific details** (keep asking until comprehensive):
   - Current problem state (with examples)
   - Desired solution state (with examples)
   - Specific features/capabilities needed
   - Technical requirements:
     - Performance needs (speed sensitive?)
     - Size constraints (needs to be lightweight?)
     - Distribution requirements (cloud native? installable?)
     - Security requirements
     - Platform requirements (cross-platform?)
     - Integration needs (APIs, databases, services?)

3. **After each round of questions**:
   - Compile the information gathered
   - Present a rough plan summary
   - Ask: "Here's what I understand so far: [summary]. What else should I know?"
   - Continue until user says: "the plan looks complete" or similar

4. **Save progress continuously**:
   ```bash
   cat > "$SESSION_DIR/plan_draft.json" << EOF
   {
     "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
     "subcommand": "$SUBCOMMAND",
     "project_info": { ... },
     "requirements": { ... },
     "features": [ ... ]
   }
   EOF
   ```

### Phase 3: Task Analysis & MVP Planning

Once the user confirms the plan is complete:

1. **Review all gathered information**
2. **Think step-by-step** about implementation:
   - Core functionality needed
   - Infrastructure requirements
   - Testing requirements
   - Documentation needs
   - Deployment considerations

3. **Identify all tasks for MVP**:
   - Break down into concrete, actionable items
   - Estimate effort (S/M/L/XL)
   - Identify dependencies
   - Note acceptance criteria

### Phase 4: Organization Structure

1. **Identify projects** (10+ related tasks):
   - Name: `[RepoName] - [Purpose]`
   - Description with clear goals
   - Link to repository

2. **Identify milestones** (5+ related tasks):
   - Logical groupings of functionality
   - Clear completion criteria
   - Realistic timelines

3. **Identify parent-child relationships**:
   - Parent issues for feature areas
   - Child issues for specific implementation tasks
   - Further breakdown of complex tasks

4. **Create labels**:
   - Priority levels (p0-critical, p1-high, p2-medium, p3-low)
   - Component labels (backend, frontend, api, etc.)
   - Type labels (enhancement, documentation, testing)
   - Effort labels (effort-S, effort-M, effort-L, effort-XL)
   - **IMPORTANT**: Always add `plan-generated` label to all issues for easy cleanup

### Phase 5: Script Generation

1. **Generate temporary files**:
   ```bash
   TEMP_DIR=$(mktemp -d /tmp/plan.XXXXXX)
   echo "📁 Generating files in: $TEMP_DIR"
   
   # Repository information
   REPO_OWNER=$(gh repo view --json owner -q .owner.login)
   REPO_NAME=$(gh repo view --json name -q .name)
   REPO_ID=$(gh api graphql -q '.data.repository.id' -f query='
     query { repository(owner: "'$REPO_OWNER'", name: "'$REPO_NAME'") { id } }
   ')
   ```

2. **Create data files** (following capture-todos patterns):
   - `milestones.json`
   - `projects.json`
   - `labels.json`
   - `parent_issues.json`
   - `child_issues.json`
   - `assignments.json` (batch assignments by feature/area)

3. **Generate GraphQL query files**:
   ```bash
   cat > $TEMP_DIR/link_project.graphql << 'EOF'
   mutation($projectId: ID!, $repoId: ID!) {
     linkProjectV2ToRepository(input: {
       projectId: $projectId
       repositoryId: $repoId
     }) {
       repository { name }
     }
   }
   EOF
   ```

4. **Create execution script** with:
   - Progress tracking
   - Parallel execution where possible
   - Error handling and logging
   - Rate limit management (exponential backoff, max 10 retries)
   - Deduplication (check existing projects/milestones)

### Phase 6: Preview & Approval

1. **Generate visual preview** (Mermaid diagram):
   ```mermaid
   graph TD
     P1[Project: Main Development]
     M1[Milestone: Core Features]
     M2[Milestone: Testing Framework]
     
     P1 --> M1
     P1 --> M2
     
     M1 --> I1[Parent: Authentication System]
     I1 --> I2[Child: Implement JWT]
     I1 --> I3[Child: Create login UI]
   ```

2. **Show creation summary**:
   ```
   📋 PLANNING SUMMARY
   ==================
   🎯 Milestones: X
   📊 Projects: Y
   🏷️ Labels: Z
   🐛 Parent Issues: A
   📝 Child Issues: B
   👥 Assignments: C batches
   
   Ready to review the script? (y/n)
   ```

3. **Offer options**:
   - Review generated script
   - Dry run (show what would be created)
   - Modify plan
   - Execute

### Phase 7: Execution & Tracking

1. **Execute with progress tracking**
2. **Log all operations**
3. **Handle failures gracefully**
4. **Generate summary report**

## Subcommand-Specific Features

### `init` - New Project Initialization

Additional gathering:
- Preferred programming language(s)
- License type (MIT, Apache, GPL, etc.)
- Package registry plans (npm, PyPI, crates.io, etc.)
- App store requirements

Additional actions:
1. **Create project scaffolding**:
   ```bash
   # Create README.md
   # Create LICENSE
   # Create .gitignore
   # Create directory structure
   ```

2. **Setup CI/CD** (with approval for each):
   - "Would you like GitHub Actions for testing? Here's what it would do..."
   - "Would you like automated releases? Here's the workflow..."

3. **Configure branch protection**:
   - Require PR reviews
   - Require status checks
   - Protect main branch

### `feature` - Feature Development

Additional gathering:
- Feature scope and boundaries
- User stories
- UI/UX requirements
- Performance targets

Additional actions:
1. **Create feature branch**:
   ```bash
   FEATURE_BRANCH="feature/$FEATURE_NAME"
   git checkout -b "$FEATURE_BRANCH"
   ```

2. **Feature flags** (if requested):
   - "Would you like to add feature flag configuration?"
   - Generate flag templates

3. **Documentation templates**:
   - Feature specification
   - API documentation
   - User guide template

### `fix` - Bug Fixes

Additional gathering:
- Bug reproduction steps
- Affected versions
- Severity assessment
- Workarounds available?

Additional actions:
1. **Link to bug reports**:
   ```bash
   # Search for related issues
   gh issue list --search "bug $KEYWORDS"
   ```

2. **Generate test templates**:
   - Regression test structure
   - Test cases for the fix

3. **Impact analysis**:
   ```bash
   # Find files that might be affected
   rg -l "$AFFECTED_FUNCTION" --type-add 'code:*.{js,ts,py,go,rs}'
   ```

### `refactor` - Code Refactoring

Additional gathering:
- Scope of refactoring
- Breaking changes?
- Migration requirements
- Performance goals

Additional actions:
1. **Create comparison docs**:
   - Before/after API
   - Migration examples
   - Breaking changes list

2. **Analyze test coverage**:
   ```bash
   # Check current coverage
   # Identify tests that need updates
   ```

3. **Version planning**:
   - Semantic version bump needed?
   - Migration timeline

### `clean` - Cleanup Plan Artifacts

Purpose: Remove artifacts created by the plan command, including local files and GitHub resources (with confirmation).

#### Cleanup Workflow

1. **Detect cleanup scope**:
   ```bash
   echo "🧹 Plan Cleanup Utility"
   echo "====================="
   echo ""
   echo "What would you like to clean?"
   echo "1) Local artifacts only (.plan directory)"
   echo "2) GitHub artifacts only (issues, milestones, projects)"
   echo "3) Everything (local + GitHub artifacts)"
   echo "4) List artifacts without removing"
   echo ""
   read -p "Select option (1-4): " CLEANUP_SCOPE
   ```

2. **Local artifact cleanup**:
   ```bash
   cleanup_local() {
     if [ -d ".plan" ]; then
       echo "📁 Found local plan directory:"
       du -sh .plan 2>/dev/null || echo "Size calculation unavailable"
       
       # List sessions
       if [ -d ".plan/sessions" ]; then
         echo ""
         echo "Sessions found:"
         ls -la .plan/sessions/
       fi
       
       read -p "Remove all local plan artifacts? (y/n): " CONFIRM
       if [ "$CONFIRM" = "y" ]; then
         rm -rf .plan
         echo "✅ Local artifacts removed"
       else
         echo "❌ Cleanup cancelled"
       fi
     else
       echo "ℹ️ No local artifacts found"
     fi
   }
   ```

3. **GitHub artifact discovery**:
   ```bash
   discover_github_artifacts() {
     echo "🔍 Scanning for GitHub artifacts created by plan command..."
     
     REPO_OWNER=$(gh repo view --json owner -q .owner.login)
     REPO_NAME=$(gh repo view --json name -q .name)
     
     # Check for plan metadata in sessions
     PLAN_SESSIONS=()
     if [ -d ".plan/sessions" ]; then
       for session in .plan/sessions/*/; do
         if [ -f "$session/plan_draft.json" ]; then
           PLAN_SESSIONS+=("$session")
         fi
       done
     fi
     
     # Find projects with naming pattern
     echo ""
     echo "📊 Projects:"
     gh project list --owner "$REPO_OWNER" --format json | \
       jq -r '.projects[] | select(.title | startswith("'$REPO_NAME' - ")) | 
       "  [\(.number)] \(.title) (items: \(.items.totalCount))"'
     
     # Find milestones (check for those created in recent sessions)
     echo ""
     echo "🎯 Milestones:"
     if [ ${#PLAN_SESSIONS[@]} -gt 0 ]; then
       # Try to match milestones from session files
       for session in "${PLAN_SESSIONS[@]}"; do
         if [ -f "$session/milestones.json" ]; then
           echo "  From session $(basename $session):"
           jq -r '.[] | "    [\(.title)]"' "$session/milestones.json" 2>/dev/null || true
         fi
       done
     fi
     gh api "repos/$REPO_OWNER/$REPO_NAME/milestones" --paginate | \
       jq -r '.[] | "  [\(.number)] \(.title) (open: \(.open_issues), closed: \(.closed_issues))"'
     
     # Find issues with plan labels or patterns
     echo ""
     echo "📝 Issues (checking multiple patterns):"
     
     # Pattern 1: plan-generated label
     echo "  With 'plan-generated' label:"
     gh issue list --label "plan-generated" --limit 100 --json number,title | \
       jq -r '.[] | "    #\(.number) \(.title)"'
     
     # Pattern 2: Issues created in batches (check for session references)
     if [ ${#PLAN_SESSIONS[@]} -gt 0 ]; then
       echo "  From plan sessions:"
       for session in "${PLAN_SESSIONS[@]}"; do
         if [ -f "$session/child_issues.json" ] || [ -f "$session/parent_issues.json" ]; then
           echo "    Session $(basename $session) has issue definitions"
         fi
       done
     fi
     
     # Count total artifacts
     PROJECT_COUNT=$(gh project list --owner "$REPO_OWNER" --format json | \
       jq '[.projects[] | select(.title | startswith("'$REPO_NAME' - "))] | length')
     MILESTONE_COUNT=$(gh api "repos/$REPO_OWNER/$REPO_NAME/milestones" --paginate | jq '. | length')
     ISSUE_COUNT=$(gh issue list --label "plan-generated" --limit 1000 --json number | jq '. | length')
     
     echo ""
     echo "📊 Total artifacts found:"
     echo "  Projects: $PROJECT_COUNT"
     echo "  Milestones: $MILESTONE_COUNT"
     echo "  Issues: $ISSUE_COUNT (with 'plan-generated' label)"
     echo "  Sessions: ${#PLAN_SESSIONS[@]}"
   }
   ```

4. **GitHub artifact removal**:
   ```bash
   cleanup_github() {
     discover_github_artifacts
     
     echo ""
     echo "⚠️  WARNING: This will permanently delete GitHub artifacts!"
     echo "This action cannot be undone."
     echo ""
     
     read -p "Type 'DELETE' to confirm removal of GitHub artifacts: " CONFIRM
     if [ "$CONFIRM" != "DELETE" ]; then
       echo "❌ GitHub cleanup cancelled"
       return
     fi
     
     # Detailed confirmation for each type
     echo ""
     echo "Select what to delete:"
     echo "1) All artifacts"
     echo "2) Projects only"
     echo "3) Milestones only"
     echo "4) Issues only"
     echo "5) Cancel"
     read -p "Selection: " DELETE_SCOPE
     
     case $DELETE_SCOPE in
       1) delete_all_github_artifacts ;;
       2) delete_projects ;;
       3) delete_milestones ;;
       4) delete_issues ;;
       *) echo "❌ Cancelled" ;;
     esac
   }
   ```

5. **Deletion functions**:
   ```bash
   delete_projects() {
     echo "🗑️ Deleting projects..."
     gh project list --owner "$REPO_OWNER" --format json | \
       jq -r '.projects[] | select(.title | startswith("'$REPO_NAME' - ")) | .number' | \
       while read -r PROJECT_NUM; do
         echo "  Deleting project #$PROJECT_NUM..."
         gh project delete "$PROJECT_NUM" --owner "$REPO_OWNER" --yes
       done
     echo "✅ Projects deleted"
   }
   
   delete_milestones() {
     echo "🗑️ Deleting milestones..."
     gh api "repos/$REPO_OWNER/$REPO_NAME/milestones" --paginate | \
       jq -r '.[] | .number' | \
       while read -r MILESTONE_NUM; do
         echo "  Deleting milestone #$MILESTONE_NUM..."
         gh api -X DELETE "repos/$REPO_OWNER/$REPO_NAME/milestones/$MILESTONE_NUM"
       done
     echo "✅ Milestones deleted"
   }
   
   delete_issues() {
     echo "🗑️ Closing and labeling issues for deletion..."
     gh issue list --label "plan-generated" --limit 1000 --json number | \
       jq -r '.[].number' | \
       while read -r ISSUE_NUM; do
         echo "  Processing issue #$ISSUE_NUM..."
         # Close issue and add deletion label
         gh issue close "$ISSUE_NUM"
         gh issue edit "$ISSUE_NUM" --add-label "deleted-by-plan-clean"
       done
     echo "✅ Issues closed and labeled"
     echo "ℹ️ Note: Issues are closed but not deleted (GitHub doesn't allow issue deletion)"
   }
   
   delete_all_github_artifacts() {
     echo "🗑️ Deleting all GitHub artifacts..."
     create_backup
     delete_projects
     delete_milestones
     delete_issues
     echo "✅ All GitHub artifacts processed"
   }
   ```

6. **Backup before deletion**:
   ```bash
   create_backup() {
     BACKUP_DIR=".plan/backups/$(date +%Y%m%d_%H%M%S)"
     mkdir -p "$BACKUP_DIR"
     
     echo "💾 Creating backup in $BACKUP_DIR..."
     
     # Export projects
     gh project list --owner "$REPO_OWNER" --format json > "$BACKUP_DIR/projects.json"
     
     # Export milestones
     gh api "repos/$REPO_OWNER/$REPO_NAME/milestones" --paginate > "$BACKUP_DIR/milestones.json"
     
     # Export issues
     gh issue list --label "plan-generated" --limit 1000 --json '*' > "$BACKUP_DIR/issues.json"
     
     echo "✅ Backup created"
   }
   ```

7. **Safety features**:
   - Always show what will be deleted before deletion
   - Require explicit confirmation (typing "DELETE")
   - Create backups before deletion
   - Provide granular control over what to delete
   - Log all operations

#### Usage Examples

```bash
# Clean everything (interactive)
/plan clean

# List artifacts without removing
/plan clean --list-only

# Clean local artifacts only
/plan clean --local-only

# Clean GitHub artifacts only
/plan clean --github-only

# Force cleanup without confirmation (dangerous!)
/plan clean --force

# Create backup without deleting
/plan clean --backup-only
```

## Advanced Features

### Templates System
1. **Check for templates**:
   ```bash
   TEMPLATE_DIR=".plan/templates/$SUBCOMMAND"
   if [ -d "$TEMPLATE_DIR" ]; then
     echo "📋 Available templates:"
     ls "$TEMPLATE_DIR"
     echo "Use a template? (name/n)"
   fi
   ```

2. **Common templates**:
   - Web API project
   - CLI tool
   - Library/package
   - Microservice
   - Mobile app

### Import from Markdown
```bash
if [ -f "$1" ]; then
  echo "📄 Importing requirements from: $1"
  # Parse markdown for requirements
  # Extract user stories
  # Generate initial task list
fi
```

### Notification Configuration
```bash
# Check for notification config
if [ -f ".plan/notifications.json" ]; then
  # Send notifications on completion
  # Slack webhook
  # Email via sendmail
  # GitHub notifications
fi
```

## Error Handling

1. **Rate limiting**:
   ```bash
   retry_with_backoff() {
     local retries=0
     local max_retries=10
     local delay=1
     
     while [ $retries -lt $max_retries ]; do
       if "$@"; then
         return 0
       fi
       
       echo "⏳ Rate limited. Waiting ${delay}s... (attempt $((retries+1))/$max_retries)"
       sleep $delay
       delay=$((delay * 2))
       retries=$((retries + 1))
     done
     
     echo "❌ Max retries reached. Saving progress..."
     save_progress
     return 1
   }
   ```

2. **Deduplication**:
   - Projects: Check by name pattern `[RepoName] -*`
   - Milestones: Update if exists
   - Issues: Check for similar titles

3. **Recovery**:
   - Save state after each major step
   - Allow resume from any point
   - Detailed error logging

## Usage Examples

```bash
# New project
/project:plan init

# Add a feature
/project:plan feature

# Plan a bug fix
/project:plan fix

# Plan a refactor
/project:plan refactor

# Clean up plan artifacts
/project:plan clean

# Resume a session
/project:plan --resume

# Use a template
/project:plan init --template web-api

# Import requirements
/project:plan feature requirements.md

# Dry run
/project:plan init --dry-run

# Clean with specific options
/project:plan clean --list-only
/project:plan clean --local-only
/project:plan clean --github-only
```

## Important Notes

1. **Always iterate** on requirements gathering - don't accept vague descriptions
2. **Think deeply** during task analysis - consider all aspects of implementation
3. **Batch operations** for efficiency - use parallel execution where possible
4. **Preserve context** - link all created items appropriately
5. **Handle failures gracefully** - always allow resume/retry

Remember: The goal is to transform high-level ideas into comprehensive, actionable project plans that accelerate development while maintaining quality and organization.