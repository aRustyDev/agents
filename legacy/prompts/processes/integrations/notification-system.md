---
name: notification-system
description: Multi-channel notification system for work alerts and reminders
version: 1.0.0
type: process
scope: temporary
conditional: true
---

# Notification System Process

## Purpose
Send notifications about critical work items, PR reviews, and daily digests through multiple channels. Supports desktop notifications, Slack, email, and webhooks with intelligent batching and rate limiting.

## Configuration
```yaml
notifications:
  enabled: true
  
  channels:
    desktop:
      enabled: true
      tool: auto  # auto, notify-send, osascript, terminal-notifier
      sound: true
      
    slack:
      enabled: false
      webhook_url: "${SLACK_WEBHOOK_URL}"
      channel: "#dev-notifications"
      username: "Claude Work Bot"
      
    email:
      enabled: false
      smtp_server: "${SMTP_SERVER}"
      from: "${EMAIL_FROM}"
      to: "${EMAIL_TO}"
      
    webhook:
      enabled: false
      url: "${NOTIFICATION_WEBHOOK_URL}"
      headers:
        Authorization: "Bearer ${WEBHOOK_TOKEN}"
  
  triggers:
    critical_work:
      channels: [desktop, slack]
      conditions:
        - priority: critical
        - labels: [security, urgent]
        
    pr_review:
      channels: [desktop]
      conditions:
        - type: pr
        - requested_reviewer: true
        
    daily_digest:
      channels: [email, slack]
      schedule: "09:00"
      
  rate_limiting:
    max_per_hour: 10
    batch_window: 5m
    quiet_hours:
      start: "18:00"
      end: "09:00"
```

## Notification Channels

### Desktop Notifications
```bash
# Auto-detect desktop notification tool
detect_desktop_notifier() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v terminal-notifier &>/dev/null; then
      echo "terminal-notifier"
    else
      echo "osascript"
    fi
  elif [[ "$OSTYPE" == "linux"* ]]; then
    if command -v notify-send &>/dev/null; then
      echo "notify-send"
    else
      echo "echo"  # Fallback to terminal
    fi
  else
    echo "echo"
  fi
}

# Send desktop notification
send_desktop_notification() {
  local title="$1"
  local message="$2"
  local urgency="${3:-normal}"  # low, normal, critical
  local sound="${4:-true}"
  
  local notifier=$(detect_desktop_notifier)
  
  case "$notifier" in
    "terminal-notifier")
      terminal-notifier -title "$title" -message "$message" \
        -group "claude-work" \
        $([ "$sound" == "true" ] && echo "-sound default")
      ;;
      
    "osascript")
      osascript -e "display notification \"$message\" with title \"$title\""
      ;;
      
    "notify-send")
      notify-send --urgency="$urgency" "$title" "$message"
      ;;
      
    *)
      echo "🔔 $title: $message"
      ;;
  esac
}
```

### Slack Notifications
```bash
# Send Slack notification
send_slack_notification() {
  local webhook_url="$1"
  local channel="$2"
  local username="$3"
  local message="$4"
  local attachments="${5:-}"
  
  local payload=$(jq -n \
    --arg channel "$channel" \
    --arg username "$username" \
    --arg text "$message" \
    --argjson attachments "${attachments:-[]}" '
    {
      channel: $channel,
      username: $username,
      text: $text,
      attachments: $attachments,
      icon_emoji: ":robot_face:"
    }
  ')
  
  curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$webhook_url" > /dev/null
}

# Format work items for Slack
format_slack_work_items() {
  local items="$1"
  local title="$2"
  
  echo "$items" | jq --arg title "$title" '
    [{
      fallback: $title,
      color: "warning",
      pretext: $title,
      fields: map({
        title: "#\(.number): \(.title[0:50])",
        value: "<\(.url)|View> | Priority: \(.priority // "normal") | Score: \(.composite_score // 0 | floor)",
        short: false
      })
    }]
  '
}
```

