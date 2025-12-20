---
name: output-formatting
description: Consistent output formatting across multiple formats (terminal, markdown, JSON, CSV, HTML)
version: 1.0.0
type: process
scope: persistent
---

# Output Formatting Process

## Purpose
Provide consistent, reusable formatting functions for displaying work items and recommendations across different output formats. Supports terminal display with colors, markdown for reports, JSON for automation, and more.

## Supported Formats

### Terminal Output
```bash
# Format for terminal display with colors
format_terminal_output() {
  local items="$1"
  local group_by="${2:-priority}"
  local color="${3:-true}"
  
  # Color codes
  local RED='\033[0;31m'
  local YELLOW='\033[0;33m'
  local GREEN='\033[0;32m'
  local BLUE='\033[0;34m'
  local BOLD='\033[1m'
  local NC='\033[0m' # No Color
  
  # Disable colors if requested
  if [[ "$color" != "true" ]]; then
    RED="" YELLOW="" GREEN="" BLUE="" BOLD="" NC=""
  fi
  
  case "$group_by" in
    "priority")
      format_by_priority_terminal "$items" "$RED" "$YELLOW" "$GREEN" "$BLUE" "$BOLD" "$NC"
      ;;
    "type")
      format_by_type_terminal "$items" "$RED" "$YELLOW" "$GREEN" "$BLUE" "$BOLD" "$NC"
      ;;
    "score")
      format_by_score_terminal "$items" "$RED" "$YELLOW" "$GREEN" "$BLUE" "$BOLD" "$NC"
      ;;
    *)
      format_flat_terminal "$items" "$RED" "$YELLOW" "$GREEN" "$BLUE" "$BOLD" "$NC"
      ;;
  esac
}

# Format by priority groups
format_by_priority_terminal() {
  local items="$1"
  local RED="$2" YELLOW="$3" GREEN="$4" BLUE="$5" BOLD="$6" NC="$7"
  
  # Group items
  local critical=$(echo "$items" | jq '[.[] | select(.priority == "critical")]')
  local high=$(echo "$items" | jq '[.[] | select(.priority == "high")]')
  local medium=$(echo "$items" | jq '[.[] | select(.priority == "medium")]')
  local low=$(echo "$items" | jq '[.[] | select(.priority == "low" or .priority == null)]')
  
  # Display groups
  if [[ $(echo "$critical" | jq 'length') -gt 0 ]]; then
    echo -e "\n${RED}${BOLD}🚨 CRITICAL PRIORITY${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    format_items_terminal "$critical" "$RED" "$NC"
  fi
  
  if [[ $(echo "$high" | jq 'length') -gt 0 ]]; then
    echo -e "\n${YELLOW}${BOLD}⚠️  HIGH PRIORITY${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    format_items_terminal "$high" "$YELLOW" "$NC"
  fi
  
  if [[ $(echo "$medium" | jq 'length') -gt 0 ]]; then
    echo -e "\n${BLUE}${BOLD}📋 MEDIUM PRIORITY${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    format_items_terminal "$medium" "$BLUE" "$NC"
  fi
  
  if [[ $(echo "$low" | jq 'length') -gt 0 ]]; then
    echo -e "\n${GREEN}${BOLD}💭 LOW PRIORITY${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    format_items_terminal "$low" "$GREEN" "$NC"
  fi
}

# Format individual items for terminal
format_items_terminal() {
  local items="$1"
  local color="$2"
  local nc="$3"
  
  echo "$items" | jq -r --arg color "$color" --arg nc "$nc" '.[] | 
    "\($color)[\(.type | ascii_upcase)] #\(.number)\($nc) \(.title[0:60])\(if (.title | length) > 60 then "..." else "" end)\n" +
    "  Score: \(.composite_score // 0 | floor) | " +
    (if .labels then "Labels: \(.labels | join(", ")) | " else "" end) +
    (if .estimated_minutes then "Est: \(.estimated_minutes)min | " else "" end) +
    "URL: \(.url)"
  '
}
```

