---
name: interactive-selection
description: Interactive UI for browsing and selecting work items with preference learning
version: 1.0.0
type: process
scope: temporary
conditional: true
---

# Interactive Selection UI Process

## Purpose
Provide an interactive interface for browsing work items one by one, allowing users to accept, reject, or skip items while learning preferences over time to improve future recommendations.

## Core Features
- One-by-one item presentation
- Accept/Reject/Skip actions with reason tracking
- Real-time filtering and search
- Preference learning and persistence
- Keyboard shortcuts for efficiency

## Interactive UI Components

### Terminal UI Handler
```bash
# Main interactive selection loop
interactive_select_items() {
  local items="$1"
  local session_file="${HOME}/.claude/cache/interactive-session.json"
  local prefs_file="${HOME}/.claude/data/work-preferences.json"
  
  # Initialize session
  init_interactive_session "$session_file" "$items"
  
  # Clear screen and show instructions
  clear
  show_interactive_instructions
  
  local current_index=0
  local total_items=$(echo "$items" | jq 'length')
  local selected_items="[]"
  local rejected_items="[]"
  
  while [[ $current_index -lt $total_items ]]; do
    local item=$(echo "$items" | jq ".[$current_index]")
    
    # Display current item
    clear
    display_item_interactive "$item" "$((current_index + 1))" "$total_items"
    
    # Get user action
    local action=$(get_user_action)
    
    case "$action" in
      "a"|"accept")
        selected_items=$(echo "$selected_items" | jq ". + [$item]")
        record_preference "$item" "accepted" "" "$prefs_file"
        ((current_index++))
        ;;
        
      "r"|"reject")
        local reason=$(get_rejection_reason)
        rejected_items=$(echo "$rejected_items" | jq --arg reason "$reason" ". + [{item: $item, reason: \$reason}]")
        record_preference "$item" "rejected" "$reason" "$prefs_file"
        ((current_index++))
        ;;
        
      "s"|"skip")
        ((current_index++))
        ;;
        
      "b"|"back")
        if [[ $current_index -gt 0 ]]; then
          ((current_index--))
        fi
        ;;
        
      "f"|"filter")
        apply_interactive_filter "$items" "$current_index"
        ;;
        
      "i"|"info")
        show_detailed_info "$item"
        ;;
        
      "q"|"quit")
        save_session "$session_file" "$current_index" "$selected_items" "$rejected_items"
        break
        ;;
        
      "d"|"done")
        break
        ;;
    esac
  done
  
  # Show summary
  show_selection_summary "$selected_items" "$rejected_items"
  
  # Return selected items
  echo "$selected_items"
}

# Display instructions
show_interactive_instructions() {
  cat <<'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                    INTERACTIVE WORK SELECTION                  ║
╠═══════════════════════════════════════════════════════════════╣
║  [A]ccept  - Add to work list                                ║
║  [R]eject  - Skip with reason (helps improve suggestions)    ║
║  [S]kip    - Skip without feedback                          ║
║  [B]ack    - Previous item                                  ║
║  [F]ilter  - Apply filters                                  ║
║  [I]nfo    - Show detailed information                      ║
║  [D]one    - Finish selection                               ║
║  [Q]uit    - Save and exit                                  ║
╚═══════════════════════════════════════════════════════════════╝

Press any key to start...
EOF
  read -n 1 -s
}

# Display single item
display_item_interactive() {
  local item="$1"
  local current="$2"
  local total="$3"
  
  # Header
  echo "┌────────────────────────────────────────────────────────────┐"
  printf "│ Item %3d of %3d                                              │\n" "$current" "$total"
  echo "├────────────────────────────────────────────────────────────┤"
  
  # Item details
  echo "$item" | jq -r '
    "│ [\(.type | ascii_upcase)] #\(.number)                                                    │",
    "│                                                            │",
    "│ \(.title[0:56])    │",
    (if (.title | length) > 56 then "│ \(.title[56:112])    │" else empty end),
    "│                                                            │",
    "├────────────────────────────────────────────────────────────┤",
    "│ Score: \(.composite_score // 0 | floor) | Priority: \(.priority // "normal") | Est: \(.estimated_minutes // "?")min          │",
    "│ Labels: \((.labels // []) | join(", ") | .[0:48])         │",
    "│                                                            │",
    (if .scores then
      "│ Scoring Breakdown:                                         │",
      "│   Priority: \(.scores.priority) | Momentum: \(.scores.momentum)                    │",
      "│   Context: \(.scores.context) | Type: \(.scores.type)                       │"
    else empty end),
    "└────────────────────────────────────────────────────────────┘"
  ' | while IFS= read -r line; do
    # Pad lines to fixed width
    printf "%-64s\n" "$line"
  done
  
  # Action prompt
  echo ""
  echo -n "Action ([A]ccept/[R]eject/[S]kip/[B]ack/[I]nfo/[F]ilter/[D]one/[Q]uit): "
}

# Get user action
get_user_action() {
  local action
  read -n 1 -s action
  echo  # New line after input
  echo "$action" | tr '[:upper:]' '[:lower:]'
}

# Get rejection reason
get_rejection_reason() {
  echo ""
  echo "Rejection reason (helps improve future suggestions):"
  echo "  1) Not relevant to current work"
  echo "  2) Too complex/large"
  echo "  3) Blocked by other work"
  echo "  4) Not my area/expertise"
  echo "  5) Low priority for me"
  echo "  6) Already in progress"
  echo "  7) Other (specify)"
  echo ""
  echo -n "Select reason (1-7): "
  
  local reason_num
  read -n 1 reason_num
  echo ""
  
  case "$reason_num" in
    "1") echo "not_relevant";;
    "2") echo "too_complex";;
    "3") echo "blocked";;
    "4") echo "wrong_expertise";;
    "5") echo "low_personal_priority";;
    "6") echo "already_working";;
    "7")
      echo -n "Specify reason: "
      read custom_reason
      echo "other:$custom_reason"
      ;;
    *) echo "unknown";;
  esac
}
```

