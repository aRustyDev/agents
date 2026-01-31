#!/bin/bash
# Session management functions for plan command
# Extracted from _core.md

# Create a new session
create_session() {
  SESSION_ID=$(date +%Y%m%d_%H%M%S)
  SESSION_DIR=".plan/sessions/$SESSION_ID"
  mkdir -p "$SESSION_DIR"
  echo "$SESSION_DIR"
}

# Load an existing session
load_session() {
  local session_id=$1
  if [ -d ".plan/sessions/$session_id" ]; then
    SESSION_DIR=".plan/sessions/$session_id"
    echo "✅ Loaded session: $session_id"
    return 0
  else
    echo "❌ Session not found: $session_id"
    return 1
  fi
}

# List all sessions
list_sessions() {
  if [ -d ".plan/sessions" ] && [ "$(ls -A .plan/sessions)" ]; then
    echo "📁 Available sessions:"
    for session in .plan/sessions/*/; do
      session_name=$(basename "$session")
      created=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$session" 2>/dev/null || echo "Unknown")
      echo "  • $session_name (created: $created)"
    done
  else
    echo "ℹ️ No sessions found"
  fi
}

# Get repository information
get_repo_info() {
  REPO_OWNER=$(gh repo view --json owner -q .owner.login)
  REPO_NAME=$(gh repo view --json name -q .name)
  REPO_URL=$(gh repo view --json url -q .url)
}

# Check prerequisites
check_prerequisites() {
  # Check for gh CLI
  if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI not found"
    echo "Please install GitHub CLI: https://cli.github.com" >&2
    exit 1
  fi
  
  # Check for git repository
  if ! git rev-parse --git-dir &> /dev/null; then
    echo "❌ Error: Not in a git repository"
    echo "Run this command from within a git repository" >&2
    exit 2
  fi
  
  # Check GitHub authentication
  if ! gh auth status &>/dev/null; then
    echo "❌ Error: Not authenticated with GitHub"
    echo "Run: gh auth login" >&2
    exit 3
  fi
  
  # Check repository access
  if ! gh repo view &>/dev/null; then
    echo "❌ Error: Cannot access repository"
    echo "Check repository permissions" >&2
    exit 4
  fi
}

# Handle errors consistently
handle_error() {
  local error_code=$1
  local error_message=$2
  
  echo -e "❌ Error: ${error_message}" >&2
  
  case $error_code in
    1)
      echo "Please install GitHub CLI: https://cli.github.com" >&2
      ;;
    2)
      echo "Run this command from within a git repository" >&2
      ;;
    3)
      echo "Run: gh auth login" >&2
      ;;
    4)
      echo "Check repository permissions" >&2
      ;;
  esac
  
  exit $error_code
}