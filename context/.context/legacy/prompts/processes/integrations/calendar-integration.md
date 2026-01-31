---
name: calendar-integration
description: Check calendar availability and filter work by available time slots
version: 1.0.0
type: process
scope: temporary
conditional: true
---

# Calendar Integration Process

## Purpose
Integrate with calendar systems to check availability and suggest work that fits within available time slots. Supports multiple calendar platforms with graceful fallbacks.

## Configuration
```yaml
calendar:
  provider: auto  # auto, google, outlook, ical, local
  working_hours:
    start: "09:00"
    end: "17:00"
    timezone: "local"
  
  buffer_time: 15  # Minutes between tasks
  
  sync:
    enabled: true
    frequency: 15m
    cache_duration: 5m
```

## Calendar Providers

### Auto-Detection
```bash
detect_calendar_provider() {
  # Check for various calendar configurations
  if [[ -f "${HOME}/.config/gcalcli/gcalclirc" ]]; then
    echo "google"
  elif command -v icalBuddy &>/dev/null; then
    echo "ical"
  elif [[ -f "${HOME}/.config/khal/config" ]]; then
    echo "khal"
  elif [[ -f "${HOME}/.claude/calendar/schedule.json" ]]; then
    echo "local"
  else
    echo "none"
  fi
}
```

### Google Calendar Integration
```bash
# Using gcalcli
get_google_calendar_events() {
  local start_time="${1:-now}"
  local end_time="${2:-today 23:59}"
  
  if command -v gcalcli &>/dev/null; then
    gcalcli agenda "$start_time" "$end_time" --nocolor --tsv | \
    awk -F'\t' '{
      print "{"
      print "  \"start\": \"" $1 " " $2 "\","
      print "  \"end\": \"" $3 " " $4 "\","
      print "  \"title\": \"" $5 "\","
      print "  \"duration_minutes\": " ((($3 " " $4) - ($1 " " $2)) / 60)
      print "},"
    }' | sed '$ s/,$//' | jq -s '.'
  else
    echo "[]"
  fi
}
```

### Local Calendar File
```bash
# Simple JSON-based local calendar
get_local_calendar_events() {
  local calendar_file="${HOME}/.claude/calendar/schedule.json"
  local today=$(date +%Y-%m-%d)
  
  if [[ -f "$calendar_file" ]]; then
    jq --arg today "$today" '
      .events | 
      map(select(.date == $today or .recurring == true)) |
      map({
        start: .start,
        end: .end,
        title: .title,
        duration_minutes: .duration_minutes
      })
    ' < "$calendar_file"
  else
    echo "[]"
  fi
}
```

## Availability Checking

### Calculate Free Slots
```bash
calculate_free_slots() {
  local events="$1"
  local working_start="${2:-09:00}"
  local working_end="${3:-17:00}"
  local buffer_minutes="${4:-15}"
  
  echo "$events" | jq --arg start "$working_start" --arg end "$working_end" --arg buffer "$buffer_minutes" '
    # Convert time strings to minutes since midnight
    def time_to_minutes: 
      split(":") | (.[0] | tonumber) * 60 + (.[1] | tonumber);
    
    # Convert minutes to time string
    def minutes_to_time:
      (. / 60 | floor) as $hours |
      (. % 60) as $minutes |
      "\($hours):\($minutes | tostring | if length == 1 then "0" + . else . end)";
    
    # Working hours in minutes
    ($start | time_to_minutes) as $work_start |
    ($end | time_to_minutes) as $work_end |
    ($buffer | tonumber) as $buffer_min |
    
    # Sort events by start time
    sort_by(.start | time_to_minutes) as $sorted_events |
    
    # Find gaps between events
    reduce $sorted_events[] as $event (
      {slots: [], last_end: $work_start};
      
      ($event.start | time_to_minutes) as $event_start |
      ($event.end | time_to_minutes) as $event_end |
      
      # Add slot if gap is large enough
      if ($event_start - .last_end) >= $buffer_min then
        .slots += [{
          start: (.last_end | minutes_to_time),
          end: (($event_start - $buffer_min) | minutes_to_time),
          duration_minutes: ($event_start - .last_end - $buffer_min)
        }]
      else . end |
      
      .last_end = ($event_end + $buffer_min)
    ) |
    
    # Add final slot if time remains
    if (.last_end < $work_end) then
      .slots += [{
        start: (.last_end | minutes_to_time),
        end: ($work_end | minutes_to_time),
        duration_minutes: ($work_end - .last_end)
      }]
    else . end |
    
    .slots
  '
}
```