### Detailed Information View
```bash
# Show detailed item information
show_detailed_info() {
  local item="$1"
  
  clear
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║                    DETAILED INFORMATION                       ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  
  echo "$item" | jq -r '
    "Type: \(.type | ascii_upcase)",
    "Number: #\(.number)",
    "Title: \(.title)",
    "",
    "URL: \(.url)",
    "",
    "Priority: \(.priority // "normal")",
    "State: \(.state // "open")",
    "Created: \(.created_at // "unknown")",
    "Updated: \(.updated_at // "unknown")",
    "Age: \(.age_days // 0) days",
    "",
    "Labels: \((.labels // []) | join(", "))",
    "",
    "Composite Score: \(.composite_score // 0 | floor)",
    "",
    "Score Breakdown:",
    "  Priority: \(.scores.priority // 0)",
    "  Momentum: \(.scores.momentum // 0)",
    "  Context: \(.scores.context // 0)",
    "  Age: \(.scores.age // 0)",
    "  Effort: \(.scores.effort // 0)",
    "  Deadline: \(.scores.deadline // 0)",
    "  Type: \(.scores.type // 0)",
    "",
    if .description then "Description:\n\(.description[0:500])" else empty end,
    "",
    if .blocks_count and .blocks_count > 0 then "⚠️  Blocks \(.blocks_count) other items" else empty end,
    if .fitting_slots then "📅 Can fit in \(.fitting_slots | length) time slots today" else empty end
  '
  
  echo ""
  echo "Press any key to continue..."
  read -n 1 -s
}
```

