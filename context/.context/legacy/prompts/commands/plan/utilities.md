---
module: PlanUtilities
scope: context
triggers: []
conflicts: []
dependencies: []
priority: medium
---

# PlanUtilities - Common Utility Functions

## Purpose
Shared utility functions used across all plan modules.

## Utility Functions

### Format Duration
```bash
format_duration() {
  local seconds=$1
  local hours=$((seconds / 3600))
  local minutes=$(( (seconds % 3600) / 60 ))
  local secs=$((seconds % 60))
  
  if [ $hours -gt 0 ]; then
    printf "%dh %dm %ds" $hours $minutes $secs
  elif [ $minutes -gt 0 ]; then
    printf "%dm %ds" $minutes $secs
  else
    printf "%ds" $secs
  fi
}
```

### Progress Bar
```bash
show_progress() {
  local current=$1
  local total=$2
  local width=50
  
  local progress=$((current * width / total))
  local percentage=$((current * 100 / total))
  
  printf "\r["
  printf "%${progress}s" | tr ' ' '='
  printf "%$((width - progress))s" | tr ' ' '-'
  printf "] %d%%" $percentage
}
```

### JSON Helpers
```bash
# Extract value from JSON
json_extract() {
  local json=$1
  local key=$2
  echo "$json" | jq -r ".$key"
}

# Pretty print JSON
json_pretty() {
  local json=$1
  echo "$json" | jq '.'
}
```

### Date/Time Helpers
```bash
# Get timestamp
get_timestamp() {
  date +%Y%m%d_%H%M%S
}

# Get human readable date
get_date() {
  date "+%Y-%m-%d %H:%M:%S"
}
```

### String Manipulation
```bash
# Trim whitespace
trim() {
  local string="$1"
  echo "$string" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

# Escape for JSON
escape_json() {
  local string="$1"
  echo "$string" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\r/\\r/g; s/\t/\\t/g'
}
```

## Usage

These functions are available to all plan modules that include utilities.md in their dependencies.

Example:
```bash
# Format execution time
start_time=$(date +%s)
# ... do work ...
end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Execution time: $(format_duration $duration)"

# Show progress
total_items=100
for i in $(seq 1 $total_items); do
  show_progress $i $total_items
  # ... process item ...
done
```