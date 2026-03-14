#!/usr/bin/env bash
# promote-safety.sh
# Warns about direct writes to src/data/blog/ unless the promote marker is present
# Usage: promote-safety.sh <file>
# Returns JSON: {"allowed": bool, "reason": string}
#
# The promote marker is: # promoted-by: /blog/publish/promote
# This marker must be the first line of the file to bypass the warning.

set -euo pipefail

FILE="${1:-}"

if [[ -z "$FILE" ]]; then
  echo '{"allowed": false, "reason": "No file provided"}'
  exit 1
fi

# Check if file is in src/data/blog/
if [[ ! "$FILE" =~ src/data/blog/ ]]; then
  # Not a blog file, allow without restriction
  echo '{"allowed": true, "reason": "Not a blog file"}'
  exit 0
fi

# Check if file exists (could be new file)
if [[ ! -f "$FILE" ]]; then
  # New file without promote marker - warn
  echo '{"allowed": false, "reason": "Direct write to src/data/blog/ detected. Use /blog/publish/promote to publish drafts."}'
  exit 0
fi

# Check for promote marker on first line
FIRST_LINE=$(head -n 1 "$FILE")

if [[ "$FIRST_LINE" == "# promoted-by: /blog/publish/promote" ]]; then
  echo '{"allowed": true, "reason": "Promote marker present"}'
  exit 0
fi

# Check if this is an update to existing published post
# Published posts may not have the marker but can be edited in place
if grep -qE "^draft:\s*false" "$FILE" 2>/dev/null; then
  echo '{"allowed": true, "reason": "Updating existing published post"}'
  exit 0
fi

# No marker and not an existing published post
echo '{"allowed": false, "reason": "Direct write to src/data/blog/ detected. Use /blog/publish/promote to publish drafts."}'