### Interactive Filtering
```bash
# Apply filters interactively
apply_interactive_filter() {
  local all_items="$1"
  local current_index="$2"
  
  clear
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║                        APPLY FILTERS                          ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "1) Filter by priority (critical/high/medium/low)"
  echo "2) Filter by type (issue/pr/todo)"
  echo "3) Filter by time estimate (<30min/<1h/<2h)"
  echo "4) Filter by labels"
  echo "5) Filter by score (>80/>60/>40)"
  echo "6) Clear all filters"
  echo "0) Cancel"
  echo ""
  echo -n "Select filter option: "
  
  local option
  read -n 1 option
  echo ""
  
  case "$option" in
    "1")
      echo -n "Enter priority (critical/high/medium/low): "
      read priority
      filter_by_priority "$all_items" "$priority"
      ;;
    "2")
      echo -n "Enter type (issue/pr/todo): "
      read type
      filter_by_type "$all_items" "$type"
      ;;
    "3")
      echo "Select time limit:"
      echo "  1) < 30 minutes"
      echo "  2) < 1 hour"
      echo "  3) < 2 hours"
      read -n 1 time_option
      case "$time_option" in
        "1") filter_by_time "$all_items" 30;;
        "2") filter_by_time "$all_items" 60;;
        "3") filter_by_time "$all_items" 120;;
      esac
      ;;
    "4")
      echo -n "Enter label to filter by: "
      read label
      filter_by_label "$all_items" "$label"
      ;;
    "5")
      echo -n "Enter minimum score: "
      read min_score
      filter_by_score "$all_items" "$min_score"
      ;;
    "6")
      echo "$all_items"
      ;;
    *)
      return
      ;;
  esac
}

# Filter functions
filter_by_priority() {
  local items="$1"
  local priority="$2"
  echo "$items" | jq --arg p "$priority" '[.[] | select(.priority == $p)]'
}

filter_by_type() {
  local items="$1"
  local type="$2"
  echo "$items" | jq --arg t "$type" '[.[] | select(.type == $t)]'
}

filter_by_time() {
  local items="$1"
  local max_minutes="$2"
  echo "$items" | jq --arg m "$max_minutes" '[.[] | select(.estimated_minutes <= ($m | tonumber))]'
}

filter_by_label() {
  local items="$1"
  local label="$2"
  echo "$items" | jq --arg l "$label" '[.[] | select(.labels | any(. == $l))]'
}

filter_by_score() {
  local items="$1"
  local min_score="$2"
  echo "$items" | jq --arg s "$min_score" '[.[] | select(.composite_score >= ($s | tonumber))]'
}
```

