#!/bin/bash
# Error handling functions for plan command
# Extracted from implementation.md

# Error recovery functions
handle_execution_error() {
  local error_type=$1
  local error_details=$2
  local session_dir=$3
  
  echo "❌ Execution error: $error_type"
  echo "Details: $error_details"
  
  case $error_type in
    "auth")
      echo "Solution: Run 'gh auth login' and try again"
      ;;
    "permission")
      echo "Solution: Check repository permissions"
      ;;
    "network")
      echo "Solution: Check internet connection and GitHub status"
      ;;
    "duplicate")
      echo "Solution: Some items already exist, continuing..."
      ;;
    *)
      echo "Solution: Check error details and try again"
      ;;
  esac
  
  # Save error state for recovery
  echo "{
    \"error_type\": \"$error_type\",
    \"error_details\": \"$error_details\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"session\": \"$session_dir\"
  }" > "$session_dir/error_state.json"
}

# Rollback functions
rollback_labels() {
  local labels_file=$1
  echo "🔄 Rolling back labels..."
  
  for label in $(jq -r '.[].name' "$labels_file"); do
    gh label delete "$label" --yes 2>/dev/null || true
  done
}

rollback_milestones() {
  local milestone_map=$1
  echo "🔄 Rolling back milestones..."
  
  echo "$milestone_map" | jq -r 'to_entries[] | .value' | while read -r number; do
    gh api -X DELETE "repos/:owner/:repo/milestones/$number" 2>/dev/null || true
  done
}

rollback_issues() {
  local session_dir=$1
  echo "🔄 Rolling back issues..."
  
  # Find issues created in this session
  gh issue list --label "plan-generated" --json number,createdAt | \
    jq -r --arg session "$session_dir" '.[] | select(.createdAt > $session) | .number' | \
    while read -r issue_num; do
      gh issue close "$issue_num" --comment "Rolled back by plan command" 2>/dev/null || true
    done
}

# Recovery functions
recover_from_partial() {
  local session_dir=$1
  local recovery_point=$2
  
  echo "🔧 Recovering from partial execution..."
  echo "Recovery point: $recovery_point"
  
  case $recovery_point in
    "labels")
      echo "Labels created successfully, continuing from milestones..."
      ;;
    "milestones")
      echo "Milestones created successfully, continuing from issues..."
      ;;
    "issues")
      echo "Issues created successfully, continuing from project..."
      ;;
    *)
      echo "Unknown recovery point, starting fresh..."
      ;;
  esac
}

# Validation before execution
validate_plan_data() {
  local session_dir=$1
  
  echo "✓ Validating plan data..."
  
  # Check required files
  local errors=0
  
  if [ ! -f "$session_dir/issues.json" ]; then
    echo "  ❌ Missing issues.json"
    ((errors++))
  else
    # Validate JSON structure
    if ! jq empty "$session_dir/issues.json" 2>/dev/null; then
      echo "  ❌ Invalid JSON in issues.json"
      ((errors++))
    fi
  fi
  
  if [ ! -f "$session_dir/milestones.json" ] && jq -r '.[].milestone // empty' "$session_dir/issues.json" | grep -q .; then
    echo "  ⚠️  Issues reference milestones but milestones.json missing"
  fi
  
  if [ $errors -gt 0 ]; then
    echo "❌ Validation failed with $errors errors"
    return 1
  else
    echo "✅ Validation passed"
    return 0
  fi
}

# Safe execution wrapper
safe_execute() {
  local command=$1
  local error_handler=$2
  
  if ! eval "$command" 2>/tmp/plan_error.log; then
    local error_msg=$(cat /tmp/plan_error.log)
    $error_handler "$error_msg"
    return 1
  fi
  
  return 0
}

# Export functions for use by other scripts
export -f handle_execution_error
export -f rollback_labels
export -f rollback_milestones
export -f rollback_issues
export -f recover_from_partial
export -f validate_plan_data
export -f safe_execute