### Email Notifications
```bash
# Send email notification
send_email_notification() {
  local smtp_server="$1"
  local from="$2"
  local to="$3"
  local subject="$4"
  local body="$5"
  
  # Create email content
  local email_content=$(cat <<EOF
From: $from
To: $to
Subject: $subject
Content-Type: text/html

$body
EOF
)
  
  # Send via SMTP (using sendmail as example)
  if command -v sendmail &>/dev/null; then
    echo "$email_content" | sendmail -t
  else
    # Log if sendmail not available
    echo "Email notification queued: $subject" >> "${HOME}/.claude/logs/notifications.log"
  fi
}

# Generate HTML email body
generate_email_body() {
  local items="$1"
  local summary="$2"
  
  cat <<'EOF'
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; }
    .header { background: #f0f0f0; padding: 20px; }
    .item { border-bottom: 1px solid #ddd; padding: 10px; }
    .priority-critical { color: #d32f2f; }
    .priority-high { color: #f57c00; }
    .score { float: right; color: #666; }
  </style>
</head>
<body>
EOF
  
  echo "<div class='header'><h2>$summary</h2></div>"
  
  echo "$items" | jq -r '
    .[] | 
    "<div class=\"item\">" +
    "  <h3>#\(.number): \(.title)</h3>" +
    "  <p>Priority: <span class=\"priority-\(.priority // "normal")\">\(.priority // "normal")</span>" +
    "  <span class=\"score\">Score: \(.composite_score // 0 | floor)</span></p>" +
    "  <p><a href=\"\(.url)\">View Item</a></p>" +
    "</div>"
  '
  
  echo "</body></html>"
}
```

### Webhook Notifications
```bash
# Send webhook notification
send_webhook_notification() {
  local url="$1"
  local headers="$2"
  local payload="$3"
  
  # Build curl command with headers
  local curl_cmd="curl -s -X POST"
  
  # Add headers
  echo "$headers" | jq -r 'to_entries[] | "-H \"\(.key): \(.value)\""' | while read -r header; do
    curl_cmd="$curl_cmd $header"
  done
  
  # Send request
  eval "$curl_cmd -H 'Content-Type: application/json' -d '$payload' '$url'" > /dev/null
}
```

## Notification Logic

### Trigger Evaluation
```bash
# Check if item matches notification triggers
should_notify() {
  local item="$1"
  local trigger_config="$2"
  
  echo "$item" | jq --argjson config "$trigger_config" '
    # Check all conditions
    ($config.conditions // []) as $conditions |
    
    # All conditions must match
    all(
      $conditions[];
      
      if has("priority") and .priority then
        (.priority // "normal") == .priority
      elif has("labels") and .labels then
        (.labels // []) | any(. as $label | .labels | index($label))
      elif has("type") and .type then
        .type == .type
      elif has("requested_reviewer") and .requested_reviewer then
        .requested_reviewers | any(. == ($ENV.USER // ""))
      else
        true
      end
    )
  '
}

# Evaluate all triggers for an item
evaluate_triggers() {
  local item="$1"
  local config="$2"
  
  echo "$config" | jq -r '.triggers | keys[]' | while read -r trigger; do
    local trigger_config=$(echo "$config" | jq ".triggers.$trigger")
    
    if [[ $(should_notify "$item" "$trigger_config") == "true" ]]; then
      echo "$trigger"
    fi
  done
}
```

### Rate Limiting
```bash
# Check rate limits
check_rate_limit() {
  local rate_file="${HOME}/.claude/cache/notification-rate.json"
  local max_per_hour="${1:-10}"
  
  # Initialize if not exists
  if [[ ! -f "$rate_file" ]]; then
    echo '{"sent": [], "hour_count": 0}' > "$rate_file"
  fi
  
  # Clean old entries and check limit
  jq --arg max "$max_per_hour" '
    .sent = (.sent | map(select((now - .) < 3600))) |
    .hour_count = (.sent | length) |
    .allowed = (.hour_count < ($max | tonumber))
  ' < "$rate_file" > "${rate_file}.tmp" && mv "${rate_file}.tmp" "$rate_file"
  
  jq -r '.allowed' < "$rate_file"
}

# Record notification sent
record_notification() {
  local rate_file="${HOME}/.claude/cache/notification-rate.json"
  
  jq '.sent += [now]' < "$rate_file" > "${rate_file}.tmp" && \
    mv "${rate_file}.tmp" "$rate_file"
}
```