### Preference Learning
```bash
# Record user preferences
record_preference() {
  local item="$1"
  local action="$2"
  local reason="$3"
  local prefs_file="$4"
  
  # Initialize preferences file if needed
  if [[ ! -f "$prefs_file" ]]; then
    mkdir -p "$(dirname "$prefs_file")"
    echo '{"preferences": [], "patterns": {}}' > "$prefs_file"
  fi
  
  # Add preference record
  local pref_record=$(echo "$item" | jq --arg action "$action" --arg reason "$reason" '
    {
      timestamp: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
      action: $action,
      reason: $reason,
      item_features: {
        type: .type,
        priority: .priority,
        labels: .labels,
        score: .composite_score,
        has_pr: (.type == "pr"),
        is_bug: (.labels | any(. == "bug")),
        is_feature: (.labels | any(. == "feature" or . == "enhancement")),
        estimated_time: .estimated_minutes
      }
    }
  ')
  
  # Update preferences
  jq --argjson record "$pref_record" '.preferences += [$record]' "$prefs_file" > "${prefs_file}.tmp" && \
    mv "${prefs_file}.tmp" "$prefs_file"
  
  # Update patterns (after every 10 preferences)
  if [[ $(jq '.preferences | length' "$prefs_file") -gt 0 ]] && \
     [[ $(($(jq '.preferences | length' "$prefs_file") % 10)) -eq 0 ]]; then
    update_preference_patterns "$prefs_file"
  fi
}

# Analyze preferences to find patterns
update_preference_patterns() {
  local prefs_file="$1"
  
  jq '
    .preferences as $prefs |
    
    # Calculate acceptance rates by feature
    {
      preferences: .preferences,
      patterns: {
        by_type: (
          $prefs | group_by(.item_features.type) |
          map({
            key: .[0].item_features.type,
            value: {
              total: length,
              accepted: map(select(.action == "accepted")) | length,
              rate: ((map(select(.action == "accepted")) | length) / length)
            }
          }) | from_entries
        ),
        by_priority: (
          $prefs | group_by(.item_features.priority) |
          map({
            key: (.[0].item_features.priority // "normal"),
            value: {
              total: length,
              accepted: map(select(.action == "accepted")) | length,
              rate: ((map(select(.action == "accepted")) | length) / length)
            }
          }) | from_entries
        ),
        rejection_reasons: (
          $prefs | map(select(.action == "rejected" and .reason)) |
          group_by(.reason) | map({key: .[0].reason, value: length}) | from_entries
        ),
        preferred_time_range: (
          $prefs | map(select(.action == "accepted" and .item_features.estimated_time)) |
          if length > 0 then {
            min: (map(.item_features.estimated_time) | min),
            max: (map(.item_features.estimated_time) | max),
            avg: (map(.item_features.estimated_time) | add / length)
          } else null end
        )
      }
    }
  ' "$prefs_file" > "${prefs_file}.tmp" && mv "${prefs_file}.tmp" "$prefs_file"
}

# Apply learned preferences to boost scores
apply_preference_boost() {
  local items="$1"
  local prefs_file="${2:-${HOME}/.claude/data/work-preferences.json}"
  
  if [[ ! -f "$prefs_file" ]]; then
    echo "$items"
    return
  fi
  
  local patterns=$(jq '.patterns' "$prefs_file")
  
  echo "$items" | jq --argjson patterns "$patterns" '
    map(
      . as $item |
      
      # Calculate preference boost
      (
        # Type preference boost
        ($patterns.by_type[.type].rate // 0.5) * 10 +
        
        # Priority preference boost
        ($patterns.by_priority[.priority // "normal"].rate // 0.5) * 10 +
        
        # Time preference boost
        (if $patterns.preferred_time_range and .estimated_minutes then
          if .estimated_minutes >= $patterns.preferred_time_range.min and
             .estimated_minutes <= $patterns.preferred_time_range.max
          then 5 else -5 end
        else 0 end)
      ) as $preference_boost |
      
      . + {
        preference_boost: $preference_boost,
        adjusted_score: (.composite_score + $preference_boost)
      }
    ) | sort_by(-.adjusted_score)
  '
}
```

### Session Management
```bash
# Initialize interactive session
init_interactive_session() {
  local session_file="$1"
  local items="$2"
  
  mkdir -p "$(dirname "$session_file")"
  
  echo "$items" | jq '{
    created: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
    total_items: length,
    current_index: 0,
    selected: [],
    rejected: [],
    items: .
  }' > "$session_file"
}

# Save session state
save_session() {
  local session_file="$1"
  local current_index="$2"
  local selected="$3"
  local rejected="$4"
  
  jq --arg idx "$current_index" \
     --argjson selected "$selected" \
     --argjson rejected "$rejected" '
    .current_index = ($idx | tonumber) |
    .selected = $selected |
    .rejected = $rejected |
    .updated = (now | strftime("%Y-%m-%dT%H:%M:%SZ"))
  ' "$session_file" > "${session_file}.tmp" && \
    mv "${session_file}.tmp" "$session_file"
}

# Resume previous session
resume_session() {
  local session_file="${HOME}/.claude/cache/interactive-session.json"
  
  if [[ -f "$session_file" ]]; then
    local session_age=$(($(date +%s) - $(date -d "$(jq -r '.updated // .created' "$session_file")" +%s)))
    
    # Session expires after 1 hour
    if [[ $session_age -lt 3600 ]]; then
      echo -n "Resume previous session? (y/n): "
      read -n 1 resume
      echo ""
      
      if [[ "$resume" == "y" ]]; then
        local items=$(jq '.items' "$session_file")
        local current_index=$(jq '.current_index' "$session_file")
        interactive_select_items "$items" "$current_index"
        return $?
      fi
    fi
  fi
  
  return 1
}
```

