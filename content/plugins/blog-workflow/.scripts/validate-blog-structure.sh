#!/bin/bash
# Validates blog workflow directory structure exists
# Usage: validate-blog-structure.sh [target_dir]

TARGET_DIR="${1:-.}"

DIRS=(
  "content/_projects"
  "content/_drafts"
  "content/_templates/personas"
  "content/_templates/outlines"
  "content/_templates/research-plans"
  "content/_templates/review-checklists"
  "content/_templates/brainstorm-plans"
  "content/_templates/schemas"
)

MISSING=0
for dir in "${DIRS[@]}"; do
  if [ ! -d "$TARGET_DIR/$dir" ]; then
    echo "Missing: $TARGET_DIR/$dir"
    MISSING=$((MISSING + 1))
  fi
done

if [ "$MISSING" -eq 0 ]; then
  echo "All directories present"
  exit 0
else
  echo "Missing $MISSING directories"
  exit 1
fi