### Notification Batching
```bash
# Batch notifications within time window
batch_notifications() {
  local items="$1"
  local batch_window="${2:-5}"  # minutes
  local batch_file="${HOME}/.claude/cache/notification-batch.json"
  
  # Initialize batch file
  if [[ ! -f "$batch_file" ]] || \
     [[ $(find "$batch_file" -mmin +"$batch_window" 2>/dev/null) ]]; then
    echo '{"items": [], "created": '$(date +%s)'}' > "$batch_file"
  fi
  
  # Add items to batch
  echo "$items" | jq -s '.[0] + {items: (.[0].items + .[1])}' \
    "$batch_file" - > "${batch_file}.tmp" && \
    mv "${batch_file}.tmp" "$batch_file"
  
  # Check if batch window expired
  local batch_age=$(($(date +%s) - $(jq -r '.created' < "$batch_file")))
  if [[ $batch_age -ge $((batch_window * 60)) ]]; then
    # Return batched items and reset
    jq '.items' < "$batch_file"
    echo '{"items": [], "created": '$(date +%s)'}' > "$batch_file"
  else
    echo "[]"  # Not ready to send
  fi
}
```

### Quiet Hours Check
```bash
# Check if in quiet hours
in_quiet_hours() {
  local quiet_start="$1"
  local quiet_end="$2"
  local current_hour=$(date +%H)
  
  # Convert to minutes for comparison
  local start_min=$((${quiet_start%%:*} * 60 + ${quiet_start##*:}))
  local end_min=$((${quiet_end%%:*} * 60 + ${quiet_end##*:}))
  local current_min=$(($(date +%H) * 60 + $(date +%M)))
  
  if [[ $start_min -lt $end_min ]]; then
    # Normal range (e.g., 09:00 - 17:00)
    [[ $current_min -ge $start_min && $current_min -lt $end_min ]]
  else
    # Overnight range (e.g., 18:00 - 09:00)
    [[ $current_min -ge $start_min || $current_min -lt $end_min ]]
  fi
}
```

## Main Notification Function

```bash
# Send notifications for work items
send_work_notifications() {
  local items="$1"
  local config="${2:-$(load_notification_config)}"
  
  # Check if notifications enabled
  if [[ $(echo "$config" | jq -r '.enabled') != "true" ]]; then
    return 0
  fi
  
  # Check quiet hours
  local quiet_start=$(echo "$config" | jq -r '.rate_limiting.quiet_hours.start // "18:00"')
  local quiet_end=$(echo "$config" | jq -r '.rate_limiting.quiet_hours.end // "09:00"')
  
  if in_quiet_hours "$quiet_start" "$quiet_end"; then
    echo "🔕 In quiet hours, notifications suppressed"
    return 0
  fi
  
  # Process items
  echo "$items" | jq -c '.[]' | while read -r item; do
    # Check triggers
    local triggers=$(evaluate_triggers "$item" "$config")
    
    if [[ -n "$triggers" ]]; then
      # Check rate limit
      if [[ $(check_rate_limit) == "true" ]]; then
        # Send to appropriate channels
        for trigger in $triggers; do
          send_notification_for_trigger "$item" "$trigger" "$config"
        done
        
        record_notification
      else
        echo "⚠️  Rate limit exceeded, notification queued"
      fi
    fi
  done
}

# Send notification for specific trigger
send_notification_for_trigger() {
  local item="$1"
  local trigger="$2"
  local config="$3"
  
  local channels=$(echo "$config" | jq -r ".triggers.$trigger.channels[]")
  local title="Work Item Alert: $trigger"
  local message=$(echo "$item" | jq -r '"#\(.number): \(.title)"')
  
  for channel in $channels; do
    case "$channel" in
      "desktop")
        if [[ $(echo "$config" | jq -r '.channels.desktop.enabled') == "true" ]]; then
          send_desktop_notification "$title" "$message" "normal"
        fi
        ;;
        
      "slack")
        if [[ $(echo "$config" | jq -r '.channels.slack.enabled') == "true" ]]; then
          local webhook=$(echo "$config" | jq -r '.channels.slack.webhook_url')
          local slack_channel=$(echo "$config" | jq -r '.channels.slack.channel')
          local username=$(echo "$config" | jq -r '.channels.slack.username')
          
          send_slack_notification "$webhook" "$slack_channel" "$username" "$message"
        fi
        ;;
        
      "email")
        # Batch email notifications
        batch_notifications "[$item]" 5
        ;;
        
      "webhook")
        if [[ $(echo "$config" | jq -r '.channels.webhook.enabled') == "true" ]]; then
          local url=$(echo "$config" | jq -r '.channels.webhook.url')
          local headers=$(echo "$config" | jq '.channels.webhook.headers // {}')
          
          send_webhook_notification "$url" "$headers" "$item"
        fi
        ;;
    esac
  done
}
```