### Match Work to Time Slots
```bash
match_work_to_slots() {
  local work_items="$1"
  local free_slots="$2"
  
  echo "$work_items" | jq --argjson slots "$free_slots" '
    map(
      . as $item |
      
      # Estimate time based on various factors
      (
        if .labels | any(. == "effort:xs") then 30
        elif .labels | any(. == "effort:s") then 60
        elif .labels | any(. == "effort:m") then 180
        elif .labels | any(. == "effort:l") then 360
        elif .type == "pr" and .additions < 50 then 45
        elif .type == "pr" and .additions < 200 then 90
        elif .type == "bug" then 120
        else 60
        end
      ) as $estimated_minutes |
      
      # Find fitting slots
      ($slots | map(select(.duration_minutes >= $estimated_minutes))) as $fitting_slots |
      
      . + {
        estimated_minutes: $estimated_minutes,
        fitting_slots: $fitting_slots,
        can_fit_today: (($fitting_slots | length) > 0)
      }
    )
  '
}
```

## Calendar-Aware Filtering

### Filter by Available Time
```bash
filter_by_available_time() {
  local work_items="$1"
  local time_constraint="${2:-any}"  # any, 30min, 1h, 2h, 4h
  
  # Get current calendar
  local provider=$(detect_calendar_provider)
  local events=$(get_calendar_events "$provider")
  local free_slots=$(calculate_free_slots "$events")
  
  # Match work to slots
  local matched=$(match_work_to_slots "$work_items" "$free_slots")
  
  # Apply time constraint filter
  case "$time_constraint" in
    "30min")
      echo "$matched" | jq 'map(select(.estimated_minutes <= 30 and .can_fit_today))'
      ;;
    "1h")
      echo "$matched" | jq 'map(select(.estimated_minutes <= 60 and .can_fit_today))'
      ;;
    "2h")
      echo "$matched" | jq 'map(select(.estimated_minutes <= 120 and .can_fit_today))'
      ;;
    "4h")
      echo "$matched" | jq 'map(select(.estimated_minutes <= 240 and .can_fit_today))'
      ;;
    *)
      echo "$matched" | jq 'map(select(.can_fit_today))'
      ;;
  esac
}
```

## Smart Scheduling

### Suggest Optimal Work Order
```bash
suggest_work_schedule() {
  local matched_work="$1"
  local optimization="${2:-efficiency}"  # efficiency, momentum, energy
  
  echo "$matched_work" | jq --arg opt "$optimization" '
    # Sort by optimization strategy
    (
      if $opt == "efficiency" then
        # Pack small tasks first
        sort_by(.estimated_minutes)
      elif $opt == "momentum" then
        # Quick wins first
        sort_by(-.scores.momentum, .estimated_minutes)
      elif $opt == "energy" then
        # Complex tasks when fresh
        sort_by(-.estimated_minutes) | reverse
      else
        .
      end
    ) as $sorted |
    
    # Build schedule
    reduce $sorted[] as $item (
      {schedule: [], current_slot_idx: 0, slots: .fitting_slots[0]};
      
      # Try to fit item in current slot
      if .slots[.current_slot_idx].duration_minutes >= $item.estimated_minutes then
        .schedule += [{
          item: $item,
          slot: .slots[.current_slot_idx],
          start_time: .slots[.current_slot_idx].start
        }] |
        .slots[.current_slot_idx].duration_minutes -= $item.estimated_minutes
      else
        # Move to next slot
        .current_slot_idx += 1 |
        if .current_slot_idx < (.slots | length) then
          .schedule += [{
            item: $item,
            slot: .slots[.current_slot_idx],
            start_time: .slots[.current_slot_idx].start
          }]
        else .
        end
      end
    ) |
    
    .schedule
  '
}
```

