#!/bin/bash
# Backup creation for plan artifacts
# Extracted from plan/cleanup.md

create_backup() {
  BACKUP_DIR=".plan/backups/$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$BACKUP_DIR"
  
  echo "💾 Creating backup in $BACKUP_DIR..."
  
  # Get repository info
  REPO_OWNER=$(gh repo view --json owner -q .owner.login)
  REPO_NAME=$(gh repo view --json name -q .name)
  
  # Export projects
  gh project list --owner "$REPO_OWNER" --format json > "$BACKUP_DIR/projects.json"
  
  # Export milestones
  gh api "repos/$REPO_OWNER/$REPO_NAME/milestones" --paginate > "$BACKUP_DIR/milestones.json"
  
  # Export issues
  gh issue list --label "plan-generated" --limit 1000 --json '*' > "$BACKUP_DIR/issues.json"
  
  # Save session info if exists
  if [ -d ".plan/sessions" ]; then
    cp -r .plan/sessions "$BACKUP_DIR/sessions"
  fi
  
  echo "✅ Backup created"
  echo "📁 Location: $BACKUP_DIR"
  
  # Create backup manifest
  cat > "$BACKUP_DIR/manifest.txt" << EOF
Plan Artifacts Backup
Created: $(date)
Repository: $REPO_OWNER/$REPO_NAME

Contents:
- projects.json: GitHub project data
- milestones.json: Repository milestones
- issues.json: Issues with 'plan-generated' label
- sessions/: Local session data (if exists)
EOF
}