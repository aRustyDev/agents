#!/usr/bin/env bash
# validate-blog-frontmatter.sh
# Validates blog post frontmatter against AstroPaper schema
# Usage: validate-blog-frontmatter.sh <file>
# Returns JSON: {"valid": bool, "errors": [...], "warnings": [...]}

set -euo pipefail

FILE="${1:-}"

if [[ -z "$FILE" ]]; then
  echo '{"valid": false, "errors": ["No file provided"], "warnings": []}'
  exit 1
fi

if [[ ! -f "$FILE" ]]; then
  echo '{"valid": false, "errors": ["File not found: '"$FILE"'"], "warnings": []}'
  exit 1
fi

# Extract frontmatter (between --- markers)
FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$FILE" | sed '1d;$d')

if [[ -z "$FRONTMATTER" ]]; then
  echo '{"valid": false, "errors": ["No frontmatter found"], "warnings": []}'
  exit 1
fi

errors=()
warnings=()

# Check required fields
check_required() {
  local field="$1"
  if ! echo "$FRONTMATTER" | grep -qE "^${field}:"; then
    errors+=("Missing required field: $field")
  fi
}

check_required "id"
check_required "title"
check_required "description"
check_required "pubDatetime"
check_required "tags"

# Check for deprecated field names
if echo "$FRONTMATTER" | grep -qE "^date:"; then
  errors+=("Deprecated field 'date' found - use 'pubDatetime' instead")
fi

if echo "$FRONTMATTER" | grep -qE "^image:"; then
  errors+=("Deprecated field 'image' found - use 'ogImage' instead")
fi

# Validate UUID format for id field
ID_VALUE=$(echo "$FRONTMATTER" | grep -E "^id:" | sed 's/^id:\s*//' | tr -d '"' | tr -d "'")
if [[ -n "$ID_VALUE" ]]; then
  UUID_REGEX='^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
  if ! echo "$ID_VALUE" | grep -qiE "$UUID_REGEX"; then
    errors+=("id '$ID_VALUE' is not valid UUIDv4")
  fi
fi

# Validate pubDatetime format (ISO 8601)
PUB_DATE=$(echo "$FRONTMATTER" | grep -E "^pubDatetime:" | sed 's/^pubDatetime:\s*//' | tr -d '"' | tr -d "'")
if [[ -n "$PUB_DATE" ]]; then
  # Basic ISO 8601 check
  if ! echo "$PUB_DATE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2})?'; then
    errors+=("pubDatetime '$PUB_DATE' is not valid ISO 8601")
  fi
fi

# Check description length
DESC=$(echo "$FRONTMATTER" | grep -E "^description:" | sed 's/^description:\s*//' | tr -d '"' | tr -d "'")
if [[ -n "$DESC" ]]; then
  DESC_LEN=${#DESC}
  if [[ $DESC_LEN -gt 160 ]]; then
    errors+=("description is $DESC_LEN chars (max 160)")
  elif [[ $DESC_LEN -lt 100 ]]; then
    warnings+=("description is only $DESC_LEN chars (recommend 100-160)")
  fi
fi

# Check draft status
if echo "$FRONTMATTER" | grep -qE "^draft:\s*true"; then
  warnings+=("Post is marked as draft")
fi

# Build JSON output
valid="true"
if [[ ${#errors[@]} -gt 0 ]]; then
  valid="false"
fi

# Format errors array
errors_json="[]"
if [[ ${#errors[@]} -gt 0 ]]; then
  errors_json=$(printf '%s\n' "${errors[@]}" | jq -R . | jq -s .)
fi

# Format warnings array
warnings_json="[]"
if [[ ${#warnings[@]} -gt 0 ]]; then
  warnings_json=$(printf '%s\n' "${warnings[@]}" | jq -R . | jq -s .)
fi

echo "{\"valid\": $valid, \"errors\": $errors_json, \"warnings\": $warnings_json}"