### Markdown Output
```bash
# Format as markdown
format_markdown_output() {
  local items="$1"
  local title="${2:-Work Items}"
  local include_toc="${3:-true}"
  
  # Header
  echo "# $title"
  echo ""
  echo "_Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")_"
  echo ""
  
  # Summary stats
  local stats=$(calculate_summary_stats "$items")
  echo "## Summary"
  echo ""
  echo "$stats" | jq -r '
    "- Total items: \(.total)",
    "- Average score: \(.avg_score)",
    "- By priority: \(.by_priority | to_entries | map("\(.key): \(.value)") | join(", "))",
    "- By type: \(.by_type | to_entries | map("\(.key): \(.value)") | join(", "))"
  '
  echo ""
  
  # Table of contents
  if [[ "$include_toc" == "true" ]]; then
    echo "## Table of Contents"
    echo ""
    echo "- [Critical Priority](#critical-priority)"
    echo "- [High Priority](#high-priority)"
    echo "- [Medium Priority](#medium-priority)"
    echo "- [Low Priority](#low-priority)"
    echo ""
  fi
  
  # Items by priority
  format_markdown_by_priority "$items"
}

# Format items by priority in markdown
format_markdown_by_priority() {
  local items="$1"
  
  # Critical
  local critical=$(echo "$items" | jq '[.[] | select(.priority == "critical")]')
  if [[ $(echo "$critical" | jq 'length') -gt 0 ]]; then
    echo "## Critical Priority"
    echo ""
    format_markdown_table "$critical"
    echo ""
  fi
  
  # High
  local high=$(echo "$items" | jq '[.[] | select(.priority == "high")]')
  if [[ $(echo "$high" | jq 'length') -gt 0 ]]; then
    echo "## High Priority"
    echo ""
    format_markdown_table "$high"
    echo ""
  fi
  
  # Medium
  local medium=$(echo "$items" | jq '[.[] | select(.priority == "medium")]')
  if [[ $(echo "$medium" | jq 'length') -gt 0 ]]; then
    echo "## Medium Priority"
    echo ""
    format_markdown_table "$medium"
    echo ""
  fi
  
  # Low
  local low=$(echo "$items" | jq '[.[] | select(.priority == "low" or .priority == null)]')
  if [[ $(echo "$low" | jq 'length') -gt 0 ]]; then
    echo "## Low Priority"
    echo ""
    format_markdown_table "$low"
    echo ""
  fi
}

# Format items as markdown table
format_markdown_table() {
  local items="$1"
  
  echo "| Type | # | Title | Score | Labels | Est. Time |"
  echo "|------|---|-------|-------|--------|-----------|"
  
  echo "$items" | jq -r '.[] |
    "| \(.type) | [\(.number)](\(.url)) | \(.title[0:40])\(if (.title | length) > 40 then "..." else "" end) | \(.composite_score // 0 | floor) | \(.labels // [] | join(", ")) | \(.estimated_minutes // "-")min |"
  '
}
```

### JSON Output
```bash
# Format as JSON with metadata
format_json_output() {
  local items="$1"
  local include_metadata="${2:-true}"
  local pretty="${3:-true}"
  
  local output=$(echo "$items" | jq --arg meta "$include_metadata" '
    if $meta == "true" then
      {
        metadata: {
          generated: (now | strftime("%Y-%m-%dT%H:%M:%SZ")),
          version: "1.0.0",
          total_items: length,
          score_range: {
            min: (map(.composite_score // 0) | min),
            max: (map(.composite_score // 0) | max),
            avg: (map(.composite_score // 0) | add / length)
          }
        },
        items: .
      }
    else
      .
    end
  ')
  
  if [[ "$pretty" == "true" ]]; then
    echo "$output" | jq '.'
  else
    echo "$output" | jq -c '.'
  fi
}
```

### CSV Output
```bash
# Format as CSV
format_csv_output() {
  local items="$1"
  local headers="${2:-true}"
  
  # Headers
  if [[ "$headers" == "true" ]]; then
    echo "Type,Number,Title,Priority,Score,Labels,URL,Estimated Minutes"
  fi
  
  # Data rows
  echo "$items" | jq -r '.[] |
    [
      .type,
      .number,
      (.title | gsub(","; ";")),  # Escape commas
      (.priority // "normal"),
      (.composite_score // 0 | floor),
      (.labels // [] | join(";")),
      .url,
      (.estimated_minutes // "")
    ] | @csv
  '
}
```

