#!/bin/bash
# Plan execution script
# Extracted from implementation.md

# Pre-execution checks
pre_execution_checks() {
  # Verify GitHub CLI is authenticated
  if ! gh auth status &>/dev/null; then
      echo "❌ Error: Not authenticated with GitHub CLI"
      echo "Run: gh auth login"
      exit 1
  fi

  # Verify we're in a git repository
  if ! git rev-parse --git-dir &>/dev/null; then
      echo "❌ Error: Not in a git repository"
      exit 1
  fi

  # Check repository access
  if ! gh repo view &>/dev/null; then
      echo "❌ Error: Cannot access repository"
      exit 1
  fi
}

# Create labels from JSON
create_labels() {
  local labels_file=$1
  echo "🏷️  Creating labels..."
  
  for label in $(jq -r '.[] | @base64' "$labels_file"); do
      _jq() {
          echo ${label} | base64 --decode | jq -r ${1}
      }
      
      name=$(_jq '.name')
      color=$(_jq '.color')
      description=$(_jq '.description')
      
      if gh label create "$name" --color "$color" --description "$description" 2>/dev/null; then
          echo "  ✅ Created label: $name"
      else
          echo "  ⏭️  Label exists: $name"
      fi
  done
}

# Create milestones from JSON
create_milestones() {
  local milestones_file=$1
  echo "🎯 Creating milestones..."
  
  MILESTONE_MAP="{}"
  
  for milestone in $(jq -r '.[] | @base64' "$milestones_file"); do
      _jq() {
          echo ${milestone} | base64 --decode | jq -r ${1}
      }
      
      title=$(_jq '.title')
      description=$(_jq '.description')
      due_on=$(_jq '.due_on // empty')
      
      # Create milestone with gh CLI
      if [ -n "$due_on" ]; then
          result=$(gh api repos/:owner/:repo/milestones \
              --method POST \
              --field title="$title" \
              --field description="$description" \
              --field due_on="$due_on" 2>/dev/null || echo "{}")
      else
          result=$(gh api repos/:owner/:repo/milestones \
              --method POST \
              --field title="$title" \
              --field description="$description" 2>/dev/null || echo "{}")
      fi
      
      if [ -n "$result" ] && [ "$result" != "{}" ]; then
          milestone_number=$(echo "$result" | jq -r '.number')
          MILESTONE_MAP=$(echo "$MILESTONE_MAP" | jq ". + {\"$title\": $milestone_number}")
          echo "  ✅ Created milestone: $title (#$milestone_number)"
      else
          # Try to find existing milestone
          existing=$(gh api repos/:owner/:repo/milestones --paginate | jq -r ".[] | select(.title == \"$title\") | .number" | head -1)
          if [ -n "$existing" ]; then
              MILESTONE_MAP=$(echo "$MILESTONE_MAP" | jq ". + {\"$title\": $existing}")
              echo "  ⏭️  Milestone exists: $title (#$existing)"
          else
              echo "  ❌ Failed to create milestone: $title"
          fi
      fi
  done
  
  echo "$MILESTONE_MAP"
}

# Create issues from JSON
create_issues() {
  local issues_file=$1
  local milestone_map=$2
  echo "📝 Creating issues..."
  
  issue_count=0
  total_issues=$(jq '. | length' "$issues_file")
  
  for issue in $(jq -r '.[] | @base64' "$issues_file"); do
      _jq() {
          echo ${issue} | base64 --decode | jq -r ${1}
      }
      
      title=$(_jq '.title')
      body=$(_jq '.body')
      labels=$(_jq '.labels | join(",")')
      milestone_title=$(_jq '.milestone // empty')
      assignees=$(_jq '.assignees // empty | join(",")')
      
      # Build gh issue create command
      cmd="gh issue create --title \"$title\" --body \"$body\""
      
      [ -n "$labels" ] && cmd="$cmd --label \"$labels\""
      [ -n "$assignees" ] && cmd="$cmd --assignee \"$assignees\""
      
      # Map milestone title to number
      if [ -n "$milestone_title" ]; then
          milestone_number=$(echo "$milestone_map" | jq -r ".\"$milestone_title\" // empty")
          [ -n "$milestone_number" ] && [ "$milestone_number" != "null" ] && cmd="$cmd --milestone \"$milestone_number\""
      fi
      
      # Execute command
      if eval "$cmd" >/dev/null 2>&1; then
          ((issue_count++))
          echo "  ✅ Created issue: $title"
      else
          echo "  ❌ Failed to create issue: $title"
      fi
      
      # Show progress
      progress=$((issue_count * 100 / total_issues))
      echo -ne "\r  Progress: [$progress%] $issue_count/$total_issues issues created"
  done
  
  echo ""
  echo "✅ Created $issue_count issues"
}

# Create GitHub project
create_project() {
  local project_file=$1
  echo "📊 Creating project board..."
  
  if [ -f "$project_file" ]; then
      title=$(jq -r '.title' "$project_file")
      body=$(jq -r '.body // empty' "$project_file")
      
      # Create project
      project_id=$(gh project create --owner "@me" --title "$title" --body "$body" --format json | jq -r '.id')
      
      if [ -n "$project_id" ] && [ "$project_id" != "null" ]; then
          echo "  ✅ Created project: $title"
          
          # Add fields/columns if specified
          if [ -n "$(jq -r '.columns // empty' "$project_file")" ]; then
              for column in $(jq -r '.columns[]' "$project_file"); do
                  gh project field-create "$project_id" --owner "@me" --name "$column" --data-type "TEXT" 2>/dev/null || true
              done
          fi
          
          echo "$project_id"
      else
          echo "  ❌ Failed to create project"
          echo ""
      fi
  fi
}

# Main execution function
execute_plan() {
  local session_dir=$1
  
  echo "🚀 Starting plan execution..."
  
  # Run pre-execution checks
  pre_execution_checks
  
  # Create artifacts in order
  [ -f "$session_dir/labels.json" ] && create_labels "$session_dir/labels.json"
  
  milestone_map="{}"
  [ -f "$session_dir/milestones.json" ] && milestone_map=$(create_milestones "$session_dir/milestones.json")
  
  [ -f "$session_dir/issues.json" ] && create_issues "$session_dir/issues.json" "$milestone_map"
  
  [ -f "$session_dir/project.json" ] && create_project "$session_dir/project.json"
  
  echo ""
  echo "✅ Plan execution complete!"
}

# Handle execution based on arguments
if [ "$1" = "execute" ] && [ -n "$2" ]; then
  execute_plan "$2"
fi