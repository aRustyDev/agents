#!/bin/bash
# Cleanup session script extracted from cleanup.md

cleanup_session() {
  local session_id=$1
  local session_dir=".plan/sessions/$session_id"
  
  if [ ! -d "$session_dir" ]; then
    echo "❌ Session not found: $session_id"
    return 1
  fi
  
  # Confirm deletion
  echo "⚠️  This will permanently delete session: $session_id"
  echo "Files to be removed:"
  ls -la "$session_dir"
  echo ""
  read -p "Are you sure? (yes/no): " confirm
  
  if [ "$confirm" = "yes" ]; then
    rm -rf "$session_dir"
    echo "✅ Session deleted: $session_id"
  else
    echo "❌ Cleanup cancelled"
  fi
}