### Summary Display
```bash
# Show selection summary
show_selection_summary() {
  local selected="$1"
  local rejected="$2"
  
  clear
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║                    SELECTION SUMMARY                          ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  
  local selected_count=$(echo "$selected" | jq 'length')
  local rejected_count=$(echo "$rejected" | jq 'length')
  
  echo "Selected: $selected_count items"
  echo "Rejected: $rejected_count items"
  echo ""
  
  if [[ $selected_count -gt 0 ]]; then
    echo "Selected Items:"
    echo "$selected" | jq -r '.[] | "  - [\(.type)] #\(.number): \(.title[0:50])"'
    echo ""
  fi
  
  if [[ $rejected_count -gt 0 ]]; then
    echo "Rejection Reasons:"
    echo "$rejected" | jq -r '
      group_by(.reason) |
      map({reason: .[0].reason, count: length}) |
      .[] | "  - \(.reason): \(.count) items"
    '
  fi
  
  echo ""
  echo "Actions:"
  echo "  [E]xport selected items"
  echo "  [A]dd selected to TODO system"
  echo "  [V]iew detailed list"
  echo "  [Q]uit"
  echo ""
  echo -n "Choose action: "
  
  local action
  read -n 1 action
  echo ""
  
  case "$action" in
    "e"|"E")
      export_selected_items "$selected"
      ;;
    "a"|"A")
      add_to_todo_system "$selected"
      ;;
    "v"|"V")
      view_detailed_list "$selected"
      ;;
  esac
}
```

## Integration Functions

### Main Entry Point
```bash
# Interactive work selection
select_work_interactive() {
  local items="$1"
  local options="${2:-{}}"
  
  # Apply preference boost if enabled
  if [[ $(echo "$options" | jq -r '.use_preferences // "true"') == "true" ]]; then
    items=$(apply_preference_boost "$items")
  fi
  
  # Check for resume
  if ! resume_session; then
    # Start new session
    interactive_select_items "$items"
  fi
}
```

### Export Functions
```bash
# Export selected items
export_selected_items() {
  local items="$1"
  local format="${2:-json}"
  local output_file="${3:-selected-work.json}"
  
  case "$format" in
    "json")
      echo "$items" > "$output_file"
      ;;
    "markdown")
      echo "# Selected Work Items" > "$output_file"
      echo "" >> "$output_file"
      echo "$items" | jq -r '.[] | "- [\(.type)] #\(.number): [\(.title)](\(.url))"' >> "$output_file"
      ;;
    "csv")
      echo "Type,Number,Title,Priority,Score,URL" > "$output_file"
      echo "$items" | jq -r '.[] | [.type, .number, .title, .priority, .composite_score, .url] | @csv' >> "$output_file"
      ;;
  esac
  
  echo "✅ Exported $(echo "$items" | jq 'length') items to $output_file"
}
```

## Examples

### Basic Interactive Selection
```bash
# Select work interactively
find_work_interactive() {
  local all_work=$(get_prioritized_work)
  select_work_interactive "$all_work"
}
```

### With Preference Learning
```bash
# Use learned preferences
find_personalized_work() {
  local work=$(get_all_work_items)
  select_work_interactive "$work" '{"use_preferences": true}'
}
```

### Quick Morning Selection
```bash
# Quick selection for morning work
morning_work_selection() {
  local work=$(get_work_items | jq '[.[] | select(.estimated_minutes <= 240)]')
  select_work_interactive "$work" '{
    "use_preferences": true,
    "auto_filter": "morning_suitable"
  }'
}
```