### HTML Output
```bash
# Format as HTML
format_html_output() {
  local items="$1"
  local title="${2:-Work Items}"
  local standalone="${3:-true}"
  
  if [[ "$standalone" == "true" ]]; then
    cat <<EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>$title</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; }
    h1 { color: #333; }
    .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    .priority-section { margin-bottom: 30px; }
    .priority-critical h2 { color: #d32f2f; }
    .priority-high h2 { color: #f57c00; }
    .priority-medium h2 { color: #1976d2; }
    .priority-low h2 { color: #388e3c; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #f5f5f5; font-weight: bold; }
    .score { text-align: center; }
    .labels { font-size: 0.9em; color: #666; }
    a { color: #1976d2; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
EOF
  fi
  
  # Title and summary
  echo "<h1>$title</h1>"
  
  local stats=$(calculate_summary_stats "$items")
  echo '<div class="summary">'
  echo "$stats" | jq -r '
    "<p><strong>Generated:</strong> \(now | strftime("%Y-%m-%d %H:%M:%S UTC"))</p>",
    "<p><strong>Total Items:</strong> \(.total)</p>",
    "<p><strong>Average Score:</strong> \(.avg_score)</p>"
  '
  echo '</div>'
  
  # Group and display by priority
  format_html_by_priority "$items"
  
  if [[ "$standalone" == "true" ]]; then
    echo "</body></html>"
  fi
}

# Format HTML sections by priority
format_html_by_priority() {
  local items="$1"
  
  local priorities=("critical" "high" "medium" "low")
  local icons=("🚨" "⚠️" "📋" "💭")
  
  for i in "${!priorities[@]}"; do
    local priority="${priorities[$i]}"
    local icon="${icons[$i]}"
    
    local filtered=$(echo "$items" | jq --arg p "$priority" '
      [.[] | select(
        if $p == "low" then (.priority == "low" or .priority == null)
        else .priority == $p
        end
      )]
    ')
    
    if [[ $(echo "$filtered" | jq 'length') -gt 0 ]]; then
      echo "<div class='priority-section priority-$priority'>"
      echo "<h2>$icon ${priority^} Priority</h2>"
      format_html_table "$filtered"
      echo "</div>"
    fi
  done
}

# Format HTML table
format_html_table() {
  local items="$1"
  
  echo "<table>"
  echo "<thead><tr>"
  echo "<th>Type</th><th>#</th><th>Title</th><th class='score'>Score</th><th>Labels</th><th>Est.</th>"
  echo "</tr></thead>"
  echo "<tbody>"
  
  echo "$items" | jq -r '.[] |
    "<tr>",
    "  <td>\(.type | ascii_upcase)</td>",
    "  <td><a href=\"\(.url)\">#\(.number)</a></td>",
    "  <td>\(.title[0:60])\(if (.title | length) > 60 then "..." else "" end)</td>",
    "  <td class=\"score\">\(.composite_score // 0 | floor)</td>",
    "  <td class=\"labels\">\(.labels // [] | join(", "))</td>",
    "  <td>\(.estimated_minutes // "-")m</td>",
    "</tr>"
  '
  
  echo "</tbody></table>"
}
```

### Digest Format
```bash
# Format as daily digest
format_digest_output() {
  local items="$1"
  local format="${2:-markdown}"  # markdown, text, html
  
  # Calculate digest sections
  local digest=$(echo "$items" | jq '
    {
      morning_priorities: [.[] | select(.priority == "critical" or .priority == "high")] | .[0:5],
      quick_wins: [.[] | select(.estimated_minutes <= 30 and .composite_score > 60)] | .[0:5],
      prs_needing_review: [.[] | select(.type == "pr" and .state == "open")] | .[0:5],
      stale_items: [.[] | select(.age_days > 30)] | sort_by(-.age_days) | .[0:5],
      blocked_work: [.[] | select(.blocks_count > 0)] | .[0:3]
    }
  ')
  
  case "$format" in
    "markdown")
      format_digest_markdown "$digest"
      ;;
    "html")
      format_digest_html "$digest"
      ;;
    *)
      format_digest_text "$digest"
      ;;
  esac
}

# Format digest as markdown
format_digest_markdown() {
  local digest="$1"
  
  echo "# Daily Work Digest"
  echo ""
  echo "_$(date +"%A, %B %d, %Y")_"
  echo ""
  
  # Morning priorities
  echo "## 🌅 Morning Priorities"
  echo ""
  echo "$digest" | jq -r '.morning_priorities[] |
    "- [\(.type | ascii_upcase) #\(.number)](\(.url)): \(.title[0:60])\(if (.title | length) > 60 then "..." else "" end)"
  '
  echo ""
  
  # Quick wins
  echo "## ⚡ Quick Wins (<30 min)"
  echo ""
  echo "$digest" | jq -r '.quick_wins[] |
    "- [\(.type | ascii_upcase) #\(.number)](\(.url)): \(.title[0:60]) (\(.estimated_minutes)min)"
  '
  echo ""
  
  # PRs needing review
  if [[ $(echo "$digest" | jq '.prs_needing_review | length') -gt 0 ]]; then
    echo "## 👀 PRs Needing Review"
    echo ""
    echo "$digest" | jq -r '.prs_needing_review[] |
      "- [PR #\(.number)](\(.url)): \(.title[0:60])"
    '
    echo ""
  fi
  
  # Stale items warning
  if [[ $(echo "$digest" | jq '.stale_items | length') -gt 0 ]]; then
    echo "## ⏰ Aging Items (>30 days)"
    echo ""
    echo "$digest" | jq -r '.stale_items[] |
      "- [\(.type | ascii_upcase) #\(.number)](\(.url)): \(.age_days) days old"
    '
    echo ""
  fi
}
```