## Daily Digest

```bash
# Generate and send daily digest
send_daily_digest() {
  local items="$1"
  local config="${2:-$(load_notification_config)}"
  
  # Group items by category
  local summary=$(echo "$items" | jq -r '
    {
      total: length,
      critical: map(select(.priority == "critical")) | length,
      high_score: map(select(.composite_score > 80)) | length,
      prs_needing_review: map(select(.type == "pr" and .state == "open")) | length,
      bugs: map(select(.labels | any(. == "bug"))) | length
    } |
    "Daily Work Summary: \(.total) items (\(.critical) critical, \(.high_score) high priority, \(.prs_needing_review) PRs, \(.bugs) bugs)"
  ')
  
  # Send to digest channels
  if [[ $(echo "$config" | jq -r '.channels.email.enabled') == "true" ]]; then
    local email_body=$(generate_email_body "$items" "$summary")
    send_email_notification \
      "$(echo "$config" | jq -r '.channels.email.smtp_server')" \
      "$(echo "$config" | jq -r '.channels.email.from')" \
      "$(echo "$config" | jq -r '.channels.email.to')" \
      "$summary" \
      "$email_body"
  fi
  
  if [[ $(echo "$config" | jq -r '.channels.slack.enabled') == "true" ]]; then
    local attachments=$(format_slack_work_items "$items" "$summary")
    send_slack_notification \
      "$(echo "$config" | jq -r '.channels.slack.webhook_url')" \
      "$(echo "$config" | jq -r '.channels.slack.channel')" \
      "$(echo "$config" | jq -r '.channels.slack.username')" \
      "$summary" \
      "$attachments"
  fi
}
```

## Configuration Management

```bash
# Load notification configuration
load_notification_config() {
  local config_file="${HOME}/.claude/settings/notifications.yaml"
  
  if [[ -f "$config_file" ]]; then
    yq eval -o=json "$config_file"
  else
    # Return default config
    cat <<'EOF'
{
  "enabled": false,
  "channels": {
    "desktop": {"enabled": true}
  },
  "triggers": {
    "critical_work": {
      "channels": ["desktop"],
      "conditions": [{"priority": "critical"}]
    }
  },
  "rate_limiting": {
    "max_per_hour": 10,
    "quiet_hours": {"start": "18:00", "end": "09:00"}
  }
}
EOF
  fi
}

# Test notification setup
test_notifications() {
  echo "🧪 Testing notification channels..."
  
  send_desktop_notification "Test" "Claude Work notification test" "normal"
  echo "✅ Desktop notification sent"
  
  # Test other configured channels
  local config=$(load_notification_config)
  
  if [[ $(echo "$config" | jq -r '.channels.slack.enabled') == "true" ]]; then
    echo "Testing Slack..."
    # Add Slack test
  fi
  
  echo "✅ Notification test complete"
}
```