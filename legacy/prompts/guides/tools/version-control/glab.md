# GitLab CLI (glab) Reference Guide for Claude Code

## Overview
This guide provides essential information for assisting users with GitLab CLI (`glab`) operations. The GitLab CLI is the official command-line interface for interacting with GitLab repositories, issues, merge requests, and CI/CD pipelines.

## Core Concepts

### Authentication Context
- **Primary Command**: `glab auth login`
- **Key Understanding**: Authentication must be completed before any other operations
- **Common Issues**: Token permissions, self-hosted instance URLs
- **Helper Commands**: 
  - `glab auth status` - Check current authentication
  - `glab config set --global` - Configure default settings

### Command Structure Pattern
All glab commands follow this structure:
```
glab <resource> <action> [<id>] [flags]
```
Examples:
- `glab issue create`
- `glab pipeline view 12345`
- `glab mr list --assignee=@me`

## Essential Command Categories

### 1. Issue Management

**Core Operations:**
```bash
# Listing and filtering
glab issue list                          # All issues in current project
glab issue list --assignee=@me          # User's assigned issues
glab issue list --label="bug,critical"  # Multiple label filtering
glab issue list --state=closed          # Closed issues

# CRUD operations
glab issue create                        # Interactive creation
glab issue view <id>                    # Display issue details
glab issue update <id> --title "New"    # Update properties
glab issue close <id>                   # Close issue
glab issue reopen <id>                  # Reopen issue
glab issue delete <id>                  # Remove issue

# Advanced operations
glab issue note <id> -m "Comment"       # Add comment
glab issue subscribe <id>               # Subscribe to notifications
```

**Important Context:**
- Issue IDs are project-specific integers
- Labels must exist in the project before use
- The `@me` alias represents the authenticated user

### 2. Merge Request Operations

**Core Operations:**
```bash
# Creation and management
glab mr create                          # Interactive MR creation
glab mr create --fill                   # Auto-fill from commits
glab mr list --state=opened             # List open MRs
glab mr view <id>                       # Show MR details
glab mr checkout <id>                   # Check out MR branch locally

# Review workflow
glab mr diff <id>                       # View changes
glab mr approve <id>                    # Approve MR
glab mr revoke <id>                     # Revoke approval
glab mr merge <id>                      # Merge immediately
glab mr merge <id> --when-pipeline-succeeds  # Auto-merge

# MR options
--squash                                # Squash commits on merge
--remove-source-branch                  # Delete branch after merge
--draft                                 # Create as draft
```

**Key Relationships:**
- MRs can be linked to issues using `--issue <id>`
- Pipeline status affects merge availability
- Draft MRs cannot be merged until marked ready

### 3. CI/CD Pipeline Management

**Pipeline Operations:**
```bash
# Viewing pipelines
glab pipeline list                      # Recent pipelines
glab pipeline status                    # Latest pipeline status
glab pipeline view <id>                 # Detailed pipeline info
glab pipeline view <id> --jobs          # Show all jobs

# Pipeline control
glab pipeline run                       # Trigger new pipeline
glab pipeline retry <id>                # Retry failed pipeline
glab pipeline cancel <id>               # Stop running pipeline
glab pipeline delete <id>               # Remove pipeline record

# Job-specific commands
glab job view <job-id> --log           # View job output
glab job retry <job-id>                # Retry single job
glab job artifact <job-id>             # Download artifacts
glab job play <job-id>                 # Trigger manual job
```

**Understanding Pipeline States:**
- `created`: Pipeline created but not started
- `waiting_for_resource`: Waiting for runner
- `preparing`: Preparing job environment
- `pending`: Ready to run
- `running`: Currently executing
- `success`: Completed successfully
- `failed`: One or more jobs failed
- `canceled`: Manually stopped
- `skipped`: Skipped due to rules

### 4. Repository Operations

**Core Commands:**
```bash
# Repository info
glab repo view                          # Current repo details
glab repo clone <path>                  # Clone repository
glab repo fork                          # Create fork
glab repo archive                       # Download archive

# File operations
glab repo file <path>                   # View file contents
glab repo tree                          # List repository tree
```

### 5. Release Management

**Release Operations:**
```bash
glab release list                       # List all releases
glab release create <tag>               # Create new release
glab release view <tag>                 # View release details
glab release download <tag>             # Download release assets
glab release delete <tag>               # Remove release
```

## Advanced Features

### API Access
For operations not covered by specific commands:
```bash
glab api <endpoint>                     # GET request
glab api <endpoint> -X POST -f key=val  # POST with data
glab api graphql -f query=@file.graphql # GraphQL queries
```