## Utility Functions

### Summary Statistics
```bash
# Calculate summary statistics
calculate_summary_stats() {
  local items="$1"
  
  echo "$items" | jq '
    {
      total: length,
      avg_score: (if length > 0 then (map(.composite_score // 0) | add / length | floor) else 0 end),
      by_priority: (
        group_by(.priority // "normal") | 
        map({key: .[0].priority // "normal", value: length}) | 
        from_entries
      ),
      by_type: (
        group_by(.type) | 
        map({key: .[0].type, value: length}) | 
        from_entries
      ),
      score_distribution: {
        high: (map(select(.composite_score > 80)) | length),
        medium: (map(select(.composite_score <= 80 and .composite_score > 50)) | length),
        low: (map(select(.composite_score <= 50)) | length)
      }
    }
  '
}
```

### Format Selection
```bash
# Select appropriate formatter
format_output() {
  local items="$1"
  local format="${2:-terminal}"
  local options="${3:-{}}"
  
  case "$format" in
    "terminal"|"tty")
      format_terminal_output "$items" \
        "$(echo "$options" | jq -r '.group_by // "priority"')" \
        "$(echo "$options" | jq -r '.color // "true"')"
      ;;
      
    "markdown"|"md")
      format_markdown_output "$items" \
        "$(echo "$options" | jq -r '.title // "Work Items"')" \
        "$(echo "$options" | jq -r '.toc // "true"')"
      ;;
      
    "json")
      format_json_output "$items" \
        "$(echo "$options" | jq -r '.metadata // "true"')" \
        "$(echo "$options" | jq -r '.pretty // "true"')"
      ;;
      
    "csv")
      format_csv_output "$items" \
        "$(echo "$options" | jq -r '.headers // "true"')"
      ;;
      
    "html")
      format_html_output "$items" \
        "$(echo "$options" | jq -r '.title // "Work Items"')" \
        "$(echo "$options" | jq -r '.standalone // "true"')"
      ;;
      
    "digest")
      format_digest_output "$items" \
        "$(echo "$options" | jq -r '.digest_format // "markdown"')"
      ;;
      
    *)
      echo "Error: Unknown format '$format'" >&2
      return 1
      ;;
  esac
}
```

### Interactive Format Detection
```bash
# Auto-detect best format
detect_output_format() {
  local force_format="$1"
  
  if [[ -n "$force_format" ]]; then
    echo "$force_format"
  elif [[ -t 1 ]]; then
    # Interactive terminal
    echo "terminal"
  elif [[ -n "$GITHUB_ACTIONS" ]]; then
    # GitHub Actions
    echo "markdown"
  elif [[ -n "$CI" ]]; then
    # Generic CI
    echo "json"
  else
    # Piped or redirected
    echo "json"
  fi
}
```

## Examples

### Basic Terminal Output
```bash
# Display work items in terminal
display_work() {
  local items=$(get_work_items)
  format_output "$items" "terminal" '{"group_by": "priority", "color": true}'
}
```

### Generate Report
```bash
# Create markdown report
generate_work_report() {
  local items=$(get_prioritized_work)
  format_output "$items" "markdown" '{"title": "Sprint 23 Work Items", "toc": true}' > sprint-23-report.md
}
```

### Export for Automation
```bash
# Export as JSON for automation
export_work_json() {
  local items=$(get_work_items)
  format_output "$items" "json" '{"metadata": true, "pretty": false}' > work-items.json
}
```

### Daily Digest Email
```bash
# Generate HTML digest
create_daily_digest() {
  local items=$(get_prioritized_work)
  format_output "$items" "digest" '{"digest_format": "html"}' > daily-digest.html
}
```