## Calendar Sync

### Export Work to Calendar
```bash
export_to_calendar() {
  local schedule="$1"
  local provider="${2:-local}"
  
  case "$provider" in
    "google")
      export_to_google_calendar "$schedule"
      ;;
    "ical")
      export_to_ical "$schedule"
      ;;
    *)
      export_to_local_calendar "$schedule"
      ;;
  esac
}

export_to_local_calendar() {
  local schedule="$1"
  local calendar_file="${HOME}/.claude/calendar/work-items.json"
  
  mkdir -p "$(dirname "$calendar_file")"
  
  echo "$schedule" | jq '
    map({
      title: ("Work: " + .item.title),
      start: .start_time,
      duration_minutes: .item.estimated_minutes,
      type: "work_item",
      url: .item.url,
      created: now | strftime("%Y-%m-%dT%H:%M:%SZ")
    })
  ' > "$calendar_file"
  
  echo "✅ Exported $(echo "$schedule" | jq 'length') work items to calendar"
}
```

## Usage Functions

### Main Calendar Integration
```bash
integrate_calendar() {
  local work_items="$1"
  local options="$2"
  
  echo "📅 Checking calendar availability..."
  
  # Parse options
  local time_filter=$(echo "$options" | jq -r '.time // "any"')
  local export_cal=$(echo "$options" | jq -r '.export // false')
  local show_schedule=$(echo "$options" | jq -r '.show_schedule // true')
  
  # Filter by calendar availability
  local filtered=$(filter_by_available_time "$work_items" "$time_filter")
  
  # Generate schedule if requested
  if [[ "$show_schedule" == "true" ]]; then
    local schedule=$(suggest_work_schedule "$filtered")
    
    echo ""
    echo "📋 Suggested Schedule:"
    echo "$schedule" | jq -r '.[] | "  \(.start_time) - \(.item.title[0:60])... (~\(.item.estimated_minutes)min)"'
  fi
  
  # Export if requested
  if [[ "$export_cal" == "true" ]]; then
    export_to_calendar "$schedule"
  fi
  
  # Return filtered items
  echo "$filtered"
}
```

### Quick Availability Check
```bash
check_time_available() {
  local duration_minutes="$1"
  
  local provider=$(detect_calendar_provider)
  local events=$(get_calendar_events "$provider")
  local free_slots=$(calculate_free_slots "$events")
  
  echo "$free_slots" | jq --arg duration "$duration_minutes" '
    map(select(.duration_minutes >= ($duration | tonumber))) |
    if length > 0 then
      {
        available: true,
        next_slot: .[0],
        total_slots: length
      }
    else
      {
        available: false,
        message: "No slots available for \($duration) minutes today"
      }
    end
  '
}
```

## Examples

### Basic Calendar Filtering
```bash
# Find work that fits in available time slots
filter_work_by_calendar() {
  local all_work=$(get_all_work_items)
  integrate_calendar "$all_work" '{"time": "2h"}'
}
```

### Morning Planning
```bash
# Plan morning work session
plan_morning_work() {
  local work=$(get_prioritized_work)
  integrate_calendar "$work" '{
    "time": "4h",
    "show_schedule": true,
    "export": true
  }'
}
```

### Quick Task Hunt
```bash
# Find tasks for short break
find_quick_tasks() {
  local work=$(get_all_work_items)
  integrate_calendar "$work" '{"time": "30min"}'
}
```