Common API endpoints:
- `/projects/:id/boards` - Project boards
- `/projects/:id/milestones` - Milestones
- `/projects/:id/variables` - CI/CD variables

### Configuration Management
```bash
# Project-specific settings
glab config set --local remote.origin <url>

# Global preferences
glab config set --global editor vim
glab config set --global browser firefox

# CI/CD variables
glab variable set KEY "value" --masked --protected
glab variable list
glab variable delete KEY
```

## Common Workflows

### 1. Feature Development Flow
```bash
# Start feature
git checkout -b feature/new-feature
glab issue create --title "Implement feature"

# Work and commit changes
git add . && git commit -m "Add feature"
git push origin feature/new-feature

# Create MR linked to issue
glab mr create --fill --issue <issue-id>

# Monitor and merge
glab pipeline status
glab mr merge <mr-id> --squash --remove-source-branch
```

### 2. Pipeline Debugging Flow
```bash
# Check pipeline status
glab pipeline view <id> --jobs

# Find failed job
glab job view <job-id> --log | less

# Retry specific job or entire pipeline
glab job retry <job-id>  # OR
glab pipeline retry <id>
```

### 3. Issue Triage Flow
```bash
# List unassigned issues
glab issue list --assignee=none

# Bulk operations using shell
for id in $(glab issue list --label="bug" -F id); do
  glab issue update $id --label="in-progress"
done
```

## Error Handling Patterns

### Common Errors and Solutions

**Authentication Errors:**
- `401 Unauthorized`: Token expired or invalid - run `glab auth login`
- `403 Forbidden`: Insufficient permissions - check token scopes
- `404 Not Found`: Wrong project context - ensure correct repository

**Pipeline Errors:**
- `Pipeline cannot be retried`: Check if pipeline is retryable state
- `Job is not retryable`: Manual jobs or successful jobs cannot be retried
- `No runners available`: Project lacks configured runners

**Merge Request Errors:**
- `Cannot merge`: Check pipeline status, approvals, and conflicts
- `Source branch does not exist`: Branch was deleted or not pushed

## Integration Patterns

### Shell Scripting
```bash
# Get pipeline status for automation
if glab pipeline status | grep -q "failed"; then
  echo "Pipeline failed"
  exit 1
fi

# Extract data using JSON parsing
glab api projects/:id/pipelines | jq '.[0].status'
```

### Git Hooks Integration
```bash
# In .git/hooks/pre-push
#!/bin/bash
if ! glab pipeline status | grep -q "success"; then
  echo "Warning: Last pipeline did not succeed"
  read -p "Continue push? (y/n) " -n 1 -r
  echo
  [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi
```

## Performance Considerations

### Efficient Command Usage
- Use `--limit` flag for list operations to reduce output
- Prefer specific queries over broad searches
- Cache authentication tokens appropriately
- Use `--output json` for machine parsing

### Batch Operations
Instead of multiple individual calls:
```bash
# Inefficient
for id in 1 2 3; do glab issue close $id; done

# Better - using API
glab api projects/:id/issues/bulk_update -X PUT \
  -f "issue_ids[]=1" -f "issue_ids[]=2" -f "state=closed"
```

## Quick Reference Matrix

| Task | Command | Key Flags |
|------|---------|-----------|
| Create issue | `glab issue create` | `--title`, `--label`, `--assignee` |
| List my MRs | `glab mr list --assignee=@me` | `--state`, `--draft` |
| Check pipeline | `glab pipeline status` | `--branch` |
| View job logs | `glab job view <id> --log` | `--follow` |
| Trigger pipeline | `glab pipeline run` | `--ref`, `--variables` |
| Merge MR | `glab mr merge <id>` | `--squash`, `--when-pipeline-succeeds` |

## Important Notes for Claude Code

1. **Context Awareness**: Always verify the user is in a Git repository with GitLab remote before suggesting glab commands
2. **ID Requirements**: Most view/update commands require numeric IDs, not titles
3. **State Machines**: Understand resource states (issues, MRs, pipelines) to provide appropriate commands
4. **Permission Levels**: Many operations require specific GitLab permissions (Developer, Maintainer, etc.)
5. **API Fallback**: When glab doesn't have a specific command, use `glab api` with appropriate endpoints
6. **Error Interpretation**: Pipeline and job failures often require log examination for root cause
7. **Workflow Context**: Consider the user's current development stage when suggesting commands
