#!/bin/bash
# Local artifact cleanup functions
# Extracted from plan/cleanup.md

cleanup_local() {
  if [ -d ".plan" ]; then
    echo "📁 Found local plan directory:"
    du -sh .plan 2>/dev/null || echo "Size calculation unavailable"
    
    # List sessions
    if [ -d ".plan/sessions" ]; then
      echo ""
      echo "Sessions found:"
      ls -la .plan/sessions/
    fi
    
    read -p "Remove all local plan artifacts? (y/n): " CONFIRM
    if [ "$CONFIRM" = "y" ]; then
      rm -rf .plan
      echo "✅ Local artifacts removed"
    else
      echo "❌ Cleanup cancelled"
    fi
  else
    echo "ℹ️ No local artifacts found"
  fi
}

# Archive session instead of deleting
archive_session() {
  local session_id=$1
  local session_dir=".plan/sessions/$session_id"
  local archive_dir=".plan/archive/$(date +%Y%m)"
  
  if [ ! -d "$session_dir" ]; then
    echo "❌ Session not found: $session_id"
    return 1
  fi
  
  mkdir -p "$archive_dir"
  mv "$session_dir" "$archive_dir/"
  echo "✅ Session archived to: $archive_dir/$session_id"
}

# List all plan sessions
list_sessions() {
  if [ -d ".plan/sessions" ] && [ "$(ls -A .plan/sessions)" ]; then
    echo "📁 Plan sessions:"
    for session in .plan/sessions/*/; do
      session_name=$(basename "$session")
      created=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$session" 2>/dev/null || echo "Unknown")
      size=$(du -sh "$session" | cut -f1)
      echo "  • $session_name (created: $created, size: $size)"
    done
  else
    echo "ℹ️ No sessions found"
  fi
}