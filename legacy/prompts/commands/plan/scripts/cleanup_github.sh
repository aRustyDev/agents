#!/bin/bash
# GitHub artifact cleanup functions
# Extracted from plan/cleanup.md

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
  
  # Find milestones
  echo ""
  echo "🎯 Milestones:"
  gh api "repos/$REPO_OWNER/$REPO_NAME/milestones" --paginate | \
    jq -r '.[] | "  [\(.number)] \(.title) (open: \(.open_issues), closed: \(.closed_issues))"'
  
  # Find issues with plan labels
  echo ""
  echo "📝 Issues:"
  echo "  With 'plan-generated' label:"
  gh issue list --label "plan-generated" --limit 100 --json number,title | \
    jq -r '.[] | "    #\(.number) \(.title)"'
  
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
    5) echo "❌ Cancelled" ;;
    *) echo "❌ Invalid selection" ;;
  esac
}

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
  echo "🗑️ Closing issues with 'plan-generated' label..."
  gh issue list --label "plan-generated" --limit 1000 --json number | \
    jq -r '.[].number' | \
    while read -r ISSUE_NUM; do
      echo "  Closing issue #$ISSUE_NUM..."
      gh issue close "$ISSUE_NUM" --comment "Closed by plan cleanup command"
    done
  echo "✅ Issues closed"
}

delete_all_github_artifacts() {
  delete_projects
  delete_milestones
  delete_issues
}