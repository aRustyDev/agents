---
name: capture-todos
description: Analyze TODO.md files in the repository and convert them to GitHub issues with proper organization
author: Claude Code
version: 2.0.0
---

# Capture TODOs Command

You will help analyze TODO.md files in this repository and convert them into well-organized GitHub issues. Follow these steps carefully:

## Phase 1: Discovery
1. Search for all TODO.md files in the repository using: `find . -name "TODO.md" -o -name "todo.md" | grep -v node_modules | grep -v .git`
2. List all found files and ask the user to confirm which ones to analyze

## Phase 2: Analysis
For each TODO.md file:
1. Read the file contents
2. Parse TODO items considering various formats:
   - Markdown headers as categories
   - List items (-, *, +, numbered)
   - Checkbox items [ ] (unchecked only)
   - Priority indicators ([HIGH], [!!], etc.)
   - Tags (#tag format)

## Phase 3: Git History Context
For each TODO item:
1. Use `git blame` to find when it was last modified
2. Use `git log -S` to track its evolution
3. Identify related code changes and commits
4. Note the context of when and why it was added

## Phase 4: Deduplication & Grouping
1. Identify similar or duplicate TODOs across files
2. Group related items by:
   - Category/header
   - Similar content
   - Common tags
   - Related functionality
3. Present grouped TODOs showing:
   - Original text
   - File location
   - Git context
   - Suggested grouping

## Phase 5: Interactive Validation
For each TODO or group:
1. Display the TODO with all context
2. If unclear or vague, ask for clarification:
   - "Fix the thing" → What specifically needs fixing?
   - Missing context → What is the goal?
   - Technical jargon → What does this mean?
3. Allow user to:
   - Clarify titles
   - Add descriptions
   - Skip items
   - Merge duplicates

## Phase 6: Issue Planning
Create a structured plan:

### Organizational Units
- **Milestones**: For groups with 5+ related items
- **Projects**: For groups with 10+ items or complex workflows
  - Projects MUST be linked to the current repository
  - Use repository-scoped projects for better integration
- **Labels**: Based on categories, priorities, and tags

### Issue Hierarchy
- **Parent Issues**: For groups of related TODOs
- **Individual Issues**: For each TODO
- **Sub-tasks**: For TODOs with nested items

### Issue Templates
For each issue, include:
- Clear, actionable title
- Description with context
- Source reference (file:line)
- Git history context
- Acceptance criteria
- Labels and categorization

## Phase 7: Plan Presentation
Present the complete plan showing:
```
📋 ISSUE CREATION PLAN
====================

🎯 Milestones to create: X
  - Milestone Name
    Description: ...

📊 Projects to create: Y
  - Project Name
    Description: ...

🐛 Issues to create: Z
  - Parent Issue: Title
    - Child: Specific task
    - Child: Another task
  - Standalone: Independent task

Labels to use: [list of labels]
```

## Phase 8: Generate Temporary Files
After plan approval, generate temporary files for batch processing:

1. **Create temp directory**:
   ```bash
   TEMP_DIR=$(mktemp -d /tmp/capture-todos.XXXXXX)
   echo "Created temp directory: $TEMP_DIR"
   ```

2. **Generate issue data files**:
   - `$TEMP_DIR/milestones.json` - All milestone data
   - `$TEMP_DIR/projects.json` - Project creation data
   - `$TEMP_DIR/labels.json` - Label definitions
   - `$TEMP_DIR/parent_issues.json` - Parent issue data
   - `$TEMP_DIR/child_issues.json` - Child issue data with parent references
   - `$TEMP_DIR/project_mappings.json` - Issue-to-project mappings

3. **Example milestone file structure**:
   ```json
   [
     {
       "title": "Testing & Quality Framework",
       "description": "Implement comprehensive testing workflows",
       "due_on": "2025-09-30T23:59:59Z"
     }
   ]
   ```

4. **Example issue file structure**:
   ```json
   [
     {
       "title": "Testing Framework Enhancement",
       "body": "## Summary\n\nImplement testing...",
       "labels": ["enhancement", "testing"],
       "milestone": "Testing & Quality Framework",
       "assignee": "@me",
       "project_numbers": [17],
       "temp_id": "parent_1",
       "children": ["child_1", "child_2"]
     }
   ]
   ```

## Phase 9: Generate Batch Execution Script
Create an optimized script for parallel execution:

1. **Generate GraphQL query files** to avoid escaping issues:
   ```bash
   # Create GraphQL files
   cat > $TEMP_DIR/get_project_id.graphql << 'EOF'
   query($url: URI!) {
     resource(url: $url) {
       ... on ProjectV2 {
         id
       }
     }
   }
   EOF
   
   cat > $TEMP_DIR/link_project.graphql << 'EOF'
   mutation($projectId: ID!, $repoId: ID!) {
     linkProjectV2ToRepository(input: {
       projectId: $projectId
       repositoryId: $repoId
     }) {
       repository {
         name
       }
     }
   }
   EOF
   ```

2. **Generate the main execution script** at `$TEMP_DIR/execute_batch.sh`:
   ```bash
   #!/bin/bash
   set -euo pipefail
   
   # Configuration
   REPO_OWNER="<owner>"
   REPO_NAME="<repo>"
   REPO_ID="<repo_id>"
   TEMP_DIR="<temp_dir>"
   LOG_FILE="$TEMP_DIR/execution.log"
   
   # Initialize counters
   TOTAL_OPERATIONS=<total>
   CURRENT=0
   SUCCESSES=0
   FAILURES=0
   
   # Logging functions
   log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
   progress() { CURRENT=$((CURRENT + 1)); log "[$CURRENT/$TOTAL_OPERATIONS] $1"; }
   success() { SUCCESSES=$((SUCCESSES + 1)); log "✅ SUCCESS: $1"; }
   error() { FAILURES=$((FAILURES + 1)); log "❌ ERROR: $1" >&2; }
   
   # Step 1: Create labels
   log "Creating labels..."
   jq -c '.[]' "$TEMP_DIR/labels.json" | while read label; do
     progress "Creating label $(echo $label | jq -r .name)"
     gh label create $(echo $label | jq -r '
       "--name \(.name) --color \(.color) --description \"\(.description)\" --force"
     ') 2>&1 | tee -a "$LOG_FILE" && success "Label created" || error "Failed to create label"
   done
   
   # Step 2: Create milestones in parallel
   log "Creating milestones..."
   jq -c '.[]' "$TEMP_DIR/milestones.json" | \
   parallel -j 5 --bar "
     echo {} | jq -r '\"Creating milestone: \" + .title' >&2
     gh api repos/$REPO_OWNER/$REPO_NAME/milestones \
       -f title='{}' \
       -f description='{}' \
       -f due_on='{}' \
       -f state='open' 2>&1 || echo 'FAILED: {}'
   " | tee -a "$LOG_FILE"
   
   # Step 3: Create projects and link to repository
   log "Creating and linking projects..."
   jq -c '.[]' "$TEMP_DIR/projects.json" | while read project; do
     TITLE=$(echo $project | jq -r .title)
     progress "Creating project: $TITLE"
     
     # Create project
     PROJECT_JSON=$(gh project create --owner @me --title "$TITLE" --format json 2>&1)
     if [ $? -eq 0 ]; then
       PROJECT_NUMBER=$(echo "$PROJECT_JSON" | jq -r .number)
       PROJECT_ID=$(echo "$PROJECT_JSON" | jq -r .id)
       
       # Link to repository
       gh api graphql -F projectId="$PROJECT_ID" -F repoId="$REPO_ID" \
         -F query=@"$TEMP_DIR/link_project.graphql" 2>&1 | tee -a "$LOG_FILE"
       
       # Save project mapping
       echo "{\"title\": \"$TITLE\", \"number\": $PROJECT_NUMBER}" >> "$TEMP_DIR/project_numbers.json"
       success "Project $TITLE created as #$PROJECT_NUMBER"
     else
       error "Failed to create project $TITLE"
     fi
   done
   
   # Step 4: Create parent issues
   log "Creating parent issues..."
   PARENT_MAP="$TEMP_DIR/parent_issue_map.json"
   echo "{}" > "$PARENT_MAP"
   
   jq -c '.[]' "$TEMP_DIR/parent_issues.json" | while read issue; do
     TEMP_ID=$(echo $issue | jq -r .temp_id)
     progress "Creating parent issue: $(echo $issue | jq -r .title)"
     
     ISSUE_URL=$(echo $issue | jq -r '
       "gh issue create --title \"" + .title + 
       "\" --body \"" + (.body | @json | .[1:-1]) + 
       "\" --label \"" + (.labels | join(",")) + 
       "\" --assignee " + .assignee +
       (if .milestone then " --milestone \"" + .milestone + "\"" else "" end)
     ' | sh 2>&1)
     
     if [ $? -eq 0 ]; then
       ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
       jq --arg id "$TEMP_ID" --arg num "$ISSUE_NUMBER" \
         '.[$id] = $num' "$PARENT_MAP" > "$PARENT_MAP.tmp" && mv "$PARENT_MAP.tmp" "$PARENT_MAP"
       success "Created parent issue #$ISSUE_NUMBER"
       
       # Add to projects
       echo $issue | jq -r '.project_numbers[]' | while read proj_num; do
         gh project item-add "$proj_num" --owner @me --url "$ISSUE_URL" 2>&1 | tee -a "$LOG_FILE"
       done
     else
       error "Failed to create parent issue"
     fi
   done
   
   # Step 5: Create child issues with parent references
   log "Creating child issues..."
   jq -c '.[]' "$TEMP_DIR/child_issues.json" | while read issue; do
     PARENT_TEMP_ID=$(echo $issue | jq -r .parent_temp_id)
     PARENT_NUMBER=$(jq -r --arg id "$PARENT_TEMP_ID" '.[$id]' "$PARENT_MAP")
     
     progress "Creating child issue: $(echo $issue | jq -r .title)"
     
     # Update body with parent reference
     BODY=$(echo $issue | jq -r --arg pnum "$PARENT_NUMBER" '
       .body + "\n\nParent issue: #" + $pnum
     ')
     
     ISSUE_URL=$(echo $issue | jq -r --arg body "$BODY" '
       "gh issue create --title \"" + .title + 
       "\" --body \"" + ($body | @json | .[1:-1]) + 
       "\" --label \"" + (.labels | join(",")) + 
       "\" --assignee " + .assignee +
       (if .milestone then " --milestone \"" + .milestone + "\"" else "" end)
     ' | sh 2>&1)
     
     if [ $? -eq 0 ]; then
       success "Created child issue"
       # Add to projects
       echo $issue | jq -r '.project_numbers[]' | while read proj_num; do
         gh project item-add "$proj_num" --owner @me --url "$ISSUE_URL" 2>&1 | tee -a "$LOG_FILE"
       done
     else
       error "Failed to create child issue"
     fi
   done
   
   # Final summary
   log "
   ====================================
   EXECUTION COMPLETE
   ====================================
   Total operations: $TOTAL_OPERATIONS
   Successful: $SUCCESSES
   Failed: $FAILURES
   Success rate: $((SUCCESSES * 100 / TOTAL_OPERATIONS))%
   ===================================="
   ```

3. **Add validation and retry logic**:
   - Validate JSON files before execution
   - Retry failed operations up to 3 times
   - Generate detailed error report

4. **Include parallel processing where possible**:
   - Use GNU parallel for milestone creation
   - Batch API calls where supported
   - Process independent operations concurrently

## Phase 10: Approval & Execution
1. **Review generated files**:
   ```bash
   echo "📁 Generated files in $TEMP_DIR:"
   ls -la $TEMP_DIR/
   echo ""
   echo "Review the generated script:"
   cat $TEMP_DIR/execute_batch.sh
   ```

2. **Ask for final approval**: "Ready to execute the batch creation script? (y/n)"

3. **If approved, execute the script**:
   ```bash
   chmod +x $TEMP_DIR/execute_batch.sh
   $TEMP_DIR/execute_batch.sh 2>&1 | tee $TEMP_DIR/execution.log
   ```

4. **Monitor progress**:
   - Show real-time progress updates
   - Log all operations to `$TEMP_DIR/execution.log`
   - Track successful and failed operations

5. **Generate summary report**:
   ```bash
   echo "📊 Execution Summary:"
   echo "✅ Successful operations: $(grep -c "success" $TEMP_DIR/execution.log)"
   echo "❌ Failed operations: $(grep -c "error" $TEMP_DIR/execution.log)"
   ```

## Phase 11: Update TODO.md
After successful execution:

1. **Create backup**:
   ```bash
   cp TODO.md $TEMP_DIR/TODO.md.backup
   ```

2. **Update TODO.md**:
   - Mark all captured items with strikethrough
   - Add issue numbers for each item
   - Add capture metadata header
   - Preserve file structure for future additions

3. **Example updated format**:
   ```markdown
   # TODO
   
   <!-- Captured by Claude on YYYY-MM-DD -->
   <!-- Total issues created: X (Y parent + Z child issues) -->
   <!-- Projects: #A, #B | Milestones: C, D, E, F -->
   
   ## ✅ CAPTURED ITEMS
   
   ### Category Name (Issue #N)
   - ~~Original TODO item~~ → Issue #M
   
   ## 📝 NEW TODO ITEMS
   <!-- Add new TODO items below this line -->
   ```

## Phase 12: Cleanup
Clean up all temporary files and artifacts:

1. **Save important artifacts** (optional):
   ```bash
   echo "Would you like to save the execution log? (y/n)"
   # If yes, copy to project directory
   ```

2. **Clean up temp directory**:
   ```bash
   echo "🧹 Cleaning up temporary files..."
   rm -rf $TEMP_DIR
   echo "✅ Cleanup complete"
   ```

3. **Final summary**:
   - Total issues created
   - Projects and milestones created
   - Link to view all created issues
   - Suggest next steps

## Important Guidelines

### DO:
- Preserve ALL context from git history
- Ask for clarification on vague items
- Group intelligently
- Create hierarchical structure
- Use descriptive titles
- Reference source locations

### DON'T:
- Create issues without approval
- Skip validation for unclear items
- Lose track of source files
- Create duplicate issues
- Ignore git context

## Error Handling
- If `gh` CLI isn't available, provide instructions for installation
- If not in a git repository, skip git analysis
- If no TODO files found, inform user and suggest locations

## Example Interaction
```
User: /project:capture-todos

Claude: 🔍 Searching for TODO.md files...
Found 3 TODO files:
1. ./TODO.md
2. ./docs/TODO.md  
3. ./src/TODO.md

Shall I analyze all of these? (y/n)

[User confirms]

📝 Analyzing ./TODO.md...
Found 12 TODO items in 4 categories...

[After analysis and planning]

📋 ISSUE CREATION PLAN
====================
🎯 Milestones: 4
📊 Projects: 2  
🐛 Issues: 85 (17 parent + 68 child)
🏷️ Labels: 9

Ready to create these issues? (y/n)

[User confirms]

📁 Generating temporary files...
Created temp directory: /tmp/capture-todos.Xa8kL9
✅ Generated: milestones.json (4 items)
✅ Generated: projects.json (2 items)
✅ Generated: labels.json (9 items)
✅ Generated: parent_issues.json (17 items)
✅ Generated: child_issues.json (68 items)
✅ Generated: execute_batch.sh

Review the generated script? (y/n)

[User reviews]

Ready to execute the batch creation script? (y/n)

[User confirms]

🚀 Executing batch creation...
[1/103] Creating label: enhancement
[2/103] Creating label: testing
...
[10/103] Creating milestone: Testing & Quality Framework
...
[15/103] Creating project: Claude Code Enhancement Suite
✅ Project created as #17 and linked to repository
...
[32/103] Creating parent issue: Testing Framework Enhancement
✅ Created parent issue #1
...
[85/103] Creating child issue: Implement Political/Campaign roles suite
✅ Created child issue #85

====================================
EXECUTION COMPLETE
====================================
Total operations: 103
Successful: 103
Failed: 0
Success rate: 100%
====================================

📝 Updating TODO.md...
✅ TODO.md updated with 85 captured items

Would you like to save the execution log? (y/n)

[If user declines]

🧹 Cleaning up temporary files...
✅ Cleanup complete

🎉 TODO capture complete! View your issues at:
https://github.com/owner/repo/issues
```

## Implementation Notes

### Batch Processing Benefits
1. **Speed**: Parallel execution reduces time from hours to minutes
2. **Reliability**: Failed operations are logged and can be retried
3. **Visibility**: Progress tracking and detailed logging
4. **Atomicity**: All data generated before execution begins

### GraphQL Query Management
The script uses separate GraphQL files to avoid shell escaping issues:
- `get_project_id.graphql`: Retrieves project ID from URL
- `link_project.graphql`: Links project to repository

### Error Recovery
- All operations logged to `execution.log`
- Failed operations can be retried individually
- Parent-child relationships preserved even if some operations fail
- Summary report shows success/failure counts

### Performance Optimizations
1. **Parallel milestone creation**: Uses GNU parallel with 5 concurrent jobs
2. **Batch label creation**: All labels created before issues
3. **Efficient project linking**: Projects created and linked in single workflow
4. **Streaming processing**: Uses jq streaming for large JSON files

### Required Tools
- `gh`: GitHub CLI (latest version)
- `jq`: JSON processor
- `parallel`: GNU parallel (optional but recommended)
- `mktemp`: For secure temp directory creation

### Troubleshooting Common Issues

1. **GraphQL Errors**: Check that GraphQL files were created correctly
2. **Authentication**: Ensure `gh auth status` shows active session
3. **Rate Limits**: Script includes delays between operations if needed
4. **Project Permissions**: User must have permission to create projects
5. **Milestone Names**: Must be unique within repository

Remember: The goal is to transform scattered TODO items into a well-organized, actionable issue tracking system that preserves context and facilitates project management.