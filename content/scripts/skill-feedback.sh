#!/bin/bash
# Skill Feedback Hook
# Runs at session end to log skill usage for analysis
#
# Hook Type: Stop / SessionEnd
# Purpose: Log skill effectiveness data for offline analysis
#
# Configuration in settings.json:
# {
#   "hooks": {
#     "Stop": [
#       {
#         "matcher": ".*",
#         "hooks": [
#           {
#             "type": "command",
#             "command": "${WORKSPACE}/.claude/hooks/skill-feedback.sh"
#           }
#         ]
#       }
#     ]
#   }
# }

set -e

# Configuration
LOG_DIR="${CLAUDE_LOG_DIR:-$HOME/.claude/logs}"
LOG_FILE="$LOG_DIR/skill-feedback.log"
ISSUES_FILE="$LOG_DIR/skill-gaps.json"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Read hook input from stdin
INPUT=$(cat)

# Extract timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Log the session end event
cat >> "$LOG_FILE" << EOF
---
timestamp: $TIMESTAMP
event: session_end
input_length: ${#INPUT}
EOF

# Parse input for skill-related information (if available in context)
# The actual skill analysis happens via the prompt-type hook (see settings template)
# This script primarily handles logging for offline analysis

# Check if there are any pending skill gaps to report
if [[ -f "$ISSUES_FILE" ]] && [[ -s "$ISSUES_FILE" ]]; then
    PENDING_COUNT=$(jq 'length' "$ISSUES_FILE" 2>/dev/null || echo "0")
    if [[ "$PENDING_COUNT" -gt 0 ]]; then
        echo "skill_gaps_pending: $PENDING_COUNT" >> "$LOG_FILE"
    fi
fi

# Exit successfully (don't block session end)
exit 0
