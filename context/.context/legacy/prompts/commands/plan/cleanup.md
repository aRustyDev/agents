---
module: PlanCleanup  
scope: context
triggers: 
  - "/plan clean"
  - "cleanup plan"
  - "remove plan artifacts"
conflicts: []
dependencies:
  - _core.md
  - scripts/cleanup_local.sh
  - scripts/cleanup_github.sh
  - scripts/backup_artifacts.sh
priority: high
---

# PlanCleanup - Plan Artifact Cleanup

## Purpose
Remove artifacts created by the plan command, including local files and GitHub resources with proper confirmation and backup.

## Overview
This module provides safe cleanup functionality for both local planning sessions and GitHub artifacts created by the plan command.

## Cleanup Workflow

### Step 1: Detect Cleanup Scope

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

### Step 2: Handle Cleanup Options

Based on user selection:
- **Option 1**: Clean local artifacts only
- **Option 2**: Clean GitHub artifacts only
- **Option 3**: Clean both local and GitHub artifacts
- **Option 4**: List all artifacts without deletion

## Local Artifact Cleanup

Local cleanup functions handle the removal of `.plan` directory and session artifacts.

**Implementation**: See `scripts/cleanup_local.sh`

Key functions:
- `cleanup_local()` - Remove all local artifacts
- `archive_session()` - Archive instead of delete
- `list_sessions()` - Show all plan sessions

## GitHub Artifact Discovery

Discovers all GitHub artifacts created by the plan command including projects, milestones, and issues.

**Implementation**: See `scripts/cleanup_github.sh`

Artifacts discovered:
- Projects with repo name prefix
- All milestones
- Issues with 'plan-generated' label
- Local sessions with metadata

## GitHub Artifact Removal

Safely removes GitHub artifacts with multiple confirmation steps.

**Implementation**: See `scripts/cleanup_github.sh`

Key functions:
- `cleanup_github()` - Interactive GitHub cleanup
- `delete_projects()` - Remove GitHub projects
- `delete_milestones()` - Remove milestones
- `delete_issues()` - Close issues (not deleted)
- `delete_all_github_artifacts()` - Remove all artifacts

## Deletion Functions

The cleanup command provides granular control over what to delete:

1. **Projects**: Removes projects with repository name prefix
2. **Milestones**: Deletes all milestones in the repository
3. **Issues**: Closes (not deletes) issues with 'plan-generated' label
4. **All**: Performs all cleanup operations with backup

**Implementation**: See `scripts/cleanup_github.sh` for all deletion functions

### Safety Notes
- Projects are permanently deleted
- Milestones are permanently deleted
- Issues are closed and labeled but not deleted (GitHub limitation)
- Automatic backup before bulk deletion

## Backup Creation

Automatic backup creation before any deletion operation.

**Implementation**: See `scripts/backup_artifacts.sh`

Backup includes:
- All GitHub projects (JSON export)
- Repository milestones (JSON export)
- Issues with 'plan-generated' label
- Local session data
- Backup manifest with metadata

Backups are stored in `.plan/backups/` with timestamp directories.

## Safety Features

1. **Preview before deletion**: Always show what will be deleted
2. **Explicit confirmation**: Require typing "DELETE" for GitHub artifacts
3. **Automatic backup**: Create backups before any deletion
4. **Selective deletion**: Allow choosing specific artifact types
5. **Non-destructive issues**: Close issues instead of deleting

## Usage Examples

```bash
# Clean everything (interactive)
/plan clean

# List artifacts without removing
/plan clean --list

# Clean local artifacts only
/plan clean --local

# Clean GitHub artifacts only
/plan clean --github

# Force cleanup without confirmation (dangerous!)
/plan clean --force

# Create backup without deleting
/plan clean --backup-only
```

## Integration

This module:
- Works independently of other plan phases
- Uses utilities from `_core.md`
- Integrates with GitHub CLI for artifact management
- Scripts in `scripts/` for modularity

## Script Files

- `scripts/cleanup_local.sh` - Local artifact management
- `scripts/cleanup_github.sh` - GitHub artifact management
- `scripts/backup_artifacts.sh` - Backup creation
- `scripts/cleanup_session.sh` - Session-specific cleanup

## Best Practices

1. **Always backup first**: Never skip the backup step
2. **Review before deletion**: Check what will be removed
3. **Use plan-generated label**: Makes cleanup easier
4. **Document sessions**: Keep records of what was created
5. **Periodic cleanup**: Don't let artifacts accumulate